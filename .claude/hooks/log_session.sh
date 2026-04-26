#!/usr/bin/env bash
# Runs on Claude Stop event. Appends session entry to wiki/logs/core/jarvis-log.md,
# writes a minimal handover block, and optionally auto-commits.
set -euo pipefail

LOG="$CLAUDE_PROJECT_DIR/wiki/logs/core/jarvis-log.md"
SESSION_MGR="$CLAUDE_PROJECT_DIR/.jarvis/session_manager.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# 1. Append to wiki/logs/core/jarvis-log.md
cat >> "$LOG" << EOF

## $TIMESTAMP — session end
EOF

# 2. Append minimal handover stamp to session_manager.md
if [[ -f "$SESSION_MGR" ]]; then
  cat >> "$SESSION_MGR" << EOF

## Handover $TIMESTAMP
- session_end: $ISO
EOF
fi

# 3. Commit all staged changes (accumulated by autosave_hook.sh) + wiki/ + .jarvis/
# autosave_hook.sh stages individual files on each Write/Edit but does NOT commit,
# so the history stays clean — one commit per session end rather than one per file.
cd "$CLAUDE_PROJECT_DIR"
git add wiki/ .jarvis/ 2>/dev/null || true
git diff --cached --quiet 2>/dev/null || \
  git commit -m "chore: auto-commit session end $TIMESTAMP" --no-verify -q 2>/dev/null || true
