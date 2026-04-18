Run the Jarvis wiki linter to find frontmatter issues, missing summaries, and duplicate sources.

```bash
python3 /home/marcos/jarvis/tools/skills/wiki_lint.py $ARGUMENTS
```

If `$ARGUMENTS` contains `--fix`, the linter will auto-generate missing Summaries using the local LLM.

Common usage:
- `/lint` — check only, no changes
- `/lint --fix` — auto-fix missing Summaries with local model
- `/lint --fix --model sonnet` — use Claude Sonnet for better summaries
- `/lint --code EMPTY_SUMMARY` — show only notes missing a Summary

After running, summarize: how many notes checked, issues found by category, and how many were fixed.
