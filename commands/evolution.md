---
description: Show what the system learned and changed recently
---

Show the evolution log - what Evolving Lite has learned, archived, and optimized.

## Process

1. **Read evolution log**: `${CLAUDE_PLUGIN_ROOT}/_memory/analytics/evolution-log.jsonl`
2. **Read session count**: `${CLAUDE_PLUGIN_ROOT}/_memory/.session-count`
3. **Count experiences**: User-created vs pre-warmed

## Display

```
=== Evolving Lite Evolution ===

Sessions: {total}
Current tier: {tier} ({name})
Tier 2 unlocks at: session 3 {if not yet reached}
Tier 3 unlocks at: session 10 {if not yet reached}

Recent changes (last 7 days):
  {date} | {type}: {summary}
  {date} | {type}: {summary}
  ...

Experiences: {user_count} learned + {prewarmed_count} pre-warmed
  - Last learned: {most recent user experience summary}
  - Most accessed: {highest access_count experience}

{If no recent changes}:
  No changes in the last 7 days. The system learns from your corrections
  automatically - just keep working normally.
```

## If user asks "what have you learned?"

Read experience files from `_memory/experiences/` (excluding `_prewarmed/`) and show:
- Total count
- By type (solution, gotcha, pattern, etc.)
- Most recent 5 with summaries
