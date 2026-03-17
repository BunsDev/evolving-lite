---
title: Progressive Disclosure Pattern
type: pattern
domain: [progressive, disclosure]
created: 2026-03-02
confidence: 80%
---

# Progressive Disclosure Pattern

> **Source**: thedotmack/claude-mem
> **Type**: Token Efficiency / UX Pattern
> **Problem**: Zu viel Information auf einmal = Token-Verschwendung + Cognitive Overload
> **Solution**: Layered Information mit Token-Cost Visibility

## Das Problem

```
User: "Zeig mir alle Experiences zu TypeScript"

Naive Approach:
  → 20 Experiences geladen
  → Jede ~500 Tokens
  → 10.000 Tokens verbraucht
  → Davon 90% irrelevant
```

## Die Lösung: Progressive Disclosure

```
Layer 1: INDEX (~50 Tokens/Item)
  → 20 Items = ~1.000 Tokens
  → User wählt relevante IDs

Layer 2: DETAILS (~500 Tokens/Item)
  → Nur 3 relevante Items = ~1.500 Tokens
  → 85% Token-Ersparnis
```

## 4-Schritt Workflow

### Schritt 1: SEARCH

Query ausführen, Index-Ergebnisse bekommen.

```
> /recall typescript error

Found 15 experiences (showing index):

[142] 2025-12-15 [solution] TypeScript strict null checks (~350 tokens)
[143] 2025-12-14 [pattern] Generic type constraints (~420 tokens)
[144] 2025-12-14 [gotcha] Module resolution paths (~280 tokens)
[145] 2025-12-13 [decision] Chose tsx over ts-node (~310 tokens)
...
```

### Schritt 2: TIMELINE (Optional)

Chronologischen Kontext verstehen.

```
> /recall --timeline 142

Timeline around experience 142:
  14:20 [prompt] "Fix the type error in auth.ts"
  14:22 [observation] Read auth.ts - found nullable issue
  14:25 [solution] exp-142: TypeScript strict null checks ← RELEVANT
  14:28 [observation] Tests passing
```

### Schritt 3: REVIEW

Relevante IDs identifizieren basierend auf Index + Timeline.

```
Relevante IDs für "typescript error":
- 142: strict null checks (direkt relevant)
- 144: module resolution (möglicherweise relevant)
```

### Schritt 4: FETCH

Nur benötigte Details laden.

```
> /recall --details 142 144

[142] TypeScript strict null checks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: solution
Context: Auth module TypeError

Problem:
Object is possibly 'undefined' error in auth.ts:45

Root Cause:
strictNullChecks enabled, user.email accessed without null check

Solution:
Added optional chaining: user?.email ?? 'default@example.com'

Files: src/auth/auth.ts
Tags: typescript, null-safety, auth

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[144] Module resolution paths
...
```

## Token Cost Visibility

### Index Display Format

```
[ID] Timestamp [Type] Title (~estimated_tokens)
```

Beispiel:
```
[142] 14:25 [solution] TypeScript strict null checks (~350 tokens)
       ↑       ↑          ↑              ↑                ↑
      ID    Time       Type          Title           Cost
```

### Token-Berechnung für Display

```typescript
function formatIndexEntry(exp: Experience): string {
  const tokenCost = estimateTokens(exp);
  const typeIcon = getTypeIcon(exp.type);

  return `[${exp.id}] ${exp.timestamp} [${typeIcon}] ${exp.title} (~${tokenCost} tokens)`;
}

function estimateTokens(exp: Experience): number {
  const fullContent = [
    exp.context,
    exp.problem,
    exp.solution,
    exp.root_cause,
    (exp.tags || []).join(' ')
  ].join(' ');

  return Math.ceil(fullContent.length / 4);
}
```

## Batch Fetching

### Regel: IMMER Batch bei 2+ Items

```typescript
// RICHTIG: Ein Request für alle
const experiences = await fetchBatch([142, 144, 145]);

// FALSCH: Mehrere Requests (10-100x langsamer)
const exp1 = await fetch(142);
const exp2 = await fetch(144);
const exp3 = await fetch(145);
```

