---
title: Memory Architecture Pattern
type: pattern
domain: [memory, architecture]
created: 2026-03-02
confidence: 80%
source: "Agent-Skills-for-Context-Engineering (Memory Systems Skill)"
---

# Memory Architecture Pattern

**Quelle**: Agent-Skills-for-Context-Engineering (Memory Systems Skill)
**Erstellt**: 2025-12-27
**Kategorie**: System Architecture

---

## Problem

Agents verlieren State zwischen Sessions. Einfache Vector Stores verlieren Relationship-Information und haben keine temporale Validität.

## Lösung

Layered Memory Architecture mit 5 Ebenen + Temporal Knowledge Graph.

---

## Memory Spectrum

```
          Latency    Capacity    Persistence
             ↓          ↓           ↓
┌─────────────────────────────────────────────┐
│  WORKING MEMORY (Context Window)            │
│  - Zero latency, volatile                   │
│  - Scratchpad, current task state           │
└─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  SHORT-TERM MEMORY (Session-Scoped)         │
│  - Session-persistent, searchable           │
│  - Intermediate results, caches             │
└─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  LONG-TERM MEMORY (Cross-Session)           │
│  - Persistent, structured                   │
│  - User preferences, project state          │
└─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  ENTITY MEMORY (Knowledge Graph)            │
│  - Entity identity across conversations     │
│  - Relationship tracking                    │
└─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  TEMPORAL KNOWLEDGE GRAPH                   │
│  - Validity periods (valid_from/valid_until)│
│  - Time-travel queries                      │
│  - Context clash prevention                 │
└─────────────────────────────────────────────┘
```

---

## Benchmark Performance (DMR)

| Memory System | DMR Accuracy | Retrieval Latency | Notes |
|---------------|--------------|-------------------|-------|
| **Zep (Temporal KG)** | 94.8% | 2.58s | Best accuracy, fast |
| MemGPT | 93.4% | Variable | Good general |
| GraphRAG | ~75-85% | Variable | 20-35% over RAG |
| Vector RAG | ~60-70% | Fast | Loses relationships |
| Recursive Summarization | 35.3% | Low | Severe info loss |

**Key Insight**: Zep erreicht 90% Latency-Reduktion (2.58s vs 28.9s) durch selektive Subgraph-Retrieval.

---

## Implementation Patterns

### Pattern 1: File-System-as-Memory

Einfachste Implementation, keine Infrastruktur nötig.

```
_memory/
├── index.json              # Aktiver Context
├── projects/
│   └── {name}.json         # Projekt-State
├── experiences/
│   └── exp-YYYY-NNN.json   # Experience Memory
└── sessions/
    └── context.json        # Session-spezifisch
```

**Vorteile**: Einfach, transparent, portabel
**Nachteile**: Keine semantische Suche, keine Relationship-Queries

### Pattern 2: Vector RAG + Metadata

```python
def add_with_metadata(text, entity, valid_from, valid_until=None):
    embedding = embed(text)
    metadata = {
        "entity": entity,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat() if valid_until else None
    }
    vector_store.add(embedding, metadata)
```

**Vorteile**: Semantische Suche, Temporal Filtering
**Nachteile**: Keine Relationship-Traversal

### Pattern 3: Knowledge Graph (JSON-based)

```json
{
  "nodes": [...],
  "edges": [
    {
      "source": "project-alpha",
      "target": "pattern-multi-agent",
      "type": "implements",
      "valid_from": "2025-12-01T00:00:00Z",
      "valid_until": null
    }
  ]
}
```

**Vorteile**: Relationship-Queries, Temporal Validity
**Nachteile**: Keine semantische Suche (ergänzbar mit ChromaDB)

### Pattern 4: Temporal Knowledge Graph

Erweiterung von Pattern 3 mit Temporal Queries:

```python
def query_at_time(graph, query_time):
    """Query graph state at specific point in time."""
    valid_edges = []
    for edge in graph.edges:
        valid_from = parse_date(edge.get("valid_from", "1970-01-01"))
        valid_until = edge.get("valid_until")

        if valid_from <= query_time:
            if valid_until is None or parse_date(valid_until) > query_time:
                valid_edges.append(edge)

    return valid_edges
```

---

## Memory Selection Guide

| Requirement | Recommended Architecture |
|-------------|--------------------------|
| Simple persistence | File-System Memory |
| Semantic search | Vector RAG + Metadata |
| Relationship queries | Knowledge Graph |
| Temporal validity | Temporal Knowledge Graph |
| Semantic + Relationships | KG + ChromaDB (hybrid) |

---

## Memory Consolidation

Memories akkumulieren. Consolidation verhindert unbounded growth.

### Consolidation Triggers

1. Memory count > threshold (z.B. 1000)
2. Retrieval returns too many outdated results
3. Periodic schedule (weekly)
4. Explicit request

### Consolidation Process

```python
def consolidate(memory_system):
    # 1. Find duplicates (same subject + predicate)
    duplicates = find_duplicate_groups()

    # 2. Merge related facts
    for group in duplicates:
        keeper = max(group, key=lambda e: e.confidence)
        merge_properties(keeper, *group)
        delete_others(group, except_=keeper)

    # 3. Update validity periods
    update_validity_periods()

    # 4. Rebuild indexes
    rebuild_indexes()
```

---

## Reference Implementation

A common layered memory system uses:

| Layer | Implementation | Location |
|-------|----------------|----------|
| Working Memory | Context Window | (in-session) |
| Short-Term | Session State | (ephemeral) |
| Long-Term | Domain Memory | `_memory/projects/` |
| Entity Memory | Knowledge Graph | `_graph/nodes.json` |
| Temporal KG | Graph + Validity | `_graph/edges.json` (extended) |
| Experience Memory | Solutions/Patterns | `_memory/experiences/` |

### Temporal Validity in Edges

Schema erweitert um:
- `valid_from`: ISO 8601 datetime
- `valid_until`: ISO 8601 datetime oder null (aktuell gültig)

### Use Cases für Temporal Queries

1. "Was war der Projekt-Status am 15.12.?"
2. "Welche Patterns waren vor dem Refactoring aktiv?"
3. "Historische Entity-Beziehungen rekonstruieren"

---

## ChromaDB Integration (Optional)

Für semantische Suche über große Dokumentensammlungen:

```python
# Hybrid: KG für Relationships, ChromaDB für Semantic Search
def hybrid_query(query, query_time=None):
    # 1. Semantic search in ChromaDB
    semantic_results = chromadb.query(query, n=10)

    # 2. Entity extraction from results
    entities = extract_entities(semantic_results)

    # 3. Graph traversal for relationships
    related = graph.find_related(entities, query_time)

    # 4. Merge and rank
    return merge_and_rank(semantic_results, related)
```

**Wann ChromaDB nutzen:**
- Große Dokumentensammlungen (>1000 Dokumente)
- Semantic search über unstrukturierte Texte
- Embedding-basierte Similarity

**Wann Knowledge Graph reicht:**
- Strukturierte Entity-Relationships
- Temporal Queries
- Überschaubare Entity-Anzahl (<500 Entities)

---

## References

- Agent-Skills-for-Context-Engineering: Memory Systems Skill
- DMR Benchmark (Zep vs MemGPT vs Vector RAG)
- GraphRAG: 20-35% accuracy gains
