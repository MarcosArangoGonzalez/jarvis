---
title: "BJJ Java Python Contracts"
type: research
status: active
tags:
  - research
  - bjj-app
  - contracts
  - rag
  - java
  - python
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 3500
sources:
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/models/schemas.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/ai-service/routers/rag.py"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/PythonAnalysisRequestDto.java"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/PythonCallbackDto.java"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/DetectedFrameDto.java"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/JointAnglesDto.java"
  - "/home/marcos/Escritorio/TFG/pa/bjj-app/backend/src/main/java/es/udc/bjjapp/backend/rest/controllers/RagController.java"
Summary: "Mapa de contratos Java/Python para bjj-app: request de analisis, webhook de resultados, DTO de frame, angulos articulares y query RAG interna. Punto de control para evitar drift al implementar RAG agentico."
---

# BJJ Java Python Contracts

## Question

Que contratos de datos Java/Python son criticos para el RAG agentico y donde vive hoy la fuente de verdad en codigo.

## Sources

- Python Pydantic: `ai-service/models/schemas.py`.
- Python RAG API interna: `ai-service/routers/rag.py`.
- Java DTOs webhook/analysis: `PythonAnalysisRequestDto.java`, `PythonCallbackDto.java`, `DetectedFrameDto.java`, `JointAnglesDto.java`.
- Java RAG proxy: `RagController.java`.

## Findings

El proyecto no tiene todavia una carpeta compartida de schemas JSON. La fuente de verdad actual esta duplicada entre clases Pydantic en Python y DTOs Java con `@JsonProperty`. Hasta que exista un paquete compartido, esta nota es el mapa operativo para revisar drift de contrato.

## Contract 1: Start Analysis

Direccion: Java backend -> Python ai-service.

Endpoint Python: `POST /api/v1/analyze-video`.

Java source:

- `backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/PythonAnalysisRequestDto.java`

Python source:

- `ai-service/models/schemas.py::AnalysisRequest`

Campos wire-format:

- `publication_id`: string opcional en Python, string en Java.
- `video_url`: string opcional; acepta URL o `local:<filename>`.
- `callback_url`: string opcional; endpoint webhook Java.
- `user_belt`: string opcional, default `white`.
- `auto_tag`: boolean, default `true`.
- `biometric_tracking`: boolean, default `false`.

Regla: Python debe devolver `202` rapidamente y procesar en background. Nunca cambiar a un retorno sincrono como canal principal.

## Contract 2: Analysis Webhook

Direccion: Python ai-service -> Java backend.

Endpoint Java: `POST /api/v1/analysis/webhook`.

Header obligatorio:

- `X-Webhook-Secret`: debe coincidir con `project.ai-service.webhook-secret` / `AI_WEBHOOK_SECRET`.

Java source:

- `backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/PythonCallbackDto.java`

Python source:

- `ai-service/models/schemas.py::WebhookPayload`

Campos wire-format:

- `publication_id`: integer, requerido.
- `status`: string, requerido; valores operativos `completed` o `error`.
- `frames`: lista opcional de `DetectedFrameDto`.
- `error_message`: string opcional.
- `combat_story`: lista opcional. Java la recibe como `List<Map<String, Object>>`, por tanto tolera bloques enriquecidos.
- `primary_detected_class`: string opcional.

Regla: incluso ante error, Python debe enviar webhook con `status=error` para no dejar publicaciones en `PROCESSING`.

## Contract 3: Detected Frame

Java source:

- `backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/DetectedFrameDto.java`

Python source:

- `ai-service/models/schemas.py::DetectedFrameDto`

Campos comunes:

- `frame_index`: integer.
- `timestamp_seconds`: float.
- `detected_class`: string.
- `confidence`: float.
- `joint_angles`: objeto `JointAngles`, opcional.
- `feedback`: string opcional.
- `suggested_tags`: lista opcional de objetos `{tag, confidence}`.
- `player_role`: string opcional.

Observacion de drift: Python tambien define `visuals` en `DetectedFrameDto`, pero Java no lo declara en `DetectedFrameDto`. Si se necesita persistir `visuals` por frame, hay que anadir el campo en Java y su persistencia. Para `combat_story`, Java usa `Map<String,Object>` y puede aceptar `visuals` dentro de cada bloque.

## Contract 4: Joint Angles

Java source:

- `backend/src/main/java/es/udc/bjjapp/backend/rest/dtos/JointAnglesDto.java`

Python source:

- `ai-service/models/schemas.py::JointAngles`

Campos wire-format:

- `left_elbow_angle`
- `right_elbow_angle`
- `left_knee_angle`
- `right_knee_angle`
- `hip_spine_angle`
- `spine_tilt_angle`

Regla: todos son nullable. `null` significa baja confianza/oclusion de keypoints y no debe romper persistencia ni feedback.

## Contract 5: RAG Query

Direccion: frontend -> Java backend -> Python ai-service.

Endpoints:

- Publico autenticado: `POST /api/v1/rag/query`.
- Interno Python: `POST /internal/rag/query`.

Header interno:

- `X-Internal-Secret`.

Java source:

- `backend/src/main/java/es/udc/bjjapp/backend/rest/controllers/RagController.java`

Python source:

- `ai-service/routers/rag.py`

Request:

- `query`: string requerido.
- `filters.category`: string opcional.
- `filters.technique`: string opcional.

Response:

- `answer`: string.
- `sources`: lista con `publication_id`, `title`, `block_index`.

Regla: el endpoint actual es stateless. La memoria conversacional del RAG agentico debe extender este contrato de forma compatible o versionarlo, no romper la UI actual.

## Contract Risks

- Drift entre Pydantic y Java DTOs por campos snake_case nuevos.
- `visuals` existe por frame en Python pero no en Java.
- `combat_story` esta deliberadamente flexible en Java; eso reduce errores de parseo pero exige tests de persistencia.
- `publication_id` sale como string en request Java->Python y como integer en webhook Python->Java.
- `status` del webhook usa string minuscula `completed/error`, no enum Java `COMPLETED/ERROR`.
- Secrets desalineados producen 401 y pueden dejar analisis sin cerrar si el retry/error no esta controlado.

## Next Steps

1. Antes de implementar agentes, decidir si se crea `shared/contracts/` con JSON Schema/OpenAPI parcial o se mantiene esta nota como contrato operativo.
2. Anadir test de contrato para serializar `PythonAnalysisRequestDto` y validarlo contra `AnalysisRequest`.
3. Anadir test de contrato para payload `WebhookPayload` con `combat_story` enriquecido y `feedback=null`.
4. Resolver explicitamente si `visuals` por frame se persiste o se limita a `combat_story`.
