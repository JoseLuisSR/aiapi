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
