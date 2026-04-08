---
name: agentx-sre-triage
domain: AI-powered SRE incident intake and triage agent for e-commerce
maturity: mvp
tech: Python 3.12, FastAPI, PostgreSQL, Anthropic SDK, HTMX, Jinja2, Docker Compose, Langfuse
created: 2026-04-07
---

## Purpose

Solo-built hackathon entry (AgentX, April 7-9 2026). Users submit incident reports with text + files, and an AI agent triages them against the Solidus e-commerce codebase, creates tickets, notifies the team, and closes the loop on resolution.

## Active Focus

Ship a working E2E demo in ~48 hours: submit incident -> guardrail -> triage against Solidus -> ticket + notify -> resolve + notify reporter. Every decision serves the 3-minute demo video.

## Constraints

- 48-hour solo build window (deadline: April 9 at 9PM COT)
- Must run via single `docker compose up --build`
- Judged on: Reliability, Observability, Scalability, Context Engineering, Security, Documentation
- Target codebase: Solidus (~30K LOC Rails e-commerce)
- All integrations (ticketing, email, chat) are mocked with clean Protocol interfaces
