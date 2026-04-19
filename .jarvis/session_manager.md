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
- Use `tools/skills/morning_coffee.py` as a context adapter, but treat
  `wiki/tasks/index.md` as the priority source of truth.
- Do not mutate project files until the active task is clear and the relevant project log has been read.
- For Codex-style subagents, define role, ownership, expected output, model/effort preference, tone, and token budget before delegation.
- For Claude Code or similar agents, keep the same role definitions and record final handover in the project log.
- Never store secrets in the wiki or session manager.

## Handover 2026-04-18 20:58
- session_end: 2026-04-18T18:58:18Z

## Handover 2026-04-18 20:59
- session_end: 2026-04-18T18:59:54Z

## Handover 2026-04-18 21:02
- session_end: 2026-04-18T19:02:06Z

## Handover 2026-04-18 21:04
- session_end: 2026-04-18T19:04:12Z

## Handover 2026-04-18 21:12
- session_end: 2026-04-18T19:12:01Z

## Handover 2026-04-18 21:36
- session_end: 2026-04-18T19:36:00Z

## Handover 2026-04-18 21:45
- session_end: 2026-04-18T19:45:30Z

## Handover 2026-04-18 21:52
- session_end: 2026-04-18T19:52:30Z

## Handover 2026-04-18 21:53
- session_end: 2026-04-18T19:53:46Z

## Handover 2026-04-18 21:59
- session_end: 2026-04-18T19:59:55Z

## Handover 2026-04-18 22:05
- session_end: 2026-04-18T20:05:21Z

## Handover 2026-04-18 22:17
- session_end: 2026-04-18T20:17:32Z

## Handover 2026-04-18 22:25
- session_end: 2026-04-18T20:25:15Z

## Handover 2026-04-18 22:43
- session_end: 2026-04-18T20:43:05Z

## Handover 2026-04-18 22:43
- session_end: 2026-04-18T20:43:08Z

## Handover 2026-04-18 22:43
- session_end: 2026-04-18T20:43:21Z

## Handover 2026-04-18 22:44
- session_end: 2026-04-18T20:44:02Z

## Handover 2026-04-18 22:44
- session_end: 2026-04-18T20:44:31Z

## Handover 2026-04-18 22:44
- session_end: 2026-04-18T20:44:56Z

## Handover 2026-04-18 22:45
- session_end: 2026-04-18T20:45:25Z

## Handover 2026-04-18 22:45
- session_end: 2026-04-18T20:45:54Z

## Handover 2026-04-18 22:46
- session_end: 2026-04-18T20:46:39Z

## Handover 2026-04-18 22:47
- session_end: 2026-04-18T20:47:06Z

## Handover 2026-04-18 22:47
- session_end: 2026-04-18T20:47:48Z

## Handover 2026-04-18 22:48
- session_end: 2026-04-18T20:48:22Z

## Handover 2026-04-18 22:48
- session_end: 2026-04-18T20:48:50Z

## Handover 2026-04-18 22:49
- session_end: 2026-04-18T20:49:28Z

## Handover 2026-04-18 22:50
- session_end: 2026-04-18T20:50:08Z

## Handover 2026-04-18 22:50
- session_end: 2026-04-18T20:50:44Z

## Handover 2026-04-18 22:50
- session_end: 2026-04-18T20:50:48Z

## Handover 2026-04-18 22:51
- session_end: 2026-04-18T20:51:15Z

## Handover 2026-04-18 22:52
- session_end: 2026-04-18T20:52:01Z

## Handover 2026-04-18 22:52
- session_end: 2026-04-18T20:52:44Z

## Handover 2026-04-18 22:53
- session_end: 2026-04-18T20:53:21Z

## Handover 2026-04-18 22:53
- session_end: 2026-04-18T20:53:24Z

## Handover 2026-04-18 22:53
- session_end: 2026-04-18T20:53:26Z

## Handover 2026-04-18 22:54
- session_end: 2026-04-18T20:54:14Z

## Handover 2026-04-18 22:55
- session_end: 2026-04-18T20:55:21Z

## Handover 2026-04-18 22:56
- session_end: 2026-04-18T20:56:23Z

## Handover 2026-04-18 22:57
- session_end: 2026-04-18T20:57:03Z

## Handover 2026-04-18 22:57
- session_end: 2026-04-18T20:57:44Z

## Handover 2026-04-18 22:58
- session_end: 2026-04-18T20:58:43Z

## Handover 2026-04-18 22:59
- session_end: 2026-04-18T20:59:28Z

## Handover 2026-04-18 22:59
- session_end: 2026-04-18T20:59:59Z

## Handover 2026-04-18 23:00
- session_end: 2026-04-18T21:00:33Z

