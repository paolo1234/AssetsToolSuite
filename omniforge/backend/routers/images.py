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

from config import settings
from adapters.comfyui import ComfyUIAdapter
from adapters.dalle import DallEAdapter
from processors.image import PromptBuilder, ImageProcessor
from routers.project import _get_manager

router = APIRouter(prefix="/api/generate", tags=["generation"])

# ── ComfyUI Status Endpoints ───────────────────────────────────────────────

@router.get("/comfyui/status")
async def get_comfyui_status():
    """Get ComfyUI status, available models and workflow compatibility."""
    adapter = ComfyUIAdapter(server_url=settings.COMFYUI_URL)
    status = await adapter.get_comfyui_status()
    return status


@router.get("/comfyui/models")
async def get_available_models():
    """Get list of available checkpoints/models in ComfyUI."""
    adapter = ComfyUIAdapter(server_url=settings.COMFYUI_URL)
    models = await adapter.get_models()
    return {"models": models}


# ── Queue Models ─────────────────────────────────────────────────────────────

class GenerationTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    prompt: str
    adapter_id: str
    workflow_id: str = "sprite_single"
    params: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # "pending" | "processing" | "completed" | "failed"
    result_url: Optional[str] = None
    result_asset_id: Optional[str] = None
    result_bytes: Optional[bytes] = None
    error: Optional[str] = None
    progress: int = 0
    seed: Optional[int] = None
    created_at: Optional[int] = None

# Global queue state (in-memory for now)
active_tasks: dict[str, GenerationTask] = {}

# ── Request Models ───────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    project_id: str
    prompt: str
    adapter_id: str  # "comfyui" | "dalle"
    workflow_id: str = "sprite_single"
    params: dict[str, Any] = Field(default_factory=dict)


class UpscaleRequest(BaseModel):
    asset_id: str
    project_id: str
    scale: int = 4


class RefineRequest(BaseModel):
    asset_id: str
    project_id: str


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
        # Pass workflow_id to adapter
        generation_params = {**task.params, "workflow_id": task.workflow_id}
        if task.seed:
            generation_params["seed"] = task.seed
        result = await adapter.generate(full_prompt, generation_params)
        
        if not result.success:
            task.status = "failed"
            task.error = result.error_message
            return

        task.progress = 80
        
        # Save result to project
        asset_id = f"gen_{task_id[:8]}"
        file_name = f"{asset_id}.png"
        rel_path = f"assets/{file_name}"
        full_path = mgr.project_dir / rel_path
        full_path.parent.mkdir(exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(result.file_bytes)

        # Register asset in manifest
        from project.manifest import AssetEntry, AssetMetadata
        new_asset = AssetEntry(
            id=asset_id,
            name=f"Generated Image {asset_id}",
            type="image",
            category="generated",
            tags=["ai-generated", task.adapter_id],
            file_path=rel_path,
            metadata=AssetMetadata(
                source="ai_generation",
                prompt=task.prompt
            )
        )
        mgr.add_asset(new_asset)
        mgr.save()

        # Update task
        task.status = "completed"
        task.progress = 100
        task.result_url = f"/api/projects/{task.project_id}/assets/{asset_id}/file"
        task.result_asset_id = asset_id

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
        workflow_id=req.workflow_id,
        params=req.params,
        seed=req.params.get("seed") or None
    )
    active_tasks[task.id] = task
    
    background_tasks.add_task(run_generation, task.id)
    
    return {"task_id": task.id, "status": task.status}


@router.post("/upscale")
async def upscale_image(req: UpscaleRequest):
    """Upscale an existing project asset."""
    mgr = _get_manager(req.project_id)
    asset = mgr.get_asset_by_id(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="No image to upscale")

    with open(file_path, "rb") as f:
        image_bytes = f.read()

    from processors.image import ImageProcessor
    upscaled = ImageProcessor.upscale(image_bytes, req.scale)

    new_asset_id = f"{req.asset_id}_4x"
    new_file_name = f"{new_asset_id}.png"
    new_file_path = mgr.project_dir / "assets" / new_file_name
    new_file_path.parent.mkdir(exist_ok=True)
    with open(new_file_path, "wb") as f:
        f.write(upscaled)

    from project.manifest import AssetEntry, AssetMetadata
    new_asset = AssetEntry(
        id=new_asset_id,
        name=f"{asset.name} (4x Upscale)",
        type=asset.type,
        category=asset.category,
        tags=asset.tags + ["upscaled"],
        file_path=f"assets/{new_file_name}",
        metadata=AssetMetadata(source="upscale", prompt=asset.metadata.prompt)
    )
    mgr.add_asset(new_asset)
    mgr.save()

    return {
        "asset_id": new_asset_id,
        "result_url": f"/api/projects/{req.project_id}/assets/{new_asset_id}/file"
    }


@router.post("/refine")
async def refine_image(req: RefineRequest):
    """Refine an existing project asset (re-run gen on the image)."""
    mgr = _get_manager(req.project_id)
    asset = mgr.get_asset_by_id(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="File not found")

    # Read original image, re-generate as a new asset
    from processors.image import ImageProcessor
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    # Use the original prompt to re-generate
    prompt = (asset.metadata.prompt if hasattr(asset.metadata, 'prompt') else asset.name) or asset.name
    
    # Run a new generation with the prompt
    adapter = ComfyUIAdapter(server_url=settings.COMFYUI_URL)
    result = await adapter.generate(f"refined: {prompt}", {"steps": 30, "cfg": 7})

    if not result.success:
        raise HTTPException(status_code=500, detail=f"Refine failed: {result.error_message}")

    new_asset_id = f"{req.asset_id}_refined"
    new_file_name = f"{new_asset_id}.png"
    new_file_path = mgr.project_dir / "assets" / new_file_name
    new_file_path.parent.mkdir(exist_ok=True)
    with open(new_file_path, "wb") as f:
        f.write(result.file_bytes)

    from project.manifest import AssetEntry, AssetMetadata
    new_asset = AssetEntry(
        id=new_asset_id,
        name=f"{asset.name} (Refined)",
        type=asset.type,
        category=asset.category,
        tags=asset.tags + ["refined"],
        file_path=f"assets/{new_file_name}",
        metadata=AssetMetadata(source="refine", prompt=prompt)
    )
    mgr.add_asset(new_asset)
    mgr.save()

    return {
        "asset_id": new_asset_id,
        "result_url": f"/api/projects/{req.project_id}/assets/{new_asset_id}/file"
    }


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Poll status of a generation task."""
    task = active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump(exclude={'result_bytes'})


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
