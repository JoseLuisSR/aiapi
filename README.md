# AIAPI 🤖

AIAPI is a small web service that sends one generation request to different AI providers and returns a standard JSON response. It supports OpenAI, Claude, and Gemini.

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

## Configuration 🔧

This project reads its secrets from a `.env` file in the project root. Create it like this:

```dotenv
# OpenAI
OPENAI_API_KEY="your_openai_api_key"

# Claude
CLAUDE_API_KEY="your_claude_api_key"

# Gemini
GEMINI_API_KEY="your_gemini_api_key"
```

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


## Web API 🌐

### URL

`POST http://127.0.0.1:8080/api/v1/generate`

### Request JSON

```json
{
	"provider": "OPENAI_API",
	"model": "gpt-4o-mini",
	"prompt": "Write a short summary about hexagonal architecture.",
	"temperature": 0.2,
	"top_p": 0.9,
	"top_k": 40,
	"max_tokens": 200
}
```

### Response JSON

```json
{
	"success": true,
	"provider": "OPENAI_API",
	"model": "gpt-4o-mini",
	"result": "Hexagonal architecture keeps business logic isolated from external systems.",
	"error": null
}
```

### API 💻

You can call the API directly with `curl` and format the response with `jq`:

```bash
curl -s -X POST http://127.0.0.1:8080/api/v1/generate \
	-H "Content-Type: application/json" \
	-d '{
		"provider": "GEMINI_API",
		"model": "gemini-2.5-flash",
		"prompt": "Escribe un resumen breve sobre Python.",
		"temperature": 0.2,
		"top_p": 0.9,
		"top_k": 20,
		"max_tokens": 256
	}' | jq .
```

### Tips ✨

- Make sure the server is running before you send the request.
- Use `jq` to read the JSON response in a nicer format.
- You can change the provider, model, and sampling parameters as needed.
- You can use Postman or other tools to call the API.


## Project Structure

```text
application/            # Core use-case logic and data contracts
├── dto/
│   ├── ai_request.py   # Request data model
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
│   └── gemini_adapter.py   # Adapter for Gemini (Google)
└── api/
    └── app.py          # FastAPI application and route definitions

config.py               # Global configuration settings
main.py                 # Application entrypoint (starts the server)
pyproject.toml          # Project metadata and dependencies
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
- `infrastructure/adapters` contains the concrete clients for OpenAI, Claude, and Gemini.
- `infrastructure/api` exposes the FastAPI web layer.
- `main.py` starts the server.

## AI Providers 🔌

### Per-provider parameter support (verified) ✅

- **OpenAI**: forwards `model`, `prompt`, `temperature`, `top_p`. OpenAI Chat/Completions supports `temperature` and `top_p`, but **does not support** `top_k` in the current chat API.
- **Claude (Anthropic)**: forwards `model`, `prompt`, `temperature`, `max_tokens`, `top_k`. Claude supports `temperature` or `top_p` and `top_k` (the `top_p` and `temperature` parameters can not be combine).
- **Gemini (Google)**: forwards `model`, `prompt`, `temperature`, `top_p`, `top_k`. Gemini supports `temperature`, `top_p`, and `top_k` via `GenerateContentConfig`.

### Parameter Meaning (common behavior) 🧠

The parameters control sampling randomness and diversity in a similar way across providers, but availability differs:

- `temperature` (all providers): float that scales the model probability distribution. Lower (e.g. 0.2) → more deterministic; higher (e.g. 1.0) → more random.
- `top_p` (OpenAI, Gemini): nucleus sampling threshold. The model samples from the smallest token set whose cumulative probability ≥ `top_p`.
- `top_k` (Claude, Gemini): hard cutoff to the top `k` most probable tokens; sampling is limited to those tokens.

Summary: the conceptual meaning (control of randomness/diversity) is the same across providers, but which parameters each provider accepts differs: OpenAI (temperature, top_p), Claude (temperature, top_k), Gemini (temperature, top_p, top_k).
