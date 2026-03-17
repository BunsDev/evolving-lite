---
description: Structured code review with severity categorization (distinct from Claude Code's PR review)
argument-hint: [File path or "recent changes"]
---

Perform a structured code review focused on correctness, security, and quality.

## Input: $ARGUMENTS

If empty: Review recent unstaged changes (`git diff`)
If file path: Review that specific file
If "recent": Review all changes since last commit

## Review Checklist

### 1. Correctness
- Does the code do what it claims?
- Are edge cases handled?
- Are error paths tested?

### 2. Security (OWASP Top 10)
- Input validation at boundaries
- No hardcoded secrets
- SQL/command injection prevention
- XSS prevention (if web)
- Authentication/authorization checks

### 3. Quality
- Is the code readable without comments?
- Are names descriptive?
- Is there unnecessary complexity?
- Any code duplication that should be abstracted?

### 4. Performance
- Any O(n^2) or worse in hot paths?
- Unnecessary file I/O or network calls?
- Missing caching opportunities?

## Output

```markdown
## Code Review: {file or scope}

### Issues Found

| # | Severity | File:Line | Issue | Suggestion |
|---|----------|-----------|-------|-----------|
| 1 | HIGH | path:42 | ... | ... |

### Summary
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

Verdict: {APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION}
```
