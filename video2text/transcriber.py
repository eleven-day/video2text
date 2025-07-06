"""Audio transcription using OpenAI Whisper."""

import os
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import whisper
from .config import TranscriptionConfig, OutputFormat, get_config


logger = logging.getLogger(__name__)


class TranscriptionResult:
    """Container for transcription results."""
    
    def __init__(self, text: str, segments: List[Dict], language: str, metadata: Dict[str, Any]):
        self.text = text
        self.segments = segments
        self.language = language
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'segments': self.segments,
            'language': self.language,
            'metadata': self.metadata
        }
    
    def to_srt(self) -> str:
        """Convert to SRT subtitle format."""
        srt_content = []
        for i, segment in enumerate(self.segments, 1):
            start_time = self._format_time(segment['start'])
            end_time = self._format_time(segment['end'])
            text = segment['text'].strip()
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # Empty line between subtitles
        
        return "\n".join(srt_content)
    
    def to_vtt(self) -> str:
        """Convert to WebVTT format."""
        vtt_content = ["WEBVTT", ""]
        
        for segment in self.segments:
            start_time = self._format_time_vtt(segment['start'])
            end_time = self._format_time_vtt(segment['end'])
            text = segment['text'].strip()
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text)
            vtt_content.append("")
        
        return "\n".join(vtt_content)
    
    def _format_time(self, seconds: float) -> str:
        """Format time for SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time for VTT format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"


class WhisperTranscriber:
    """Whisper-based audio transcriber."""
    
    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or get_config().transcription
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.config.model}")
            
            # Auto-detect GPU availability
            use_gpu = self.config.is_gpu_available()
            device = "cuda" if use_gpu else "cpu"
            
            if use_gpu:
                logger.info("GPU detected and will be used for acceleration")
            else:
                if self.config.force_cpu:
                    logger.info("GPU usage disabled by configuration")
                else:
                    logger.info("GPU not available, using CPU")
            
            self.model = whisper.load_model(self.config.model.value, device=device)
            logger.info(f"Successfully loaded model on {device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe audio file."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if self.model is None:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"Starting transcription of: {audio_path}")
            
            # Prepare transcription options
            options = {
                'language': self.config.language,
                'temperature': self.config.temperature,
                'beam_size': self.config.beam_size,
                'best_of': self.config.best_of,
                'patience': self.config.patience,
            }
            
            # Remove None values
            options = {k: v for k, v in options.items() if v is not None}
            
            # Transcribe
            result = self.model.transcribe(audio_path, **options)
            
            # Extract metadata
            metadata = {
                'model': self.config.model.value,
                'language': result.get('language'),
                'duration': result.get('duration', 0),
                'audio_file': audio_path,
                'options': options
            }
            
            transcription_result = TranscriptionResult(
                text=result['text'],
                segments=result['segments'],
                language=result['language'],
                metadata=metadata
            )
            
            logger.info(f"Transcription completed. Language: {result['language']}, Duration: {metadata['duration']:.2f}s")
            return transcription_result
            
        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {str(e)}")
            raise
    
    def transcribe_batch(self, audio_files: List[str]) -> List[TranscriptionResult]:
        """Transcribe multiple audio files."""
        results = []
        for audio_file in audio_files:
            try:
                result = self.transcribe(audio_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file}: {str(e)}")
                # Continue with other files
                continue
        return results


class OutputWriter:
    """Write transcription results to various formats."""
    
    @staticmethod
    def write_result(result: TranscriptionResult, output_path: str, format: OutputFormat) -> str:
        """Write transcription result to file."""
        output_file = Path(output_path)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add appropriate extension if not present
        if not output_file.suffix:
            output_file = output_file.with_suffix(f".{format.value}")
        
        try:
            if format == OutputFormat.TXT:
                content = result.text
            elif format == OutputFormat.SRT:
                content = result.to_srt()
            elif format == OutputFormat.VTT:
                content = result.to_vtt()
            elif format == OutputFormat.JSON:
                content = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported output format: {format}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully wrote {format.value} output to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to write output to {output_file}: {str(e)}")
            raise
    
    @staticmethod
    def write_multiple_formats(result: TranscriptionResult, base_path: str, formats: List[OutputFormat]) -> List[str]:
        """Write transcription result to multiple formats."""
        output_files = []
        base_file = Path(base_path)
        
        for format in formats:
            output_path = base_file.with_suffix(f".{format.value}")
            output_file = OutputWriter.write_result(result, str(output_path), format)
            output_files.append(output_file)
        
        return output_files


def transcribe_audio(audio_path: str, output_path: Optional[str] = None, 
                    config: Optional[TranscriptionConfig] = None) -> TranscriptionResult:
    """Convenience function to transcribe audio file."""
    transcriber = WhisperTranscriber(config)
    result = transcriber.transcribe(audio_path)
    
    if output_path:
        format = config.output_format if config else OutputFormat.TXT
        OutputWriter.write_result(result, output_path, format)
    
    return result


def transcribe_from_url(url: str, output_path: Optional[str] = None,
                       config: Optional[TranscriptionConfig] = None) -> TranscriptionResult:
    """Transcribe audio from video URL."""
    from .downloader import download_and_extract_audio
    
    # Download and extract audio
    audio_path = download_and_extract_audio(url)
    
    try:
        # Transcribe
        result = transcribe_audio(audio_path, output_path, config)
        return result
    finally:
        # Clean up audio file
        try:
            os.remove(audio_path)
            logger.info(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up audio file {audio_path}: {str(e)}") 