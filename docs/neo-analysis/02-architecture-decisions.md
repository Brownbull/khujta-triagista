# Architecture Decisions

> Locked 2026-04-07. Each decision includes alternatives considered and rationale.

## Decision Log

### D1: Agent Framework → Anthropic Agent SDK (Python)

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Anthropic Agent SDK** | Native Claude, clean tool_use, multimodal built-in | Newer, smaller ecosystem | **SELECTED** |
| LangGraph | Stateful graphs, durable execution, visual state machines | Heavier setup, overkill for single-agent flow | Runner-up |
| CrewAI | Multi-agent out of box | Too opinionated, abstracts too much | Rejected |
| Pydantic AI | Type-safe, clean | Less agent orchestration | Rejected |

**Rationale**: The assignment is a single agent with a linear pipeline (not a multi-agent swarm). Anthropic SDK gives us native multimodal support, structured output via tool_use, and minimal abstraction overhead. In 48 hours, simple wins.

### D2: Web Framework → FastAPI

**Rationale**: Async by default, auto-generates OpenAPI docs (helps reviewers), lightweight Docker image, strong Python ecosystem integration. Serves both the API and a simple Jinja2 frontend.

### D3: LLM → Claude Sonnet (primary) + OpenRouter (fallback)

| LLM | Multimodal | Cost | Notes |
|-----|------------|------|-------|
| **Claude Sonnet** | ✅ Images | Pay-as-go | Primary — best reasoning + multimodal |
| OpenRouter | Multi-provider | Variable | Fallback — shows provider flexibility |
| Gemini Flash | ✅ | Free tier | Budget option for dev/testing |

**Rationale**: Claude Sonnet for demo quality. OpenRouter support documented in .env.example shows judges we're not locked to one provider.

### D4: E-Commerce Codebase → Reaction Commerce

| Repo | Stack | Size | Verdict |
|------|-------|------|---------|
| **Reaction Commerce** | Node.js | ~200K LOC | **SELECTED** |
| eShop | .NET | Large microservices | Too heavy, .NET not our stack |
| Solidus | Rails | Modular | Good alternative |

**Key insight**: The agent doesn't RUN the e-commerce app. It READS the codebase as context for triage. The repo is mounted read-only. We pick for richness of code/docs to analyze, not for runtime compatibility.

### D5: Database → PostgreSQL + Redis

| Service | Purpose |
|---------|---------|
| PostgreSQL | Incident records, ticket state, triage history |
| Redis | Task queue (resolution polling), caching |

**Rationale**: Both have official Docker images, zero-config startup, and are industry standard for SRE tooling.

### D6: Observability → OpenTelemetry + Langfuse

| Layer | Tool | Why |
|-------|------|-----|
| Infrastructure | OpenTelemetry | Industry standard, judges expect it, traces HTTP + DB |
| LLM-specific | Langfuse (OSS) | Self-hosted in Docker, visual trace UI, token/cost tracking |

**Rationale**: OTel shows we know production observability. Langfuse adds LLM-specific tracing (prompts, completions, latency, cost) with a built-in dashboard — essentially free "observability dashboard" bonus points.

### D7: Integrations → Mocked with clean interfaces

```python
# Clean interface pattern — swap mock for real with one import change
class TicketService(Protocol):
    async def create(self, incident: TriagedIncident) -> Ticket: ...
    async def update_status(self, ticket_id: str, status: str) -> None: ...
    async def get(self, ticket_id: str) -> Ticket: ...

class MockTicketService:  # For hackathon
    ...

class LinearTicketService:  # For production (optional)
    ...
```

**Rationale**: Rules explicitly say "mocked components are acceptable if the end-to-end flow is clearly demoable." Clean Protocol interfaces show production thinking without wasting time on API integration.

---

## Full Architecture

```
┌─────────────── Docker Compose ──────────────────────────┐
│                                                          │
│  ┌──────────────────────────────────────────────┐       │
│  │            FastAPI Application                │       │
│  │                                               │       │
│  │  UI (Jinja2)                                  │       │
│  │    └─ /submit (text + image upload)           │       │
│  │    └─ /incidents (status dashboard)           │       │
│  │    └─ /incidents/{id} (detail + timeline)     │       │
│  │                                               │       │
│  │  API                                          │       │
│  │    └─ POST /api/incidents                     │       │
│  │    └─ GET  /api/incidents/{id}                │       │
│  │    └─ POST /api/incidents/{id}/resolve        │       │
│  │                                               │       │
│  │  Agent Pipeline                               │       │
│  │    └─ Ingest → Guardrail → Triage →          │       │
│  │       Dispatch → Resolve                      │       │
│  │                                               │       │
│  │  ════════════════════════════════════════     │       │
│  │  OpenTelemetry + Langfuse instrumentation     │       │
│  └──────────────────────────────────────────────┘       │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │ Postgres │  │  Redis   │  │  Langfuse (OSS)  │      │
│  │ :5432    │  │  :6379   │  │  :3000           │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐       │
│  │  Reaction Commerce (read-only volume)         │       │
│  └──────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

### Docker Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| app | Custom (Python 3.12) | 8000 | FastAPI + Agent |
| postgres | postgres:16-alpine | 5432 | Incident/ticket storage |
| redis | redis:7-alpine | 6379 | Queue + cache |
| langfuse | langfuse/langfuse | 3000 | LLM observability dashboard |
| langfuse-db | postgres:16-alpine | 5433 | Langfuse's database |
