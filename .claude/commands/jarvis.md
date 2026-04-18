Show all available Jarvis commands and their usage.

List the following commands and their descriptions:

| Command | What it does |
|---|---|
| `/jarvis-ingest <url_or_path>` | Analyze URL or file → wiki note + project relevance mapping |
| `/jarvis-search <query>` | Search wiki summaries and note bodies |
| `/jarvis-validate [note_path\|--scan\|--list-new]` | Validate notes: NEW → VERIFIED, find authoritative sources |
| `/jarvis-lint [--fix]` | Check frontmatter, detect missing Summaries, fix with LLM |
| `/jarvis-tasks [keyword]` | Show P0/P1 active tasks from wiki/tasks/ |
| `/jarvis-backlog [--dry-run\|--limit N]` | Process WhatsApp URL backlog through content analyzer |
| `/jarvis-storage [--clean\|--docker-clean\|--push-image\|--cloud-check]` | Disk, Docker, and cloud storage management |
| `/jarvis-log` | Write a semantic session log entry + handover block to wiki/log.md and session_manager.md |
| `/jarvis-commit [message]` | Stage and commit wiki/ + .jarvis/ + tools/ changes with a safe, reviewed commit |
| `/jarvis-remind [keyword]` | Surface P0/P1 tasks, overdue items, and blocked work; notify-send on P0 |

**Quick examples:**
- `/jarvis-ingest https://youtube.com/watch?v=...` — analyze a YouTube video
- `/jarvis-ingest /path/to/Chat\ de\ WhatsApp.zip` — ingest exported chat → actions + concepts
- `/jarvis-validate --scan --limit 10` — verify 10 unvalidated notes
- `/jarvis-search RAG` — find all notes mentioning RAG
- `/jarvis-lint --fix --model sonnet` — auto-generate missing Summaries

**Jarvis root:** `/home/marcos/jarvis/`
**Wiki:** `wiki/sources/` · `wiki/tasks/` · `wiki/projects/` · `wiki/concepts/` · `wiki/patterns/`
**Skills:** `tools/skills/` — content_analyzer, wiki_validator, relevance_mapper, storage_manager, jarvis_chat, jarvis_llm

Run `ls /home/marcos/jarvis/.claude/commands/` to see project-scoped commands as well.
