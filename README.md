# JarvisOS

JarvisOS is a local-first operating layer for Marcos Arango: project memory,
task planning, ingestion, research notes, voice tooling, and agent handover
protocols.

## Daily Start

Use the shortest prompt:

```text
Jarvis, morning coffee.
```

This means:

1. Read `.jarvis/session_manager.md`.
2. Read `wiki/tasks/index.md`.
3. Review P0/P1 tasks and active project logs.
4. Produce a daily priority report.
5. Ask what to add, remove, reorder, or plan.
6. Configure the session mode, roles, subagents, language, verbosity, and token budget.

For direct BJJ RAG work from the `bjj-app` repo:

```text
Jarvis, morning coffee. Focus bjj-app.
```

## Directory Map

- `.jarvis/session_manager.md`: canonical bootstrap and handover protocol.
- `CLAUDE.md`: Jarvis control plane and pointer to the session manager.
- `.claude.md`: persistent user profile and preferences.
- `wiki/`: curated memory.
- `wiki/tasks/`: global and project task dashboards.
- `wiki/projects/`: project logs and project-level memory.
- `wiki/analyses/`: research/design notes.
- `raw/`: unprocessed inputs and backups.
- `templates/`: frontmatter templates.
- `tools/skills/`: local executable adapters.
- `tools/local/`: local binaries/models/virtualenvs used by skills.

## Task System

Tasks are split by purpose:

- `wiki/tasks/index.md`: daily dashboard and cross-project priorities.
- `wiki/tasks/inbox.md`: fast capture before classification.
- `wiki/tasks/projects/*.md`: project-specific backlogs.
- `wiki/tasks/areas/*.md`: non-project life areas.

Priority rules:

- P0: blocks today's work or a critical failure.
- P1: advances the main active objective.
- P2: important but not blocking.
- P3: backlog or future improvement.

Do not create new task folders casually. If a project or area does not fit the
existing structure, ask before creating a new file.

## Session Modes

Default mode is `Senior Architect`.

- `Senior Architect`: design, contracts, modularity, security, trade-offs.
- `Research Scientist`: TFG, sources, methodology, reproducibility.
- `SRE Debug`: logs, failures, metrics, quota, runtime stability.

Each session should declare:

- project
- mission
- mode
- primary role
- supporting roles/subagents
- token/verbosity constraints

## Voice Roadmap

The target workflow is invisible voice input:

```text
keyboard shortcut -> record -> transcribe -> optionally refine -> paste into focused app
```

Current state:

- `tools/skills/voice_bridge.py` supports `check`, `notify`, `speak`, `transcribe <audio>`, and `listen`.
- Legacy invocation also works: `voice_bridge.py --listen --duration 8 --language es --type`.
- `tools/skills/jarvis_voice_flow.sh` wraps the default dictation flow for an Ubuntu keyboard shortcut.
- Piper and whisper.cpp runtime assets exist under `tools/local/`.
- The workstation is currently on Wayland, so paste is Wayland-first with X11 fallback.

Default usage:

```bash
/home/marcos/jarvis/tools/skills/jarvis_voice_flow.sh
```

Recommended next configuration:

1. Bind the wrapper to an Ubuntu custom keyboard shortcut.
2. Ensure Wayland paste works by running `ydotoold` or installing `wtype`.
3. If refinement is needed, install an Ollama model and set `JARVIS_VOICE_REFINE=1` plus `JARVIS_VOICE_REFINE_MODEL=<model>`.
4. Optionally compare against OpenWhispr later if the custom flow is not smooth enough.

## Handover

At the end of substantial work:

1. Update the relevant project log.
2. Update `wiki/log.md`.
3. Update any durable analysis note if new constraints were discovered.
4. Produce a handover prompt with YAML frontmatter.

See `.jarvis/session_manager.md` for the exact handover block.
