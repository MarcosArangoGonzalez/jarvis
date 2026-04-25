---
title: "BJJ RAG Implementation"
type: project
status: active
tags:
  - project
  - bjj-app
  - rag
  - agentic-rag
  - tfg
created: 2026-04-12
updated: 2026-04-19
tokens_consumed: 12000
sources:
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agentic-rag-context.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/project/tfg-bjj-app.md"
  - "/home/marcos/jarvis/CLAUDE.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/CLAUDE.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/SESSION_CONTEXT.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5B.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5C.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5D.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agent-knowledge-index.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/plan-assessment.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/rag-patterns.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/agent-langgraph-migration.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/company-vs-tfg-comparison.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/improvements-prompt.md"
Summary: "Log activo del proyecto para convertir el RAG actual de bjj-app en un RAG agentico: inicio de sesion 2026-04-12, estado base, restricciones de seguridad y modularidad, contratos Java/Python, protocolo JarvisOS de sesion, diseno de grafo agentico, hitos pendientes y criterios de validacion."
---

# BJJ RAG Implementation

## Goal

Convertir el RAG actual de `bjj-app` en una capa agentica para tutor BJJ y feedback tecnico, manteniendo el contrato seguro Java/Python y la estabilidad del pipeline de analisis de video.

## Context

Estado base al 2026-04-12:

- Frontend `/rag` existe y consulta el endpoint actual, pero es stateless.
- Backend `POST /api/v1/rag/query` proxya a `ai-service` usando `X-Internal-Secret`.
- Python `ai-service` tiene `RagService` con ChromaDB, embeddings `all-MiniLM-L6-v2` y documentos master/bloque por publicacion.
- `AgentService` existe para feedback biomecanico por frame con LangChain/Gemini, RAG tool, safety tool y fallback `None`/heuristico.
- `combat_story`, `primary_detected_class`, `suggested_tags`, `vectorized` y `curated` son campos clave para el flywheel y para retrieval de calidad.
- Las reglas de Jarvis y `bjj-app/CLAUDE.md` obligan a modularidad, secrets por entorno, seguridad de webhook y continuidad del pipeline si el LLM falla.

## Session Log

### 2026-04-12 - Context Sync

- Leidas reglas de Jarvis en `/home/marcos/jarvis/CLAUDE.md`.
- Leidos templates `research.md` y `project.md`.
- Revisado contexto de `bjj-app`: `CLAUDE.md`, sesiones `SESSION_CONTEXT.md` y `SESSION_SUMMARY.md`, fases 5B/5C/5C-refinement/5D, contextos Java/Python y guia de conexion AI service.
- Revisado codigo RAG actual: `RagService`, `AgentService`, router interno `/internal/rag/query`, proxy Spring `RagController` y pantalla frontend `/rag`.
- Creada nota de investigacion: `/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agentic-rag-context.md`.
- Creado este log de proyecto: `/home/marcos/jarvis/wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md`.

### 2026-04-12 - Data Debt and Contract Map

- Movidos residuos de ingesta TFG fuera de la cola del watcher:
  - de `/home/marcos/jarvis/raw/ingest_queue/tfg_rescatado.json`
  - de `/home/marcos/jarvis/raw/ingest_queue/tfg_rescue.json`
  - a `/home/marcos/jarvis/raw/backup/ingest_queue/2026-04-12/`
- Documentados contratos Java/Python en `/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md`.
- Riesgo detectado: Python define `visuals` por frame en `DetectedFrameDto`, pero Java no lo modela en `DetectedFrameDto`; `combat_story` si admite bloques enriquecidos por `List<Map<String,Object>>`.

### 2026-04-12 - JarvisOS Session Protocol

- Implementado protocolo global de sesion en `/home/marcos/jarvis/.jarvis/session_manager.md`.
- Actualizado `/home/marcos/jarvis/CLAUDE.md` con puntero obligatorio al protocolo de bootstrap y handover.
- Definido `Senior Architect` como perfil por defecto para la siguiente fase del RAG.
- Definidos roles de apoyo por sesion: Contract Guardian, Research Curator, SRE Debugger e Implementation Worker.
- Decidido que el proyecto activo se infiere por path; si no hay mapeo claro, el agente debe preguntar antes de escribir project logs.
- Decidido inicialmente que no se crearian notas por sesion en `wiki/logs/`; politica posterior actualizada a logs centralizados en `wiki/logs/core/` y `wiki/logs/projects/` segun ambito.

### 2026-04-12 - Agentic Graph Design

