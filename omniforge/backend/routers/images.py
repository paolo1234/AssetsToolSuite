"""
OmniForge Backend — Image Generation Router
Handles AI generation, inpainting, and post-processing.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from ..config import settings
from ..adapters.comfyui import ComfyUIAdapter
from ..adapters.dalle import DallEAdapter
from ..processors.image import PromptBuilder, ImageProcessor
from .project import _get_manager

router = APIRouter(prefix="/api/generate", tags=["generation"])

# ── Queue Models ─────────────────────────────────────────────────────────────

class GenerationTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    prompt: str
    adapter_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # "pending" | "processing" | "completed" | "failed"
    result_url: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0

# Global queue state (in-memory for now)
active_tasks: dict[str, GenerationTask] = {}

# ── Request Models ───────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    project_id: str
    prompt: str
    adapter_id: str  # "comfyui" | "dalle"
    params: dict[str, Any] = Field(default_factory=dict)


class ProcessRequest(BaseModel):
    project_id: str
    asset_id: str
    pipeline: list[dict[str, Any]]  # List of ops: remove_bg, palette, pixelate


# ── Generation Logic ─────────────────────────────────────────────────────────

async def run_generation(task_id: str):
    """Background worker for AI generation."""
    task = active_tasks.get(task_id)
    if not task: return

    task.status = "processing"
    task.progress = 10

    try:
        # Get project manifest for style injection
        mgr = _get_manager(task.project_id)
        full_prompt = PromptBuilder.build(task.prompt, mgr.manifest)
        
        # Select adapter
        adapter = None
        if task.adapter_id == "comfyui":
            adapter = ComfyUIAdapter(server_url=settings.COMFYUI_URL)
        elif task.adapter_id == "dalle":
            adapter = DallEAdapter(api_key=settings.OPENAI_API_KEY)
        
        if not adapter:
            raise ValueError(f"Unknown adapter: {task.adapter_id}")

        task.progress = 30
        result = await adapter.generate(full_prompt, task.params)
        
        if not result.success:
            task.status = "failed"
            task.error = result.error_message
            return

        task.progress = 80
        
        # Save result to project
        asset_name = f"gen_{task_id[:8]}"
        file_name = f"{asset_name}.png"
        rel_path = f"assets/{file_name}"
        full_path = mgr.project_dir / rel_path
        full_path.parent.mkdir(exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(result.file_bytes)

        # Update task
        task.status = "completed"
        task.progress = 100
        task.result_url = f"/api/projects/{task.project_id}/assets/{asset_name}" # Placeholder

    except Exception as e:
        task.status = "failed"
        task.error = str(e)

# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/image")
async def start_generation(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Start an AI image generation task."""
    task = GenerationTask(
        project_id=req.project_id,
        prompt=req.prompt,
        adapter_id=req.adapter_id,
        params=req.params
    )
    active_tasks[task.id] = task
    
    background_tasks.add_task(run_generation, task.id)
    
    return {"task_id": task.id, "status": task.status}


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Poll status of a generation task."""
    task = active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/process")
async def process_image(req: ProcessRequest):
    """Apply post-processing pipeline to an existing asset."""
    mgr = _get_manager(req.project_id)
    asset = mgr.get_asset_by_id(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")

    with open(file_path, "rb") as f:
        img_bytes = f.read()

    processed_bytes = ImageProcessor.apply_pipeline(img_bytes, req.pipeline)

    # Overwrite or save as new? 
    # For now, we save it back and update version
    with open(file_path, "wb") as f:
        f.write(processed_bytes)

    mgr.update_asset(req.asset_id, {"updated_at": "now"}) # Triggers versioning in future
    
    return {"status": "processed", "asset_id": req.asset_id}
