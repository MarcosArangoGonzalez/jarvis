---
title: "BJJ Agent Design"
type: research
status: active
tags:
  - research
  - bjj-app
  - rag
  - agentic-rag
  - tfg
  - architecture
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 4500
sources:
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-agentic-rag-context.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md"
  - "/home/marcos/jarvis/wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/services/rag_service.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/services/agent_service.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/routers/rag.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/constants/bjj_logic.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/model/services/TagTaxonomy.java"
Summary: "Diseno v1 del grafo agentico BJJ RAG: Custom Graph Service sin LangGraph, intent classifier, router, retriever, generator, evaluator combinado, debugger tecnico con gate estricto, memoria session_summary, cache LRU de embeddings y metricas TFG."
---

# BJJ Agent Design

## Question

Como convertir el RAG stateless actual de `bjj-app` en un sistema agentico que busque, evalue, dude, corrija y explique tecnica BJJ como profesor, sin romper los contratos Java/Python existentes.

## Decision

La v1 para el TFG sera un `Custom Graph Service` en Python, migrable a LangGraph post-TFG, pero sin anadir `langgraph` como dependencia ahora. El servicio se disena para vivir en `ai-service/services/agent_graph_service.py` y apoyarse en `RagService.query_documents()`, `bjj_logic.py` y el contrato RAG actual.

La primera implementacion posterior a esta nota debe seguir este orden:

1. Wiki: este diseno.
2. Intent Classifier + Router: reglas baratas primero, sin LLM.
3. `search_kb` + `get_query_embedding`: cache LRU.
4. Generator: prompt de tutor BJJ.
5. Combined Evaluator: relevancia + grounding con fallback si Gemini falla.
6. Technique Debugger: con gate estricto.
7. Query Rewriter: al final, porque es el mas propenso a introducir comportamiento inesperado.
8. `agent_metrics`: metricas para TFG y comparacion RAG stateless vs RAG agentico.

## V1 Scope

Incluido:

- Tutor BJJ para preguntas tecnicas.
- Grading de relevancia documental.
- Hallucination/grounding check.
- Depuracion tecnica de video sobre `combat_story + joint_angles`.
- Memoria corta con `session_summary` devuelto por el agente y reenviado por frontend.
- Metricas de evaluacion para memoria TFG.

Excluido en v1:

- Dependencia LangGraph real.
- Memoria persistente en Postgres.
- Perfil de alumno persistente.
- Analisis directo de raw frames en el agente.
- GraphRAG.
- Taxonomia BJJ externa u oficial nueva.

## Graph Nodes

### Intent Classifier

Primero usa reglas baratas; solo llama LLM si hay ambiguedad.

Intenciones v1:

- `technique_question`: "como", "que es", "explica", "ensena".
- `video_debug`: `publication_id` presente, "mi video", "analiza esto".
- `recommendation`: "recomiendame", "que videos", "quiero aprender".
- `training_plan`: "plan", "semana", "entreno", "progreso".
- `insufficient`: query demasiado corta o sin contexto BJJ.

### Router

El router solo enruta; no clasifica.

- `technique_question -> Retriever -> Grader -> Query Rewriter? -> Generator -> Combined Evaluator`.
- `video_debug -> Technique Debugger Gate -> Retriever -> Technique Debugger -> Generator -> Combined Evaluator`.
- `recommendation -> Retriever -> Generator -> Combined Evaluator`.
- `training_plan -> Retriever -> Generator -> Combined Evaluator`.
- `insufficient -> Guarded Fallback`.

Para `recommendation`, el retriever usa filtros por posicion/tecnica cuando existan; el generator usa prompt de recomendacion.

Para `training_plan`, el retriever ejecuta tres queries: posicion base, transicion y sumision; el generator usa prompt de plan de entrenamiento. No se crean nodos nuevos para estos modos en v1.

### Retriever

Usa `RagService.query_documents()` y conserva compatibilidad con Chroma actual.

Prioridad de fuente:

1. `curated=true`.
2. PDF gold-standard / conocimiento semilla validado.
3. Contenido autogenerado por publicaciones.

### Query Rewriter

Solo se ejecuta si el `Grader` falla en el primer intento.

Reglas:

- Un unico retry.
- Solo puede anadir sinonimos BJJ, por ejemplo `rnc -> rear_naked_choke`.
- Solo puede anadir posicion base si no aparece.
- No puede cambiar significado semantico.
- `MAX_REWRITTEN_QUERY_LENGTH = 150`.

### Generator

Redacta como profesor de BJJ:

- Respuesta tecnica.
- Explica por que funciona o no funciona una tecnica/secuencia.
- Si el contexto es parcial, lo dice explicitamente.
- No inventa detalles no recuperados.

### Combined Evaluator

Una sola llamada LLM para dos preguntas:

1. Si los documentos cubren la query.
2. Si la respuesta esta grounded en los documentos y que claims no soportados hay.

Si Gemini falla por 429, timeout o error:

- No bloquear respuesta.
- Devolver `warnings=["unverified_response"]`.
- Usar `confidence=0.5`.

### Technique Debugger

Solo se activa si pasa el gate:

- `publication_id` presente.
- `vectorized=true`.
- `has_combat_story=true`.
- `joint_angles` no vacios.

