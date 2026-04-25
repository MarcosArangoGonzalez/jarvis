from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect

from ...integrations.terminal import TerminalError
from ...schemas import TerminalSessionCreate


router = APIRouter()


@router.post("/api/terminal/sessions")
async def create_terminal_session(payload: TerminalSessionCreate, request: Request):
    try:
        session = request.app.state.kernel.create_terminal_session(payload)
    except TerminalError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return session.model_dump(mode="json")


@router.get("/api/terminal/sessions")
async def list_terminal_sessions(request: Request):
    return [session.model_dump(mode="json") for session in request.app.state.kernel.list_terminal_sessions()]


@router.delete("/api/terminal/sessions/{session_id}")
async def close_terminal_session(session_id: str, request: Request):
    session = request.app.state.kernel.close_terminal_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Terminal session not found.")
    return session.model_dump(mode="json")


@router.websocket("/ws/terminal/{session_id}")
async def terminal_socket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = websocket.app.state.kernel.terminal.get_session(session_id)
    if session is None:
        await websocket.send_json({"type": "error", "message": "Terminal session not found."})
        await websocket.close()
        return

    await websocket.send_json({"type": "status", "status": session.info().status})

    async def pty_to_browser() -> None:
        try:
            while session.info().status == "active":
                chunk = await asyncio.to_thread(session.read)
                if not chunk:
                    break
                await websocket.send_json({"type": "output", "data": chunk})
                await websocket.send_json({"type": "metrics", **session.info().metrics.model_dump(mode="json")})
            await websocket.send_json({"type": "status", "status": "closed"})
        except (RuntimeError, WebSocketDisconnect):
            session.close()

    async def browser_to_pty() -> None:
        try:
            while True:
                message = await websocket.receive_json()
                message_type = message.get("type")
                if message_type == "input":
                    session.write(str(message.get("data", "")))
                elif message_type == "resize":
                    session.resize(int(message.get("cols", 120)), int(message.get("rows", 32)))
                elif message_type == "close":
                    session.close()
                    break
        except TerminalError as exc:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except WebSocketDisconnect:
            session.close()

    producer = asyncio.create_task(pty_to_browser())
    consumer = asyncio.create_task(browser_to_pty())
    done, pending = await asyncio.wait({producer, consumer}, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    if consumer in done and session.info().status == "closed":
        try:
            await websocket.send_json({"type": "status", "status": "closed"})
        except (RuntimeError, WebSocketDisconnect):
            pass
