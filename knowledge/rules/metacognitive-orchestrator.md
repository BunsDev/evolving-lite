# Metacognitive Orchestrator

Automatic task-type detection and routing.

## Request Types

| Type | Signal | Action |
|------|--------|--------|
| Trivial | Single file, known location | Direct tools only |
| Explicit | Specific file/line, clear command | Execute directly |
| Exploratory | "How does X work?", "Find Y" | Delegate to Explore agent |
| Open-ended | "Improve", "Refactor", "Add feature" | Run DSV first, then assess |
| Ambiguous | Unclear scope | Ask ONE clarifying question |

## When to ask vs. proceed

| Situation | Action |
|-----------|--------|
| Single valid interpretation | Proceed |
| Multiple interpretations, similar effort | Proceed, note assumption |
| Multiple interpretations, 2x+ effort difference | Ask |
| Missing critical info | Ask |

## Context Loading

Load knowledge on-demand from `${CLAUDE_PLUGIN_ROOT}/_graph/cache/context-router.json`:
- Extract keywords from user input
- Match against route keywords
- Load only matched patterns/rules (not everything)
- This keeps context small (~5K tokens baseline instead of loading all knowledge)
