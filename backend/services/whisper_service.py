import os
import openai
import logging
from typing import Optional
import tempfile

from models.transcription_request import TranscriptionSettings

# Try to load local whisper if available
try:
    import whisper
    WHISPER_LOCAL_AVAILABLE = True
except ImportError:
    WHISPER_LOCAL_AVAILABLE = False
    logging.warning("Local Whisper model not available. Install it with: pip install openai-whisper")

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

class WhisperService:
    def __init__(self):
        self.local_model = None
        if WHISPER_LOCAL_AVAILABLE:
            # Load a small model by default - can be 'tiny', 'base', 'small', 'medium', 'large'
            try:
                self.local_model = whisper.load_model("base")
                logging.info("Loaded local Whisper model")
            except Exception as e:
                logging.error(f"Failed to load local Whisper model: {str(e)}")
        
        # Set up OpenAI client if API key is available
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
        
    def transcribe_audio(self, audio_path: str, settings: TranscriptionSettings) -> str:
        """Transcribe audio file using either OpenAI API or local model."""
        if settings.use_openai_api:
            return self._transcribe_with_openai_api(audio_path, settings.language)
        else:
            return self._transcribe_with_local_model(audio_path, settings.language)
    
    def _transcribe_with_openai_api(self, audio_path: str, language: str) -> str:
        """Transcribe audio using OpenAI's Whisper API."""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        
        with open(audio_path, "rb") as audio_file:
            options = {"model": "whisper-1"}
            if language != "auto":
                options["language"] = language
            
            response = openai.audio.transcriptions.create(
                audio=audio_file,
                **options
            )
            return response["text"]
    
    def _transcribe_with_local_model(self, audio_path: str, language: str) -> str:
        """Transcribe audio using the local Whisper model."""
        if not WHISPER_LOCAL_AVAILABLE or self.local_model is None:
            raise ValueError("Local Whisper model is not available. Install it with: pip install openai-whisper")
        
        options = {}
        if language != "auto":
            options["language"] = language
        
        result = self.local_model.transcribe(audio_path, **options)
        return result["text"]
