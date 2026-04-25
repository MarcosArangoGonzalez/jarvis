from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/cicd/status")
async def cicd_status(request: Request, repo: str = ""):
    status = request.app.state.kernel.cicd.get_status(repo=repo)
    return status.model_dump()


@router.post("/api/cicd/trigger")
async def cicd_trigger(request: Request, repo: str = "", workflow_id: str = "ci.yml", ref: str = "main"):
    ok = request.app.state.kernel.cicd.trigger_workflow(repo=repo, workflow_id=workflow_id, ref=ref)
    return {"triggered": ok}
