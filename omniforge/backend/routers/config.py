"""
OmniForge Backend — Config Router
Endpoints for reading and updating global application settings.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/api/config", tags=["config"])

class ConfigUpdate(BaseModel):
    settings: Dict[str, Any]

@router.get("")
async def get_config():
    """Get current global settings (excluding sensitive keys if needed, but for local it's fine)."""
    return {
        "BACKEND_HOST": settings.BACKEND_HOST,
        "BACKEND_PORT": settings.BACKEND_PORT,
        "BRIDGE_PORT": settings.BRIDGE_PORT,
        "PROJECTS_DIR": str(settings.PROJECTS_DIR),
        "MAX_ASSET_VERSIONS": settings.MAX_ASSET_VERSIONS,
        "QUALITY_GATE_THRESHOLD": settings.QUALITY_GATE_THRESHOLD,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "COMFYUI_URL": settings.COMFYUI_URL,
        "ELEVENLABS_API_KEY": settings.ELEVENLABS_API_KEY,
        "REPLICATE_API_KEY": settings.REPLICATE_API_KEY,
        "SUNO_API_KEY": settings.SUNO_API_KEY,
    }

@router.post("")
async def update_config(update: ConfigUpdate):
    """Update global settings and persist to disk."""
    try:
        settings.update(update.settings)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
