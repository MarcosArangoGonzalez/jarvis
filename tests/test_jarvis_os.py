from __future__ import annotations

import json

from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.markitdown import MarkItDownIngestor
from jarvis_os.integrations.security import SecurityRegexScanner
from jarvis_os.integrations.vault import VaultMigrator
from jarvis_os.kernel.service import KernelService
from jarvis_os.schemas import SecurityScanRequest, VaultSearchQuery


def make_kernel() -> KernelService:
    return KernelService(get_settings())


def test_overview_has_metrics_and_recent_notes() -> None:
    overview = make_kernel().get_overview()
    assert overview.metrics
    assert overview.recent_notes


def test_vault_search_returns_results_for_rag() -> None:
    result = make_kernel().search_vault(VaultSearchQuery(query="RAG"))
    assert result.mode == "text"
    assert result.total >= 1


def test_semantic_vault_search_degrades_to_textual_fallback() -> None:
    result = make_kernel().search_vault(VaultSearchQuery(query="RAG", mode="semantic"))
    assert result.mode == "semantic"
    if result.supported:
        assert "vault-index.db" in result.notice
    else:
        assert "fallback textual" in result.notice
    assert result.total >= 1


def test_skills_discover_legacy_workspace_files() -> None:
    skills = make_kernel().get_skills()
    assert any(item.id == "content-analyzer" for item in skills)


def test_app_registers_expected_routes() -> None:
    app = create_app(enable_scheduler=False)
    paths = {route.path for route in app.routes}
    expected = {
        "/",
        "/architecture",
        "/vault/search",
        "/sessions",
        "/skills",
        "/jobs",
        "/terminal",
        "/research",
        "/graph",
        "/notepad",
        "/newsletter",
        "/integrations",
        "/api/overview",
        "/api/topology",
        "/api/vault/search",
        "/api/vault/graph",
        "/api/notes/daily/today",
        "/api/notes/{path:path}",
        "/api/calendar/events",
        "/api/newsletter/generate",
        "/api/newsletter/status/{job_id}",
        "/newsletter/{target_date}",
        "/newsletter/{target_date}/html",
        "/api/jobs",
        "/api/inbox",
        "/api/ingestions",
        "/api/security/scan",
        "/api/security/findings",
        "/api/sessions/{session_id}",
        "/api/research/query",
        "/api/research/history",
        "/api/terminal/sessions",
        "/ws/terminal/{session_id}",
        "/api/skills/{skill_id}",
    }
    assert expected.issubset(paths)


def test_health_snapshot_job_succeeds() -> None:
    job = make_kernel().create_job(kind="health_snapshot")
    assert job.status == "succeeded"


def test_inbox_process_job_records_ingestions(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    inbox_file = settings.vault_inbox_dir / "sample.md"
    inbox_file.parent.mkdir(parents=True)
    inbox_file.write_text("# Sample\n\n## Section\n\nBody", encoding="utf-8")
    kernel = KernelService(settings)
    job = kernel.create_job(kind="inbox_process")
    assert job.status == "succeeded"
    assert kernel.get_ingestions()


def test_security_scan_job_persists_findings(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    sample = settings.root_dir / "sample.env"
    sample.write_text("AWS=AKIAABCDEFGHIJKLMNOP\n", encoding="utf-8")
    kernel = KernelService(settings)
    job = kernel.create_job(kind="security_scan", payload={"path": str(sample), "mode": "artifact"})
    assert job.status == "succeeded"
    assert any(finding.pattern_id == "aws-key" for finding in kernel.get_security_findings())
    persisted = json.loads((settings.runtime_dir / "security-findings.json").read_text(encoding="utf-8"))
    assert any(finding["pattern_id"] == "aws-key" for finding in persisted)


def test_markitdown_convert_job_persists_ingestion(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    source = settings.vault_inbox_dir / "convert-me.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Convert Me\n\n## Context\n\nBody", encoding="utf-8")
    kernel = KernelService(settings)
    job = kernel.create_job(kind="markitdown_convert", payload={"path": str(source)})
    assert job.status == "succeeded"
    assert job.result is not None
    assert job.result.artifacts
    ingestions = kernel.get_ingestions()
    assert len(ingestions) == 1
    assert ingestions[0].status == "converted"
    assert (settings.root_dir / ingestions[0].output_path).exists()
    persisted = json.loads((settings.runtime_dir / "ingestions.json").read_text(encoding="utf-8"))
    assert persisted[0]["title"] == "Convert Me"
    assert persisted[0]["status"] == "converted"


def test_vault_migration_copies_wiki_into_vault_layout(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    source = settings.wiki_dir / "sources" / "rag-note.md"
    source.parent.mkdir(parents=True)
    source.write_text("---\ntitle: RAG Note\nSummary: test\n---\n# RAG Note\n", encoding="utf-8")
    stats = VaultMigrator(settings).migrate()
    assert stats["copied"] >= 2
    assert (settings.vault_dir / "02-Research" / "sources" / "rag-note.md").exists()
    claude_md = (settings.vault_dir / "CLAUDE.md").read_text(encoding="utf-8")
    for section in (
        "## Pipeline RAG",
        "## MarkItDown",
        "## Regex de seguridad",
        "## Stack de desarrollo",
        "## Búsqueda en vault",
    ):
        assert section in claude_md


def test_markitdown_ingestor_uses_text_fallback_for_markdown(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    inbox_file = settings.vault_inbox_dir / "sample.md"
    inbox_file.parent.mkdir(parents=True)
    inbox_file.write_text("# Sample\n\n## Section\n\nBody", encoding="utf-8")
    result = MarkItDownIngestor(settings).convert(inbox_file)
    assert result.status == "converted"
    assert result.chunks == 1
    assert (settings.root_dir / result.output_path).exists()


def test_security_scanner_detects_aws_key_and_jwt(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    sample = settings.root_dir / "sample.env"
    sample.write_text(
        "AWS=AKIAABCDEFGHIJKLMNOP\nTOKEN=eyABCDEFGHIJKL.eyABCDEFGHIJKL.signaturepart\n",
        encoding="utf-8",
    )
    result = SecurityRegexScanner(settings).scan(SecurityScanRequest(path=str(sample)))
    pattern_ids = {finding.pattern_id for finding in result.findings}
    assert "aws-key" in pattern_ids
    assert "jwt" in pattern_ids


def _temp_settings(root) -> Settings:
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
