# SRE Triage Agent

AI-powered SRE Incident Intake & Triage Agent — analyzes incident reports against the [Solidus](https://github.com/solidusio/solidus) e-commerce codebase and produces structured triage with severity, root cause hypothesis, affected files, and recommended actions.

## Quick Start

```bash
# 1. Copy environment file and add your Anthropic API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 2. Start everything
docker compose up --build -d

# 3. Open the app
open http://localhost:8100
```

The app seeds itself with 4 sample incidents on first startup.

## Access Credentials

| Service | URL | Credentials |
|---------|-----|-------------|
| **App** | http://localhost:8100 | No auth required |
| **Langfuse** (LLM Observability) | http://localhost:3100 | `admin@sre-triage.local` / `admin123` |
| **API Docs** | http://localhost:8100/docs | Swagger UI |
| **Health Check** | http://localhost:8100/health | — |
| **Observability Status** | http://localhost:8100/api/observability | — |

> Langfuse account, project, and API keys are **auto-created** on first startup. No manual setup needed.

## Demo Flow (3 minutes)

1. **View seeded incidents** at `/incidents` — 2 triaged (P1, P2) + 2 untriaged
2. **Submit a new incident** via `/incidents/new` — describe an e-commerce issue
3. **Run AI Triage** — click the button on the detail page, watch Claude analyze it
4. **See results** — severity, root cause, affected Solidus files, recommended actions
5. **Check dispatch** — expand ticket, email, and chat cards to see generated content
6. **View Langfuse** — open http://localhost:3100 to see LLM traces with token usage

## Architecture

```
User → FastAPI + HTMX UI
         ↓
    Guardrail (injection detection, PII scan, rate limiting)
         ↓
    Triage Agent (Claude Haiku + Solidus codebase index)
         ↓
    Dispatch (ticket + email + chat notifications)
         ↓
    Observability (OpenTelemetry spans + Langfuse LLM traces)
```

## Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL
- **Frontend**: HTMX, Jinja2, CSS (Linear/Modern design system)
- **AI**: Anthropic Claude Haiku 4.5 (tool_use for structured output)
- **Observability**: OpenTelemetry, Langfuse
- **Infrastructure**: Docker Compose, Redis

## Port Map

| Service | Port |
|---------|------|
| App | 8100 |
| PostgreSQL | 5433 |
| Redis | 6380 |
| Langfuse | 3100 |

## Testing

```bash
# Unit + integration tests (inside Docker)
docker compose exec app pytest tests/ -v

# E2E tests with screenshots (from host, requires Playwright)
npx playwright test

# Lint
docker compose exec app ruff check app/ tests/
```

## Project Structure

```
app/
├── config.py                 # Settings (env vars)
├── main.py                   # FastAPI app + lifespan
├── database.py               # Async SQLAlchemy
├── models/                   # ORM models (incident, ticket, notification)
├── schemas/                  # Pydantic DTOs
├── routes/                   # API + HTML page routes
├── pipeline/
│   ├── guardrail/            # Injection detection, PII scan, rate limiting
│   ├── triage/               # Claude AI agent (structured triage)
│   └── dispatch/             # Ticket + notification creation
└── services/
    ├── codebase_indexer.py   # Solidus repo keyword index
    ├── observability.py      # OpenTelemetry + Langfuse setup
    ├── seed_data.py          # Sample incidents for dev
    └── seed_langfuse.py      # Auto-create Langfuse account/keys
```
