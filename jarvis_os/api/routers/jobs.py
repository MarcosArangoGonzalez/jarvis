from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Request


router = APIRouter()


class JobCreatePayload(BaseModel):
    kind: str
    payload: dict = Field(default_factory=dict)


@router.get("/api/jobs")
def jobs(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_jobs()]


@router.post("/api/jobs")
def create_job(payload: JobCreatePayload, request: Request):
    return request.app.state.kernel.create_job(kind=payload.kind, payload=payload.payload).model_dump(mode="json")
