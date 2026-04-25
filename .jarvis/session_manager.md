# JarvisOS Session Manager

This file is the canonical session protocol for agents working inside `~/jarvis`
or on projects connected to the Jarvis wiki. It is tool-agnostic: Codex, Claude
Code, and future agents follow the same rules unless a tool note says otherwise.

## Active Session Config

- Mission: Configure JarvisOS session bootstrap, progress tracking, logs, and handover protocol before continuing `bjj-app`.
- Default work mode: Senior Architect.
- Active project resolution: infer from the execution path. For `/home/marcos/Escritorio/TFG/pa/bjj-app`, use `wiki/projects/bjj_rag_implementation.md`.
- Primary role: Senior Architect.
- Supporting roles available at session start:
  - Contract Guardian: checks API/schema drift, security headers, and compatibility.
  - Research Curator: updates analysis notes only when new constraints or evidence appear.
  - SRE Debugger: focuses on logs, runtime health, reproducibility, and failure modes.
  - Implementation Worker: applies scoped code changes only after the session goal is clear.
- Model guidance: use the strongest coding/architecture model available for design and contract work; use smaller/cheaper subagents only for bounded, parallel, non-blocking subtasks.
- Language: technical engineering Spanish by default; preserve code identifiers and API terms in English.
- Verbosity: concise by default. Prefer decisions, checklists, diffs, and diagrams over broad prose.
- Token efficiency: read frontmatter `Summary` first for notes over 100 lines; read bodies only when the summary is insufficient.

## Bootstrap Protocol

At the beginning of every session:

1. Read `wiki/index.md` and `wiki/overview.md`.
2. Infer the active project from the current path.
3. Read the active project log frontmatter and its current status section. For `bjj-app`, read `wiki/projects/bjj_rag_implementation.md`.
4. Read related analysis frontmatter from the project `sources`; open full bodies only if needed.
5. Declare the session configuration in the chat:
   - project
   - mission
   - primary role
   - supporting roles/subagents, if any
   - mode profile
   - context loaded
6. Open with this shape:

```text
Contexto cargado. Ultima sesion: [summary]. Objetivo de hoy: [goal].
Modo: [profile]. Rol principal: [role]. Roles de apoyo: [roles].
```

If the current path does not map clearly to a project note, ask before writing
project logs. In that case, writing to `wiki/logs/core/jarvis-log.md` is allowed only for global
Jarvis maintenance.

## Morning Coffee

Short prompt:

```text
Jarvis, morning coffee.
```

Meaning:

1. Read this file.
2. Read `wiki/tasks/index.md`.
3. Read only the active project logs needed for P0/P1 tasks.
4. Produce a daily priority report:
   - top 3 tasks
   - blockers
   - recommended session target
   - suggested mode
   - primary role
   - supporting roles/subagents
5. Ask what to add, remove, reorder, or plan.
6. Prepare the selected task in Plan Mode before implementation when the environment supports it.

If the user says `Jarvis, morning coffee. Focus <project>`, prioritize the task
file under `wiki/tasks/projects/` that matches `<project>`.

## Work Mode Profiles

### Senior Architect

- Use for system design, contracts, security boundaries, migrations, modularity, and trade-offs.
- Tone: concise, technical, decision-oriented.
- Expected output: implementation plan, interface decisions, risk list, acceptance criteria.
- Token policy: summarize long context; inspect exact code only around boundaries being changed.
- Supporting roles: Contract Guardian and Implementation Worker.

### Research Scientist

- Use for TFG, methodology, comparisons, source evaluation, and reproducibility.
- Tone: formal, source-aware, careful with claims.
- Expected output: research notes, citations, confidence levels, methodology and limitations.
- Token policy: prioritize frontmatter and source summaries; expand only for evidence.
- Supporting roles: Research Curator and Contract Guardian.

### SRE Debug

- Use for broken pipelines, service health, logs, quota, secrets, and runtime failures.
- Tone: very concise, metrics/logs first.
- Expected output: symptom, likely cause, command trail, fix, verification.
- Token policy: avoid broad context; read logs/configs closest to failure first.
- Supporting roles: SRE Debugger and Contract Guardian.

## Handover Protocol

At the end of every substantial session:

1. Update the active project log with:
   - date
   - technical changes or decisions
   - files or notes touched
   - verification performed
   - remaining blockers
2. Update `wiki/logs/core/jarvis-log.md` with one concise global line.
3. If a new durable constraint was discovered, update the relevant note in `wiki/analyses/`.
4. Update the feature progress table in the active project log. Percentages are directional only; always include a natural-language conclusion.
5. Produce a handover prompt with YAML frontmatter and a structured body.

Use this handover block:

```markdown
---
type: handover
project: "<project>"
date: "YYYY-MM-DD"
mode: "<mode>"
status: "<active|blocked|done>"
next_goal: "<one sentence>"
---

## Handover para la siguiente sesion

Ultima posicion:
Cambios realizados:
Validacion:
Bloqueos/riesgos:
Siguiente objetivo:
Contexto que debe leerse:
```

Do not create a per-session file in `wiki/logs/` by default. Use the global log
in `wiki/logs/core/jarvis-log.md` and project logs in `wiki/logs/projects/`
unless the user explicitly requests a standalone session note.

## Feature Progress Table

Project logs should maintain this table when the project has multiple active
features:

```markdown
| Feature | Status | Progreso | Ultima modificacion | Conclusion | Siguiente accion |
|---|---|---:|---|---|---|
| Example | Backlog | 0% | - | No iniciado. | Definir alcance. |
```

Allowed status values:

- Done
- WIP
- Backlog
- Blocked
- Deferred

Percentages are rough indicators, not delivery guarantees. The `Conclusion`
column is mandatory because it carries the real progress signal.

