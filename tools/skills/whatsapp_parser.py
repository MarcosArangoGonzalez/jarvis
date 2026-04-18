#!/usr/bin/env python3
"""Parse WhatsApp exported chat (.txt) and extract URLs into wiki notes.

Usage:
  python3 whatsapp_parser.py <chat.txt> [--limit N] [--type youtube|instagram|all]
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCES = ROOT / "wiki" / "sources"

# WhatsApp export line format: "DD/MM/YY, HH:MM - Sender: message"
LINE_RE = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)$")
URL_RE = re.compile(r"https?://[^\s<>\"']+")


@dataclass
class Message:
    date: str
    time: str
    sender: str
    text: str


@dataclass
class ChatLink:
    url: str
    date: str
    category: str
    raw_message: str


def categorize(url: str) -> str:
    if re.search(r"youtube\.com|youtu\.be", url):
        return "youtube"
    if re.search(r"instagram\.com/reel", url):
        return "instagram-reel"
    if re.search(r"instagram\.com/p/", url):
        return "instagram-post"
    if re.search(r"instagram\.com", url):
        return "instagram"
    return "article"


def parse_chat(path: Path) -> list[Message]:
    messages: list[Message] = []
    current: Message | None = None

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE_RE.match(raw_line)
        if m:
            current = Message(date=m.group(1), time=m.group(2), sender=m.group(3), text=m.group(4))
            messages.append(current)
        elif current:
            current.text += "\n" + raw_line

    return messages


def extract_links(messages: list[Message], category_filter: str = "all") -> list[ChatLink]:
    links: list[ChatLink] = []
    seen: set[str] = set()

    for msg in messages:
        for url in URL_RE.findall(msg.text):
            url = url.rstrip(".,;)")
            if url in seen:
                continue
            seen.add(url)
            cat = categorize(url)
            if category_filter != "all" and cat != category_filter:
                continue
            links.append(ChatLink(url=url, date=msg.date, category=cat, raw_message=msg.text.strip()))

    return links


def build_note(links: list[ChatLink], chat_name: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    # Count by category
    counts: dict[str, int] = {}
    for lnk in links:
        counts[lnk.category] = counts.get(lnk.category, 0) + 1

    counts_str = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))

    lines = [
        "---",
        f'title: "WhatsApp Links — {chat_name}"',
        'type: source',
        'status: draft',
        'tags:',
        '  - whatsapp',
        '  - links',
        '  - inbox',
        f'created: {today}',
        f'updated: {today}',
        'tokens_consumed: 0',
        'sources:',
        '  - "whatsapp-export"',
        f'Summary: "Links exportados del chat de WhatsApp: {counts_str} ({len(links)} total)."',
        'requires_verification: true',
        "---",
        "",
        f"# WhatsApp Links — {chat_name}",
        "",
        f"> {len(links)} links extraídos del chat exportado. `requires_verification: true`",
        "",
    ]

    # Group by category
    by_cat: dict[str, list[ChatLink]] = {}
    for lnk in links:
        by_cat.setdefault(lnk.category, []).append(lnk)

    cat_order = ["youtube", "instagram-reel", "instagram-post", "instagram", "article"]
    for cat in cat_order:
        if cat not in by_cat:
            continue
        lines.append(f"## {cat.replace('-', ' ').title()} ({len(by_cat[cat])})")
        lines.append("")
        for lnk in by_cat[cat]:
            lines.append(f"- [{lnk.url}]({lnk.url}) — {lnk.date}")
        lines.append("")

    lines.append("## Related")
    lines.append("")
    lines.append("[[wiki/sources]] | [[wiki/index]]")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="WhatsApp exported .txt file")
    parser.add_argument("--limit", type=int, default=None, help="Process only last N messages")
    parser.add_argument("--type", dest="category", default="all",
                        choices=["all", "youtube", "instagram-reel", "instagram-post", "article"],
                        help="Filter by content type")
    parser.add_argument("--print", action="store_true", help="Print note to stdout instead of saving")
    args = parser.parse_args()

    chat_path = Path(args.input)
    messages = parse_chat(chat_path)
    if args.limit:
        messages = messages[-args.limit:]

    links = extract_links(messages, category_filter=args.category)

    chat_name = chat_path.stem[:40]
    note = build_note(links, chat_name)

    if args.print:
        print(note)
        return

    WIKI_SOURCES.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", chat_name.lower()).strip("_")
    out = WIKI_SOURCES / f"whatsapp_{slug}.md"
    counter = 1
    while out.exists():
        out = WIKI_SOURCES / f"whatsapp_{slug}_{counter}.md"
        counter += 1

    out.write_text(note, encoding="utf-8")
    print(f"✓ {len(links)} links → {out.relative_to(ROOT)}")
    print(f"  youtube: {sum(1 for l in links if l.category == 'youtube')}")
    print(f"  instagram reels: {sum(1 for l in links if l.category == 'instagram-reel')}")
    print(f"  instagram posts: {sum(1 for l in links if l.category == 'instagram-post')}")
    print(f"  articles: {sum(1 for l in links if l.category == 'article')}")


if __name__ == "__main__":
    main()
