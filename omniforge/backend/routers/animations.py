"""
OmniForge Backend — Animation Router
Handles spritesheet slicing and animation metadata management.
"""

from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from processors.spritesheet import SpritesheetProcessor
from routers.project import _get_manager

router = APIRouter(prefix="/api/animations", tags=["animations"])

class SliceRequest(BaseModel):
    project_id: str
    asset_id: str
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None

@router.post("/slice")
async def slice_asset(req: SliceRequest):
    """Slice an existing asset into frames."""
    mgr = _get_manager(req.project_id)
    asset = mgr.get_asset_by_id(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    with open(file_path, "rb") as f:
        img_bytes = f.read()

    # Detect grid if not provided
    if not req.frame_width or not req.frame_height:
        grid = SpritesheetProcessor.detect_grid(img_bytes)
        fw, fh = grid["frame_width"], grid["frame_height"]
    else:
        fw, fh = req.frame_width, req.frame_height

    # Slicing (mock for now, in reality we'd return metadata or save sub-assets)
    # For now, we return the detected grid and frame count
    img = SpritesheetProcessor.slice_grid(img_bytes, fw, fh)
    
    # Update asset metadata
    mgr.update_asset(req.asset_id, {
        "metadata": {
            "frames": len(img),
            "frame_width": fw,
            "frame_height": fh
        }
    })

    return {
        "asset_id": req.asset_id,
        "frame_count": len(img),
        "grid": {"width": fw, "height": fh}
    }

@router.get("/{project_id}/{asset_id}/godot_resource")
async def get_godot_resource(project_id: str, asset_id: str):
    """Generate Godot .tres file content for an animation."""
    mgr = _get_manager(project_id)
    asset = mgr.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Generate metadata (mock)
    frames = []
    for i in range(asset.metadata.get("frames", 0)):
        frames.append({"id": i})

    res_content = SpritesheetProcessor.export_godot_resource(frames, f"res://{asset.file_path}")
    
    return {"content": res_content}
