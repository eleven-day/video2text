"""Video and audio download functionality."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import yt_dlp
import ffmpeg
from .config import DownloadConfig, get_config


logger = logging.getLogger(__name__)


class VideoDownloader:
    """Video downloader using yt-dlp."""
    
    def __init__(self, config: Optional[DownloadConfig] = None):
        self.config = config or get_config().download
        
    def download_video(self, url: str, output_path: Optional[str] = None) -> str:
        """Download video from URL and return the path to downloaded file."""
        if output_path is None:
            output_path = self.config.output_dir
            
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
        
        if self.config.max_filesize:
            ydl_opts['format'] += f'[filesize<{self.config.max_filesize}]'
            
        if self.config.proxy:
            ydl_opts['proxy'] = self.config.proxy
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = self._find_downloaded_file(output_path, video_title)
                logger.info(f"Successfully downloaded video: {downloaded_file}")
                return downloaded_file
                
        except Exception as e:
            logger.error(f"Failed to download video from {url}: {str(e)}")
            raise
    
    def _find_downloaded_file(self, output_path: str, title: str) -> str:
        """Find the downloaded file in the output directory."""
        # Common video extensions
        extensions = ['.mp4', '.mkv', '.avi', '.webm', '.mov']
        
        for ext in extensions:
            # Try exact match first
            file_path = os.path.join(output_path, f"{title}{ext}")
            if os.path.exists(file_path):
                return file_path
                
        # If exact match not found, search for files with similar names
        for file in os.listdir(output_path):
            if any(file.endswith(ext) for ext in extensions):
                if title.lower() in file.lower():
                    return os.path.join(output_path, file)
                    
        # If still not found, return the most recent file
        files = [f for f in os.listdir(output_path) 
                if any(f.endswith(ext) for ext in extensions)]
        if files:
            latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(output_path, f)))
            return os.path.join(output_path, latest_file)
            
        raise FileNotFoundError(f"Downloaded file not found in {output_path}")


class AudioExtractor:
    """Audio extraction from video files using ffmpeg."""
    
    def __init__(self, config: Optional[DownloadConfig] = None):
        self.config = config or get_config().download
        
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from video file."""
        if output_path is None:
            # Generate output path based on input file
            video_file = Path(video_path)
            output_path = str(video_file.parent / f"{video_file.stem}.{self.config.audio_format}")
            
        try:
            # Use ffmpeg to extract audio
            stream = ffmpeg.input(video_path)
            audio = stream.audio
            
            # Configure audio settings
            audio_opts = {
                'acodec': 'mp3' if self.config.audio_format == 'mp3' else 'pcm_s16le',
                'ar': '16000',  # Whisper prefers 16kHz
            }
            
            if self.config.audio_format == 'mp3':
                audio_opts['audio_bitrate'] = f"{self.config.audio_quality}k"
            
            out = ffmpeg.output(audio, output_path, **audio_opts)
            ffmpeg.run(out, overwrite_output=True, quiet=True)
            
            logger.info(f"Successfully extracted audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to extract audio from {video_path}: {str(e)}")
            raise
    
    def convert_audio(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Convert audio file to the desired format."""
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}.{self.config.audio_format}")
            
        try:
            stream = ffmpeg.input(input_path)
            audio = stream.audio
            
            # Configure audio settings for Whisper
            audio_opts = {
                'acodec': 'mp3' if self.config.audio_format == 'mp3' else 'pcm_s16le',
                'ar': '16000',  # Whisper prefers 16kHz
                'ac': '1',      # Mono audio
            }
            
            if self.config.audio_format == 'mp3':
                audio_opts['audio_bitrate'] = f"{self.config.audio_quality}k"
            
            out = ffmpeg.output(audio, output_path, **audio_opts)
            ffmpeg.run(out, overwrite_output=True, quiet=True)
            
            logger.info(f"Successfully converted audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to convert audio {input_path}: {str(e)}")
            raise


def download_and_extract_audio(url: str, output_dir: Optional[str] = None) -> str:
    """Download video from URL and extract audio in one step."""
    downloader = VideoDownloader()
    extractor = AudioExtractor()
    
    # Download video
    video_path = downloader.download_video(url, output_dir)
    
    # Extract audio
    audio_path = extractor.extract_audio(video_path)
    
    # Clean up video file to save space
    try:
        os.remove(video_path)
        logger.info(f"Cleaned up video file: {video_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up video file {video_path}: {str(e)}")
    
    return audio_path


def process_local_file(file_path: str, output_dir: Optional[str] = None) -> str:
    """Process local video or audio file."""
    file_obj = Path(file_path)
    
    if not file_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if it's already an audio file
    audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
    if file_obj.suffix.lower() in audio_extensions:
        # Convert to the desired format if needed
        extractor = AudioExtractor()
        return extractor.convert_audio(file_path, output_dir)
    
    # It's a video file, extract audio
    extractor = AudioExtractor()
    if output_dir:
        output_path = os.path.join(output_dir, f"{file_obj.stem}.mp3")
    else:
        output_path = None
        
    return extractor.extract_audio(file_path, output_path) 