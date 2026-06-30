# Docker Containerization — Implementation Plan

**Date:** 2026-06-28
**Scope:** Containerize `aiapi` with a production-ready Dockerfile (multi-stage),
a development Docker Compose definition, and a `.dockerignore` file.

---

## Context and pre-implementation findings

### Critical issue: `main.py` binds to `127.0.0.1`

`main.py` calls `uvicorn.run(..., host="127.0.0.1", port=8080, reload=True)`.
Inside a container `127.0.0.1` resolves only to the container's loopback interface;
the server is unreachable from outside. **The Dockerfile CMD must bypass `main.py`
and invoke Uvicorn directly on `0.0.0.0`.**

```
CMD ["uvicorn", "src.infrastructure.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

This avoids modifying application source code for a containerization concern.

### Dependency manager: `uv`

`uv` is not present on the base `python:3.13.5-slim` image.
The recommended pattern is to copy the `uv` binary from the official
`ghcr.io/astral-sh/uv` image in the builder stage.

### Import resolution

All modules use absolute imports rooted at the project root
(e.g. `from src.application.dto.ai_request import AIRequest`).
Uvicorn adds the current working directory to `sys.path` when loading the
application module, so `WORKDIR /app` + the `src.infrastructure.api.app:app`
app string resolves correctly without altering `PYTHONPATH`.

### API keys / secrets

Keys are read at runtime via `python-dotenv` from `.env`.
They must **never** be baked into an image layer (no `ARG` / `ENV` for secrets in
the Dockerfile). The `.dockerignore` excludes `.env`, and the Compose definition
injects them at start-up with `env_file: .env`.

---

## Files to create

| # | File path (from project root) | Purpose |
|---|---|---|
| 1 | `.dockerignore` | Exclude secrets, artifacts, and dev files from build context |
| 2 | `Dockerfile` | Multi-stage production image |
| 3 | `docker-compose.yml` | Local development orchestration |

---

## Phase 1 — `.dockerignore`

**Path:** `/Users/joseluissr/Workspace/sw/python/aiapi/.dockerignore`

Exclude everything that should not land in the build context: secrets, virtual
environments, caches, test artifacts, IDE config, and VCS metadata. This reduces
build context size and prevents accidental secret leakage.

```dockerignore
# ── Secrets (never bake into image) ──────────────────────────────────────────
.env
.env.*
!.env.example

# ── Virtual environment (rebuilt inside the image) ───────────────────────────
.venv/

# ── Python bytecode / caches ─────────────────────────────────────────────────
__pycache__/
*.pyc
*.pyo
*.pyd

# ── Testing and quality-tool artifacts ───────────────────────────────────────
tests/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
.pre-commit-config.yaml

# ── Version control ───────────────────────────────────────────────────────────
.git/
.github/

# ── IDE / editor ──────────────────────────────────────────────────────────────
.vscode/
.idea/

# ── Documentation (not needed at runtime) ────────────────────────────────────
docs/
*.md
!README.md

# ── Agent memory (internal tooling) ──────────────────────────────────────────
.claude/

# ── uv runtime artefacts ─────────────────────────────────────────────────────
.python-version

# ── System ───────────────────────────────────────────────────────────────────
.DS_Store
Thumbs.db
```

---

## Phase 2 — `Dockerfile` (multi-stage)

**Path:** `/Users/joseluissr/Workspace/sw/python/aiapi/Dockerfile`

### Stage design

```
builder  →  installs uv, resolves + installs runtime deps into /app/.venv
runtime  →  copies .venv from builder, copies app source, drops privileges
```

### Layer ordering rationale (cache efficiency)

1. Copy `pyproject.toml` + `uv.lock` **before** source code.
   These change infrequently; dependency installation is cached unless the lock
   file changes.
2. Copy `config.py` before `src/` — it changes less often than feature code.
3. Copy `src/` last — most frequently modified.

### Non-root user

A dedicated `appuser` (UID 1000) is created in the runtime stage.
The application directory is owned by that user; the container process runs
without root privileges.

### Full Dockerfile content

```dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 · builder
#   Installs uv and resolves all runtime Python dependencies.
#   The resulting .venv is the only artefact copied to the runtime stage.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13.5-slim AS builder

# Bring in the uv binary from the official distribution image (pinned minor).
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests first to maximise Docker layer cache hits.
COPY pyproject.toml uv.lock ./

# Install only runtime dependencies; skip dev group; disable the uv cache so
# no cache data is stored in this layer.
RUN uv sync --frozen --no-dev --no-cache

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 · runtime
#   Minimal image: no uv, no dev tools, no source of secrets.
#   Runs as a non-root user.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13.5-slim AS runtime

# Create a non-root user for the application process.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage.
COPY --from=builder /app/.venv /app/.venv

