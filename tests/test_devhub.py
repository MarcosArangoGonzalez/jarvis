from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jarvis_os.app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app(enable_scheduler=False)
    return TestClient(app)


def test_devhub_api(client):
    resp = client.get("/api/devhub")
    assert resp.status_code == 200
    data = resp.json()
    assert "recent_jobs" in data
    assert "recent_findings" in data
    assert "recent_insights" in data
    assert "cicd" in data
    assert "metrics" in data


def test_devhub_api_types(client):
    data = client.get("/api/devhub").json()
    assert isinstance(data["recent_jobs"], list)
    assert isinstance(data["recent_findings"], list)
    assert isinstance(data["recent_insights"], list)
    assert isinstance(data["metrics"], list)


def test_insights_api(client):
    resp = client.get("/api/insights")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_insights_api_limit(client):
    resp = client.get("/api/insights?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 3


def test_devhub_page(client):
    resp = client.get("/dev_hub")
    assert resp.status_code == 200
    assert b"Dev Hub" in resp.content or b"hub" in resp.content.lower()


def test_insights_page(client):
    resp = client.get("/insights")
    assert resp.status_code == 200
    assert b"insight" in resp.content.lower()
