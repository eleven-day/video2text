# downloader.py

import subprocess
from pathlib import Path

def download_video(video_url: str, output_dir: Path) -> Path:
    """
    使用 yt-dlp 将远程视频下载到本地，并返回下载后的视频文件路径。
    """
    output_template = str(output_dir / "temp_video.%(ext)s")

    cmd = [
        "yt-dlp",
        "-o", output_template,
        video_url
    ]
    print("Downloading video using yt-dlp ...")
    subprocess.run(cmd, check=True)

    # 查找下载好的文件
    downloaded_file = None
    for file in output_dir.iterdir():
        if file.is_file() and file.name.startswith("temp_video."):
            downloaded_file = file
            break
    if not downloaded_file:
        raise FileNotFoundError("Video file not found after download.")

    print(f"Video downloaded: {downloaded_file}")
    return downloaded_file