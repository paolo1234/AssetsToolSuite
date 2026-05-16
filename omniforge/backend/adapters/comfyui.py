"""
OmniForge Backend — ComfyUI Adapter
Connects to a local ComfyUI instance via its API and WebSocket.
"""

from __future__ import annotations

import asyncio
import json
import uuid
import aiohttp
from typing import Any, Optional

from .base import AIAdapter, AdapterType, GenerationResult


class ComfyUIAdapter(AIAdapter):
    """
    Adapter for local ComfyUI server.
    Handles workflow submission, progress tracking via WebSocket, and output retrieval.
    """

    def __init__(self, server_url: str = "http://localhost:8188") -> None:
        self.server_url = server_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

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
        Execute a ComfyUI workflow.
        In a real scenario, this would load a JSON workflow template and inject the prompt.
        """
        start_time = asyncio.get_event_loop().time()
        
        # 1. Prepare simple workflow (example structure)
        # This is a simplified mock of a ComfyUI API request
        workflow = params.get("workflow", self._get_default_workflow(prompt, params))
        
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
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
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
