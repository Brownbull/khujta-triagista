# Screen Recording Guide — Triagista Demo

> Actions only. No narration context. Read the time + action, do it on screen.

**Total target: 3:00** | Start recording before each segment.

---

## Pre-recording Setup

- [ ] `docker compose down -v && docker compose up --build -d` (fresh seed)
- [ ] Open browser at `http://localhost:8100/incidents`
- [ ] Dark theme active, sidebar expanded
- [ ] Langfuse open in a second tab: `http://localhost:3100`
- [ ] Browser zoom: 100%, window ~1280x800
- [ ] Have a sample `.log` file ready to attach (any text file renamed to `.log`)

---

## Recording Actions

### 0:00 — 0:12 | Dashboard overview

1. Screen shows `http://localhost:8100/incidents` with 18 incidents
2. Slowly scroll down the list (show severity badges, engine badges, status badges)
3. Scroll back up

### 0:12 — 0:22 | Filters and sorting

1. Click the **Status** dropdown, select **Dispatched**, let it filter
2. Click the **Severity** dropdown, select **P1**, let it filter
3. Click **Clear filters**
4. Click the **Created** column header to sort descending

### 0:22 — 0:30 | Architecture diagram

1. Open the repo README on GitHub (or local browser preview)
2. Scroll to the **Architecture** Mermaid diagram
3. Pause 3 seconds on the diagram

### 0:30 — 0:50 | Submit new incident

1. Click **+ Report New** in the sidebar
2. Fill in:
   - Name: `SRE On-Call`
   - Email: `oncall@solidus.io`
   - Description: `Payment gateway returning HTTP 502 errors during checkout. All customers affected since 14:30 UTC. Stripe webhook handler appears to be timing out. Error rate jumped from 0.1% to 45% in the last 15 minutes.`
3. Click **Choose files**, attach a `.log` file
4. Click the **Premium** engine card (should highlight blue)
5. Click **Submit Incident**
6. Progress overlay appears — let it run

### 0:50 — 1:10 | Triage results

1. Wait for redirect to detail page (or speed up the progress overlay in editing)
2. Show the top section: status badge, severity badge (P1/P2), confidence score
3. Scroll down slowly past:
   - Triage Engine strip (model, framework, tokens)
   - Description section
   - Root Cause Hypothesis
   - Related Files (Solidus paths)
   - Recommended Actions

### 1:10 — 1:25 | Pipeline info + context

1. Scroll up to the pipeline progress dots
2. Click the **Guardrail** dot — info panel appears below
3. Wait 2 seconds, click the **Triaged** dot — panel updates
4. Click the **Dispatched** dot — panel updates
5. Click outside to dismiss

### 1:25 — 1:45 | Dispatch cards

1. Scroll down to the **Dispatch** section
2. The Ticket card should be open — show title, assignee, labels
3. Click to expand the **Email** notification card
4. Click to expand the **Chat** notification card

### 1:45 — 1:55 | Acknowledge + Resolve

1. Scroll up, click **Acknowledge** button
2. Status changes — pause 1 second
3. Click **Resolve** button
4. In the dialog: select type **Fix**, type notes: `Stripe webhook timeout increased to 30s, monitoring confirmed recovery`
5. Click **Confirm Resolve**
6. Status shows Resolved

### 1:55 — 2:15 | Chat view + Explanation layers

1. Click the **Chat** tab in the top navigation
2. Scroll down the conversation timeline slowly (show AI bubbles)
3. Scroll back up
4. Go back to the **Detail** tab
5. Click **Specialist** explanation layer button
6. Click **Non-technical** explanation layer button
7. Click **General** to return

### 2:15 — 2:30 | Guardrail rejection

1. Click **All Incidents** in the sidebar
2. Filter by **Status: Rejected** (or find a rejected incident in the list)
3. Click into the rejected incident
4. Show the guardrail rejection panel: injection score, flags, threat analysis
5. Scroll to see full rejection details

### 2:30 — 2:45 | Langfuse observability

1. Switch to Langfuse tab (`http://localhost:3100`)
2. Navigate to **Traces** — show the list of pipeline traces
3. Click into one trace — show the span tree (guardrail, context-retrieval, triage-generation, dispatch)
4. Go back, click **Sessions** — show incident-grouped sessions

### 2:45 — 2:50 | Three engines

1. Switch back to the app
2. Click **+ Report New** in sidebar
3. Show the 3 engine cards: Basic, Premium, Experimental
4. Hover each briefly

### 2:50 — 3:00 | Closing

1. Navigate to `http://localhost:8100/incidents` (full list view)
2. Slowly scroll through the list one final time
3. Stop recording

---

## Post-recording Editing Notes

| Segment | Edit |
|---------|------|
| 0:50 progress overlay | Speed up 4-8x while waiting for triage |
| All navigation transitions | Cut/trim to show only the destination state |
| Langfuse login | Cut — start from already-logged-in state |
| Any error/retry | Cut out, re-record that segment |
