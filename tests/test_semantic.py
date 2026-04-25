from __future__ import annotations

from pathlib import Path

from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.semantic import SemanticIndex
from jarvis_os.kernel.service import KernelService
from jarvis_os.schemas import VaultSearchQuery


def test_vault_reindex_creates_db(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "rag.md", "RAG", "retrieval augmented generation")
    stats = SemanticIndex(settings).reindex()
    assert stats["indexed_chunks"] >= 1
    assert (settings.runtime_dir / "vault-index.db").exists()


def test_semantic_search_returns_supported_true(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "rag.md", "RAG", "retrieval augmented generation")
    kernel = KernelService(settings)
    job = kernel.create_job(kind="vault_reindex")
    result = kernel.search_vault(VaultSearchQuery(query="retrieval", mode="semantic"))
    assert job.status == "succeeded"
    assert result.supported is True
    assert result.total == 1
    assert result.items[0].title == "RAG"


def test_degradation_when_index_missing(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "rag.md", "RAG", "retrieval augmented generation")
    result = KernelService(settings).search_vault(VaultSearchQuery(query="retrieval", mode="semantic"))
    assert result.supported is False
    assert "vault_reindex" in result.notice
    assert result.total == 1


def _write_note(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\nSummary: "{body}"\n---\n# {title}\n\n{body}\n', encoding="utf-8")


def _temp_settings(root: Path) -> Settings:
    return Settings(
        root_dir=root,
        wiki_dir=root / "wiki",
        vault_dir=root / "vault",
        vault_inbox_dir=root / "vault" / "05-Inbox",
        vault_assets_dir=root / "vault" / "assets",
        tasks_dir=root / "wiki" / "tasks",
        logs_dir=root / "wiki" / "logs" / "core",
        skills_dir=root / "tools" / "skills",
        mcp_config_path=root / "tools" / "mcp_servers" / "mcp_config.json",
        runtime_dir=root / "data" / "runtime",
        templates_dir=get_settings().templates_dir,
        static_dir=get_settings().static_dir,
        session_manager_path=root / ".jarvis" / "session_manager.md",
        contexts_dir=root / "contexts",
        insights_dir=root / "vault" / "03-Dev" / "insights",
    )
