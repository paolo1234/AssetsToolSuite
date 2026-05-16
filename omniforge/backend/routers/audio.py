"""
OmniForge Backend — Audio Router
Handles AI audio generation (mock) and audio processing requests.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from processors.audio import AudioProcessor
from routers.project import _get_manager

router = APIRouter(prefix="/api/audio", tags=["audio"])

class AudioProcessRequest(BaseModel):
    project_id: str
    asset_id: str
    pipeline: list[dict[str, Any]]

class AudioGenerateRequest(BaseModel):
    project_id: str
    prompt: str
    duration_sec: int = 5

@router.post("/generate")
async def generate_audio(req: AudioGenerateRequest, background_tasks: BackgroundTasks):
    """
    Start an AI audio generation task (Mocked for now).
    In a real scenario, this would call ElevenLabs or AudioLDM.
    """
    task_id = str(uuid.uuid4())
    
    # Simulate background task
    # background_tasks.add_task(run_audio_gen, task_id, req)
    
    return {"task_id": task_id, "status": "processing"}

@router.post("/process")
async def process_audio(req: AudioProcessRequest):
    """Apply audio processing pipeline to an existing asset."""
    mgr = _get_manager(req.project_id)
    asset = mgr.get_asset_by_id(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    # Determine format from extension
    fmt = file_path.suffix.lstrip(".").lower() or "wav"
    
    processed_bytes = AudioProcessor.apply_pipeline(audio_bytes, req.pipeline, input_format=fmt)

    # Save it back (versioning handled by ProjectManager)
    with open(file_path, "wb") as f:
        f.write(processed_bytes)

    mgr.update_asset(req.asset_id, {"updated_at": "now"})
    
    return {"status": "processed", "asset_id": req.asset_id}
