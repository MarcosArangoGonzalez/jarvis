Stage and commit all Jarvis wiki and config changes.

1. Run `git -C /home/marcos/jarvis status --short` to show what's changed.
2. If there is nothing to commit, report "Nothing to commit" and stop.
3. If there are changes, ask the user to confirm with a one-line commit message, or use the argument provided: $ARGUMENTS
   - If no argument and no confirmation needed, default to: `chore: jarvis session YYYY-MM-DD`
4. Stage only safe paths: `git -C /home/marcos/jarvis add wiki/ .jarvis/ tools/skills/ .claude/`
5. Run `git -C /home/marcos/jarvis commit -m "<message>"`
6. Show the resulting `git log --oneline -3`.

Never stage: `.env`, `keys.json`, `raw/`, secrets, or anything in `.gitignore`.
