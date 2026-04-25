#!/usr/bin/env python3
"""Normalize Jarvis wiki notes for Obsidian graph readability.

This is intentionally conservative:
- only edits Markdown files under wiki/
- keeps existing frontmatter/body content
- renames obvious poor graph nodes (raw URLs, no-title, underscores)
- updates simple wikilinks that target renamed note stems
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"


@dataclass
class Note:
    path: Path
    text: str
    fm_raw: str
    body: str
    fm: dict[str, str]


def slugify(value: str, max_len: int = 80) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:max_len].strip("-") or "untitled-note"


def parse_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return Note(path, text, "", text, {})

    lines = text.splitlines(keepends=True)
    end = None
    for idx, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = idx
            break
    if end is None:
        return Note(path, text, "", text, {})

    fm_raw = "".join(lines[1:end])
    body = "".join(lines[end + 1 :])
    fm: dict[str, str] = {}
    current = ""
    for line in fm_raw.splitlines():
        if re.match(r"^\s+", line) and current:
            fm[current] = fm.get(current, "") + "\n" + line
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)", line)
        if match:
            current = match.group(1)
            fm[current] = match.group(2).strip()
    return Note(path, text, fm_raw, body, fm)


def scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")


def first_source_url(note: Note) -> str:
    match = re.search(r"https?://[^\s\"'<>\]]+", note.fm.get("sources", ""))
    return match.group(0) if match else ""


def instagram_slug(url: str) -> str:
    match = re.search(r"instagram\.com/(reel|p)/([^/?#]+)", url)
    if not match:
        return ""
    kind = "reel" if match.group(1) == "reel" else "post"
    shortcode = slugify(match.group(2), max_len=32)
    return f"bjj-instagram-{kind}-{shortcode}-learning-capture"


def title_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/")
    if "smartymeapp.com" in host:
        return "SmartyMe Instagram Ad Capture"
    if "workdayjobs.com" in host and "accenture" in host:
        return "Accenture Careers Event Registration"
    if "instagram.com" in host:
        match = re.search(r"/(reel|p)/([^/?#]+)", parsed.path)
        if match:
            kind = "Reel" if match.group(1) == "reel" else "Post"
            return f"BJJ Instagram {kind} Learning Capture {match.group(2)}"
    if path:
        return f"{host} {path.split('/')[-1].replace('-', ' ').replace('_', ' ')}".strip().title()
    return host or "Untitled Source"


def better_title(note: Note) -> str:
    title = scalar(note.fm.get("title", ""))
    url = first_source_url(note)
    if not title or title in {"[no-title]", "no-title"} or title.startswith("http"):
        return title_from_url(url)
    return title


def title_needs_rewrite(note: Note) -> bool:
    title = scalar(note.fm.get("title", ""))
    return not title or title in {"[no-title]", "no-title"} or title.startswith("http")


def planned_name(note: Note) -> str | None:
    old = note.path.stem
    title = better_title(note)
    url = first_source_url(note)

    if "instagram.com" in url and note.path.parent.name == "social-captures":
        new = instagram_slug(url)
    elif old in {"no-title", "no-title-2"}:
        new = slugify(title)
    elif "_" in old:
        new = slugify(old)
    elif old.endswith("-"):
        new = old.rstrip("-")
    elif old.startswith("https-www-instagram-com"):
        new = instagram_slug(url)
    else:
        return None

    if not new or new == old:
        return None
    return new


def set_or_insert_scalar(fm: str, key: str, value: str) -> str:
    line = f'{key}: "{value}"'
    if re.search(rf"^{re.escape(key)}:\s*.*$", fm, flags=re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}:\s*.*$", line, fm, flags=re.MULTILINE)
    return fm.rstrip() + f"\n{line}\n"


def set_or_insert_number(fm: str, key: str, value: int) -> str:
    line = f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:\s*.*$", fm, flags=re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}:\s*.*$", line, fm, flags=re.MULTILINE)
    return fm.rstrip() + f"\n{line}\n"


def set_or_insert_list(fm: str, key: str, values: list[str]) -> str:
    block = key + ":\n" + "\n".join(f'  - "{v}"' for v in values)
    pattern = rf"^{re.escape(key)}:\s*(?:\n(?:\s+- .*)+|.*)$"
    if re.search(pattern, fm, flags=re.MULTILINE):
        return re.sub(pattern, block, fm, flags=re.MULTILINE)
    return fm.rstrip() + f"\n{block}\n"


def estimate_tokens(body: str) -> int:
    words = re.findall(r"\S+", body)
    return max(1, len(words) * 4 // 3)


def normalize_note(note: Note, renamed_alias: str | None) -> str:
    if not note.fm_raw:
        return note.text

    fm = note.fm_raw
    title = better_title(note)
    rewrite_title = title_needs_rewrite(note)
    if rewrite_title:
        fm = set_or_insert_scalar(fm, "title", title)

    tokens_raw = scalar(note.fm.get("tokens_consumed", ""))
    if not tokens_raw or tokens_raw == "0":
        fm = set_or_insert_number(fm, "tokens_consumed", estimate_tokens(note.body))

    sources = note.fm.get("sources", "")
    if "sources" in note.fm and not sources.strip().replace("[]", "").replace("-", "").strip():
        fm = set_or_insert_list(fm, "sources", ["jarvis://local"])

    aliases: list[str] = []
    if renamed_alias and renamed_alias != title:
        aliases.append(renamed_alias)
    if aliases:
        deduped = list(dict.fromkeys(aliases))
        fm = set_or_insert_list(fm, "aliases", deduped)

    body = note.body
    first_heading = re.search(r"^# .*$", body, flags=re.MULTILINE)
    if rewrite_title and first_heading:
        body = re.sub(r"^# .*$", f"# {title}", body, count=1, flags=re.MULTILINE)

    return "---\n" + fm.strip() + "\n---\n" + body


def unique_target(path: Path, stem: str) -> Path:
    target = path.with_name(stem + path.suffix)
    if not target.exists() or target == path:
        return target
    idx = 2
    while True:
        candidate = path.with_name(f"{stem}-{idx}{path.suffix}")
        if not candidate.exists():
            return candidate
        idx += 1


def update_wikilinks(root: Path, rename_map: dict[str, str], dry_run: bool) -> int:
    changed = 0
    if not rename_map:
        return changed
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text = text
        for old, new in rename_map.items():
            new_text = re.sub(rf"\[\[{re.escape(old)}(?=]])", f"[[{new}", new_text)
            new_text = re.sub(rf"\[\[{re.escape(old)}(?=[|#])", f"[[{new}", new_text)
        if new_text != text:
            changed += 1
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")
    return changed


def run(root: Path, dry_run: bool) -> None:
    notes = [parse_note(path) for path in sorted(root.rglob("*.md"))]
    planned: dict[Path, Path] = {}
    for note in notes:
        new_stem = planned_name(note)
        if new_stem:
            planned[note.path] = unique_target(note.path, new_stem)

    rename_map = {old.stem: new.stem for old, new in planned.items()}

    edited = 0
    for note in notes:
        alias = rename_map.get(note.path.stem)
        new_text = normalize_note(note, alias)
        if new_text != note.text:
            edited += 1
            if not dry_run:
                note.path.write_text(new_text, encoding="utf-8")

    for old, new in planned.items():
        if old == new:
            continue
        print(f"rename: {old.relative_to(ROOT)} -> {new.relative_to(ROOT)}")
        if not dry_run:
            old.rename(new)

    link_updates = update_wikilinks(root, rename_map, dry_run)
    print(f"checked: {len(notes)}")
    print(f"metadata/body edits: {edited}")
    print(f"renames: {len(planned)}")
    print(f"wikilink files updated: {link_updates}")
    if dry_run:
        print("dry-run: no files changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=WIKI)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args.path.resolve(), args.dry_run)


if __name__ == "__main__":
    main()
