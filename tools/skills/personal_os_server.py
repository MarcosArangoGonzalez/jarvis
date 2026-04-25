#!/usr/bin/env python3
"""Run the JarvisOS Personal OS dashboard locally."""

from __future__ import annotations

import sys
import os
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    port = int(os.environ.get("JARVIS_OS_PORT", "5055"))
    uvicorn.run("jarvis_os.app:app", host="127.0.0.1", port=port, reload=False)
