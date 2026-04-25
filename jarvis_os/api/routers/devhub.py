from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import DevHubOverview


router = APIRouter()


@router.get("/api/devhub")
async def devhub_overview(request: Request):
    kernel = request.app.state.kernel
    overview = DevHubOverview(
        recent_jobs=kernel.get_jobs()[:8],
        recent_findings=kernel.get_security_findings()[:5],
        recent_insights=kernel.get_insights()[:6],
        cicd=kernel.cicd.get_status(),
        metrics=kernel.get_metrics(),
    )
    return overview.model_dump(mode="json")


@router.get("/api/insights")
async def list_insights(request: Request, limit: int = 10):
    insights = request.app.state.kernel.get_insights(limit=limit)
    return [i.model_dump() for i in insights]
