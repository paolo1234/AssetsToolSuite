from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from processors.importer import GameProjectScanner
from project.manifest import AssetEntry, AssetMetadata
from routers.project import _get_manager

router = APIRouter(prefix="/api/projects", tags=["importer"])


class ScanRequest(BaseModel):
    folder_path: str
    recursive: bool = True


class ImportRequest(BaseModel):
    folder_path: str
    recursive: bool = True
    file_patterns: list[str] = []


class FixRequest(BaseModel):
    auto_rename: bool = False
    auto_convert: bool = False


@router.post("/{project_id}/import/scan")
async def scan_folder(project_id: str, req: ScanRequest):
    """Scan a folder for game assets and detect engine type."""
    folder = Path(req.folder_path)
    if not folder.exists():
        raise HTTPException(status_code=400, detail="Cartella non trovata")

    result = GameProjectScanner.scan_folder(folder, req.recursive)

    result['importable'] = [
        a for a in result['assets']
        if a['type'] in ('image', 'audio')
    ]

    return result


@router.post("/{project_id}/import/run")
async def import_assets(project_id: str, req: ImportRequest):
    """Import found assets into the project manifest."""
    mgr = _get_manager(project_id)
    folder = Path(req.folder_path)

    if not folder.exists():
        raise HTTPException(status_code=400, detail="Cartella non trovata")

    scan = GameProjectScanner.scan_folder(folder, req.recursive)

    patterns = set(req.file_patterns) or {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.wav', '.mp3', '.ogg'}
    assets_to_import = [
        a for a in scan['assets']
        if a['ext'] in patterns
    ]

    imported = []
    for asset_data in assets_to_import:
        src = folder / asset_data['path']
        if not src.exists():
            continue

        asset_id = f"imp_{len(imported):04d}"
        ext = asset_data['ext']
        new_name = f"{asset_id}{ext}"
        rel_path = f"assets/{new_name}"
        full_path = mgr.project_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(src.read_bytes())

        new_asset = AssetEntry(
            id=asset_id,
            name=asset_data['name'],
            type=asset_data['type'],
            category='imported',
            tags=['imported', asset_data['engine']],
            file_path=rel_path,
            metadata=AssetMetadata(
                source='import',
                original_path=asset_data['path'],
                original_size_kb=asset_data['size_kb'],
            )
        )
        mgr.add_asset(new_asset)
        imported.append({
            'asset_id': asset_id,
            'name': asset_data['name'],
            'type': asset_data['type'],
            'file_path': rel_path,
        })

    if imported:
        mgr.save()

    return {
        'engine': scan['engine'],
        'scanned': scan['total_assets'],
        'imported': len(imported),
        'assets': imported,
    }


@router.get("/{project_id}/fix/check")
async def check_fixes(project_id: str):
    """Check all assets in the project for common issues."""
    mgr = _get_manager(project_id)
    issues = []

    for asset in mgr.manifest.assets:
        name = asset.name or ''
        if not re.match(r'^[a-zA-Z0-9_\-]+$', name):
            issues.append({
                'asset_id': asset.id,
                'name': name,
                'severity': 'warning',
                'type': 'naming',
                'message': f'Nome non standard: "{name}"',
                'suggested': re.sub(r'[^a-zA-Z0-9_\-]', '_', name),
            })

        file_path = mgr.project_dir / asset.file_path
        if not file_path.exists():
            issues.append({
                'asset_id': asset.id,
                'name': name,
                'severity': 'error',
                'type': 'missing_file',
                'message': f'File mancante: {asset.file_path}',
            })
        elif file_path.stat().st_size == 0:
            issues.append({
                'asset_id': asset.id,
                'name': name,
                'severity': 'error',
                'type': 'corrupted',
                'message': f'File vuoto: {asset.file_path}',
            })

    return {'issues': issues, 'total': len(issues)}


@router.post("/{project_id}/fix/run")
async def run_fixes(project_id: str, req: FixRequest):
    """Auto-fix identified issues."""
    mgr = _get_manager(project_id)
    fixes = []

    for asset in mgr.manifest.assets:
        asset_obj = vars(mgr.manifest)

        if req.auto_rename and asset.name:
            name = asset.name
            if not re.match(r'^[a-zA-Z0-9_\-]+$', name):
                new_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
                mgr.update_asset(asset.id, {'name': new_name})
                fixes.append({
                    'asset_id': asset.id,
                    'type': 'rename',
                    'from': name,
                    'to': new_name,
                })

        file_path = mgr.project_dir / asset.file_path
        if req.auto_convert and file_path.suffix.lower() not in {'.png', '.svg', '.jpg'}:
            if asset.type == 'image' and file_path.exists():
                from PIL import Image
                import io
                try:
                    img = Image.open(file_path)
                    new_path = file_path.with_suffix('.png')
                    img.save(new_path, 'PNG')
                    if file_path != new_path:
                        file_path.unlink()
                    mgr.update_asset(asset.id, {'file_path': new_path.relative_to(mgr.project_dir).as_posix()})
                    fixes.append({
                        'asset_id': asset.id,
                        'type': 'convert',
                        'from': file_path.name,
                        'to': new_path.name,
                    })
                except Exception:
                    pass

    mgr.save()
    return {'fixed': len(fixes), 'fixes': fixes}
