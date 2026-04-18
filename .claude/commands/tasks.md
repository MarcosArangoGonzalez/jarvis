Show active Jarvis tasks filtered by priority.

```bash
grep -r --include="*.md" -i "priority.*p0\|priority.*p1\|- \[ \]" /home/marcos/jarvis/wiki/tasks/ | head -40
```

Also show the tasks index:
```bash
head -60 /home/marcos/jarvis/wiki/tasks/index.md 2>/dev/null
```

Present as two sections:
1. **P0 — Blocking** (must do now)
2. **P1 — High priority** (do next)

If `$ARGUMENTS` is provided, filter tasks by that keyword.
