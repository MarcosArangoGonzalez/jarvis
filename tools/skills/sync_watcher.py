#!/usr/bin/env python3
"""Watch raw/ingest_queue and ingest supported files automatically."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "raw" / "ingest_queue"
CHAT_INGESTOR = ROOT / "tools" / "skills" / "chat_ingestor.py"
VOICE_BRIDGE = ROOT / "tools" / "skills" / "voice_bridge.py"
SUPPORTED = {".json", ".pdf", ".md", ".txt", ".html", ".htm", ".rst", ".csv"}


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


def process(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED or not path.is_file():
        return
    if not wait_until_stable(path):
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
