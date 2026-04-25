from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/metrics/overview")
def metrics_overview(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_metrics()]
