# Judges Brief — Triagista

Quick-reference document for evaluators. Points to evidence in the repo rather than duplicating it.

---

## Solution Introduction

Triagista is an AI-powered SRE incident intake and triage agent built for the Solidus e-commerce platform (~30K LOC Ruby/Rails). When an engineer reports an incident, the agent analyzes the description against the actual codebase, produces a structured triage (severity P1-P4, root cause hypothesis, affected source files, recommended actions), auto-creates a ticket, notifies the on-call team, and sends the reporter a resolution notification when the issue is closed. The full lifecycle — submit, guardrail, triage, dispatch, acknowledge, resolve, notify — runs end-to-end.

The agent supports three interchangeable triage engines: Basic (Gemini 2.5 Flash via LangChain), Premium (Claude Haiku 4.5 via Anthropic SDK with forced tool_use), and Experimental (Claude Agent SDK / Managed Agents for autonomous codebase exploration). All three produce the same structured output schema so results are comparable. The app ships with 18 pre-seeded incidents covering all lifecycle states, all three engines, and multiple attachment types — `docker compose up --build` produces a fully populated dashboard immediately.

Built solo in ~48 hours using Python 3.12, FastAPI, PostgreSQL, HTMX/Jinja2, and Docker Compose. Observability via OpenTelemetry (infrastructure tracing) and Langfuse (LLM tracing with pre-seeded dashboard). Context engineering uses a progressive disclosure knowledge base (L0 architecture → L1 components → L2 domain deep-dives → L3 source code) with keyword-based relevance scoring and Ruby file boosting.

---

## Verification Checklist

For evaluators who want to confirm the submission:

| Check | How to verify |
|-------|---------------|
| Builds from clean state | `docker compose up --build` (no host dependencies) |
| Required files present | README.md, AGENTS_USE.md, SCALING.md, QUICKGUIDE.md, docker-compose.yml, .env.example, LICENSE (MIT) |
| Seeded on startup | 18 incidents visible at http://localhost:8100 immediately |
| Langfuse dashboard | http://localhost:3100 — login: `admin@sre-triage.local` / `admin123` — 17 traces pre-loaded |
| API docs | http://localhost:8100/docs (Swagger UI) |
| Health check | http://localhost:8100/health |
| Tests | `docker compose exec app pytest tests/ -v` (87 tests) |

---

## Evaluation Dimensions — Anticipated Questions

### 1. Reliability

**Q: Does the agent work consistently?**
Yes. 18 seed incidents include real captured triage outputs from all 3 engines — not mocked JSON but actual LLM responses stored at build time. 87 pytest + 30 Playwright E2E tests validate the full lifecycle. See [REQUIREMENTS.md → D1.1-D1.4](REQUIREMENTS.md) for evidence mapping.

**Q: How does it handle failures?**
If the triage API call fails (timeout, 401, 503), the incident status reverts to `submitted` so the user can retry. The error is traced in Langfuse with `["error", "triage-generation"]` tags. The UI shows a descriptive error in-place without losing context. See [AGENTS_USE.md → Section 3](AGENTS_USE.md) for the error handling flow.

**Q: What about edge cases?**
- Prompt injection attempts are blocked by the guardrail (15 patterns, score-based). Two seed incidents demonstrate rejection with full UI visibility.
- Rate limiting enforces 10 submissions/hour per email (429 with retry-after).
- Empty or too-short descriptions are caught by Pydantic validation.
- Invalid file types are rejected at upload.

### 2. Observability

**Q: Where do I see traces?**
Langfuse at http://localhost:3100. Pre-seeded with 17 traces:
- **Traces tab**: 15 triage pipeline traces (guardrail → context-retrieval → triage-generation → dispatch) + 2 guardrail rejection traces
- **Sessions tab**: Grouped by incident ID — all activity for one incident in one view
- **Users tab**: Grouped by reporter email — submission patterns per user

**Q: What does OpenTelemetry add?**
OpenTelemetry auto-instruments FastAPI routes, SQLAlchemy queries, and HTTPX calls (Claude/Gemini API) as distributed traces. These export to structured console logs (`docker compose logs app`). Langfuse is the visual dashboard — OTel provides the infrastructure instrumentation layer underneath. We chose not to add a separate OTel UI (Jaeger/Tempo) to keep the Docker stack lean and the demo focused.

**Q: How are errors and rejections traced?**
Failed triages: `trace_triage_error()` records the failed stage, error message, and incident context in Langfuse with `["error"]` tags. Guardrail rejections: `trace_guardrail_rejection()` records the injection score, matched patterns, and input in Langfuse with `["rejected", "guardrail"]` tags. Both are visible in the Traces tab.

**Evidence**: AGENTS_USE.md section 6 includes log output samples and the `/api/observability` endpoint JSON.

### 3. Scalability

