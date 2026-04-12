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
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/.jarvis/session_manager.md"
  - "/home/marcos/jarvis/tools/skills/voice_bridge.py"
  - "/home/marcos/jarvis/tools/skills/setup_voice.sh"
Summary: "Task list for Jarvis core capabilities, starting with morning coffee and local voice flow."
---

# Jarvis Core Tasks

## Active Queue

| Priority | Task | Feature | Status | Conclusion | Next Action |
|---|---|---|---|---|---|
| P1 | Configure voice flow | Voice | Ready | Current proposal is directionally correct, but `voice_bridge.py` lacks `--listen`, `--refine`, and `--type`. | Plan implementation of recording, refinement, paste, and wrapper. |
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

Recommended implementation order:

1. Add a non-interactive `listen` subcommand that records audio to a temp WAV.
2. Reuse existing `transcribe(audio_path)`.
3. Add optional `refine` subcommand/flag with configured LLM or local model.
4. Add paste mode using clipboard plus `xdotool`, with clear dependency check.
5. Add `jarvis_voice_flow.sh`.
6. Configure Ubuntu global shortcut manually.
