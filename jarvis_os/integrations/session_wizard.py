from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from ..config import Settings
from ..schemas import ContextFile, SessionWizardRequest, SessionWizardResult


_CATEGORY_ORDER = ["models", "stack", "workflow", "quality", "personal", "profiles"]


class SessionWizard:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.contexts_dir = settings.contexts_dir

    def list_contexts(self) -> dict[str, list[ContextFile]]:
        if not self.contexts_dir.exists():
            return {}
        result: dict[str, list[ContextFile]] = {}
        for category in _CATEGORY_ORDER:
            cat_dir = self.contexts_dir / category
            if not cat_dir.is_dir():
                continue
            files = []
            for md_file in sorted(cat_dir.glob("*.md")):
                ctx = self._parse_context_file(md_file, category)
                if ctx:
                    files.append(ctx)
            if files:
                result[category] = files
        return result

    def list_profiles(self) -> list[ContextFile]:
        return self.list_contexts().get("profiles", [])

    def generate_claude_md(self, request: SessionWizardRequest) -> SessionWizardResult:
        sources: list[str] = []
        parts: list[str] = [
            "# CLAUDE.md — Sesión generada por JarvisOS Session Wizard",
            f"# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        paths = list(request.contexts)
        if request.profile:
            profile_path = self.contexts_dir / request.profile
            if profile_path.exists():
                paths.insert(0, request.profile)

        for rel_path in paths:
            full_path = self.contexts_dir / rel_path
            if not full_path.exists():
                continue
            content = full_path.read_text(encoding="utf-8")
            body = self._strip_frontmatter(content)
            if body.strip():
                parts.append(body.strip())
                parts.append("")
                sources.append(rel_path)

        claude_md = "\n".join(parts)
        saved_path: str | None = None

        if request.save_profile and request.profile_name:
            saved_path = self._save_session_profile(claude_md, request.profile_name)

        return SessionWizardResult(claude_md=claude_md, sources=sources, saved_path=saved_path)

    def _save_session_profile(self, content: str, name: str) -> str:
        dest_dir = self.settings.vault_dir / "04-Skills" / "contexts"
        dest_dir.mkdir(parents=True, exist_ok=True)
        slug = name.lower().replace(" ", "-").replace("/", "-")
        date_str = datetime.now().strftime("%Y-%m-%d")
        dest = dest_dir / f"session-{date_str}-{slug}.md"
        dest.write_text(content, encoding="utf-8")
        return str(dest.relative_to(self.settings.root_dir))

    def _parse_context_file(self, path: Path, category: str) -> ContextFile | None:
        try:
            content = path.read_text(encoding="utf-8")
            meta = self._extract_frontmatter(content)
            return ContextFile(
                name=meta.get("name", path.stem),
                category=category,
                path=str(path.relative_to(self.contexts_dir)),
                description=meta.get("description", ""),
            )
        except Exception:
            return None

    def _extract_frontmatter(self, content: str) -> dict:
        if not content.startswith("---"):
            return {}
        try:
            end = content.index("---", 3)
            return yaml.safe_load(content[3:end]) or {}
        except (ValueError, yaml.YAMLError):
            return {}

    def _strip_frontmatter(self, content: str) -> str:
        if not content.startswith("---"):
            return content
        try:
            end = content.index("---", 3)
            return content[end + 3:]
        except ValueError:
            return content
