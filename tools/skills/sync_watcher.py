#!/usr/bin/env python3
"""Watch raw/ingest_queue and ingest supported files automatically."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "raw" / "ingest_queue"
CHAT_INGESTOR = ROOT / "tools" / "skills" / "chat_ingestor.py"
CONTENT_ANALYZER = ROOT / "tools" / "skills" / "content_analyzer.py"
VOICE_BRIDGE = ROOT / "tools" / "skills" / "voice_bridge.py"
RAW_ARCHIVE = ROOT / "raw" / "archive" / "ingest_queue"
SUPPORTED = {".json", ".pdf", ".md", ".txt", ".html", ".htm", ".rst", ".csv"}
URL_RE = re.compile(r"https?://[^\s\)\]>\"']+")


def wait_until_stable(path: Path, attempts: int = 5, delay: float = 0.5) -> bool:
    previous = -1
    for _ in range(attempts):
        if not path.exists():
            return False
        current = path.stat().st_size
        if current == previous:
            return True
        previous = current
        time.sleep(delay)
    return True


def notify_success(path: Path) -> None:
    subprocess.run([sys.executable, str(VOICE_BRIDGE), "notify", f"Ingesta completada: {path.name}"], check=False)


def first_url(path: Path) -> str | None:
    if path.suffix.lower() != ".txt":
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = URL_RE.search(text)
    if not match:
        return None
    return match.group(0).rstrip(".,;)>")


def archive_original(path: Path) -> Path:
    archive_dir = RAW_ARCHIVE / date.today().isoformat()
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / path.name
    counter = 2
    while target.exists():
        target = archive_dir / f"{path.stem}-{counter}{path.suffix}"
        counter += 1
    shutil.move(str(path), str(target))
    return target


def process(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED or not path.is_file():
        return
    if not wait_until_stable(path):
        return
    url = first_url(path)
    if url:
        origin = "whatsapp" if "whatsapp" in path.name.lower() else "queue"
        completed = subprocess.run(
            [sys.executable, str(CONTENT_ANALYZER), url, "--origin", origin],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout.strip())
        result["archived_to"] = str(archive_original(path))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        notify_success(path)
        return
    completed = subprocess.run([sys.executable, str(CHAT_INGESTOR), str(path), "--archive"], check=True, capture_output=True, text=True)
    print(completed.stdout.strip())
    notify_success(path)


def run_once() -> None:
    QUEUE.mkdir(parents=True, exist_ok=True)
    for path in sorted(QUEUE.iterdir()):
        process(path)


def watch() -> None:
    try:
        from watchdog.events import FileSystemEventHandler  # type: ignore
        from watchdog.observers import Observer  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"watchdog is required for watch mode: {exc}") from exc

    class Handler(FileSystemEventHandler):
        def on_created(self, event):  # type: ignore[no-untyped-def]
            if not event.is_directory:
                process(Path(event.src_path))

        def on_moved(self, event):  # type: ignore[no-untyped-def]
            if not event.is_directory:
                process(Path(event.dest_path))

    QUEUE.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(Handler(), str(QUEUE), recursive=False)
    observer.start()
    print(f"Watching {QUEUE}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Process current queue and exit.")
    args = parser.parse_args()
    if args.once:
        run_once()
    else:
        watch()


if __name__ == "__main__":
    main()
