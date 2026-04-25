from __future__ import annotations

from pathlib import Path

import httpx
import pytest

import jarvis_os.app as app_module
from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.vault import VaultMigrator


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_vault_graph_builds_nodes(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "a.md", "A", "See [[B]].")
    _write_note(settings.vault_dir / "02-Research" / "b.md", "B", "Backlink target.")
    graph = VaultMigrator(settings).build_graph()
    assert {node.title for node in graph.nodes} == {"A", "B"}
    assert len(graph.edges) == 1


def test_wikilinks_parsed_as_edges(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "03-Dev" / "source.md", "Source", "[[Target Note]]")
    _write_note(settings.vault_dir / "03-Dev" / "target-note.md", "Target Note", "")
    graph = VaultMigrator(settings).build_graph(folder="dev")
    assert graph.edges[0].source.endswith("source.md")
    assert graph.edges[0].target.endswith("target-note.md")


def test_graph_api_returns_json(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "a.md", "A", "[[B]]")
    _write_note(settings.vault_dir / "02-Research" / "b.md", "B", "")
    monkeypatch.setattr(app_module, "get_settings", lambda: settings)
    app = create_app(enable_scheduler=False)
    paths = {route.path for route in app.routes}
    assert "/api/vault/graph" in paths


@pytest.mark.anyio
async def test_graph_api_json_payload(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "a.md", "A", "[[B]]")
    _write_note(settings.vault_dir / "02-Research" / "b.md", "B", "")
    monkeypatch.setattr(app_module, "get_settings", lambda: settings)
    transport = httpx.ASGITransport(app=create_app(enable_scheduler=False))
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/vault/graph")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["nodes"]) == 2
    assert payload["edges"] == [{"source": "vault/02-Research/a.md", "target": "vault/02-Research/b.md"}]


def _write_note(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\n---\n# {title}\n\n{body}\n', encoding="utf-8")


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
