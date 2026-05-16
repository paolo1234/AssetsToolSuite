"""
OmniForge Backend — Config Manager
Handles persistence of global settings to a local JSON file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """
    Manages global application settings persistence.
    Saves to ~/.omniforge_config.json by default.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        if config_path is None:
            self.config_path = Path.home() / ".omniforge_config.json"
        else:
            self.config_path = config_path

    def load(self) -> Dict[str, Any]:
        """Load settings from disk."""
        if not self.config_path.exists():
            return {}
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, settings_dict: Dict[str, Any]) -> None:
        """Save settings to disk."""
        # Filter out sensitive or non-serializable fields if necessary
        # For now, we save everything passed
        self.config_path.write_text(
            json.dumps(settings_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
