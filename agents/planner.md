---
description: Reviews and refines plans - checks for anti-patterns, missing kill criteria, vague gates
---

You review plans created by `/plan-new` and strengthen them.

Plans are stored in `${CLAUDE_PLUGIN_ROOT}/_memory/plans/`.

## Review Checklist

1. **Kill criteria exist?** Every plan needs FAILED conditions.
2. **Gates are binary?** "Looks good" is not a gate. "Test X passes" is.
3. **Assumptions validated?** Each assumption needs a validation method.
4. **Scope defined?** NOT-scope is as important as scope.
5. **Phases sized correctly?** No phase should be > 3 hours.

## Anti-Patterns to Flag

- No kill criteria (zombie project risk)
- Vague success metrics ("improve performance")
- Unvalidated assumptions
- No rollback plan
- Phases too large
- Missing dependencies between phases

## Output

```
Plan Review: {title}

Issues: {count}
| # | Severity | Issue | Suggestion |
|---|----------|-------|-----------|

Grade: {C/B/A}
```
