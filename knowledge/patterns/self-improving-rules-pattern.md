---
title: "Self-Improving Rules Pattern"
type: pattern
domain: [self, improving, rules]
created: 2026-03-02
confidence: 80%
source: "we-promise/sure (.cursor/rules/self_improve.mdc)"
---

# Self-Improving Rules Pattern

**Source**: we-promise/sure (.cursor/rules/self_improve.mdc)
**Typ**: Pattern
**Relevanz**: MITTEL - Automatische Evolution des Rule-Systems
**Erstellt**: 2025-12-22

---

## Problem

Rules werden einmal geschrieben und veralten:
- Neue Patterns entstehen, werden aber nicht dokumentiert
- Wiederkehrende Fehler führen zu repetitivem Feedback
- Code-Reviews enthalten immer die gleichen Kommentare
- Rules bleiben statisch obwohl sich Best Practices ändern

---

## Lösung: Self-Improving Rules

### Kern-Prinzip

> "Wenn ein Pattern 3+ Mal in Code auftaucht, sollte es eine Rule werden."

### Trigger für neue Rules

| Trigger | Beschreibung | Beispiel |
|---------|--------------|----------|
| **3+ Occurrences** | Pattern erscheint in 3+ Dateien | `cn()` Utility in allen Components |
| **Recurring Feedback** | Gleiche Code-Review Kommentare | "Fehlt Error Handling" |
| **Preventable Errors** | Fehler der hätte vermieden werden können | Import-Reihenfolge Bug |
| **New Tools** | Neue Library konsistent genutzt | shadcn/ui Components |
| **Refactoring Complete** | Nach größerem Refactoring | Neues State Management |

### Rule Evolution Workflow

```
┌─────────────────────────────────────────────────────┐
│                  Code Review / Usage                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Pattern erkannt?   │
              │  (3+ Occurrences)   │
              └─────────────────────┘
                    │         │
                   JA        NEIN
                    │         │
                    ▼         └──→ Weiter
         ┌─────────────────────┐
         │   Existiert Rule?   │
         └─────────────────────┘
               │         │
              JA        NEIN
               │         │
               ▼         ▼
    ┌──────────────┐  ┌──────────────┐
    │  Rule Update │  │ Neue Rule    │
    │  (Ergänzen)  │  │  erstellen   │
    └──────────────┘  └──────────────┘
                         │
                         ▼
         ┌─────────────────────────────┐
         │  Rule mit echten Beispielen │
         │  aus dem aktuellen Code     │
         └─────────────────────────────┘
```

---

## Qualitätsstandards für Rules

### DO

1. **Actionable sein**
   ```markdown
   # Schlecht
   "Code sollte gut strukturiert sein"

   # Gut
   "Nutze ContextBuilder für alle LLM-Calls. Beispiel: siehe orchestrator.py:45"
   ```

2. **Echte Code-Beispiele**
   ```markdown
   # Schlecht
   "Verwende TypeScript Generics"

   # Gut
   "Definiere Props mit Generics:
    ```typescript
    // Aus src/components/DataTable.tsx:12
    interface Props<T extends BaseItem> {
      items: T[]
      renderItem: (item: T) => ReactNode
    }
    ```"
   ```

3. **Cross-References**
   ```markdown
   # Gut
   "Für Error Handling siehe auch:
    - compact-errors-pattern.md
    - experience-suggest.md (Error-Matching)"
   ```

4. **Scope definieren**
   ```yaml
   ---
   paths: src/components/**/*.tsx
   alwaysApply: false
   ---
   ```

### DON'T

1. **Theoretische Rules** ohne Praxis-Bezug
2. **Veraltete Beispiele** aus gelöschtem Code
3. **Zu breite Rules** die alles abdecken wollen
4. **Duplikate** von existierenden Rules

---

## Implementation

### Monitoring (Mental Model)

Bei Code-Arbeit beachten:

```
"Habe ich das schon 3x gemacht?"
  → JA: Rule erstellen/erweitern
  → NEIN: Weitermachen

"Gab es dazu schon mal Review-Feedback?"
  → JA: Rule erstellen
  → NEIN: Notieren für später
```

### Rule-Erstellung

```markdown
# .claude/rules/example-rule.md

---
paths: src/**/*.ts  # Optional: Scope begrenzen
---

# [Rule Name]

**Trigger**: [Wann gilt diese Rule?]

## Pattern

[Was ist das Pattern?]

## Beispiel (aus Code)

```typescript
// Aus src/example.ts:25
[Echter Code]
```

## Anti-Pattern

```typescript
// NICHT so:
[Falscher Code]
```

## Related

- [Andere Rule](andere-rule.md)
```

### Obsolete Rules entfernen

Nach Major Refactors:
1. Rules durchgehen
2. Prüfen: Ist das Pattern noch aktuell?
3. Veraltete Rules archivieren oder löschen

---

## Beispiel: Rule-Evolution

### Stufe 1: Pattern bemerkt

```
Session 1: cn() Utility für Tailwind Classes genutzt
Session 2: cn() wieder genutzt
Session 3: cn() wieder genutzt, neuer Dev fragt "was ist cn()?"
```

### Stufe 2: Rule erstellt

```markdown
# .claude/rules/tailwind-cn-utility.md

**Trigger**: Bei Tailwind Class-Kombinationen

## Pattern

Nutze `cn()` für conditional Tailwind Classes:

```typescript
// Aus dashboard/src/components/Button.tsx:15
import { cn } from '@/lib/utils'

<button className={cn(
  "px-4 py-2 rounded",
  variant === 'primary' && "bg-blue-500",
  disabled && "opacity-50"
)}>
```

## Anti-Pattern

```typescript
// NICHT Template Strings:
className={`px-4 py-2 ${variant === 'primary' ? 'bg-blue-500' : ''}`}
```
```

### Stufe 3: Rule erweitert (später)

```markdown
## Ergänzung: cva() für Varianten

Bei Components mit vielen Varianten, nutze `cva()`:

```typescript
// Aus dashboard/src/components/Badge.tsx:8
const badgeVariants = cva("rounded-full px-2", {
  variants: {
    color: {
      green: "bg-green-100 text-green-800",
      red: "bg-red-100 text-red-800"
    }
  }
})
```
```

---

## Metriken für Self-Improvement

Tracke mental:

| Metrik | Ziel |
|--------|------|
| Rules pro Monat erstellt | 1-3 |
| Rules pro Monat aktualisiert | 2-5 |
| Rules pro Quartal archiviert | 0-2 |
| Review-Kommentare reduziert | -20% |

---

## Multi-AI Tool Support (Bonus)

Verschiedene AI-Tools bevorzugen verschiedene Formate:

| Tool | Format | Location |
|------|--------|----------|
| Claude Code | `.md` mit YAML Frontmatter | `.claude/rules/` |
| Cursor | `.mdc` mit YAML Frontmatter | `.cursor/rules/` |
| Gemini | `config.yaml` | `.gemini/` |
| Junie | Konsolidierte `.md` | `.junie/guidelines.md` |

**Tipp**: Core Rules in einem Format, dann bei Bedarf konvertieren.

---

## Related

- [Interview Before Implement Pattern](interview-before-implement-pattern.md)
- [Progressive Disclosure Pattern](progressive-disclosure-pattern.md)
