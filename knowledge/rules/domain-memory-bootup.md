# Domain Memory Bootup (Evolving Lite)

**Priority**: HIGH
**Trigger**: Session start, after compaction, when user says "continue"/"weiter"

## Session Start

### 1. Read Memory

```
1. ${CLAUDE_PLUGIN_ROOT}/_memory/index.json -> Active project, last session
2. ${CLAUDE_PLUGIN_ROOT}/_memory/projects/{active}.json -> Goals, Progress, Next Step
```

### 2. Orient

- What was the last progress entry?
- Are there known failures or blockers?
- What was suggested as next step?

### 3. Announce

```
"Evolving Lite | Session {n} | Tier {tier}
 Last: {last_progress}
 Next: {next_step}"
```

### 4. Pick One Task

Choose ONE task. Not multiple. Atomic progress.

## Continue Trigger

When user says "continue", "weiter", "weitermachen", "fortsetzen":
1. Read most recent session summary from `_memory/sessions/`
2. Load plan if referenced
3. Continue immediately - no questions

## Progress Logging

After completing a task, update `_memory/projects/{project}.json`:

```json
{"date": "YYYY-MM-DD", "action": "What was done", "result": "Outcome", "next": "Next step"}
```

This happens automatically via session-summary hook at session end. For explicit mid-session saves, use `/remember`.
