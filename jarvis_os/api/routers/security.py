from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas import SecurityScanRequest


router = APIRouter()


@router.post("/api/security/scan")
def security_scan(payload: SecurityScanRequest, request: Request):
    return request.app.state.kernel.scan_security(payload).model_dump(mode="json")


@router.get("/api/security/findings")
def security_findings(request: Request):
    return [item.model_dump(mode="json") for item in request.app.state.kernel.get_security_findings()]
