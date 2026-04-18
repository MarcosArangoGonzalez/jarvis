Validate a Jarvis wiki note against authoritative sources, updating its status (NEW → VERIFIED).

```bash
python3 /home/marcos/jarvis/tools/skills/wiki_validator.py $ARGUMENTS
```

Common usage:
- `/validate wiki/sources/some-note.md` — validate a specific note
- `/validate --scan` — validate all notes with status: NEW or DRAFT
- `/validate --scan --limit 5` — validate next 5 unverified notes
- `/validate --list-new` — list all notes still at status: NEW
- `/validate --list-status PROCESSING` — list notes stuck in PROCESSING
- `/validate --model sonnet wiki/sources/note.md` — use Claude for better source search

Status lifecycle:
  NEW → just ingested, unreviewed
  PROCESSING → validator working on it
  VERIFIED → confirmed against authoritative source
  STALE → content may be outdated

After running, report: which notes were validated, what authoritative sources were found, and how many moved from NEW to VERIFIED.
