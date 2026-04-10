# Screen Recording Guide — Synced to Narration Audio (2:54)

> Play `narration_complete.wav` through headphones while screen recording.
> Match your screen actions to the timestamps below.

**Audio duration: 2:54** | Play audio → do actions on screen in sync

---

## Pre-recording Setup

- [ ] `docker compose down -v && docker compose up --build -d` (fresh seed)
- [ ] Browser at `http://localhost:8100/incidents` — dark theme, sidebar expanded
- [ ] Langfuse in second tab: `http://localhost:3100` (already logged in)
- [ ] Browser zoom 100%, window ~1280x800
- [ ] Sample `.log` file ready to attach
- [ ] `narration_complete.wav` loaded in Audacity or media player — headphones on
- [ ] OBS recording ready — capture browser window only

---

## Synced Actions

### [0:00 — 0:11] HOOK — Dashboard overview
*"When an SRE incident hits... Triagista does that in fifteen seconds."*

1. Show `localhost:8100/incidents` with 18 incidents
2. Slowly scroll down the list (show severity, engine, status badges)
3. Scroll back up

---

### [0:11 — 0:28] WHAT IT IS — Scroll list details
*"It's an AI agent that takes an incident report... auto-dispatches a ticket with team notifications."*

1. Scroll through list showing different statuses and engines
2. Click Status dropdown → filter → clear
3. Click Severity dropdown → filter P1 → clear

---

### [0:28 — 0:40] ARCHITECTURE — Diagram
*"The pipeline has five stages... Let me show you the full flow."*

1. Open README.md Mermaid architecture diagram
2. Pause 3 seconds on diagram
3. Navigate back to app

---

### [0:40 — 0:54] SUBMIT — New incident
*"I'm submitting a new incident... Watch the progress overlay."*

1. Click **+ Report New**
2. Fill: Name `SRE On-Call`, Email `oncall@solidus.io`
3. Description: `Payment gateway returning HTTP 502 errors during checkout. All customers affected since 14:30 UTC. Stripe webhook handler appears to be timing out.`
4. Attach `.log` file
5. Click **Premium** engine card
6. Click **Submit Incident**

---

### [0:54 — 1:14] TRIAGE RESULTS
*"In about fifteen seconds... engine info strip shows model, framework, and exact token usage."*

1. Progress overlay appears (speed up 4-8x in editing if needed)
2. Detail page loads — show severity badge, confidence score
3. Scroll past: Triage Engine strip, Root Cause, Related Files, Recommended Actions

---

### [1:14 — 1:34] CONTEXT ENGINEERING
*"The context engineering here is key... each file is verified to exist in the repo."*

1. Scroll to Related Files section (Solidus Ruby paths)
2. Click **Guardrail** pipeline dot — info panel
3. Click **Triaged** dot
4. Click **Dispatched** dot

---

### [1:34 — 1:52] DISPATCH
*"Dispatch happened automatically... connecting to real Jira or Slack is configuration."*

1. Scroll to Dispatch section
2. Show Ticket card (title, assignee, labels)
3. Expand **Email** notification card
4. Expand **Chat** notification card

---

### [1:52 — 2:05] RESOLVE
*"The on-call engineer acknowledges... acknowledge, resolve, notify."*

1. Click **Acknowledge** → status changes
2. Click **Resolve** → type **Fix**, notes: `Stripe webhook timeout increased to 30s`
3. Click **Confirm Resolve**

---

### [2:05 — 2:14] EXPLANATION LAYERS
*"These explanation layers let you switch... same triage, three audiences."*

1. In **Details** view, click **Specialist** explanation layer
2. Click **Non-technical** layer
3. Click **General** to return

---

### [2:14 — 2:27] GUARDRAILS
*"If someone submits a prompt injection... fully traced in Langfuse."*

1. Click **All Incidents** in sidebar
2. Find a **Rejected** incident → click into it
3. Show guardrail panel: injection score, flags
4. Scroll rejection details

---

### [2:27 — 2:35] OBSERVABILITY
*"Langfuse captures every pipeline stage... rejections are tagged and visible."*

1. Switch to Langfuse tab
2. Show **Traces** list → click into one trace
3. Go back → **Sessions** tab

---

### [2:35 — 2:44] THREE ENGINES
*"Three engines to choose from... same structured output, different providers."*

1. Switch back to app → **+ Report New**
2. Show the 3 engine cards: Basic, Premium, Experimental
3. Hover each briefly

---

### [2:44 — 2:54] WRAP
*"Triagista. Built solo in forty-eight hours... Thanks for watching."*

1. Navigate to `localhost:8100/incidents` (full list)
2. Hold steady for 10 seconds
3. Stop recording

---

## Post-recording Editing

| Edit | Where |
|------|-------|
| Speed up 4-8x | Progress overlay (~0:54) |
| Cut transitions | Navigation between pages |
| Cut Langfuse login | Start from logged-in state |
