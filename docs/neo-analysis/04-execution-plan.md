# Execution Plan

> 12 phases mapped to MoSCoW priorities. ~25h total. Feed into `/gsd:new-project`.

## Time Budget

```
Available: ~48 hours (Apr 7 evening → Apr 9 9PM COT)
Realistic coding: ~25 hours (sleep, breaks, debugging)
Buffer: ~5 hours (unexpected issues)
```

---

## Phase Plan

### MUST — Day 1 (Phases 1–6, ~13h)

These phases deliver a working E2E demo. Without all 6, submission is incomplete.

| Phase | Scope | Est. | Depends On |
|-------|-------|------|------------|
| **1. Scaffold** | Repo structure, Docker skeleton, docker-compose.yml, .env.example, Dockerfile, basic CI | 2h | — |
| **2. Incident UI** | FastAPI + Jinja2 form: text input, image upload, reporter email. Status page listing incidents. | 2h | Phase 1 |
| **3. Triage Agent** | Claude Sonnet multimodal triage: structured output with severity, category, summary, confidence. Core brain of the system. | 4h | Phase 1 |
| **4. Context Loader** | Clone Reaction Commerce, build file index, keyword-to-file matching, snippet extraction. Mount as read-only volume. | 2h | Phase 1 |
| **5. Ticket Service** | Create/read/update tickets in Postgres. Mock service with Protocol interface. Status tracking. | 2h | Phase 1 |
| **6. Notifications** | Email + chat mock services. Send on ticket creation. Log-based with clear output. | 1h | Phase 5 |

**Day 1 checkpoint**: Full E2E flow works — submit incident → triage → ticket → notifications.

### SHOULD — Day 2 Morning (Phases 7–9, ~7h)

These phases hit evaluation criteria directly.

| Phase | Scope | Est. | Depends On | Eval Dimension |
|-------|-------|------|------------|----------------|
| **7. Guardrails** | Input validation, file type checks, injection detection (pattern + LLM-based), rate limiting, PII flagging. | 2h | Phase 2, 3 | Security |
| **8. Observability** | OpenTelemetry spans across all 5 stages. Langfuse integration for LLM traces. Docker service setup. | 3h | Phase 1, 3 | Observability |
| **9. Resolution Tracker** | Poll/webhook for ticket status changes. Notify reporter on resolution via email mock. | 2h | Phase 5, 6 | Reliability |

**Day 2 AM checkpoint**: All 6 evaluation dimensions addressed.

### COULD — Day 2 Afternoon (Phase 10, ~2h)

Bonus points if time allows.

| Phase | Scope | Est. | Depends On | Bonus Category |
|-------|-------|------|------------|----------------|
| **10. Extras** | Severity scoring with reasoning, runbook suggestions from codebase, incident deduplication check. | 2h | Phase 3, 4 | "Smarter routing" |

### MUST — Day 2 Late Afternoon (Phases 11–12, ~3h)

Non-negotiable deliverables.

| Phase | Scope | Est. | Depends On |
|-------|-------|------|------------|
| **11. Documentation** | README.md, AGENTS_USE.md, SCALING.md, QUICKGUIDE.md. Architecture diagrams. | 2h | All prior |
| **12. Demo Video** | Record full E2E flow, 3 min max, YouTube, #AgentXHackathon. | 1h | All prior |

---

## Dependency Graph

```
Phase 1 (Scaffold)
  ├── Phase 2 (UI)
  │     └── Phase 7 (Guardrails)
  ├── Phase 3 (Triage Agent)
  │     ├── Phase 7 (Guardrails)
  │     ├── Phase 8 (Observability)
  │     └── Phase 10 (Extras)
  ├── Phase 4 (Context Loader)
  │     └── Phase 10 (Extras)
  ├── Phase 5 (Ticket Service)
  │     ├── Phase 6 (Notifications)
  │     │     └── Phase 9 (Resolution Tracker)
  │     └── Phase 9 (Resolution Tracker)
  └── Phase 8 (Observability)

Phase 11 (Documentation) ← depends on all above
Phase 12 (Demo Video) ← depends on all above
```

## Parallel Opportunities

```
Can build simultaneously:
  - Phase 2 (UI) + Phase 3 (Agent) + Phase 4 (Context) + Phase 5 (Tickets)
    All depend only on Phase 1 (Scaffold)

  - Phase 7 (Guardrails) + Phase 8 (Observability) + Phase 9 (Resolution)
    Can start once their upstream phase is done
```

---

## Critical Path

```
Phase 1 → Phase 3 → Phase 8 → Phase 11 → Phase 12
  2h        4h        3h        2h         1h    = 12h minimum
```

This is the longest chain. Everything else can be parallelized around it.

---

## Checkpoints & Go/No-Go

| Time | Checkpoint | Go/No-Go |
|------|-----------|----------|
| End of Day 1 | E2E flow works (submit → triage → ticket → notify) | **Must pass** or scope cut |
| Day 2 10AM | Guardrails + Observability wired | On track for strong submission |
| Day 2 2PM | All SHOULD phases done | Green light for extras |
| Day 2 5PM | Docs written, docker-compose verified | Ready for video |
| Day 2 7PM | Video recorded and uploaded | **Submission ready** |
| Day 2 9PM COT | Deadline | Submit |

---

## Risk Mitigations

| Risk | Trigger | Mitigation |
|------|---------|------------|
| Docker issues | Day 1 build fails | Test `docker compose up` after EVERY phase, not at the end |
| Triage quality | Agent outputs garbage | Use structured output (tool_use), iterate prompt, test with 3+ incidents |
| Time overrun | Phase 3 takes >4h | Cut image analysis, do text-only triage first, add image later |
| API costs | Claude usage spikes | Use Haiku for development, Sonnet only for demo/video |
| Demo video | Recording issues | Record incrementally after each milestone, not last minute |
