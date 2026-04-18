Process the WhatsApp URL backlog through the Jarvis content analyzer.

```bash
python3 /home/marcos/jarvis/tools/skills/process_whatsapp_backlog.py $ARGUMENTS
```

Common usage:
- `/backlog --dry-run` — show pending URLs without processing
- `/backlog --limit 10` — process next 10 URLs
- `/backlog --limit 10 --model local:llama3.1` — use llama3.1 for better analysis
- `/backlog` — process all remaining URLs (can take a long time)

The job is resumable: progress is saved to `raw/backlog_progress.json` after each URL.

After running, report: how many processed, how many failed, and total remaining.
