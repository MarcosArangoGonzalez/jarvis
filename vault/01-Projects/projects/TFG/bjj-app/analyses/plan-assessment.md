---
title: "BJJ Agent Plan Assessment"
type: analysis
status: approved
tags:
  - bjj-app
  - tfg
  - rag
  - agentic-rag
  - architecture
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 753
sources:
  - "/home/marcos/Descargas/plan-assessment.md"
Summary: "Assessment of the AgentGraphService plan: correct architectural choices, weak points to track, rejected alternatives, and implementation details that determine RAG quality."
---

# BJJ Agent — Plan Assessment

> **Status:** Approved with notes  
> **Phase:** 5D — AgentGraphService  
> **Last updated:** 2026-04-19

---

## What the plan gets right

### Rules-first intent classification
The classifier fires a dictionary lookup before spending a single token. For "cómo", "explica", "qué es" — zero latency, zero cost. The LLM only activates when rules fail. This is what production systems do and it was the correct call to reject LLM-for-everything.

### Combined Evaluator
Merging relevance grading and hallucination checking into one LLM call is both token-efficient and architecturally sound. The CRAG paper (2024) validates this pattern explicitly. Two separate calls would double cost and latency for no quality gain.

### Technique Debugger gate
Refusing to run without `vectorized + combat_story + joint_angles` means the system never fabricates a debug session. Most AI systems fail here — they generate confident-sounding nonsense when data is missing. The hard stop is the correct design.

### Stateless session memory
Storing `session_summary` on the client and resending it each turn is exactly how production chatbots handle session memory without a database. OpenAI's API works this way. It is not a compromise — it is the correct pattern for stateless servers.

### Data Flywheel
Most RAG systems have a static knowledge base. This one grows with every analyzed video and every PROFESSOR correction. The system gets better the more it is used, without retraining. This is a genuine architectural differentiator.

---

## Weak points to track

| Issue | Severity | Fix |
|---|---|---|
| ChromaDB no horizontal scaling | Post-TFG | Migrate to Weaviate or Pinecone |
| LRU cache too small (100 entries) | Low | Redis with TTL post-TFG |
| session_summary has no length budget | Medium | Hard cap 120 words, drop oldest first |
| Query Rewriter undefined on unknown terms | Low | Pass through rather than hallucinate |
| Technique Debugger needs unconfirmed Java endpoints | Blocker for Phase 5 | Confirm GET /publications/{id}/combat-story |

---

## Why alternatives were correctly rejected

**LangGraph now:** heavyweight dependency with version drift risk in a short TFG evaluation window. Custom graph is structurally isomorphic — migration is mechanical, not a rewrite.

**GraphRAG now:** requires entity extraction pipeline, graph database (Neo4j), query planner. A separate project of comparable scope. Correct for post-TFG.

**Vector-only RAG:** cannot handle routing. "How do I escape mount?" and "debug my kimura video" require fundamentally different pipelines. Collapsing them does both badly.

**Fine-tuned model:** requires thousands of labeled BJJ Q&A pairs that do not exist yet. RAG is the correct approach when you have structured knowledge but limited labeled examples.

---

## Implementation details that determine quality

### Generator prompt (highest leverage)
The system prompt must include: *"If the retrieved documents do not support a claim, say so explicitly rather than inferring."* Most RAG systems omit this and hallucinate confidently.

### session_summary updater
```python
summary_prompt = f"""
Summarise this conversation in max 120 words.
Drop oldest context first if needed.
Previous summary: {state.session_summary}
Latest exchange: Q: {state.query} A: {state.answer[:200]}
"""
```

### Embedding cache normalisation
```python
def normalise_query(q: str) -> str:
    return q.lower().strip().replace("  ", " ")

@lru_cache(maxsize=200)
def get_cached_embedding(normalised_query: str): ...
```
Without normalisation, "How do I escape Mount?" and "how do i escape mount?" are two cache misses.

---

## Links
- [[agent-langgraph-migration]] — LangGraph migration path
- [[rag-patterns]] — RAG pattern comparison
- [[company-vs-tfg-comparison]] — resource comparison
