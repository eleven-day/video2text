# stt_api.py

import openai
from pathlib import Path
import os

def transcribe_audio(audio_path: Path) -> str:
    """
    使用 OpenAI Whisper API 对音频文件进行转录，返回文本结果。
    """
    # 确保有API密钥
    if not openai.api_key:
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    print("Transcribing audio with OpenAI Whisper API...")
    
    try:
        # 适用于新版本的OpenAI API
        client = openai.OpenAI()
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except AttributeError:
        # 兼容旧版本的OpenAI API
        with open(audio_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return response.get("text", "")