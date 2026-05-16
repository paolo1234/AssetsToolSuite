"""
OmniForge Backend — AI Adapter Base
Abstract interface that every AI engine adapter must implement.
Changing provider = changing one value in the manifest. Zero rewrites.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AdapterType(str, Enum):
    """Categories of AI adapters."""
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class GenerationResult:
    """Standardized result from any AI adapter."""
    success: bool
    file_path: Optional[str] = None      # Path to the generated file on disk
    file_bytes: Optional[bytes] = None   # Raw bytes (if not saved to disk yet)
    mime_type: str = "image/png"
    seed: Optional[int] = None           # For reproducibility
    prompt_used: str = ""                # The actual prompt sent to the AI
    adapter_name: str = ""
    params_used: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    duration_ms: int = 0


class AIAdapter(ABC):
    """
    Abstract Base Class for all AI generation adapters.

    Every AI engine (ComfyUI, DALL-E, Replicate, AudioLDM, etc.)
    implements this interface. This ensures:
    - Swapping providers requires zero code changes in the pipeline
    - All adapters return the same GenerationResult format
    - Health checks are standardized
    """

    @abstractmethod
    async def generate(self, prompt: str, params: dict[str, Any]) -> GenerationResult:
        """
        Generate content (image or audio) from a prompt.

        Args:
            prompt: The user prompt (already enhanced by PromptBuilder if applicable)
            params: Adapter-specific parameters (size, steps, model, etc.)

        Returns:
            GenerationResult with the generated file or error details.
        """
        ...

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Verify that the AI backend is reachable and operational.
        Returns True if the service is healthy.
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Human-readable name of this adapter (e.g. 'ComfyUI Local')."""
        ...

    @abstractmethod
    def get_adapter_type(self) -> AdapterType:
        """Whether this adapter generates images or audio."""
        ...

    @abstractmethod
    def get_supported_params(self) -> list[str]:
        """
        List of parameter names this adapter accepts.
        Used by the frontend to show the correct controls.
        """
        ...

    def get_info(self) -> dict[str, Any]:
        """Summary dict for API responses."""
        return {
            "name": self.get_name(),
            "type": self.get_adapter_type().value,
            "supported_params": self.get_supported_params(),
        }
