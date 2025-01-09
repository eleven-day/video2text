# audio_extractor.py

import subprocess
from pathlib import Path

def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """
    使用 ffmpeg 将视频中的音频部分提取为 WAV 文件。
    """
    audio_path = output_dir / "temp_audio.wav"
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                # 不需要视频
        "-acodec", "pcm_s16le",
        "-ar", "16000",       # 采样率16k
        "-ac", "1",           # 单声道
        str(audio_path)
    ]
    print("Extracting audio using ffmpeg ...")
    subprocess.run(cmd, check=True)
    print(f"Audio extracted: {audio_path}")
    return audio_path