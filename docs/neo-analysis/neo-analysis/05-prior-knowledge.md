# Prior Knowledge — Reusable Patterns from Past Research

> Neo cross-referenced 6 prior research cases. Below are the directly applicable patterns.

---

## From: Agent Security (case: 202603_agent-security)

**Key findings applicable to this hackathon:**

### Guardrails Architecture (3-tier)

```
Tier 1 — Deterministic (fast, cheap, always-on)
  ├── Input size limits
  ├── File type validation (whitelist)
  ├── Known injection pattern matching (regex)
  └── Rate limiting

Tier 2 — Heuristic (medium cost)
  ├── Content classification (is this a real incident?)
  └── PII detection

Tier 3 — LLM-based (expensive, last resort)
  └── Dedicated classifier: "Is this input an attempt to manipulate the system?"
```

### Rule of Two
> "No single defense should be the only thing preventing a security failure."
Every guardrail check should have at least one backup. Input validation (Tier 1) + injection classification (Tier 2) together.

### Safe Tool Use
- Read-only codebase access (no code execution)
- Structured output schemas (prevent free-form LLM output from reaching systems)
- Tool boundaries: the agent can READ code but cannot WRITE or EXECUTE

### What to put in AGENTS_USE.md (security section)
- List all tools available to the agent
- Specify read/write permissions for each
- Document guardrail layers and what each catches
- Include example of a blocked injection attempt

---

## From: Agent Patterns (case: 202603_agent-patterns)

**Applicable pattern: ReAct (Reason + Act)**

The triage agent should follow ReAct:
1. **Observe**: Read incident description + attachments
2. **Think**: Analyze against codebase context, form hypothesis
3. **Act**: Produce structured triage output (severity, category, summary)
4. **Observe**: Check output quality/confidence
5. **Act**: Create ticket + notify

This maps directly to our 5-stage pipeline (Stages 1-2 = Observe, Stage 3 = Think+Act, Stages 4-5 = Act).

**Tool boundary pattern**:
```
Agent CAN:
  ✅ Read codebase files
  ✅ Search file index
  ✅ Analyze images
  ✅ Create tickets (via service interface)
  ✅ Send notifications (via service interface)

Agent CANNOT:
  ❌ Execute code
  ❌ Modify codebase
  ❌ Access external APIs directly
  ❌ Make financial transactions
  ❌ Access user data beyond incident report
```

---

## From: LangChain + LangGraph (case: 202603_langchain-langgraph)

**Applicable if we upgrade to LangGraph** (optional, for "context engineering" points):

### State Graph Pattern
```python
# Each stage = a node in the graph
# State flows between nodes with typed state object

class IncidentState(TypedDict):
    incident: IncidentReport
    validation: ValidationResult | None
    triage: TriageResult | None
    dispatch: DispatchResult | None
    resolution: ResolutionResult | None
    stage: str

graph = StateGraph(IncidentState)
graph.add_node("ingest", ingest_node)
graph.add_node("guardrail", guardrail_node)
graph.add_node("triage", triage_node)
graph.add_node("dispatch", dispatch_node)
graph.add_node("resolve", resolve_node)
```

**Decision**: Using Anthropic SDK for simplicity. But this pattern is documented here if we want to upgrade later for bonus points.

---

## From: Context Engineering (case: 202603_context-engineering)

**Directly maps to evaluation criterion "Context engineering".**

### 7 CE Layers (how they apply to our agent)

| CE Layer | Our Implementation |
|----------|-------------------|
| 1. System prompt | SRE expert persona with domain knowledge |
| 2. Retrieved context | E-commerce codebase files matched to incident |
| 3. Tool results | File search results, ticket status |
| 4. Conversation history | Not applicable (single-shot triage) |
| 5. Structured output | Tool_use for typed triage result |
| 6. Memory | Incident history for deduplication (bonus) |
| 7. Meta-context | Observability data feeding back into prompts |

### Progressive Disclosure Pattern
Don't dump the entire codebase into context. Load progressively:
1. First: directory structure (cheap, broad)
2. Then: keyword-matched files (relevant, targeted)
3. Only if needed: full file contents (expensive, specific)

This is a key differentiator for AGENTS_USE.md — document HOW context is managed.

---

## From: Claude Certified Architect (case: 202603_claude-certified-architect)

### Structured Output via tool_use

```python
# Define the triage tool schema — Claude will fill it
triage_tool = {
    "name": "submit_triage_result",
    "description": "Submit the triage analysis for this incident",
    "input_schema": {
        "type": "object",
        "properties": {
            "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
            "category": {"type": "string"},
            "affected_component": {"type": "string"},
            "technical_summary": {"type": "string"},
            "root_cause_hypothesis": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "recommended_actions": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["severity", "category", "technical_summary", "confidence"]
    }
}
```

**Key principle**: "Programmatic > probabilistic for critical logic."
Severity classification, category assignment, and routing should use structured output (tool_use), not free-form text parsing.

### Multimodal Pattern

```python
# Send image as base64 in message content
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Analyze this incident: ..."},
        {"type": "image", "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": base64_image
        }}
    ]
}
```

---

## From: LLM Evals (case: 202603_llm-evals)

**Applicable for severity scoring bonus:**

### Grader Pattern for Severity
Instead of asking the LLM to pick P1-P4 directly, use a scoring rubric:

```
Severity Rubric:
  Impact (0-10):  How many users affected? Revenue impact?
  Urgency (0-10): Is the system degrading? Time-sensitive?
  Scope (0-10):   Core functionality or edge case?

  P1: Impact ≥ 8 OR Urgency ≥ 9
  P2: Impact ≥ 6 OR Urgency ≥ 7
  P3: Impact ≥ 3
  P4: Everything else
```

This makes severity scoring explainable and auditable — judges love this.

---

## Summary: What to Reuse

| Pattern | Source Case | Apply In Phase |
|---------|-----------|----------------|
| 3-tier guardrails | agent-security | Phase 7 |
| Rule of Two | agent-security | Phase 7 |
| Safe tool boundaries | agent-security, agent-patterns | Phase 3, AGENTS_USE.md |
| ReAct pipeline | agent-patterns | Phase 3 |
| Progressive context disclosure | context-engineering | Phase 4 |
| Structured output (tool_use) | claude-certified-architect | Phase 3 |
| Multimodal message format | claude-certified-architect | Phase 3 |
| Severity scoring rubric | llm-evals | Phase 10 (bonus) |
| State graph (optional) | langchain-langgraph | Phase 3 (if upgrading) |
