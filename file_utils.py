# file_utils.py

import shutil
from pathlib import Path

def save_text_to_file(text: str, filename: str):
    """把文本结果保存到指定的文件中。"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Transcription saved to: {filename}")

def cleanup_temp_files(*paths):
    """删除给定的文件或目录。"""
    for path in paths:
        if path and path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)