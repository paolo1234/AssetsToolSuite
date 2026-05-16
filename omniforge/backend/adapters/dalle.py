"""
OmniForge Backend — DALL-E Adapter
Connects to OpenAI API for cloud image generation.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from adapters.base import AIAdapter, AdapterType, GenerationResult


class DallEAdapter(AIAdapter):
    """
    Adapter for OpenAI DALL-E 3 API.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/images/generations"

    def get_name(self) -> str:
        return "DALL-E 3 (Cloud)"

    def get_adapter_type(self) -> AdapterType:
        return AdapterType.IMAGE

    def get_supported_params(self) -> list[str]:
        return ["quality", "style", "size"]

    async def check_health(self) -> bool:
        """Simple check if API key is provided."""
        return bool(self.api_key)

    async def generate(self, prompt: str, params: dict[str, Any]) -> GenerationResult:
        """Generate image via DALL-E 3."""
        start_time = asyncio.get_event_loop().time()
        
        if not self.api_key:
            return GenerationResult(success=False, error_message="OpenAI API Key missing")

        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": params.get("size", "1024x1024"),
            "quality": params.get("quality", "standard"),
            "style": params.get("style", "vivid"),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                
                if resp.status_code != 200:
                    err_data = resp.json()
                    return GenerationResult(
                        success=False, 
                        error_message=err_data.get("error", {}).get("message", "OpenAI API Error")
                    )
                
                data = resp.json()
                img_url = data["data"][0]["url"]
                revised_prompt = data["data"][0].get("revised_prompt", "")

                # Download the image from the temporary URL
                img_resp = await client.get(img_url)
                if img_resp.status_code != 200:
                    return GenerationResult(success=False, error_message="Failed to download generated image")
                
                image_bytes = img_resp.content

                duration = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return GenerationResult(
                    success=True,
                    file_bytes=image_bytes,
                    mime_type="image/png",
                    prompt_used=revised_prompt or prompt,
                    adapter_name=self.get_name(),
                    duration_ms=duration
                )

        except Exception as e:
            return GenerationResult(success=False, error_message=str(e))
