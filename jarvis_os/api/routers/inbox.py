from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/inbox")
def inbox(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_inbox()]


@router.get("/api/ingestions")
def ingestions(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_ingestions()]
