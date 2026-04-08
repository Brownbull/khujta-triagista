FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy source first so pyproject.toml can find the package
COPY pyproject.toml .
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY static/ static/
COPY templates/ templates/

# Install deps (non-editable) + dev deps for testing
RUN pip install --no-cache-dir ".[dev]"

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
