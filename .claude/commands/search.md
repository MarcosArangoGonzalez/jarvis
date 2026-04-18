Search the Jarvis wiki for the given query and return the most relevant notes.

Steps:
1. Search frontmatter Summary fields first (fast):
```bash
grep -r --include="*.md" -i -l "$ARGUMENTS" /home/marcos/jarvis/wiki/
```

2. For each matching file, extract the title and Summary from frontmatter and show them as a ranked list.

3. If fewer than 3 results, also search note bodies:
```bash
grep -r --include="*.md" -i -C 2 "$ARGUMENTS" /home/marcos/jarvis/wiki/
```

Present results as a concise list: `[type] title — Summary` with the file path. Highlight the most relevant match.
