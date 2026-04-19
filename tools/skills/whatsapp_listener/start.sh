#!/usr/bin/env bash
# Start Jarvis WhatsApp listener.
# Usage: bash start.sh
# Sessions persist in .wwebjs_auth/ — no re-scan needed after first auth.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JARVIS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Load secrets
if [ -f "$HOME/toolbox/secrets/load-env.sh" ]; then
  set +e
  source "$HOME/toolbox/secrets/load-env.sh"
  set -e
fi

if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  set +e
  source "$SCRIPT_DIR/.env"
  set -e
  set +a
fi

if [ -z "${JARVIS_WHATSAPP_CHAT_ID:-}" ] && [ "${JARVIS_WHATSAPP_ALLOW_ALL_CHATS:-0}" != "1" ]; then
  echo "JARVIS_WHATSAPP_CHAT_ID is not set. Refusing to process all WhatsApp chats." >&2
  echo "Set it in $SCRIPT_DIR/.env or export JARVIS_WHATSAPP_ALLOW_ALL_CHATS=1." >&2
  exit 2
fi

export JARVIS_ROOT
cd "$SCRIPT_DIR"
mkdir -p "$JARVIS_ROOT/raw/logs"

if [ ! -d node_modules ]; then
  echo "Installing dependencies..."
  npm install
fi

echo "[$(date -Is)] starting jarvis whatsapp listener" >> "$JARVIS_ROOT/raw/logs/whatsapp-listener.log"
exec node listener.js >> "$JARVIS_ROOT/raw/logs/whatsapp-listener.log" 2>&1
