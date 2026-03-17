---
title: "Delegation-Request Pattern"
type: pattern
domain: [delegation, request]
created: 2026-03-02
confidence: 80%
---

# Delegation-Request Pattern

**Typ**: Coordination Pattern
**Kontext**: Agent Swarm, Multi-Layer Delegation

---

## Problem

Sub-Agents (Layer 2) haben keinen Zugriff auf das Task Tool. Sie können keine weiteren Agents spawnen oder Tasks mit Dependencies erstellen.

**Limitation**: Layer 2 → Layer 3 Delegation ist technisch nicht möglich.

---

## Lösung

Sub-Agent gibt einen strukturierten **Delegation-Request** zurück. Layer 1 (Orchestrator) interpretiert diesen und führt die empfohlenen Delegations aus.

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 1 (Orchestrator)               │
│                                                         │
│  Empfängt Request → Validiert → Erstellt Tasks → Führt │
│  aus → Sammelt Ergebnisse → Gibt zurück an User        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ Delegation-Request (JSON)
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    LAYER 2 (Sub-Agent)                  │
│                                                         │
│  Analysiert Task → Erkennt Komplexität → Empfiehlt     │
│  weitere Agents via Delegation-Request                  │
└─────────────────────────────────────────────────────────┘
```

---

## Wann nutzen?

Sub-Agent sollte Delegation-Request zurückgeben wenn:

| Situation | Indikator |
|-----------|-----------|
| **Task zu groß** | Würde > 50% Context verbrauchen |
| **Spezialisierung nötig** | Verschiedene Expertise-Bereiche |
| **Parallelisierbar** | Unabhängige Teilaufgaben erkannt |
| **Dependencies** | Reihenfolge zwischen Teilaufgaben |

---

## JSON Schema

```json
{
  "delegation_request": true,
  "reason": "Kurze Begründung für die Empfehlung",
  "recommended_tasks": [
    {
      "subject": "Prägnante Task-Beschreibung",
      "description": "Detaillierte Beschreibung (optional)",
      "model": "haiku | sonnet",
      "agent": "Explore | debugger | general-purpose | Plan",
      "traits": ["expertise", "personality", "approach"],
      "blockedBy": ["Subject eines anderen Tasks"],
      "expected_outcome": "Was soll der Task liefern"
    }
  ],
  "coordination_notes": "Optionale Hinweise für Layer 1"
}
```

### Felder

| Feld | Required | Beschreibung |
|------|----------|--------------|
| `delegation_request` | ✅ | Muss `true` sein |
| `reason` | ✅ | Warum Delegation sinnvoll ist |
| `recommended_tasks` | ✅ | Array von Task-Empfehlungen |
| `subject` | ✅ | Kurzer Task-Titel |
| `model` | ✅ | `haiku` oder `sonnet` |
| `agent` | ✅ | Agent-Typ oder `general-purpose` |
| `traits` | ❌ | Für general-purpose Agents |
| `blockedBy` | ❌ | Dependencies (Task-Subjects) |
| `description` | ❌ | Erweiterte Beschreibung |
| `expected_outcome` | ❌ | Erwartetes Ergebnis |
| `coordination_notes` | ❌ | Hinweise für Orchestrator |

---

## Layer 1 Execution Flow

```
Delegation-Request empfangen
         │
         ▼
