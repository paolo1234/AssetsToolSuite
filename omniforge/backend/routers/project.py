"""
OmniForge Backend — Project Router
REST API endpoints for project and asset CRUD operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..config import settings
from ..project.manifest import AssetEntry, AssetMetadata, ManifestManager, ProjectManifest
from ..project.versioning import AssetVersionManager

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ── Request/Response Models ──────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    project_name: str
    target_resolution_w: int = 320
    target_resolution_h: int = 180
    tile_size: int = 16
    base_fps: int = 12
    godot_project_path: str = ""


class UpdateProjectRequest(BaseModel):
    project_name: Optional[str] = None
    target_resolution_w: Optional[int] = None
    target_resolution_h: Optional[int] = None
    tile_size: Optional[int] = None
    base_fps: Optional[int] = None
    godot_project_path: Optional[str] = None
    palette_reference: Optional[str] = None
    light_direction_degrees: Optional[float] = None
    naming_convention: Optional[str] = None


class AddAssetRequest(BaseModel):
    name: str
    type: str  # "image" | "spritesheet" | "audio" | "ui" | "tilemap" | "effect"
    category: str  # "character" | "enemy" | "item" | "environment" | "ui" | "sfx" | "music"
    tags: list[str] = Field(default_factory=list)
    file_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateAssetRequest(BaseModel):
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    category: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class RollbackRequest(BaseModel):
    target_version: int


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_manager(project_id: str) -> ManifestManager:
    """Resolve project_id to a ManifestManager. project_id = folder name."""
    project_dir = settings.PROJECTS_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    mgr = ManifestManager(project_dir)
    mgr.load()
    return mgr


def _get_version_mgr(project_id: str) -> AssetVersionManager:
    project_dir = settings.PROJECTS_DIR / project_id
    return AssetVersionManager(project_dir, max_versions=settings.MAX_ASSET_VERSIONS)


# ── Project CRUD ─────────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_project(req: CreateProjectRequest) -> dict[str, Any]:
    """Create a new OmniForge project."""
    # Sanitize project name for folder
    folder_name = req.project_name.lower().replace(" ", "_")
    project_dir = settings.PROJECTS_DIR / folder_name

    if project_dir.exists():
        raise HTTPException(status_code=409, detail="Project already exists")

    mgr = ManifestManager(project_dir)
    manifest = mgr.create(
        project_name=req.project_name,
        target_resolution={"width": req.target_resolution_w, "height": req.target_resolution_h},
        tile_size=req.tile_size,
        base_fps=req.base_fps,
        godot_project_path=req.godot_project_path,
    )

    return {
        "id": folder_name,
        "project_name": manifest.project_name,
        "path": str(project_dir),
    }


@router.get("")
async def list_projects() -> list[dict[str, str]]:
    """List all projects in the projects directory."""
    settings.ensure_dirs()
    projects = []
    for p in settings.PROJECTS_DIR.iterdir():
        manifest_file = p / "omniforge.project.json"
        if p.is_dir() and manifest_file.exists():
            try:
                mgr = ManifestManager(p)
                mgr.load()
                projects.append({
                    "id": p.name,
                    "project_name": mgr.manifest.project_name,
                    "path": str(p),
                })
            except Exception:
                continue
    return projects


@router.get("/{project_id}")
async def get_project(project_id: str) -> dict[str, Any]:
    """Get full project details including manifest."""
    mgr = _get_manager(project_id)
    return {
        "id": project_id,
        "manifest": mgr.manifest.model_dump(mode="json"),
    }


@router.put("/{project_id}")
async def update_project(project_id: str, req: UpdateProjectRequest) -> dict[str, Any]:
    """Update project settings."""
    mgr = _get_manager(project_id)

    updates = req.model_dump(exclude_none=True)
    manifest = mgr.manifest

    if "project_name" in updates:
        manifest.project_name = updates["project_name"]
    if "target_resolution_w" in updates or "target_resolution_h" in updates:
        manifest.target_resolution.width = updates.get("target_resolution_w", manifest.target_resolution.width)
        manifest.target_resolution.height = updates.get("target_resolution_h", manifest.target_resolution.height)
    if "tile_size" in updates:
        manifest.tile_size = updates["tile_size"]
    if "base_fps" in updates:
        manifest.base_fps = updates["base_fps"]
    if "godot_project_path" in updates:
        manifest.godot_project_path = updates["godot_project_path"]
    if "palette_reference" in updates:
        manifest.palette_reference = updates["palette_reference"]
    if "light_direction_degrees" in updates:
        manifest.light_direction_degrees = updates["light_direction_degrees"]
    if "naming_convention" in updates:
        manifest.naming_convention = updates["naming_convention"]

    mgr.save()
    return {"id": project_id, "manifest": manifest.model_dump(mode="json")}


@router.delete("/{project_id}")
async def delete_project(project_id: str) -> dict[str, str]:
    """Delete a project and all its files."""
    project_dir = settings.PROJECTS_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    import shutil
    shutil.rmtree(project_dir)
    return {"status": "deleted", "id": project_id}


# ── Asset CRUD ───────────────────────────────────────────────────────────────

@router.post("/{project_id}/assets", status_code=201)
async def add_asset(project_id: str, req: AddAssetRequest) -> dict[str, Any]:
    """Add an asset to the project manifest."""
    mgr = _get_manager(project_id)

    asset = AssetEntry(
        name=req.name,
        type=req.type,
        category=req.category,
        tags=req.tags,
        file_path=req.file_path,
        metadata=AssetMetadata(**req.metadata) if req.metadata else AssetMetadata(),
    )

    mgr.add_asset(asset)

    # Create initial version snapshot
    ver_mgr = _get_version_mgr(project_id)
    ver_mgr.create_version(asset.id, mgr)

    return {"asset": asset.model_dump(mode="json")}


@router.get("/{project_id}/assets")
async def list_assets(
    project_id: str,
    tag: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
) -> list[dict[str, Any]]:
    """List assets with optional tag/category filters."""
    mgr = _get_manager(project_id)

    assets = mgr.manifest.assets
    if tag:
        assets = [a for a in assets if tag in a.tags]
    if category:
        assets = [a for a in assets if a.category == category]

    return [a.model_dump(mode="json") for a in assets]


@router.put("/{project_id}/assets/{asset_id}")
async def update_asset(project_id: str, asset_id: str, req: UpdateAssetRequest) -> dict[str, Any]:
    """Update an asset's properties."""
    mgr = _get_manager(project_id)
    updates = req.model_dump(exclude_none=True)

    # Create version before update
    ver_mgr = _get_version_mgr(project_id)
    ver_mgr.create_version(asset_id, mgr)

    asset = mgr.update_asset(asset_id, updates)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return {"asset": asset.model_dump(mode="json")}


