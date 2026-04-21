---
title: "Jarvis Tasks"
type: tasks
status: active
tags:
  - jarvis
  - tasks
  - planning
created: 2026-04-12
updated: 2026-04-20
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/tasks/tfg-bjj-app-tasks.md"
  - "/home/marcos/jarvis/wiki/tasks/projects/jarvis_core.md"
  - "/home/marcos/jarvis/wiki/tasks/projects/sie.md"
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
| P1 | Implement Intent Classifier + Router | BJJ RAG | Agentic RAG | Ready | Start with rules-only classifier, no LLM | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P2 | Create TFG anteproyecto/memoria outline | TFG BJJ App | TFG Docs | Backlog | Draft document structure and evaluation rubric | `wiki/projects/TFG/bjj-app/tasks/tfg-bjj-app-tasks.md` |
| P0 | Configurar OAuth Google Drive MCP | SIE | Integración | Pendiente | Ejecutar flujo OAuth para activar acceso a Drive | `wiki/tasks/projects/sie.md` |
| P1 | Validar modulo Odoo de audiolibros desde UI | SIE | Practica 3 Odoo | Backlog | Abrir `http://localhost:8069`, usar DB `sie_p3_test3` y ejecutar checklist manual | `wiki/tasks/projects/sie.md` |
| P1 | Ampliar investigación + redactar contenido | SIE | Investigación | WIP | Fuentes en NotebookLM; doc en Drive necesita más desarrollo | `wiki/tasks/projects/sie.md` |

## Cross-Project Backlog

| Priority | Task | Project | Feature | Status | Next Action | Source |
|---|---|---|---|---|---|---|
| P1 | `search_kb` + query embedding cache | BJJ RAG | Retrieval Quality | Backlog | Implement after Router | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P2 | Generator prompt as BJJ tutor | BJJ RAG | Agentic RAG | Backlog | Implement after search_kb | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P2 | Combined Evaluator | BJJ RAG | Grounding | Backlog | Add fallback `unverified_response` | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P2 | Resolve `visuals` contract drift | BJJ RAG | Contract Drift | Backlog | Decide Java field vs combat_story-only | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P3 | Technique Debugger | BJJ RAG | Technique Debug | Backlog | Implement gate strictness | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |
| P3 | Query Rewriter | BJJ RAG | Retrieval Retry | Backlog | Implement last | `wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md` |

## Morning Coffee Output

Each daily report should include:

- top 3 recommended tasks
- blockers
- suggested session target
- mode
- primary role
- supporting roles/subagents
- tasks to add/remove/reorder
