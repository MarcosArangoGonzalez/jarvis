---
title: "BJJ Agent Knowledge Index"
type: index
status: active
tags:
  - bjj-app
  - tfg
  - rag
  - agentic-rag
  - index
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 0
sources:
  - "/home/marcos/Descargas/README(1).md"
Summary: "Section index for BJJ Agent AI architecture documents covering plan assessment, RAG patterns, LangGraph migration, resource comparison, and implementation improvements."
---

# BJJ Agent — Knowledge Index

> **Section:** AI Architecture  
> **Last updated:** 2026-04-19

---

## Documents in this section

### [[plan-assessment]]
Assessment of the AgentGraphService plan — what it gets right, weak points to track, and implementation details that determine quality. Start here.

### [[rag-patterns]]
Comparison of Naive RAG, Agentic RAG (CRAG), and GraphRAG. Includes which pattern fits each use case (technique questions, video debugging, recommendations, training plans) and key academic references.

### [[agent-langgraph-migration]]
Step-by-step migration path from the custom AgentGraphService to LangGraph post-TFG. Includes structural equivalence table, what LangGraph adds (persistence, streaming, parallel execution), and a migration checklist.

### [[company-vs-tfg-comparison]]
Honest comparison between what a well-funded company would build vs what BJJ-app builds. Includes expected results table (accuracy, latency, hallucination rate, concurrency) and post-TFG improvements ranked by ROI.

### [[improvements-prompt]]
Claude Code prompt to implement the six specific improvements suggested after plan review: embedding cache normalisation, session_summary length budget, Query Rewriter defensive behavior, Generator grounding constraint, complete agent_metrics, and specific fallback messages.

---

## Architecture summary

```
Video analysis pipeline (deterministic):
  YOLO → Random Forest → Geometry → [Gemini Vision fallback] → Aggregator → Webhook

RAG agent pipeline (agentic):
  Query → Intent Classifier → Router →
    [technique] → Retriever → Generator → Evaluator → [retry via Rewriter] → Response
    [video_debug] → Technique Debugger (strict gate) → Retriever → Generator → Evaluator
    [recommendation] → Retriever (filtered) → Generator → Response
    [insufficient] → Guarded Fallback → Response
```

## Key decisions

| Decision | Rationale |
|---|---|
| Rules-first classifier | Zero cost for 80% of queries |
| Combined Evaluator | One LLM call instead of two |
| Custom graph over LangGraph | No dependency risk; mechanical migration later |
| ChromaDB over Neo4j | 80% quality at 5% complexity for current scale |
| Stateless session_summary | Correct pattern for stateless servers |
| Hard gate on Technique Debugger | Never fabricate a debug session |
