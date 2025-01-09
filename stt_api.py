# stt_api.py

import openai
from pathlib import Path

def transcribe_audio(audio_path: Path) -> str:
    """
    使用 OpenAI Whisper API 对音频文件进行转录，返回文本结果。
    """
    # 在 main.py 或其他地方已设置 openai.api_key，这里直接调用即可
    print("Transcribing audio with OpenAI Whisper API...")
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )

    # 注意：OpenAI Whisper API 返回的数据结构中，text 字段即为识别后的完整文本
    return response.get("text", "")