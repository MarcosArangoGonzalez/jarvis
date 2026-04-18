Analyze and ingest a URL or local file path into the Jarvis wiki.

Run the following command and report the result:

```bash
python3 /home/marcos/jarvis/tools/skills/content_analyzer.py "$ARGUMENTS" --model local
```

Supported types (auto-detected):
- YouTube / YouTube Shorts URL → transcript + analysis
- Instagram reel/post URL → caption + transcript if available
- GitHub repo URL → README + stack + patterns
- Article URL → extracted body + key points
- PDF file path → extracted text + summary
- WhatsApp .txt or .zip export → actions, concepts, questions extracted
- Any local text file

What gets created:
1. `wiki/sources/<slug>.md` — main analysis note (status: NEW)
2. `wiki/tasks/actions-<slug>.md` — action items (chat exports only)
3. `## Where This Applies` section — maps content to active projects with specific suggestions

Options:
- `--model sonnet` — use Claude for higher quality analysis
- `--no-relevance` — skip project mapping (faster)
- `--no-llm` — extract raw content only

After ingesting, show:
- Which note(s) were created
- The summary
- The "Where This Applies" project mappings (if any)
- Next suggested action (run `/validate <note_path>` to verify)
