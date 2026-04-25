from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jarvis_os.app import create_app
from jarvis_os.integrations.cicd import CiCdIntegration


@pytest.fixture(scope="module")
def client():
    app = create_app(enable_scheduler=False)
    return TestClient(app)


def test_cicd_status_no_token(client):
    resp = client.get("/api/cicd/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    # Without GITHUB_TOKEN this should return available=False
    if not data["available"]:
        assert "notice" in data


def test_cicd_status_structure(client):
    resp = client.get("/api/cicd/status")
    data = resp.json()
    assert isinstance(data.get("runs", []), list)


def test_cicd_trigger_no_token(client):
    resp = client.post("/api/cicd/trigger")
    assert resp.status_code == 200
    data = resp.json()
    assert "triggered" in data
    assert data["triggered"] is False


def test_cicd_unit_no_token():
    from jarvis_os.config import get_settings
    settings = get_settings()
    cicd = CiCdIntegration(settings)
    status = cicd.get_status()
    assert not status.available


def test_cicd_detect_repo_graceful():
    from jarvis_os.config import get_settings
    settings = get_settings()
    cicd = CiCdIntegration(settings)
    repo = cicd._detect_repo()
    assert isinstance(repo, str)
