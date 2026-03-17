---
description: Show current project status and suggest next steps
---

Show where we are and what to do next.

## Process

1. **Read project state**:
   - `${CLAUDE_PLUGIN_ROOT}/_memory/index.json` for active project
   - `${CLAUDE_PLUGIN_ROOT}/_memory/projects/{project}.json` for progress
   - Most recent file in `${CLAUDE_PLUGIN_ROOT}/_memory/sessions/` for last session summary

2. **Show status**:

```
Project: {name or "No active project"}
Last session: {date} - {summary}
Progress: {last 3 entries}
Next step: {suggested next action}
```

3. **If no active project**: List available project files in `_memory/projects/` or suggest creating one.

4. **If resuming after a break**: Check for handoff documents in `_memory/sessions/` and present the most recent one.

## Creating a Handoff

If the user is ending a session, create a handoff:

```markdown
# Session Handoff - {date}

## What was done
- {action 1}
- {action 2}

## Current state
- {what's working}
- {what's broken/incomplete}

## Next steps
1. {most important next action}
2. {second priority}

## Open questions
- {anything unresolved}
```

Save to `${CLAUDE_PLUGIN_ROOT}/_memory/sessions/handoff-{date}.md`
