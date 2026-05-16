from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Optional


class GameProjectScanner:
    EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
                  '.wav', '.mp3', '.ogg', '.flac',
                  '.tres', '.res', '.tscn', '.gd',
                  '.prefab', '.unity', '.asset', '.fbx', '.glb', '.gltf',
                  '.yyp', '.yy', '.sprite', '.obj', '.blend'}

    @staticmethod
    def detect_engine(root: Path) -> str:
        indicators = {
            'godot': ['project.godot', '.godot'],
            'unity': ['Assets/', 'ProjectSettings/', 'Packages/manifest.json'],
            'gamemaker': ['Project.yyp', '*.yyp'],
            'unreal': ['*.uproject', 'Config/'],
            'phaser': ['package.json', 'index.html'],
        }
        for engine, markers in indicators.items():
            for marker in markers:
                if marker.endswith('/'):
                    if (root / marker).exists():
                        return engine
                else:
                    matches = list(root.rglob(marker))
                    if matches:
                        return engine
        return 'generic'

    @staticmethod
    def scan_folder(root: Path, recursive: bool = True) -> dict[str, Any]:
        root = Path(root).resolve()
        if not root.exists():
            return {'error': 'Path not found', 'assets': []}

        engine = GameProjectScanner.detect_engine(root)
        assets = []
        issues = []

        pattern = '**/*' if recursive else '*'
        for file_path in root.glob(pattern):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext not in GameProjectScanner.EXTENSIONS:
                continue

            rel_path = file_path.relative_to(root).as_posix()
            size_kb = file_path.stat().st_size / 1024
            asset_type = GameProjectScanner._classify(ext)

            entry = {
                'path': rel_path,
                'name': file_path.stem,
                'ext': ext,
                'size_kb': round(size_kb, 1),
                'type': asset_type,
                'engine': engine,
            }

            issues.extend(GameProjectScanner._check_issues(entry, file_path))
            assets.append(entry)

        return {
            'engine': engine,
            'root': str(root),
            'total_assets': len(assets),
            'assets': assets,
            'issues': issues,
        }

    @staticmethod
    def _classify(ext: str) -> str:
        image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        audio_exts = {'.wav', '.mp3', '.ogg', '.flac'}
        godot_exts = {'.tres', '.res', '.tscn', '.gd'}
        unity_exts = {'.prefab', '.unity', '.asset'}
        model_exts = {'.fbx', '.glb', '.gltf', '.obj', '.blend'}
        if ext in image_exts:
            return 'image'
        if ext in audio_exts:
            return 'audio'
        if ext in godot_exts:
            return 'godot_resource'
        if ext in unity_exts:
            return 'unity_resource'
        if ext in model_exts:
            return 'model'
        return 'other'

    @staticmethod
    def _check_issues(entry: dict, file_path: Path) -> list[dict]:
        issues = []
        name = entry['name']

        if not re.match(r'^[a-zA-Z0-9_\-]+$', name):
            issues.append({
                'asset': entry['path'],
                'severity': 'warning',
                'type': 'naming',
                'message': f'Nome non standard: "{name}" (usa solo lettere, numeri, _ -)',
                'suggested': re.sub(r'[^a-zA-Z0-9_\-]', '_', name),
            })

        if entry['size_kb'] == 0:
            issues.append({
                'asset': entry['path'],
                'severity': 'error',
                'type': 'corrupted',
                'message': f'File vuoto o corrotto (0 KB)',
            })

        if entry['ext'] not in {'.png', '.svg', '.jpg', '.jpeg'} and entry['type'] == 'image':
            issues.append({
                'asset': entry['path'],
                'severity': 'info',
                'type': 'format',
                'message': f'Formato non ottimale: {entry["ext"]}. Convertire in PNG.',
                'suggested': f'{entry["name"]}.png',
            })

        return issues

    @staticmethod
    def fix_naming(path: Path, old_rel: str, new_name: str) -> Optional[str]:
        full = path / old_rel
        if not full.exists():
            return None
        new_rel = Path(old_rel).parent / f'{new_name}{full.suffix}'
        new_full = path / new_rel
        new_full.parent.mkdir(parents=True, exist_ok=True)
        full.rename(new_full)
        return new_rel.as_posix()

    @staticmethod
    def import_into_project(scanned_assets: list[dict], project_dir: Path, dest_dir: str = 'assets') -> list[dict]:
        imported = []
        dest_path = project_dir / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)

        for asset in scanned_assets:
            src = project_dir.parent / asset['path']  # scanned from elsewhere
            if not src.exists():
                continue
            import_name = f"{asset['name']}{asset['ext']}"
            dst = dest_path / import_name
            dst.write_bytes(src.read_bytes())
            imported.append({
                'original': asset['path'],
                'imported': f'{dest_dir}/{import_name}',
                'name': asset['name'],
                'type': asset['type'],
            })

        return imported
