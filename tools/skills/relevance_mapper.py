#!/usr/bin/env python3
"""Map ingested content to active Jarvis projects and suggest specific applications.

Loads project/research context from wiki/projects/ and wiki/analyses/, then
asks the LLM where newly ingested content can add value — with concrete actions.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm: dict = {}
    current_key = ""
    for line in lines[1:end]:
        if re.match(r"^\s+", line) and current_key:
            fm[current_key] = fm.get(current_key, "") + "\n" + line
        else:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)", line)
            if m:
                current_key = m.group(1)
                fm[current_key] = m.group(2).strip()
    return fm


def load_context(wiki_root: Path = WIKI) -> list[dict]:
    """Load active projects and notable research/analyses as context items."""
    items: list[dict] = []

    # Active projects
    projects_dir = wiki_root / "projects"
    if projects_dir.exists():
        for p in sorted(projects_dir.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                fm = _parse_frontmatter(text)
                if fm.get("status", "active") not in ("archived", "done", "cancelled"):
                    # Extract a richer description from the note body
                    body_start = text.find("---", 3)
                    body = text[body_start + 3:].strip()[:1500] if body_start > 0 else ""
                    items.append({
                        "name": fm.get("title", p.stem),
                        "type": "project",
                        "status": fm.get("status", "active"),
                        "summary": fm.get("Summary", "").strip('"').strip("'"),
                        "tags": fm.get("tags", ""),
                        "body_excerpt": body[:600],
                        "path": str(p.relative_to(ROOT)),
                    })
            except OSError:
                pass

    # Notable analyses (research context)
    analyses_dir = wiki_root / "analyses"
    if analyses_dir.exists():
        for p in sorted(analyses_dir.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                fm = _parse_frontmatter(text)
                summary = fm.get("Summary", "").strip('"').strip("'")
                if summary:
                    items.append({
                        "name": fm.get("title", p.stem),
                        "type": "research",
                        "summary": summary,
                        "tags": fm.get("tags", ""),
                        "path": str(p.relative_to(ROOT)),
                    })
            except OSError:
                pass

    return items


def map_relevance(
    content_title: str,
    content_summary: str,
    concepts: list[str],
    tags: list[str],
    model: str = "local",
    wiki_root: Path = WIKI,
) -> list[dict]:
    """Return list of {project, relevance, how_it_applies, action, component} dicts."""
    context_items = load_context(wiki_root)
    if not context_items:
        return []

    sys.path.insert(0, str(Path(__file__).parent))
    from jarvis_llm import JarvisLLM  # type: ignore

    llm = JarvisLLM(model)

    context_lines = []
    for item in context_items:
        line = f"[{item['type'].upper()}] {item['name']}: {item['summary']}"
        if item.get("body_excerpt"):
            line += f"\n  Details: {item['body_excerpt'][:300]}"
        context_lines.append(line)

    prompt = (
        f"New content ingested: \"{content_title}\"\n"
        f"Summary: {content_summary}\n"
        f"Key concepts: {', '.join(concepts) if concepts else 'N/A'}\n"
        f"Tags: {', '.join(tags) if tags else 'N/A'}\n\n"
        f"Active projects and research:\n"
        + "\n".join(context_lines)
        + "\n\n"
        "For each project or research area where this content is DIRECTLY applicable "
        "(not just vaguely related), return a JSON array with:\n"
        "- project: project name\n"
        "- relevance: high|medium\n"
        "- how_it_applies: specific explanation of the connection\n"
        "- action: one concrete next step (implement X in Y, add to Z, study W)\n"
        "- component: which subsystem or part of the project (optional, null if N/A)\n\n"
        "Only include items with medium or high relevance. Return [] if nothing applies.\n"
        "Return ONLY valid JSON array, no extra text."
    )

    resp = llm.complete(prompt, system="You are a technical project advisor. Be specific and practical. Always return valid JSON.")
    text = resp.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        result = json.loads(text)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return []


def format_relevance_section(mappings: list[dict]) -> str:
    """Render the ## Where This Applies section for a wiki note."""
    if not mappings:
        return ""

    lines = ["## Where This Applies", ""]
    for item in mappings:
        relevance_badge = f"**{item.get('relevance', 'medium').upper()}**"
        project = item.get("project", "Unknown")
        lines.append(f"### {project} — {relevance_badge}")
        lines.append("")
        how = item.get("how_it_applies", "")
        if how:
            lines.append(how)
            lines.append("")
        action = item.get("action", "")
        component = item.get("component", "")
        if action:
            lines.append(f"**Action:** {action}")
        if component:
            lines.append(f"**Component:** {component}")
        lines.append("")

    return "\n".join(lines)
