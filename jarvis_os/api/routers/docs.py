from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import DocCheckRequest


router = APIRouter()


@router.post("/api/docs/check")
async def check_docs(payload: DocCheckRequest, request: Request):
    result = request.app.state.kernel.context7.check_docs(payload)
    return result.model_dump()
