---
title: "TFG BJJ App"
type: project
status: active
tags:
  - project
  - tfg
  - bjj-app
  - software-architecture
  - security-specs
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 1200
sources:
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/memory/tfg.md"
  - "/home/marcos/jarvis/wiki/analyses/bjj_agent_design.md"
  - "/home/marcos/jarvis/wiki/projects/bjj_rag_implementation.md"
Summary: "Indice de gestion del TFG para bjj-app: anteproyecto, memoria, metodologia, bibliografia, experimentos, decisiones arquitectonicas y pendientes."
---

# TFG BJJ App

## Goal

Gestionar los documentos y decisiones del TFG asociado a `bjj-app`, especialmente la arquitectura del sistema, seguridad de contratos Java/Python, RAG agentico y evaluacion empirica.

## Documents

| Documento | Estado | Ubicacion | Siguiente accion |
|---|---|---|---|
| Anteproyecto | Backlog | Pendiente | Crear esquema inicial y objetivos. |
| Memoria | Backlog | Pendiente | Sincronizar estructura con `memory/tfg.md`. |
| Bibliografia | Backlog | Pendiente | Consolidar referencias RAG, pgvector, LangChain, HNSW y agentes. |
| Evaluacion empirica | Backlog | Pendiente | Definir tabla RAG stateless vs RAG agentico. |

## Methodology

- Evaluar una arquitectura realista de software: Spring Boot para estado/persistencia y Python para vision/RAG/LLM.
- Comparar RAG stateless contra RAG agentico usando metricas de calidad, grounding, latencia y utilidad tecnica.
- Mantener human-in-the-loop: conocimiento `curated` y validacion de profesor por encima de contenido generado.

## Architecture Decisions

- Java mantiene autenticacion, REST, estado y persistencia.
- Python mantiene vision, embeddings, ChromaDB, agente y LLM.
- El canal de retorno del analisis de video sigue siendo webhook con `X-Webhook-Secret`.
- V1 del RAG agentico usa Custom Graph Service; LangGraph queda para post-TFG.
- Memoria v1 es `session_summary` devuelto por el agente y almacenado localmente por frontend, sin persistencia en BD.

## Experiments

| Experimento | Objetivo | Metricas | Estado |
|---|---|---|---|
| RAG stateless vs RAG agentico | Comparar calidad y grounding | relevancia, utilidad, latencia, hallucination_detected | Backlog |
| Technique Debugger | Evaluar correcciones sobre videos | precision tecnica, top 3 correcciones, utilidad profesor | Backlog |
| Retrieval retry | Medir valor del Query Rewriter | retrieval_attempts, grader_passed_first_attempt | Backlog |

## Open Questions

- Definir dataset final de videos/frame cases para evaluacion.
- Decidir si `agent_metrics` se expone solo en modo debug/eval o tambien en UI interna.
- Resolver drift `visuals` por frame entre Python y Java.
- Decidir si se crea `shared/contracts/` o si la Wiki queda como contrato operativo versionado durante el TFG.

## Next Actions

1. Crear esquema de anteproyecto.
2. Crear indice de memoria.
3. Vincular experimentos con `bjj_agent_design.md`.
4. Definir rubrica de evaluacion de profesor para respuestas y debugger.
