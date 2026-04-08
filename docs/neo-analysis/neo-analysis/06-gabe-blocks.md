# Gabe Blocks — Cognitive Translation

> Physical-system analogies for key architecture concepts.
> Produced by Neo using the Gabe Lens format. Designed to survive fatigue and context loss.

---

## Full Gabe Blocks

```
┌─── GABE BLOCK: SRE Triage Agent ─────────────────────────┐
│                                                            │
│  THE PROBLEM      An e-commerce site breaks. A human      │
│                   reports "checkout doesn't work."         │
│                   Someone needs to figure out what's       │
│                   really broken, how bad it is, and        │
│                   who should fix it — before it costs      │
│                   money.                                   │
│                                                            │
│  THE ANALOGY      Emergency room triage nurse. Patient     │
│                   walks in saying "my chest hurts."        │
│                   Nurse checks vitals (guardrails),        │
│                   reads X-ray (image analysis), checks     │
│                   medical history (codebase context),      │
│                   assigns severity (P1-P4), files the      │
│                   chart (ticket), and pages the right      │
│                   specialist (notification). When the      │
│                   surgeon finishes, nurse calls the        │
│                   family (reporter notification).          │
│                                                            │
│  ANALOGY LIMITS   Case: The ER nurse has years of          │
│                   training and intuition. Our agent has    │
│                   zero domain memory between incidents.    │
│                   Why: Each triage is stateless — no       │
│                   learning from past incidents (unless     │
│                   we add dedup as a bonus).                │
│                                                            │
│  THE MAP                                                   │
│     Reporter ──▶ [Intake Form]                            │
│                      │                                     │
│                      ▼                                     │
│                 [Vital Signs]  ← guardrails                │
│                      │                                     │
│                      ▼                                     │
│                 [X-Ray + History] ← LLM + codebase        │
│                      │                                     │
│                ┌─────┼─────┐                               │
│                ▼     ▼     ▼                               │
│            [Chart] [Page] [Alert]                          │
│            ticket  email  chat                             │
│                                                            │
│  CONSTRAINT BOX                                            │
│    IS:      An automated first-responder that reads        │
│             the symptoms, checks the patient's file,       │
│             and routes to the right doctor                 │
│    IS NOT:  The doctor who fixes the problem               │
│    DECIDES: How urgent this is and who sees it first       │
│                                                            │
│  ONE-LINE HANDLE                                           │
│    "ER triage nurse who reads X-rays and pages surgeons"   │
│                                                            │
│  SIGNAL: ✓ Does the agent produce actionable triage?       │
│          ◆ Can the agent learn from resolved incidents?    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

```
┌─── GABE BLOCK: Context Loading (Progressive Disclosure) ──┐
│                                                            │
│  THE PROBLEM      The e-commerce codebase has thousands    │
│                   of files. The agent can't read them all. │
│                   But it needs to find the RIGHT files     │
│                   for each incident — fast.                │
│                                                            │
│  THE ANALOGY      Library reference desk. A student asks   │
│                   "something's wrong with payments."       │
│                   The librarian doesn't hand them every    │
│                   book. She checks the catalog (index),    │
│                   walks to the right shelf (keyword        │
│                   match), and pulls 3-5 relevant books     │
│                   (code snippets). The student reads       │
│                   those, not the whole library.            │
│                                                            │
│  ANALOGY LIMITS   Case: A librarian understands the        │
│                   content of books. Our index is keyword-  │
│                   based, not semantic.                     │
│                   Why: We match filenames and paths, not   │
│                   code meaning. Could miss relevant files  │
│                   with unexpected names.                   │
│                                                            │
│  THE MAP                                                   │
│     Full Codebase (1000s of files)                         │
│           │                                                │
│           ▼                                                │
│     [Catalog] ← pre-built at startup                      │
│           │                                                │
│     incident keywords → [Shelf Lookup]                     │
│                              │                             │
│                              ▼                             │
│                    [3-5 Relevant Books]                     │
│                         │                                  │
│                         ▼                                  │
│                    Claude reads these                      │
│                                                            │
│  CONSTRAINT BOX                                            │
│    IS:      A librarian who finds the right books,         │
│             not someone who reads the whole library        │
│    IS NOT:  Full-text search or vector embeddings          │
│    DECIDES: Relevance vs completeness — we sacrifice       │
│             some recall for speed and cost control         │
│                                                            │
│  ONE-LINE HANDLE                                           │
│    "Reference librarian who pulls 5 books, not 5000"       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

```
┌─── GABE BLOCK: Guardrails (Defense in Depth) ─────────────┐
│                                                            │
│  THE PROBLEM      Users submit text + files to the agent.  │
│                   A malicious user could inject prompts,   │
│                   upload harmful files, or overwhelm       │
│                   the system.                              │
│                                                            │
│  THE ANALOGY      Airport security with 3 checkpoints.     │
│                   Checkpoint 1 (metal detector): fast,     │
│                   catches obvious threats — size limits,    │
│                   file type checks. Checkpoint 2 (X-ray    │
│                   scanner): looks inside — pattern         │
│                   matching for known injection templates.   │
│                   Checkpoint 3 (human inspector): slow     │
│                   but thorough — LLM classifies whether    │
│                   the input is a real incident or an       │
│                   attack. Each layer catches what the      │
│                   previous one missed.                     │
│                                                            │
│  ANALOGY LIMITS   Case: Airport security is adversarial    │
│                   by design — everyone is a suspect.       │
│                   Our users are mostly legitimate           │
│                   reporters.                               │
│                   Why: Over-aggressive guardrails will     │
│                   block real incidents. We flag, not       │
│                   block, for edge cases.                   │
│                                                            │
│  CONSTRAINT BOX                                            │
│    IS:      Layered checkpoints — fast/cheap first,        │
│             slow/expensive last                            │
│    IS NOT:  A single wall that either blocks or passes     │
│    DECIDES: Security vs usability — we lean toward         │
│             flagging suspicious input, not rejecting it    │
│                                                            │
│  ONE-LINE HANDLE                                           │
│    "Three airport checkpoints — metal detector, X-ray,     │
│     human inspector"                                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## One-Line Handles (all concepts)

| Concept | Handle |
|---------|--------|
| **SRE Triage Agent** | ER triage nurse who reads X-rays and pages surgeons |
| **Context Loading** | Reference librarian who pulls 5 books, not 5000 |
| **Guardrails** | Three airport checkpoints — metal detector, X-ray, human inspector |
| **Observability** | Flight recorder on every stage — black box that survives the crash |
| **Ticket Service** | Hospital chart that follows the patient between departments |
| **Notifications** | Paging system — beeps the right doctor, calls the family when done |
| **Resolution Tracker** | Waiting room board — "your number has been called" |
| **E-Commerce Codebase** | The patient's medical history — not the patient itself |
| **Structured Output** | Form with checkboxes, not a blank page — forces complete answers |
| **Docker Compose** | Shipping container — everything packed, runs anywhere |
| **48h Hackathon** | Factory line — one finished car beats three half-built prototypes |
