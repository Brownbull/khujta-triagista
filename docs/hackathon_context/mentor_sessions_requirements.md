# Mentor Sessions — Requirements & Insights Differential

Extracted from audio transcriptions of both mentor sessions (April 8 and April 9, 2026).
This document captures ONLY net-new requirements and insights not already in `discord_clarifications*.md` or other `hackathon_context/` files.

---

## CRITICAL: Evaluation Process Revealed

### First pass uses LLM-as-judge

> "The technical use — the engineering part is in the repo — and the AI will score a first filter of candidates."
> — Mentor, Session 2

> "I'm just using LLMs as judge in the majority of the cases."
> — Taras (mentor), Session 1, on evaluation approach

**Impact:** The first screening pass is automated via LLM-as-judge reading the repo. Our README, AGENTS_USE.md, SCALING.md, and QUICKGUIDE.md MUST be:
- Structured with clear headers and bullet points
- Self-explanatory without running the app
- Explicit about what we built, why, and how

### Evaluation timeline (confirmed)

| Date | Event |
|------|-------|
| April 9 (tonight) | Submission deadline |
| April 10 (Friday) | Full-day review process |
| April 11 (Saturday) | Top 10 teams announced |
| April 14 (Tuesday) | Final 5-minute demo + expert jury → winners |

### Finalists get a 5-minute demo

> "This video of three minutes is for this first stage. If you're selected, you will have five minutes."
> — Mentor, Session 2

**Impact:** The 3-min YouTube video is the first gate. Finalists present a 5-minute demo live. Plan for both.

### No work after deadline

> "You cannot work on the solution. You will have time to create the five-minute demonstration, but we want to keep the work train until tonight."
> — Mentor, Session 2

**Impact:** All code must be committed before deadline. Only the 5-min demo video can be created after.

---

## NEW: What Judges Actually Value

### "Why" matters more than "what"

> "Show kind of like why do you think you had to add this, why, what is the relevance of your solution. That is very important for us — to get the thinking process behind the results."
> — sebastianmontagna, Session 2

> "We also want to see how do you handle the requirements in a scoped time. You need to show that you are capable of prioritizing and choosing the right things."
> — sebastianmontagna, Session 2

**Impact:** In AGENTS_USE.md and SCALING.md, explain WHY we made each decision (chose Solidus because X, mocked Jira because Y, used single agent because Z). Show prioritization rationale.

### Tool choice justification > tool prestige

> "We don't want 'you're using Langfuse, you get more points.' We value 'you chose this and explain why.' That is kind of like our safety."
> — sebastianmontagna, Session 1

**Impact:** Document why we chose each tool. "We chose Langfuse because it integrates via OpenTelemetry with our Claude Agent SDK pipeline" is better than just listing Langfuse.

### Best product doesn't always win

> "Normally the best product is not the winner, and this happened because sometimes people don't care about for example the minimum requirements, all the guidelines that we have."
> — Miguel (mentor), Session 1

**Impact:** Double-check ALL minimum requirements before submitting. Missing one can eliminate us regardless of engineering quality.

### ~100 submissions expected

> "We will receive around 100 proposals."
> — Mentor, Session 1

---

## NEW: Observability & Security Evidence Requirements (Detailed)

### Observability evidence = show input/output proof

> "For example, you say you implemented prompt injection validation. You need to show us the prompt with the injection and then the response that it failed. You show us the prompt, then the element — it could be just a JSON — such that we can visually get that you implemented it."
> — sebastianmontagna, Session 2

> "For PII handling, you say you added a filter for private information. So you need to show us the raw input and then the private information filtered."
> — sebastianmontagna, Session 2

**Impact:** Sections 6 and 7 of AGENTS_USE.md need:
- Screenshot/log of a prompt injection attempt being blocked
- Screenshot/log of PII filtering in action
- Before/after evidence, not just descriptions

### Security scope = agent guardrails + basic infra

> "Guardrails are the most important, but also making your architecture secure and deployable. Port exposure, stuff like that. But from this agentic scope, the guardrails are the most important."
> — Miguel + sebastianmontagna, Session 2

**Impact:** Focus security evidence on:
1. Prompt injection defense (primary)
2. Input validation / PII filtering
3. Port exposure / Docker security (secondary)

