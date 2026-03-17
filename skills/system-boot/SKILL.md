---
name: system-boot
description: Auto-activating session startup - reads memory, orients Claude, announces status. Triggers on session start or when user says "continue", "weiter", "resume".
---

# System Boot

On every session start, perform this bootup sequence:

## 1. Read Memory

Read `${CLAUDE_PLUGIN_ROOT}/_memory/index.json` for:
- `active_project`: Which project the user was working on
- `last_session`: When the last session was

If `active_project` is set, read `${CLAUDE_PLUGIN_ROOT}/_memory/projects/{active_project}.json` for:
- `progress`: Array of recent progress entries
- `next_step`: What was planned next
- `failures`: Known blockers or failures

## 2. Orient

Based on memory:
- What was the last progress entry?
- Are there any known failures or blockers?
- What was suggested as the next step?

## 3. Announce

Output a compact status line:

```
Evolving Lite | Session {n} | Tier {tier} | {experience_count} experiences
Last: {last_progress_summary}
Next: {next_step}
```

If this is the first session ever (no progress), announce:

```
Evolving Lite v1.0 | First session | {prewarmed_count} pre-warmed experiences loaded
Ready to work. The system learns from your corrections automatically.
```

## 4. Pick One Task

If the user hasn't specified what to work on, suggest the `next_step` from memory. Don't start multiple tasks - pick one.

## Continue Trigger

When the user says "continue", "weiter", "weitermachen", "fortsetzen", or "resume":
1. Read the most recent session summary from `${CLAUDE_PLUGIN_ROOT}/_memory/sessions/`
2. Load the plan if one was referenced
3. Continue immediately - no questions, just pick up where we left off

## Session End

When a session ends naturally (user says goodbye, or Stop hook fires):
- The session-summary hook handles progress logging automatically
- No manual action needed from the user
