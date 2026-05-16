"""
OmniForge Backend — Spritesheet Processor
Handles automatic slicing, grid detection, and metadata extraction.
"""

from __future__ import annotations

import io
from typing import Any, Optional
from PIL import Image


class SpritesheetProcessor:
    """
    Logic for slicing spritesheets into individual frames.
    Supports fixed grid and atlas (detected by transparency).
    """

    @staticmethod
    def detect_grid(image_bytes: bytes) -> dict[str, int]:
        """
        Attempt to detect grid size based on image dimensions.
        Very basic heuristic for now.
        """
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        
        # Check common sizes
        for size in [16, 32, 64, 128]:
            if w % size == 0 and h % size == 0:
                return {"frame_width": size, "frame_height": size}
        
        return {"frame_width": w, "frame_height": h}

    @staticmethod
    def slice_grid(image_bytes: bytes, frame_width: int, frame_height: int) -> list[bytes]:
        """Slice into a list of PNG frames."""
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        
        frames = []
        for y in range(0, h, frame_height):
            for x in range(0, w, frame_width):
                box = (x, y, x + frame_width, y + frame_height)
                frame = img.crop(box)
                
                # Check if frame is empty (all transparent)
                if frame.getbbox():
                    out_io = io.BytesIO()
                    frame.save(out_io, format="PNG")
                    frames.append(out_io.getvalue())
        
        return frames

    @staticmethod
    def export_godot_resource(frames_metadata: list[dict[str, Any]], atlas_path: str) -> str:
        """
        Generate a Godot 4.x .tres (SpriteFrames) content string.
        """
        # This is a simplified version of a Godot resource file
        res = [
            '[gd_resource type="SpriteFrames" load_steps=2 format=3]',
            f'[ext_resource type="Texture2D" path="{atlas_path}" id="1_tex"]',
            '',
            '[resource]',
            'animations = [{',
            '  "frames": ['
        ]
        
        for f in frames_metadata:
            # Godot AtlasTexture format
            res.append(f'    {{ "texture": SubResource("AtlasTexture_{f["id"]}") }},')
            
        res.extend([
            '  ],',
            '  "loop": true,',
            '  "name": "default",',
            '  "speed": 10.0',
            '}]'
        ])
        
        return "\n".join(res)
