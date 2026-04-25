from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jarvis_os.app import create_app
from jarvis_os.integrations.renderer import DiagramRenderer
from jarvis_os.schemas import RenderRequest


@pytest.fixture(scope="module")
def client():
    app = create_app(enable_scheduler=False)
    return TestClient(app)


def test_render_mermaid_api(client):
    resp = client.post("/api/render", json={"spec": "graph LR; A-->B", "mode": "mermaid"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "mermaid"
    assert "A-->B" in data["output"]
    assert data["format"] == "mermaid"


def test_render_auto_detects_mermaid(client):
    resp = client.post("/api/render", json={"spec": "flowchart TD\n  A[Start] --> B[End]", "mode": "auto"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "mermaid"


def test_render_strips_code_fences():
    renderer = DiagramRenderer()
    req = RenderRequest(spec="```mermaid\ngraph LR; A-->B\n```", mode="mermaid")
    result = renderer.render(req)
    assert "```" not in result.output
    assert "A-->B" in result.output


def test_render_claude_mode_no_key():
    renderer = DiagramRenderer()
    req = RenderRequest(spec="graph LR; A-->B", mode="claude")
    result = renderer.render(req)
    assert result.output
    # Without API key, falls back to cleaned mermaid spec
    assert isinstance(result.output, str)


def test_render_unit_clean_mermaid():
    renderer = DiagramRenderer()
    spec = "```\ngraph LR\n  A --> B\n```"
    cleaned = renderer._clean_mermaid(spec)
    assert "graph LR" in cleaned
    assert "```" not in cleaned
