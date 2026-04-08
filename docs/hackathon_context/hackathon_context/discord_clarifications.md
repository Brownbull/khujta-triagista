# Discord Clarifications & Additional Context

Supplementary context extracted from the AgentX Hackathon Discord server on 2026-04-07.
This file captures organizer rulings, Q&A answers, and details NOT present in the other hackathon_context files.

---

## Submission Deadline (Exact Times)

- Mexico: April 9, 9:00 PM CST (UTC-6)
- Colombia: April 9, 10:00 PM COT (UTC-5)
- Chile: April 9, 11:00 PM CLT (UTC-4)

All teams have the same amount of time from kick-off. Late submissions will not be accepted.

---

## Organizer Q&A Rulings (from Kick-off and Discord)

These are direct answers from the organizer (sebastianmontagna) that clarify ambiguities in the assignment.

### What counts as an "incident report"?

> "That's up to you to define, scope, implement and manage."

The assignment intentionally leaves the format open. You define what an incident report looks like for your SRE Agent.

### Must we build an input UI?

> "You should create an input UI. After processing, you can send tickets to Jira, Notion, or other systems."

An input UI is required. The ticketing system integration is downstream.

### Does the resolution step require human or agent action?

> "If you can come up with an extra step to classify and address things agentically, it is a great differentiator and would be great. But it is also complex, so up to you!"

The 5 required steps assume the ticket gets resolved (by a human or otherwise). Adding agentic resolution is optional but valued as a differentiator.

### Required steps (confirmed as the only mandatory ones)

1. Submit the report via UI.
2. Agent triages on submit: extracts key details + produces an initial technical summary (using code/docs as available).
3. The agent creates a ticket in a ticketing system (Jira/Linear/Other).
4. Agent notifies the technical team (email and/or communicator).
5. When the ticket becomes resolved, the agent notifies the original reporter.

### Demo video format

> "The video should clearly demonstrate the value and main flow of the solution (step-by-step is not strictly required)."

### Can we team up with solo participants?

Yes. The #team-creation channel was enabled for coordination.

### Can we use local LLM models?

> "Yes, preferably with an OpenAI-compatible endpoint for integration."

### Any restrictions on what we can build?

> "No strict restrictions, but solutions should follow ethical AI principles and responsible AI guidelines."

### Security level expected?

> "No strict requirements — follow responsible AI principles, though this is open for you to showcase your engineering and creative capabilities."

### Ticketing workflow — is one provided?

> "No predefined system — you can choose and design your own approach."

### Which LLM providers are allowed?

> "There is no restriction on which LLM provider you use."

OpenAI-compatible APIs are a plus for maintainability, scalability, and portability.
OpenRouter is recommended if you want to give reviewers flexibility (single API key, multiple models).

### API keys for reviewers

From the organizer team (adroh_sose):
> "Please don't include API keys. We have access to most providers. As long as the endpoint supports the OPENAI or Anthropic API, we can configure it."

---

## AGENTS_USE.md — Required Template (9 Sections)

Every team must include an `AGENTS_USE.md` file at the root of the repository. The template has 9 sections:

1. **Agent Overview** — name, purpose, tech stack
2. **Agents & Capabilities** — structured description of each agent/sub-agent (Role, Type, LLM, Inputs, Outputs, Tools)
3. **Architecture & Orchestration** — system design, data flow, error handling, handoff logic (include a diagram)
4. **Context Engineering** — context sources, strategy, token management, grounding
5. **Use Cases** — step-by-step walkthroughs from trigger to resolution
6. **Observability** — logging, tracing, metrics, dashboards
7. **Security & Guardrails** — prompt injection defense, input validation, tool safety, data handling
8. **Scalability** — current capacity, scaling approach, bottlenecks
9. **Lessons Learned & Team Reflections** — what worked, what you'd change, key trade-offs

**Critical:** Sections 6 (Observability) and 7 (Security) require **actual evidence** — screenshots, log samples, trace exports, or test results. Descriptions alone are NOT sufficient.

The full template is available at: `docs/discord-export/attachments/AGENTS_USE.md`

---

## FAQ Summary (from #faq channel)

### FAQ #1: Submission deadline
See "Submission Deadline" section above.

### FAQ #2: API keys / licenses
Not provided by organizers. Use free tiers:
- Free: Google Gemini, Groq, Mistral, Cloudflare Workers AI, Hugging Face
- Pay-as-you-go: OpenAI ($5 min), Anthropic ($5 min), OpenRouter, Together AI

### FAQ #3: Where to find assignment details
All in the #assignment channel: Assignment, Technical Requirements, Deliverables (3 posts).

### FAQ #4: E-commerce framework options
Recommended:
- .NET — eShop by Microsoft: https://github.com/dotnet/eShop
- Ruby on Rails — Solidus: https://github.com/solidusio/solidus
- Node.js — Reaction Commerce: https://github.com/reactioncommerce/reaction

Any open-source e-commerce repo is allowed if it is publicly available, medium-to-complex, and gives the agent enough code/docs to analyze.

### FAQ #5: How #ask-mentors works
Restricted to Team Leaders. One question per message, include team name in brackets.
Mentors help with: architecture, observability, security best practices, assignment clarification.
Mentors will NOT: write code, debug your implementation, answer logistics.

### FAQ #6: API provider guidance
- Be explicit about which provider/model your project requires in QUICKGUIDE.md and .env.example
- OpenAI-compatible APIs are a plus
- OpenRouter is a good single-key option for reviewer flexibility

### FAQ #7: What is AGENTS_USE.md?
See "AGENTS_USE.md" section above.

---

## Evaluation Dimensions (for reference)

1. **Reliability** — consistent behavior, edge case handling
2. **Observability** — structured logs, traces, metrics across agent stages
3. **Scalability** — growth handling, documented assumptions
4. **Context engineering** — how well the agent manages and uses context
5. **Security** — prompt injection defenses, safe tool usage
6. **Documentation** — well-documented, clear, reproducible

---

## Hackathon Scale

91 teams registered. Participants from Mexico, Colombia, and Chile.
Organized by SoftServe.

Prizes: 1st $5,000 / 2nd $3,000 / 3rd $2,000