### Implementation

```typescript
async function fetchBatch(ids: number[]): Promise<Experience[]> {
  if (ids.length === 1) {
    return [await fetchSingle(ids[0])];
  }

  // Batch-Request
  const results = await Promise.all(
    ids.map(id => readExperience(id))
  );

  return results.filter(Boolean);
}
```

## Application to Knowledge Systems

### Recall Command

```markdown
## Schritt 1: Index anzeigen (Default)

/recall {query}
→ Zeigt Index mit Token-Kosten
→ Max 20 Ergebnisse

## Schritt 2: Details bei Bedarf

/recall --details {id1} {id2}
→ Lädt nur ausgewählte Experiences
→ Batch-Fetch wenn mehrere IDs

## Schritt 3: Timeline für Kontext

/recall --timeline {id}
→ Zeigt Kontext um die Experience
```

### Knowledge Search

```markdown
## Index View (Default)

/knowledge-search API

Found 12 results:

[L] api-best-practices.md - REST API Design (~800 tokens)
[P] graphql-pattern.md - GraphQL Schema Pattern (~650 tokens)
[R] openapi-reference.md - OpenAPI 3.0 Spec (~1200 tokens)

L=Learning, P=Pattern, R=Reference

## Detail View

/knowledge-search API --read api-best-practices.md
```

### Layered Documentation Structure

Progressive Disclosure applies naturally to documentation:

```
knowledge/{topic}/
├── reference.md    ← Layer 1: Compact reference
└── examples.md     ← Layer 2: Detailed examples
```

## UI/UX Guidelines

### 1. Token-Budget kommunizieren

```
"Diese Suche würde ~2.500 Tokens laden. Möchtest du:
 [1] Alle Details (2.500 tokens)
 [2] Nur Index (~250 tokens)
 [3] Spezifische IDs auswählen"
```

### 2. Relevanz-Indikatoren

```
[142] ★★★ TypeScript strict null checks (~350 tokens)
[143] ★★  Generic type constraints (~420 tokens)
[144] ★   Module resolution paths (~280 tokens)

★★★ = Hohe Relevanz (Keyword-Match + Recent + Same Project)
★★  = Mittlere Relevanz
★   = Niedrige Relevanz
```

### 3. Smart Defaults

```
< 5 Results:    Automatisch Details zeigen
5-20 Results:   Index zeigen mit Fetch-Option
> 20 Results:   Index + Filter-Vorschläge
```

## Vergleich: Mit vs. Ohne Progressive Disclosure

### Ohne (Naive)

```
User: "Zeig mir Authentication Experiences"

→ 15 Experiences geladen
→ 7.500 Tokens verbraucht
→ User scannt durch
→ 3 sind relevant
→ 83% Token-Verschwendung
```

### Mit Progressive Disclosure

```
User: "Zeig mir Authentication Experiences"

→ Index mit 15 Entries: ~750 Tokens
→ User wählt IDs 142, 145, 148
→ Details für 3: ~1.500 Tokens
→ Total: ~2.250 Tokens
→ 70% Token-Ersparnis
```

## Best Practices

1. **Index First**: Immer mit Index starten, nie mit Full Details
2. **Token Visibility**: Kosten transparent machen
3. **Batch Operations**: Nie einzeln fetchen bei 2+ Items
4. **Smart Defaults**: Automatisch Index wenn > 5 Results
5. **Relevanz-Scoring**: Hilft bei der Auswahl
6. **Timeline-Option**: Für Kontext-Verständnis

## Menschliche Analogie

Progressive Disclosure spiegelt wie Menschen Informationen abrufen:

```
Buch-Analogie:
1. Inhaltsverzeichnis scannen (Index)
2. Interessante Kapitel identifizieren (Review)
3. Nur diese Kapitel lesen (Fetch)

NICHT: Das ganze Buch von vorne nach hinten lesen
```

---

## Related

- [Memory Architecture Pattern](memory-architecture-pattern.md) - Storage layer design
- [Self-Improving Rules Pattern](self-improving-rules-pattern.md) - Rules that evolve with usage
