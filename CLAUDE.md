# AgentX SRE Triage Agent (ECC Workflow)

## Project Overview

AI-powered SRE Incident Intake & Triage Agent for the AgentX Hackathon (April 7-9, 2026). This is a parallel build of the same project being done in `/home/khujta/projects/hackathon/202604-agentx` (which uses GSD workflow). This repo uses the ECC suite to contrast workflows.

**Core Value:** When an incident is reported, the agent produces an accurate, code-aware triage that identifies the likely affected components in the Solidus e-commerce codebase.

## Stack

- Python 3.12, FastAPI, PostgreSQL, Claude Agent SDK, HTMX, Jinja2, Docker Compose, Langfuse

## Constraints

- **Timeline**: ~48 hours (April 7-9, 2026)
- **Solo builder**
- **Deployment**: `docker compose up --build`
- **Demo**: Max 3-minute YouTube video
- **Target codebase**: Solidus (~30K LOC Rails e-commerce)

## Local Ports (ECC fork)

This fork uses offset ports to avoid conflicts with parallel sessions:

| Service      | Host Port | Container Port | URL                        |
|-------------|-----------|----------------|----------------------------|
| App (FastAPI)| **8100**  | 8000           | http://localhost:8100       |
| PostgreSQL   | **5433**  | 5432           | localhost:5433              |
| Redis        | **6380**  | 6379           | localhost:6380              |
| Langfuse     | **3100**  | 3000           | http://localhost:3100       |
| Langfuse DB  | (internal)| 5432           | (no host port)             |

**Testing**: `docker compose exec app pytest tests/ -v`

## Workflow

This project uses **ECC (Everything Claude Code)** for workflow management. Key commands:

- `/plan` - Create implementation plan
- `/tdd` - Test-driven development
- `/code-review` - Review code quality
- `/build-fix` - Fix build errors
- `/verify` - Verification loop
- `/e2e` - E2E testing

## Alignment

- KDBP suite is in `.kdbp/` — values, behavior, and alignment ledger
- Hackathon context docs are in `docs/hackathon_context/`
- Architecture analysis is in `docs/neo-analysis/`

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- PRs to main
