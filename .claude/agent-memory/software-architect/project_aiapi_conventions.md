---
name: project-aiapi-conventions
description: AIAPI hexagonal conventions, adapter pattern, and known tech debt as of 2026-06
metadata:
  type: project
---

AIAPI architecture facts confirmed by reading source (2026-06-21):

- Hexagonal: `application` core (ports/services/dto) depends only on `AIProviderPort` ABC.
  Adapters in `src/infrastructure/adapters/` wrap each SDK. Factory in
  `src/bootstrap/ai_factory.py` maps a provider string via match/case. DI helper in
  `src/bootstrap/dependencies.py`. Driving adapter is FastAPI `src/infrastructure/api/app.py`.
- Port contract: `generate_content(params: dict) -> str` and `close_client()`. Adapters
  build their SDK client in `__init__` reading the API key via `os.environ.get(Config.X)`.
- `Config` (config.py) holds only env var NAME strings. `.env` loaded with `load_dotenv()`.
- Provider identifier strings are duplicated string constants in the factory
  (CLAUDE_API/GEMINI_API/OPENAI_API) and not validated in `AIRequest`. A shared Enum is
  the recommended fix and is a precondition for cleanly adding new providers.
- Docstring style: uppercase section headers (DESCRIPTION, ARGS, RETURN, EXCEPTIONS, EXAMPLES).
- Quality gates: ruff (E,F,UP,B,SIM,I,S/bandit), mypy, pytest. Tests mirror src/ tree,
  use unittest.TestCase + Mock, pythonpath=["src"].
- Routes are `async def` but SDK calls are blocking — known tech debt (event-loop blocking).

**Why:** designing a new Copilot/Azure OpenAI provider; must follow these conventions exactly.
**How to apply:** new provider = new adapter + factory entry + Config env names, core untouched.
