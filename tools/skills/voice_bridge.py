#!/usr/bin/env python3
"""Local voice bridge using whisper.cpp for STT and Piper for TTS."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WHISPER_BIN = ROOT / "tools" / "local" / "whisper.cpp" / "build" / "bin" / "whisper-cli"
DEFAULT_WHISPER_MODEL = ROOT / "tools" / "local" / "whisper.cpp" / "models" / "ggml-base.bin"
DEFAULT_PIPER_BIN = ROOT / "tools" / "local" / "voice-venv" / "bin" / "piper"
DEFAULT_PIPER_MODEL = ROOT / "tools" / "local" / "piper-voices" / "en_US-lessac-medium.onnx"


def resolve_binary(env_name: str, fallback: str, local_default: Path) -> str | None:
    configured = os.getenv(env_name)
    if configured:
        return configured
    if local_default.exists():
        return str(local_default)
    return shutil.which(fallback)


def resolve_path(env_name: str, local_default: Path) -> str | None:
    configured = os.getenv(env_name)
    if configured:
        return configured
    if local_default.exists():
        return str(local_default)
    return None


def copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"pyperclip is required for clipboard injection: {exc}") from exc
    pyperclip.copy(text)


def transcribe(audio_path: Path) -> str:
    whisper_bin = resolve_binary("WHISPER_CPP_BIN", "whisper-cli", DEFAULT_WHISPER_BIN)
    model = resolve_path("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)
    if not whisper_bin:
        raise RuntimeError("WHISPER_CPP_BIN or whisper-cli is required.")
    if not model:
        raise RuntimeError("WHISPER_MODEL must point to a whisper.cpp ggml model.")

    command = [whisper_bin, "-m", model, "-f", str(audio_path), "-nt"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    text = completed.stdout.strip()
    copy_to_clipboard(text)
    return text


def speak(text: str) -> Path:
    piper_bin = resolve_binary("PIPER_BIN", "piper", DEFAULT_PIPER_BIN)
    voice_model = resolve_path("PIPER_VOICE_MODEL", DEFAULT_PIPER_MODEL)
    if not piper_bin:
        raise RuntimeError("PIPER_BIN or piper is required.")
    if not voice_model:
        raise RuntimeError("PIPER_VOICE_MODEL must point to a Piper voice model.")

    output = Path(tempfile.gettempdir()) / "jarvis-piper-output.wav"
    subprocess.run([piper_bin, "--model", voice_model, "--output_file", str(output)], input=text, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    player = shutil.which("aplay") or shutil.which("paplay") or shutil.which("ffplay")
    if player:
        if Path(player).name == "ffplay":
            subprocess.run([player, "-nodisp", "-autoexit", str(output)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run([player, str(output)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output


def check() -> int:
    whisper_bin = resolve_binary("WHISPER_CPP_BIN", "whisper-cli", DEFAULT_WHISPER_BIN)
    piper_bin = resolve_binary("PIPER_BIN", "piper", DEFAULT_PIPER_BIN)
    checks = {
        "WHISPER_CPP_BIN": whisper_bin,
        "WHISPER_MODEL": resolve_path("WHISPER_MODEL", DEFAULT_WHISPER_MODEL),
        "PIPER_BIN": piper_bin,
        "PIPER_VOICE_MODEL": resolve_path("PIPER_VOICE_MODEL", DEFAULT_PIPER_MODEL),
    }
    for key, value in checks.items():
        print(f"{key}: {value or 'missing'}")
    return 0 if all(checks.values()) else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check")
    notify_parser = subparsers.add_parser("notify")
    notify_parser.add_argument("text")
    speak_parser = subparsers.add_parser("speak")
    speak_parser.add_argument("text")
    transcribe_parser = subparsers.add_parser("transcribe")
    transcribe_parser.add_argument("audio", type=Path)
    args = parser.parse_args()

    if args.command == "check":
        raise SystemExit(check())
    if args.command in {"speak", "notify"}:
        print(speak(args.text))
        return
    if args.command == "transcribe":
        print(transcribe(args.audio))
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"voice_bridge error: {exc}", file=sys.stderr)
        raise SystemExit(1)
