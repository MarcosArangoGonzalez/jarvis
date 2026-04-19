---
title: Jarvis Log
type: log
status: active
tags:
  - jarvis
  - log
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 0
sources: []
Summary: Chronological operating log for JarvisOS.
---

# Jarvis Log

## 2026-04-12

- Initialized JarvisOS workspace in `/home/marcos/jarvis`.
- Added identity switching, local voice, queue-based ingest, and token pruning plan.
- Added global session protocol in `.jarvis/session_manager.md`, linked it from `CLAUDE.md`, and initialized BJJ RAG feature progress tracking.
- Added BJJ agentic RAG graph design and TFG project document index.
- Added scalable task structure under `wiki/tasks/`, root `README.md`, and morning coffee quick-start protocol.
- Implemented Jarvis Voice Flow v1: fixed-duration recording, whisper.cpp transcription, optional Ollama refinement, Wayland/X11 clipboard and paste attempt, and Ubuntu shortcut wrapper.
- Improved Jarvis Voice Flow recognition quality: downloaded Whisper `ggml-small.bin`, made it the preferred model, and added a technical/BJJ prompt for better Codex/RAG/BJJ vocabulary handling.
- Added Jarvis Voice Toggle: press shortcut once to start recording, press again to stop/transcribe/paste, plus optional `.desktop` launcher for icon activation.
- Configured Jarvis Voice Toggle access: `Super + Shift + V` GNOME shortcut, local `.desktop` launcher installed, and `ydotoold` active for Wayland paste support.
- Fixed Jarvis Voice Wayland injection: prefer direct `ydotool type`/`wtype` text insertion before falling back to simulated paste, avoiding raw keycode artifacts such as `2442`.
- Reduced Jarvis Voice latency: added `JARVIS_VOICE_MODE=fast|balanced`, set the toggle default to `fast`, and made clipboard copy non-fatal when desktop clipboard access is unavailable.

## 2026-04-19 12:30 — Jarvis auto-log: limpieza del sistema de logs y hooks de sesión

- Eliminadas 87 entradas vacías `session end` de `wiki/log.md`; log restaurado a contenido semántico real.
- Añadida regla **Auto-log** en `CLAUDE.md`: Claude escribe entrada detallada en `wiki/log.md` tras cualquier respuesta con trabajo significativo, sin necesidad de pedirlo.
- Reescrito `~/.claude/commands/jarvis-log.md`: exige 3–6 bullets concretos y sobreescribe `## Last Session` en `session_manager.md` en lugar de crear entradas duplicadas infinitas.
- Creado `tools/skills/session_end_hook.sh`: detecta archivos modificados/creados via `git diff` y `git ls-files`; escribe entrada automática al cerrar sesión.
- Registrado Stop hook en `~/.claude/settings.json`: ejecuta el script en cada cierre de Claude Code.
- Siguiente acción: hacer `/hooks` o reiniciar Claude Code para activar el hook en la sesión actual.


## 2026-04-19 12:24 — session end

## 2026-04-19 12:24 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - tools/skills/whatsapp_listener/listener.js
  - wiki/tasks/actions-chat-de-whatsapp-con-34-647-00-10-54.md


## 2026-04-19 12:27 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - .jarvis/session_manager.md
  - tools/skills/session_end_hook.sh
  - tools/skills/whatsapp_listener/listener.js
  - wiki/log.md
  - wiki/tasks/actions-chat-de-whatsapp-con-34-647-00-10-54.md


## 2026-04-19 12:27 — session end

## 2026-04-19 12:32 — session end

## 2026-04-19 12:32 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - .jarvis/session_manager.md
  - wiki/log.md


## 2026-04-19 19:08 — session end

## 2026-04-19 19:08 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - wiki/projects/TFG/bjj-app/analyses/agent-langgraph-migration.md
  - wiki/projects/TFG/bjj-app/analyses/bjj-agent-knowledge-index.md
  - wiki/projects/TFG/bjj-app/analyses/company-vs-tfg-comparison.md
  - wiki/projects/TFG/bjj-app/analyses/improvements-prompt.md
  - wiki/projects/TFG/bjj-app/analyses/plan-assessment.md
  - wiki/projects/TFG/bjj-app/analyses/rag-patterns.md
  - wiki/index.md
  - wiki/log.md
  - wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md
  - wiki/projects/TFG/bjj-app/project/tfg-bjj-app.md
  - wiki/projects/TFG/bjj-app/tasks/bjj-rag-tasks.md


## 2026-04-19 20:57 — session end

## 2026-04-19 20:57 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - .obsidian/graph.json

## 2026-04-19 — Phase 5D: AgentGraphService wired into rag.py + main.py

- Creado `agent_graph_service.py` (Phase 1 completo): GraphState, clasificador de intención, nodos retriever/generator/evaluator/rewriter/technique-debugger/session-summary/guarded-fallback, y método `run()` async.
- ChromaDB poblado con 13 chunks gold-standard BJJ (Phase 0 completo).
- Extendido `routers/rag.py`: `RagQueryRequest` acepta `session_summary`, `publication_id`, `debug`; `RagQueryResponse` incluye `confidence`, `warnings`, `mode`, `session_summary`, `agent_metrics`; endpoint delega a `AgentGraphService.run()` con fallback directo a `RagService` si no está inicializado.
- Actualizado `main.py`: `AgentGraphService` se inicializa en el lifespan tras `RagService` y se almacena en `app.state.agent_graph_service`.
- Decisión clave: sin LangGraph — custom graph isomorfo, dependencia cero, migrable post-TFG.
- Siguiente acción: escribir `tests/test_agent_graph_service.py` y confirmar endpoint Java `GET /publications/{id}/combat-story` (bloqueante para Technique Debugger).


## 2026-04-19 21:10 — session end

## 2026-04-19 21:10 — session end (auto)

- Archivos modificados o creados en esta sesión:
  - .obsidian/graph.json
  - README.md
  - tools/skills/relevance_mapper.py
  - wiki/analyses/agent-langgraph-migration.md
  - wiki/analyses/bjj_agent_design.md
  - wiki/analyses/bjj_agentic_rag_context.md
  - wiki/analyses/bjj-agent-knowledge-index.md
  - wiki/analyses/bjj_java_python_contracts.md
  - wiki/analyses/company-vs-tfg-comparison.md
  - wiki/analyses/improvements-prompt.md
  - wiki/analyses/plan-assessment.md
  - wiki/analyses/rag-patterns.md
  - wiki/entities/marcos_arango.md
  - wiki/index.md
  - wiki/log.md
  - wiki/projects/TFG/bjj-app/analyses/agent-langgraph-migration.md
  - wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md
  - wiki/projects/TFG/bjj-app/analyses/bjj-agentic-rag-context.md
  - wiki/projects/TFG/bjj-app/analyses/bjj-agent-knowledge-index.md
  - wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md
  - wiki/projects/TFG/bjj-app/analyses/company-vs-tfg-comparison.md
  - wiki/projects/TFG/bjj-app/analyses/improvements-prompt.md
  - wiki/projects/TFG/bjj-app/analyses/plan-assessment.md
  - wiki/projects/TFG/bjj-app/analyses/rag-patterns.md
  - wiki/projects/TFG/bjj-app/bjj-app-index.md

