FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.12 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./

RUN uv sync --no-dev --extra api

COPY src/ ./src/
COPY sdk/ ./sdk/

RUN addgroup --system matrix \
    && adduser --system --ingroup matrix --home /app matrix \
    && mkdir -p /app/logs \
    && chown -R matrix:matrix /app

USER matrix

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]

CMD ["/app/.venv/bin/uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