**Q: How would this scale beyond a hackathon?**
Three-tier strategy documented in [SCALING.md](SCALING.md):
1. **Vertical** (10x): Multi-worker uvicorn, Redis rate limiting, connection pooling
2. **Horizontal** (100x): Load balancer, multiple app containers, shared file storage
3. **Queue-based** (1000x): Async triage via message queue, separate worker pool scaled independently from API

**Q: What's the primary bottleneck?**
LLM API latency (10-20s per triage for Basic/Premium, 1-3 min for Experimental). The architecture already handles this: HTMX auto-polls every 3s during the "triaging" state, so the user sees a progress overlay while the agent works. Moving to queue-based would decouple user response from triage completion entirely.

**Q: Cost at scale?**
~$230/month for 1,000 incidents/day. Breakdown: Claude Haiku ~$5/day, PostgreSQL (RDS) ~$50/month, App hosting ~$30/month, Langfuse self-hosted $0. See [SCALING.md → Cost Estimates](SCALING.md).

### 4. Context Engineering

**Q: How does the agent understand the codebase?**
Progressive disclosure knowledge base with 4 levels:
- **L0** (Architecture Map, ~500 tokens): Always included — gem structure, 6 business domains
- **L1** (Component Index, ~1,500 tokens): Always included — key models, controllers
- **L2** (Domain Deep-Dives, ~900 tokens each): Keyword-matched against the incident — payment, inventory, orders, search, auth, shipping
- **L3** (Source Code, first 80 lines): Fallback if no L2 match — actual file content

Additionally, the Solidus repo is keyword-indexed at startup (~30K LOC). At triage time, the incident description is tokenized and matched against the index. Ruby files get a 1.5x boost; models/controllers/services get 1.3x. Top 5 files are included as context.

Total per triage: ~3,000-5,000 input tokens, ~800-1,300 output tokens. See [AGENTS_USE.md → Section 4](AGENTS_USE.md) with the context engineering flow diagram.

**Q: How is structured output enforced?**
- **Premium engine**: Claude's `tool_use` with `tool_choice: {"type": "tool", "name": "submit_triage"}` — forces the model to call our schema, never freeform text
- **Basic engine**: LangChain `with_structured_output()` using a Pydantic `TriageResult` schema with fallback chain
- Both produce identical schema: severity, category, affected_component, technical_summary, root_cause_hypothesis, confidence, recommended_actions, related_files

**Q: Why three engines instead of one?**
Demonstrates the strategy pattern — same interface, different providers. Lets evaluators compare LLM quality directly. Also shows cost-vs-quality tradeoff: Basic is free-tier, Premium is ~$0.005, Experimental is ~$0.02-0.05 but explores autonomously.

### 5. Security

**Q: How is prompt injection defended?**
15 regex patterns with weighted scoring (0.0-1.0). Direct instruction override and system prompt extraction patterns score 0.90-0.95. Multiple pattern matches boost the score. Submissions scoring >= 0.90 are blocked with a 400 response. The guardrail rejection panel in the UI shows which patterns triggered and the threat analysis.

**Evidence in the app**: Two seed incidents (INC-INJECT-1, INC-INJECT-2) demonstrate blocked prompt injections. Their detail pages show the guardrail rejection panel. Their Langfuse traces show rejection tags.

**Q: How is PII handled?**
`detect_pii()` scans for SSN, credit cards, API keys, phone numbers, emails. PII in the incident description is used for diagnosis (the agent needs it to triage). After the LLM returns its response, `sanitize_for_output()` strips any PII from output fields (technical_summary, root_cause_hypothesis, recommended_actions, related_files.relevance). Approach: "use PII to diagnose, never to display."

**Q: Is tool use safe?**
Claude's `tool_choice` is forced to `submit_triage` — the model can only produce the expected structured output schema. It cannot call arbitrary tools, access the filesystem, or execute code. The Experimental engine (Managed Agents) runs in Anthropic's sandboxed cloud container, not on our infrastructure.

### 6. Documentation

**Q: Are all required files present?**

| File | Status | Content |
|------|--------|---------|
| README.md | Present | Architecture diagrams (Mermaid), quick start, 3 engines, lifecycle state machine, features, stack, testing |
| AGENTS_USE.md | Present | 10 sections per Anthropic template: overview, agents, pipeline sequence diagram, context engineering flow diagram, use cases, observability, security, scalability, scope decisions, lessons |
| SCALING.md | Present | 3-tier strategy with Mermaid diagrams, bottleneck analysis, cost estimates, multi-ticket handling |
| QUICKGUIDE.md | Present | 10-step walkthrough from clone to full demo, troubleshooting table |
| docker-compose.yml | Present | App + PostgreSQL + Redis + Langfuse + Solidus clone |
| .env.example | Present | All env vars with placeholders and comments |
| LICENSE | Present | MIT |
| REQUIREMENTS.md | Present | Full traceability matrix: R1-R6 minimum requirements + D1-D6 evaluation dimensions mapped to phases and evidence |

