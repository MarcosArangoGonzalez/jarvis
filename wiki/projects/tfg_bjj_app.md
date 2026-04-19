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
updated: 2026-04-19
tokens_consumed: 1200
sources:
  - "/home/marcos/Descargas/20260416-Anteproxecto-TFG-MarcosArangoGonzález.pdf"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/memory/tfg.md"
  - "/home/marcos/jarvis/wiki/analyses/bjj_agent_design.md"
  - "/home/marcos/jarvis/wiki/projects/bjj_rag_implementation.md"
  - "/home/marcos/jarvis/wiki/analyses/bjj-agent-knowledge-index.md"
  - "/home/marcos/jarvis/wiki/analyses/plan-assessment.md"
  - "/home/marcos/jarvis/wiki/analyses/rag-patterns.md"
  - "/home/marcos/jarvis/wiki/analyses/agent-langgraph-migration.md"
  - "/home/marcos/jarvis/wiki/analyses/company-vs-tfg-comparison.md"
  - "/home/marcos/jarvis/wiki/analyses/improvements-prompt.md"
Summary: "Indice de gestion del TFG para bjj-app: anteproyecto firmado (15/04/2026), memoria, metodologia, bibliografia, experimentos, decisiones arquitectonicas y pendientes."
---

# TFG BJJ App

## Goal

Gestionar los documentos y decisiones del TFG asociado a `bjj-app`, especialmente la arquitectura del sistema, seguridad de contratos Java/Python, RAG agentico y evaluacion empirica.

## Documents

| Documento | Estado | Ubicacion | Siguiente accion |
|---|---|---|---|
| Anteproyecto | **Entregado** (asinado 15/04/2026) | `/home/marcos/Descargas/20260416-Anteproxecto-TFG-MarcosArangoGonzález.pdf` | — |
| Memoria | Backlog | Pendiente | Sincronizar estructura con `memory/tfg.md`. |
| Bibliografia | Backlog | Pendiente | Consolidar referencias RAG, pgvector, LangChain, HNSW y agentes. |
| Evaluacion empirica | Backlog | Pendiente | Definir tabla RAG stateless vs RAG agentico. |
| Arquitectura AI Agent | Activo | [[bjj-agent-knowledge-index]] | Usar como indice de decisiones y mejoras del AgentGraphService. |

## Anteproyecto — Resumen

- **Título (ES):** Diseño e implementación de una plataforma inteligente de análisis y aprendizaje para Brazilian Jiu-Jitsu
- **Título (EN):** Design and Implementation of an Intelligent Analysis and Learning Platform for Brazilian Jiu-Jitsu
- **Tutor:** Álvarez Díaz, Manuel (manuel.alvarez@udc.es) — FIC, UDC
- **Tipo:** Clásico de enxeñaría · Mención Ingeniería del Software · Propuesta del alumno
- **Firmado:** A Coruña, 15/04/2026

### Objetivo principal
Plataforma web inteligente para análisis, búsqueda y aprendizaje en BJJ, integrando visión artificial, búsqueda semántica y modelos de lenguaje.

### Objetivos concretos
1. Arquitectura backend en capas con Spring Boot (REST, microservicios, escalabilidad).
2. Pipeline de análisis de vídeo: detección de poses por keypoints (YOLOv8-pose), clasificación ML (Random Forest / ViCoS), inferencia geométrica de ángulos.
3. Motor de búsqueda híbrido: relacional por metadatos + semántico vectorial (ChromaDB / pgvector).
4. Sistema RAG agentico como tutor especializado: responde preguntas técnicas, recomienda vídeos, planifica entrenamientos, mejora continua validada por PROFESSOR.
5. Interfaz de usuario: visualización biomecánica sobre vídeo, timeline del combate, consulta al tutor.
6. Seguridad: autenticación y autorización con roles PROFESSOR / USER.
7. Diseño desacoplado para adaptación a otros deportes.
8. Evaluación empírica del pipeline de visión y calidad del feedback del tutor.

### Stack tecnológico
| Capa | Tecnologías |
|---|---|
| Backend | Java, Spring Boot, Hibernate/JPA, Spring Security |
| Base de datos | PostgreSQL + pgvector |
| Servicio IA | Python, FastAPI, YOLOv8-pose, Random Forest (scikit-learn, ViCoS), NumPy, Gemini Vision, ChromaDB |
| Frontend | React, Tailwind CSS, shadcn/ui |
| Despliegue | Docker Compose, webhooks |
| Herramientas | Maven, npm, Git, VS Code |

### Metodología
Desarrollo iterativo e incremental para único desarrollador. Iteraciones de 2-3 semanas con entregable funcional verificable por pruebas de integración.

### Fases
1. Investigación y formación en tecnologías necesarias.
2. Definición de requisitos y diseño de arquitectura.
3. Desarrollo iterativo: Backend → Servicio IA → Frontend → Pruebas → Documentación.
4. Despliegue local y pruebas de integración.

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
- Agentic RAG/CRAG es el patron elegido para tecnica y grounding; GraphRAG y LangGraph quedan documentados como mejoras post-TFG.

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
- Confirmar endpoint Java para `combat_story` antes de cerrar Technique Debugger.

## Next Actions

1. Crear esquema de anteproyecto.
2. Crear indice de memoria.
3. Vincular experimentos con `bjj_agent_design.md`.
4. Definir rubrica de evaluacion de profesor para respuestas y debugger.
