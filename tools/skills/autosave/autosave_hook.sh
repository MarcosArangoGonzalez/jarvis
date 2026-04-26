#!/bin/bash
# Stage any modified tracked file after Claude Code writes it.
# Does NOT commit — commit happens once at session end via log_session.sh.
# Registered as PostToolUse hook (matcher: Write|Edit) in .claude/settings.json.

FILE="${CLAUDE_TOOL_INPUT_FILE_PATH:-$1}"
if [[ -z "$FILE" ]]; then
  exit 0
fi

REPO_ROOT=$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null)
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

cd "$REPO_ROOT" || exit 0
RELATIVE=$(realpath --relative-to="$REPO_ROOT" "$FILE" 2>/dev/null || echo "$FILE")

git add "$RELATIVE" 2>/dev/null || true
