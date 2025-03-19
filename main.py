# main.py

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 自定义模块
from video_processor import VideoProcessor
from web_app import create_app

def run_cli():
    """运行命令行界面处理单个视频"""
    if len(sys.argv) < 3:
        print("用法: python main.py <视频链接> <输出文本文件>")
        print("示例: python main.py https://www.youtube.com/watch?v=XXXX result.txt")
        sys.exit(1)

    input_video_url = sys.argv[1]
    output_txt_file = sys.argv[2]
    
    processor = VideoProcessor()
    processor.process_video_url(input_video_url, output_txt_file)

def run_web_app():
    """运行Web服务应用"""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    if len(sys.argv) > 1:
        run_cli()  # 有参数时运行CLI模式
    else:
        run_web_app()  # 无参数时启动Web服务