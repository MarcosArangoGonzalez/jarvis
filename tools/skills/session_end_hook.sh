#!/usr/bin/env bash
# Stop hook: writes a session-end entry to wiki/logs/core/jarvis-log.md and auto-commits wiki changes.
# Called by Claude Code on session stop. Does NOT require conversation context.

JARVIS_DIR="/home/marcos/jarvis"
LOG_FILE="$JARVIS_DIR/wiki/logs/core/jarvis-log.md"
DATE=$(date '+%Y-%m-%d %H:%M')

# Files changed since last commit (excluding noise)
CHANGES=$(git -C "$JARVIS_DIR" diff --name-only HEAD 2>/dev/null \
  | grep -v "node_modules\|\.wwebjs_auth\|__pycache__\|\.pyc" \
  | head -15)

# Untracked files in wiki/ and tools/ (new notes created this session)
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

# Stage and commit wiki/, tools/, .jarvis/ changes (skip raw/ and secrets)
git -C "$JARVIS_DIR" add \
  wiki/ \
  tools/skills/ \
  .jarvis/ \
  CLAUDE.md \
  2>/dev/null

# Only commit if there's something staged
if ! git -C "$JARVIS_DIR" diff --cached --quiet 2>/dev/null; then
  git -C "$JARVIS_DIR" commit -m "chore: auto-commit session end $(date '+%Y-%m-%d %H:%M')

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>" \
  --no-gpg-sign 2>/dev/null
fi
