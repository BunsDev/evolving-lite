---
title: ReAct Pattern
type: pattern
domain: [react]
created: 2026-03-02
confidence: 90%
source: "Yao et al. (2022), \"ReAct: Synergizing Reasoning and Acting in Language Models\""
---

# ReAct Pattern

**Typ**: Agent Pattern
**Confidence**: 90%
**Source**: Yao et al. (2022), "ReAct: Synergizing Reasoning and Acting in Language Models"
**Priority**: P1 - High

---

## Problem

LLMs generieren oft Antworten ohne systematische Untersuchung. Bei Debugging führt das zu:
- Vorschnellen Fixes ohne Root-Cause-Verständnis
- Übersehenen Edge Cases
- Ineffizienten Trial-and-Error-Schleifen

## Solution

Strukturierter Reason-Act-Observe Loop der Hypothesen systematisch testet:

```
User Problem
    │
    ▼
┌─────────────────┐
│    REASON       │◄──────────────┐
│ Analysiere      │               │
│ Bilde Hypothese │               │
└────────┬────────┘               │
         │                        │
         ▼                        │
┌─────────────────┐               │
│     ACT         │               │
│ Führe Test aus  │               │
│ Sammle Daten    │               │
└────────┬────────┘               │
         │                        │
         ▼                        │
┌─────────────────┐               │
│   OBSERVE       │───────────────┘
│ Dokumentiere    │    (Loop bis gelöst)
│ Ergebnisse      │
│ Update Wissen   │
└────────┬────────┘
         │
         ▼
   Problem gelöst
   oder eskalieren
```

## Implementation

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class HypothesisStatus(str, Enum):
    UNTESTED = "untested"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    PARTIAL = "partial"

class Hypothesis(BaseModel):
    id: str = Field(description="Unique hypothesis ID")
    statement: str = Field(description="What we think might be true")
    probability: float = Field(ge=0, le=1, description="Initial likelihood")
    test_action: str = Field(description="How to test this hypothesis")
    status: HypothesisStatus = HypothesisStatus.UNTESTED

class Observation(BaseModel):
    action_taken: str = Field(description="What was done")
    result: str = Field(description="What happened")
    supports_hypothesis: Optional[bool] = Field(description="Does this support or refute?")
    new_information: list[str] = Field(default_factory=list)

class ReActState(BaseModel):
    problem: str
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    current_hypothesis: Optional[str] = None
    iteration: int = 0
    max_iterations: int = 10
    solved: bool = False
    solution: Optional[str] = None
```

### LangGraph Flow

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class ReActGraphState(TypedDict):
    problem: str
    hypotheses: list[dict]
    observations: list[dict]
    current_hypothesis_id: str
    iteration: int
    max_iterations: int
    solved: bool
    solution: str

def reason_node(state: ReActGraphState) -> dict:
    """Generate or refine hypotheses based on current knowledge."""

    prompt = f"""
    Problem: {state['problem']}

    Previous observations:
    {format_observations(state['observations'])}

    Current hypotheses:
    {format_hypotheses(state['hypotheses'])}

    Based on the evidence so far:
    1. Which hypothesis should we test next?
    2. If all are tested, generate new hypotheses
    3. Prioritize by probability and testability

    Output the next hypothesis to test with a specific test action.
    """

    result = llm.with_structured_output(ReasoningOutput).invoke(prompt)

    return {
        "hypotheses": update_hypotheses(state['hypotheses'], result),
        "current_hypothesis_id": result.next_hypothesis_id
    }

def act_node(state: ReActGraphState) -> dict:
    """Execute the test action for current hypothesis."""

    hypothesis = get_hypothesis(state['hypotheses'], state['current_hypothesis_id'])

    # Execute the test (tool use, code execution, file read, etc.)
    action_result = execute_test_action(hypothesis.test_action)

    return {
        "observations": state['observations'] + [{
            "action_taken": hypothesis.test_action,
            "result": action_result,
            "hypothesis_id": hypothesis.id
        }],
        "iteration": state['iteration'] + 1
    }

def observe_node(state: ReActGraphState) -> dict:
    """Analyze results and update hypothesis status."""

    latest_observation = state['observations'][-1]
    hypothesis = get_hypothesis(state['hypotheses'], latest_observation['hypothesis_id'])

    prompt = f"""
    Hypothesis: {hypothesis.statement}
    Test action: {latest_observation['action_taken']}
    Result: {latest_observation['result']}

    Analyze:
    1. Does this confirm, reject, or partially support the hypothesis?
    2. What new information did we learn?
    3. Is the problem solved?
    """

    analysis = llm.with_structured_output(ObservationAnalysis).invoke(prompt)

    updated_hypotheses = update_hypothesis_status(
        state['hypotheses'],
        hypothesis.id,
        analysis.status
    )

    return {
        "hypotheses": updated_hypotheses,
        "solved": analysis.problem_solved,
        "solution": analysis.solution if analysis.problem_solved else None
    }

def should_continue(state: ReActGraphState) -> str:
    if state['solved']:
        return "solved"
    if state['iteration'] >= state['max_iterations']:
        return "max_iterations"
    if all_hypotheses_exhausted(state['hypotheses']):
        return "need_new_hypotheses"
    return "continue"

# Build Graph
graph = StateGraph(ReActGraphState)
graph.add_node("reason", reason_node)
graph.add_node("act", act_node)
graph.add_node("observe", observe_node)
graph.add_node("summarize", summarize_node)

graph.add_edge(START, "reason")
graph.add_edge("reason", "act")
graph.add_edge("act", "observe")
graph.add_conditional_edges(
    "observe",
    should_continue,
    {
        "continue": "reason",
        "solved": "summarize",
        "max_iterations": "summarize",
        "need_new_hypotheses": "reason"
    }
)
graph.add_edge("summarize", END)

react_chain = graph.compile()
```

