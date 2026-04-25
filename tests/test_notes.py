from __future__ import annotations

from pathlib import Path

import httpx
import pytest

import jarvis_os.app as app_module
from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations.notes import NoteStore, NoteStoreError


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_note_write_creates_with_frontmatter(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    note = NoteStore(settings).write("00-Daily/test-note.md", "Body")
    assert note.path == "vault/00-Daily/test-note.md"
    assert note.content.startswith("---")
    assert "# Test Note" in note.content


def test_daily_today_creates_in_00daily(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    note = NoteStore(settings).today()
    assert note.path.startswith("vault/00-Daily/journal-")
    assert "type: journal" in note.content


def test_calendar_reads_dated_notes(tmp_path) -> None:
    settings = _temp_settings(tmp_path)
    path = settings.vault_dir / "00-Daily" / "journal-2026-04-25.md"
    path.parent.mkdir(parents=True)
    path.write_text('---\ntitle: "Daily Note"\n---\n# Daily Note\n', encoding="utf-8")
    events = NoteStore(settings).calendar_events(year=2026, month=4)
    assert events[0].date == "2026-04-25"
    assert events[0].title == "Daily Note"


def test_note_store_rejects_outside_vault(tmp_path) -> None:
    with pytest.raises(NoteStoreError):
        NoteStore(_temp_settings(tmp_path)).write("../outside.md", "bad")


@pytest.mark.anyio
async def test_notes_api_roundtrip(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    monkeypatch.setattr(app_module, "get_settings", lambda: settings)
    transport = httpx.ASGITransport(app=create_app(enable_scheduler=False))
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        write = await client.put("/api/notes/00-Daily/api-note.md", json={"content": "hello"})
        read = await client.get("/api/notes/00-Daily/api-note.md")
        today = await client.get("/api/notes/daily/today")
        events = await client.get("/api/calendar/events?year=2026&month=4")
    assert write.status_code == 200
    assert read.json()["content"].startswith("---")
    assert today.status_code == 200
    assert events.status_code == 200


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