- Disenado el grafo agentico v1 en `/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md`.
- Definida v1 TFG como `Custom Graph Service` en Python, sin dependencia `langgraph`, migrable post-TFG.
- Fijados nodos: Intent Classifier, Router, Retriever, Query Rewriter, Generator, Combined Evaluator, Technique Debugger y Guarded Fallback.
- Fijado gate estricto para Technique Debugger: `publication_id`, `vectorized=true`, `has_combat_story=true` y `joint_angles` no vacios.
- Fijado contrato backward-compatible: mantener `answer/sources` y anadir opcionales `confidence`, `warnings`, `mode`, `session_summary` y `agent_metrics`.
- Fijado orden de implementacion posterior: Wiki, Intent Classifier + Router, `search_kb` + cache LRU, Generator, Combined Evaluator, Technique Debugger, Query Rewriter y `agent_metrics`.
- Creado indice de gestion TFG en `/home/marcos/jarvis/wiki/projects/TFG/bjj-app/project/tfg-bjj-app.md`.

### 2026-04-19 - Agent Architecture Notes Imported

- Incorporadas notas descargadas de arquitectura AI Agent en `wiki/analyses/`.
- Creado indice `[[bjj-agent-knowledge-index]]` para navegar `[[plan-assessment]]`, `[[rag-patterns]]`, `[[agent-langgraph-migration]]`, `[[company-vs-tfg-comparison]]` y `[[improvements-prompt]]`.
- Validado criterio de alcance: AgentGraphService custom para TFG; LangGraph, GraphRAG, Redis cache, streaming y fine-tuning quedan como roadmap post-TFG.
- Convertido `[[improvements-prompt]]` en prompt operativo para cerrar cache, memoria, rewriter defensivo, grounding, metricas y fallback.

## Feature Progress

| Feature | Status | Progreso | Ultima modificacion | Conclusion | Siguiente accion |
|---|---|---:|---|---|---|
| Context Sync | Done | 100% | 2026-04-12 | Contexto base del RAG sincronizado en Jarvis. | Usarlo como entrada para diseno de agentes. |
| Contract Map | Done | 100% | 2026-04-12 | Contratos Java/Python documentados; queda riesgo concreto en `visuals`. | Resolver si `visuals` se persiste por frame o solo en `combat_story`. |
| JarvisOS Session Protocol | Done | 100% | 2026-04-12 | Protocolo Markdown-only creado y conectado desde `CLAUDE.md`. | Aplicarlo en la siguiente sesion real y ajustar si hay friccion. |
| Agentic RAG Design | Done | 100% | 2026-04-20 | AgentGraphService implementado: todos los nodos, GraphState, run() async, wired en rag.py y main.py. | — |
| AgentInput/AgentOutput Contracts | WIP | 75% | 2026-04-20 | Pydantic extendido con confidence/warnings/mode/session_summary/agent_metrics. Falta RagController.java. | Actualizar RagController.java para reenviar campos nuevos. |
| Conversation Memory | WIP | 50% | 2026-04-20 | session_summary generada y devuelta por el agente. Falta que frontend la almacene y reenvie. | Implementar localStorage en /rag page. |
| Retrieval Quality / Curated Weighting | Done | 85% | 2026-04-20 | Retriever con LRU cache, normalización de query, fallback sin filtro implementados. Bug document_type corregido. | Verificar con LLM real cuando se resetee quota. |
| AgentGraphService Improvements | Ready | 0% | 2026-04-19 | Prompt operativo preparado. Bloques 1/3/4/6 parcialmente cubiertos en v1. | Ejecutar improvements-prompt.md tras query real con Gemini. |
| Java/Python Contract Drift | WIP | 50% | 2026-04-20 | Python extendido. Java RagController aun solo reenvía query+filters. vectorized no en PublicationDto — verificado via ChromaDB. | Actualizar RagController.java. |
| Tests / E2E Validation | WIP | 40% | 2026-04-20 | 27 tests unitarios pasan. E2e validado hasta generator (falla por quota Gemini). Falta test con LLM real. | Query real tras reset de quota. |
| TFG Document Management | WIP | 20% | 2026-04-12 | Indice TFG creado; faltan anteproyecto, memoria y rubrica de evaluacion. | Crear esquema de anteproyecto y memoria. |

## Milestones

