---
name: project-conventions
description: Coding conventions, docstring style, test style, and project structure decisions for AIAPI
metadata:
  type: project
---

## Docstring style

All modules, classes, and methods use uppercase-section docstrings:
DESCRIPTION, ARGS, RETURN, EXCEPTIONS, EXAMPLES. Example:

```python
"""Short one-line summary.

DESCRIPTION
Multi-line narrative.

ARGS
param: type
    Description.

RETURN
type
    Description.

EXAMPLES
>>> usage_example()
"""
```

## Test style

- `unittest.TestCase` subclasses, named `<Class>Test`.
- `setUp` builds `self.params: dict` and `self.adapter = Adapter()`.
- `tearDown` calls `self.adapter.close_client()`.
- Mocking pattern: `self.adapter.client = Mock()` then configure return values.
- `SimpleNamespace` from `types` used to build mock response objects (avoids
  creating full dataclass stubs).
- Tests named `test_<what>_<expected_outcome>`.
- `unittest.mock.patch.dict(os.environ, {...})` used to inject env vars for
  adapters that validate config in `__init__`.
- When an adapter's `client` attribute is typed as an SDK class with overloaded
  methods (e.g. `AzureOpenAI`), assign a local `self.mock_client: Mock = Mock()`
  and use `self.adapter.client = self.mock_client  # type: ignore[assignment]`.
  Accessing mock internals through `self.mock_client` (not `self.adapter.client`)
  avoids mypy `attr-defined` errors caused by overload resolution.

## File / import conventions

- All adapters: `import os`, `from dotenv import load_dotenv`, `load_dotenv()` at
  module level, then `os.environ.get(Config.SOME_KEY)` in `__init__`.
- `Config` is at root `config.py`; adapters import with `from config import Config`.
- Application-layer imports use `from src.application....` style.
- No relative imports anywhere.
- New packages require an `__init__.py` file.

## Architecture constraints

- `application` layer must NEVER import provider SDKs or `infrastructure` code.
- `infrastructure` adapters import `src.application.ports.ai_provider_port` and
  `config`, plus their SDK.
- `bootstrap` is the composition root; it may import both layers.
- Enum `AIProvider(StrEnum)` lives in `src/application/domain/ai_provider.py`
  (new package created for the Copilot feature). Use `StrEnum` (not `str, Enum`)
  because ruff UP042 flags the latter.
- HTTP error responses use structured detail dicts:
  `{"code": "ERROR_CODE", "message": "..."}` — never echo raw exception strings
  in 500 responses, and never echo secret values in any error message.

## Provider identifier casing

After ADR-003 implementation, provider identifiers are **lowercase** (`openai_api`,
`claude_api`, `gemini_api`, `copilot_api`). The old uppercase constants
(`"OPENAI_API"`) are no longer valid in the request contract.

## Quality tools

- `uv run ruff check .` — must pass (rules E,F,UP,B,SIM,I,S)
- `uv run mypy .` — must pass
- `uv run pytest` — all tests green