---

## Design Decisions — Why We Built It This Way

| Decision | Why |
|----------|-----|
| **Solidus** as target codebase | ~30K LOC Ruby/Rails — complex enough for meaningful triage, well-documented, real state machines (orders, payments, inventory) |
| **Claude Haiku** as primary engine | 3x cheaper than Sonnet, fast enough for triage (10-15s), quality is sufficient for structured output with forced tool_use |
| **Three engines** instead of one | Strategy pattern demonstrates provider abstraction; lets evaluators compare LLM quality directly; shows cost-vs-quality tradeoff |
| **Keyword index** over vector embeddings | Simpler, no embedding model needed, good enough for ~30K LOC. Vector search would be the first upgrade for larger codebases |
| **HTMX** over React/Vue | Server-rendered, no build step, smaller bundle, faster development. Perfect for a 48-hour hackathon |
| **Mock dispatch** over real Jira/Slack | The content is fully generated and rendered in the UI. Connecting to real APIs is configuration, not engineering — and would require judges to have Jira/Slack accounts |
| **Langfuse** for observability | Open-source, self-hosted (no external account needed), native LLM tracing (tokens, sessions, users), auto-seeded so judges see data immediately |
| **Progressive disclosure** knowledge base | Reduces hallucination by giving the LLM structured context at the right level. L0 always, L2 only when keywords match — avoids flooding the prompt with irrelevant domain details |
| **OpenTelemetry** for infrastructure tracing | Industry standard, auto-instruments FastAPI/SQLAlchemy/HTTPX with zero code changes in routes. Exports to console logs — no separate dashboard needed for the demo |
| **Pre-seeded 18 incidents** | Judges see a populated dashboard on `docker compose up` without needing API keys. Real captured triage outputs from all 3 engines, not mock data |
| **Solo build** | One developer, ~48 hours. Every feature was prioritized by demo impact (V2: Demo or Die) |

---

## What We Built vs What We Didn't

### Built (working end-to-end)
- Full 5-step lifecycle: submit → triage → ticket → notify → resolve → notify reporter
- 3 triage engines with structured output
- Progressive disclosure codebase knowledge base
- Guardrails: prompt injection (15 patterns), PII detection + sanitization, rate limiting
- Observability: OpenTelemetry + Langfuse (pre-seeded dashboard)
- Ops dashboard: dark/light theme, pipeline progress, KPIs, explanation layers, chat timeline
- 87 pytest + 30 Playwright E2E tests
- 18 seed incidents with real LLM outputs and attachments

### Not built (and why)
- **Interactive chat with agent**: Chat tab shows the triage conversation timeline but real-time follow-up requires WebSocket/SSE streaming — scope vs. time tradeoff
- **Multimodal image analysis**: File attachments are uploaded and displayed but not sent to the LLM for visual analysis — Claude supports it, would be the first feature add
- **Real Jira/Slack/SendGrid**: Mocked intentionally — the content is real, the integration is configuration
- **Incident deduplication**: Would require vector embeddings + similarity search — documented in SCALING.md as a scale feature
- **Separate OTel dashboard (Jaeger)**: OTel instruments to console logs, Langfuse is the visual UI — adding Jaeger would add compose complexity without demo value

---

## E2E Screenshots Reference

18 test scenarios with 38 screenshots in `e2e/screenshots/`:

| # | Scenario | What it shows |
|---|----------|---------------|
| 01 | Incident list | Populated dashboard with filters, sorting, pagination |
| 02 | Submit form | New incident form with engine selector and file upload |
| 03 | Create incident | Submission flow with form data |
| 04 | Untriaged | Incident awaiting triage with status badge |
| 05 | Triage results | Full triage output: severity, RCA, files, actions |
| 06 | Dispatch | Ticket + email + chat notification cards |
| 07 | List dispatched | Dashboard after dispatch |
| 08 | Acknowledge | Team pickup flow |
| 09 | Resolve | Resolution dialog with type and notes |
| 10 | List final | Dashboard with resolved incidents |
| 11 | Not found | Error state for invalid incident ID |
| 12 | Guardrail | Prompt injection rejection panel |
| 13 | Search | Incident ID search functionality |
| 14 | Chat view | Conversation timeline of triage |
| 15 | Settings | Theme, font size, font family toggles |
| 16 | Sidebar | Collapsed sidebar state |
| 17 | Pipeline info | Click-to-expand stage details |
| 18 | Langfuse | Traces, sessions, and users tabs |

---

## Test Coverage

| Type | Count | Framework |
|------|-------|-----------|
| Unit + integration | 87 | pytest (async) |
| E2E (with screenshots) | 30 | Playwright (Chromium) |
| **Total** | **117** | |
