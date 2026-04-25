from __future__ import annotations

from ..config import Settings
from ..schemas import DocCheckRequest, DocCheckResult, DocStatus
from .research import ResearchEngine


class Context7Client:
    """Wrapper around Context7 MCP or Perplexity fallback for doc checking."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._research = ResearchEngine(settings)

    def check_docs(self, request: DocCheckRequest) -> DocCheckResult:
        docs: list[DocStatus] = []
        for lib in request.libraries:
            docs.append(self._check_library(lib))
        vault_path: str | None = None
        if request.save_to_vault and docs:
            vault_path = self._save_to_vault(docs)
        return DocCheckResult(docs=docs, vault_path=vault_path)

    def _check_library(self, library: str) -> DocStatus:
        from ..schemas import ResearchQuery, ResearchBackend
        query = ResearchQuery(
            query=f"Latest version, key changes, and current documentation for {library}",
            backend="perplexity",  # type: ignore[arg-type]
            save_to_vault=False,
        )
        try:
            result = self._research.query(query, None)
            if result.supported:
                return DocStatus(
                    library=library,
                    summary=result.answer[:400],
                    source=result.citations[0] if result.citations else "perplexity",
                    available=True,
                )
        except Exception:
            pass
        return DocStatus(library=library, summary="No disponible — verificar conexión o PERPLEXITY_API_KEY", available=False)

    def _save_to_vault(self, docs: list[DocStatus]) -> str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        dest_dir = self.settings.vault_dir / "02-Research" / "doc-snapshots"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{date_str}-doc-check.md"
        lines = [
            "---",
            "title: Doc Check Snapshot",
            "type: reference",
            f"created: {date_str}",
            "---",
            "",
            f"# Doc Check — {date_str}",
            "",
        ]
        for doc in docs:
            status = "✅" if doc.available else "❌"
            lines.append(f"## {status} {doc.library}")
            if doc.version:
                lines.append(f"**Versión:** {doc.version}")
            lines.append("")
            lines.append(doc.summary)
            lines.append("")
        dest.write_text("\n".join(lines), encoding="utf-8")
        return str(dest.relative_to(self.settings.root_dir))
