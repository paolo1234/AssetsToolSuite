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


class ComfyUIStatus:
    """Checks ComfyUI availability and installed models/nodes."""
    
    def __init__(self, server_url: str = "http://localhost:8188"):
        self.server_url = server_url.rstrip("/")
    
    async def check_health(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/system_stats") as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def get_models(self) -> dict:
        """Get available checkpoints."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/object_info/CheckpointLoaderSimple") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("output", {}).get("required", {}).get("ckpt_name", [{}])[0].get("choices", [])
        except Exception:
            pass
        return []
    
    async def get_custom_nodes(self) -> list:
        """Get installed custom nodes."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/system_stats") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("plugins", [])
        except Exception:
            pass
        return []
    
    async def download_model(self, model_name: str, model_type: str = "checkpoints") -> bool:
        """Download a model from HuggingFace or other sources."""
        # This would typically download from HF or CivitAI
        # For now, return False as actual download needs more setup
        return False


STANDARD_WORKFLOWS = {
    "sprite_single": {
        "nodes_required": [],
        "models_required": [],
    },
    "spritesheet_animation": {
        "nodes_required": [],
        "models_required": [],
    },
    "background_tileable": {
        "nodes_required": [],
        "models_required": [],
    },
    "ui_icon_button": {
        "nodes_required": [],
        "models_required": [],
    },
    "prop_item": {
        "nodes_required": [],
        "models_required": [],
    },
    "tilemap_tileset": {
        "nodes_required": [],
        "models_required": [],
    },
    "vfx_particles": {
        "nodes_required": [],
        "models_required": [],
    },
    "character_portrait": {
        "nodes_required": [],
        "models_required": [],
    },
}


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

    async def get_comfyui_status(self) -> dict:
        """Get ComfyUI status, available models and check workflow compatibility."""
        status = {
            "connected": False,
            "available_models": [],
            "workflows_compatible": {},
            "missing_nodes": {},
            "missing_models": {},
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check connection
                async with session.get(f"{self.server_url}/system_stats") as resp:
                    if resp.status == 200:
                        status["connected"] = True
                        
                # Get available models
                async with session.get(f"{self.server_url}/object_info/CheckpointLoaderSimple") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choices = data.get("output", {}).get("required", {}).get("ckpt_name", [{}])
                        if choices:
                            status["available_models"] = choices[0].get("choices", [])
                
                # Check each workflow
                for wf_id, wf_info in STANDARD_WORKFLOWS.items():
                    compatible = True
                    missing_nodes = []
                    missing_models = []
                    
                    # Check nodes
                    loaded = self.load_workflow(wf_id)
                    if loaded:
                        for node_id, node in loaded.items():
                            class_type = node.get("class_type", "")
                            if class_type not in ["KSampler", "CheckpointLoaderSimple", "CLIPTextEncode", 
                                                  "EmptyLatentImage", "VAEDecode", "SaveImage", "VAEEncode",
                                                  "ImageScale", "LoadImage", "LoraLoader", "ControlNetLoader",
                                                  "ControlNetApply"]:
                                missing_nodes.append(class_type)
                    
                    status["workflows_compatible"][wf_id] = not missing_nodes
                    if missing_nodes:
                        status["missing_nodes"][wf_id] = list(set(missing_nodes))
                        
        except Exception as e:
            status["error"] = str(e)
            
        return status

    def get_standard_workflow(self, workflow_id: str, prompt: str, params: dict) -> dict:
        """Get a workflow that uses only standard nodes (no custom nodes)."""
        preset = WORKFLOW_PRESETS.get(workflow_id, WORKFLOW_PRESETS["sprite_single"])
        size = preset.get("default_size", (512, 512))
        steps = preset.get("default_steps", 25)
        
        workflow = {
            "3": {"class_type": "KSampler", "inputs": {
                "seed": params.get("seed", 42),
                "steps": params.get("steps", steps),
                "cfg": params.get("cfg", 8),
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {
                "ckpt_name": "SDXL\\sd_xl_base_1.0.safetensors"
            }},
            "5": {"class_type": "EmptyLatentImage", "inputs": {
                "width": params.get("width", size[0]),
                "height": params.get("height", size[1]),
                "batch_size": 1
            }},
            "6": {"class_type": "CLIPTextEncode", "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            }},
            "7": {"class_type": "CLIPTextEncode", "inputs": {
                "text": preset.get("negative_default", "low quality, blurry, watermark"),
                "clip": ["4", 1]
            }},
            "8": {"class_type": "VAEDecode", "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }},
            "9": {"class_type": "SaveImage", "inputs": {
                "filename_prefix": f"omni_{workflow_id}",
                "images": ["8", 0]
            }}
        }
        
        return workflow

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
        Uses standard-only workflow to avoid missing node errors.
        """
        start_time = asyncio.get_event_loop().time()
        
        workflow_id = params.get("workflow_id", "sprite_single")
        
        # Use standard workflow (only built-in nodes) to avoid missing node errors
        workflow = self.get_standard_workflow(workflow_id, prompt, params)
        
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
