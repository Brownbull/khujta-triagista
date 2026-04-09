# Python Dependency Analysis Report

**Generated:** 2026-04-09 | **Branch:** main

## Summary

| Metric | Value |
|--------|-------|
| Total modules | 37 |
| Total edges | 75 (74 unique) |
| Circular dependencies | 6 cycles |
| Orphaned modules | 3 |
| Layer violations | 1 |
| Entry points | 5 |

## Output Files

| File | Path |
|------|------|
| DOT graph | `dependency-diagrams/dependency-graph.dot` |
| SVG graph | `dependency-diagrams/dependency-graph.svg` |
| Metrics JSON | `dependency-diagrams/_metrics.json` |

## Top Fan-Out (most outgoing imports)

| Module | Out |
|--------|-----|
| routes/incidents | 12 |
| main | 11 |
| pipeline/triage/agent | 5 |
| routes/pages | 5 |
| models/__init__ | 4 |
| pipeline/triage/provider | 4 |
| services/seed_data | 4 |
| models/incident | 3 |
| pipeline/dispatch/service | 3 |
| models/notification | 2 |
| models/ticket | 2 |
| pipeline/triage/anthropic_provider | 2 |
| pipeline/triage/langchain_provider | 2 |
| pipeline/triage/managed_provider | 2 |
| routes/__init__ | 2 |

## Top Fan-In (most depended upon)

| Module | In |
|--------|-----|
| config | 11 |
| models/incident | 8 |
| models/ticket | 6 |
| models/notification | 5 |
| pipeline/triage/agent | 5 |
| services/observability | 4 |
| models/base | 4 |
| database | 3 |
| services/codebase_indexer | 3 |
| routes/incidents | 2 |
| routes/pages | 2 |
| services/seed_data | 2 |
| pipeline/knowledge/loader | 2 |
| pipeline/dispatch/__init__ | 2 |
| schemas/incident | 2 |

## Circular Dependencies (6 cycles)

### Cycle 1: models/incident ↔ models/notification
```
app/models/incident.py → app/models/notification.py → app/models/incident.py
```

### Cycle 2: models/incident ↔ models/ticket
```
app/models/incident.py → app/models/ticket.py → app/models/incident.py
```

### Cycle 3: pipeline/triage/agent ↔ pipeline/triage/provider
```
app/pipeline/triage/agent.py → app/pipeline/triage/provider.py → app/pipeline/triage/agent.py
```

### Cycle 4: agent → provider → anthropic_provider → agent
```
app/pipeline/triage/agent.py → app/pipeline/triage/provider.py → app/pipeline/triage/anthropic_provider.py → app/pipeline/triage/agent.py
```

### Cycle 5: agent → provider → langchain_provider → agent
```
app/pipeline/triage/agent.py → app/pipeline/triage/provider.py → app/pipeline/triage/langchain_provider.py → app/pipeline/triage/agent.py
```

### Cycle 6: agent → provider → managed_provider → agent
```
app/pipeline/triage/agent.py → app/pipeline/triage/provider.py → app/pipeline/triage/managed_provider.py → app/pipeline/triage/agent.py
```

## Layer Violations

Expected dependency direction: `config ← database ← models ← schemas ← services ← pipeline ← routes ← main`

| Source | Target | Source Layer | Target Layer | Direction |
|--------|--------|-------------|-------------|-----------|
| services/seed_data | pipeline/dispatch/__init__ | services | pipeline | ← wrong (services → pipeline) |

**1 violation found.** The `seed_data` service reaches up into the pipeline layer.

## Entry Points (no incoming deps)

| Module | Fan-Out | Status |
|--------|---------|--------|
| app/main.py | 11 | expected (app entrypoint) |
| app/routes/__init__.py | 2 | expected (router registry) |
| app/schemas/__init__.py | 1 | expected (schema barrel) |
| app/schemas/notification.py | 0 | verify-usage |
| app/schemas/ticket.py | 0 | verify-usage |

## Orphaned Modules (no in or out)

| Module | Note |
|--------|------|
| app/__init__.py | Package marker — expected |
| app/pipeline/__init__.py | Package marker — expected |
| app/services/__init__.py | Package marker — expected |

All orphans are `__init__.py` package markers — no concern.

## Cross-Layer Dependency Matrix

| From ↓ / To → | config | database | models | schemas | services | pipeline | routes |
|---------------|--------|----------|--------|---------|----------|----------|--------|
| **database** | 1 | — | — | — | — | — | — |
| **models** | — | — | 11 | — | — | — | — |
| **schemas** | — | — | 3 | 1 | — | — | — |
| **services** | 1 | — | 2 | — | 1 | 1* | — |
| **pipeline** | 6 | — | 3 | — | 1 | 14 | — |
| **routes** | 2 | 2 | 4 | 1 | 3 | 5 | 2 |
| **main** | 1 | 1 | 1 | — | 5 | 1 | 2 |

`*` = layer violation

## Architectural Observations

### God Modules
- **routes/incidents.py** (fan-out: 12) — imports from nearly every layer. This is common for a "fat controller" pattern but worth monitoring.
- **config.py** (fan-in: 11) — imported by almost everything. Expected for a config module.

### Cycle Roots
1. **Model mutual references** (cycles 1-2): `incident ↔ notification` and `incident ↔ ticket`. Likely ORM relationship back-references — common in SQLAlchemy but could use `TYPE_CHECKING` imports to break the static cycle.
2. **Triage provider pattern** (cycles 3-6): The `agent ↔ provider` cycle suggests the provider registry imports concrete providers which import back to the agent. Consider a separate types/protocol file to break this.

### Coupling Hotspots
- **pipeline/triage/** has 4 intra-package cycles — the most coupled sub-package.
- **models/** has high internal coupling (11 intra-layer edges) but this is typical for an ORM model layer.

### Layer Discipline
- **Generally good.** Only 1 violation: `seed_data` → `pipeline/dispatch`. This is a seeding/dev helper, so low risk.
- The main dependency flow follows the expected bottom-up pattern: config ← models ← services ← pipeline ← routes ← main.

### Recommendations (non-blocking, future improvement)
1. Break model cycles with `from __future__ import annotations` + `TYPE_CHECKING` guards
2. Extract a `pipeline/triage/types.py` protocol file to break agent ↔ provider cycle
3. Consider moving `seed_data`'s dispatch dependency behind an interface
