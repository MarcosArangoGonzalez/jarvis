from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import SessionWizardRequest


router = APIRouter()


@router.get("/api/session/contexts")
async def list_contexts(request: Request):
    wizard = request.app.state.kernel.session_wizard
    contexts = wizard.list_contexts()
    return {cat: [c.model_dump() for c in files] for cat, files in contexts.items()}


@router.get("/api/session/profiles")
async def list_profiles(request: Request):
    wizard = request.app.state.kernel.session_wizard
    return [p.model_dump() for p in wizard.list_profiles()]


@router.post("/api/session/generate")
async def generate_session(payload: SessionWizardRequest, request: Request):
    result = request.app.state.kernel.session_wizard.generate_claude_md(payload)
    return result.model_dump()


@router.post("/api/session/save")
async def save_session_profile(payload: SessionWizardRequest, request: Request):
    payload.save_profile = True
    result = request.app.state.kernel.session_wizard.generate_claude_md(payload)
    return result.model_dump()
