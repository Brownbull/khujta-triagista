# Neo Analysis — AgentX Hackathon 2026

> Pre-build intelligence produced by **Neo**, a knowledge absorption and cognitive translation agent.
> Neo ingested the hackathon brief, cross-referenced 6 prior research cases, and generated
> the architecture decisions and execution plan below.

## What's in this folder

| File | Purpose |
|------|---------|
| [01-hackathon-brief.md](01-hackathon-brief.md) | Distilled assignment, rules, evaluation criteria, and deadlines |
| [02-architecture-decisions.md](02-architecture-decisions.md) | Stack choices, trade-off analysis, and locked decisions |
| [03-agent-pipeline.md](03-agent-pipeline.md) | 5-stage agent pipeline design with observability mapping |
| [04-execution-plan.md](04-execution-plan.md) | Phased build plan with MoSCoW priorities and time budget |
| [05-prior-knowledge.md](05-prior-knowledge.md) | Reusable patterns from 6 prior research cases |
| [06-gabe-blocks.md](06-gabe-blocks.md) | Cognitive translation — physical-system analogies for key concepts |

## How this was produced

```
Neo Agent Pipeline:
  1. FEED    — Ingested 5 hackathon docs (assignment, rules, deliverables, tech reqs, resources)
  2. ABSORB  — Extracted requirements, constraints, evaluation dimensions
  3. RECALL  — Cross-referenced 6 past cases (agent-security, agent-patterns, langchain-langgraph,
               claude-certified-architect, context-engineering, llm-evals)
  4. MAP     — Created Gabe Blocks (physical-system analogies) for architecture concepts
  5. PACKAGE — Produced this folder as project kickstart context
```

## How to use

1. Read `01-hackathon-brief.md` for the "what" and "when"
2. Read `02-architecture-decisions.md` for the "how"
3. Feed `04-execution-plan.md` into your project planning tool (GSD, Linear, etc.)
4. Reference `05-prior-knowledge.md` when implementing guardrails, observability, or agent design
5. Use `06-gabe-blocks.md` to quickly re-orient on architecture concepts when fatigued
