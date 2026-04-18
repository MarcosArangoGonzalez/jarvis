#!/usr/bin/env bash
# Runs after Write or Edit tool calls. Lints the file if it's under wiki/.
# Reads tool input JSON from stdin.
set -uo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || echo "")

# Only lint files inside the wiki/ directory
if [[ "$FILE_PATH" != *"/wiki/"* ]]; then
  exit 0
fi

VENV="$CLAUDE_PROJECT_DIR/.venv/bin/python3"
PYTHON="${VENV:-python3}"
if [[ ! -x "$VENV" ]]; then
  PYTHON="python3"
fi

OUTPUT=$("$PYTHON" "$CLAUDE_PROJECT_DIR/tools/skills/wiki_lint.py" --path "$CLAUDE_PROJECT_DIR/wiki" 2>&1 | grep -F "$(basename "$FILE_PATH")" || true)

if [[ -n "$OUTPUT" ]]; then
  echo "[wiki-lint] $OUTPUT" >&2
fi

exit 0
