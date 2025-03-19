# video_processor.py

import os
import uuid
import tempfile
from pathlib import Path
import concurrent.futures
import re
from typing import List, Dict, Union, Tuple

import openai

from downloader import download_video
from audio_extractor import extract_audio
from stt_api import transcribe_audio
from file_utils import save_text_to_file, cleanup_temp_files

class VideoProcessor:
    def __init__(self):
        self.base_temp_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "temp"
        self.base_temp_dir.mkdir(exist_ok=True)
    
    def process_video_url(self, url: str, output_file: str = None) -> str:
        """处理单个视频URL并返回转录文本"""
        # 创建唯一的临时工作目录
        temp_dir = self.base_temp_dir / f"job_{uuid.uuid4().hex}"
        temp_dir.mkdir(exist_ok=True)
        
        video_file = None
        audio_file = None
        
        try:
            # 1. 下载视频
            video_file = download_video(url, temp_dir)
            
            # 2. 提取音频
            audio_file = extract_audio(video_file, temp_dir)
            
            # 3. 转录音频
            text_result = transcribe_audio(audio_file)
            
            # 4. 如果提供了输出文件路径，则保存结果
            if output_file:
                save_text_to_file(text_result, output_file)
                
            return text_result
            
        except Exception as e:
            print(f"处理视频 {url} 时出错: {e}")
            return f"错误: {str(e)}"
        finally:
            # 清理临时文件
            cleanup_temp_files(video_file, audio_file, temp_dir)
    
    def process_local_video(self, video_path: Path, output_file: str = None) -> str:
        """处理本地视频文件并返回转录文本"""
        # 创建唯一的临时工作目录
        temp_dir = self.base_temp_dir / f"job_{uuid.uuid4().hex}"
        temp_dir.mkdir(exist_ok=True)
        
        audio_file = None
        
        try:
            # 1. 提取音频
            audio_file = extract_audio(video_path, temp_dir)
            
            # 2. 转录音频
            text_result = transcribe_audio(audio_file)
            
            # 3. 如果提供了输出文件路径，则保存结果
            if output_file:
                save_text_to_file(text_result, output_file)
                
            return text_result
            
        except Exception as e:
            print(f"处理视频 {video_path} 时出错: {e}")
            return f"错误: {str(e)}"
        finally:
            # 清理临时文件
            cleanup_temp_files(audio_file, temp_dir)
    
    def process_multiple_urls(self, urls: List[str], output_dir: Path = None) -> Dict[str, str]:
        """处理多个URL并返回每个URL的转录结果"""
        results = {}
        
        # 使用线程池并行处理多个视频
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有任务
            future_to_url = {
                executor.submit(self.process_video_url, url): url for url in urls
            }
            
            # 处理完成的任务结果
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    text = future.result()
                    results[url] = text
                    
                    # 如果提供了输出目录，则为每个视频创建单独的输出文件
                    if output_dir:
                        # 从URL生成安全的文件名
                        filename = re.sub(r'[^\w]', '_', url)[-40:] + ".txt"
                        output_file = output_dir / filename
                        save_text_to_file(text, str(output_file))
                        
                except Exception as e:
                    results[url] = f"错误: {str(e)}"
        
        return results
    
    def process_url_file(self, file_path: Path, output_dir: Path = None) -> Dict[str, str]:
        """处理包含多个URL的文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            return self.process_multiple_urls(urls, output_dir)
            
        except Exception as e:
            return {"error": f"处理URL文件时出错: {str(e)}"}
