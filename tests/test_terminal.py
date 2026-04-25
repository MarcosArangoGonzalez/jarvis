from __future__ import annotations

from pathlib import Path

import pytest
import httpx

from jarvis_os.app import create_app
from jarvis_os.config import Settings, get_settings
from jarvis_os.integrations import terminal as terminal_integration
from jarvis_os.integrations.terminal import ClaudeTerminal, TerminalError, update_metrics_from_stream
from jarvis_os.schemas import SessionMetrics, TerminalSessionCreate


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_metrics_parsed_from_stream() -> None:
    metrics = SessionMetrics()
    update_metrics_from_stream(metrics, "Tokens: 47,234 input, 12,841 output ... Context: 68.4% ... Cost: $0.84")
    assert metrics.tokens_in == 47234
    assert metrics.tokens_out == 12841
    assert metrics.context_pct == 68.4
    assert metrics.cost_usd == 0.84


def test_metrics_parser_ignores_unknown_stream() -> None:
    metrics = SessionMetrics()
    update_metrics_from_stream(metrics, "normal shell output\n$ ls")
    assert metrics.tokens_in == 0
    assert metrics.tokens_out == 0
    assert metrics.context_pct == 0
    assert metrics.cost_usd == 0


def test_terminal_rejects_cwd_outside_root(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    monkeypatch.setattr(terminal_integration.shutil, "which", lambda _: "/usr/bin/claude")
    terminal = ClaudeTerminal(settings)
    with pytest.raises(TerminalError, match="inside the JarvisOS root"):
        terminal.create_session(TerminalSessionCreate(cwd=str(tmp_path.parent), load_vault_context=False))


def test_terminal_routes_registered() -> None:
    app = create_app(enable_scheduler=False)
    paths = {route.path for route in app.routes}
    assert {"/terminal", "/api/terminal/sessions", "/ws/terminal/{session_id}"}.issubset(paths)


@pytest.mark.anyio
async def test_terminal_session_create_handles_missing_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(terminal_integration.shutil, "which", lambda _: None)
    app = create_app(enable_scheduler=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/terminal/sessions", json={"cwd": ".", "model": "claude-sonnet-4-6"})
    assert response.status_code == 400
    assert "Claude Code CLI not found" in response.json()["detail"]


def test_terminal_session_create_uses_pty(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _temp_settings(tmp_path)
    workdir = settings.root_dir / "work"
    workdir.mkdir(parents=True)
    calls = {}

    monkeypatch.setattr(terminal_integration.shutil, "which", lambda _: "/usr/bin/claude")
    def fake_spawn(argv, cwd=None, env=None, echo=True, preexec_fn=None, dimensions=(24, 80), pass_fds=()):
        calls["argv"] = argv
        calls["cwd"] = cwd
        calls["dimensions"] = dimensions
        return FakePtyProcess()

    monkeypatch.setattr(terminal_integration.PtyProcess, "spawn", fake_spawn)
    terminal = ClaudeTerminal(settings)
    session = terminal.create_session(
        TerminalSessionCreate(cwd="work", model="claude-test-model", load_vault_context=False)
    )

    assert calls["argv"] == ["claude", "--model", "claude-test-model"]
    assert calls["cwd"] == str(workdir.resolve())
    assert calls["dimensions"] == (32, 120)
    assert session.metrics.model == "claude-test-model"


class FakePtyProcess:
    def __init__(self) -> None:
        self.alive = True
        self.writes: list[bytes] = []

    def isalive(self) -> bool:
        return self.alive

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def read(self, size: int = 1024) -> bytes:
        return b""

    def setwinsize(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols

    def terminate(self, force: bool = False) -> None:
        self.alive = False


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
