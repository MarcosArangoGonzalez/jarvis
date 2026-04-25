#!/usr/bin/env python3
"""Generate a session insight note from today's jarvis-log entries."""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOG_PATH = ROOT / "wiki" / "logs" / "core" / "jarvis-log.md"
INSIGHTS_DIR = ROOT / "vault" / "03-Dev" / "insights"


def extract_today_entries(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    today = datetime.now().strftime("%Y-%m-%d")
    entries: list[str] = []
    current: list[str] = []
    in_today = False
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and today in line:
            in_today = True
            current = [line]
        elif line.startswith("## ") and in_today:
            if current:
                entries.append("\n".join(current))
            current = []
            in_today = False
        elif in_today:
            current.append(line)
    if current:
        entries.append("\n".join(current))
    return entries


def extract_technologies(entries: list[str]) -> list[str]:
    tech_patterns = [
        r"\bfastapi\b", r"\bpython\b", r"\bpydantic\b", r"\bsqlalchemy\b",
        r"\bjavaScript\b", r"\btypescript\b", r"\breact\b", r"\bnext\.?js\b",
        r"\bdocker\b", r"\bkubernetes\b", r"\bgit\b", r"\bpytest\b",
        r"\bsqlite\b", r"\bpostgresql\b", r"\bredis\b", r"\bhtmx\b",
    ]
    text = " ".join(entries).lower()
    found = []
    for pat in tech_patterns:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat.strip(r"\b").replace(r"\.", "."))
    return list(dict.fromkeys(found))[:8]


def generate_insight(entries: list[str]) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    hour_str = now.strftime("%H")
    technologies = extract_technologies(entries)
    body = "\n\n".join(entries) if entries else "Sin entradas en el log de hoy."

    frontmatter = [
        "---",
        f'title: "Session Insights {date_str}"',
        "type: insight",
        f"date: {date_str}",
        f"technologies: [{', '.join(technologies)}]",
        "patterns_used: []",
        f"created: {date_str}",
        "---",
        "",
    ]
    content_lines = [
        f"# Session Insights — {date_str}",
        "",
        "## Qué se trabajó hoy",
        "",
        body,
        "",
        "## Notas de aprendizaje",
        "",
        "> Completar manualmente: qué fue nuevo, qué fue difícil, qué harías diferente.",
        "",
    ]
    return "\n".join(frontmatter + content_lines)


def main() -> int:
    entries = extract_today_entries(LOG_PATH)
    if not entries:
        print("No entries found in today's jarvis-log. Creating stub insight.", file=sys.stderr)

    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    filename = f"{now.strftime('%Y-%m-%d-%H')}-session.md"
    dest = INSIGHTS_DIR / filename
    content = generate_insight(entries)
    dest.write_text(content, encoding="utf-8")
    print(f"Insight written to {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
