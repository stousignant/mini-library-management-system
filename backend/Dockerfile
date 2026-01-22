# ------------------------------------------------------------------------------------
# STAGE 1: Builder
# ------------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1. Install dependencies (Cached Layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2. Install Project (Code Layer)
COPY . .
RUN uv sync --frozen --no-dev

# ------------------------------------------------------------------------------------
# STAGE 2: Runtime
# ------------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm

WORKDIR /app

# 1. Copy Virtual Environment
COPY --from=builder /app/.venv /app/.venv

# 2. Copy Application Code
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

# 3. Copy and prepare startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 4. Security: Run as non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["/app/start.sh"]
