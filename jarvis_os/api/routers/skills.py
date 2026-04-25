from __future__ import annotations

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/api/skills")
def skills(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_skills()]


@router.get("/api/skills/{skill_id}")
def skill_detail(skill_id: str, request: Request):
    skill = request.app.state.kernel.get_skill(skill_id)
    if skill is None:
        return {"status": "not_found", "skill_id": skill_id}
    return skill.model_dump(mode="json")
