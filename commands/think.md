---
description: Apply structured thinking frameworks to a problem
argument-hint: [Problem or decision to analyze]
---

Apply structured thinking frameworks to break down complex problems.

## Input: $ARGUMENTS

If empty: "What problem or decision should I think through?"

## Available Frameworks

### 80/20 (Pareto)
What 20% of the effort delivers 80% of the value?

### First Principles
Strip away assumptions. What is fundamentally true? Build up from there.

### Inversion
Instead of "how to succeed", ask "how could this fail?" Then avoid those failures.

### SWOT
Strengths, Weaknesses, Opportunities, Threats - in context of the specific problem.

### Pre-Mortem
Imagine it's 6 months later and this failed. What went wrong? Work backwards.

### Decision Matrix
List options, list criteria, score each option against each criterion.

## Process

1. Auto-detect the best framework (or let user choose)
2. Apply the framework step by step
3. Present the insight clearly
4. End with a concrete recommendation

## Output

```
Framework: {which one}
Key insight: {the one thing that changes your thinking}
Recommendation: {what to do}
```
