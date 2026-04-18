#!/usr/bin/env bash
# Start Jarvis WhatsApp listener.
# Usage: bash start.sh
# Sessions persist in .wwebjs_auth/ — no re-scan needed after first auth.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JARVIS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Load secrets
if [ -f "$HOME/toolbox/secrets/load-env.sh" ]; then
  source "$HOME/toolbox/secrets/load-env.sh"
fi

export JARVIS_ROOT
cd "$SCRIPT_DIR"

if [ ! -d node_modules ]; then
  echo "Installing dependencies..."
  npm install
fi

exec node listener.js
