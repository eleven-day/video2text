# Video to Text with OpenAI Whisper API

本项目演示如何从视频网站下载视频文件，提取音频，并使用 OpenAI Whisper 云端 API 将音频转录为文本。

## 目录结构

```
video-to-text/
├── .env                  # 可选，用于存储 OPENAI_API_KEY
├── README.md             # 项目说明
├── requirements.txt      # 依赖库列表
├── downloader.py         # 下载视频模块
├── audio_extractor.py    # 提取音频模块
├── stt_api.py            # 调用 OpenAI Whisper API 模块
├── file_utils.py         # 文件操作工具模块
└── main.py               # 主入口
```

## 安装依赖

1. 克隆/下载本项目。  
2. 在项目根目录下执行:
   ```
   pip install -r requirements.txt
   ```
3. 确保系统环境中已安装 ffmpeg，并可直接通过命令 ffmpeg 调用。

## 配置 OpenAI API Key

1. 在 OpenAI 平台(https://platform.openai.com/) 生成 API Key。  
2. 在项目根目录下创建 .env 文件，并写入你的 API Key，例如：  
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxx
   ```
   或者在代码中直接设置 openai.api_key = "sk-xxxxxx"。

## 运行

在命令行执行：

```
python main.py <视频链接> <输出文本文件>
```

示例：
```
python main.py https://www.youtube.com/watch?v=XXXX my_transcript.txt
```

程序会自动完成以下操作：  
1. 使用 yt-dlp 下载视频到临时目录。  
2. 使用 ffmpeg 提取音频。  
3. 调用 OpenAI Whisper API 转录音频得到文本。  
4. 将文本内容保存到 my_transcript.txt。  
5. 最后删除临时目录及下载的文件。

## 注意事项

- ffmpeg 使用请参考 https://ffmpeg.org 下载并安装。  
- OpenAI Whisper API 目前是付费 API，请确保你的账户余额充足。  
- 如果需要识别其他语言，请在 `stt_api.py` 中配置对应的参数(详见 OpenAI Whisper API 文档)。  