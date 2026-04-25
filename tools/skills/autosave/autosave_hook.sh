#!/bin/bash
# Auto-commit any modified tracked file after Claude Code writes it.
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

git add "$RELATIVE" 2>/dev/null || exit 0
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "auto: ${TIMESTAMP} — ${RELATIVE}" --no-verify -q 2>/dev/null || true
