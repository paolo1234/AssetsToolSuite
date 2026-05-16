"""
OmniForge Backend — Project Manifest (SSOT)
Single Source of Truth for all project data.
Every module reads/writes through this class only.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Pydantic Models ──────────────────────────────────────────────────────────

class AssetMetadata(BaseModel):
    """Flexible metadata attached to an asset (frames, fps, pivot, etc.)."""
    frames: Optional[int] = None
    fps: Optional[int] = None
    pivot: Optional[dict[str, int]] = None
    loop_mode: Optional[str] = None  # "loop" | "ping-pong" | "once"
    loop_in: Optional[int] = None
    loop_out: Optional[int] = None
    duration_ms: Optional[int] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class AssetEntry(BaseModel):
    """A single asset tracked in the manifest."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # "image" | "spritesheet" | "audio" | "ui" | "tilemap" | "effect"
    category: str  # "character" | "enemy" | "item" | "environment" | "ui" | "sfx" | "music"
    tags: list[str] = Field(default_factory=list)
    file_path: str  # Relative to project root
    hash_md5: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: int = 1
    metadata: AssetMetadata = Field(default_factory=AssetMetadata)
    dna_id: Optional[str] = None
    quality_score: Optional[int] = None


class Resolution(BaseModel):
    width: int = 320
    height: int = 180


class ProjectManifest(BaseModel):
    """Root manifest — the single source of truth for an OmniForge project."""
    version: str = "1.0"
    project_name: str = "Untitled Project"
    target_resolution: Resolution = Field(default_factory=Resolution)
    tile_size: int = 16
    base_fps: int = 12
    godot_project_path: str = ""
    palette_reference: str = ""
    light_direction_degrees: float = 30.0
    naming_convention: str = "{category}_{name}_{variant}"
    style_bible_images: list[str] = Field(default_factory=list)
    assets: list[AssetEntry] = Field(default_factory=list)
    presets: dict[str, Any] = Field(default_factory=dict)
    export_history: list[dict[str, Any]] = Field(default_factory=list)


# ── Manifest Manager ─────────────────────────────────────────────────────────

MANIFEST_FILENAME = "omniforge.project.json"


class ManifestManager:
    """
    Manages reading/writing the project manifest on disk.
    All state flows through this class — no module keeps its own state.
    """

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.manifest_path = project_dir / MANIFEST_FILENAME
        self._manifest: Optional[ProjectManifest] = None

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def create(self, project_name: str, **kwargs: Any) -> ProjectManifest:
        """Create a new project manifest on disk."""
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories
        for subdir in ["assets", ".versions"]:
            (self.project_dir / subdir).mkdir(exist_ok=True)

        manifest = ProjectManifest(project_name=project_name, **kwargs)
        self._manifest = manifest
        self.save()
        return manifest

    def load(self) -> ProjectManifest:
        """Load manifest from disk. Raises FileNotFoundError if missing."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"No manifest at {self.manifest_path}")

        raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self._manifest = ProjectManifest(**raw)
        return self._manifest

    def save(self) -> None:
        """Persist the current manifest to disk."""
        if self._manifest is None:
            raise RuntimeError("No manifest loaded — call create() or load() first.")

        payload = self._manifest.model_dump(mode="json")
        self.manifest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @property
    def manifest(self) -> ProjectManifest:
        if self._manifest is None:
            raise RuntimeError("Manifest not loaded.")
        return self._manifest

    # ── Asset CRUD ────────────────────────────────────────────────────────

    def add_asset(self, asset: AssetEntry) -> AssetEntry:
        """Add an asset to the manifest and compute its file hash."""
        file_path = self.project_dir / asset.file_path
        if file_path.exists():
            asset.hash_md5 = self._compute_md5(file_path)

        self.manifest.assets.append(asset)
        self.save()
        return asset

    def remove_asset(self, asset_id: str) -> bool:
        """Remove an asset by ID. Returns True if found and removed."""
        before = len(self.manifest.assets)
        self.manifest.assets = [a for a in self.manifest.assets if a.id != asset_id]
        removed = len(self.manifest.assets) < before
        if removed:
            self.save()
        return removed

    def update_asset(self, asset_id: str, updates: dict[str, Any]) -> Optional[AssetEntry]:
        """Update fields of an existing asset."""
        for asset in self.manifest.assets:
            if asset.id == asset_id:
                for key, value in updates.items():
                    if hasattr(asset, key):
                        setattr(asset, key, value)
                asset.updated_at = datetime.now(timezone.utc).isoformat()
                asset.version += 1

                # Recompute hash if file changed
                file_path = self.project_dir / asset.file_path
                if file_path.exists():
                    asset.hash_md5 = self._compute_md5(file_path)

                self.save()
                return asset
        return None

    def get_asset_by_id(self, asset_id: str) -> Optional[AssetEntry]:
        """Find an asset by its UUID."""
        for asset in self.manifest.assets:
            if asset.id == asset_id:
                return asset
        return None

    def get_assets_by_tag(self, tag: str) -> list[AssetEntry]:
        """Filter assets by tag."""
        return [a for a in self.manifest.assets if tag in a.tags]

    def get_assets_by_category(self, category: str) -> list[AssetEntry]:
        """Filter assets by category."""
        return [a for a in self.manifest.assets if a.category == category]

    # ── Disk Conflict Detection ───────────────────────────────────────────

    def check_disk_conflicts(self) -> list[dict[str, str]]:
        """
        Compare stored MD5 hashes with current files on disk.
        Returns a list of conflicts (asset changed externally).
        """
        conflicts: list[dict[str, str]] = []
        for asset in self.manifest.assets:
            file_path = self.project_dir / asset.file_path
            if not file_path.exists():
                conflicts.append({
                    "asset_id": asset.id,
                    "name": asset.name,
                    "issue": "file_missing",
                    "detail": f"File not found: {asset.file_path}",
                })
                continue

            current_hash = self._compute_md5(file_path)
            if asset.hash_md5 and current_hash != asset.hash_md5:
                conflicts.append({
                    "asset_id": asset.id,
                    "name": asset.name,
                    "issue": "file_changed",
                    "detail": f"Hash mismatch: expected {asset.hash_md5[:8]}… got {current_hash[:8]}…",
                })
        return conflicts

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _compute_md5(file_path: Path) -> str:
        """Compute MD5 hash of a file."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
