#!/usr/bin/env python3
"""Local voice bridge using whisper.cpp for STT and Piper for TTS."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WHISPER_BIN = ROOT / "tools" / "local" / "whisper.cpp" / "build" / "bin" / "whisper-cli"
DEFAULT_WHISPER_MODEL = ROOT / "tools" / "local" / "whisper.cpp" / "models" / "ggml-base.bin"
PREFERRED_WHISPER_MODEL = ROOT / "tools" / "local" / "whisper.cpp" / "models" / "ggml-small.bin"
DEFAULT_PIPER_BIN = ROOT / "tools" / "local" / "voice-venv" / "bin" / "piper"
DEFAULT_PIPER_MODEL = ROOT / "tools" / "local" / "piper-voices" / "en_US-lessac-medium.onnx"
DEFAULT_LISTEN_SECONDS = int(os.getenv("JARVIS_VOICE_DURATION", "8"))
DEFAULT_LANGUAGE = os.getenv("JARVIS_VOICE_LANGUAGE", "es")
DEFAULT_WHISPER_PROMPT = os.getenv(
    "JARVIS_WHISPER_PROMPT",
    (
        "Jarvis, Codex, Claude Code, bjj-app, RAG agentico, LangGraph, backend, frontend, "
        "Python, Java, Spring Boot, Docker, PostgreSQL, Chroma, Gemini, Ollama, Whisper, "
        "Brazilian Jiu Jitsu, BJJ, jiu jitsu, guardia, media guardia, guardia mariposa, "
        "De la Riva, mount, side control, back control, rear naked choke, armbar, triangle, "
        "kimura, americana, berimbolo, combat story, grader, router, retriever, evaluator."
    ),
)


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
    if env_name == "WHISPER_MODEL" and PREFERRED_WHISPER_MODEL.exists():
        return str(PREFERRED_WHISPER_MODEL)
    if local_default.exists():
        return str(local_default)
    return None


def notify(title: str, message: str) -> None:
    notifier = shutil.which("notify-send")
    if notifier:
        subprocess.run([notifier, title, message, "-i", "audio-input-microphone", "-t", "2500"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def copy_to_clipboard(text: str) -> None:
    wl_copy = shutil.which("wl-copy")
    if os.getenv("WAYLAND_DISPLAY") and wl_copy:
        subprocess.run([wl_copy], input=text, text=True, check=True)
        return

    xclip = shutil.which("xclip")
    if os.getenv("DISPLAY") and xclip:
        subprocess.run([xclip, "-selection", "clipboard"], input=text, text=True, check=True)
        return

    try:
        import pyperclip  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"wl-copy, xclip, or pyperclip is required for clipboard injection: {exc}") from exc
    pyperclip.copy(text)


def paste_clipboard(terminal: bool = False) -> bool:
    if os.getenv("WAYLAND_DISPLAY"):
        wtype = shutil.which("wtype")
        if wtype:
            command = [wtype, "-M", "ctrl", "-M", "shift", "v", "-m", "shift", "-m", "ctrl"] if terminal else [wtype, "-M", "ctrl", "v", "-m", "ctrl"]
            if subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                return True

        ydotool = shutil.which("ydotool")
        if ydotool:
            command = [ydotool, "key", "29:1", "42:1", "47:1", "47:0", "42:0", "29:0"] if terminal else [ydotool, "key", "29:1", "47:1", "47:0", "29:0"]
            if subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                return True

    xdotool = shutil.which("xdotool")
    if os.getenv("DISPLAY") and xdotool:
        command = [xdotool, "key", "ctrl+shift+v"] if terminal else [xdotool, "key", "ctrl+v"]
        if subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return True

    return False


def type_text(text: str, terminal: bool = False) -> bool:
    copy_to_clipboard(text)
    time.sleep(0.08)
    return paste_clipboard(terminal=terminal)


def record_audio(output: Path, duration: int) -> Path:
    if duration <= 0:
        raise RuntimeError("duration must be greater than zero seconds.")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        command = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "pulse", "-i", "default", "-t", str(duration), "-ac", "1", "-ar", "16000", str(output)]
        if subprocess.run(command, check=False).returncode == 0:
            return output

    arecord = shutil.which("arecord")
    if arecord:
        command = [arecord, "-D", "pulse", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", str(duration), str(output)]
        subprocess.run(command, check=True)
        return output

    raise RuntimeError("ffmpeg or arecord is required for voice recording.")


def refine_text(text: str) -> str:
    model = os.getenv("JARVIS_VOICE_REFINE_MODEL") or os.getenv("OLLAMA_MODEL")
    ollama = shutil.which("ollama")
    if not model or not ollama:
        print("voice_bridge warning: refine requested but JARVIS_VOICE_REFINE_MODEL/OLLAMA_MODEL or ollama is unavailable; using raw transcription.", file=sys.stderr)
        return text

    prompt = (
        "Corrige la transcripcion de voz manteniendo el significado original. "
        "Devuelve solo el texto final, sin explicaciones. "
        "Respeta terminos tecnicos de programacion, BJJ, Codex, Claude y Jarvis.\n\n"
        f"Transcripcion:\n{text}"
    )
    try:
        completed = subprocess.run([ollama, "run", model, prompt], check=True, capture_output=True, text=True, timeout=45)
    except Exception as exc:
        print(f"voice_bridge warning: refine failed ({exc}); using raw transcription.", file=sys.stderr)
        return text
    refined = completed.stdout.strip()
    return refined or text


def transcribe(audio_path: Path, language: str | None = None, prompt: str | None = DEFAULT_WHISPER_PROMPT) -> str:
    whisper_bin = resolve_binary("WHISPER_CPP_BIN", "whisper-cli", DEFAULT_WHISPER_BIN)
    model = resolve_path("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)
    if not whisper_bin:
        raise RuntimeError("WHISPER_CPP_BIN or whisper-cli is required.")
    if not model:
        raise RuntimeError("WHISPER_MODEL must point to a whisper.cpp ggml model.")

    command = [whisper_bin, "-m", model, "-f", str(audio_path), "-nt"]
    if language:
        command.extend(["-l", language])
    if prompt:
        command.extend(["--prompt", prompt])
    command.append("--suppress-nst")
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    text = completed.stdout.strip()
    copy_to_clipboard(text)
    return text


def listen(duration: int, output: Path | None, language: str | None, prompt: str | None, refine: bool, inject: bool, terminal: bool, keep_audio: bool) -> str:
    audio_path = output or (Path(tempfile.gettempdir()) / f"jarvis-voice-{os.getpid()}.wav")
    notify("JarvisOS", f"Escuchando durante {duration}s...")
    record_audio(audio_path, duration)
    notify("JarvisOS", "Transcribiendo...")
    text = transcribe(audio_path, language=language, prompt=prompt)
    if refine:
        notify("JarvisOS", "Corrigiendo transcripcion...")
        text = refine_text(text)
        copy_to_clipboard(text)
    pasted = type_text(text, terminal=terminal) if inject else False
    if inject and not pasted:
        notify("JarvisOS", "Texto copiado. Pega manualmente con Ctrl+V.")
    else:
        notify("JarvisOS", "Dictado listo.")
    if not keep_audio and not output:
        audio_path.unlink(missing_ok=True)
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
        "WHISPER_PROMPT": "configured" if DEFAULT_WHISPER_PROMPT else "disabled",
        "PIPER_BIN": piper_bin,
        "PIPER_VOICE_MODEL": resolve_path("PIPER_VOICE_MODEL", DEFAULT_PIPER_MODEL),
        "RECORDER": shutil.which("ffmpeg") or shutil.which("arecord"),
        "CLIPBOARD": shutil.which("wl-copy") or shutil.which("xclip") or "pyperclip",
        "PASTE_TOOL": shutil.which("wtype") or shutil.which("ydotool") or shutil.which("xdotool") or "clipboard-only",
    }
    for key, value in checks.items():
        print(f"{key}: {value or 'missing'}")
    return 0 if all(checks.values()) else 1


def normalize_legacy_args(argv: list[str]) -> list[str]:
    commands = {"check", "notify", "speak", "transcribe", "listen"}
    if any(arg in commands for arg in argv):
        return argv
    if "--listen" in argv:
        return ["listen"] + [arg for arg in argv if arg != "--listen"]
    return argv


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
    transcribe_parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    transcribe_parser.add_argument("--prompt", default=DEFAULT_WHISPER_PROMPT)
    transcribe_parser.add_argument("--no-prompt", action="store_true")
    transcribe_parser.add_argument("--refine", action="store_true")
    transcribe_parser.add_argument("--type", action="store_true", dest="inject")
    transcribe_parser.add_argument("--terminal-paste", action="store_true")
    listen_parser = subparsers.add_parser("listen")
    listen_parser.add_argument("--duration", "-d", type=int, default=DEFAULT_LISTEN_SECONDS)
    listen_parser.add_argument("--output", type=Path)
    listen_parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    listen_parser.add_argument("--prompt", default=DEFAULT_WHISPER_PROMPT)
    listen_parser.add_argument("--no-prompt", action="store_true")
    listen_parser.add_argument("--refine", action="store_true")
    listen_parser.add_argument("--type", action="store_true", dest="inject")
    listen_parser.add_argument("--terminal-paste", action="store_true")
    listen_parser.add_argument("--keep-audio", action="store_true")
    args = parser.parse_args(normalize_legacy_args(sys.argv[1:]))

    if args.command == "check":
        raise SystemExit(check())
    if args.command in {"speak", "notify"}:
        print(speak(args.text))
        return
    if args.command == "transcribe":
        prompt = None if args.no_prompt else args.prompt
        text = transcribe(args.audio, language=args.language, prompt=prompt)
        if args.refine:
            text = refine_text(text)
            copy_to_clipboard(text)
        if args.inject and not type_text(text, terminal=args.terminal_paste):
            notify("JarvisOS", "Texto copiado. Pega manualmente con Ctrl+V.")
        print(text)
        return
    if args.command == "listen":
        prompt = None if args.no_prompt else args.prompt
        print(listen(args.duration, args.output, args.language, prompt, args.refine, args.inject, args.terminal_paste, args.keep_audio))
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"voice_bridge error: {exc}", file=sys.stderr)
        raise SystemExit(1)
