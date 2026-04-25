from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from ..config import Settings
from ..schemas import IngestionResult, InboxItem


class MarkItDownIngestor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def list_inbox(self) -> list[InboxItem]:
        self.settings.vault_inbox_dir.mkdir(parents=True, exist_ok=True)
        items: list[InboxItem] = []
        for path in sorted(self.settings.vault_inbox_dir.iterdir()):
            if path.is_dir() or path.name.startswith("."):
                continue
            items.append(
                InboxItem(
                    path=str(path.relative_to(self.settings.root_dir)),
                    name=path.name,
                    suffix=path.suffix.lower(),
                    size_bytes=path.stat().st_size,
                    updated_at=datetime.fromtimestamp(path.stat().st_mtime),
                )
            )
        return items

    def convert(self, source: Path) -> IngestionResult:
        source = source if source.is_absolute() else self.settings.root_dir / source
        if not source.exists():
            return IngestionResult(source_path=str(source), status="failed", error="Source file does not exist.")
        try:
            text = self._convert_to_markdown(source)
        except Exception as exc:
            return IngestionResult(source_path=str(source), status="failed", error=str(exc))
        title = self._title_from_markdown(text) or source.stem.replace("-", " ").title()
        output = self.settings.vault_dir / "02-Research" / f"{self._slug(title)}.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        content = self._note_content(title, source, text)
        output.write_text(content, encoding="utf-8")
        return IngestionResult(
            source_path=str(source.relative_to(self.settings.root_dir)),
            output_path=str(output.relative_to(self.settings.root_dir)),
            status="converted",
            title=title,
            chunks=self._count_h2_chunks(text),
        )

    def _convert_to_markdown(self, source: Path) -> str:
        try:
            from markitdown import MarkItDown  # type: ignore
        except Exception:
            if source.suffix.lower() in {".md", ".txt", ".csv", ".json", ".xml", ".html"}:
                return source.read_text(encoding="utf-8", errors="replace")
            raise RuntimeError("MarkItDown is not installed and this file type has no text fallback.")
        converter = MarkItDown(enable_plugins=True)
        result = converter.convert(str(source))
        return result.text_content

    @staticmethod
    def _title_from_markdown(text: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return ""

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
        return slug[:80] or "untitled"

    @staticmethod
    def _count_h2_chunks(text: str) -> int:
        return max(1, len(re.findall(r"^##\s+", text, flags=re.MULTILINE)))

    @staticmethod
    def _note_content(title: str, source: Path, text: str) -> str:
        today = datetime.now().date().isoformat()
        excerpt = text.strip()
        return f"""---
title: "{title}"
type: source
status: NEW
tags:
  - markitdown
  - inbox
created: {today}
updated: {today}
tokens_consumed: 0
sources:
  - "{source}"
Summary: "Converted from 05-Inbox with MarkItDown pipeline."
requires_verification: true
validated: ~
---

# {title}

## Source

- Path: {source}
- Converter: MarkItDown

## Raw Extract

{excerpt}
"""
