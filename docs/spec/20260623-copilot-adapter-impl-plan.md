# Implementation Plan: Microsoft Copilot / Azure OpenAI Adapter

| Field | Value |
|---|---|
| Date | 2026-06-23 |
| Author | Backend Developer Agent |
| RFC | `docs/rfc/20260621-copilot-api-provider.md` |
| Branch | `develop` |
| Status | Approved — ready for implementation |

---

## 1. Scope and goals

Add `copilot_api` as a fourth LLM provider to the AIAPI gateway, backed by Azure
OpenAI Service, without modifying the behavior of any existing provider. The work
covers:

- A new `AIProvider` enum (fixes Tech Debt #1 — provider-identifier drift).
- Four new Azure env-var names in `Config`.
- A new `CopilotAdapter` that wraps `AzureOpenAI` from the already-installed
  `openai` SDK.
- A new factory branch in `AIProviderFactory`.
- Two new optional fields (`deployment`, `api_version`) in `AIRequest`.
- Forwarding those new fields through `app.generate` into `params`.
- Structured error `detail` objects in `app.py` (ADR-004, non-blocking).
- Unit tests in `tests/infrastructure/adapters/test_copilot_adapter.py` mirroring
  existing style.

**What is NOT in scope:** changes to `AIService`, `AIProviderPort`, `GeminiAdapter`,
`ClaudeAdapter`, `OpenAIAdapter`, `dependencies.py`, or `main.py`. No new
third-party dependencies.

---

## 2. Dependency order

The phases below must be executed in this order because each phase is consumed by
the next:

```
Phase 1 → Phase 2 → Phase 4 → Phase 3 (parallel with Phase 4 is fine)
                 → Phase 5 → Phase 6 → Phase 7
```

Concretely:
- **Phase 1** (`AIProvider` enum) must be done first; Phase 2 (`AIRequest`) and
  Phase 4 (`AIProviderFactory`) both import it.
- **Phase 2** (`Config`) has no dependencies; it can run in parallel with Phase 1.
- **Phase 3** (`AIRequest`) depends on Phase 1 (enum).
- **Phase 4** (`AIProviderFactory`) depends on Phase 1 (enum) and Phase 5
  (`CopilotAdapter`).
- **Phase 5** (`CopilotAdapter`) depends on Phase 2 (`Config`) and Phase 1
  (indirectly, via port).
- **Phase 6** (`app.py`) depends on Phase 3 (`AIRequest` new fields).
- **Phase 7** (tests) depends on all production phases.

---

## 3. Phases and file-level changes

---

### Phase 1 — Create `AIProvider` enum (new file)

**File:** `src/application/domain/ai_provider.py` (CREATE)

**Also create:** `src/application/domain/__init__.py` (CREATE, empty module marker)

**What to add:**

1. Module-level docstring following the existing convention (DESCRIPTION + EXAMPLES
   sections in uppercase).
2. Import `enum.Enum` from stdlib only — no provider-SDK imports allowed in the
   `application` layer.
3. Define `AIProvider(str, Enum)` so that each member's value is a plain string and
   Pydantic can accept `"copilot_api"` directly without a custom validator.
   - `OPENAI_API = "openai_api"` — **lowercase**, matching the RFC JSON contract.
   - `CLAUDE_API = "claude_api"`
   - `GEMINI_API = "gemini_api"`
   - `COPILOT_API = "copilot_api"`
4. Add a `@classmethod from_value(cls, value: str) -> "AIProvider"` that wraps
   `cls(value)` and raises a descriptive `ValueError` (listing valid values) when
   the string is not recognized.
5. Class-level docstring using the same DESCRIPTION / ATTRIBUTES / METHODS /
   EXAMPLES pattern used throughout the project.

**Gotchas:**
- The enum values use **lowercase** (`openai_api`), which differs from the
  current factory string constants (`OPENAI_API` / `"OPENAI_API"`). This is an
  intentional breaking-tech-debt change: the RFC contract (Section 7.6.4) and the
  OpenAPI schema define lowercase provider IDs. The factory constants and the
  `app.py` error paths must be updated accordingly in later phases.
- Inherit from both `str` and `Enum` (`class AIProvider(str, Enum)`) so that
  Pydantic v2 serializes the value as a plain string in JSON responses — no
  `"AIProvider.copilot_api"` surprises.
- Do NOT import this enum in `AIProviderPort` or `AIService`; those are
  provider-agnostic. Only `AIRequest` (DTO) and `AIProviderFactory` (bootstrap)
  use it.

---

### Phase 2 — Extend `Config` with Azure env-var names

**File:** `config.py` (MODIFY)

**What to add:**

Inside the `Config` class, after `CLAUDE_API_KEY`, add four new class-level string
constants (same pattern as the existing three):

```
COPILOT_API_KEY      = "COPILOT_API_KEY"
COPILOT_API_ENDPOINT = "COPILOT_API_ENDPOINT"
COPILOT_API_VERSION  = "COPILOT_API_VERSION"
COPILOT_DEPLOYMENT   = "COPILOT_DEPLOYMENT"
```

Update the class docstring's `ATTRIBUTES` section to list all seven constants.
Update the module-level docstring `EXAMPLES` line to remain accurate.

**Gotchas:**
- These are env-var **name** strings only — no default values, no `os.environ`
  reads inside `Config`. That is the adapter's responsibility.
- The constant names are `SCREAMING_SNAKE_CASE`; their string values are identical
  (same convention as the three existing keys).

---

### Phase 3 — Extend `AIRequest` with new optional fields and enum-typed provider

**File:** `src/application/dto/ai_request.py` (MODIFY)

**What to change:**

1. Add import: `from src.application.domain.ai_provider import AIProvider`.
2. Change the `provider` field type from `str` to `AIProvider`:
   ```python
   provider: AIProvider = Field(..., description="AI provider identifier")
   ```
   Pydantic v2 with a `str`-based enum will coerce the incoming JSON string
   (e.g. `"copilot_api"`) into `AIProvider.COPILOT_API` automatically, and
   serialize it back to `"copilot_api"` without any custom validator.
3. After `max_tokens`, add two new optional fields:
   ```python
   deployment: str | None = Field(default=None, description="Azure OpenAI deployment name (copilot_api only)")
   api_version: str | None = Field(default=None, description="Azure OpenAI API version (copilot_api only)")
   ```
4. Update the class docstring's `ARGS` block to document `provider` as `AIProvider`,
   `deployment`, and `api_version`.
5. Update the module-level docstring `EXAMPLES` line to reflect valid lowercase
   provider values (e.g. `'copilot_api'`).

**Gotchas:**
- The `provider` field type change is backward-compatible for callers already sending
  lowercase strings (e.g. `"openai_api"`). However, the existing factory constants
  are uppercase (`"OPENAI_API"`). After this change, a request with
  `"provider": "OPENAI_API"` will fail Pydantic validation with a 422 (not
  recognized by the enum). This is the intended correction under ADR-003 — the
  contract moves to lowercase. Coordinate with any integration tests that send
  uppercase provider strings.
- `deployment` and `api_version` are `str | None` with `default=None`, so they are
  entirely optional and invisible to existing providers.

---

### Phase 4 — Update `AIProviderFactory` with Copilot branch and enum references

**File:** `src/bootstrap/ai_factory.py` (MODIFY)

**What to change:**

1. Add import: `from src.application.domain.ai_provider import AIProvider`.
2. Add import: `from src.infrastructure.adapters.copilot_adapter import CopilotAdapter`.
3. Add class constant after `OPENAI_API`:
   ```python
   COPILOT_API = AIProvider.COPILOT_API.value   # "copilot_api"
   ```
   Also update the existing constants to use the enum values for consistency:
   ```python
   CLAUDE_API  = AIProvider.CLAUDE_API.value    # "claude_api"
   GEMINI_API  = AIProvider.GEMINI_API.value    # "gemini_api"
   OPENAI_API  = AIProvider.OPENAI_API.value    # "openai_api"
   ```
4. Update the `match/case` to use the new lowercase values. Since the constants
   themselves become lowercase strings, the existing `case AIProviderFactory.X:`
   syntax remains valid — no other match/case code change is needed.
5. Add the Copilot case before the default:
   ```python
   case AIProviderFactory.COPILOT_API:
       ai_provider = CopilotAdapter()
   ```
6. Update the class docstring `ATTRIBUTES` to include `COPILOT_API`.
7. Update the `create` method's docstring to mention Copilot.

**Gotchas:**
- Changing `CLAUDE_API`, `GEMINI_API`, `OPENAI_API` from `"CLAUDE_API"` to
  `"claude_api"` etc. is a **breaking change** for any caller that uses the string
  literal `"OPENAI_API"` directly (e.g., existing test setUp data, the old
  `AIRequest` examples). Cross-reference with test files to update them.
- `dependencies.py` passes `provider: str` to `AIProviderFactory.create(provider)`.
  After Phase 3, `create_ai_provider` receives an `AIProvider` enum value from
  `request.provider`. The `create` signature accepts `str` today. Since
  `AIProvider(str, Enum)`, the enum value is also a `str`, so the match/case
  comparison with the string constant works without changing `dependencies.py`.
  However, the type annotation on `create(provider: str)` should be updated to
  `create(provider: str | AIProvider)` or simply left as-is (both work because
  `AIProvider` is a `str` subclass). Keeping `str` is simpler and avoids touching
  more files.
- The `ValueError` message in the default case (`"Provider {provider} is not
  support."`) has a typo ("support" instead of "supported"). Fixing it here is a
  low-risk improvement within scope since we are already editing the file.

---

### Phase 5 — Create `CopilotAdapter`

**File:** `src/infrastructure/adapters/copilot_adapter.py` (CREATE)

**What to implement:**

#### Module-level structure

```
module docstring (DESCRIPTION + EXAMPLES)
imports: os, dotenv.load_dotenv, openai.AzureOpenAI, config.Config,
         src.application.ports.ai_provider_port.AIProviderPort
load_dotenv()
class CopilotAdapter(AIProviderPort): ...
```

#### `__init__(self)`

1. Read the four required Azure config values using `os.environ.get(Config.X)`:
   - `api_key` from `Config.COPILOT_API_KEY`
   - `azure_endpoint` from `Config.COPILOT_API_ENDPOINT`
   - `api_version` from `Config.COPILOT_API_VERSION`
   - `self._default_deployment` from `Config.COPILOT_DEPLOYMENT`
2. Validate that `api_key`, `azure_endpoint`, and `api_version` are all non-empty
   strings. If any is missing or empty, raise:
   ```python
   raise ValueError(
       "Copilot provider is not configured. "
       "Required environment variables are missing: "
       "COPILOT_API_KEY, COPILOT_API_ENDPOINT, COPILOT_API_VERSION."
   )
   ```
   The message must **not** echo the actual key/endpoint values (NFR-3 / AC-8).
3. Construct the client:
   ```python
   self.client = AzureOpenAI(
       api_key=api_key,
       azure_endpoint=azure_endpoint,
       api_version=api_version,
   )
   ```
   Note: `api_version` passed here is the env-level default. When `api_version`
   arrives in `params` (per-request override), a new client instance is needed per
   request to honour that override. v1 uses the env-level `api_version` for the
   client; the per-request `api_version` field is a contract extension for future
   use (see gotchas).

#### Private helper `_resolve_deployment(self, params: dict) -> str`

Resolution precedence (RFC Section 7.5, AC-3):
1. `params.get("deployment")` — per-request override takes priority.
2. `params.get("model")` — model field used as deployment name if `deployment` absent.
3. `self._default_deployment` — env-level `COPILOT_DEPLOYMENT`.

If all three are `None` or empty string, raise:
```python
raise ValueError(
    "No Azure OpenAI deployment could be resolved. "
    "Provide 'deployment' in the request or set COPILOT_DEPLOYMENT."
)
```
Again, no secret values in the error message.

#### `generate_content(self, params: dict) -> str`

1. Call `_resolve_deployment(params)` to get `deployment`.
2. Build the `kwargs` dict for sampling parameters — only include non-None values:
   ```python
   sampling: dict = {}
   if params.get("temperature") is not None:
       sampling["temperature"] = params["temperature"]
   if params.get("top_p") is not None:
       sampling["top_p"] = params["top_p"]
   if params.get("max_tokens") is not None:
       sampling["max_tokens"] = params["max_tokens"]
   # top_k is never forwarded
   ```
3. Call the Azure client:
   ```python
   self.response = self.client.chat.completions.create(
       model=deployment,
       messages=[{"role": "user", "content": params.get("prompt")}],
       **sampling,
   )
   ```
4. Return `self.response.choices[0].message.content`.

#### `close_client(self)`

Call `self.client.close()`.

**Docstrings:** Follow the exact uppercase-section style used in `openai_adapter.py`:
DESCRIPTION, ARGS, RETURN, EXCEPTIONS, EXAMPLES.

**Gotchas:**
- `top_k` must **never** be forwarded to `AzureOpenAI.chat.completions.create`.
  Azure OpenAI does not accept it and will raise a 400 error. The RFC explicitly
  calls this out (AC-2).
- Per-request `api_version` override: the `AzureOpenAI` client is constructed once
  in `__init__` with the env-level `api_version`. A per-request `api_version`
  override (from `params.get("api_version")`) would require constructing a new
  client per call — this adds complexity and is explicitly deferred in v1 per
  RFC Section 7.5 ("Defaults to env `COPILOT_API_VERSION`"). Document this
  limitation in the method docstring.
- `self.response` is stored as an instance attribute (same pattern as
  `OpenAIAdapter.response`). This enables direct assertion in tests
  (`self.adapter.response`).
- Bandit rule S105 / S106 (hardcoded secrets): none are present here. Bandit S108
  (temp file): not applicable. The `os.environ.get` calls are clean.
- The `AzureOpenAI` client signature (`api_key`, `azure_endpoint`, `api_version`)
  maps exactly to the `openai>=2.37.0` SDK already in the dependency list.
  No version bump required.

---

### Phase 6 — Update `app.py` to forward new fields and structured errors

**File:** `src/infrastructure/api/app.py` (MODIFY)

**What to change:**

#### 6a. Forward `deployment` and `api_version` in the `params` dict

In the `generate` function, add the two new keys to the `params` dict after
`max_tokens`:
```python
params = {
    "model": request.model,
    "prompt": request.prompt,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "max_tokens": request.max_tokens,
    "deployment": request.deployment,
    "api_version": request.api_version,
}
```
Both are `None` by default, so existing adapters that do not read these keys are
unaffected.

#### 6b. Update `app.description` to mention Copilot

Change the FastAPI `description` in `app = FastAPI(...)`:
```python
description="AI API Gateway for OpenAI, Gemini, Claude, and Microsoft Copilot (Azure OpenAI)"
```

#### 6c. Update `version` to `"0.2.0"` (matches RFC OpenAPI contract)

#### 6d. (ADR-004, Recommended) Structured error detail

Replace the two `raise HTTPException` calls with structured `detail` dicts:

**Unsupported provider (400):**
```python
raise HTTPException(
    status_code=400,
    detail={
        "code": "UNSUPPORTED_PROVIDER",
        "message": f"Provider '{request.provider}' is not supported.",
        "supported": [p.value for p in AIProvider],
    },
) from e
```
This requires adding `from src.application.domain.ai_provider import AIProvider`
to the imports.

**Provider value error / misconfiguration (400):**
```python
raise HTTPException(
    status_code=400,
    detail={
        "code": "PROVIDER_MISCONFIGURED",
        "message": str(e),
    },
) from e
```

**Unexpected internal error (500):**
```python
raise HTTPException(
    status_code=500,
    detail={
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred.",
    },
) from e
```
The 500 case must **not** echo `str(e)` to avoid leaking internal details or
secret-adjacent stack traces (NFR-3 / AC-8).

**Gotchas:**
- `request.provider` is now an `AIProvider` enum, so using it in f-strings or
  `detail` dicts will emit its `.value` string (e.g. `"copilot_api"`) because the
  class inherits from `str`. No `.value` suffix needed in the f-string.
- ADR-004 is marked "recommended, non-blocking". If the team decides to defer it,
  skip step 6d entirely. The plan flags it as Important (not Critical).
- The existing `create_ai_provider` call in `app.generate` passes
  `request.provider` (now an `AIProvider` enum) to `dependencies.py`, which
  passes it to `AIProviderFactory.create(provider: str)`. Because `AIProvider`
  inherits `str`, this type-passes without a cast. No changes to `dependencies.py`.

---

### Phase 7 — Write unit tests for `CopilotAdapter`

**File:** `tests/infrastructure/adapters/test_copilot_adapter.py` (CREATE)

**Style reference:** `tests/infrastructure/adapters/test_openai_adapter.py`

**Test class:** `CopilotAdapterTest(unittest.TestCase)`

#### `setUp`

```python
self.params = {
    "model": "gpt-4o",
    "prompt": "Write a summary about Python.",
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 20,
    "max_tokens": 256,
    "deployment": "gpt-4o-prod",
    "api_version": "2024-10-21",
}
self.adapter = CopilotAdapter()
```

Because the adapter validates env vars in `__init__`, the test module must patch
or set env vars before constructing `CopilotAdapter`. Use
`unittest.mock.patch.dict(os.environ, {...})` in `setUp` (or as a class decorator)
to inject dummy Azure credentials without needing a real `.env` file.

#### `tearDown`

```python
self.adapter.close_client()
```

#### Test cases

| Test method | Scenario | Assert |
|---|---|---|
| `test_generate_content_returns_expected_value` | Happy path — all params set, `top_k` in params but must not be forwarded | Mock `self.adapter.client.chat.completions.create`; assert return value equals expected; assert called with `model="gpt-4o-prod"`, `messages=[...]`, `temperature`, `top_p`, `max_tokens`; assert `top_k` NOT in call kwargs |
| `test_generate_content_uses_model_as_deployment_fallback` | `deployment` is `None` in params; `model` becomes the deployment | Same mock; assert `model=self.params["model"]` in the call |
| `test_generate_content_uses_env_deployment_as_last_resort` | Both `deployment` and `model` are `None`; falls back to `self.adapter._default_deployment` | Set `self.adapter._default_deployment = "env-deploy"`; assert `model="env-deploy"` in call |
| `test_generate_content_raises_when_no_deployment_resolved` | `deployment=None`, `model=None`, `_default_deployment=None` | Assert `ValueError` raised |
| `test_generate_content_skips_none_sampling_params` | `temperature=None`, `top_p=None`, `max_tokens=None` | Assert none of those keys appear in call kwargs |
| `test_generate_content_internal_server_error` | SDK raises `Exception` with `status_code=503` | Assert exception propagates; assert `status_code == 503` |
| `test_close_client` | `close_client()` called | Mock client; assert `client.close()` called once |
| `test_init_raises_when_api_key_missing` | `COPILOT_API_KEY` not in env | `patch.dict` removing the key; assert `ValueError` raised on construction |
| `test_init_raises_when_endpoint_missing` | `COPILOT_API_ENDPOINT` not in env | Same pattern |
| `test_init_raises_when_api_version_missing` | `COPILOT_API_VERSION` not in env | Same pattern |
| `test_error_message_contains_no_secret_values` | Misconfiguration error text | Assert `api_key`, `endpoint`, or deployment values do NOT appear in the exception message |

#### Mocking pattern (mirroring `test_openai_adapter.py`)

```python
from types import SimpleNamespace
from unittest.mock import Mock, patch

# In test method:
self.adapter.client = Mock()
self.adapter.client.chat.completions.create.return_value.choices = [
    SimpleNamespace(message=SimpleNamespace(content=expected))
]
```

For init tests, patch the AzureOpenAI constructor so no real network call is made
even if valid env vars happen to be set:
```python
with patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI"):
    with patch.dict(os.environ, {}, clear=True):
        with self.assertRaises(ValueError):
            CopilotAdapter()
```

---

## 4. Files touched — summary table

| File | Action | Phase |
|---|---|---|
| `src/application/domain/__init__.py` | CREATE (empty) | 1 |
| `src/application/domain/ai_provider.py` | CREATE | 1 |
| `config.py` | MODIFY (add 4 constants) | 2 |
| `src/application/dto/ai_request.py` | MODIFY (provider type + 2 fields) | 3 |
| `src/bootstrap/ai_factory.py` | MODIFY (enum refs + Copilot case) | 4 |
| `src/infrastructure/adapters/copilot_adapter.py` | CREATE | 5 |
| `src/infrastructure/api/app.py` | MODIFY (params dict + structured errors) | 6 |
| `tests/infrastructure/adapters/test_copilot_adapter.py` | CREATE | 7 |

**Files NOT touched:** `main.py`, `dependencies.py`, `ai_service.py`,
`ai_provider_port.py`, `ai_response.py`, `openai_adapter.py`, `claude_adapter.py`,
`gemini_adapter.py`.

---

## 5. Quality checklist (per-phase)

| Check | Applies to phases |
|---|---|
| Uppercase-section docstrings (DESCRIPTION / ARGS / RETURN / EXCEPTIONS / EXAMPLES) | 1, 3, 4, 5, 6 |
| `ruff check` passes (E, F, UP, B, SIM, I, S) | all |
| `mypy` passes (no `Any` leakage, return types annotated) | all |
| No secret value echoed in error messages | 5, 6 |
| `top_k` never forwarded to AzureOpenAI | 5, 7 |
| Deployment precedence enforced: request > model > env | 5, 7 |
| `AIService.try/finally` guarantees `close_client()` — no change needed | — (existing) |
| Existing adapter tests still pass unchanged | 7 (regression check) |

---

## 6. Edge cases and design decisions

### 6.1 Provider identifier casing change (Critical)

Existing factory constants use uppercase strings (`"OPENAI_API"`). After this
implementation, the public API contract moves to lowercase (`"openai_api"`). Any
existing client sending `"OPENAI_API"` will receive a 422 from Pydantic's enum
validation. This is intentional (ADR-003) and must be communicated to frontend and
QA before deployment.

### 6.2 Per-request `api_version` override

The `api_version` field is accepted in `AIRequest` and forwarded in `params`, but
the `CopilotAdapter` uses the env-level `COPILOT_API_VERSION` for the
`AzureOpenAI` client (which is constructed once in `__init__`). A per-request
override would require re-constructing the client on each call — deferred to v2.
Document this in the `generate_content` docstring and in the RFC consequences.

### 6.3 `AIProviderFactory.create` type signature

The function accepts `provider: str`. After Phase 3, callers pass an `AIProvider`
(which is a `str` subclass). No signature change is needed; the `match/case`
compares against the constants (which hold `.value` strings), and since
`AIProvider.COPILOT_API == "copilot_api"` is `True` (thanks to `str` inheritance),
the match works correctly.

### 6.4 `AIResponse.provider` field

`AIResponse.provider` is typed `str | None`. After Phase 3, `app.generate` passes
`request.provider` (an `AIProvider` enum) to `AIResponse(provider=request.provider)`.
Since `AIProvider` is a `str` subclass, Pydantic will serialize it as a string in
the JSON response. No change to `AIResponse` is needed.

### 6.5 Bandit (S rules) surface in `CopilotAdapter`

- `os.environ.get(...)` — clean; no subprocess or eval involved.
- `AzureOpenAI(api_key=..., azure_endpoint=..., ...)` — Bandit S105 does not flag
  variable assignments; only hardcoded string secrets. All values come from env.
- No URL concatenation; the endpoint is passed as-is to the SDK.

### 6.6 Missing `__init__.py` for `application/domain`

The `src/application/domain/` directory does not exist. Create an empty
`__init__.py` alongside `ai_provider.py` to make it a proper Python package
discoverable by the import system.

---

## 7. Prioritized open items

| Priority | Item |
|---|---|
| **Critical** | Confirm provider-ID casing change with frontend/QA before merging — existing uppercase strings break on 422 |
| **Critical** | Verify `AzureOpenAI` constructor accepts `azure_endpoint` (not `base_url`) in the project's pinned `openai>=2.37.0` |
| **Important** | Decide on ADR-004 (structured errors) before Phase 6d — if deferred, keep existing string `detail` |
| **Important** | Update existing test `setUp` params that use uppercase provider strings if any integration or API-level tests exist |
| **Suggestion** | Plan per-request `api_version` client re-construction as a v2 follow-up |
| **Suggestion** | Plan `max_completion_tokens` support for o-series Azure deployments |
| **Suggestion** | Add `pytest.ini` / `[tool.pytest.ini_options]` with `pythonpath = ["src"]` and `testpaths = ["tests"]` to `pyproject.toml` if not already configured (currently absent from `pyproject.toml`) |
