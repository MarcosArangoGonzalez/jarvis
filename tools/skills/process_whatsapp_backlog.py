#!/usr/bin/env python3
"""Process the 90 WhatsApp URLs backlog through content_analyzer.py.

Reads URLs from the existing wiki/sources/whatsapp_*.md note, deduplicates
against already-processed notes, and runs content_analyzer on each remaining URL.
Progress is persisted so the job can be resumed after interruption.

Usage:
  python3 process_whatsapp_backlog.py [options]

Options:
  --source   path to WhatsApp links note (default: auto-detect in wiki/sources/)
  --limit N  process only N URLs in this run (default: all)
  --model    LLM backend (default: $JARVIS_DEFAULT_MODEL or local:llama3.1)
  --resume   resume from progress file (default: True if progress file exists)
  --dry-run  print URLs to process without making LLM calls
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCES = ROOT / "wiki" / "sources"
PROGRESS_FILE = ROOT / "raw" / "backlog_progress.json"

URL_RE = re.compile(r"https?://[^\s\)\]>\"']+")


def find_backlog_note() -> Path | None:
    for p in sorted(WIKI_SOURCES.glob("whatsapp_*.md")):
        return p
    return None


def extract_urls_from_note(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    urls = URL_RE.findall(text)
    # Deduplicate preserving order
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        url = url.rstrip(".,;)>")
        if url not in seen and url.startswith("http"):
            seen.add(url)
            result.append(url)
    return result


def already_processed_urls() -> set[str]:
    """Scan wiki/sources/ notes for URLs that already have a dedicated analysis note.

    Only counts URLs appearing in the `sources:` YAML frontmatter of notes
    that are NOT the whatsapp backlog note itself.
    """
    import re as _re
    sources_re = _re.compile(r'^\s*-\s+"?(https?://[^\s"]+)"?', _re.MULTILINE)
    found: set[str] = set()
    for md in WIKI_SOURCES.glob("*.md"):
        if md.name.startswith("whatsapp_"):
            continue  # skip the backlog note itself
        text = md.read_text(encoding="utf-8", errors="replace")
        for url in sources_re.findall(text):
            found.add(url.rstrip(".,;)>"))
    return found


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"processed": [], "failed": [], "skipped": []}


def save_progress(progress: dict) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


def process_url(url: str, model: str) -> dict:
    analyzer = ROOT / "tools" / "skills" / "content_analyzer.py"
    result = subprocess.run(
        [sys.executable, str(analyzer), url, "--model", model],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode == 0:
        return json.loads(result.stdout.strip())
    raise RuntimeError(result.stderr.strip()[:300])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default=None, help="WhatsApp links note path")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-resume", action="store_true", help="Ignore existing progress file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    import os
    model = args.model or os.environ.get("JARVIS_DEFAULT_MODEL", "local:llama3.1")

    # Find source note
    if args.source:
        source_note = Path(args.source)
    else:
        source_note = find_backlog_note()
    if not source_note or not source_note.exists():
        print("No WhatsApp backlog note found in wiki/sources/. Run whatsapp_parser.py first.", file=sys.stderr)
        sys.exit(1)

    print(f"Source: {source_note.relative_to(ROOT)}")
    all_urls = extract_urls_from_note(source_note)
    print(f"URLs in backlog note: {len(all_urls)}")

    # Load progress
    progress = {} if args.no_resume else load_progress()
    already_done: set[str] = set(progress.get("processed", [])) | set(progress.get("skipped", []))
    already_done |= already_processed_urls()

    # Filter
    pending = [u for u in all_urls if u not in already_done]
    print(f"Already processed/skipped: {len(all_urls) - len(pending)}")
    print(f"Pending: {len(pending)}")

    if args.limit:
        pending = pending[:args.limit]
        print(f"Limiting to {args.limit} URLs")

    if args.dry_run:
        print("\nDRY RUN — URLs to process:")
        for i, url in enumerate(pending, 1):
            print(f"  {i:3}. {url}")
        return

    if not pending:
        print("Nothing to do.")
        return

    print(f"\nProcessing {len(pending)} URLs with model={model}\n")

    done_count = 0
    fail_count = 0

    for i, url in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {url[:80]}", end=" ", flush=True)
        try:
            result = process_url(url, model)
            note = result.get("output", "?")
            title = result.get("title", "?")[:50]
            print(f"✓ {title} → {note}")
            progress.setdefault("processed", []).append(url)
            done_count += 1
        except subprocess.TimeoutExpired:
            print("⚠ timeout")
            progress.setdefault("failed", []).append(url)
            fail_count += 1
        except Exception as exc:
            print(f"✗ {str(exc)[:80]}")
            progress.setdefault("failed", []).append(url)
            fail_count += 1

        save_progress(progress)
        time.sleep(1)  # rate limiting for LLM calls

    print(f"\n── Summary ──────────────────────")
    print(f"  Processed: {done_count}")
    print(f"  Failed:    {fail_count}")
    print(f"  Progress:  {PROGRESS_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
