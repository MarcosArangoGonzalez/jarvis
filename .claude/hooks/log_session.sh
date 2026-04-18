#!/usr/bin/env bash
# Runs on Claude Stop event. Appends session entry to wiki/log.md,
# writes a minimal handover block, and optionally auto-commits.
set -euo pipefail

LOG="$CLAUDE_PROJECT_DIR/wiki/log.md"
SESSION_MGR="$CLAUDE_PROJECT_DIR/.jarvis/session_manager.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# 1. Append to wiki/log.md
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

# 3. Auto-commit wiki/ + .jarvis/ if JARVIS_AUTO_COMMIT=1
if [[ "${JARVIS_AUTO_COMMIT:-0}" == "1" ]]; then
  cd "$CLAUDE_PROJECT_DIR"
  git add wiki/ .jarvis/ 2>/dev/null || true
  git diff --cached --quiet 2>/dev/null || \
    git commit -m "chore: jarvis session $TIMESTAMP" --no-gpg-sign 2>/dev/null || true
fi
