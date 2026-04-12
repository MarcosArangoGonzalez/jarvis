---
title: "Jarvis Tasks"
type: tasks
status: active
tags:
  - jarvis
  - tasks
  - planning
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/tasks/projects/bjj_rag.md"
  - "/home/marcos/jarvis/wiki/tasks/projects/tfg_bjj_app.md"
  - "/home/marcos/jarvis/wiki/tasks/projects/jarvis_core.md"
Summary: "Global Jarvis task dashboard for daily planning across projects and life areas."
---

# Jarvis Tasks

## Priority Rules

- P0: blocks today's work or fixes a critical failure.
- P1: advances the main active objective.
- P2: important but not blocking.
- P3: backlog or future improvement.

## Today

| Priority | Task | Project | Feature | Status | Next Action | Source |
|---|---|---|---|---|---|---|
| P1 | Configure Jarvis voice flow | Jarvis Core | Voice | Implemented v1 | Bind `jarvis_voice_flow.sh` to an Ubuntu shortcut and validate paste in Codex/Claude | `wiki/tasks/projects/jarvis_core.md` |
| P1 | Implement Intent Classifier + Router | BJJ RAG | Agentic RAG | Ready | Start with rules-only classifier, no LLM | `wiki/tasks/projects/bjj_rag.md` |
| P2 | Create TFG anteproyecto/memoria outline | TFG BJJ App | TFG Docs | Backlog | Draft document structure and evaluation rubric | `wiki/tasks/projects/tfg_bjj_app.md` |

## Cross-Project Backlog

| Priority | Task | Project | Feature | Status | Next Action | Source |
|---|---|---|---|---|---|---|
| P1 | `search_kb` + query embedding cache | BJJ RAG | Retrieval Quality | Backlog | Implement after Router | `wiki/tasks/projects/bjj_rag.md` |
| P2 | Generator prompt as BJJ tutor | BJJ RAG | Agentic RAG | Backlog | Implement after search_kb | `wiki/tasks/projects/bjj_rag.md` |
| P2 | Combined Evaluator | BJJ RAG | Grounding | Backlog | Add fallback `unverified_response` | `wiki/tasks/projects/bjj_rag.md` |
| P2 | Resolve `visuals` contract drift | BJJ RAG | Contract Drift | Backlog | Decide Java field vs combat_story-only | `wiki/tasks/projects/bjj_rag.md` |
| P3 | Technique Debugger | BJJ RAG | Technique Debug | Backlog | Implement gate strictness | `wiki/tasks/projects/bjj_rag.md` |
| P3 | Query Rewriter | BJJ RAG | Retrieval Retry | Backlog | Implement last | `wiki/tasks/projects/bjj_rag.md` |

## Morning Coffee Output

Each daily report should include:

- top 3 recommended tasks
- blockers
- suggested session target
- mode
- primary role
- supporting roles/subagents
- tasks to add/remove/reorder