@router.delete("/{project_id}/assets/{asset_id}")
async def delete_asset(project_id: str, asset_id: str) -> dict[str, str]:
    """Remove an asset from the project."""
    mgr = _get_manager(project_id)
    if not mgr.remove_asset(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"status": "deleted", "asset_id": asset_id}


# ── Versioning ───────────────────────────────────────────────────────────────

@router.get("/{project_id}/assets/{asset_id}/history")
async def get_asset_history(project_id: str, asset_id: str) -> list[dict[str, Any]]:
    """Get version history for an asset."""
    ver_mgr = _get_version_mgr(project_id)
    return ver_mgr.get_history(asset_id)


@router.post("/{project_id}/assets/{asset_id}/rollback")
async def rollback_asset(project_id: str, asset_id: str, req: RollbackRequest) -> dict[str, Any]:
    """Rollback an asset to a previous version."""
    mgr = _get_manager(project_id)
    ver_mgr = _get_version_mgr(project_id)

    success = ver_mgr.rollback(asset_id, req.target_version, mgr)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed — version not found or file missing")

    return {"status": "rolled_back", "asset_id": asset_id, "version": req.target_version}


# ── Conflict Detection ───────────────────────────────────────────────────────

@router.get("/{project_id}/conflicts")
async def check_conflicts(project_id: str) -> list[dict[str, str]]:
    """Check for disk conflicts (external file changes)."""
    mgr = _get_manager(project_id)
    return mgr.check_disk_conflicts()
