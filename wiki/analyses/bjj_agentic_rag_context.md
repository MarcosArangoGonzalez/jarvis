---
title: "BJJ Agentic RAG Context"
type: research
status: active
tags:
  - research
  - bjj-app
  - rag
  - agentic-rag
  - tfg
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 12000
sources:
  - "/home/marcos/jarvis/CLAUDE.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/CLAUDE.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/SESSION_CONTEXT.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/SESSION_SUMMARY.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/context/python.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/context/java.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5B.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5C.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5C-refinement.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/phases/5D.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/GUIA_CONEXION_NUEVO_AI_SERVICE.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/services/rag_service.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/services/agent_service.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/routers/rag.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/controllers/RagController.java"
  - "/home/marcos/jarvis/wiki/analyses/bjj_java_python_contracts.md"
Summary: "Contexto sincronizado para disenar el RAG agentico de bjj-app: estado actual del pipeline Python/Spring, contratos de seguridad y datos, estado del RAG stateless, restricciones de modularidad y objetivos pendientes para agentes, memoria conversacional, retrieval y validacion."
---

# BJJ Agentic RAG Context

## Question

Que estado real tiene hoy el RAG de `bjj-app`, que objetivos tecnicos siguen pendientes y que reglas de desarrollo deben gobernar el diseno de los agentes.

## Sources

- Jarvis control plane: `CLAUDE.md` exige local-first, notas con frontmatter, fuentes trazables, secrets fuera del repo y uso de memoria local antes de herramientas externas.
- Proyecto `bjj-app`: `CLAUDE.md`, `SESSION_CONTEXT.md`, `SESSION_SUMMARY.md`, `context/java.md`, `context/python.md`, `phases/5B.md`, `phases/5C.md`, `phases/5C-refinement.md`, `phases/5D.md`, `GUIA_CONEXION_NUEVO_AI_SERVICE.md`.
- Codigo actual: `ai-service/services/rag_service.py`, `ai-service/services/agent_service.py`, `ai-service/routers/rag.py`, `backend/rest/controllers/RagController.java`, `frontend/src/app/rag/page.tsx`.

## Findings

El sistema actual ya tiene una base RAG operativa, pero no es todavia un RAG conversacional agentico. La pantalla `/rag` se define explicitamente como "Stateless RAG": cada pregunta se resuelve de forma independiente contra documentos indexados, sin memoria conversacional ni planificacion multi-paso.

La arquitectura actual separa responsabilidades correctamente: Java gestiona autenticacion, REST, estados, persistencia y webhook; Python gestiona vision, RAG, agente, flywheel y LLM. El canal de retorno obligatorio es unico: webhook `POST /api/v1/analysis/webhook` con `X-Webhook-Secret`. No debe anadirse otro canal paralelo de callback.

El flujo de RAG de consulta ya existe: frontend llama `POST /api/v1/rag/query`; Spring `RagController` proxya a `ai-service` en `/internal/rag/query` con `X-Internal-Secret`; Python valida el secreto, consulta ChromaDB y genera respuesta con Gemini si hay clave disponible, o usa fallback determinista si falla el LLM.

`RagService` usa ChromaDB persistente y embeddings `sentence-transformers/all-MiniLM-L6-v2` con 384 dimensiones. Esta decision es critica porque debe mantenerse alineada con pgvector/Java. El servicio indexa un documento master por publicacion y documentos por bloque `combat_story`, con metadatos como `publication_id`, `title`, `category`, `technique`, `block_index`, `curated`, `duration` y `start_timestamp`.

`AgentService` actual es un agente LangChain de feedback biomecanico por frame con Gemini y dos herramientas: `search_bjj_theory` y `check_angle_safety`. La regla de resiliencia ya esta clara: si falla LLM, herramienta o parsing, devuelve `None` y el pipeline continua. Tambien existe fallback heuristico en espanol y una funcion `infer_technique_tags` para validar senales Roboflow/RF/geometria.

Las fases historicas indican una evolucion: Phase 5B planteaba skills desacopladas; el codigo actual no tiene todavia el directorio `services/skills/` propuesto, sino un `AgentService` centralizado con tools. Phase 5C amplio el pipeline hacia RF, Gemini Vision, Chroma real, flywheel y endpoints internos. Phase 5C-refinement priorizo precision: confidence gate, subclasificacion heuristica, estabilidad temporal, `combat_story` y logs mas limpios. Phase 5D queda como fase de tests end-to-end y experimento RAG vs Long-Context para la memoria del TFG.

