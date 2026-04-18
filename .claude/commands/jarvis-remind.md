Check active Jarvis tasks and surface anything urgent.

1. Read `wiki/tasks/index.md` and all files it references under `wiki/tasks/projects/`.
2. Identify tasks that are:
   - Priority P0 or P1
   - Due today or overdue (today: use current date)
   - Blocked and waiting on an external dependency
3. Output a compact table:

| Priority | Project | Task | Due | Status |
|----------|---------|------|-----|--------|

4. If $ARGUMENTS is provided, filter to tasks matching that keyword.
5. If any P0 tasks exist, run: `notify-send "Jarvis P0 Alert" "<task title>"` via Bash.
6. Suggest the single most actionable next step.
