import os
import subprocess
import tempfile
import requests
from typing import Optional
import re
import logging
import chardet

from models.transcription_request import TranscriptionSettings
from services.whisper_service import WhisperService
from services.subtitle_parser import SubtitleParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.whisper_service = WhisperService()
        self.subtitle_parser = SubtitleParser()
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)

    def process_video(self, video_path: str, job_id: str, settings: TranscriptionSettings):
        """Process a local video file."""
        try:
            text = self._process_video_file(video_path, settings)
            self._save_result(job_id, text)
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            self._save_error(job_id, str(e))
        finally:
            # Cleanup
            if os.path.exists(video_path):
                os.remove(video_path)

    def process_video_url(self, url: str, job_id: str, settings: TranscriptionSettings):
        """Download and process a video from a URL."""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_path = tmp_file.name
            
            # Download the video
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(tmp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Process the downloaded video
            text = self._process_video_file(tmp_path, settings)
            self._save_result(job_id, text)
        except Exception as e:
            logger.error(f"Error processing video from URL: {str(e)}")
            self._save_error(job_id, str(e))
        finally:
            # Cleanup
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _process_video_file(self, video_path: str, settings: TranscriptionSettings) -> str:
        """Process a video file to extract text."""
        # First, try to extract subtitles
        subtitle_path = self._extract_subtitles(video_path)
        
        if subtitle_path and os.path.exists(subtitle_path):
            try:
                # Parse the subtitle file
                text = self.subtitle_parser.parse_srt(subtitle_path)
                os.remove(subtitle_path)  # Clean up
                return text
            except Exception as e:
                logger.warning(f"Failed to parse subtitles: {str(e)}. Falling back to audio extraction.")
                os.remove(subtitle_path)  # Clean up
        
        # If no subtitles or parsing failed, extract audio and transcribe
        audio_path = self._extract_audio(video_path)
        try:
            text = self.whisper_service.transcribe_audio(audio_path, settings)
            return text
        finally:
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def _extract_subtitles(self, video_path: str) -> Optional[str]:
        """Extract subtitles from video if available."""
        subtitle_path = tempfile.mktemp(suffix=".srt")
        try:
            command = [
                "ffmpeg", "-i", video_path, 
                "-map", "0:s:0", subtitle_path,
                "-y"
            ]
            subprocess.run(command, check=True, capture_output=True)
            
            if os.path.exists(subtitle_path) and os.path.getsize(subtitle_path) > 0:
                return subtitle_path
        except subprocess.CalledProcessError:
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)
            logger.info("No subtitles found in the video")
            
        return None

    def _extract_audio(self, video_path: str) -> str:
        """Extract audio from video."""
        audio_path = tempfile.mktemp(suffix=".wav")
        command = [
            "ffmpeg", "-i", video_path, 
            "-q:a", "0", "-map", "a", 
            "-y", audio_path
        ]
        subprocess.run(command, check=True)
        return audio_path

    def _save_result(self, job_id: str, text: str):
        """Save transcription result to a file."""
        result_path = os.path.join(self.results_dir, f"{job_id}.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(text)

    def _save_error(self, job_id: str, error: str):
        """Save error message to a file."""
        error_path = os.path.join(self.results_dir, f"{job_id}.error")
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(error)
