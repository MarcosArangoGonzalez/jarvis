from __future__ import annotations

import shutil
from pathlib import Path

from ..config import Settings


class VaultMigrator:
    """Non-destructive wiki -> vault copier for the Personal OS v2 layout."""

    FOLDERS = ("00-Daily", "01-Projects", "02-Research", "03-Dev", "04-Skills", "05-Inbox", "assets")

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ensure_layout(self) -> list[Path]:
        created: list[Path] = []
        self.settings.vault_dir.mkdir(parents=True, exist_ok=True)
        for folder in self.FOLDERS:
            path = self.settings.vault_dir / folder
            if not path.exists():
                path.mkdir(parents=True)
                created.append(path)
        return created

    def migrate(self, *, limit: int | None = None) -> dict[str, int]:
        self.ensure_layout()
        copied = 0
        skipped = 0
        for source in sorted(self.settings.wiki_dir.rglob("*.md")):
            target = self._target_for(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                skipped += 1
                continue
            shutil.copy2(source, target)
            copied += 1
            if limit is not None and copied >= limit:
                break
        claude_md = self.settings.vault_dir / "CLAUDE.md"
        if not claude_md.exists():
            claude_md.write_text(self._default_claude_md(), encoding="utf-8")
            copied += 1
        return {"copied": copied, "skipped": skipped}

    def _target_for(self, source: Path) -> Path:
        rel = source.relative_to(self.settings.wiki_dir)
        raw = str(rel).lower()
        if raw.startswith("tasks/") or raw.startswith("logs/"):
            base = "00-Daily"
        elif raw.startswith("projects/"):
            base = "01-Projects"
        elif raw.startswith("sources/") or raw.startswith("analyses/") or raw.startswith("areas/"):
            base = "02-Research"
        elif raw.startswith("patterns/") or raw.startswith("concepts/"):
            base = "03-Dev"
        else:
            base = "04-Skills"
        return self.settings.vault_dir / base / rel

    @staticmethod
    def _default_claude_md() -> str:
        return """# Personal OS - CLAUDE.md

Motor: Claude Code
Base de conocimiento: Obsidian-compatible vault
Integraciones: MCP servers

## Capas

- Dashboard / interfaz unificada
- Claude Code / kernel agentic
- Modulos: Dev, Research, Projects, Daily OS
- MCP Servers
- Pipeline RAG: MarkItDown, chunks, retrieval
- Vault Obsidian como sistema nervioso
"""
