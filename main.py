# main.py

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 自定义模块
from downloader import download_video
from audio_extractor import extract_audio
from stt_api import transcribe_audio
from file_utils import save_text_to_file, cleanup_temp_files

def main():
    # 加载 .env 中的环境变量（如 OPENAI_API_KEY 等），可选
    load_dotenv()

    if len(sys.argv) < 3:
        print("用法: python main.py <视频链接> <输出文本文件>")
        print("示例: python main.py https://www.youtube.com/watch?v=XXXX result.txt")
        sys.exit(1)

    input_video_url = sys.argv[1]
    output_txt_file = sys.argv[2]

    # 创建临时目录来存放下载后的视频和提取的音频
    temp_dir = Path(__file__).parent / "temp"
    temp_dir.mkdir(exist_ok=True)

    video_file = None
    audio_file = None

    try:
        # 设置OpenAI API Key，如果不使用 .env，也可在此处直接写 openai.api_key = "sk-xxxx"
        # import openai
        # openai.api_key = os.getenv("OPENAI_API_KEY")

        # 1. 下载视频
        video_file = download_video(input_video_url, temp_dir)

        # 2. 提取音频
        audio_file = extract_audio(video_file, temp_dir)

        # 3. 调用OpenAI Whisper API识别
        text_result = transcribe_audio(audio_file)

        # 4. 保存文本
        save_text_to_file(text_result, output_txt_file)

    except Exception as e:
        print(f"处理出错: {e}")
    finally:
        # 删除下载的临时文件
        cleanup_temp_files(video_file, audio_file, temp_dir)

if __name__ == "__main__":
    main()