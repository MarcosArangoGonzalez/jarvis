#!/usr/bin/env python3
"""Collect CI/CD failures into raw/alerts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
ALERTS = ROOT / "raw" / "alerts"


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")


def write_alert(source: str, title: str, payload: dict) -> Path:
    ALERTS.mkdir(parents=True, exist_ok=True)
    output = ALERTS / f"{stamp()}-{source}.json"
    output.write_text(json.dumps({
        "source": source,
        "title": title,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def github_actions(repo: str | None) -> Path:
    if not repo:
        payload = {"status": "skipped", "reason": "repo not provided"}
    else:
        try:
            completed = subprocess.run(["gh", "run", "list", "--repo", repo, "--status", "failure", "--limit", "10", "--json", "databaseId,displayTitle,status,conclusion,url"], capture_output=True, text=True, check=True)
            payload = {"status": "ok", "runs": json.loads(completed.stdout or "[]")}
        except Exception as exc:
            payload = {"status": "error", "error": str(exc)}
    return write_alert("github-actions", "GitHub Actions failures", payload)


def sonar(project_key: str | None) -> Path:
    token = os.getenv("SONAR_TOKEN")
    host = os.getenv("SONAR_HOST_URL", "https://sonarcloud.io")
    if not project_key or not token:
        payload = {"status": "skipped", "reason": "SONAR_TOKEN or project key missing"}
    else:
        url = f"{host}/api/qualitygates/project_status?projectKey={project_key}"
        try:
            request = Request(url, headers={"Authorization": f"Bearer {token}"})
            with urlopen(request, timeout=10) as response:
                payload = {"status": "ok", "quality_gate": json.loads(response.read().decode("utf-8"))}
        except Exception as exc:
            payload = {"status": "error", "error": str(exc)}
    return write_alert("sonar", "Sonar quality gate", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub repo as owner/name.")
    parser.add_argument("--sonar-project-key")
    args = parser.parse_args()
    print(github_actions(args.repo))
    print(sonar(args.sonar_project_key))


if __name__ == "__main__":
    main()
