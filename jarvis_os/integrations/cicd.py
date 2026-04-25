from __future__ import annotations

import os
from datetime import datetime

import httpx

from ..config import Settings
from ..schemas import CiCdRun, CiCdStatus


class CiCdIntegration:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._github_token = os.getenv("GITHUB_TOKEN", "")
        self._sonar_token = os.getenv("SONAR_TOKEN", "")
        self._sonar_url = os.getenv("SONAR_URL", "")

    def get_status(self, repo: str = "") -> CiCdStatus:
        if not self._github_token:
            return CiCdStatus(available=False, notice="GITHUB_TOKEN no configurado")
        if not repo:
            repo = self._detect_repo()
        if not repo:
            return CiCdStatus(available=False, notice="Repositorio no detectado")
        try:
            runs = self._fetch_runs(repo)
            gate = self._fetch_sonar_gate() if self._sonar_token else None
            return CiCdStatus(available=True, runs=runs, sonar_gate=gate)
        except Exception as exc:
            return CiCdStatus(available=False, notice=str(exc))

    def trigger_workflow(self, repo: str, workflow_id: str, ref: str = "main") -> bool:
        if not self._github_token or not repo:
            return False
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
        headers = {"Authorization": f"Bearer {self._github_token}", "Accept": "application/vnd.github+json"}
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(url, headers=headers, json={"ref": ref})
                return resp.status_code == 204
        except Exception:
            return False

    def _fetch_runs(self, repo: str, limit: int = 10) -> list[CiCdRun]:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page={limit}"
        headers = {"Authorization": f"Bearer {self._github_token}", "Accept": "application/vnd.github+json"}
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        runs = []
        for r in data.get("workflow_runs", []):
            runs.append(CiCdRun(
                workflow=r.get("name", ""),
                status=r.get("status", ""),
                conclusion=r.get("conclusion"),
                created_at=r.get("created_at", ""),
                url=r.get("html_url", ""),
            ))
        return runs

    def _fetch_sonar_gate(self) -> str | None:
        if not self._sonar_url:
            return None
        url = f"{self._sonar_url}/api/qualitygates/project_status"
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(url, headers={"Authorization": f"Bearer {self._sonar_token}"})
                if resp.status_code == 200:
                    return resp.json().get("projectStatus", {}).get("status")
        except Exception:
            pass
        return None

    def _detect_repo(self) -> str:
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.settings.root_dir,
                capture_output=True, text=True, timeout=5,
            )
            url = result.stdout.strip()
            if "github.com" in url:
                parts = url.rstrip(".git").split("github.com")[-1].lstrip("/:")
                return parts
        except Exception:
            pass
        return ""
