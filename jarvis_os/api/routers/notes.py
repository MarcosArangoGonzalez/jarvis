from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Request

from ...integrations.notes import NoteStoreError
from ...schemas import NoteWriteRequest


router = APIRouter()


@router.get("/api/notes/daily/today")
async def daily_today(request: Request):
    return request.app.state.kernel.get_today_note().model_dump(mode="json")


@router.get("/api/notes/{path:path}")
async def read_note(path: str, request: Request):
    try:
        return request.app.state.kernel.get_note(path).model_dump(mode="json")
    except NoteStoreError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/api/notes/{path:path}")
async def write_note(path: str, payload: NoteWriteRequest, request: Request):
    try:
        return request.app.state.kernel.write_note(path, payload.content).model_dump(mode="json")
    except NoteStoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/calendar/events")
async def calendar_events(request: Request, year: int | None = None, month: int | None = None):
    today = date.today()
    return [
        item.model_dump(mode="json")
        for item in request.app.state.kernel.get_calendar_events(year=year or today.year, month=month or today.month)
    ]
