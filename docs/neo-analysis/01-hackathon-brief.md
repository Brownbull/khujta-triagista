# Hackathon Brief — AgentX 2026

> Distilled from 5 source documents. AI-generated summary — verify against originals.

## The Assignment

Build an **SRE Incident Intake & Triage Agent** for an e-commerce application.

### Core E2E Flow

```
Reporter submits incident (text + image/log)
       │
       ▼
Agent triages: extracts details, analyzes code/docs, produces technical summary
       │
       ▼
Agent creates ticket in ticketing system
       │
       ▼
Agent notifies technical team (email + communicator)
       │
       ▼
Ticket gets resolved
       │
       ▼
Agent notifies the original reporter
```

## Timeline

| Date | Event | Notes |
|------|-------|-------|
| **Apr 7** | Kick-off | Today |
| **Apr 8–9** | Build sprint | Online, own pace |
| **Apr 9, 9PM COT** | Submission deadline | Hard cutoff, no late submissions |
| Apr 10 | Mentor pre-screening | Top submissions reviewed |
| Apr 13 | Expert evaluation | Finalist panel |
| Apr 14 | Awards ceremony | Online |

**Effective build time: ~48 hours.**

## Minimum Requirements

| # | Requirement | Details |
|---|-------------|---------|
| 1 | **Multimodal input** | Text + at least one other modality (image, log file, video). Multimodal LLM required. |
| 2 | **Guardrails** | Prompt injection defense + safe tool use + input handling |
| 3 | **Observability** | Logs, traces, metrics across all stages (ingest → triage → ticket → notify → resolved) |
| 4 | **Integrations** | Ticketing + email + communicator. Real or mocked, but must be demoable. |
| 5 | **E-commerce codebase** | Medium/complex open-source repo as the application being triaged |
| 6 | **Docker Compose** | Entire app runs via `docker compose up --build`. No host dependencies. |

## Evaluation Criteria (6 dimensions)

| Dimension | What Judges Look For |
|-----------|---------------------|
| **Reliability** | Works consistently, handles edge cases |
| **Observability** | Structured logs, traces, metrics across agent stages |
| **Scalability** | Handles growth; assumptions documented |
| **Context engineering** | How well the agent manages and uses context |
| **Security** | Prompt injection defenses, safe tool usage |
| **Documentation** | Clear, reproducible, well-structured |

> "All teams receive the same assignment — what sets you apart is how well you build it."

## Required Deliverables

### Repository (public, MIT license)

| File | Content |
|------|---------|
| README.md | Architecture overview, setup, project summary |
| AGENTS_USE.md | Agent docs: use cases, implementation, observability, safety |
| SCALING.md | Scaling explanation, assumptions, technical decisions |
| QUICKGUIDE.md | clone → .env → `docker compose up --build` |
| docker-compose.yml | All services |
| .env.example | All env vars with placeholders + comments |
| LICENSE | MIT |

### Demo Video
- YouTube, max 3 minutes, English
- Tag: #AgentXHackathon
- Show full E2E flow: submit → triage → ticket → notify → resolve → reporter notified

## Optional Extras (bonus points)

- Smarter routing or severity scoring
- Incident deduplication
- Runbook suggestions
- Observability dashboards
- Team-wide agent configuration (AGENTS.md, sub-agents, etc.)

## E-Commerce Repo Options

| Repo | Stack | URL |
|------|-------|-----|
| eShop | .NET (Microsoft) | github.com/dotnet/eShop |
| Solidus | Ruby on Rails | github.com/solidusio/solidus |
| Reaction Commerce | Node.js | github.com/reactioncommerce/reaction |

## Rules Highlights

- Teams of 1–4 members
- Own tools, API keys, infrastructure (nothing provided)
- English only (all communication + deliverables)
- No code sharing in Discord during sprint
- Mocked integrations are acceptable if demoable
