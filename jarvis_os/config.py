from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    wiki_dir: Path
    vault_dir: Path
    vault_inbox_dir: Path
    vault_assets_dir: Path
    tasks_dir: Path
    logs_dir: Path
    skills_dir: Path
    mcp_config_path: Path
    runtime_dir: Path
    templates_dir: Path
    static_dir: Path
    session_manager_path: Path


def get_settings() -> Settings:
    root_dir = Path(__file__).resolve().parents[1]
    return Settings(
        root_dir=root_dir,
        wiki_dir=root_dir / "wiki",
        vault_dir=root_dir / "vault",
        vault_inbox_dir=root_dir / "vault" / "05-Inbox",
        vault_assets_dir=root_dir / "vault" / "assets",
        tasks_dir=root_dir / "wiki" / "tasks",
        logs_dir=root_dir / "wiki" / "logs" / "core",
        skills_dir=root_dir / "tools" / "skills",
        mcp_config_path=root_dir / "tools" / "mcp_servers" / "mcp_config.json",
        runtime_dir=root_dir / "data" / "runtime",
        templates_dir=root_dir / "jarvis_os" / "dashboard" / "templates",
        static_dir=root_dir / "jarvis_os" / "dashboard" / "static",
        session_manager_path=root_dir / ".jarvis" / "session_manager.md",
    )
