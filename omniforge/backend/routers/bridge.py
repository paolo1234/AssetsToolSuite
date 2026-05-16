"""
OmniForge Backend — Bridge Router
Exposes endpoints for the frontend to send commands to Godot.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel

from bridge.websocket_server import bridge_server

router = APIRouter(prefix="/api/bridge", tags=["bridge"])

class BridgeCommand(BaseModel):
    cmd: str
    path: Optional[str] = None
    extra: dict[str, Any] = {}

@router.post("/broadcast")
async def broadcast_command(command: dict):
    """Broadcast a raw command to all connected Godot instances."""
    await bridge_server.broadcast(command)
    return {"status": "broadcasted"}