┌────────────────────────────────┐
│ 1. VALIDIERUNG                 │
│                                │
│ • Alle required Felder da?     │
│ • Models valide (haiku/sonnet)?│
│ • Agents existieren?           │
│ • blockedBy referenziert       │
│   existierende Tasks?          │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ 2. TASK CREATION               │
│                                │
│ FOR each recommended_task:     │
│   TaskCreate(subject, desc)    │
│   → Speichere Task-ID          │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ 3. DEPENDENCIES SETZEN         │
│                                │
│ FOR each task with blockedBy:  │
│   TaskUpdate(id, addBlockedBy) │
│   → Mapping: subject → ID      │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ 4. PARALLEL EXECUTION          │
│                                │
│ Gruppiere Tasks:               │
│ • Gruppe 0: Keine blockedBy    │
│ • Gruppe 1: blockedBy Gruppe 0 │
│ • Gruppe 2: blockedBy Gruppe 1 │
│                                │
│ Führe Gruppen sequentiell aus, │
│ Tasks innerhalb parallel       │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ 5. RESULT AGGREGATION          │
│                                │
│ Sammle alle Task-Ergebnisse    │
│ Formatiere für User            │
└────────────────────────────────┘
```

---

## Beispiele

### Beispiel 1: Refactoring mit Dependencies

Sub-Agent analysiert großes Refactoring:

```json
{
  "delegation_request": true,
  "reason": "Refactoring betrifft 3 Module mit klaren Dependencies",
  "recommended_tasks": [
    {
      "subject": "Types refactoren",
      "model": "sonnet",
      "agent": "general-purpose",
      "traits": ["engineer", "precise"],
      "blockedBy": [],
      "expected_outcome": "Neue Type-Definitionen"
    },
    {
      "subject": "Auth-Service refactoren",
      "model": "sonnet",
      "agent": "general-purpose",
      "traits": ["engineer", "iterative"],
      "blockedBy": ["Types refactoren"],
      "expected_outcome": "Aktualisierter Auth-Service"
    },
    {
      "subject": "API-Layer refactoren",
      "model": "sonnet",
      "agent": "general-purpose",
      "traits": ["engineer", "iterative"],
      "blockedBy": ["Types refactoren"],
      "expected_outcome": "Aktualisierte API-Endpoints"
    },
    {
      "subject": "Integration Tests",
      "model": "haiku",
      "agent": "general-purpose",
      "blockedBy": ["Auth-Service refactoren", "API-Layer refactoren"],
      "expected_outcome": "Passing Tests"
    }
  ],
  "coordination_notes": "Auth und API können parallel nach Types"
}
```

**Execution**:
1. Types refactoren (keine Deps)
2. Auth + API parallel (beide warten auf Types)
3. Integration Tests (wartet auf Auth + API)

### Beispiel 2: Research mit Parallelisierung

```json
{
  "delegation_request": true,
  "reason": "3 unabhängige Research-Bereiche",
  "recommended_tasks": [
    {
      "subject": "API Documentation recherchieren",
      "model": "haiku",
      "agent": "Explore",
      "blockedBy": []
    },
    {
      "subject": "Existing Patterns analysieren",
      "model": "haiku",
      "agent": "Explore",
      "blockedBy": []
    },
    {
      "subject": "Best Practices sammeln",
      "model": "haiku",
      "agent": "general-purpose",
      "traits": ["researcher", "thorough"],
      "blockedBy": []
    },
    {
      "subject": "Synthese erstellen",
      "model": "sonnet",
      "agent": "general-purpose",
      "traits": ["analyst", "systematic"],
      "blockedBy": [
        "API Documentation recherchieren",
        "Existing Patterns analysieren",
        "Best Practices sammeln"
      ]
    }
  ]
}
```

**Execution**:
1. Alle 3 Research-Tasks parallel
2. Synthese nach Abschluss aller Research-Tasks

---

## Anti-Patterns

| Don't | Why |
|-------|-----|
| Zu viele Tasks (>5) | Koordinations-Overhead |
| Künstliche Dependencies | Verliert Parallelisierung |
| Triviale Tasks delegieren | Overhead > Nutzen |
| Unklare Subjects | Layer 1 kann nicht validieren |

---

## Related

- [Parallel Agent Dispatch Pattern](parallel-agent-dispatch-pattern.md)
- [Task Decomposition Pipeline](task-decomposition-pipeline.md)
- [Recursive Research Pattern](recursive-research-pattern.md)