El conocimiento RAG ya puede alimentarse desde publicaciones completadas. `scripts/backfill_publications.py` consume `/api/v1/publications/completed-for-rag`, indexa master + bloques en Chroma y marca la publicacion como vectorizada. La migracion `6-AddCuratedFlagMigration.sql` anade `curated`, senal de que el siguiente paso debe ponderar conocimiento validado/profesor frente a contenido autogenerado.

Las sesiones documentadas de Claude Code muestran problemas resueltos y restricciones que no deben repetirse: secretos de webhook desalineados, Gemini sin cuota, modelos inexistentes, settings de motor ignorados, campos inexistentes como `position_base`, `combat_story` como JSON, y tags sugeridos que no llegaban o no eran buscables. No se encontro una transcripcion local de Codex con contenido comparable; `.codex` existe como fichero vacio y el contexto util proviene de notas de sesion, fases y codigo.

Los contratos Java/Python quedan documentados en `wiki/analyses/bjj_java_python_contracts.md`. Hasta que exista una carpeta compartida de schemas, la fuente real esta duplicada entre Pydantic y DTOs Java. Riesgo concreto: Python define `visuals` en el DTO de frame, pero Java no lo modela en `DetectedFrameDto`; `combat_story` si acepta bloques enriquecidos porque Java lo recibe como `List<Map<String,Object>>`.

## Technical Objectives

- Convertir el RAG stateless en una capa agentica con memoria corta entre turnos, sin romper el endpoint actual.
- Mantener el retrieval como base: master documents + `combat_story` blocks + filtros por `category`/`technique`.
- Separar capacidades: tutor RAG conversacional, correccion tecnica desde video, seguridad biomecanica, planificacion de transiciones y explicacion por nivel de cinturon.
- Reintroducir o formalizar skills modulares si aportan claridad: tono, identificacion posicional, diagnostico de submission, recomendacion defensiva, planificacion de transiciones.
- Definir contratos `AgentInput`/`AgentOutput` estables para evitar que cada capa pase diccionarios ad hoc.
- Decidir si se crea `shared/contracts/` con JSON Schema/OpenAPI parcial o si la Wiki versionada sera el contrato operativo durante la implementacion.
- Integrar memoria conversacional limitada y trazable: historial corto, resumen de sesion y fuentes recuperadas, sin persistir secretos ni datos innecesarios.
- Mejorar retrieval: priorizar `curated=true`, soportar filtros robustos, exponer fuentes, y evitar respuestas con confianza excesiva si el contexto es parcial.
- Mantener fallback determinista cuando Gemini no tenga cuota o falle, para que el pipeline y la UI sigan funcionando.
- Cubrir con tests: RAG retrieval nunca lanza, agente devuelve `None`/heuristica en fallo, webhook rechaza secretos incorrectos, endpoint `/rag/query` maneja caidas del ai-service.

## Constraints

- Webhook siempre protegido por `X-Webhook-Secret`; endpoints internos por `X-Internal-Secret`.
- `startAnalysis()` debe respetar maquina de estados; no dejar publicaciones en `PROCESSING` sin webhook final.
- Python no debe hardcodear secrets; usar settings/env.
- LLM/RAG no puede romper analisis de video: `feedback=null` o heuristico y continuar.
- Java conserva estado y persistencia; Python conserva LLM, embeddings y RAG.
- Embeddings deben seguir en 384 dimensiones con `all-MiniLM-L6-v2` salvo migracion coordinada.
- No reintroducir LangChain4j/embeddings en Java: esa responsabilidad fue eliminada en Phase 5A.

## Confidence

Alta para el estado de arquitectura y contratos porque estan respaldados por codigo actual y documentos de sesion. Media para la completitud historica de sesiones Codex porque solo se encontro `.codex` vacio; la evidencia fuerte local corresponde a Claude Code, notas de fase y commits.

## Next Steps

1. Disenar el modelo de agentes sobre `RagService` y `AgentService` sin cambiar el contrato externo.
2. Definir `AgentInput`, `AgentOutput`, memoria corta y politica de fuentes.
3. Decidir si las skills de Phase 5B se implementan como clases separadas o como tools especializadas del agente.
4. Crear pruebas de regresion antes de tocar el flujo de webhook/RAG.
5. Actualizar el log de proyecto en Jarvis con hitos y decisiones a medida que avance la implementacion.