Si el video existe pero no tiene `combat_story` o `joint_angles`, ir a `Guarded Fallback` con warning especifico. No debe fingir depuracion tecnica sin evidencia.

Salida v1: top 3 correcciones por secuencia, usando tecnica, rol, confianza, `combat_story`, angulos y KB.

### Guarded Fallback

Respuesta limitada cuando falta evidencia o falla una pieza critica:

- Explica que falta.
- No inventa tecnica.
- Sugiere siguiente accion: subir video procesado, anadir filtros, consultar tecnica concreta o esperar vectorizacion.

## Tools

- `search_kb(query, filters)`: wrapper sobre `RagService.query_documents()`.
- `get_query_embedding(query)`: cache LRU de 100 embeddings para reducir latencia en consultas repetidas.
- `validate_bjj_taxonomy(value)`: reutiliza `bjj_logic.py`; Java `TagTaxonomy` queda como contraparte backend. No crear una tercera taxonomia.
- `get_video_context(publication_id)`: obtiene contexto tecnico y valida gate del debugger.
- `check_biomechanics(combat_story, joint_angles)`: devuelve top 3 correcciones por secuencia.
- `evaluate_answer(query, docs, answer)`: relevancia + grounding en una llamada.

Cache propuesta:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_query_embedding(query: str) -> list[float]:
    ...
```

## API Contract

Mantener contrato actual:

```json
{
  "query": "string",
  "filters": {
    "category": "string",
    "technique": "string"
  }
}
```

Extender input de forma compatible con `context` opcional:

```json
{
  "query": "como paso de mount a triangle",
  "filters": {"category": "TRANSITION"},
  "context": {
    "session_summary": "El usuario esta trabajando ataques desde mount.",
    "publication_id": 123
  }
}
```

Mantener response actual:

```json
{
  "answer": "string",
  "sources": []
}
```

Extender response con campos opcionales:

```json
{
  "answer": "string",
  "sources": [],
  "confidence": 0.82,
  "warnings": [],
  "mode": "tutor",
  "session_summary": "Resumen actualizado para el siguiente turno.",
  "agent_metrics": {
    "retrieval_attempts": 1,
    "grader_passed_first_attempt": true,
    "hallucination_detected": false,
    "nodes_visited": ["intent_classifier", "router", "retriever", "generator", "combined_evaluator"],
    "total_llm_calls": 2,
    "latency_ms": 740,
    "embedding_cache_hit": false
  }
}
```

`confidence` representa la confianza global del agente en su respuesta, no la confianza de vision.

`warnings` representa degradaciones o limites: `unverified_response`, `insufficient_context`, `missing_combat_story`, `missing_joint_angles`, `video_not_vectorized`.

`mode` representa el tipo de respuesta: `tutor`, `technique_debug`, `recommendation`, `training_plan`, `insufficient_context`, `fallback`.

`agent_metrics` solo debe exponerse en modo debug/eval o para experimentos TFG.

## Memory V1

El servidor permanece stateless.

Flujo:

1. Frontend envia `context.session_summary` si existe.
2. Agente usa ese resumen como memoria corta.
3. Agente devuelve `session_summary` actualizado.
4. Frontend lo almacena localmente y lo reenvia en el siguiente turno.

No hay persistencia en BD en v1.

## TFG Metrics

Metricas para comparar RAG stateless vs RAG agentico:

- `retrieval_attempts`.
- `grader_passed_first_attempt`.
- `hallucination_detected`.
- `nodes_visited`.
- `total_llm_calls`.
- `latency_ms`.
- `embedding_cache_hit`.

Estas metricas alimentan la evaluacion empirica de la memoria: RAG-05/stateless vs RAG-agentico.

## Implementation Phases

### V1 TFG

- Custom Graph Service.
- Intent Classifier + Router.
- Retriever + cache LRU.
- Generator como tutor BJJ.
- Combined Evaluator con fallback.
- Technique Debugger con gate estricto.
- Query Rewriter acotado y al final.
- `agent_metrics`.

### V2 Post-TFG

- Migracion a LangGraph.
- Memoria persistente en Postgres por usuario.
- Perfil de alumno e historial de debilidades tecnicas.
- Agente para padel con taxonomia adaptada.
- GraphRAG si el dataset supera 50.000 documentos.

## Validation

- La v1 no anade `langgraph`.
- El contrato sigue aceptando `{query, filters} -> {answer, sources}`.
- Todos los campos nuevos son opcionales.
- `Technique Debugger` no se ejecuta sin `vectorized`, `combat_story` y `joint_angles`.
- `recommendation` y `training_plan` no introducen nodos nuevos; solo cambian filtros/prompts.
- Si `Combined Evaluator` falla, la respuesta vuelve con `unverified_response` y `confidence=0.5`.
- `Query Rewriter` queda acotado y no cambia semantica.
- La taxonomia reutiliza `bjj_logic.py` y `TagTaxonomy`, sin tercera copia.

## Next Steps

1. Implementar `Intent Classifier + Router` con reglas baratas.
2. Implementar `search_kb` y cache LRU.
3. Implementar `Generator`.
4. Implementar `Combined Evaluator`.
5. Implementar `Technique Debugger`.
6. Implementar `Query Rewriter`.
7. Exponer `agent_metrics` para evaluacion TFG.
