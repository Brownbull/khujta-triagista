# Gabe-Align Setup Fixes — Field Report

**Project:** AgentX SRE Triage Agent
**Date:** 2026-04-07
**Context:** `/gabe-align init` on a fresh project, then verified gabe suite readiness

---

## Issue 1: KDBP hooks not installed by `init`

**What happened:** After running `/gabe-align init`, the `.kdbp/` directory was created correctly (BEHAVIOR.md, VALUES.md, LEDGER.md), but the two required hooks were not added to `~/.claude/settings.json`. Without them, the automatic checkpoint system is dead on arrival.

**Expected:** `/gabe-align init` should check for the hooks and either install them or warn that they're missing.

**Missing hooks:**

1. **SessionStart** — loads `~/.kdbp/VALUES.md` + `.kdbp/VALUES.md` + `.kdbp/BEHAVIOR.md` into session context
2. **PreToolUse (Bash matcher)** — fires KDBP checkpoint before `git commit` / `gh pr create`

**Fix applied manually:** Added both hooks to `~/.claude/settings.json` alongside existing rtk-rewrite and gsd hooks. The PreToolUse KDBP hook was added as a second entry under the existing Bash matcher (same matcher, multiple hooks).

**Suggested fix for base repo:** In SKILL.md's init procedure, after writing `.kdbp/` files, check `~/.claude/settings.json` for the two KDBP hooks. If missing:
- Option A: Auto-install them (with user confirmation)
- Option B: Print a warning with the exact JSON to add
- Option C: Provide a `/gabe-align install-hooks` subcommand

### Hook JSON reference

```json
// Add to PreToolUse[matcher="Bash"].hooks array:
{
  "type": "command",
  "command": "TOOL_INPUT=$(cat); if echo \"$TOOL_INPUT\" | grep -qE '\"command\".*git commit|\"command\".*gh pr'; then if [ -f ~/.kdbp/VALUES.md ] || [ -f .kdbp/VALUES.md ]; then echo '{\"additionalContext\": \"KDBP CHECKPOINT: Before committing, evaluate all values (from ~/.kdbp/VALUES.md and .kdbp/VALUES.md) against git diff. For each changed source file, name 3 realistic user scenarios (including errors, empty data, edge conditions) and check if each has a test. Report per-value PASS/CONCERN and per-scenario COVERED/NOT COVERED. If untested scenarios exist, suggest writing tests before committing.\"}'; fi; fi",
  "timeout": 3000
}

// Add to SessionStart[0].hooks array:
{
  "type": "command",
  "command": "VALUES=''; if [ -f ~/.kdbp/VALUES.md ]; then VALUES=\"USER_VALUES=$(head -20 ~/.kdbp/VALUES.md)\"; fi; if [ -f .kdbp/VALUES.md ]; then VALUES=\"$VALUES PROJECT_VALUES=$(head -20 .kdbp/VALUES.md)\"; fi; if [ -f .kdbp/BEHAVIOR.md ]; then VALUES=\"$VALUES BEHAVIOR=$(head -10 .kdbp/BEHAVIOR.md)\"; fi; if [ -n \"$VALUES\" ]; then echo \"{\\\"additionalContext\\\": \\\"KDBP Active. $VALUES\\\"}\"; fi",
  "timeout": 3000
}
```

---

## Issue 2: No gabe-lens cognitive profile

**What happened:** `~/.claude/gabe-lens-profile.md` doesn't exist. Gabe-align deep mode references it for cognitive constraints section in the alignment brief.

**Impact:** Low — only affects deep mode output. Shallow/standard/checkpoint all work without it.

**Suggested fix for base repo:** In SKILL.md deep mode procedure, if profile is missing, skip the "Cognitive Profile Constraints" section with a note: `"No cognitive profile found. Run /gabe-lens to generate one."` Currently it's a silent omission.

---

## Issue 3: Init doesn't verify skill dependencies

**What happened:** Had to manually audit whether all 7 gabe-* skills were installed, hooks were configured, and user/project `.kdbp/` existed. The init command only creates files — it doesn't report on the broader readiness state.

**Suggested fix for base repo:** After init writes files, run a quick readiness check and print a summary:

```
✅ .kdbp/ created (BEHAVIOR.md, VALUES.md, LEDGER.md)
✅ ~/.kdbp/VALUES.md found (3 user values)
❌ SessionStart hook missing — run /gabe-align install-hooks
❌ PreToolUse checkpoint hook missing — run /gabe-align install-hooks
⚠️  ~/.claude/gabe-lens-profile.md missing (optional, for deep mode)
```

This would save the manual audit step every time.

---

## Summary

| Fix | Severity | Effort |
|-----|----------|--------|
| Hook installation during init | High — checkpoint system doesn't work without it | Medium — need to read/write settings.json safely |
| Missing profile graceful handling | Low — only deep mode | Low — add conditional in procedure |
| Post-init readiness report | Medium — saves manual debugging | Low — just read and report |
