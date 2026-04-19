#!/usr/bin/env bash
# Stop hook: writes a session-end entry to wiki/log.md with git-derived context.
# Called by Claude Code on session stop. Does NOT require conversation context.

JARVIS_DIR="/home/marcos/jarvis"
LOG_FILE="$JARVIS_DIR/wiki/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')

# Files changed since last commit (excluding noise)
CHANGES=$(git -C "$JARVIS_DIR" diff --name-only HEAD 2>/dev/null \
  | grep -v "node_modules\|\.wwebjs_auth\|__pycache__\|\.pyc" \
  | head -15)

# Also include untracked files in wiki/ and tools/ (new notes created this session)
UNTRACKED=$(git -C "$JARVIS_DIR" ls-files --others --exclude-standard 2>/dev/null \
  | grep -E "^(wiki|tools|\.jarvis)/" \
  | grep -v "node_modules\|__pycache__" \
  | head -10)

ALL_FILES=$(printf "%s\n%s" "$CHANGES" "$UNTRACKED" | grep -v "^$" | sort -u)

if [ -z "$ALL_FILES" ]; then
  exit 0
fi

FILE_BULLETS=$(echo "$ALL_FILES" | sed 's/^/  - /')

ENTRY="
## $DATE — session end (auto)

- Archivos modificados o creados en esta sesión:
$FILE_BULLETS
"

printf "%s\n" "$ENTRY" >> "$LOG_FILE"
