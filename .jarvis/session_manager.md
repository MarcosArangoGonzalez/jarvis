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
project logs. In that case, writing to `wiki/log.md` is allowed only for global
Jarvis maintenance.

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
2. Update `wiki/log.md` with one concise global line.
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

Do not create a per-session file in `wiki/logs/` by default. Use the project log
and `wiki/log.md` unless the user explicitly requests a standalone session note.

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
- Do not mutate project files until the active task is clear and the relevant project log has been read.
- For Codex-style subagents, define role, ownership, expected output, model/effort preference, tone, and token budget before delegation.
- For Claude Code or similar agents, keep the same role definitions and record final handover in the project log.
- Never store secrets in the wiki or session manager.
