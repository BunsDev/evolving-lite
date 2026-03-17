---
title: "Interview-Before-Implement Pattern"
type: pattern
domain: [planning, validation]
created: 2026-03-02
confidence: 80%
source: "robzolkos gist"
---

# Interview-Before-Implement Pattern

**Source**: robzolkos gist
**Category**: planning, validation
**Tags**: interview, plan-validation, requirements-gathering

---

## Problem

Pläne werden oft ohne tiefgehende Prüfung implementiert. Wichtige Details, Edge Cases und Tradeoffs werden erst während der Implementierung entdeckt - wenn Änderungen teuer sind.

## Solution

**Strukturiertes Interview VOR Implementation:**

```
Plan erstellt
    ↓
Interview-Session
    ↓
Probing Questions zu:
- Technical Implementation
- UI/UX Details
- Risks & Concerns
- Tradeoffs
- Edge Cases
- Dependencies
    ↓
Plan aktualisiert mit Erkenntnissen
    ↓
Implementation mit klarerem Scope
```

## Key Principles

1. **Non-obvious Questions**: Keine oberflächlichen Fragen, sondern probing
2. **Multi-dimensional**: Tech, UX, Risk, Tradeoffs - alles abdecken
3. **Iterativ**: Weiterfragen bis erschöpft
4. **Dokumentiert**: Erkenntnisse zurück in Plan

## Implementation

### Als Command

```markdown
---
description: Interview me about the plan
model: opus
---

Read plan file and interview about:
- Technical implementation
- UI & UX
- Concerns & tradeoffs
- Edge cases

Continue until complete, then update plan.
```

### Als Workflow

1. `/interview-plan knowledge/plans/my-plan.md`
2. Beantworte alle Fragen
3. Plan wird mit Erkenntnissen aktualisiert
4. Dann erst implementieren

## Wann nutzen?

| Situation | Empfehlung |
|-----------|------------|
| Neue Feature > 1 Tag Arbeit | ✅ Interview |
| Architektur-Entscheidung | ✅ Interview |
| Quick Fix | ❌ Overkill |
| Gut verstandenes Pattern | ❌ Nicht nötig |

## Anti-Pattern

- Oberflächliche Fragen stellen
- Interview abbrechen wenn "genug"
- Erkenntnisse nicht dokumentieren
- Trotzdem ohne Plan implementieren

## Related

- [Tree of Thoughts Pattern](tree-of-thoughts-pattern.md) - Systematic option exploration
- [Task Decomposition Pipeline](task-decomposition-pipeline.md) - Breaking complex tasks into phases

---

**Integrated**: 2025-12-30
