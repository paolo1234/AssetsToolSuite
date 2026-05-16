"""
OmniForge Backend — Configuration
Global settings loaded from environment or defaults.
"""

from pathlib import Path
from dataclasses import dataclass, field
import os


@dataclass
class Settings:
    """Application-wide settings. All ports, paths, and limits in one place."""

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 47831
    BRIDGE_PORT: int = 47832

    # Paths
    PROJECTS_DIR: Path = field(default_factory=lambda: Path.home() / "OmniForge" / "projects")
    
    # Asset versioning
    MAX_ASSET_VERSIONS: int = 10

    # Quality Gate
    QUALITY_GATE_THRESHOLD: int = 70

    # AI API Keys (loaded from environment)
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    COMFYUI_URL: str = field(default_factory=lambda: os.getenv("COMFYUI_URL", "http://localhost:8188"))
    ELEVENLABS_API_KEY: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    REPLICATE_API_KEY: str = field(default_factory=lambda: os.getenv("REPLICATE_API_KEY", ""))
    SUNO_API_KEY: str = field(default_factory=lambda: os.getenv("SUNO_API_KEY", ""))

    # CORS
    CORS_ORIGINS: list[str] = field(default_factory=lambda: [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Fallback
        "http://localhost:47831",
    ])

    def ensure_dirs(self) -> None:
        """Create required directories if they don't exist."""
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
