from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_os.app import create_app


def make_client() -> TestClient:
    app = create_app(enable_scheduler=False)
    return TestClient(app)
