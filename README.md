# JarvisOS

Local-first personal operating layer for Marcos Arango. Structured knowledge wiki, task management, content ingestion, voice input, and multi-agent orchestration — running inside Claude Code, Codex, and a local CLI, with all memory in Markdown under `~/jarvis/`.

---

## What it is

- Session bootstrap: load project context, declare mode, roles, and token budget
- Wiki-based long-term memory: sources, projects, tasks, analyses, concepts, entities
- Content ingestion from URLs, PDFs, chats, WhatsApp backlog, and clipboard
- Voice input via whisper.cpp → auto-paste (keyboard shortcut)
- Multi-agent orchestration: Claude Code + Codex + local Ollama models
- Automatic session logging and wiki linting via Claude Code hooks
- MCP integrations: GitHub, Google Drive, Linear, Notion, NotebookLM, Slack

---

## Implementation & Tools

### Architecture

- Memory: Markdown + YAML frontmatter in `wiki/` (token-efficient: read `Summary` first)
- Skills: Python scripts in `tools/skills/` — one file per capability
- Hooks: `.claude/hooks/` — fire on Claude Code `Stop` and `PostToolUse` events
- Slash commands: `.claude/commands/` (project) and `~/.claude/commands/` (global)
- MCP servers: `tools/mcp_servers/mcp_config.json`
- Local models via Ollama; cloud via Anthropic SDK (`jarvis_llm.py`)

### Stack

| Tool | Purpose |
|---|---|
| whisper.cpp (`ggml-base` / `ggml-small`) | Speech-to-text |
| Piper | Text-to-speech |
| Ollama (`phi3:mini`, `llama3.1:8b`) | Local LLM — summaries, lint, batch ops |
| ChromaDB | Vector store (BJJ RAG) |
| FastAPI (`ingest_server.py`) | Local webhook receiver on port 5000 |
| Green API | WhatsApp real-time listener |
| yt-dlp | YouTube / Instagram transcript extraction |
| MCP servers | GitHub, Drive, Linear, Notion, NotebookLM, Slack |
| Codex CLI | Bounded code implementation subagent |
| Claude Code hooks | Automatic log writing, wiki lint on save, auto-commit |

---

## Features & Commands

### Session

```
Jarvis, morning coffee.                  # bootstrap + daily priorities
Jarvis, morning coffee. Focus bjj-app.   # load specific project context
Jarvis, set mode Research Scientist.     # switch to TFG/academic mode
Jarvis, set mode SRE Debug.              # switch to logs/metrics mode
Jarvis, handover.                        # write handover block
/jarvis-log                              # semantic session summary → wiki/logs/core/jarvis-log.md
/jarvis-commit [message]                 # show staged diff → confirm → commit
/jarvis-remind [keyword]                 # surface P0/P1/overdue; notify-send on P0
```

### Tasks

```
/jarvis-tasks [keyword]                         # P0/P1 task list
Jarvis, add task "<desc>" to inbox.             # fast capture
Jarvis, add task "<desc>" to <project>.         # add to project backlog
Jarvis, mark task "<desc>" done.
Jarvis, show tasks for <project>.
```

Priority: **P0** blocks today · **P1** advances main objective · **P2** important · **P3** backlog

### Knowledge & Search

```
/jarvis-search <query>                   # search wiki summaries
Jarvis, what do I know about <topic>?   # local wiki first, MCP only if needed
Jarvis, open <note-filename>.
```

### Ingest

```
/jarvis-ingest <url|path>               # URL or file → wiki note (auto-type)
Jarvis, ingest <URL> as reference.      # → relevant project folder or wiki/sources/
Jarvis, ingest chat <file>.             # exported chat → wiki source note
Jarvis, process ingest queue.           # run sync_watcher on raw/ingest_queue/
/jarvis-backlog [--dry-run|--limit N]   # process WhatsApp URL backlog
```

### Wiki Maintenance

```
/jarvis-lint [--fix]          # validate frontmatter; LLM-fix missing Summaries
/jarvis-validate [note|--scan] # verify notes: NEW → VERIFIED
```

### Voice

```
Super + Shift + V   # toggle record → whisper.cpp → paste (Wayland-first, X11 fallback)
```

| Env var | Effect |
|---|---|
| `JARVIS_VOICE_MODE=fast` | `ggml-base.bin` — low latency (default) |
| `JARVIS_VOICE_MODE=balanced` | `ggml-small.bin` — better quality |
| `JARVIS_VOICE_TYPE=0` | Clipboard only, no auto-paste |
| `JARVIS_VOICE_DURATION=<n>` | Fixed recording window in seconds |

### Multi-Agent

| Agent | Use for | Invoke |
|---|---|---|
| Claude Code | Architecture, planning, contracts, wiki, orchestration | Default |
| Codex | Implement a class, write tests, refactor a file | `/codex:rescue <scoped task>` |
| Local (Ollama) | Summaries, frontmatter, lint, TFG memory drafts | `jarvis --model local` |

Token rule: read `Summary` frontmatter on notes >100 lines before opening body. Delegate implementation to Codex. Log once at session end.

### Storage & CI

```
/jarvis-storage [--clean|--docker-clean]   # disk, Docker, cloud usage
Jarvis, check CI for <owner>/<repo>.       # GitHub Actions via MCP
Jarvis, check alerts.                      # summarise raw/alerts/
```

### IDE Automation (hooks)

Fires automatically on every Claude Code session in this project:

| Hook | Trigger | Effect |
|---|---|---|
| `log_session.sh` | Every turn stop | Timestamp → `wiki/logs/core/jarvis-log.md`, stamp → `session_manager.md` |
| `wiki_lint_check.sh` | `Edit`/`Write` on `wiki/` | Frontmatter warnings in terminal |

```bash
export JARVIS_AUTO_COMMIT=1   # also commit wiki/ + .jarvis/ on every stop
```

Desktop task reminder: `~/.claude/scheduled-tasks/jarvis-tasks/` — runs every 30 min, `notify-send` on P0/P1 (requires Claude Desktop).

---

## Ideas

- Conectar agents y BDs como Obsidian a gafas con IA

---

## Directory Map

| Path | Purpose |
|---|---|
| `.jarvis/session_manager.md` | Bootstrap + handover protocol |
| `CLAUDE.md` | Jarvis control plane |
| `wiki/tasks/` | Task dashboards (index + per-project) |
| `wiki/projects/<area>/<project>/` | Project notes, analyses, tasks, and sources |
| `wiki/logs/core/` | Global operational logs |
| `wiki/logs/projects/` | Centralized logs by project or area |
| `wiki/areas/bjj/learning-videos/` | BJJ sport-learning videos from WhatsApp/social captures |
| `wiki/analyses/` | Global research and design notes not owned by one project |
| `wiki/sources/` | Ingested external content |
| `raw/` | Unprocessed inputs, alerts, backups |
| `tools/skills/` | Local Python skill adapters |
| `.claude/hooks/` | Automatic session hooks |
| `.claude/commands/` | Project-scoped slash commands |
