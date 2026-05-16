"""
OmniForge Backend — ComfyUI Adapter
Connects to a local ComfyUI instance via its API and WebSocket.
"""

from __future__ import annotations

import asyncio
import json
import uuid
import aiohttp
from pathlib import Path
from typing import Any, Optional

from adapters.base import AIAdapter, AdapterType, GenerationResult


WORKFLOW_PRESETS = {
    "sprite_single": {
        "name": "Single Sprite",
        "description": "Generate single game sprite (character, NPC, enemy)",
        "positive_default": "pixel art game character, 2d sprite, isometric view, consistent style",
        "negative_default": "3d, blurry, low quality, watermark, text, multiple objects",
        "default_size": (512, 512),
        "default_steps": 25,
    },
    "spritesheet_animation": {
        "name": "Spritesheet Animation",
        "description": "Generate animated sprite sheet (walk, attack, idle)",
        "positive_default": "video game sprite sheet, walk cycle frames, consistent character",
        "negative_default": "inconsistent frames, bad anatomy, blurry, low quality",
        "default_size": (1024, 1024),
        "default_steps": 30,
    },
    "background_tileable": {
        "name": "Tileable Background",
        "description": "Generate seamless background for game scenes",
        "positive_default": "game background, forest, atmospheric",
        "negative_default": "asymmetric, visible seams, gradient, low quality",
        "default_size": (512, 512),
        "default_steps": 28,
    },
    "ui_icon_button": {
        "name": "UI Icon/Button",
        "description": "Generate UI elements (icons, buttons, inventory items)",
        "positive_default": "game ui icon, clean vector style, flat design",
        "negative_default": "3d, realistic, shadows, gradients, messy",
        "default_size": (256, 256),
        "default_steps": 20,
    },
    "prop_item": {
        "name": "Props & Items",
        "description": "Generate game props, items, weapons, artifacts",
        "positive_default": "video game prop, isometric item, glowing sword",
        "negative_default": "3d, realistic, multiple objects, blurry, photograph",
        "default_size": (512, 512),
        "default_steps": 25,
    },
    "tilemap_tileset": {
        "name": "Tileset",
        "description": "Generate tileable tileset for tilemap editors",
        "positive_default": "pixel art game tile, grass, stone, ground",
        "negative_default": "asymmetric, visible seams, broken edges, 3d",
        "default_size": (256, 256),
        "default_steps": 25,
    },
    "vfx_particles": {
        "name": "VFX & Particles",
        "description": "Generate particle effects and spell visuals",
        "positive_default": "game vfx effect, particle system, magical spell",
        "negative_default": "static, non-animated, blurry, solid background",
        "default_size": (512, 512),
        "default_steps": 25,
    },
    "character_portrait": {
        "name": "Character Portrait",
        "description": "Generate character portraits and face sprites",
        "positive_default": "game character portrait, detailed face, consistent style",
        "negative_default": "3d, realistic, blurry, deformed anatomy, bad proportions",
        "default_size": (512, 512),
        "default_steps": 28,
    },
}


