---
title: "BJJ RAG Tasks"
type: tasks
status: active
tags:
  - bjj-app
  - rag
  - agentic-rag
  - tasks
created: 2026-04-12
updated: 2026-04-19
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/improvements-prompt.md"
Summary: "Project task list for implementing the BJJ agentic RAG system."
---

# BJJ RAG Tasks

## Active Queue

| Priority | Task | Feature | Status | Conclusion | Next Action |
|---|---|---|---|---|---|
| P1 | Implement Intent Classifier + Router | Agentic RAG | Ready | First code step; rules-only and low risk. | Define service API and tests. |
| P1 | Implement `search_kb` + `get_query_embedding` cache | Retrieval Quality | Backlog | Needed before generator quality work. | Add LRU cache and source metadata handling. |
| P2 | Implement Generator prompt as BJJ tutor | Agentic RAG | Backlog | Makes answers product-visible. | Use retrieved docs and mode-specific prompts. |
| P2 | Implement Combined Evaluator | Grounding | Backlog | Controls hallucination and relevance. | Add fallback `unverified_response`, `confidence=0.5`. |
| P2 | Resolve `visuals` contract drift | Contract Drift | Backlog | Python frame visuals are not modelled in Java. | Decide Java field vs combat_story-only. |
| P3 | Implement Technique Debugger | Technique Debug | Backlog | Depends on gate and video context availability. | Enforce `vectorized`, `combat_story`, `joint_angles`. |
| P3 | Implement Query Rewriter | Retrieval Retry | Backlog | Least critical and most behaviorally risky. | Implement last, max 150 chars. |
| P3 | Expose `agent_metrics` | TFG Evaluation | Backlog | Needed for empirical comparison. | Add debug/eval response fields. |
| P3 | Apply AgentGraphService improvements | Quality Hardening | Ready after v1 | Six-block prompt exists in `[[improvements-prompt]]`. | Run after AgentGraphService v1 is implemented and tested. |

## Implementation Order

1. Intent Classifier + Router.
2. `search_kb` + `get_query_embedding`.
3. Generator.
4. Combined Evaluator.
5. Technique Debugger.
6. Query Rewriter.
7. `agent_metrics`.
