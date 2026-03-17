---
description: Show context window usage, active tier, and system stats
---

Show current system status and context statistics.

## Display

```
=== Evolving Lite Status ===

Session: {n} | Tier: {tier} ({tier_name})
Experiences: {user_count} user + {prewarmed_count} pre-warmed = {total}

Hooks active:
  Tier 1 (Safety):    context-warning, security-tier-check, health-sentinel, usage-tracker
  Tier 2 (Learning):  {active/inactive} correction-detector, delegation-enforcer, session-summary
  Tier 3 (Deep):      {active/inactive} thinking-recall, auto-archival, precompact-extract

Usage (this session):
  Tool calls: {from usage.json}
  Top tools: {top 3 by count}

Memory:
  Active project: {name or "none"}
  Sessions tracked: {count of session files}
  Plans: {count of plan files}
```

## Data Sources

- Session count: `${CLAUDE_PLUGIN_ROOT}/_memory/.session-count`
- Tier: Calculated from session count (1: 0+, 2: 3+, 3: 10+)
- Experiences: Count files in `_memory/experiences/` and `_memory/experiences/_prewarmed/`
- Usage: Read `${CLAUDE_PLUGIN_ROOT}/_memory/analytics/usage.json`
- Project: Read `${CLAUDE_PLUGIN_ROOT}/_memory/index.json`
