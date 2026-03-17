# Delegation

Delegate automatically when delegation score >= 3.

## Score Calculation

| Factor | Points |
|--------|--------|
| Scope > 2 files | +2 |
| Bulk operation | +2 |
| Research/learn | +2 |
| Code review | +2 |
| Exploration/search | +3 |
| Independent task | +2 |
| Critical keywords (production, deploy, password, secret) | -10 |
| User wants to see ("show me", "explain") | -5 |

## Model Selection

| Complexity | Model | Use for |
|-----------|-------|---------|
| 1-2 | Haiku | File search, grep, simple lookups |
| 3-6 | Sonnet | Standard tasks, code review, debugging |
| 7+ | Don't delegate | Handle yourself (needs deep reasoning) |

## Always delegate (no score needed)

| Task | Agent type | Model |
|------|-----------|-------|
| Exploration/search | Explore | Haiku |
| Codebase questions | Explore | Haiku |

## Never delegate

- Critical keywords: production, deploy, payment, password, secret
- Destructive operations: delete all, drop database, rm -rf
- User explicitly wants to see the process
