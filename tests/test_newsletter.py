from __future__ import annotations

from datetime import date
from pathlib import Path

import httpx
import pytest

import jarvis_os.app as app_module
from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.newsletter import NewsletterEngine
from jarvis_os.kernel.service import KernelService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_newsletter_generate_creates_files(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "claude.md", "Claude MCP", "claude mcp agent python")
    result = NewsletterEngine(settings).generate(target_date=date(2026, 4, 25), export_pdf=False)
    assert result.items_total >= 1
    assert (settings.root_dir / result.md_path).exists()
    assert (settings.root_dir / result.html_path).exists()


def test_newsletter_html_contains_sections(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "claude.md", "Claude MCP", "claude mcp agent python")
    result = NewsletterEngine(settings).generate(target_date=date(2026, 4, 25), export_pdf=False)
    html = (settings.root_dir / result.html_path).read_text(encoding="utf-8")
    assert "JarvisOS Daily" in html
    assert "Tecnología &amp; IA" in html


def test_newsletter_job_records_artifacts(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "claude.md", "Claude MCP", "claude mcp agent python")
    job = KernelService(settings).create_job(kind="newsletter_generate", payload={"date": "2026-04-25", "export_pdf": False})
    assert job.status == "succeeded"
    assert job.result is not None
    assert any(artifact.label == "HTML" for artifact in job.result.artifacts)


@pytest.mark.anyio
async def test_newsletter_api_generates(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    _write_note(settings.vault_dir / "02-Research" / "claude.md", "Claude MCP", "claude mcp agent python")
    monkeypatch.setattr(app_module, "get_settings", lambda: settings)
    transport = httpx.ASGITransport(app=create_app(enable_scheduler=False))
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/newsletter/generate", json={"date": "2026-04-25", "export_pdf": False})
        page = await client.get("/newsletter/2026-04-25/html")
    assert response.status_code == 200
    assert page.status_code == 200
    assert "JarvisOS Daily" in page.text


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
