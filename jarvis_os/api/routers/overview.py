from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/overview")
def overview(request: Request):
    return request.app.state.kernel.get_overview().model_dump(mode="json")
