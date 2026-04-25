from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import ResearchQuery


router = APIRouter()


@router.post("/api/research/query")
async def research_query(payload: ResearchQuery, request: Request):
    return request.app.state.kernel.run_research(payload).model_dump(mode="json")


@router.get("/api/research/history")
async def research_history(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_research_history()]
