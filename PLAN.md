# Project Plan — SRE Triage Agent (ECC Workflow)

> AgentX Hackathon, April 7-9, 2026  
> Workflow: ECC (Everything Claude Code)  
> Original plan: [docs/neo-analysis/04-execution-plan.md](docs/neo-analysis/04-execution-plan.md)

---

## Phase Status

| Phase | Scope | Priority | Status | Commit | Tests |
|-------|-------|----------|--------|--------|-------|
| **1. Scaffold** | Docker, FastAPI, SQLAlchemy, Alembic, CI | MUST | ✅ Done | `36e6e75` | — |
| **2. Incident UI** | Form, list, detail pages, file uploads, HTMX | MUST | ✅ Done | `60858d8` | 14 |
| **3. Triage Agent** | Claude Haiku tool_use, codebase indexer | MUST | ✅ Done | `4ec2c31` | 15 |
| **4. Context Loader** | Solidus repo scan, keyword index, file search | MUST | ✅ Done | *(merged into Phase 3)* | — |
| **5. Ticket Service** | Auto-create ticket after triage, labels, assignee | MUST | ✅ Done | `8c487ee` | 3 |
| **6. Notifications** | Email + chat mock dispatch, on-call roster | MUST | ✅ Done | `8c487ee` | 3 |
| **7. Guardrails** | Injection detection, PII scan, rate limiting | SHOULD | ✅ Done | `814c885` | 18 |
| **8. Observability** | OpenTelemetry spans, Langfuse LLM tracing | SHOULD | ✅ Done | `4155547` | 4 |
| **9. Resolution** | Acknowledge/resolve lifecycle, reporter notify | SHOULD | ✅ Done | `phase9` | 8 |
| **10. Extras** | Severity reasoning, runbooks, dedup | COULD | ⏭ Skipped | — | — |
| **11. Documentation** | README, AGENTS_USE.md, SCALING.md, QUICKGUIDE.md, LICENSE | MUST | ✅ Done | `phase11` | — |
| **12. Demo Video** | 3-min YouTube walkthrough | MUST | 🔲 Pending | — | — |
| **13. UI Polish** | Triage button fix, HTMX vendoring, favicon, auto-redirect, seed resilience, health check | SHOULD | ✅ Done | — | — |
| **14. UI Redesign** | Ops dashboard + chat view + settings (based on mockup 13) | MUST | ✅ Done | `phase14` | — |
| **15. Agent Providers** | Strategy pattern: Anthropic, LangChain, Managed Agents | MUST | ✅ Done | `phase15` | — |
| **16. Test Updates** | Pytest selectors updated for new UI | MUST | ✅ Done | `phase16` | 80 |

**Test total: 80 pytest + 16 Playwright E2E**

---

## Current State (Apr 8, 2026)

### What works end-to-end
```
Submit incident → Guardrail scan → AI triage (Claude Haiku) → 
Auto-dispatch (ticket + email + chat) → Acknowledge → Resolve → Reporter notified
```

### What's in the app
- Linear/Modern dark UI with Outfit font, ambient blobs, glass cards
- Team icons and badges (Payments, Platform, Frontend, Infrastructure, Security, Fulfillment)
- Incident ID search bar (partial UUID lookup)
- Sticky incident header with ID, status, severity, team
- Acknowledge + Resolve lifecycle with resolution dialog
- Reporter email notification on resolution
- Expandable dispatch cards showing ticket/email/chat content
- Integration-ready notices (mock → Jira/SendGrid/Slack)
- Seed data: 4 sample incidents on startup
- Langfuse auto-seeded with dev account + API keys
- Guardrails: prompt injection detection, PII scan, rate limiting
- Observability: OpenTelemetry spans + Langfuse LLM tracing
- Full documentation: README, AGENTS_USE.md, SCALING.md, QUICKGUIDE.md, LICENSE

### What's remaining
- **Phase 12**: Demo video recording

---

## Phase 9: Resolution Tracker (Done)

**Goal**: Close the incident lifecycle — acknowledge → resolve → notify reporter.

