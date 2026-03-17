---
title: Recursive Research Pattern
type: pattern
domain: [recursive, research]
created: 2026-03-02
confidence: 80%
---

# Recursive Research Pattern

> **Source**: Cranot/deep-research
> **Type**: Multi-Agent Research Pattern
> **Problem**: Komplexe Fragen erfordern mehrere Perspektiven und tiefe Analyse
> **Solution**: Rekursive Agent-Dekomposition mit automatischer Synthese

## Das Konzept

```
Komplexe Frage
      ↓
  Orchestrator
      ↓
┌─────┼─────┐
│     │     │
R1    R2    R3   (Researchers parallel)
│           │
├──┐     ┌──┤
S1 S2   S3 S4   (Sub-agents rekursiv)
│     │
└──┬──┘
   ↓
SYNTHESIS
```

## Core Agent DNA

Der Schlüssel zum Pattern ist eine selbst-propagierende Instruktion:

```markdown
Bevor du antwortest, IMMER fragen:
"Gibt es mehrere Perspektiven die Exploration verdienen?"

WENN JA:
  → Spawne Sub-Agents für jede Perspektive
  → Sammle alle Findings
  → Synthetisiere zu kohärentem Ergebnis

WENN NEIN:
  → Antworte direkt mit Bias zu gründlicher Untersuchung
```

Diese Instruktion wird an ALLE Sub-Agents vererbt → rekursive Tiefe entsteht automatisch.

## Multi-Model Tiering

### Modell-Konfigurationen

| Orchestrator | Researcher | Tiefe | Speed | Cost | Use Case |
|--------------|------------|-------|-------|------|----------|
| Opus | Sonnet | Tief | Langsam | $$$ | Premium Research |
| Sonnet | Sonnet | Tief | Mittel | $$ | Balanced |
| Sonnet | Haiku | Flach | Schnell | $ | Quick Answers |

### Regel: Haiku spawnt nicht

```
WICHTIG: Haiku-Researchers spawnen KEINE Sub-Researchers.
→ Für tiefe Rekursion: Mindestens Sonnet als Researcher
```

## Question Decomposition

### Atomic vs Decomposable

```
Atomic (direkt beantworten):
- "Was ist die Definition von X?"
- "Wann wurde Y erfunden?"
- Faktenfragen mit klarer Antwort

Decomposable (Sub-Agents spawnen):
- "Warum treffen intelligente Menschen schlechte Entscheidungen?"
- "Was macht gute Software-Architektur aus?"
- Fragen mit mehreren Dimensionen
```

### Decomposition Heuristiken

```typescript
function shouldDecompose(question: string): boolean {
  const signals = [
    question.includes('warum'),
    question.includes('wie'),
    question.includes('was macht'),
    question.split(' ').length > 10,
    hasMultipleDimensions(question)
  ];

  return signals.filter(Boolean).length >= 2;
}
```

## Synthesis Framework

### 6-Dimensional Analysis

| Dimension | Fokus | Fragen |
|-----------|-------|--------|
| **Technical** | Struktur & Qualität | Was sind die technischen Anforderungen? |
| **Human** | Menschen & Teams | Wie beeinflusst es die Arbeit? |
| **Business** | Wert & ROI | Welcher Business-Nutzen entsteht? |
| **Context** | Situationsabhängigkeit | Wann gilt was? |
| **Evolution** | Zeitliche Entwicklung | Wie verändert es sich? |
| **Decision** | Entscheidungsfindung | Wie wählt man? |

### Synthesis Output Format

```markdown
# Research Report: {Question}

## Methodology
- Orchestrator: {model}
- Researchers: {model}
- Sub-agent Depth: {max_depth}
- Total Agents: {count}

## Findings by Dimension

### 1. Technical & Structural
{findings}

### 2. Human & Social
{findings}

### 3. Business & Economic
{findings}

### 4. Context-Dependence
| Factor | Startup | Enterprise |
|--------|---------|------------|
| {x}    | {y}     | {z}        |

### 5. Evolution Over Time
- Phase 1: {description}
- Phase 2: {description}
- Phase 3: {description}

### 6. Decision Framework
{criteria}

## Synthesis
{integrative_conclusion}

## Meta-Principle
{one_sentence_truth}

## Practical Application
1. {question_1}
2. {question_2}
...
```