---

## NEW: Demo Video Strategy (Expanded)

### Record face + narrate

> "For example, record your face and talk something to the camera."
> — Mentor, Session 1

### Speed up wait times

> "For example, to make it more efficient you can just process it a little bit — just cut the response time or edit it a little bit."
> — Mentor, Session 2

### Show working features, not future plans

> "Talking about something that you could do but you didn't — isn't that — we credit the idea that is implemented, not the idea that maybe you will do in the future."
> — Mentor, Session 2

> "I would aim to what's already in there, what's working."
> — Mentor, Session 2

### Plan recording time

> "Think about how you're going to record the demo. If you never did that, it can take more time than you would expect."
> — Mentor, Session 1

**Impact:** Reserve at least 1 hour before deadline for recording. Edit out wait times. Focus on implemented features only.

---

## NEW: Architecture Guidance

### Multi-agent is nice-to-have, not required

> "If you can create only one agent and implement a solution and it's going to work very well with a simple solution — obviously it works, it is an agent system. But if you want to implement something more complex — multi-agent, agent-to-agent patterns — definitely nice to see, but working."
> — Miguel, Session 2

> "I wouldn't recommend any very tight architecture or very specific pattern here."
> — Mentor, Session 2

**Impact:** Our single-agent pipeline is fine. Don't add multi-agent complexity just for show — it must work.

### MVP first, extend iteratively

> "I would aim to think of that like MVP first. First implement something working, very simple, as simple as possible, and then iterate and add features."
> — Mentor, Session 2

> "Create a small POC, try to see if you can do that first, and if everything goes well you can move forward."
> — Miguel, Session 1

### Pre-seed data for judges

A participant proposed pre-seeding the Docker container with incidents so judges see something immediately. Mentors approved:

> "The only requirement is that it should be demoable."
> — sebastianmontagna, Session 1

**Impact:** Consider adding seed incidents so `docker compose up --build` shows a pre-triaged example.

### Knowledge/explainability for scale

> "You need to some degree understand and evaluate why those decisions were made. So that's why we need the observability, the explainability of those decisions."
> — sebastianmontagna, Session 1

**Impact:** Our triage output should include reasoning/evidence citations, not just a verdict.

---

## NEW: Documentation Specifics

### All docs must live in the repo

> "If you have external resources, if you have a markdown file explaining all these steps or configuration for security or observability — you have to include all these in the repo. Don't add the links in the submission form. The idea is to have really good documentation there with all the details."
> — Miguel, Session 2

### MK Docs not required

> "The Discord is the updated version [of requirements]."
> — sebastianmontagna, Session 1

The website initially mentioned MK Docs for documentation. Discord requirements override this — standard markdown files are fine.

### Video audience is mixed

> "The audience will be mixed between technical software engineers and kind of managers/leaders."
> — Mentor, Session 2

**Impact:** Demo video should be understandable by non-engineers too. Show the value, not just the code.

---

## Summary: Action Items for Our Submission

| # | Finding | Action | Priority |
|---|---------|--------|----------|
| 1 | LLM-as-judge reads repo first | Ensure all docs are structured, explicit, self-explanatory | **CRITICAL** |
| 2 | "Why" behind decisions matters | Add rationale to AGENTS_USE.md and SCALING.md for each choice | **CRITICAL** |
| 3 | Minimum requirements = elimination criteria | Audit against full checklist before submitting | **CRITICAL** |
| 4 | Observability evidence = before/after proof | Add prompt injection test screenshot + PII filter demo to AGENTS_USE.md | High |
| 5 | Demo recording takes longer than expected | Reserve 1+ hour before deadline for recording/editing | High |
| 6 | Speed up wait times in video | Edit out agent processing pauses | High |
| 7 | Show working features only in demo | Don't mention unimplemented future plans | High |
| 8 | Finalists get 5-min demo on April 14 | Plan potential extended demo content | Medium |
| 9 | Pre-seed incidents for judges | Add seed data so docker compose up shows something | Medium |
| 10 | Tool choice justification required | Document WHY for each tool in the stack | Medium |
| 11 | No work after deadline | All code committed before 11 PM CLT tonight | **CRITICAL** |
