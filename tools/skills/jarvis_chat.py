#!/usr/bin/env python3
"""Jarvis terminal REPL — multi-model chat interface.

Usage:
  python3 jarvis_chat.py [--model local|local:llama3.1|sonnet|opus|gemini]

Slash commands (within the REPL):
  /model <name>     — switch model
  /ingest <url>     — analyze URL with content_analyzer.py
  /search <query>   — search wiki sources
  /tasks            — show P0/P1 tasks
  /clear            — clear session history
  /help             — show commands
  /exit             — quit
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.rule import Rule
    from rich.text import Text
    import rich.box as box
    RICH = True
except ImportError:
    RICH = False


def _plain_print(text: str, style: str = "") -> None:
    print(text)


console = Console() if RICH else None


def cprint(text: str, style: str = "") -> None:
    if console:
        console.print(text, style=style)
    else:
        print(text)


def render_response(text: str, model_name: str, elapsed: float) -> None:
    if not RICH:
        print(f"\n[Jarvis · {model_name} · {elapsed:.1f}s]\n{text}\n")
        return
    label = Text(f" Jarvis · {model_name} · {elapsed:.1f}s ", style="bold cyan")
    try:
        md = Markdown(text)
        console.print(Panel(md, title=label, title_align="left", border_style="cyan", box=box.ROUNDED))
    except Exception:
        console.print(Panel(text, title=label, title_align="left", border_style="cyan"))


def render_header(model_display: str, session_num: int) -> None:
    if not RICH:
        print(f"\n=== Jarvis  ·  model: {model_display}  ·  session #{session_num} ===\n")
        return
    title = Text(f"  Jarvis  ·  model: {model_display}  ·  session: #{session_num}  ", style="bold white on dark_blue")
    console.print(Panel(title, border_style="blue", box=box.DOUBLE_EDGE, padding=(0, 0)))


def load_system_context() -> str:
    parts: list[str] = [
        "You are Jarvis, a local-first AI assistant for Marcos Arango González. "
        "Be concise, technical, and pragmatic. Default language: Spanish unless the user writes in English."
    ]

    index = ROOT / "wiki" / "index.md"
    if index.exists():
        text = index.read_text(encoding="utf-8")[:2000]
        parts.append(f"\n## Wiki index (excerpt)\n{text}")

    tasks_index = ROOT / "wiki" / "tasks" / "index.md"
    if tasks_index.exists():
        text = tasks_index.read_text(encoding="utf-8")[:1000]
        parts.append(f"\n## Active tasks (excerpt)\n{text}")

    return "\n".join(parts)


def cmd_search(query: str) -> None:
    wiki = ROOT / "wiki"
    try:
        result = subprocess.run(
            ["grep", "-r", "-l", "-i", query, str(wiki)],
            capture_output=True, text=True, timeout=10,
        )
        files = [Path(f).relative_to(ROOT) for f in result.stdout.strip().splitlines() if f]
        if files:
            cprint(f"  Found in {len(files)} file(s):", "green")
            for f in files[:10]:
                cprint(f"  · {f}", "dim")
        else:
            cprint(f"  No results for '{query}' in wiki.", "yellow")
    except Exception as exc:
        cprint(f"  Search error: {exc}", "red")


def cmd_tasks() -> None:
    tasks_dir = ROOT / "wiki" / "tasks"
    for md in sorted(tasks_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        p0 = [ln.strip() for ln in text.splitlines() if "P0" in ln or "P1" in ln]
        if p0:
            cprint(f"\n  {md.relative_to(ROOT)}:", "bold yellow")
            for item in p0[:5]:
                cprint(f"    {item}", "dim")


def cmd_ingest(url_or_path: str) -> None:
    analyzer = ROOT / "tools" / "skills" / "content_analyzer.py"
    if not analyzer.exists():
        cprint("  content_analyzer.py not found. Run Fase 2 implementation first.", "red")
        return
    cprint(f"  Ingesting: {url_or_path}", "cyan")
    try:
        result = subprocess.run(
            [sys.executable, str(analyzer), url_or_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            cprint(f"  ✓ {result.stdout.strip()}", "green")
        else:
            cprint(f"  ✗ {result.stderr.strip()[:300]}", "red")
    except subprocess.TimeoutExpired:
        cprint("  Timeout (>120s). Content may still be processing.", "yellow")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=None,
                        help="Model to use: local, local:llama3.1, sonnet, opus, gemini")
    args = parser.parse_args()

    # Import here so errors are clear
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from jarvis_llm import JarvisLLM
    except ImportError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    llm = JarvisLLM(args.model)
    session_num = 1
    history: list[dict[str, str]] = []
    system = load_system_context()

    render_header(llm.display_name, session_num)

    if RICH:
        console.print(
            "  [dim]Type your message. Commands: /model, /ingest, /search, /tasks, /clear, /help, /exit[/dim]\n"
        )
    else:
        print("  Commands: /model, /ingest, /search, /tasks, /clear, /help, /exit\n")

    while True:
        try:
            if RICH:
                user_input = Prompt.ask("[bold green]You[/bold green]").strip()
            else:
                user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            cprint("\n  Bye.", "dim")
            break

        if not user_input:
            continue

        # ── slash commands ────────────────────────────────────────────────────
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/exit":
                cprint("  Bye.", "dim")
                break

            elif cmd == "/clear":
                history.clear()
                session_num += 1
                render_header(llm.display_name, session_num)
                cprint("  History cleared.", "dim")

            elif cmd == "/model":
                if not arg:
                    cprint(f"  Current model: {llm.display_name}", "cyan")
                    cprint("  Options: local, local:llama3.1, sonnet, opus, gemini", "dim")
                else:
                    llm = JarvisLLM(arg)
                    cprint(f"  ✓ Model changed to {llm.display_name}", "green")
                    render_header(llm.display_name, session_num)

            elif cmd == "/search":
                if arg:
                    cmd_search(arg)
                else:
                    cprint("  Usage: /search <query>", "yellow")

            elif cmd == "/tasks":
                cmd_tasks()

            elif cmd == "/ingest":
                if arg:
                    cmd_ingest(arg)
                else:
                    cprint("  Usage: /ingest <url_or_path>", "yellow")

            elif cmd == "/help":
                help_text = (
                    "/model <name>     switch model (local, local:llama3.1, sonnet, opus, gemini)\n"
                    "/ingest <url>     analyze URL or file with content_analyzer\n"
                    "/search <query>   grep wiki for query\n"
                    "/tasks            show P0/P1 tasks\n"
                    "/clear            clear session history\n"
                    "/exit             quit"
                )
                if RICH:
                    console.print(Panel(help_text, title="Commands", border_style="dim", box=box.SIMPLE))
                else:
                    print(help_text)
            else:
                cprint(f"  Unknown command: {cmd}. Type /help.", "yellow")

            continue

        # ── LLM call ──────────────────────────────────────────────────────────
        history.append({"role": "user", "content": user_input})

        if RICH:
            with console.status(f"[dim]{llm.display_name} thinking...[/dim]", spinner="dots"):
                try:
                    resp = llm.chat(history, system=system)
                except Exception as exc:
                    cprint(f"\n  ✗ {exc}", "red")
                    history.pop()
                    continue
        else:
            print(f"[{llm.display_name}]...")
            try:
                resp = llm.chat(history, system=system)
            except Exception as exc:
                print(f"Error: {exc}")
                history.pop()
                continue

        history.append({"role": "assistant", "content": resp.text})
        render_response(resp.text, llm.display_name, resp.elapsed)


if __name__ == "__main__":
    main()
