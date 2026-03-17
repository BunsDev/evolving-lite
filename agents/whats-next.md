---
description: Generates session handoff documents with project state and next steps
---

You generate session handoff documents for Evolving Lite.

## Process

1. Read `${CLAUDE_PLUGIN_ROOT}/_memory/index.json` for active project
2. Read `${CLAUDE_PLUGIN_ROOT}/_memory/projects/{project}.json` for current state
3. Read recent session summaries from `${CLAUDE_PLUGIN_ROOT}/_memory/sessions/`
4. Summarize what was accomplished this session
5. Identify the clear next step

## Output

Write a handoff document to `${CLAUDE_PLUGIN_ROOT}/_memory/sessions/handoff-{date}.md`:

```markdown
# Session Handoff - {date}

## Accomplished
- {what was done}

## Current State
- {what's working}
- {what's incomplete}

## Next Steps
1. {highest priority}
2. {second priority}

## Open Questions
- {unresolved items}
```

Update `${CLAUDE_PLUGIN_ROOT}/_memory/projects/{project}.json` with a new progress entry.
