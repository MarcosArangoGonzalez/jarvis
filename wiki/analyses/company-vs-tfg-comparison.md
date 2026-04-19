---
title: "Company vs TFG Resource Comparison"
type: analysis
status: reference
tags:
  - bjj-app
  - tfg
  - rag
  - architecture
  - roadmap
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 0
sources:
  - "/home/marcos/Descargas/company-vs-tfg-comparison.md"
Summary: "Honest comparison between a well-funded BJJ AI product and the TFG system, including tradeoffs, projected metrics, security gaps, moat, and post-TFG roadmap."
---

# Resource Comparison — Well-funded Company vs BJJ-app TFG

> **Status:** Reference  
> **Purpose:** Honest assessment of tradeoffs, expected results, and post-TFG roadmap

---

## What a well-funded team would build

A team like Khanmigo (Khan Academy) or a well-resourced sports AI startup would approach each layer differently:

### Knowledge layer
Not ChromaDB with flat vector chunks — a property graph database (Neo4j or Amazon Neptune) where every BJJ position, technique, escape, and counter is a node with typed relationships.

"Kimura from side control" is not a text chunk. It is an entity connected to:
- `side_control` (position)
- `figure-four grip` (grip type)
- `shoulder rotation` (mechanism)
- `trap the arm` (setup)
- `Video #47` (demonstration)

Queries traverse the graph rather than searching by vector similarity. Retrieval precision: ~90%+ for technique-specific questions vs ~70% for vector similarity.

### Model layer
A domain fine-tuned model — either Llama 3 fine-tuned on 50,000 labeled BJJ Q&A pairs, or GPT-4 with systematic prompt engineering validated against a gold-standard test set. Common questions answered from model weights without retrieval. Response time under 1 second.

### Vision layer
Not YOLOv8 + Random Forest — a purpose-built pose estimation model trained on 1M+ BJJ frames, with multi-person tracking that maintains athlete identity across occlusions, and a temporal model (LSTM or Transformer) over pose sequences rather than individual frames. Technique classification accuracy: ~90%+ vs ~70–80% for the current system.

### Infrastructure
- Vector database with horizontal scaling: Pinecone or Weaviate
- Dedicated embedding server (not sentence-transformers in-process)
- Message queue for video processing: Celery + Redis
- Feature store for pre-computed embeddings
- Continuous evaluation pipeline with A/B testing of prompt variations
- Human raters reviewing a sample of responses daily

---

## What BJJ-app builds and why it is not just a compromise

### ChromaDB instead of Neo4j
You lose graph traversal but gain zero operational overhead. At 5,000–20,000 documents, vector similarity retrieval with good metadata filtering gets 80% of the quality at 5% of the complexity. The flywheel means quality improves over time without architectural changes.

### Rules-first classifier instead of fine-tuned
Zero latency for 80% of queries. The 20% that need LLM classification are genuinely ambiguous — a fine-tuned classifier would not do much better on those cases.

### Gemini Vision as fallback instead of purpose-built vision model
State-of-the-art visual reasoning for technique identification without training data. The tradeoff is latency and cost. Gemini's visual reasoning on BJJ frames is genuinely better than a small custom model trained on limited data — until the dataset is large enough to justify training.

### Custom graph instead of LangGraph
Zero dependency risk, full control over behavior, mechanical migration path. The only things missing are built-in persistence and streaming — both addable post-TFG.

---

## Expected results — honest projections

| Metric | TFG system | Post-TFG improvements | Well-funded company |
|---|---|---|---|
| Technique question accuracy | 65–75% | 75–85% with GraphRAG | 90%+ fine-tuned model |
| Video debug accuracy | 60–70% | 75%+ better vision | 85%+ purpose-built model |
| Response latency | 2–5s | 1–2s caching + streaming | <1s local fine-tuned model |
| Hallucination rate | ~15% (evaluator catches ~70%) | ~8% larger KB | <5% fine-tuned model |
| Session coherence | 3–5 turns | 10+ turns persistent memory | Full history |
| Concurrent users | 5–10 single process | 50–100 async workers | 10,000+ distributed |
| Knowledge freshness | Hours (batch flywheel) | Minutes (streaming flywheel) | Real-time |

### The numbers that matter for the TFG demo
- **Response latency under 5 seconds** — achievable. With LRU cache and rules-first classifier, most queries call Gemini once (Generator) or twice (Generator + Evaluator): 1.5–3 seconds.
- **Hallucination rate low enough that evaluator warnings are rarely visible** — achievable with curated KB and tight generator prompt.

### Accuracy ceiling
Bottlenecked by ChromaDB content quality. With 219 documents indexed and PROFESSOR curation active, the honest ceiling for technique questions is ~70%. Not because the architecture is wrong — because the knowledge base is still small. Every new curated video raises this ceiling.

---

## Security assessment

| Threat | Current mitigation | Gap |
|---|---|---|
| Prompt injection via user queries | Evaluator grounding check (partial) | Dedicated input sanitizer |
| PII in knowledge base | No PII in video annotations | Fine |
| Webhook spoofing | X-Webhook-Secret header | Fine |
| JWT expiry | Standard Spring Security | Fine |
| ChromaDB access | Internal only, not exposed | Fine |

The main risk is prompt injection — someone crafting a query to make the tutor return incorrect technique advice. The evaluator's grounding check partially mitigates this (injected claims won't be supported by documents). A dedicated sanitizer would be the production fix.

---

## Where the TFG system genuinely beats the well-funded alternative

A general-purpose AI assistant (ChatGPT, Gemini) cannot replicate:
- The `combat_story` format tied to actual video analysis
- The position taxonomy mapped to real RF classifier output
- The Technique Debugger grounded in actual joint angles from the athlete's own video
- The PROFESSOR curation loop creating domain-specific trust signals

These are domain-specific features that require the vision pipeline to exist. They are the genuine moat.

---

## Post-TFG improvements by ROI

| Improvement | Effort | Impact |
|---|---|---|
| Persistent memory in PostgreSQL | 1 week | Session coherence for 10+ turns |
| Streaming responses to frontend | 3 days | Perceived latency cut by 60% |
| Redis cache for embeddings | 2 days | Handles concurrent users |
| LangGraph migration | 1–2 days | Persistence + streaming + parallel retrieval |
| GraphRAG knowledge layer | 3–4 weeks | Accuracy +10–15% on relational queries |
| Larger curated KB (BJJ manuals, WPT) | Ongoing | Biggest single accuracy driver |
| Fine-tuned model on BJJ Q&A | 2–3 months | Accuracy ceiling raised to 90%+ |
| Purpose-built vision model | 3–6 months | Video debug accuracy +15–20% |

---

## Links
- [[plan-assessment]] — Plan assessment
- [[rag-patterns]] — RAG pattern comparison
- [[agent-langgraph-migration]] — LangGraph migration path
