from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import VaultSearchQuery


router = APIRouter()


@router.get("/api/vault/search")
def vault_search(
    request: Request,
    query: str = "",
    mode: str = "text",
    folder: str = "all",
    date_filter: str = "any",
    tags: list[str] | None = None,
):
    payload = VaultSearchQuery(
        query=query,
        mode=mode,  # type: ignore[arg-type]
        folder=folder,
        date_filter=date_filter,  # type: ignore[arg-type]
        tags=tags or [],
    )
    return request.app.state.kernel.search_vault(payload).model_dump(mode="json")
