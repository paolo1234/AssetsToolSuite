"""
OmniForge Backend — Configuration
Global settings loaded from environment or defaults.
"""

from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
import os


from project.config_manager import ConfigManager

@dataclass
class Settings:
    """Application-wide settings. All ports, paths, and limits in one place."""

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 47831
    BRIDGE_PORT: int = 47832

    # Paths
    PROJECTS_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("OMNIFORGE_DATA", str(Path.home() / "OmniForge"))) / "projects"
    )
    
    # Asset versioning
    MAX_ASSET_VERSIONS: int = 10

    # Quality Gate
    QUALITY_GATE_THRESHOLD: int = 70

    # AI API Keys
    OPENAI_API_KEY: str = ""
    COMFYUI_URL: str = "http://localhost:8188"
    ELEVENLABS_API_KEY: str = ""
    REPLICATE_API_KEY: str = ""
    SUNO_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:47831",
    ])

    def __post_init__(self):
        self._manager = ConfigManager()
        self.load_from_disk()

    def load_from_disk(self) -> None:
        """Load settings from disk, overriding defaults/env."""
        data = self._manager.load()
        for key, value in data.items():
            if hasattr(self, key):
                if key == "PROJECTS_DIR":
                    setattr(self, key, Path(value))
                else:
                    setattr(self, key, value)
        
        # Env vars still take precedence if set
        if os.getenv("OMNIFORGE_DATA"):
            self.PROJECTS_DIR = Path(os.environ["OMNIFORGE_DATA"]) / "projects"
        if os.getenv("OPENAI_API_KEY"):
            self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        if os.getenv("COMFYUI_URL"):
            self.COMFYUI_URL = os.environ["COMFYUI_URL"]

    def update(self, new_settings: dict[str, Any]) -> None:
        """Update settings and persist to disk."""
        for key, value in new_settings.items():
            if hasattr(self, key) and not key.startswith("_"):
                if key == "PROJECTS_DIR":
                    setattr(self, key, Path(value))
                else:
                    setattr(self, key, value)
        
        # Save to disk (only serializable fields)
        to_save = {
            k: str(v) if isinstance(v, Path) else v 
            for k, v in self.__dict__.items() 
            if not k.startswith("_") and k != "CORS_ORIGINS"
        }
        self._manager.save(to_save)

    def ensure_dirs(self) -> None:
        """Create required directories if they don't exist."""
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
