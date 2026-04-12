#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/marcos/jarvis"
PYTHON="$ROOT/tools/local/voice-venv/bin/python"
BRIDGE="$ROOT/tools/skills/voice_bridge.py"
DURATION="${JARVIS_VOICE_DURATION:-8}"
LANGUAGE="${JARVIS_VOICE_LANGUAGE:-es}"

if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi

ARGS=(listen --duration "$DURATION" --language "$LANGUAGE" --type)

if [ "${JARVIS_VOICE_REFINE:-0}" = "1" ]; then
  ARGS+=(--refine)
fi

exec "$PYTHON" "$BRIDGE" "${ARGS[@]}"
