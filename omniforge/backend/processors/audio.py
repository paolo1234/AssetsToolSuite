"""
OmniForge Backend — Audio Processor
Handles trimming, normalization, and format conversion (WAV, OGG, MP3).
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Optional

from pydub import AudioSegment


class AudioProcessor:
    """
    Logic for audio manipulation using pydub.
    """

    @staticmethod
    def load_audio(file_bytes: bytes, format: str = "wav") -> AudioSegment:
        """Load bytes into an AudioSegment."""
        return AudioSegment.from_file(io.BytesIO(file_bytes), format=format)

    @staticmethod
    def export_audio(audio: AudioSegment, format: str = "wav") -> bytes:
        """Export AudioSegment to bytes."""
        out_io = io.BytesIO()
        audio.export(out_io, format=format)
        return out_io.getvalue()

    @staticmethod
    def trim(audio: AudioSegment, start_ms: int, end_ms: int) -> AudioSegment:
        """Trim audio between start and end milliseconds."""
        return audio[start_ms:end_ms]

    @staticmethod
    def normalize(audio: AudioSegment, target_dbfs: float = -3.0) -> AudioSegment:
        """Normalize audio to a target dBFS level."""
        change_in_dbfs = target_dbfs - audio.max_dbfs
        return audio.apply_gain(change_in_dbfs)

    @staticmethod
    def apply_pipeline(file_bytes: bytes, pipeline: list[dict[str, Any]], input_format: str = "wav") -> bytes:
        """Apply a sequence of audio processing steps."""
        audio = AudioProcessor.load_audio(file_bytes, format=input_format)
        
        for step in pipeline:
            op = step.get("op")
            params = step.get("params", {})
            
            if op == "trim":
                audio = AudioProcessor.trim(
                    audio, 
                    params.get("start_ms", 0), 
                    params.get("end_ms", len(audio))
                )
            elif op == "normalize":
                audio = AudioProcessor.normalize(
                    audio, 
                    params.get("target_dbfs", -3.0)
                )
            elif op == "gain":
                audio = audio.apply_gain(params.get("db", 0))
        
        # Default output format is same as input unless specified
        output_format = pipeline[-1].get("output_format", input_format) if pipeline else input_format
        return AudioProcessor.export_audio(audio, format=output_format)