## Handover 2026-04-18 23:01
- session_end: 2026-04-18T21:01:08Z

## Handover 2026-04-18 23:01
- session_end: 2026-04-18T21:01:59Z

## Handover 2026-04-18 23:02
- session_end: 2026-04-18T21:02:15Z

## Handover 2026-04-18 23:03
- session_end: 2026-04-18T21:03:04Z

## Handover 2026-04-18 23:04
- session_end: 2026-04-18T21:04:09Z

## Handover 2026-04-18 23:04
- session_end: 2026-04-18T21:04:31Z

## Handover 2026-04-18 23:05
- session_end: 2026-04-18T21:05:02Z

## Handover 2026-04-18 23:05
- session_end: 2026-04-18T21:05:30Z

## Handover 2026-04-18 23:06
- session_end: 2026-04-18T21:06:01Z

## Handover 2026-04-18 23:06
- session_end: 2026-04-18T21:06:33Z

## Handover 2026-04-18 23:07
- session_end: 2026-04-18T21:07:12Z

## Handover 2026-04-18 23:07
- session_end: 2026-04-18T21:07:46Z

## Handover 2026-04-18 23:08
- session_end: 2026-04-18T21:08:26Z

## Handover 2026-04-18 23:08
- session_end: 2026-04-18T21:08:50Z

## Handover 2026-04-18 23:09
- session_end: 2026-04-18T21:09:31Z

## Handover 2026-04-18 23:09
- session_end: 2026-04-18T21:09:58Z

## Handover 2026-04-18 23:10
- session_end: 2026-04-18T21:10:42Z

## Handover 2026-04-18 23:11
- session_end: 2026-04-18T21:11:47Z

## Handover 2026-04-18 23:12
- session_end: 2026-04-18T21:12:21Z

## Handover 2026-04-18 23:13
- session_end: 2026-04-18T21:13:14Z

## Handover 2026-04-18 23:13
- session_end: 2026-04-18T21:13:23Z

## Handover 2026-04-18 23:14
- session_end: 2026-04-18T21:14:12Z

## Handover 2026-04-18 23:14
- session_end: 2026-04-18T21:14:14Z

## Handover 2026-04-18 23:14
- session_end: 2026-04-18T21:14:40Z

## Handover 2026-04-18 23:15
- session_end: 2026-04-18T21:15:14Z

## Handover 2026-04-18 23:15
- session_end: 2026-04-18T21:15:16Z

## Handover 2026-04-18 23:16
- session_end: 2026-04-18T21:16:01Z

## Handover 2026-04-18 23:16
- session_end: 2026-04-18T21:16:48Z

## Handover 2026-04-18 23:17
- session_end: 2026-04-18T21:17:33Z

## Handover 2026-04-18 23:18
- session_end: 2026-04-18T21:18:13Z

## Handover 2026-04-18 23:19
- session_end: 2026-04-18T21:19:39Z

## Handover 2026-04-18 23:20
- session_end: 2026-04-18T21:20:31Z

## Handover 2026-04-18 23:21
- session_end: 2026-04-18T21:21:22Z

## Handover 2026-04-18 23:24
- session_end: 2026-04-18T21:24:16Z

## Handover 2026-04-18 23:38
- session_end: 2026-04-18T21:38:46Z

## Handover 2026-04-18 23:39
- session_end: 2026-04-18T21:39:40Z

## Handover 2026-04-18 23:56
- session_end: 2026-04-18T21:56:42Z

## Handover 2026-04-19 00:05
- session_end: 2026-04-18T22:05:55Z

## Handover 2026-04-19 00:15
- session_end: 2026-04-18T22:15:07Z

## Handover 2026-04-19 00:16
- session_end: 2026-04-18T22:16:34Z

## Handover 2026-04-19 12:09
- session_end: 2026-04-19T10:09:58Z

## Handover 2026-04-19 12:12
- session_end: 2026-04-19T10:12:12Z

## Handover 2026-04-19 12:22
- session_end: 2026-04-19T10:22:55Z

## Handover 2026-04-19 12:24
- session_end: 2026-04-19T10:24:52Z

## Handover 2026-04-19 12:27
- session_end: 2026-04-19T10:27:27Z

## Handover 2026-04-19 12:32
- session_end: 2026-04-19T10:32:19Z

## Handover 2026-04-19 19:08
- session_end: 2026-04-19T17:08:14Z

## Handover 2026-04-19 20:57
- session_end: 2026-04-19T18:57:38Z

## Handover 2026-04-19 21:10
- session_end: 2026-04-19T19:10:49Z

## Handover 2026-04-19 21:18
- session_end: 2026-04-19T19:18:51Z

## Handover 2026-04-19 22:07
- session_end: 2026-04-19T20:07:20Z
