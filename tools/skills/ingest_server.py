#!/usr/bin/env python3
"""FastAPI receiver for browser chat rescue payloads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]
RAW_CHATS = ROOT / "raw" / "chats"


class BrowserIngestPayload(BaseModel):
    title: str = "Browser Chat Export"
    url: str | None = None
    exported_at: str | None = None
    user_agent: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    raw_text: str | None = None


app = FastAPI(title="JarvisOS Ingest Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "https://gemini.google.com", "https://claude.ai"],
    allow_origin_regex=r"https://.*",
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


def safe_stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest/browser")
async def ingest_browser(payload: BrowserIngestPayload, request: Request) -> dict[str, Any]:
    RAW_CHATS.mkdir(parents=True, exist_ok=True)
    document = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    document["received_at"] = datetime.now(timezone.utc).isoformat()
    document["client"] = request.client.host if request.client else None
    output = RAW_CHATS / f"{safe_stamp()}-browser-chat.json"
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "path": str(output), "messages": len(payload.messages)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