### Delivered
- [x] POST /api/incidents/{id}/acknowledge — moves ticket to in_progress
- [x] POST /api/incidents/{id}/resolve — resolves incident, closes ticket, notifies reporter
- [x] Resolve dialog with resolution type (fix, workaround, not-a-bug, duplicate, won't fix) + notes
- [x] Reporter email notification on resolution (mock)
- [x] Lifecycle buttons in sticky header (Acknowledge, Resolve)
- [x] 8 new tests including full lifecycle test (submit → triage → acknowledge → resolve)

---

## Phase 11: Documentation (Done)

### Deliverables
- [x] README.md — solution intro, quickstart, credentials, architecture
- [x] AGENTS_USE.md — agent docs (9 sections per Anthropic template)
- [x] SCALING.md — 3-tier scaling strategy with diagrams and cost estimates
- [x] QUICKGUIDE.md — juror walkthrough (setup → full demo in 3 minutes)
- [x] LICENSE — MIT

---

## Phase 12: Demo Video (Pending)

### Script
1. Show the app (incidents list with seed data)
2. Submit a new incident through the form
3. Run AI triage — show Claude analyzing against Solidus
4. Show triage results (severity, root cause, related files)
5. Show dispatch (ticket, email, chat notifications)
6. Show Langfuse dashboard with LLM trace
7. Show guardrails (try injection → blocked)
8. Close — architecture overview, what's next

---

## Phase 13: UI Polish (Done)

### Delivered
- [x] Triage button — replaced broken HTMX (JSON swap) with JS fetch + spinner + reload
- [x] Removed orphaned reporter_team dropdown from submit form
- [x] Vendored HTMX to static/htmx.min.js (no CDN dependency)
- [x] Inline SVG favicon (no 404 in DevTools)
- [x] Submit form auto-redirects to incident detail after 1s
- [x] Root `/` redirects to `/incidents`
- [x] Seed data resilience — re-seeds on page visit if DB empty (survives test cleanup)
- [x] Health endpoint checks PostgreSQL connectivity (`ok`/`degraded`)
- [x] Updated PLAN.md with accurate test counts and state

---

## Phase 14: UI Redesign (Pending)

**Goal**: Replace the current top-nav stacked-card UI with a sidebar-based ops dashboard with 3 switchable views, matching [mockup 13](docs/mockups/13-combined-final/mockup.html).

### Architecture Decisions

- **Template strategy**: New `base_dashboard.html` + separate view partials. Old `base.html` kept as fallback.
- **Chat view**: Server-side reconstruction of incident lifecycle into message bubbles. No new models — purely presentational.
- **Sidebar navigation**: Full page loads initially. HTMX partial rendering only for triage polling.
- **Settings**: Theme/font size/font family stored in localStorage, applied via CSS classes/variables.
- **CSS**: New `dashboard.css` alongside (not replacing) old `style.css`.

### New files
- [x] `static/dashboard.css` — all dashboard styles extracted from mockup
- [x] `static/dashboard.js` — settings persistence, acknowledge/resolve/triage JS
- [x] `templates/base_dashboard.html` — sidebar + topbar + content + statusbar shell
- [x] `templates/incidents/dashboard_list.html` — incidents table view
- [x] `templates/incidents/dashboard_detail.html` — KPI strip + compact panels
- [x] `templates/incidents/dashboard_chat.html` — conversation timeline view
- [x] `templates/incidents/dashboard_submit.html` — submit form (dashboard style)
- [x] `templates/incidents/dashboard_not_found.html` — 404 page (dashboard style)

### Modified files
- [x] `app/routes/pages.py` — render new templates, pass `recent_incidents` for sidebar, `?view=chat` query param

### Chat view message reconstruction
```
1. System pill:  "Incident submitted by {reporter} at {time}"
2. User bubble:  description text
3. System pill:  "Guardrail passed — injection: X%, clean"
4. System pill:  "AI triage started — Claude Haiku 4.5"
5. AI bubble:    Triage Assessment (severity, category, component, confidence, team)
6. AI bubble:    Root Cause + Related Files chips
7. AI bubble:    Recommended Actions checklist
8. System pill:  "Auto-dispatch completed"
9. AI bubble:    Dispatch cards (ticket, email, chat)
10. System pill: "Incident resolved at {time}" (if resolved)
```

### Views
| View | URL | Topbar |
|------|-----|--------|
| List | `/incidents` | "All Incidents", no tabs, no actions |
| Detail | `/incidents/{id}` | ID + badges + Detail/Chat tabs + Ack/Resolve |
| Chat | `/incidents/{id}?view=chat` | Same topbar, Chat tab active |

---

## Phase 15: Agent Providers (Pending)

**Goal**: Refactor the triage agent to support 3 provider modes via a strategy pattern.

### Provider interface
```python
class TriageProvider(Protocol):
    async def triage(
        self, description: str, codebase_context: str,
        attachment_descriptions: list[str] | None = None,
    ) -> TriageResult: ...
```

### Providers
| Provider | Env Var | API Key | Status |
|----------|---------|---------|--------|
| `anthropic` | `TRIAGE_PROVIDER=anthropic` | `ANTHROPIC_API_KEY` | Extract from current agent.py |
| `langchain` | `TRIAGE_PROVIDER=langchain` | `GOOGLE_API_KEY` or `GROQ_API_KEY` | LangChain + free LLM (Gemini/Groq) |
| `managed` | `TRIAGE_PROVIDER=managed` | None | Stub returning hardcoded TriageResult |

### New files
- [x] `app/pipeline/triage/provider.py` — Protocol + factory
- [x] `app/pipeline/triage/anthropic_provider.py` — extracted from agent.py
- [x] `app/pipeline/triage/langchain_provider.py` — LangChain + Gemini/Groq
- [x] `app/pipeline/triage/managed_provider.py` — stub/placeholder

### Modified files
- [x] `app/pipeline/triage/agent.py` — thin facade calling provider
- [x] `app/config.py` — `triage_provider`, `google_api_key`, `groq_api_key`
- [x] `pyproject.toml` — add `langchain-core`, `langchain-google-genai`, `langchain-groq`
- [x] `docker-compose.yml` — `TRIAGE_PROVIDER`, `GOOGLE_API_KEY`, `GROQ_API_KEY` env vars
- [x] `.env` — document new vars

### Migration safety
The `run_triage()` function signature stays identical. Routes and tests call `run_triage()` — they never see the provider. Existing tests mock `run_triage` and pass regardless.

---

## Phase 16: Test Updates (Pending)

**Goal**: Update pytest and Playwright tests for the new UI selectors.

### pytest
- API tests (`/api/incidents`) return JSON — **no changes needed**
- Any tests checking HTML responses update selectors to new classes
- Add provider unit tests (mock LLM calls, verify TriageResult shape)

### Playwright E2E
- Update selectors: `.incidents-table` (was `.table`), `.panel` (was `.detail-card`), sidebar nav
- Add `data-testid` attributes to key elements for stability
- Add new tests: view switching (detail ↔ chat), settings persistence, sidebar selection

---

## ECC Workflow Checklist

For each remaining phase:
```
1. Update PLAN.md tasks      → document what to build
2. Implement                 → write code
3. /code-review              → catch issues
4. /verify                   → full verification loop  
5. Commit + push             → ship it
6. Update PLAN.md status     → mark done
```

---

## Commit History

| Commit | Phase | Description |
|--------|-------|-------------|
| `36e6e75` | 1 | Scaffold — Docker, FastAPI, SQLAlchemy |
| `60858d8` | 2 | Incident UI — API, HTMX, file uploads |
| `4ec2c31` | 3+4 | Triage agent + codebase indexer |
| `8c487ee` | 5+6 | Ticket service + notifications |
| `e283a88` | UI | Linear/Modern design system |
| `814c885` | 7 | Guardrails — injection, PII, rate limit |
| `4155547` | 8 | Observability — OTel + Langfuse |
| `bb7c312` | 11 | README (partial) |
