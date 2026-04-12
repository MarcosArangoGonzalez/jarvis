#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL_DIR="$ROOT/tools/local"
WHISPER_DIR="$LOCAL_DIR/whisper.cpp"
PY_VENV="$LOCAL_DIR/voice-venv"

mkdir -p "$LOCAL_DIR"
python3 -m venv "$PY_VENV"
"$PY_VENV/bin/python" -m pip install --upgrade pip

if command -v cmake >/dev/null 2>&1; then
  CMAKE_BIN="$(command -v cmake)"
else
  "$PY_VENV/bin/python" -m pip install cmake
  CMAKE_BIN="$PY_VENV/bin/cmake"
fi

if [ ! -d "$WHISPER_DIR/.git" ]; then
  git clone https://github.com/ggml-org/whisper.cpp.git "$WHISPER_DIR"
fi

"$CMAKE_BIN" -S "$WHISPER_DIR" -B "$WHISPER_DIR/build" -DCMAKE_BUILD_TYPE=Release
"$CMAKE_BIN" --build "$WHISPER_DIR/build" --config Release

"$PY_VENV/bin/python" -m pip install piper-tts pyperclip
mkdir -p "$LOCAL_DIR/piper-voices"
"$PY_VENV/bin/python" -m piper.download_voices --data-dir "$LOCAL_DIR/piper-voices" en_US-lessac-medium

cat <<EOF
Voice runtime prepared.

Default local paths:
export WHISPER_CPP_BIN="$WHISPER_DIR/build/bin/whisper-cli"
export WHISPER_MODEL="$WHISPER_DIR/models/ggml-base.bin"
export PIPER_BIN="$PY_VENV/bin/piper"
export PIPER_VOICE_MODEL="$LOCAL_DIR/piper-voices/en_US-lessac-medium.onnx"

Download a whisper.cpp model with:
$WHISPER_DIR/models/download-ggml-model.sh base

Download a Piper voice from the OHF-Voice/Piper voice releases or model catalog and place it under:
$LOCAL_DIR/piper-voices/
EOF
