from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/sessions")
def sessions(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_sessions()]


@router.get("/api/sessions/{session_id}")
def session_detail(session_id: str, request: Request):
    session = request.app.state.kernel.get_session(session_id)
    if session is None:
        return {"status": "not_found", "session_id": session_id}
    return session.model_dump(mode="json")
