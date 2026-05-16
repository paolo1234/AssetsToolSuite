"""
OmniForge Backend — Image Processor
Handles prompt building, rembg, palette quantization, and pixel art filtering.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PIL import Image
from rembg import remove

from ..project.manifest import ProjectManifest


class PromptBuilder:
    """Enhanced prompts with project style tags."""

    @staticmethod
    def build(user_prompt: str, manifest: ProjectManifest) -> str:
        """
        Inject style tags from manifest into user prompt.
        Example: "a hero" -> "a hero, pixel art, 16-bit, limited palette"
        """
        # In a real scenario, we'd extract actual style tags from manifest.presets or similar
        # For now, we simulate basic style injection
        style_hints = []
        if manifest.tile_size <= 32:
            style_hints.append("pixel art")
        
        # Add project name as context if it's a specific art style
        # prompt = f"{user_prompt}, {', '.join(style_hints)}"
        
        # Simulate advanced building
        if not style_hints:
            return user_prompt
        return f"{user_prompt}, {', '.join(style_hints)}"


class ImageProcessor:
    """
    Core image processing logic: background removal, palette, pixelation.
    Operations are generally non-destructive until saved.
    """

    @staticmethod
    def remove_background(image_bytes: bytes) -> bytes:
        """Remove background using rembg."""
        input_image = Image.open(io.BytesIO(image_bytes))
        output_image = remove(input_image)
        
        out_io = io.BytesIO()
        output_image.save(out_io, format="PNG")
        return out_io.getvalue()

    @staticmethod
    def quantize_palette(image_bytes: bytes, colors: int = 16, dither: bool = True) -> bytes:
        """Reduce image to a specific number of colors with optional dithering."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        
        # Quantize
        dither_val = Image.FLOYDSTEINBERG if dither else Image.NONE
        # Note: Quantize requires 'P' or 'RGB' mode
        alpha = img.getchannel('A')
        img_rgb = img.convert("RGB")
        
        quantized = img_rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=dither_val)
        
        # Restore alpha
        result = quantized.convert("RGBA")
        result.putalpha(alpha)
        
        out_io = io.BytesIO()
        result.save(out_io, format="PNG")
        return out_io.getvalue()

    @staticmethod
    def apply_pixel_art_filter(image_bytes: bytes, target_width: int, target_height: int) -> bytes:
        """Downscale with nearest neighbor to create a pixelated look."""
        img = Image.open(io.BytesIO(image_bytes))
        
        # Downscale
        small = img.resize((target_width, target_height), Image.NEAREST)
        
        # Upscale back to original (optional, depends on if we want to preview at scale)
        # upscale = small.resize(img.size, Image.NEAREST)
        
        out_io = io.BytesIO()
        small.save(out_io, format="PNG")
        return out_io.getvalue()

    @staticmethod
    def apply_pipeline(image_bytes: bytes, pipeline: list[dict[str, Any]]) -> bytes:
        """Apply a sequence of processing steps."""
        current = image_bytes
        for step in pipeline:
            op = step.get("op")
            params = step.get("params", {})
            
            if op == "remove_bg":
                current = ImageProcessor.remove_background(current)
            elif op == "palette":
                current = ImageProcessor.quantize_palette(
                    current, 
                    colors=params.get("colors", 16),
                    dither=params.get("dither", True)
                )
            elif op == "pixelate":
                current = ImageProcessor.apply_pixel_art_filter(
                    current,
                    target_width=params.get("width", 64),
                    target_height=params.get("height", 64)
                )
        return current