class ComfyUIAdapter(AIAdapter):
    """
    Adapter for local ComfyUI server.
    Handles workflow submission, progress tracking via WebSocket, and output retrieval.
    """

    def __init__(self, server_url: str = "http://localhost:8188", workflow_dir: str = None) -> None:
        self.server_url = server_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self.workflow_dir = Path(workflow_dir) if workflow_dir else Path(__file__).parent.parent.parent.parent / "comfy_workflows"
        self._workflow_cache: dict[str, dict] = {}

    @staticmethod
    def get_workflow_presets() -> dict:
        return WORKFLOW_PRESETS

    def load_workflow(self, workflow_id: str) -> Optional[dict]:
        if workflow_id in self._workflow_cache:
            return self._workflow_cache[workflow_id]
        
        workflow_file = self.workflow_dir / f"{workflow_id}.json"
        if workflow_file.exists():
            try:
                with open(workflow_file, "r") as f:
                    workflow = json.load(f)
                    self._workflow_cache[workflow_id] = workflow
                    return workflow
            except Exception:
                pass
        return None

    def inject_prompt(self, workflow: dict, prompt: str, params: dict) -> dict:
        injected = json.loads(json.dumps(workflow))
        
        preset = WORKFLOW_PRESETS.get(params.get("workflow_id", "sprite_single"))
        negative = preset.get("negative_default", "low quality") if preset else "low quality"
        
        for node_id, node in injected.items():
            if node.get("class_type") == "CLIPTextEncode":
                inputs = node.get("inputs", {})
                text = inputs.get("text", "")
                if "{{positive_prompt}}" in text:
                    inputs["text"] = text.replace("{{positive_prompt}}", prompt)
                elif "text" in inputs and node_id != "7":
                    inputs["text"] = prompt
                if "{{negative_prompt}}" in text:
                    inputs["text"] = text.replace("{{negative_prompt}}", negative)
            elif node.get("class_type") == "KSampler":
                inputs = node.get("inputs", {})
                if "seed" in inputs:
                    inputs["seed"] = params.get("seed", 42)
                if "steps" in inputs:
                    inputs["steps"] = params.get("steps", preset.get("default_steps", 25) if preset else 25)
                if "cfg" in inputs:
                    inputs["cfg"] = params.get("cfg", 8)
            elif node.get("class_type") == "EmptyLatentImage":
                inputs = node.get("inputs", {})
                size = preset.get("default_size", (512, 512)) if preset else (512, 512)
                inputs["width"] = params.get("width", size[0])
                inputs["height"] = params.get("height", size[1])
        
        return injected

    def get_name(self) -> str:
        return "ComfyUI Local"

    def get_adapter_type(self) -> AdapterType:
        return AdapterType.IMAGE

    def get_supported_params(self) -> list[str]:
        return ["steps", "cfg", "sampler_name", "scheduler", "denoise", "seed", "workflow_id"]

    async def check_health(self) -> bool:
        """Check if ComfyUI is reachable."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/system_stats") as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def generate(self, prompt: str, params: dict[str, Any]) -> GenerationResult:
        """
        Execute a ComfyUI workflow using preset templates.
        """
        start_time = asyncio.get_event_loop().time()
        
        workflow_id = params.get("workflow_id", "sprite_single")
        
        if workflow_id == "default":
            workflow = self._get_default_workflow(prompt, params)
        else:
            loaded = self.load_workflow(workflow_id)
            if loaded:
                workflow = self.inject_prompt(loaded, prompt, params)
            else:
                workflow = self._get_default_workflow(prompt, params)
        
        try:
            async with aiohttp.ClientSession() as session:
                # 2. Submit prompt
                payload = {"prompt": workflow, "client_id": self.client_id}
                async with session.post(f"{self.server_url}/prompt", json=payload) as resp:
                    if resp.status != 200:
                        err = await resp.text()
                        return GenerationResult(success=False, error_message=f"ComfyUI Error: {err}")
                    
                    data = await resp.json()
                    prompt_id = data["prompt_id"]

                # 3. Wait for completion (via polling or websocket)
                # For brevity, we poll the history
                while True:
                    async with session.get(f"{self.server_url}/history/{prompt_id}") as resp:
                        history = await resp.json()
                        if prompt_id in history:
                            break
                    await asyncio.sleep(1)

                # 4. Extract output
                outputs = history[prompt_id]["outputs"]
                # Get first image from first node
                image_info = None
                for node_id in outputs:
                    if "images" in outputs[node_id]:
                        image_info = outputs[node_id]["images"][0]
                        break
                
                if not image_info:
                    return GenerationResult(success=False, error_message="No image generated")

                # 5. Download image bytes
                img_params = {
                    "filename": image_info["filename"],
                    "subfolder": image_info["subfolder"],
                    "type": image_info["type"]
                }
                async with session.get(f"{self.server_url}/view", params=img_params) as resp:
                    image_bytes = await resp.read()

                duration = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return GenerationResult(
                    success=True,
                    file_bytes=image_bytes,
                    mime_type="image/png",
                    prompt_used=prompt,
                    adapter_name=self.get_name(),
                    duration_ms=duration,
                    seed=params.get("seed")
                )

        except Exception as e:
            return GenerationResult(success=False, error_message=str(e))

    def _get_default_workflow(self, prompt: str, params: dict[str, Any]) -> dict[str, Any]:
        """Simple txt2img workflow for ComfyUI API."""
        return {
            "3": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": params.get("steps", 20),
                    "cfg": params.get("cfg", 8),
                    "sampler_name": params.get("sampler_name", "euler"),
                    "scheduler": params.get("scheduler", "normal"),
                    "denoise": params.get("denoise", 1),
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {"ckpt_name": "SD1.5\\v1-5-pruned-emaonly.ckpt"},
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {"text": prompt, "clip": ["4", 1]},
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {"text": "text, watermark, low quality", "clip": ["4", 1]},
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {"filename_prefix": "OmniForge", "images": ["8", 0]},
                "class_type": "SaveImage"
            }
        }
