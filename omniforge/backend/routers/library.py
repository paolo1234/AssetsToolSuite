"""
OmniForge Backend — Library & Export Router
Handles bulk operations and global exports.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from routers.project import _get_manager

router = APIRouter(prefix="/api/library", tags=["library"])

@router.post("/{project_id}/export")
async def export_project(project_id: str, target_dir: Optional[str] = None):
    """
    Export the entire project assets to a target directory (e.g. Godot project).
    """
    mgr = _get_manager(project_id)
    
    if not target_dir:
        # Default to a subfolder in the project dir
        target_path = mgr.project_dir / "export_godot"
    else:
        target_path = Path(target_dir)

    target_path.mkdir(parents=True, exist_ok=True)

    # Copy all files referenced in manifest
    for asset in mgr.manifest.assets:
        src = mgr.project_dir / asset.file_path
        dst = target_path / asset.file_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if src.exists():
            shutil.copy2(src, dst)
            
    return {"status": "success", "path": str(target_path)}

@router.post("/{project_id}/tags")
async def update_tags(project_id: str, asset_ids: List[str], tags: List[str], mode: str = "add"):
    """Bulk update tags for assets."""
    mgr = _get_manager(project_id)
    
    for aid in asset_ids:
        asset = mgr.get_asset_by_id(aid)
        if not asset: continue
        
        current_tags = set(asset.tags)
        if mode == "add":
            current_tags.update(tags)
        elif mode == "remove":
            current_tags.difference_update(tags)
        else:
            current_tags = set(tags)
            
        mgr.update_asset(aid, {"tags": list(current_tags)})
        
    return {"status": "success"}
