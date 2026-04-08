# ECC + Gabe Workflow Guide

Quick reference for developing with Everything Claude Code (ECC) and the Gabe/KDBP alignment suite on this project.

---

## The Loop

```
/resume-session          # Pick up where you left off
     |
/plan                    # Clarify requirements, identify risks — wait for confirm
     |
/gabe-align [target]     # Check alignment with values before building
     |
/tdd                     # RED: write failing test → GREEN: make it pass → REFACTOR
     |                     (hooks run automatically: lint, format, quality gate)
/gabe-assess [change]    # Before non-obvious decisions — surfaces blast radius
     |
/verify                  # Build → types → lint → tests → security → diff review
     |
/code-review             # Security + quality review of uncommitted changes
     |
/gabe-review             # Risk-priced findings + deferred item tracking
     |
git commit               # KDBP checkpoint fires automatically (values + scenarios)
     |
/save-session            # Capture state for next session
```

Not every command runs every cycle. Use what fits the moment.

---

## ECC Commands

### Planning & Structure

| Command | When | What it does |
|---------|------|-------------|
| `/plan` | Before coding | Restates requirements, assesses risks, creates step-by-step plan. Waits for your confirm. |
| `/blueprint` | Big multi-session work | Breaks objective into self-contained steps a fresh agent can execute cold. |

### Implementation

| Command | When | What it does |
|---------|------|-------------|
| `/tdd` | Writing features/fixes | Enforces RED → GREEN → REFACTOR. Commits at each stage. 80%+ coverage. |
| `/build-fix` | Build/type errors | Fixes one error at a time with minimal safe changes. |

### Quality Gates

| Command | When | What it does |
|---------|------|-------------|
| `/verify` | Before PR | Runs build, types, lint, tests, security scan, diff review in order. Blocks on CRITICAL/HIGH. |
| `/code-review` | Before merge | Reviews uncommitted changes or GitHub PRs. 7-point checklist (correctness, types, patterns, security, perf, completeness, maintainability). |

### Session Continuity

| Command | When | What it does |
|---------|------|-------------|
| `/save-session` | End of work | Captures what worked, what failed, what to try next, blockers. |
| `/resume-session` | Start of work | Loads last session, shows briefing, waits for your go. |
| `/checkpoint` | Major milestones | Named state snapshot for comparison. |
| `/compact` | Phase boundaries | Strategic context clear. Use after research→planning or debug→next feature. Not mid-implementation. |

### Learning

| Command | When | What it does |
|---------|------|-------------|
| `/learn` | After solving something | Extracts reusable patterns from session. |
| `/evolve` | Periodically | Clusters learned instincts into skills/commands. |

---

## Gabe Commands

### Alignment

| Command | When | What it does |
|---------|------|-------------|
| `/gabe-align shallow` | Quick check | Core values only (A1-A3 + V1-V3). 3-5 lines. |
| `/gabe-align` | Before features | Full structural + user + project values check. |
| `/gabe-align deep` | Architecture decisions | Full values + alignment brief with risks and approach. |

### Decision Support

| Command | When | What it does |
|---------|------|-------------|
| `/gabe-assess [change]` | Before "obvious" changes | Surfaces blast radius, maturity fit, prerequisites, alternatives. |
| `/gabe-roast [perspective]` | Stress-testing | Adversarial gap review from a specific angle (e.g., `security`, `scalability`, `user`). |

### Code Quality

| Command | When | What it does |
|---------|------|-------------|
| `/gabe-review` | Before commit/PR | Risk-priced code review with confidence scoring. Tracks deferred items across reviews. |
| `/gabe-review deferred` | Periodically | Shows accumulated debt from checkpoints and past reviews. Items deferred 3x become BLOCKING. |

### Situational

| Command | When | What it does |
|---------|------|-------------|
| `/gabe-health` | Before epics, retros | God files, churn hotspots, coupling clusters, scope creep vs plan. |
| `/gabe-lens [concept]` | Concept unclear | Translates tech concepts into physical analogies and spatial maps. |
| `/gabe-help` | Uncertain what to do | Scans project state, recommends next Gabe command. |

---

## KDBP (Automatic)

KDBP runs via hooks — you don't call it directly.

### What fires automatically

| Trigger | What happens |
|---------|-------------|
| **Session start** | Loads `~/.kdbp/VALUES.md` + `.kdbp/VALUES.md` + `.kdbp/BEHAVIOR.md` into context |
| **git commit** | Checkpoint: evaluates all session/story values against diff, checks 3 scenarios per changed file for test coverage |
| **gh pr create** | Same checkpoint as commit |

### This project's values (checked every commit)

- **V1 — No Ghost States:** Every async operation has visible status. No fire-and-forget.
- **V2 — Demo or Die:** If it won't show in the 3-min demo, deprioritize it.
- **V3 — Deliver, Don't Design:** Working > elegant. Refactor only if it unblocks.

### Checkpoint output looks like

```
KDBP Checkpoint — Pre-Commit

Values:
  V1 — No Ghost States:     PASS
  V2 — Demo or Die:         CONCERN — new feature not on demo path
  V3 — Deliver, Don't Design: PASS

Scenarios (pipeline/triage.py):
  User submits incident with image      COVERED
  Empty submission (no text)             NOT COVERED
  API timeout during triage              NOT COVERED

Action: 2 untested scenarios. Fix now or defer to /gabe-review deferred
```

---

## ECC Hooks (Run Automatically)

You don't invoke these — they fire on tool use:

| Hook | When | Effect |
|------|------|--------|
| block-no-verify | `git commit --no-verify` | **BLOCKS** — protects pre-commit hooks |
| commit-quality | `git commit` | Lints staged files, validates message, detects secrets. Blocks on critical. |
| git-push-reminder | `git push` | Warns to review changes first |
| config-protection | Edit linter/formatter configs | **BLOCKS** — fix code, don't weaken configs |
| suggest-compact | Every ~50 tool calls | Suggests `/compact` at logical intervals |
| quality-gate | After file edits | Fast quality checks in background |
| console-warn | After edits | Warns about console.log |
| session-end | Response complete | Persists session state, extracts patterns, tracks cost |

---

## Workflow Recipes

### Starting a new feature

```
/plan                        # What are we building?
/gabe-align [target]         # Does it align with values?
/tdd                         # Write test first, then implement
/verify                      # Quality gates
git commit                   # KDBP checkpoint fires
```

### Fixing a bug

```
/tdd                         # Write reproducing test (RED), then fix (GREEN)
/verify                      # Make sure nothing else broke
/gabe-review                 # Check the fix is solid
git commit
```

### Before submitting the hackathon

```
/gabe-roast security         # Stress-test security (high-scoring category)
/gabe-roast user             # Will a user actually be able to use this?
/gabe-health                 # Any fragile spots?
/verify                      # Full quality gate
/gabe-align deep             # Final alignment check
```

### Switching context (pause/resume)

```
/save-session                # Capture everything
# ... time passes ...
/resume-session              # Load and orient
```

### Quick decision check

```
/gabe-assess [change]        # Is this change safe? What's the blast radius?
```

---

## File Locations

| What | Where |
|------|-------|
| Project values | `.kdbp/VALUES.md` |
| Project behavior | `.kdbp/BEHAVIOR.md` |
| Alignment ledger | `.kdbp/LEDGER.md` |
| Deferred items | `.kdbp/deferred-cr.md` (created on first defer) |
| Session data | `~/.claude/session-data/` |
| ECC install config | `ecc-install.json` |
| Project settings | `.claude/settings.json` |
| Hackathon context | `docs/hackathon_context/` |
| Architecture analysis | `docs/neo-analysis/` |