## Example: Debugging Integration

### Systematic Debug Function

```python
def debug_with_react(error_description: str, context: dict) -> DebugResult:
    """Use ReAct pattern for systematic debugging."""

    initial_state = {
        "problem": error_description,
        "hypotheses": generate_initial_hypotheses(error_description, context),
        "observations": [],
        "iteration": 0,
        "max_iterations": 10,
        "solved": False
    }

    result = react_chain.invoke(initial_state)

    return DebugResult(
        solved=result['solved'],
        solution=result['solution'],
        hypotheses_tested=len([h for h in result['hypotheses'] if h['status'] != 'untested']),
        key_observations=extract_key_observations(result['observations'])
    )
```

### Hypothesis Templates

```python
HYPOTHESIS_TEMPLATES = {
    "type_error": [
        "Variable {var} has unexpected type",
        "Function {func} receives wrong argument type",
        "Type coercion fails at {location}"
    ],
    "null_reference": [
        "Object {obj} is null/undefined",
        "Optional value not properly checked",
        "Async operation not awaited"
    ],
    "logic_error": [
        "Condition {cond} evaluates incorrectly",
        "Loop boundary off by one",
        "State mutation in wrong order"
    ],
    "integration": [
        "API endpoint returns unexpected format",
        "Environment variable missing/wrong",
        "Version mismatch between dependencies"
    ]
}
```

## Trace Format

ReAct produces readable traces:

```
[Iteration 1]
REASON: Error occurs on line 42. Hypothesis: The API response is null when user not found.
        Test: Add console.log before line 42 to check response value.

ACT: Added logging statement. Running test...

OBSERVE: Log shows response is {status: 404, data: null}. Hypothesis CONFIRMED.
         New info: API returns 404 with null data instead of throwing.

[Iteration 2]
REASON: Need to handle 404 case. Hypothesis: Adding null check before access will fix.
        Test: Add if (response.data) check.

ACT: Added null check. Running test...

OBSERVE: Error resolved. Hypothesis CONFIRMED. Problem SOLVED.

SOLUTION: Added null check for API response before accessing data property.
          Root cause: API returns null data on 404 instead of throwing error.
```

---

## Trade-offs

| Pro | Contra |
|-----|--------|
| Systematisch statt raten | 1.5-2x Token-Verbrauch |
| Nachvollziehbarer Trace | Nicht für kreative Tasks |
| Vermeidet Rabbit Holes | Braucht klares Problem |
| Findet Root Cause | Overhead bei trivialen Bugs |
| Dokumentiert Lernprozess | Kann bei komplexen Systemen langsam sein |

## When to Use

- **JA**: Bugs finden, Fehler analysieren, Code explorieren, Root-Cause-Analyse
- **NEIN**: Kreative Tasks, Output-Verbesserung, bekannte Lösungen anwenden

## Configuration

```json
{
  "max_iterations": 10,
  "hypothesis_per_round": 3,
  "confidence_threshold": 0.8,
  "auto_tool_execution": true,
  "trace_verbosity": "detailed"
}
```

## Related Patterns

- [Reflection Pattern](reflection-pattern.md) - Für Output-Verbesserung statt Debugging
- [Task Decomposition Pipeline](task-decomposition-pipeline.md) - Für komplexe mehrstufige Aufgaben
