FROM python:3.14-slim AS base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /bin/

FROM base AS build
WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ ./src/
COPY README.md LICENSE ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST="0.0.0.0"
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN useradd --no-create-home --no-log-init -s /sbin/nologin -u 1001 appuser
USER appuser

COPY --from=build --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=build --chown=appuser:appuser /app/src /app/src

EXPOSE 8000

CMD ["python", "-m", "osint_engine"]
