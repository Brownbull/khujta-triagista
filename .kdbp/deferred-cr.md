<!-- gabe-review:1.3 -->
# Deferred Code Review Items

| # | First Seen | Review | Finding | File | Defer Risk | Times Deferred | Status | Resolved |
|---|-----------|--------|---------|------|------------|----------------|--------|----------|
| D1 | 2026-04-07 | Phase-2 | MIME validation relies on client Content-Type — no server-side content sniffing | app/routes/incidents.py:69 | FILE TYPE BYPASS — P(medium), I(moderate) | 1 | Deferred | |
| D2 | 2026-04-08 | Guardrails | In-memory rate limiter resets on container restart — attacker gets fresh budget each redeploy | app/pipeline/guardrail/rate_limit.py:25 | RATE LIMIT BYPASS — P(high), I(moderate) | 2 | Resolved | 2026-04-08 |
| D3 | 2026-04-09 | Observability | trace_triage_pipeline() major refactor with zero unit tests — 4 Langfuse span paths untested | app/services/observability.py:124 | BLIND REFACTOR — P(medium), I(moderate) | 1 | Deferred | |