- [x] Sincronizar contexto Jarvis con estado real del RAG.
- [x] Retirar residuos `tfg_rescatado`/`tfg_rescue` de la cola de ingesta.
- [x] Documentar contratos Java/Python actuales en la Wiki.
- [x] Configurar protocolo de sesion JarvisOS para bootstrap, roles, progreso, logs y handover.
- [x] Disenar arquitectura del RAG agentico sin romper endpoints existentes.
- [x] Definir contratos `AgentInput`/`AgentOutput` y politica de memoria corta a nivel Wiki.
- [x] Incorporar notas de evaluacion y roadmap del AgentGraphService en Wiki.
- [ ] Decidir si los contratos pasan a `shared/contracts/` o si la Wiki queda como contrato operativo versionado.
- [ ] Resolver drift `visuals` por frame: persistirlo en Java o limitarlo a `combat_story`.
- [ ] Decidir estrategia de skills/tools: clases `services/skills/` vs tools LangChain especializadas.
- [ ] Incorporar memoria conversacional en `/rag` manteniendo respuesta stateless compatible.
- [ ] Mejorar retrieval: ponderacion `curated`, filtros robustos por `category`/`technique`, fuentes trazables y fallback cuando no hay evidencia.
- [ ] Separar capacidades: tutor conversacional, diagnostico de tecnica, seguridad biomecanica, transiciones y explicacion por cinturon.
- [ ] Anadir tests de regresion para RAG, agente y seguridad de endpoints internos.
- [ ] Ejecutar validacion end-to-end con backend + ai-service + Chroma.
- [ ] Documentar resultados para memoria TFG, incluyendo comparativa RAG vs Long-Context si procede.

## Development Rules

- No hardcodear secrets; usar `.env`/settings.
- No cambiar el canal de retorno: webhook con `X-Webhook-Secret`.
- No romper el pipeline si falla LLM/RAG; usar `None`, fallback heuristico o respuesta de contexto insuficiente.
- Mantener Java como capa de auth/estado/persistencia y Python como capa de vision/RAG/LLM.
- Mantener embeddings de 384 dimensiones alineados con `all-MiniLM-L6-v2`.
- No reintroducir LangChain4j ni embeddings Java.
- Preservar estado de publicaciones: `UPLOADED`, `PROCESSING`, `COMPLETED`, `ERROR`.
- Tests proporcionales al riesgo antes de tocar contratos compartidos.

## Next Actions

1. Implementar Intent Classifier + Router con reglas baratas y sin LLM.
2. Implementar `search_kb` y `get_query_embedding` con cache LRU.
3. Implementar Generator con prompt de tutor BJJ.
4. Implementar Combined Evaluator con fallback `unverified_response`.
5. Implementar Technique Debugger con gate estricto.
6. Implementar Query Rewriter al final, con un solo retry y maximo 150 caracteres.
7. Exponer `agent_metrics` para evaluacion TFG.
8. Aplicar mejoras de `[[improvements-prompt]]` tras validar AgentGraphService v1.

## Implementation Order

1. Wiki: diseno y gestion TFG.
2. Intent Classifier + Router: reglas baratas primero, sin LLM.
3. `search_kb` + `get_query_embedding` con cache LRU.
4. Generator con prompt de tutor BJJ.
5. Combined Evaluator con fallback si Gemini falla.
6. Technique Debugger con gate estricto.
7. Query Rewriter, solo si los pasos anteriores funcionan.
8. `agent_metrics` para comparar RAG stateless vs RAG agentico.

## Continuity Prompt

```markdown
---
type: handover
project: "bjj-rag-implementation"
date: "2026-04-12"
mode: "Senior Architect"
status: "active"
next_goal: "Implementar Intent Classifier + Router del RAG agentico con reglas baratas y sin LLM."
---

## Handover para la siguiente sesion

Ultima posicion: Diseno del grafo agentico v1 aprobado en `wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md`; gestion TFG iniciada en `wiki/projects/TFG/bjj-app/project/tfg-bjj-app.md`.
Cambios realizados: contexto RAG sincronizado, contratos Java/Python documentados, residuos TFG movidos a backup, protocolo de bootstrap/handover definido, grafo agentico documentado.
Validacion: revisar `wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md`, `wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md`, `wiki/projects/TFG/bjj-app/analyses/bjj-agentic-rag-context.md`, `wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md`, `wiki/projects/TFG/bjj-app/project/tfg-bjj-app.md`.
Bloqueos/riesgos: Python define `visuals` por frame pero Java no lo modela; no existe schema compartido; Query Rewriter debe implementarse al final para no introducir comportamiento inesperado.
Siguiente objetivo: implementar Intent Classifier + Router con reglas baratas y sin LLM.
Contexto que debe leerse: `wiki/index.md`, `wiki/overview.md`, `.jarvis/session_manager.md`, `wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md`, `wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md`.
```
