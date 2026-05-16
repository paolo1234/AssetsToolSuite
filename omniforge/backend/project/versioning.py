"""
OmniForge Backend — Asset Versioning
Maintains up to N versions of each asset for 1-click rollback.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from project.manifest import ManifestManager


class VersionEntry:
    """Represents a single version snapshot of an asset."""

    def __init__(self, version: int, timestamp: str, file_path: str, metadata: dict[str, Any]) -> None:
        self.version = version
        self.timestamp = timestamp
        self.file_path = file_path  # Relative to versions dir
        self.metadata = metadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "file_path": self.file_path,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VersionEntry":
        return cls(
            version=data["version"],
            timestamp=data["timestamp"],
            file_path=data["file_path"],
            metadata=data.get("metadata", {}),
        )


class AssetVersionManager:
    """
    Manages version history for assets.
    Stores up to MAX_VERSIONS copies of each asset file + metadata snapshot.
    
    Storage layout:
        {project}/.versions/{asset_id}/
            versions.json          ← version index
            v001_hero_idle.png     ← file backup
            v002_hero_idle.png
            ...
    """

    def __init__(self, project_dir: Path, max_versions: int = 10) -> None:
        self.project_dir = project_dir
        self.versions_dir = project_dir / ".versions"
        self.max_versions = max_versions
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def _asset_versions_dir(self, asset_id: str) -> Path:
        """Get the version storage directory for a specific asset."""
        d = self.versions_dir / asset_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _load_index(self, asset_id: str) -> list[VersionEntry]:
        """Load the version index for an asset."""
        index_path = self._asset_versions_dir(asset_id) / "versions.json"
        if not index_path.exists():
            return []
        raw = json.loads(index_path.read_text(encoding="utf-8"))
        return [VersionEntry.from_dict(v) for v in raw]

    def _save_index(self, asset_id: str, entries: list[VersionEntry]) -> None:
        """Persist the version index."""
        index_path = self._asset_versions_dir(asset_id) / "versions.json"
        index_path.write_text(
            json.dumps([e.to_dict() for e in entries], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def create_version(self, asset_id: str, manifest_mgr: ManifestManager) -> Optional[VersionEntry]:
        """
        Snapshot the current state of an asset.
        Copies the file and saves metadata from the manifest.
        """
        asset = manifest_mgr.get_asset_by_id(asset_id)
        if asset is None:
            return None

        source_file = self.project_dir / asset.file_path
        if not source_file.exists():
            return None

        entries = self._load_index(asset_id)
        new_version = (entries[-1].version + 1) if entries else 1

        # Copy file to versions directory
        ext = source_file.suffix
        backup_name = f"v{new_version:03d}_{source_file.stem}{ext}"
        backup_path = self._asset_versions_dir(asset_id) / backup_name

        shutil.copy2(source_file, backup_path)

        # Create version entry with metadata snapshot
        entry = VersionEntry(
            version=new_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            file_path=backup_name,
            metadata=asset.metadata.model_dump() if asset.metadata else {},
        )
        entries.append(entry)

        # Enforce max versions — remove oldest if over limit
        if len(entries) > self.max_versions:
            removed = entries[: len(entries) - self.max_versions]
            entries = entries[len(entries) - self.max_versions :]
            for old in removed:
                old_path = self._asset_versions_dir(asset_id) / old.file_path
                if old_path.exists():
                    old_path.unlink()

        self._save_index(asset_id, entries)
        return entry

    def rollback(self, asset_id: str, target_version: int, manifest_mgr: ManifestManager) -> bool:
        """
        Rollback an asset to a previous version.
        Restores the file and metadata from the version snapshot.
        """
        entries = self._load_index(asset_id)
        target = next((e for e in entries if e.version == target_version), None)
        if target is None:
            return False

        asset = manifest_mgr.get_asset_by_id(asset_id)
        if asset is None:
            return False

        # Restore file
        backup_path = self._asset_versions_dir(asset_id) / target.file_path
        if not backup_path.exists():
            return False

        dest_path = self.project_dir / asset.file_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, dest_path)

        # Restore metadata in manifest
        manifest_mgr.update_asset(asset_id, {
            "metadata": target.metadata,
        })

        return True

    def get_history(self, asset_id: str) -> list[dict[str, Any]]:
        """Get the version history for an asset."""
        entries = self._load_index(asset_id)
        return [e.to_dict() for e in entries]

    def cleanup_old(self, asset_id: str) -> int:
        """Remove versions beyond the max limit. Returns count of removed versions."""
        entries = self._load_index(asset_id)
        if len(entries) <= self.max_versions:
            return 0

        removed_count = len(entries) - self.max_versions
        removed = entries[:removed_count]
        entries = entries[removed_count:]

        for old in removed:
            old_path = self._asset_versions_dir(asset_id) / old.file_path
            if old_path.exists():
                old_path.unlink()

        self._save_index(asset_id, entries)
        return removed_count
