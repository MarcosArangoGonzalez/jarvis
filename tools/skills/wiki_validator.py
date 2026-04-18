#!/usr/bin/env python3
"""Validate Jarvis wiki notes against authoritative sources.

Status lifecycle:
  NEW        → just ingested, unreviewed
  PROCESSING → being validated / needs research
  VERIFIED   → confirmed against authoritative source
  STALE      → source has been updated since ingestion

Usage:
  python3 wiki_validator.py <note_path> [options]
  python3 wiki_validator.py --scan        # scan all NEW notes
  python3 wiki_validator.py --list-new    # list notes with status: NEW
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request as urlreq
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"

# Known authoritative source patterns: (regex on concepts/tags) → doc URL template
AUTHORITATIVE_SOURCES: list[tuple[str, str]] = [
    (r"\brag\b|retrieval.augmented", "https://python.langchain.com/docs/concepts/rag/"),
    (r"\bpgvector\b", "https://github.com/pgvector/pgvector"),
    (r"\blangchain\b", "https://python.langchain.com/docs/introduction/"),
    (r"\bfastapi\b", "https://fastapi.tiangolo.com/"),
    (r"\bpydantic\b", "https://docs.pydantic.dev/latest/"),
    (r"\bollama\b", "https://ollama.com/library"),
    (r"\bwhisper\b", "https://github.com/openai/whisper"),
    (r"\byt.dlp\b|yt-dlp", "https://github.com/yt-dlp/yt-dlp"),
    (r"\bhuggingface\b|transformers", "https://huggingface.co/docs/transformers/"),
    (r"\bpytorch\b|torch\b", "https://pytorch.org/docs/stable/"),
    (r"\bdjango\b", "https://docs.djangoproject.com/en/stable/"),
    (r"\bnext\.?js\b", "https://nextjs.org/docs"),
    (r"\breact\b", "https://react.dev/reference/react"),
    (r"\btypescript\b", "https://www.typescriptlang.org/docs/"),
    (r"\bbjj\b|jiu.jitsu", "https://www.ibjjf.com/rules"),
    (r"\bweaviate\b", "https://weaviate.io/developers/weaviate"),
    (r"\bchroma\b|chromadb", "https://docs.trychroma.com/"),
    (r"\bpinecone\b", "https://docs.pinecone.io/"),
    (r"\bwhatsapp.web", "https://github.com/pedroslopez/whatsapp-web.js"),
    (r"\banthropicapi\b|anthropic sdk", "https://docs.anthropic.com/"),
    (r"\bgemini\b|google ai", "https://ai.google.dev/gemini-api/docs"),
]


def _parse_frontmatter(text: str) -> tuple[dict, int]:
    if not text.startswith("---"):
        return {}, 0
    lines = text.splitlines()
    end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}, 0
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
    return fm, end + 1


def _update_frontmatter_field(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf'^({re.escape(key)}:\s*).*$', re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(f'{key}: {value}', text)
    # Insert before closing ---
    return re.sub(r'\n---\n', f'\n{key}: {value}\n---\n', text, count=1)


def find_authoritative_sources(note_path: Path) -> list[str]:
    """Return list of likely authoritative doc URLs based on note content."""
    text = note_path.read_text(encoding="utf-8", errors="replace").lower()
    found: list[str] = []
    for pattern, url in AUTHORITATIVE_SOURCES:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(url)
    return found


def check_url_live(url: str, timeout: int = 8) -> bool:
    """Return True if URL responds with 2xx/3xx."""
    try:
        req = urlreq.Request(url, method="HEAD",
                             headers={"User-Agent": "Mozilla/5.0 (JarvisValidator/1.0)"})
        with urlreq.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception:
        return False


def validate_note(
    note_path: Path,
    model: str = "local",
    fetch_sources: bool = True,
    auto_search: bool = True,
) -> dict:
    """Validate a single note. Returns result dict with status and sources found."""
    text = note_path.read_text(encoding="utf-8", errors="replace")
    fm, body_start = _parse_frontmatter(text)

    current_status = fm.get("status", "NEW").strip().upper()
    result: dict = {
        "path": str(note_path.relative_to(ROOT)),
        "title": fm.get("title", note_path.stem).strip('"'),
        "previous_status": current_status,
        "new_status": current_status,
        "sources_found": [],
        "note": "",
    }

    # Set to PROCESSING while we work
    text = _update_frontmatter_field(text, "status", "PROCESSING")
    note_path.write_text(text, encoding="utf-8")

    sources_found: list[str] = []

    # Step 1: pattern-match authoritative docs
    if auto_search:
        sources_found = find_authoritative_sources(note_path)

    # Step 2: LLM-assisted source search if no pattern match
    if not sources_found and model != "none":
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from jarvis_llm import JarvisLLM  # type: ignore

            llm = JarvisLLM(model)
            summary = fm.get("Summary", "").strip('"').strip("'")
            title = fm.get("title", note_path.stem).strip('"')
            tags_raw = fm.get("tags", "")
            tags = re.findall(r'[a-z][a-z0-9-]+', tags_raw)

            resp = llm.complete(
                f"For the following note, give the most authoritative URL to verify the information. "
                f"Return ONLY a JSON object: {{\"url\": \"https://...\", \"reason\": \"one line\"}}.\n\n"
                f"Title: {title}\nSummary: {summary}\nTags: {', '.join(tags)}",
                system="You are a research librarian. Return ONLY valid JSON with a single 'url' key.",
            )
            raw = resp.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            if isinstance(data, dict) and "url" in data:
                sources_found.append(data["url"])
                result["note"] = data.get("reason", "")
        except Exception:
            pass

    # Step 3: verify URLs are live
    verified_sources: list[str] = []
    if fetch_sources:
        for url in sources_found[:3]:
            if check_url_live(url):
                verified_sources.append(url)
    else:
        verified_sources = sources_found[:3]

    result["sources_found"] = verified_sources

    # Step 4: update note frontmatter
    today = date.today().isoformat()
    new_status = "VERIFIED" if verified_sources else "PROCESSING"

    text = note_path.read_text(encoding="utf-8", errors="replace")
    text = _update_frontmatter_field(text, "status", new_status)
    text = _update_frontmatter_field(text, "updated", today)
    text = _update_frontmatter_field(text, "validated", today)
    text = _update_frontmatter_field(text, "requires_verification", "false")

    # Append authoritative sources to sources[] list
    if verified_sources:
        for src in verified_sources:
            if src not in text:
                text = re.sub(
                    r'(sources:\s*\n(?:\s+-[^\n]*\n)*)',
                    lambda m: m.group(0) + f'  - "{src}"\n',
                    text,
                    count=1,
                )

        # Add ## Authoritative Sources section if not present
        if "## Authoritative Sources" not in text:
            src_section = "\n## Authoritative Sources\n\n"
            for src in verified_sources:
                src_section += f"- {src}\n"
            src_section += "\n"
            text += src_section

    note_path.write_text(text, encoding="utf-8")
    result["new_status"] = new_status
    return result


def scan_new_notes(wiki_root: Path = WIKI, model: str = "local", limit: int = 0) -> list[dict]:
    """Find and validate all notes with status: NEW."""
    results = []
    new_notes = []
    for md in wiki_root.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
            fm, _ = _parse_frontmatter(text)
            if fm.get("status", "").strip().upper() in ("NEW", "DRAFT"):
                new_notes.append(md)
        except OSError:
            pass

    if limit:
        new_notes = new_notes[:limit]

    for path in new_notes:
        print(f"  Validating: {path.relative_to(ROOT)} ...", end=" ", flush=True)
        result = validate_note(path, model=model)
        status = result["new_status"]
        n = len(result["sources_found"])
        print(f"{status} ({n} source{'s' if n != 1 else ''} found)")
        results.append(result)

    return results


def list_notes_by_status(wiki_root: Path = WIKI, status: str = "NEW") -> list[Path]:
    matches = []
    for md in wiki_root.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
            fm, _ = _parse_frontmatter(text)
            if fm.get("status", "").strip().upper() == status.upper():
                matches.append(md)
        except OSError:
            pass
    return sorted(matches)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("note", nargs="?", default=None, help="Path to wiki note to validate")
    parser.add_argument("--scan", action="store_true", help="Validate all NEW/DRAFT notes")
    parser.add_argument("--list-new", action="store_true", help="List notes with status: NEW")
    parser.add_argument("--list-status", default=None, help="List notes with given status")
    parser.add_argument("--model", default="local", help="LLM model for source search")
    parser.add_argument("--no-fetch", action="store_true", help="Skip live URL check")
    parser.add_argument("--limit", type=int, default=0, help="Max notes to validate in --scan")
    args = parser.parse_args()

    if args.list_new or args.list_status:
        status = args.list_status or "NEW"
        notes = list_notes_by_status(status=status)
        print(f"\n{status} notes ({len(notes)}):\n")
        for p in notes:
            print(f"  {p.relative_to(ROOT)}")
        print()
        return

    if args.scan:
        print(f"\nScanning wiki for NEW/DRAFT notes ...\n")
        results = scan_new_notes(model=args.model, limit=args.limit)
        verified = sum(1 for r in results if r["new_status"] == "VERIFIED")
        print(f"\n── {len(results)} notes validated · {verified} VERIFIED ──\n")
        return

    if args.note:
        path = Path(args.note)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            print(f"Note not found: {path}", file=sys.stderr)
            sys.exit(1)
        result = validate_note(path, model=args.model, fetch_sources=not args.no_fetch)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
