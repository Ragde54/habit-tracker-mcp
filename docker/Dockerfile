# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv venv $VIRTUAL_ENV && \
    uv sync --no-dev --frozen

# ---- Stage 2: final ----
FROM python:3.12-slim AS final

WORKDIR /app

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN mkdir -p /app/data && \
    chown appuser:appgroup /app/data && \
    chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV DATABASE_URL="sqlite:////app/data/habit_tracker.db"

USER appuser

ENTRYPOINT ["./entrypoint.sh"]
