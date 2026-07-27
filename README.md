# AIAPI 🤖

AIAPI is a small web service that sends one generation request to different AI providers and returns a standard JSON response. It supports OpenAI, Claude, Gemini, and Microsoft Copilot (Azure OpenAI).

## Installation with uv 🚀

```bash
# Go to the project folder
cd aiapi

# Install the dependencies defined in pyproject.toml
uv sync

# Install the development tools too, if you want to work on the project
uv sync --group dev

# Start the app with the main entrypoint
uv run python main.py

# Or run FastAPI directly with Uvicorn
uv run uvicorn infrastructure.api.app:app --reload --host 127.0.0.1 --port 8080
```

### Quick notes 💡

- `uv sync` creates the virtual environment and installs all runtime dependencies.
- `uv sync --group dev` adds tools like `ruff`, `mypy`, and `pre-commit`.
- The application runs on `http://127.0.0.1:8080`.
- Once it's running, open `http://127.0.0.1:8080/` in a browser for the web UI, or call `http://127.0.0.1:8080/api/v1/generate` directly (see [Web API](#web-api-) and [Web UI](#web-ui-) below).

## Deployment with Docker 🐳

The project ships with a production-ready `Dockerfile` (multi-stage build) and a `docker-compose.yml` for local development.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running.
- A `.env` file in the project root with your API keys (see [Configuration](#configuration-) below).

### Build the image

```bash
docker build -t aiapi:latest .
```

### Run the container

```bash
# Inject API keys from .env at runtime (keys are never baked into the image)
docker run --rm \
  --env-file .env \
  -p 127.0.0.1:8080:8080 \
  aiapi:latest
```

Or pass individual keys:

```bash
docker run --rm \
  -e OPENAI_API_KEY=sk-... \
  -e CLAUDE_API_KEY=sk-ant-... \
  -e GEMINI_API_KEY=AIza... \
  -p 127.0.0.1:8080:8080 \
  aiapi:latest
```

The server is available at `http://localhost:8080` once the container starts.

> **Loopback-only by default.** `/api/v1/generate` has no built-in authentication, so the examples above publish only to `127.0.0.1` — matching the pre-Docker behavior where the API was reachable solely from the same machine. If you genuinely need the container reachable from other hosts, publish more broadly yourself (e.g. `-p 0.0.0.0:8080:8080` or `-p 8080:8080`) and put an authenticating reverse proxy or network policy in front of it first, since anyone who can reach the port can spend your provider API quota.

### Development stack with Docker Compose

`docker-compose.yml` enables live reload by mounting the source code into the container:

```bash
# Build and start
docker compose up --build

# Start in detached mode
docker compose up --build -d

# Tail logs
docker compose logs -f aiapi

# Stop and remove
docker compose down
```

## Configuration 🔧

This project reads its secrets from a `.env` file in the project root. Create it like this:

```dotenv
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Claude
CLAUDE_API_KEY=your_claude_api_key

# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Microsoft Copilot (Azure OpenAI)
COPILOT_API_KEY=your_azure_openai_api_key
COPILOT_API_ENDPOINT=https://your-resource.openai.azure.com/
COPILOT_API_VERSION=2024-10-21
COPILOT_DEPLOYMENT=your_default_deployment_name
```

> **Important — no quotes around values.** `python-dotenv` (used for local `uv` runs) strips quotes automatically, but `docker --env-file` passes them literally. Writing values without quotes works correctly in both contexts.

### How To Get Each API Key ✨

#### OpenAI 🤖

1. Go to the OpenAI API keys page: https://platform.openai.com/api-keys.
2. Sign in to your OpenAI account.
3. Create a new API key in the dashboard.
4. Copy the key and paste it into `.env` as `OPENAI_API_KEY`.

#### Claude 🧠

1. Open the Anthropic Console: https://platform.claude.com/.
2. Sign in and go to the keys page: https://platform.claude.com/settings/keys.
3. Create a new API key.
4. Copy the key and save it in `.env` as `CLAUDE_API_KEY`.

#### Gemini 🌟

1. Open Google AI Studio: https://aistudio.google.com/app/apikey.
2. If needed, sign in with your Google account.
3. Create or import a Google Cloud project in AI Studio.
4. Generate a Gemini API key and save it in `.env` as `GEMINI_API_KEY`.

#### Microsoft Copilot (Azure OpenAI) ☁️

1. Go to the Azure Portal and create an **Azure OpenAI** resource.
2. Once created, open the resource and go to **Keys and Endpoint** to copy your key and endpoint.
3. In **Azure OpenAI Studio**, deploy a model (e.g. `gpt-4o`) and note the deployment name.
4. Set the four values in `.env`:
   - `COPILOT_API_KEY` — the API key from Keys and Endpoint.
   - `COPILOT_API_ENDPOINT` — the endpoint URL (e.g. `https://your-resource.openai.azure.com/`).
   - `COPILOT_API_VERSION` — the REST API version (e.g. `2024-10-21`).
   - `COPILOT_DEPLOYMENT` — the default deployment name used when the request omits `deployment`.


## Web UI 🖥️

A server-rendered web UI (FastAPI + Jinja2 + HTMX + Bootstrap) is available for calling `POST /api/v1/generate` from a browser, without writing any JSON or `curl` command by hand.

### Open it

1. Start the app (`uv run python main.py`, `uv run uvicorn ...`, or the Docker container — any of the ways described above).
2. Open **http://127.0.0.1:8080/** in a browser.

### How to use it

1. **Provider** — pick one from the dropdown: OpenAI, Claude, Gemini, or Copilot. The **Provider parameters** section below updates automatically (via HTMX, no page reload) to show only the fields that provider actually supports — e.g. `top_k` disappears for OpenAI/Copilot, and Claude shows a *Use temperature / Use top_p* toggle instead of both at once, since Anthropic only accepts one of the two per request.
2. **Model** — the model or deployment name (e.g. `gpt-4o-mini`, `claude-3-5-sonnet-20241022`, `gemini-2.5-flash`). For Copilot this doubles as the deployment name unless you set **Deployment override**.
3. **Prompt** — the text sent to the model.
4. **Provider parameters** — each numeric field (`temperature`, `top_p`, `top_k`, `max_tokens`) is a slider paired with a number input, labeled with its valid `min`/`max` range and default for the selected provider (see [Per-provider parameter support](#per-provider-parameter-support-verified-) below for the full table and sources). Values outside the shown range, or missing required fields (e.g. Claude's `max_tokens`), are rejected both in the browser and again on the server before any request is sent to the provider.
5. For Copilot, two extra optional text fields appear: **Deployment override** and **API version**.
6. Click **Generate**. The button disables while the request is in flight; the result — the generated text, or a Bootstrap error alert with the same error codes as the JSON API (`VALIDATION_ERROR`, `UNSUPPORTED_PROVIDER`, `PROVIDER_MISCONFIGURED`, `INTERNAL_ERROR`) — replaces the results panel in place.

> The UI is a thin presentation layer: it calls the exact same `AIService`/adapter code as the JSON API described below, so behavior (including required API keys in `.env`) is identical either way.

## Web API 🌐

### URL

`POST http://127.0.0.1:8080/api/v1/generate`

### Request JSON

```json
{
	"provider": "openai_api",
	"model": "gpt-4o-mini",
	"prompt": "Write a short summary about hexagonal architecture.",
	"temperature": 0.2,
	"top_p": 0.9,
	"top_k": 40,
	"max_tokens": 200
}
```

For Microsoft Copilot (Azure OpenAI), two additional optional fields are available:

| Field | Type | Description |
|---|---|---|
| `deployment` | `string` | Azure OpenAI deployment name. Overrides `model` and the `COPILOT_DEPLOYMENT` env var. |
| `api_version` | `string` | Azure OpenAI REST API version (accepted but deferred to v2; the env-level version is used). |

Example Copilot request:

```json
{
	"provider": "copilot_api",
	"model": "gpt-4o",
	"prompt": "Write a short summary about hexagonal architecture.",
	"temperature": 0.2,
	"top_p": 0.9,
	"max_tokens": 200,
	"deployment": "gpt-4o-prod"
}
```

### Response JSON

```json
{
	"success": true,
	"provider": "openai_api",
	"model": "gpt-4o-mini",
	"result": "Hexagonal architecture keeps business logic isolated from external systems.",
	"error": null
}
```

### Provider identifiers

All provider values are **lowercase**. Sending an uppercase value (e.g. `"OPENAI_API"`) returns a `422 Unprocessable Entity`.

| Provider | `provider` value |
|---|---|
| OpenAI | `openai_api` |
| Claude (Anthropic) | `claude_api` |
| Gemini (Google) | `gemini_api` |
| Microsoft Copilot (Azure OpenAI) | `copilot_api` |

### Error responses

The API returns structured error bodies for `400` and `500` responses:

```json
{ "code": "UNSUPPORTED_PROVIDER", "message": "Provider 'x' is not supported.", "supported": ["openai_api", "claude_api", "gemini_api", "copilot_api"] }
{ "code": "PROVIDER_MISCONFIGURED", "message": "..." }
{ "code": "INTERNAL_ERROR",        "message": "An unexpected error occurred." }
```

### API 💻

You can call the API directly with `curl` and format the response with `jq`:

```bash
curl -s -X POST http://127.0.0.1:8080/api/v1/generate \
	-H "Content-Type: application/json" \
	-d '{
		"provider": "gemini_api",
		"model": "gemini-2.5-flash",
		"prompt": "Escribe un resumen breve sobre Python.",
		"temperature": 0.2,
		"top_p": 0.9,
		"top_k": 20,
		"max_tokens": 256
	}' | jq .
```

Microsoft Copilot example:

```bash
curl -s -X POST http://127.0.0.1:8080/api/v1/generate \
	-H "Content-Type: application/json" \
	-d '{
		"provider": "copilot_api",
		"model": "gpt-4o",
		"prompt": "Escribe un resumen breve sobre Python.",
		"temperature": 0.2,
		"top_p": 0.9,
		"max_tokens": 256,
		"deployment": "gpt-4o-prod"
	}' | jq .
```

### Tips ✨

- Make sure the server is running before you send the request.
- Use `jq` to read the JSON response in a nicer format.
- You can change the provider, model, and sampling parameters as needed.
- You can use Postman or other tools to call the API.
- For Copilot, `deployment` takes priority over `model` and `COPILOT_DEPLOYMENT` for selecting the Azure deployment.


## Project Structure

```text
application/            # Core use-case logic and data contracts
├── domain/
│   └── ai_provider.py  # AIProvider enum (openai_api, claude_api, gemini_api, copilot_api)
├── dto/
│   ├── ai_request.py   # Request data model (provider, model, prompt, sampling params, deployment, api_version)
│   └── ai_response.py  # Response data model
├── ports/
│   └── ai_provider_port.py  # Provider interface definition
└── services/
    └── ai_service.py   # Service that calls the provider and closes client

bootstrap/              # Factory and dependency wiring for adapters
├── ai_factory.py       # Creates the selected AI provider adapter
└── dependencies.py     # Helper to build service instances

infrastructure/         # External adapters and API layer
├── adapters/
│   ├── openai_adapter.py   # Adapter for OpenAI API
│   ├── claude_adapter.py   # Adapter for Claude (Anthropic)
│   ├── gemini_adapter.py   # Adapter for Gemini (Google)
│   └── copilot_adapter.py  # Adapter for Microsoft Copilot (Azure OpenAI)
└── api/
    ├── app.py          # FastAPI application: JSON API routes + mounts the web UI router
    ├── web.py           # Web UI routes (GET /, GET /ui/fields, POST /ui/generate)
    ├── provider_ui.py   # Per-provider parameter matrix (min/max/default) used by the web UI
    ├── templates/        # Jinja2 templates (base page + HTMX fragments)
    └── static/           # CSS/JS assets served at /static

config.py               # Global configuration settings (includes COPILOT_* env-var names)
main.py                 # Application entrypoint (starts the server)
pyproject.toml          # Project metadata and dependencies

Dockerfile              # Multi-stage production image (builder + runtime stages)
docker-compose.yml      # Development stack with live reload and .env injection
.dockerignore           # Excludes secrets, caches, and dev artifacts from the build context
```

## Claude Code Agents 🤖

This project includes custom Claude Code agents to accelerate development. Each agent has a specific role and should be used at the right stage of the workflow.

### Available Agents 🧠

#### software-architect 🏛️

A senior software architect that designs features and systems from scratch. It produces a complete RFC document — use case diagrams, package diagrams, class diagrams, sequence diagrams, entity-relationship diagrams, JSON data models, and OpenAPI/Swagger contracts.

**When to use it:**
- You need to add a new feature and want a full architectural design before writing code.
- You need to define packages, classes, data models, API contracts, or design patterns.
- You want a structured RFC that the entire team (Backend, Frontend, QA) can follow.

> ⚠️ This agent **does not write production code**. It delivers the design document and defers implementation to the team or the `backend-developer` agent.

**How to use it:**

```
@software-architect Design a new provider adapter for Microsoft Copilot LLM API following the hexagonal architecture already in place.
```

The agent will explore the codebase, ask clarifying questions, evaluate alternatives, and write an RFC file under `docs/rfc/`.

---

#### backend-developer 💻

A senior Python backend developer that turns an already-decided architecture design (RFC, ADR) into functional, tested code. It advances step by step, pausing for human validation between changes.

**When to use it:**
- An RFC or ADR has been approved and you want to implement it.
- You need to add REST endpoints, business logic, data models, or unit/integration tests.
- You want code that follows the project's conventions, SOLID principles, and quality gates.

> ⚠️ This agent **does not make architecture decisions**. If a change requires rethinking the design, it stops and defers to the architect.

**How to use it:**

```
@backend-developer Implement the Microsoft Copilot adapter described in docs/rfc/20250601-copilot-adapter.md.
```

The agent will read the RFC, explore the codebase, present an implementation plan for your approval, and then implement each phase waiting for your validation before continuing.

---

### Recommended Workflow 🔄

```
1. 🏛️  software-architect  →  RFC document in docs/rfc/
2. ✅  Human review        →  Approve or adjust the RFC
3. 💻  backend-developer   →  Implementation + tests, phase by phase
4. ✅  Human validation    →  Review each phase before the next one
```

## Hexagonal Architecture 🧩

This project uses hexagonal architecture to keep the core logic independent from external services.

- `application` contains the use case logic and the data contracts.
- `application/ports` defines the interface that every AI provider must follow.
- `bootstrap` wires the selected provider with the service layer.
- `infrastructure/adapters` contains the concrete clients for OpenAI, Claude, Gemini, and Microsoft Copilot (Azure OpenAI).
- `infrastructure/api` exposes the FastAPI web layer.
- `main.py` starts the server.

## AI Providers 🔌

### Per-provider parameter support (verified) ✅

- **OpenAI**: forwards `model`, `prompt`, `temperature`, `top_p`. OpenAI Chat/Completions supports `temperature` and `top_p`, but **does not support** `top_k` in the current chat API.
- **Claude (Anthropic)**: forwards `model`, `prompt`, `temperature`, `max_tokens`, `top_k`. Claude supports `temperature` or `top_p` and `top_k` (the `top_p` and `temperature` parameters cannot be combined).
- **Gemini (Google)**: forwards `model`, `prompt`, `temperature`, `top_p`, `top_k`. Gemini supports `temperature`, `top_p`, and `top_k` via `GenerateContentConfig`.
- **Microsoft Copilot (Azure OpenAI)**: forwards `deployment` (or falls back to `model` / `COPILOT_DEPLOYMENT`), `prompt`, `temperature`, `top_p`, `max_tokens`. **Does not support `top_k`** — Azure OpenAI rejects it with a 400. Also accepts `api_version` in the request body (deferred to v2; the env-level version is used in v1).

| Parameter | OpenAI | Claude | Gemini | Copilot (Azure) |
|---|---|---|---|---|
| `model` / `deployment` | ✅ | ✅ | ✅ | ✅ (see note) |
| `prompt` | ✅ | ✅ | ✅ | ✅ |
| `temperature` | ✅ | ✅ (XOR top_p) | ✅ | ✅ |
| `top_p` | ✅ | ✅ (XOR temperature) | ✅ | ✅ |
| `top_k` | ❌ | ✅ | ✅ | ❌ |
| `max_tokens` | — | ✅ (required) | ✅ | ✅ |
| `deployment` | — | — | — | ✅ (overrides `model`) |
| `api_version` | — | — | — | accepted, v2 |

> **Copilot deployment note:** Azure OpenAI requires a deployment name (not a raw model ID). The adapter resolves it in this order: `deployment` field → `model` field → `COPILOT_DEPLOYMENT` env var.

### Parameter Meaning (common behavior) 🧠

The parameters control sampling randomness and diversity in a similar way across providers, but availability differs:

- `temperature` (all providers): float that scales the model probability distribution. Lower (e.g. 0.2) → more deterministic; higher (e.g. 1.0) → more random.
- `top_p` (OpenAI, Gemini, Copilot): nucleus sampling threshold. The model samples from the smallest token set whose cumulative probability ≥ `top_p`.
- `top_k` (Claude, Gemini): hard cutoff to the top `k` most probable tokens; sampling is limited to those tokens.

Summary: OpenAI (temperature, top_p), Claude (temperature, top_k), Gemini (temperature, top_p, top_k), Copilot/Azure (temperature, top_p, max_tokens — no top_k).
