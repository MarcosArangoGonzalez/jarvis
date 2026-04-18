#!/usr/bin/env python3
"""Convert raw chats/documents into JarvisOS wiki source notes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCES = ROOT / "wiki" / "sources"
RAW_ARCHIVE = ROOT / "raw" / "archive" / "ingest_queue"
SUPPORTED_EXTENSIONS = {".json", ".md", ".pdf", ".txt", ".html", ".htm", ".rst", ".csv"}


@dataclass
class IngestResult:
    source: Path
    output: Path
    archived_to: Path | None
    status: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) * 4 // 3) if text.strip() else 0


def summarize(text: str, max_chars: int = 360) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "No readable body extracted yet."
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "\n" + "\n".join(f"  - {yaml_scalar(value)}" for value in values)


def extract_messages_from_json(data: Any) -> str:
    if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
        lines: list[str] = []
        for message in data["messages"]:
            if isinstance(message, dict):
                role = message.get("role") or message.get("author") or message.get("speaker") or "unknown"
                content = message.get("content") or message.get("text") or message.get("message") or ""
                if isinstance(content, list):
                    content = " ".join(str(item) for item in content)
                lines.append(f"### {role}\n\n{content}".strip())
            else:
                lines.append(str(message))
        return "\n\n".join(lines)
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_pdf(path: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return "", f"needs_manual_review: pypdf unavailable ({exc})"

    try:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n\n".join(page.strip() for page in pages if page.strip())
        if not text:
            return "", "needs_manual_review: no extractable text"
        return text, "draft"
    except Exception as exc:  # pragma: no cover - file dependent
        return "", f"needs_manual_review: pdf extraction failed ({exc})"


def read_source(path: Path) -> tuple[str, str, list[str]]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        title = data.get("title") if isinstance(data, dict) else None
        return extract_messages_from_json(data), "draft", ["chat", "import", slugify(str(title or path.stem))]
    if suffix in {".md", ".txt", ".rst"}:
        return path.read_text(encoding="utf-8", errors="replace"), "draft", ["source", "import"]
    if suffix == ".pdf":
        text, status = read_pdf(path)
        return text, status, ["pdf", "source", "import"]
    if suffix in {".html", ".htm"}:
        raw = path.read_text(encoding="utf-8", errors="replace")
        # Strip HTML tags for plain text body
        import re
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s{2,}", "\n", text).strip()
        return text, "draft", ["html", "source", "import"]
    if suffix == ".csv":
        return path.read_text(encoding="utf-8", errors="replace"), "draft", ["csv", "source", "import"]

    raise ValueError(f"Unsupported file type: {suffix}")


def build_markdown(path: Path, body: str, status: str, tags: list[str]) -> str:
    today = date.today().isoformat()
    source_ref = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    title = path.stem.replace("-", " ").replace("_", " ").strip().title() or "Untitled"
    frontmatter = [
        "---",
        f"title: {yaml_scalar(title)}",
        f"type: {yaml_scalar('source')}",
        f"status: {yaml_scalar(status)}",
        f"tags: {yaml_list(tags)}",
        f"created: {today}",
        f"updated: {today}",
        f"tokens_consumed: {estimate_tokens(body)}",
        f"sources: {yaml_list([source_ref])}",
        f"Summary: {yaml_scalar(summarize(body))}",
        "---",
        "",
        f"# {title}",
        "",
        "## Source Body",
        "",
        body or "No body extracted. Manual review required.",
        "",
    ]
    return "\n".join(frontmatter)


def unique_output_path(base_name: str) -> Path:
    WIKI_SOURCES.mkdir(parents=True, exist_ok=True)
    candidate = WIKI_SOURCES / f"{slugify(base_name)}.md"
    counter = 2
    while candidate.exists():
        candidate = WIKI_SOURCES / f"{slugify(base_name)}-{counter}.md"
        counter += 1
    return candidate


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


def ingest(path: Path, archive: bool = False) -> IngestResult:
    source = path.resolve()
    body, status, tags = read_source(source)
    output = unique_output_path(source.stem)
    output.write_text(build_markdown(source, body, status, tags), encoding="utf-8")
    archived_to = archive_original(source) if archive else None
    return IngestResult(source=source, output=output, archived_to=archived_to, status=status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--archive", action="store_true", help="Move original into raw/archive after ingest.")
    args = parser.parse_args()

    result = ingest(args.input, archive=args.archive)
    print(json.dumps({
        "source": str(result.source),
        "output": str(result.output),
        "archived_to": str(result.archived_to) if result.archived_to else None,
        "status": result.status,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
