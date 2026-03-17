---
title: Parallel Agent Dispatch Pattern
type: pattern
domain: [parallel, agent, dispatch]
created: 2026-03-02
confidence: 80%
source: obra/superpowers
---

# Parallel Agent Dispatch Pattern

**Source**: obra/superpowers
**Extracted**: 2025-12-28
**Type**: Multi-Agent Orchestration

---

## Concept

When facing multiple independent problems, dispatch specialized agents in parallel rather than solving sequentially.

```
Sequential (slow):
  Problem A → Solve → Problem B → Solve → Problem C → Solve
  Total time: 3x

Parallel (fast):
  Problem A → Agent A ─┐
  Problem B → Agent B ─┼→ Integrate Results
  Problem C → Agent C ─┘
  Total time: 1x + integration
```

---

## The Pattern

### Step 1: Identify Independent Domains

Problems are independent when:
- No shared state during execution
- No dependency on each other's output
- Can be verified separately

**Examples:**
- Different feature modules
- Separate test suites
- Independent refactoring areas

### Step 2: Create Focused Agent Tasks

For each domain, define:

```markdown
## Agent Task: {Domain Name}

**Scope**: Only files in {path}
**Goal**: {Specific outcome}
**Constraints**:
- Do not modify files outside scope
- {Other boundaries}

**Expected Output**:
- {Deliverable 1}
- {Deliverable 2}
```

### Step 3: Dispatch in Parallel

Use Task tool with multiple invocations in single message:

```
<task 1: Agent for Domain A>
<task 2: Agent for Domain B>
<task 3: Agent for Domain C>
```

All agents run concurrently with fresh context.

### Step 4: Review and Integrate

When all agents complete:
1. Review each agent's work
2. Check for conflicts at boundaries
3. Resolve any integration issues
4. Verify combined result

---

## When to Use

**Good candidates:**
- Multiple independent features
- Parallel test fixes
- Multi-file refactoring with clear boundaries
- Research across different domains

**Poor candidates:**
- Sequential dependencies
- Shared state modifications
- Single-file changes
- Tightly coupled components

---

## Example: Feature Implementation

```
User: "Add authentication, logging, and caching"

Orchestrator:
  1. Identify: 3 independent concerns
  2. Create tasks:
     - Auth Agent: src/auth/, middleware
     - Logging Agent: src/logging/, config
     - Cache Agent: src/cache/, redis setup
  3. Dispatch parallel
  4. Integrate: wire together in main app
```

---

## Boundaries & Conflict Resolution

### Define Clear Boundaries

```markdown
**Agent A Boundary**: src/feature-a/**
**Agent B Boundary**: src/feature-b/**
**Shared Interface**: src/types/shared.ts (read-only)
```

### If Agents Need Shared Types

1. Define interface first (before dispatch)
2. Each agent implements against interface
3. Integration verifies compatibility

---

## Decision Flowchart

```
Multiple failures/tasks?
    │
    ├─ No → Single agent handles all
    │
    └─ Yes → Are they independent?
              │
              ├─ No (related) → Single agent investigates all
              │
              └─ Yes → Can they work in parallel?
                        │
                        ├─ No (shared state) → Sequential agents
                        │
                        └─ Yes → PARALLEL DISPATCH
```

---

## Agent Prompt Structure (Best Practice)

Good agent prompts are:
1. **Focused** - One clear problem domain
2. **Self-contained** - All context needed
3. **Specific about output** - What should agent return?

```markdown
Fix the 3 failing tests in src/agents/agent-tool-abort.test.ts:

1. "should abort tool with partial output" - expects 'interrupted at'
2. "should handle mixed completed and aborted" - fast tool aborted
3. "should properly track pendingToolCount" - expects 3, gets 0

These are timing/race condition issues. Your task:

1. Read the test file and understand what each test verifies
2. Identify root cause - timing issues or actual bugs?
3. Fix by:
   - Replacing arbitrary timeouts with event-based waiting
   - Fixing bugs in abort implementation if found

Do NOT just increase timeouts - find the real issue.

Return: Summary of what you found and what you fixed.
```

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too broad: "Fix all tests" | Agent gets lost | "Fix agent-tool-abort.test.ts" |
| No context | Agent doesn't know where | Paste error messages |
| No constraints | Agent refactors everything | "Do NOT change production code" |
| Vague output | You don't know what changed | "Return summary of changes" |

---

## Real Example

**Scenario**: 6 test failures across 3 files after refactoring

**Failures**:
- agent-tool-abort.test.ts: 3 failures (timing)
- batch-completion.test.ts: 2 failures (tools not executing)
- race-conditions.test.ts: 1 failure (count = 0)

**Decision**: Independent domains - abort logic separate from batch separate from race

**Dispatch**:
```
Agent 1 → Fix agent-tool-abort.test.ts
Agent 2 → Fix batch-completion.test.ts
Agent 3 → Fix race-conditions.test.ts
```

**Results**:
- Agent 1: Replaced timeouts with event-based waiting
- Agent 2: Fixed event structure bug
- Agent 3: Added wait for async completion

**Integration**: All fixes independent, no conflicts, suite green

---

## Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| Overlapping scopes | Merge conflicts |
| Implicit dependencies | Agents block each other |
| Missing integration step | Broken combined result |
| Too many parallel agents | Coordination overhead |

---

## Related

- [Delegation-Request Pattern](delegation-request-pattern.md)
- [Task Decomposition Pipeline](task-decomposition-pipeline.md)
- [Recursive Research Pattern](recursive-research-pattern.md)

---

**Updated**: 2025-12-30 (enriched with obra/superpowers examples)
