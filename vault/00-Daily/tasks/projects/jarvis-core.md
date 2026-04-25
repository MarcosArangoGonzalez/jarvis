---
title: "Jarvis Core Tasks"
type: tasks
status: active
tags:
  - jarvis
  - tasks
  - voice
created: 2026-04-12
updated: 2026-04-12
tokens_consumed: 1081
sources:
  - "/home/marcos/jarvis/.jarvis/session_manager.md"
  - "/home/marcos/jarvis/tools/skills/voice_bridge.py"
  - "/home/marcos/jarvis/tools/skills/setup_voice.sh"
  - "https://openwhispr.com/"
  - "https://github.com/HeroTools/open-whispr"
  - "https://flathub.org/apps/ink.whis.Whis"
  - "https://flathub.org/apps/net.mkiol.SpeechNote"
Summary: "Task list for Jarvis core capabilities, starting with morning coffee and local voice flow."
aliases:
  - "jarvis-core"
---

# Jarvis Core Tasks

## Active Queue

| Priority | Task | Feature | Status | Conclusion | Next Action |
|---|---|---|---|---|---|
| P1 | Configure WhatsApp listener chat filter | WhatsApp Pipeline | Ready | Listener authenticated and running but targets ALL chats. | Set JARVIS_WHATSAPP_CHAT_ID in Bitwarden; run listener in tmux permanently. |
| P1 | Configure voice flow | Voice | Implemented v1 | Custom Jarvis flow now records, transcribes, optionally refines, copies, and attempts paste on Wayland/X11. | Bind `jarvis_voice_flow.sh` to an Ubuntu shortcut and validate paste in Codex/Claude/terminal. |
| P1 | Add morning coffee task workflow | Session Planning | Ready | Prompt should be short and backed by task files. | Use `wiki/tasks/index.md` plus `.jarvis/session_manager.md`. |
| P2 | Evaluate native Codex/Claude skill wrappers | Agent UX | Backlog | Current Jarvis skill is a Python script, not a native Codex skill. | Decide whether to create Codex skill and Claude command after Markdown workflow works. |

## Voice Review

The proposed Ubuntu wrapper is conceptually correct:

- keyboard shortcut launches an invisible script
- script records/transcribes/refines/pastes
- `notify-send` gives visual feedback
- `xclip` + `xdotool` is a reasonable X11 paste strategy

Current mismatch:

- `voice_bridge.py` only supports `check`, `notify`, `speak`, and `transcribe <audio>`.
- It does not support `--listen`, `--refine`, or `--type`.
- The proposed wrapper uses `/home/marcos/jarvis/.venv`, but voice runtime dependencies currently live in `tools/local/voice-venv`.
- `xdotool` may not work reliably on Wayland sessions; Ubuntu keyboard shortcut flow should verify whether the desktop session is X11 or Wayland.

Observed workstation context on 2026-04-12:

- `XDG_SESSION_TYPE=wayland`
- `wl-copy` and `ydotool` are available.
- `xclip` is available.
- `xdotool` and `wtype` were not found in PATH.

## App-First Evaluation

Use an app before writing custom code if it covers the target workflow.

Recommended first candidate: OpenWhispr.

- Free/open-source positioning and Linux support.
- Global hotkey dictation.
- Local Whisper/Parakeet models and cloud/API options.
- Automatic paste at cursor.
- Agent/cleanup style post-processing.
- Linux packaging path includes AppImage, `.deb`, `.rpm`, `.tar.gz`, and Flatpak build targets.
- Linux paste tooling explicitly distinguishes X11 `xdotool` and Wayland `wtype`/`ydotool`.

Alternative candidates:

- Whis: Flatpak app focused on shortcut -> speak -> clipboard, with cloud or local transcription and AI post-processing. Smaller surface area than OpenWhispr.
- Speech Note: mature offline STT/TTS/translation Flatpak, but it is more a notes/transcription app than a system-wide Wispr Flow clone.
- nerd-dictation: simple/hackable Linux dictation via Vosk, but less close to Whisper/Wispr Flow quality and UX.

Decision for the next implementation session:

1. Keep OpenWhispr as a benchmark/escape hatch.
2. Use the custom Jarvis flow first because v1 is now implemented locally.
3. If the shortcut/paste UX is worse than OpenWhispr, compare both flows and keep the one with fewer desktop integration failures.

## Custom Voice Flow v1

Implemented on 2026-04-12:

- `voice_bridge.py listen --duration <seconds> --language es --type`
- legacy compatibility: `voice_bridge.py --listen --duration <seconds> --language es --type`
- fixed-duration recording via `ffmpeg` PulseAudio input, with `arecord` fallback
- whisper.cpp transcription
- clipboard copy via `wl-copy`, `xclip`, or `pyperclip`
- paste attempt via `wtype`, `ydotool`, or `xdotool`
- optional Ollama refinement when `JARVIS_VOICE_REFINE_MODEL` or `OLLAMA_MODEL` is configured
- desktop notifications through `notify-send`
- shortcut wrapper: `tools/skills/jarvis_voice_flow.sh`
- recommended toggle wrapper: `tools/skills/jarvis_voice_toggle.sh`
- optional launcher: `tools/skills/jarvis-voice-toggle.desktop`

Quality update on 2026-04-13:

- downloaded `ggml-small.bin` and made it the preferred model when present
- kept `ggml-base.bin` as fallback
- added a default Whisper prompt with Jarvis, coding, RAG, and BJJ vocabulary
- added `--prompt` and `--no-prompt` controls for `listen` and `transcribe`
- verified a 3s microphone test with `ggml-small.bin`: output was `Hola buenas tardes.`

Latency update on 2026-04-13:

- added `JARVIS_VOICE_MODE=fast|balanced`
- toggle default is now `fast`, which uses `ggml-base.bin`
- `balanced` remains available for better accuracy with `ggml-small.bin`
- short smoke benchmark: `fast` around 1.2s vs `balanced` around 3.1s on the same test audio
- clipboard copy is now non-fatal if desktop clipboard access is unavailable

Interaction update on 2026-04-13:

- added toggle behavior: first shortcut press starts recording, second press stops recording and runs transcription/paste
- kept the fixed-duration wrapper as fallback
- added a `.desktop` launcher for icon-based activation
- confirmed GNOME shortcut: `Super + Shift + V`
- confirmed `ydotoold` is running for Wayland paste support
- installed local launcher at `~/.local/share/applications/jarvis-voice-toggle.desktop`

Known constraints:

- Ollama has no local models installed yet, so refinement is disabled by default in the wrapper.
- `ydotool` is installed, but Wayland paste may require the `ydotoold` daemon.
- If paste fails, the transcription remains copied to the clipboard and the notification tells the user to paste manually.

Recommended implementation order:

1. Validate paste in Codex, Claude Code, browser text fields, and terminal.
2. If paste fails on Wayland, start/enable `ydotoold` or install `wtype`.
3. Install an Ollama model if refinement becomes necessary.
4. Compare against OpenWhispr only if the custom shortcut flow is unreliable.
