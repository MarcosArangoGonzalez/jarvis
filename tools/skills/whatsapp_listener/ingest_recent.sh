#!/usr/bin/env bash
# List or ingest selected recent video links from the configured WhatsApp chat.
#
# Usage:
#   bash ingest_recent.sh --list --since today --limit 80
#   bash ingest_recent.sh --select 1,3-5 --since today --limit 80

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JARVIS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SERVICE="jarvis-whatsapp-listener.service"
WAS_ACTIVE=0
AUTH_DIR="$SCRIPT_DIR/.wwebjs_auth/session"
TIMEOUT_SECONDS="${JARVIS_WHATSAPP_HISTORY_TIMEOUT:-120}"

cleanup_profile_locks() {
  if [ -d "$AUTH_DIR" ]; then
    rm -f "$AUTH_DIR/SingletonLock" "$AUTH_DIR/SingletonSocket" "$AUTH_DIR/SingletonCookie" "$AUTH_DIR/DevToolsActivePort"
  fi
}

stop_profile_processes() {
  local pids
  pids="$(pgrep -f "$AUTH_DIR" || true)"
  if [ -n "$pids" ]; then
    kill $pids 2>/dev/null || true
    sleep 2
  fi
}

if systemctl --user is-active --quiet "$SERVICE"; then
  WAS_ACTIVE=1
  systemctl --user stop "$SERVICE"
fi

stop_profile_processes
cleanup_profile_locks

cleanup() {
  if [ "$WAS_ACTIVE" = "1" ]; then
    systemctl --user start "$SERVICE" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

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

export JARVIS_ROOT
cd "$SCRIPT_DIR"

timeout "$TIMEOUT_SECONDS" node ingest_recent.js "$@"
