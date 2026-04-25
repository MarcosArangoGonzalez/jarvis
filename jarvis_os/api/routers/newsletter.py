from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


router = APIRouter()


class NewsletterGeneratePayload(BaseModel):
    date: str | None = None
    sections: list[str] | None = None
    export_pdf: bool = True


@router.post("/api/newsletter/generate")
async def generate_newsletter(payload: NewsletterGeneratePayload, request: Request):
    return request.app.state.kernel.generate_newsletter(
        target_date=payload.date,
        sections=payload.sections,
        export_pdf=payload.export_pdf,
    ).model_dump(mode="json")


@router.get("/api/newsletter/status/{job_id}")
async def newsletter_status(job_id: str, request: Request):
    for job in request.app.state.kernel.get_jobs():
        if job.id == job_id:
            return job.model_dump(mode="json")
    return {"status": "not_found", "job_id": job_id}


@router.get("/newsletter/{target_date}/html", response_class=HTMLResponse)
async def newsletter_html(target_date: str, request: Request):
    return HTMLResponse(request.app.state.kernel.get_newsletter_html(target_date))


@router.get("/newsletter/{target_date}", response_class=HTMLResponse)
async def newsletter_by_date(target_date: str, request: Request):
    return HTMLResponse(request.app.state.kernel.get_newsletter_html(target_date))