## Tool Notes

- Prefer local Jarvis wiki context before external tools.
- Use `tools/skills/morning_coffee.py` as a context adapter, but treat
  `wiki/tasks/index.md` as the priority source of truth.
- Do not mutate project files until the active task is clear and the relevant project log has been read.
- For Codex-style subagents, define role, ownership, expected output, model/effort preference, tone, and token budget before delegation.
- For Claude Code or similar agents, keep the same role definitions and record final handover in the project log.
- Never store secrets in the wiki or session manager.

## Handover 2026-04-20 — Phase 5D Complete

---
type: handover
project: "bjj-rag-implementation"
date: "2026-04-20"
mode: "Senior Architect"
status: "active"
next_goal: "Actualizar RagController.java para reenviar session_summary, publication_id y debug al ai-service."
---

## Handover para la siguiente sesion

Ultima posicion: Phase 5D completada — AgentGraphService integrado en FastAPI, 27 tests pasan, pipeline classifier→retriever→generator validado hasta quota Gemini.

Cambios realizados:
- `services/agent_graph_service.py`: `_fetch_publication_for_debugger`, `_java_base_url`, confidence fix (0.5/0.0), auto-fetch publication cuando intent=video_debug.
- `routers/rag.py`: `RagQueryRequest` extendido con `session_summary`, `publication_id`, `debug`; `RagQueryResponse` con `confidence`, `warnings`, `mode`, `session_summary`, `agent_metrics`.
- `main.py`: `AgentGraphService` inicializado en lifespan tras `RagService`.
- `config.py`: campos `python_parity_mode`, `spring_poc_enabled`, `spring_poc_base_url`, `poc_python_dir` añadidos; modelo por defecto → `gemini-2.0-flash`.
- `services/rag_service.py`: fallback a búsqueda sin filtro cuando `document_type=master` devuelve 0 resultados.
- `tests/test_agent_graph_service.py`: 27 tests nuevos — todos pasan.
- `frontend/src/app/(main)/page.tsx`: `showVideoThumb` evita error MIME en publicaciones `local:`.
- `.env`: `HOST_VIDEOS_DIR` apunta a ruta correcta de videos.

Validacion: 27 tests unitarios OK. E2E pipeline OK hasta generator — bloqueado por quota Gemini free tier (reset diario).

Bloqueos/riesgos:
- Quota Gemini agotada — reset diario; alternativa: habilitar billing.
- `RagController.java` todavía no reenvía `session_summary`/`publication_id`/`debug` al ai-service — bloquea uso agentico desde frontend.
- Frontend `/rag` no almacena ni reenvía `session_summary` — memoria conversacional inactiva.

Siguiente objetivo: actualizar `RagController.java` — añadir los 3 campos opcionales al DTO y propagarlos en el proxy. Cambio pequeño, desbloquea todo el camino crítico.

Contexto que debe leerse:
- `wiki/projects/TFG/bjj-app/project/bjj-rag-implementation.md`
- `wiki/projects/TFG/bjj-app/analyses/bjj-agent-design.md`
- `wiki/projects/TFG/bjj-app/analyses/bjj-java-python-contracts.md`
- `.jarvis/session_manager.md`

## Handover 2026-04-20 11:04
- session_end: 2026-04-20T09:04:01Z

## Handover 2026-04-20 11:05
- session_end: 2026-04-20T09:05:11Z

## Handover 2026-04-20 17:15
- session_end: 2026-04-20T15:15:46Z

## Handover 2026-04-20 22:24
- session_end: 2026-04-20T20:24:08Z

## Handover 2026-04-21 11:35
- session_end: 2026-04-21T09:35:06Z

## Handover 2026-04-21 11:58
- session_end: 2026-04-21T09:58:13Z

## Handover 2026-04-21 14:29
- session_end: 2026-04-21T12:29:40Z

## Handover 2026-04-21 14:32
- session_end: 2026-04-21T12:32:38Z

## Handover 2026-04-21 15:49
- session_end: 2026-04-21T13:49:15Z

## Handover 2026-04-21 16:38
- session_end: 2026-04-21T14:38:35Z

## Handover 2026-04-21 16:39
- session_end: 2026-04-21T14:39:20Z

## Handover 2026-04-21 16:50
- session_end: 2026-04-21T14:50:28Z

## Handover 2026-04-21 16:53
- session_end: 2026-04-21T14:53:14Z

## Handover 2026-04-21 16:57
- session_end: 2026-04-21T14:57:34Z

## Handover 2026-04-21 17:06
- session_end: 2026-04-21T15:06:45Z

## Handover 2026-04-21 17:30
- session_end: 2026-04-21T15:30:14Z

## Handover 2026-04-23 16:18
- session_end: 2026-04-23T14:18:12Z

## Handover 2026-04-23 16:48
- session_end: 2026-04-23T14:48:31Z

## Handover 2026-04-23 18:38
- session_end: 2026-04-23T16:38:38Z

## Handover 2026-04-23 18:54
- session_end: 2026-04-23T16:54:18Z

## Handover 2026-04-23 18:55
- session_end: 2026-04-23T16:55:48Z

## Handover 2026-04-23 19:10
- session_end: 2026-04-23T17:10:49Z

## Handover 2026-04-23 19:39
- session_end: 2026-04-23T17:39:47Z

## Handover 2026-04-24 20:58
- session_end: 2026-04-24T18:58:18Z

## Handover 2026-04-24 21:35
- session_end: 2026-04-24T19:35:45Z

## Handover 2026-04-25 23:17
- session_end: 2026-04-25T21:17:50Z

## Handover 2026-04-25 23:28
- session_end: 2026-04-25T21:28:20Z
