---
title: "RAG Patterns Comparison"
type: analysis
status: reference
tags:
  - bjj-app
  - tfg
  - rag
  - agentic-rag
  - graph-rag
  - architecture
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 0
sources:
  - "/home/marcos/Descargas/rag-patterns.md"
Summary: "Comparison of naive RAG, Agentic RAG/CRAG, GraphRAG, and Self-RAG for the BJJ-app AgentGraphService design."
---

# RAG Patterns — Comparison and Selection

> **Status:** Reference  
> **Context:** BJJ-app AgentGraphService design decisions

---

## The three main patterns

### Pattern 1 — Naive RAG
```
query → embed → retrieve → prompt + docs → LLM → answer
```
What you have in RAG-05 (stateless endpoint).

**Good for:** simple factual questions with a well-populated knowledge base.  
**Bad for:** multi-step reasoning, low-quality retrievals, ambiguous queries, domain-specific routing.  
**Hallucination rate:** high — no grounding check.

---

### Pattern 2 — Agentic RAG (CRAG)
```
query → classify intent → route → retrieve → grade → [rewrite + retry] → generate → check grounding → answer
```
What the AgentGraphService implements. Based on the CRAG paper (Corrective Retrieval Augmented Generation, 2024).

**Good for:** your exact use cases. The agent decides *how* to retrieve, not just *what* to retrieve.  
**Key insight:** "How do I escape mount?" and "debug my kimura video" need completely different retrieval strategies. A single chain collapses them into the same path and does both badly.  
**Hallucination rate:** ~15%, evaluator catches ~70% of those → effective rate ~4–5%.

---

### Pattern 3 — GraphRAG
Instead of indexing text chunks, build a knowledge graph of entities and relationships:
```
Mount → [escape techniques] → Hip escape
Hip escape → [requires] → Frame position
Frame position → [demonstrated in] → Video #47
```
Query traversal follows graph edges, not vector similarity.

**Good for:** relational knowledge where connections matter as much as content. BJJ is inherently relational — positions connect to submissions connect to escapes connect to counters.  
**Enables:** "What are all submissions available from mount, and what are their escapes?" as a graph traversal.  
**Requires:** Neo4j or Amazon Neptune, entity extraction pipeline, query planner.  
**Post-TFG only:** scope is comparable to the entire current system.

---

## Which pattern fits each use case

| Use case | Best pattern | Why |
|---|---|---|
| Technique questions | Agentic RAG | KB retrieval + grounding check |
| Video debugging | Structured data + LLM | Primary input is combat_story/joint_angles, not KB |
| Video recommendations | Filtered retrieval | Metadata filtering, minimal generation |
| Training plan | Heuristic + LLM | User level + available videos; retrieval optional |

**Key insight:** not every node needs to retrieve. The router decides per-intent whether retrieval is useful. For video debugging, the KB is supplementary — the real input is the structured pipeline output. For training plans, retrieval may add less than a well-crafted prompt with user context.

---

## The CRAG pattern in detail

CRAG (Shi et al., 2024) introduces three document quality grades:

- **Correct:** retrieved docs clearly support the query → generate directly
- **Ambiguous:** docs partially relevant → generate with low confidence, add warnings
- **Incorrect:** docs irrelevant → rewrite query and retry; if still failing, use web search or fallback

Your Combined Evaluator implements this in a single LLM call with two checks:
1. Do the docs cover the query? (relevance gate)
2. Does the answer contain only claims supported by the docs? (grounding gate)

The retry loop (evaluator fail → query rewriter → retriever → generator → evaluator) is the CRAG correction mechanism.

---

## Self-RAG

Self-RAG (Asai et al., 2023) adds reflection tokens — the LLM generates special tokens like `[Retrieve]`, `[IsRel]`, `[IsSup]`, `[IsUse]` inline with its output to decide dynamically whether to retrieve, whether retrieved docs are relevant, and whether its own claims are supported.

More powerful than CRAG but requires a fine-tuned model. Not applicable without labeled BJJ training data. Post-TFG consideration if a fine-tuned model is ever trained.

---

## LangChain components used

| Your code | LangChain equivalent |
|---|---|
| `rag_service.query_documents()` | `retriever.invoke()` |
| `gemini_vision_service.py` | `ChatGoogleGenerativeAI` |
| `agent_service.py` | `AgentExecutor` with tools |
| ChromaDB setup | `Chroma.from_documents()` |
| Manual chain | `prompt \| llm \| output_parser` |

---

## Key references

- **CRAG:** Shi et al. (2024) — "Corrective Retrieval Augmented Generation"
- **Self-RAG:** Asai et al. (2023) — "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"
- **GraphRAG:** Edge et al. (2024, Microsoft) — "From Local to Global: A Graph RAG Approach to Query-Focused Summarization"
- **LangGraph agentic RAG tutorial:** python.langchain.com/docs/tutorials/rag

---

## Links
- [[plan-assessment]] — Plan assessment
- [[agent-langgraph-migration]] — LangGraph migration
- [[company-vs-tfg-comparison]] — Resource comparison