## Implementation: Bash Script Pattern

### Core Script

```bash
#!/bin/bash

MODEL="${1:-opus}"
RESEARCHER="${2:-sonnet}"
QUESTION="$3"
WEB_FLAG="${4:-}"

# Agent DNA - wird vererbt
PROMPT="Du bist ein Research Agent.

CORE INSTRUCTION:
Bevor du antwortest, frage: 'Gibt es mehrere Perspektiven?'
- JA → Spawne Sub-Agents, synthetisiere
- NEIN → Antworte direkt

TO SPAWN SUB-AGENT:
claude -p '[sub-question]' --model $RESEARCHER --allowedTools 'Bash(claude:*)'

QUESTION: $QUESTION"

# Ausführen
claude -p "$PROMPT" \
  --model "$MODEL" \
  --allowedTools "Bash(claude:*)" \
  $WEB_FLAG
```

### Sub-Agent Spawning (durch Agent selbst)

```bash
# Agent erkennt: "Diese Frage hat 3 Perspektiven"
# Agent generiert:

claude -p "Perspektive 1: Technische Sicht auf X" --model sonnet &
claude -p "Perspektive 2: Business-Sicht auf X" --model sonnet &
claude -p "Perspektive 3: User-Sicht auf X" --model sonnet &

wait  # Alle parallel, dann sammeln
```

## Process Monitoring

### Agent Tracking Script

```bash
#!/bin/bash

# Aktive Agents zählen
active=$(ps aux | grep "claude -p" | grep -v grep | wc -l)
echo "Active agents: $active"

# Agent Details
ps aux | grep "claude -p" | grep -v grep | while read line; do
  question=$(echo "$line" | sed 's/.*-p ["\x27]*\([^"\x27]*\).*/\1/' | cut -c1-80)
  model=$(echo "$line" | grep -o '\-\-model [a-z]*' | cut -d' ' -f2)
  echo "  [$model] $question..."
done

# Report Status
echo "Reports:"
ls -d reports/2025* 2>/dev/null | while read dir; do
  if [ -f "$dir/SYNTHESIS.md" ]; then
    lines=$(wc -l < "$dir/SYNTHESIS.md")
    echo "  ✓ $dir ($lines lines)"
  else
    echo "  ◌ $dir (in progress)"
  fi
done
```

## Best Practices

1. **Model Tiering beachten**: Opus orchestriert, Sonnet forscht, Haiku für Atomic
2. **Decomposition nicht erzwingen**: Manche Fragen sind besser direkt beantwortet
3. **Depth limitieren**: 3-4 Levels meist ausreichend, mehr = diminishing returns
4. **Synthesis priorisieren**: Findings ohne Synthese sind nur Daten
5. **Parallel wo möglich**: Sub-Agents parallel, nicht sequentiell

## Vergleich mit anderen Patterns

| Aspect | Recursive Research | Task Decomposition Pipeline |
|--------|-------------------|------------------------------|
| Agent Spawning | Rekursiv, LLM-gesteuert | Task-basiert, definiert |
| Decomposition | LLM-gesteuert | Vordefinierte Subtasks |
| Synthesis | Am Ende, hierarchisch | Nach jeder Phase |
| Model Selection | Manuell per Flag | Automatisch per Complexity |

---

## Related

- [Task Decomposition Pipeline](task-decomposition-pipeline.md) - Structured alternative
- [Parallel Agent Dispatch Pattern](parallel-agent-dispatch-pattern.md) - Parallel execution
- [Delegation-Request Pattern](delegation-request-pattern.md) - Inter-agent communication
