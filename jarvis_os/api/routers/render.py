from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import RenderRequest


router = APIRouter()


@router.post("/api/render")
async def render_diagram(payload: RenderRequest, request: Request):
    result = request.app.state.kernel.renderer.render(payload)
    return result.model_dump()
