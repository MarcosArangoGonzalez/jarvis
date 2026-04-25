from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from ..config import Settings
from ..schemas import MCPServerStatus, Session, SkillDefinition, VaultNoteSummary


class LegacyWorkspace:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def list_skills(self) -> list[SkillDefinition]:
        skills: list[SkillDefinition] = []
        for path in sorted(self.settings.skills_dir.glob("*")):
            if path.is_dir() or path.name == "README.md":
                continue
            if path.suffix not in {".py", ".sh", ".js", ".desktop"}:
                continue
            skills.append(
                SkillDefinition(
                    id=path.stem.replace("_", "-"),
                    name=path.stem.replace("_", " ").title(),
                    kind=path.suffix.removeprefix("."),
                    entrypoint=str(path.relative_to(self.settings.root_dir)),
                    description=self._extract_description(path),
                    tags=self._infer_skill_tags(path),
                    supports_tokens=path.suffix == ".py",
                    health_status="healthy" if path.exists() else "degraded",
                )
            )
        return skills

    def list_integrations(self) -> list[MCPServerStatus]:
        expected = {
            "obsidian": "Vault access through Obsidian MCP.",
            "markitdown": "Document conversion into Markdown for the RAG pipeline.",
            "linear": "Issues, sprints, and roadmap state.",
            "notion": "Notion workspace documents and databases.",
            "gdrive": "Google Drive documents and research sources.",
            "github": "Repositories, pull requests, issues, and CI state.",
        }
        if not self.settings.mcp_config_path.exists():
            return [
                MCPServerStatus(id=key, name=key.replace("_", " ").title(), description=desc, configured=False)
                for key, desc in sorted(expected.items())
            ]
        payload = json.loads(self.settings.mcp_config_path.read_text(encoding="utf-8"))
        results: list[MCPServerStatus] = []
        for key, config in sorted(payload.get("mcpServers", {}).items()):
            normalized = "gdrive" if key == "google_drive" else key
            results.append(
                MCPServerStatus(
                    id=normalized,
                    name=normalized.replace("_", " ").title(),
                    description=config.get("description", expected.get(normalized, "")),
                    configured=True,
                    available=True,
                    authenticated=False,
                )
            )
        configured = {item.id for item in results}
        for key, desc in sorted(expected.items()):
            if key not in configured:
                results.append(
                    MCPServerStatus(
                        id=key,
                        name=key.replace("_", " ").title(),
                        description=desc,
                        configured=False,
                        available=False,
                    )
                )
        return results

    def recent_notes(self, *, limit: int = 8, category: str = "all") -> list[VaultNoteSummary]:
        notes = self._all_notes()
        if category != "all":
            notes = [note for note in notes if self._categorize_path(Path(note.path)) == category]
        return sorted(notes, key=lambda item: item.updated_at, reverse=True)[:limit]

    def search_notes(
        self,
        *,
        query: str,
        folder: str,
        tags: list[str],
        date_filter: str,
    ) -> list[VaultNoteSummary]:
        tokens = [token.lower() for token in query.split() if token.strip()]
        results: list[VaultNoteSummary] = []
        threshold = self._date_threshold(date_filter)
        for path in self.settings.wiki_dir.rglob("*.md"):
            if path.name.startswith("."):
                continue
            category = self._categorize_path(path)
            if folder != "all" and category != folder:
                continue
            note = self._read_note(path)
            if threshold and note.updated_at < threshold:
                continue
            if tags and not set(tags).intersection(set(note.tags)):
                continue
            haystack = f"{note.title}\n{note.summary}\n{path.read_text(encoding='utf-8', errors='replace')[:4000]}".lower()
            if tokens and not all(token in haystack for token in tokens):
                continue
            results.append(note)
        return sorted(results, key=lambda item: item.updated_at, reverse=True)[:30]

    def recent_sessions(self, *, limit: int = 6) -> list[Session]:
        log_path = self.settings.logs_dir / "jarvis-log.md"
        sessions: list[Session] = []
        if log_path.exists():
            text = log_path.read_text(encoding="utf-8", errors="replace")
            blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)
            for block in reversed(blocks):
                heading, _, body = block.partition("\n")
                heading = heading.strip()
                if not heading:
                    continue
                if "session end" not in heading.lower():
                    continue
                stamp = heading.split("—", 1)[0].strip()
                started_at = self._parse_datetime(stamp)
                summary = ""
                for line in body.splitlines():
                    if line.strip().startswith("- "):
                        summary = line.strip()[2:]
                        break
                sessions.append(
                    Session(
                        id=re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-"),
                        title=heading,
                        started_at=started_at,
                        finished_at=started_at,
                        status="completed",
                        project="JarvisOS",
                        role="Session Log",
                        summary=summary or "Session event recorded in core log.",
                        source_path=str(log_path.relative_to(self.settings.root_dir)),
                    )
                )
                if len(sessions) >= limit:
                    break
        if self.settings.session_manager_path.exists():
            sessions.insert(
                0,
                Session(
                    id="active-session",
                    title="Active session protocol",
                    started_at=datetime.fromtimestamp(self.settings.session_manager_path.stat().st_mtime),
                    status="active",
                    project="JarvisOS",
                    role="Senior Architect",
                    summary="Canonical session bootstrap and handover protocol.",
                    source_path=str(self.settings.session_manager_path.relative_to(self.settings.root_dir)),
                ),
            )
        return sessions[:limit]

    def task_table(self, *, limit: int = 6) -> list[dict[str, str]]:
        path = self.settings.tasks_dir / "index.md"
        if not path.exists():
            return []
        rows: list[dict[str, str]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("| P"):
                continue
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 7:
                continue
            rows.append(
                {
                    "priority": parts[0],
                    "title": parts[1],
                    "project": parts[2],
                    "status": parts[4],
                }
            )
        return rows[:limit]

    def vault_counts(self) -> dict[str, int]:
        counts = {"all": 0, "daily": 0, "projects": 0, "research": 0, "dev": 0, "skills": 0}
        for path in self._knowledge_root().rglob("*.md"):
            if path.name.startswith("."):
                continue
            counts["all"] += 1
            counts[self._categorize_path(path)] += 1
        return counts

    def _all_notes(self) -> list[VaultNoteSummary]:
        notes: list[VaultNoteSummary] = []
        for path in self._knowledge_root().rglob("*.md"):
            if path.name.startswith("."):
                continue
            notes.append(self._read_note(path))
        return notes

    def _knowledge_root(self) -> Path:
        if self.settings.vault_dir.exists():
            vault_notes = [path for path in self.settings.vault_dir.rglob("*.md") if path.name != "CLAUDE.md"]
            if vault_notes:
                return self.settings.vault_dir
        return self.settings.wiki_dir

    def _read_note(self, path: Path) -> VaultNoteSummary:
        text = path.read_text(encoding="utf-8", errors="replace")
        title = self._match_frontmatter(text, "title") or path.stem.replace("-", " ").title()
        summary = self._match_frontmatter(text, "Summary") or ""
        tags = re.findall(r'^\s*-\s+"?([a-zA-Z0-9:_#-]+)"?\s*$', text, flags=re.MULTILINE)
        return VaultNoteSummary(
            path=str(path.relative_to(self.settings.root_dir)),
            title=title,
            summary=summary[:220],
            tags=tags[:6],
            folder=self._categorize_path(path),
            updated_at=datetime.fromtimestamp(path.stat().st_mtime),
        )

    @staticmethod
    def _match_frontmatter(text: str, key: str) -> str:
        match = re.search(rf"^{re.escape(key)}:\s*\"?(.*?)\"?\s*$", text, flags=re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_description(path: Path) -> str:
        text = path.read_text(encoding="utf-8", errors="replace")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if first_line.startswith("#!"):
            for line in text.splitlines()[1:8]:
                line = line.strip().strip('"').strip("'")
                if line:
                    return line.removeprefix("#").strip()
        return first_line.strip().strip("#").strip()[:120]

    @staticmethod
    def _infer_skill_tags(path: Path) -> list[str]:
        stem = path.stem.lower()
        tags = []
        for token in ("whatsapp", "voice", "ingest", "wiki", "session", "storage", "ci"):
            if token in stem:
                tags.append(token)
        return tags or ["jarvis"]

    @staticmethod
    def _categorize_path(path: Path) -> str:
        raw = str(path).lower()
        if "/vault/00-daily/" in raw:
            return "daily"
        if "/vault/01-projects/" in raw:
            return "projects"
        if "/vault/02-research/" in raw:
            return "research"
        if "/vault/03-dev/" in raw:
            return "dev"
        if "/vault/04-skills/" in raw:
            return "skills"
        if "/wiki/tasks/" in raw or "/wiki/logs/" in raw:
            return "daily"
        if "/wiki/projects/" in raw:
            return "projects"
        if "/wiki/analyses/" in raw or "/wiki/sources/" in raw:
            return "research"
        if "/wiki/patterns/" in raw or "/wiki/concepts/" in raw:
            return "dev"
        return "skills" if "/wiki/entities/" in raw else "research"

    @staticmethod
    def _date_threshold(date_filter: str) -> datetime | None:
        now = datetime.now()
        if date_filter == "week":
            return now - timedelta(days=7)
        if date_filter == "month":
            return now - timedelta(days=30)
        return None

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
