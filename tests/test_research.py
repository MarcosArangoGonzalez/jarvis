from __future__ import annotations

from pathlib import Path

import httpx
import pytest

import jarvis_os.app as app_module
from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.research import ResearchEngine
from jarvis_os.kernel.service import KernelService
from jarvis_os.schemas import ResearchQuery


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_perplexity_backend_without_key_degrades(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    result = ResearchEngine(_temp_settings(tmp_path)).query(ResearchQuery(query="AI news", backend="perplexity"))
    assert result.supported is False
    assert "PERPLEXITY_API_KEY" in result.notice


def test_research_save_to_vault_creates_note(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    engine = ResearchEngine(settings)
    result = engine.query(ResearchQuery(query="RAG evaluation", backend="notebooklm", save_to_vault=True))
    assert result.vault_path is not None
    output = settings.root_dir / result.vault_path
    assert output.exists()
    assert "Research - RAG evaluation" in output.read_text(encoding="utf-8")


def test_ollama_fallback_when_no_local_api(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    note = settings.vault_dir / "02-Research" / "rag-note.md"
    note.parent.mkdir(parents=True)
    note.write_text('---\ntitle: "RAG Note"\nSummary: "Useful retrieval context."\n---\n# RAG Note\n', encoding="utf-8")
    result = KernelService(settings).run_research(ResearchQuery(query="RAG", backend="ollama", model="missing-model"))
    assert result.supported is False
    assert "vault context fallback" in result.notice
    assert "RAG Note" in result.answer


def test_research_routes_registered() -> None:
    app = create_app(enable_scheduler=False)
    paths = {route.path for route in app.routes}
    assert {"/research", "/api/research/query", "/api/research/history"}.issubset(paths)


@pytest.mark.anyio
async def test_research_api_persists_history(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    monkeypatch.setattr(app_module, "get_settings", lambda: _temp_settings(tmp_path))
    app = create_app(enable_scheduler=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/research/query", json={"query": "agentic RAG", "backend": "perplexity"})
        history = await client.get("/api/research/history")
    assert response.status_code == 200
    assert history.status_code == 200
    assert any(item["query"] == "agentic RAG" for item in history.json())


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
