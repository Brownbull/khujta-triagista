# Discord Clarifications — 2026-04-09 Differential

New information from Discord channels captured between April 8 ~16:05 and April 9 ~12:42 UTC.
This document covers ONLY net-new clarifications not already in `discord_clarifications.md` or `discord_clarifications_20260408.md`.

---

## CRITICAL: Submission Form Is Live

> **Form URL:** https://forms.cloud.microsoft/e/RmTGfWgQLQ

Published by nadiia_rnd in #hackathon-announcements on April 9 06:34 UTC.

> "Please double-check that your submission includes all required deliverables."
> "Don't forget to check the Terms & Conditions — they include full details about prize payouts and other important conditions."

**Note:** The form initially had a "Live demo link" field not mentioned in deliverables. This was flagged by a participant and **removed** by organizers (nadiia_rnd: "We've already fixed it and removed the extra field").

---

## NEW Organizer Clarifications

### Demo video strategy: quality over quantity

> "I'd suggest you to focus on making the best demo you can, for which a single ticket might be enough. Then you can clearly explain the coverage of your solution, how you implemented it and such, as part of the repo and the required documents we mentioned. They are certainly relevant for consideration, so even if you just demo one or a few tickets, supporting multiple incidents will be relevant."
> — sebastianmontagna, April 9, replying to a team asking whether to demo 2 incidents or many

**Impact:** Demo ONE incident really well. Document broader coverage in AGENTS_USE.md/SCALING.md. Judges read the docs — the video just needs to show value clearly.

### API keys: never include any, even for non-LLM tools

> "I would say that as a base, you should never provide any API keys. But if you are thinking of including something (apart from LLM providers) that requires it, ping me and we'll see if we can adjust."
> — sebastianmontagna, April 8, replying to whether non-LLM tool API keys should be included

**Impact:** No change for us (mocked integrations need no external keys). Confirms that ALL keys go in `.env.example` with placeholders, no exceptions.

### Using external AI tools in workflow is encouraged

> Q: "We are going for 2 IAs systems, since github copilot already has a PR review integration, can we use it? So we can trigger it to review the solution after the ticket is moved to 'QA'?"
> A: "Good idea 😉"
> — sebastianmontagna, April 9

**Impact:** Integrating existing AI tools (Copilot, etc.) into the SRE workflow is welcomed by judges. Not relevant for our current scope but good to know.

### "Communicator" in step 4 = Slack/Discord/Teams/etc.

A participant asked "what is the communicator?" (referring to step 4: "Agent notifies the technical team (email and/or communicator)"). No explicit answer was given, but from context throughout Discord, "communicator" means any team messaging platform (Slack, Discord, Teams). Our mocked Slack notification already covers this.

---

## NEW Logistical Updates

### Submission deadline confirmed: Thursday April 9

Same times as before (already in previous differential). No changes.

### Mentor session recordings shared

> "Here you can find the audio recordings of both mentor sessions. As a suggestion, transcription is very easy to do 👀"
> — sebastianmontagna, April 9

Audio files:
- `Mentor_Session_1.m4a` (April 8 session)
- `Mentor_Session_2.m4a` (April 9 session)

Available in #ask-mentors channel as attachments.

### Second learning session: "From Vibes to Verifiable"

> April 9, 9:00 AM CST | 10:00 AM COT | 11:00 AM CLT
> Link: https://youtube.com/live/d-w_e9BMQkY

Topic: How to move from rough idea to clear plan and spec, writing evals, verifiable agent behavior.

### Demo video reference shared by mentor

> Pawel (mentor) shared a reference hackathon demo video:
> https://www.youtube.com/watch?v=uu2M7GfkxAs
> Added to #resources channel.

### Validate public access before submitting

> "Please validate that we can actually access your demo video and repository 📣"
> — sebastianmontagna, April 9, after a team submitted with a private YouTube video

**Impact:** Before submitting: open an incognito window and verify both the YouTube video (set to Public/Unlisted) and the GitHub repo (set to Public) are accessible.

### Evaluation process includes LLM-judge

A participant asked about the evaluation process shared during kickoff: "LLM-judge -> Next -> Next..." but no detailed answer was provided in Discord. This suggests automated/LLM-based screening as the first pass (consistent with the "Automated screening" step in the evaluation process).

**Impact:** Our documentation (README, AGENTS_USE.md, QUICKGUIDE.md) should be clear enough for an LLM reader, not just humans. Structure with headers, bullet points, and explicit labels.

---

## Competitor Intelligence (from public submissions)

Two teams have already submitted publicly in #general-chat:

| Team | Stack | Approach |
|------|-------|----------|
| Fara-Hack 1.0 | Java 25, NATS JetStream | "Sovereign agentic runtime", deterministic 4-agent pipeline |
| Penguin Alley (individual) | Custom framework ("paco-framework") | Personal agent framework, fullstack |

**Impact:** Competition is active. Both submitted early (before final deadline). Focus on polish and completeness.

---

## Items NOT in Previous Docs — Action Required

| # | Finding | Action for Us | Priority |
|---|---------|---------------|----------|
| 1 | Submission form is live | Submit via https://forms.cloud.microsoft/e/RmTGfWgQLQ before deadline | **CRITICAL** |
| 2 | Demo ONE ticket well > many tickets poorly | Focus demo video on a single compelling incident end-to-end | High |
| 3 | LLM-judge likely in first screening pass | Ensure docs are LLM-readable: structured headers, explicit labels, no ambiguity | High |
| 4 | Validate public access before submit | Test repo + video in incognito before submitting | High |
| 5 | Mentor session recordings available | Optionally transcribe for any missed guidance | Low |
| 6 | Demo video reference available | Watch https://www.youtube.com/watch?v=uu2M7GfkxAs for inspiration | Low |

---

## No Changes To

These items from previous docs remain unchanged:
- 5-step core flow (submit -> triage -> ticket -> notify -> resolve)
- AGENTS_USE.md 9-section template requirement
- Evaluation dimensions (reliability, observability, scalability, context engineering, security, documentation)
- API key guidance (use .env.example, support OpenAI/Anthropic endpoints)
- Demo video format (3 min, English, YouTube, #AgentXHackathon)
- Docker Compose mandatory
- Mocked integrations acceptable
- Any e-commerce repo allowed (we use Solidus)
