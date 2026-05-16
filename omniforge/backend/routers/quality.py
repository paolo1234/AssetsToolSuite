"""
OmniForge Backend — Quality Router
Handles quality assessment and batch corrections.
"""

from __future__ import annotations

from typing import Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from processors.quality import QualityProcessor
from routers.project import _get_manager

router = APIRouter(prefix="/api/quality", tags=["quality"])

class CorrectionRequest(BaseModel):
    project_id: str
    asset_ids: List[str]
    params: dict[str, Any]

@router.get("/{project_id}/{asset_id}/analyze")
async def analyze_asset(project_id: str, asset_id: str):
    """Run quality analysis on an asset."""
    mgr = _get_manager(project_id)
    asset = mgr.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = mgr.project_dir / asset.file_path
    with open(file_path, "rb") as f:
        img_bytes = f.read()

    analysis = QualityProcessor.analyze_quality(img_bytes)
    
    # Update manifest with new quality score
    mgr.update_asset(asset_id, {"quality_score": analysis["score"]})
    
    return analysis

@router.post("/batch-correct")
async def batch_correct(req: CorrectionRequest):
    """Apply color corrections to multiple assets."""
    mgr = _get_manager(req.project_id)
    results = []

    for asset_id in req.asset_ids:
        asset = mgr.get_asset_by_id(asset_id)
        if not asset: continue
        
        file_path = mgr.project_dir / asset.file_path
        with open(file_path, "rb") as f:
            img_bytes = f.read()
            
        corrected_bytes = QualityProcessor.apply_color_correction(img_bytes, req.params)
        
        with open(file_path, "wb") as f:
            f.write(corrected_bytes)
            
        mgr.update_asset(asset_id, {"updated_at": "now"})
        results.append(asset_id)

    return {"status": "success", "corrected": results}