# Copy application source ordered from least to most frequently changed.
COPY config.py ./
COPY src/ ./src/

# Activate the virtual environment by prepending it to PATH.
ENV PATH="/app/.venv/bin:$PATH"

# Prevent Python from writing .pyc files and buffer stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Hand off ownership of the working directory to the non-root user.
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Invoke Uvicorn directly on 0.0.0.0 so the server is reachable from outside
# the container. This bypasses main.py (which binds to 127.0.0.1).
CMD ["uvicorn", "src.infrastructure.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Why `main.py` is not copied

`main.py` is not needed at runtime — the CMD calls `uvicorn` directly.
Omitting it keeps the image smaller and removes `reload=True` from the
production path without modifying source code.

---

## Phase 3 — `docker-compose.yml`

**Path:** `/Users/joseluissr/Workspace/sw/python/aiapi/docker-compose.yml`

### Design decisions

- **`env_file: .env`** — injects all provider API keys at container start-up;
  the file is never copied into the image (excluded by `.dockerignore`).
- **Source-only volume mounts** — only `src/` and `config.py` are bind-mounted,
  preserving the `/app/.venv` installed by the builder stage.
  Mounting the entire project root would overlay the `.venv` with the empty
  host `.venv` (or its absence).
- **`--reload` flag** — enables Uvicorn's file-watcher for live reload during
  development. The production `CMD` in the Dockerfile does NOT use `--reload`.
- **Healthcheck** — polls `/health` using Python's standard library so no
  additional tooling (`curl`, `wget`) needs to be installed in the image.
- **Named network** — isolates the service; useful when extending the compose
  file with additional services (e.g. a mock LLM, a database).

### Full docker-compose.yml content

```yaml
services:
  aiapi:
    build:
      context: .
      target: runtime
    image: aiapi:dev
    container_name: aiapi
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      # Bind-mount only the application source so the .venv layer is preserved.
      - ./src:/app/src
      - ./config.py:/app/config.py
    # Override CMD to enable live reload for local development.
    command: >
      uvicorn src.infrastructure.api.app:app
      --host 0.0.0.0
      --port 8080
      --reload
    healthcheck:
      test:
        - "CMD"
        - "python"
        - "-c"
        - "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    networks:
      - aiapi-net

networks:
  aiapi-net:
    driver: bridge
```

---

## Phase 4 — Build and run commands

### Build the image

```bash
# From the project root
docker build -t aiapi:latest .
```

### Run the container (production-like, API keys from .env)

```bash
docker run --rm \
  --env-file .env \
  -p 8080:8080 \
  aiapi:latest
```

### Run with individual environment variables

```bash
docker run --rm \
  -e OPENAI_API_KEY="sk-..." \
  -e CLAUDE_API_KEY="sk-ant-..." \
  -e GEMINI_API_KEY="AIza..." \
  -p 8080:8080 \
  aiapi:latest
```

### Start the development stack with Docker Compose

```bash
# Build the image and start the service
docker compose up --build

# Start in detached mode
docker compose up --build -d

# Tail logs
docker compose logs -f aiapi

# Stop and remove the container
docker compose down
```

### Smoke-test the running container

```bash
# Health check
curl http://localhost:8080/health

# Generate endpoint (replace values as needed)
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai_api",
    "model": "gpt-4o-mini",
    "prompt": "Hello, world!",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

---

## Security notes on API key handling

| Method | Safe? | Notes |
|---|---|---|
| `docker run --env-file .env` | Yes | Keys injected at runtime; not in image layers |
| `docker compose` with `env_file: .env` | Yes | Same; `.env` excluded from build context |
| `docker run -e KEY=value` | Yes | Runtime only; visible in `docker inspect` (acceptable for local dev) |
| `ENV KEY=value` in Dockerfile | **No** | Baked into image layers; visible in `docker history` |
| `ARG KEY` + `ENV KEY=$KEY` in Dockerfile | **No** | Same problem; `docker history --no-trunc` reveals ARG values |
| Docker Swarm secrets / Kubernetes secrets | Production best practice | Mounted as files at `/run/secrets/`; not in env |

The `.dockerignore` ensures `.env` is never included in the build context even
if a `COPY . .` instruction were added inadvertently.

---

## Implementation order

1. Create `.dockerignore` — prerequisite for a clean build context.
2. Create `Dockerfile` — build and verify image starts correctly.
3. Create `docker-compose.yml` — verify compose stack starts, healthcheck passes.
4. Run smoke tests against the running container.

---

## Pending / out-of-scope

- Modifying `main.py` to read `HOST`/`PORT` from environment variables
  (tracked as tech-debt item 4 in CLAUDE.md — async/blocking concern is related).
- A CI pipeline step to build and push the image to a registry.
- Production secrets management beyond `--env-file` (Vault, K8s secrets, etc.).
