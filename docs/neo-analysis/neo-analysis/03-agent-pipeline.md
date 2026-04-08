# Agent Pipeline Design

> 5-stage pipeline with full observability mapping. Each stage is a traced span.

## Pipeline Overview

```
  ┌───────────┐     ┌────────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
  │  INGEST   │────▶│  GUARDRAIL │────▶│  TRIAGE  │────▶│ DISPATCH  │────▶│ RESOLVE  │
  │  Stage 1  │     │  Stage 2   │     │  Stage 3 │     │  Stage 4  │     │ Stage 5  │
  └───────────┘     └────────────┘     └──────────┘     └───────────┘     └──────────┘
       │                  │                 │                 │                 │
       ▼                  ▼                 ▼                 ▼                 ▼
   [trace:          [trace:            [trace:           [trace:          [trace:
    modalities,      injection,         model,            ticket_id,       resolution_
    file_size]       flags]             tokens,           notified]        time]
                                        confidence]
```

---

## Stage 1: INGEST

**Purpose**: Accept multimodal incident report, normalize into structured object.

```
Input:
  - description: str (required)
  - image: file upload (optional — screenshot, error page, log snippet)
  - log_file: file upload (optional — .log, .txt)
  - reporter_email: str (required — for resolution notification)
  - reporter_name: str (optional)

Output:
  IncidentReport {
    id: uuid
    description: str
    attachments: list[Attachment]  # type, path, size, mime_type
    reporter: Reporter
    submitted_at: datetime
    modalities: list[str]  # ["text", "image"], ["text", "log"]
  }

Observability:
  - span: "incident.ingest"
  - attributes: input_type, attachment_count, file_sizes, modalities_used
```

## Stage 2: GUARDRAIL

**Purpose**: Validate input safety before sending to LLM. Defense-in-depth.

```
Checks:
  1. Input size limits (text < 10KB, files < 5MB)
  2. File type validation (only: .png, .jpg, .gif, .log, .txt, .csv)
  3. Prompt injection detection:
     a. Pattern matching (known injection templates)
     b. Content classification (is this a legitimate incident report?)
  4. PII scan (flag but don't block — incidents may contain user data)
  5. Rate limiting (per reporter, per hour)

Output:
  ValidatedIncident {
    ...IncidentReport fields
    validation: {
      passed: bool
      flags: list[str]  # ["contains_pii", "large_attachment"]
      injection_score: float  # 0.0 - 1.0
      rejected: bool
      rejection_reason: str | null
    }
  }

Observability:
  - span: "incident.guardrail"
  - attributes: injection_detected, validation_passed, flags, rejection_reason
```

## Stage 3: TRIAGE (the brain)

**Purpose**: Analyze incident using multimodal LLM + e-commerce codebase context.

```
Context Loading:
  1. Load e-commerce codebase index (pre-built at startup)
  2. Match incident keywords → relevant source files
  3. Load relevant code snippets (max 5 files, ~500 lines each)
  4. Include in Claude prompt as structured context

LLM Call (Claude Sonnet — multimodal):
  - System prompt: SRE triage expert with codebase knowledge
  - User prompt: incident description + image (if any) + relevant code
  - Tool use: structured output schema

Output:
  TriageResult {
    severity: P1 | P2 | P3 | P4
    category: str  # "payment-processing", "auth", "inventory", "ui", "infra"
    affected_component: str  # specific module/service
    technical_summary: str  # 2-3 paragraphs
    root_cause_hypothesis: str
    suggested_assignee: str  # team or role
    related_files: list[FileRef]  # files from codebase relevant to incident
    confidence: float  # 0.0 - 1.0
    recommended_actions: list[str]
  }

Observability:
  - span: "incident.triage"
  - attributes: llm_model, tokens_in, tokens_out, latency_ms,
                severity, category, confidence, codebase_files_analyzed
```

## Stage 4: DISPATCH

**Purpose**: Create ticket and notify team.

```
Actions:
  1. Create ticket:
     - Title: "[{severity}] {category}: {short_summary}"
     - Body: technical_summary + root_cause + related_files + recommended_actions
     - Labels: severity, category
     - Assignee: suggested_assignee

  2. Send email notification:
     - To: on-call team (configurable)
     - Subject: "[{severity}] New incident: {short_summary}"
     - Body: triage summary + ticket link

  3. Send chat notification:
     - Channel: #incidents (configurable)
     - Message: severity emoji + summary + ticket link

Output:
  DispatchResult {
    ticket_id: str
    ticket_url: str
    email_sent: bool
    email_recipients: list[str]
    chat_sent: bool
    chat_channel: str
  }

Observability:
  - span: "incident.dispatch"
  - attributes: ticket_id, email_sent, chat_sent, notification_latency_ms
```

## Stage 5: RESOLVE

**Purpose**: Track ticket resolution and notify reporter.

```
Mechanism:
  - Poll ticket status every N seconds (configurable)
  - OR receive webhook on status change

On Resolution:
  1. Update incident record with resolution details
  2. Send email to original reporter:
     - "Your incident {id} has been resolved"
     - Include: resolution summary, ticket link, time to resolution

Output:
  ResolutionResult {
    incident_id: str
    resolved_at: datetime
    resolution_time: timedelta
    resolution_type: str  # "fix", "workaround", "not-a-bug", "duplicate"
    reporter_notified: bool
  }

Observability:
  - span: "incident.resolve"
  - attributes: resolution_time_seconds, resolution_type, reporter_notified
```

---

## E-Commerce Context Loading Strategy

The agent doesn't run the e-commerce app — it reads the codebase for triage intelligence.

### At Startup (pre-index)

```
1. Parse directory tree → structure map
2. Read README + key docs → domain knowledge
3. Index service/module names → component map
4. Read recent git log → change context
5. Store as searchable index in memory
```

### At Triage Time (per incident)

```
1. Extract keywords from incident description
2. Match keywords → relevant files (fuzzy search on index)
3. Load top 5 matching files (truncated to ~500 lines each)
4. Include as context in Claude prompt:
   "Here are the relevant source files from the e-commerce application..."
5. Claude references specific files/lines in triage output
```

### Context Budget

```
System prompt:     ~500 tokens
Codebase context:  ~3,000 tokens (5 files × ~600 tokens)
Incident report:   ~500 tokens (text + image description)
Image:             ~800 tokens (if image attached)
───────────────────────────────
Total per triage:  ~4,800 tokens input
Output:            ~800 tokens
```

---

## Structured Output Schema

```json
{
  "severity": "P1",
  "category": "payment-processing",
  "affected_component": "checkout/payment-gateway",
  "technical_summary": "...",
  "root_cause_hypothesis": "...",
  "suggested_assignee": "payments-team",
  "related_files": [
    {"path": "src/plugins/payments/stripe.js", "relevance": "Payment processing logic"},
    {"path": "src/api/checkout.js", "relevance": "Checkout flow entry point"}
  ],
  "confidence": 0.85,
  "recommended_actions": [
    "Check Stripe webhook handler for timeout handling",
    "Review recent changes to checkout flow (last 3 commits)"
  ]
}
```
