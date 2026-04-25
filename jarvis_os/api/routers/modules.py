from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/modules/{module_name}")
def module_state(module_name: str, request: Request):
    return request.app.state.kernel.get_module_state(module_name).model_dump(mode="json")
