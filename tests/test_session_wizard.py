from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jarvis_os.app import create_app
from jarvis_os.integrations.session_wizard import SessionWizard


@pytest.fixture(scope="module")
def client():
    app = create_app(enable_scheduler=False)
    return TestClient(app)


def test_session_wizard_list_contexts(client):
    resp = client.get("/api/session/contexts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    if data:
        first_cat = next(iter(data.values()))
        assert isinstance(first_cat, list)
        assert all("name" in c and "path" in c for c in first_cat)


def test_session_wizard_list_profiles(client):
    resp = client.get("/api/session/profiles")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_session_wizard_generate_empty(client):
    resp = client.post("/api/session/generate", json={"contexts": []})
    assert resp.status_code == 200
    data = resp.json()
    assert "claude_md" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_session_wizard_generate_with_profile(client):
    resp = client.post("/api/session/generate", json={
        "contexts": [],
        "profile": "profiles/backend-dev-day.md",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "claude_md" in data


def test_session_wizard_generate_known_context(client):
    resp = client.post("/api/session/generate", json={
        "contexts": ["stack/python-fastapi.md"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "claude_md" in data
    if data["sources"]:
        assert "stack/python-fastapi.md" in data["sources"]


def test_session_wizard_page(client):
    resp = client.get("/session/new")
    assert resp.status_code == 200
    assert b"Session Wizard" in resp.content or b"wizard" in resp.content.lower()


def test_session_wizard_unit_list_contexts(tmp_path):
    from jarvis_os.config import get_settings
    settings = get_settings()
    wizard = SessionWizard(settings)
    contexts = wizard.list_contexts()
    assert isinstance(contexts, dict)


def test_session_wizard_unit_generate(tmp_path):
    from jarvis_os.config import get_settings
    from jarvis_os.schemas import SessionWizardRequest
    settings = get_settings()
    wizard = SessionWizard(settings)
    req = SessionWizardRequest(contexts=["models/sonnet-default.md"])
    result = wizard.generate_claude_md(req)
    assert result.claude_md
    assert isinstance(result.sources, list)
