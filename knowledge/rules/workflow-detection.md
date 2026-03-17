# Workflow Detection

Detect slash commands from natural language.

## Detection

Check user input against `${CLAUDE_PLUGIN_ROOT}/_graph/cache/detection-index.json`.

| Confidence | Action |
|------------|--------|
| High (9-10) | Ask: "Should I use /command?" |
| Medium (6-8) | Ask: "Do you mean /command?" |
| Low (1-5) | Ignore, respond normally |

## Rules

1. NEVER auto-execute without confirmation
2. On multi-match: ask which command fits
3. Conservative: better not trigger than trigger wrongly
