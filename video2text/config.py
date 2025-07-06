"""Configuration management for Video2Text."""

import os
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class WhisperModel(str, Enum):
    """Whisper model sizes."""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"


class OutputFormat(str, Enum):
    """Output format options."""
    TXT = "txt"
    SRT = "srt"
    JSON = "json"
    VTT = "vtt"


class TranscriptionConfig(BaseModel):
    """Configuration for transcription process."""
    model: WhisperModel = Field(default=WhisperModel.BASE, description="Whisper model to use")
    language: Optional[str] = Field(default=None, description="Language code (auto-detect if None)")
    output_format: OutputFormat = Field(default=OutputFormat.TXT, description="Output format")
    force_cpu: bool = Field(default=False, description="Force CPU usage even if GPU is available")
    temperature: float = Field(default=0.0, description="Temperature for sampling")
    beam_size: int = Field(default=5, description="Beam size for beam search")
    best_of: int = Field(default=5, description="Number of candidates to consider")
    patience: float = Field(default=1.0, description="Patience for beam search")
    
    def is_gpu_available(self) -> bool:
        """Check if GPU is available and should be used."""
        if self.force_cpu:
            return False
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False


class DownloadConfig(BaseModel):
    """Configuration for video/audio download."""
    output_dir: str = Field(default="./downloads", description="Download directory")
    audio_format: str = Field(default="mp3", description="Audio format for extraction")
    audio_quality: str = Field(default="192", description="Audio quality in kbps")
    max_filesize: Optional[str] = Field(default=None, description="Maximum file size")
    proxy: Optional[str] = Field(default=None, description="Proxy URL")


class AppConfig(BaseModel):
    """Main application configuration."""
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    temp_dir: str = Field(default="./temp", description="Temporary files directory")
    log_level: str = Field(default="INFO", description="Logging level")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure directories exist
        os.makedirs(self.download.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def update_config(**kwargs) -> AppConfig:
    """Update the global configuration."""
    global config
    config = AppConfig(**{**config.dict(), **kwargs})
    return config 