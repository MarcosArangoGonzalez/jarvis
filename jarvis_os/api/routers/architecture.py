from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/architecture")
def architecture(request: Request):
    return request.app.state.kernel.get_topology().model_dump(mode="json")


@router.get("/api/topology")
def topology(request: Request):
    return request.app.state.kernel.get_topology().model_dump(mode="json")
