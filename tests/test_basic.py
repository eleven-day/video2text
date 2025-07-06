"""Basic tests for Video2Text."""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from video2text.config import AppConfig, WhisperModel, OutputFormat


def test_config_initialization():
    """Test configuration initialization."""
    config = AppConfig()
    
    assert config.transcription.model == WhisperModel.BASE
    assert config.transcription.output_format == OutputFormat.TXT
    assert config.transcription.use_gpu == False
    assert config.transcription.language is None
    
    # Check if directories are created
    assert os.path.exists(config.download.output_dir)
    assert os.path.exists(config.temp_dir)


def test_whisper_model_enum():
    """Test WhisperModel enum values."""
    assert WhisperModel.TINY.value == "tiny"
    assert WhisperModel.BASE.value == "base"
    assert WhisperModel.SMALL.value == "small"
    assert WhisperModel.MEDIUM.value == "medium"
    assert WhisperModel.LARGE.value == "large"
    assert WhisperModel.LARGE_V2.value == "large-v2"
    assert WhisperModel.LARGE_V3.value == "large-v3"


def test_output_format_enum():
    """Test OutputFormat enum values."""
    assert OutputFormat.TXT.value == "txt"
    assert OutputFormat.SRT.value == "srt"
    assert OutputFormat.VTT.value == "vtt"
    assert OutputFormat.JSON.value == "json"


def test_config_update():
    """Test configuration update."""
    from video2text.config import update_config, get_config
    
    # Update config
    new_config = update_config(
        transcription={
            "model": "small",
            "use_gpu": True,
            "language": "zh"
        }
    )
    
    # Check if update worked
    current_config = get_config()
    assert current_config.transcription.model == WhisperModel.SMALL
    assert current_config.transcription.use_gpu == True
    assert current_config.transcription.language == "zh"


def test_transcription_result():
    """Test TranscriptionResult class."""
    from video2text.transcriber import TranscriptionResult
    
    # Mock data
    segments = [
        {"start": 0.0, "end": 5.0, "text": "Hello world"},
        {"start": 5.0, "end": 10.0, "text": "This is a test"}
    ]
    
    result = TranscriptionResult(
        text="Hello world This is a test",
        segments=segments,
        language="en",
        metadata={"model": "base", "duration": 10.0}
    )
    
    assert result.text == "Hello world This is a test"
    assert result.language == "en"
    assert len(result.segments) == 2
    
    # Test SRT format
    srt_content = result.to_srt()
    assert "1" in srt_content
    assert "00:00:00,000 --> 00:00:05,000" in srt_content
    assert "Hello world" in srt_content
    
    # Test VTT format
    vtt_content = result.to_vtt()
    assert "WEBVTT" in vtt_content
    assert "00:00:00.000 --> 00:00:05.000" in vtt_content
    
    # Test dict conversion
    result_dict = result.to_dict()
    assert result_dict["text"] == result.text
    assert result_dict["language"] == result.language


def test_file_extensions():
    """Test file extension handling."""
    from video2text.downloader import process_local_file
    
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        process_local_file("non_existent_file.mp3")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 