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
| **10. Extras** | Severity reasoning, runbooks, dedup | COULD | 🔲 Pending | — | — |
| **11. Documentation** | README, AGENTS_USE.md, SCALING.md, QUICKGUIDE.md, LICENSE | MUST | ✅ Done | `phase11` | — |
| **12. Demo Video** | 3-min YouTube walkthrough | MUST | 🔲 Pending | — | — |

**Test total: 77 pytest + 8 Playwright E2E**

---

## Current State (Apr 8, 2026)

### What works end-to-end
```
Submit incident → Guardrail scan → AI triage (Claude Haiku) → 
Auto-dispatch (ticket + email + chat) → Detail page with full results
```

### What's in the app
- Linear/Modern dark UI with Outfit font, ambient blobs, glass cards
- Team icons and badges (💳 Payments, ⚙ Platform, 🎨 Frontend, ☁ Infrastructure, 🔒 Security, 📦 Fulfillment)
- Incident ID search bar (partial UUID lookup)
- Sticky incident header with ID, status, severity, team
- Expandable dispatch cards showing ticket/email/chat content
- Integration-ready notices (mock → Jira/SendGrid/Slack)
- Seed data: 4 sample incidents on startup
- Langfuse auto-seeded with dev account + API keys

### What's missing
- **Phase 9**: Incident lifecycle buttons (acknowledge, resolve), reporter notification on resolution
- **Phase 10**: Severity reasoning, runbook suggestions (if time)
- **Phase 11**: AGENTS_USE.md, SCALING.md, architecture diagrams (README done)
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
