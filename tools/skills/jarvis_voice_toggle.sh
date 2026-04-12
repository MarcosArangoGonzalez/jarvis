#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/marcos/jarvis"
PYTHON="$ROOT/tools/local/voice-venv/bin/python"
BRIDGE="$ROOT/tools/skills/voice_bridge.py"
LANGUAGE="${JARVIS_VOICE_LANGUAGE:-es}"
STATE_DIR="${JARVIS_VOICE_STATE_DIR:-${XDG_RUNTIME_DIR:-/tmp}/jarvis-voice}"
PID_FILE="$STATE_DIR/recording.pid"
AUDIO_FILE="$STATE_DIR/recording.wav"
LOG_FILE="$STATE_DIR/recording.log"

if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi

notify() {
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "JarvisOS Voice" "$1" -i audio-input-microphone -t 2500 >/dev/null 2>&1 || true
  fi
}

recording_pid() {
  if [ -f "$PID_FILE" ]; then
    tr -dc '0-9' < "$PID_FILE"
  fi
}

is_recording() {
  local pid
  pid="$(recording_pid)"
  [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1
}

start_recording() {
  mkdir -p "$STATE_DIR"
  rm -f "$AUDIO_FILE" "$LOG_FILE"

  if ! command -v ffmpeg >/dev/null 2>&1; then
    notify "ffmpeg no esta instalado. No puedo grabar audio."
    exit 1
  fi

  notify "Grabando. Pulsa el atajo otra vez para parar."
  setsid ffmpeg -y -hide_banner -loglevel error \
    -f pulse -i default \
    -ac 1 -ar 16000 "$AUDIO_FILE" \
    >"$LOG_FILE" 2>&1 < /dev/null &
  echo "$!" > "$PID_FILE"
}

stop_recording() {
  local pid
  pid="$(recording_pid)"
  if [ -z "$pid" ]; then
    rm -f "$PID_FILE"
    start_recording
    return
  fi

  notify "Parando y transcribiendo..."
  kill -INT "-$pid" >/dev/null 2>&1 || kill -INT "$pid" >/dev/null 2>&1 || true

  for _ in $(seq 1 50); do
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      break
    fi
    sleep 0.1
  done

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill -TERM "-$pid" >/dev/null 2>&1 || kill -TERM "$pid" >/dev/null 2>&1 || true
    sleep 0.2
  fi

  rm -f "$PID_FILE"

  if [ ! -s "$AUDIO_FILE" ]; then
    notify "No se pudo crear audio. Revisa $LOG_FILE."
    exit 1
  fi

  args=(transcribe "$AUDIO_FILE" --language "$LANGUAGE")

  if [ "${JARVIS_VOICE_TYPE:-1}" = "1" ]; then
    args+=(--type)
  fi

  if [ "${JARVIS_VOICE_REFINE:-0}" = "1" ]; then
    args+=(--refine)
  fi

  if [ "${JARVIS_VOICE_TERMINAL_PASTE:-0}" = "1" ]; then
    args+=(--terminal-paste)
  fi

  "$PYTHON" "$BRIDGE" "${args[@]}"

  if [ "${JARVIS_VOICE_KEEP_AUDIO:-0}" != "1" ]; then
    rm -f "$AUDIO_FILE" "$LOG_FILE"
  fi
}

if is_recording; then
  stop_recording
else
  rm -f "$PID_FILE"
  start_recording
fi
