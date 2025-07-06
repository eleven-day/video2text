# Video2Text Transcription Tool

🎥 **Video and audio transcription tool based on OpenAI Whisper**

Supports transcribing audio from video links and local files, providing three usage methods: command line, API service, and GUI interface.

## ✨ Features

- 🔗 **Video link transcription**: Supports mainstream video websites like YouTube
- 📁 **Local file transcription**: Supports common audio and video formats
- 🤖 **Multiple models**: Supports all Whisper model specifications (tiny to large-v3)
- 🌍 **Multi-language support**: Automatic language detection or specify specific language
- 📄 **Multiple output formats**: TXT, SRT, VTT, JSON
- ⚡ **Smart GPU acceleration**: Automatically detects and uses CUDA GPU acceleration for transcription
- 🖥️ **Three interfaces**: Command line, Web API, GUI interface
- 📦 **Batch processing**: Supports batch transcription of multiple files

## 🚀 Quick Start

### Installation

```bash
# Clone the project
git clone <repository-url>
cd video2text

# Install dependencies
pip install -e .

# Or use poetry
poetry install
```

### Basic Usage

```bash
# Transcribe YouTube video
video2text url -u "https://www.youtube.com/watch?v=xxx"

# Transcribe local file
video2text file -f "audio.mp3"

# Start Web API service
video2text serve

# Start GUI interface
video2text gui
```

## 📋 Usage Methods

### 1. Command Line Tool (CLI)

#### Transcribe video links
```bash
video2text url -u "https://youtu.be/xxx" -m base -f srt -o result.srt
```

#### Transcribe local files
```bash
video2text file -f "video.mp4" -m small -o transcription.txt

# Force CPU usage (disable GPU acceleration)
video2text file -f "video.mp4" -m small --force-cpu -o transcription.txt
```

#### Batch transcription
```bash
# Create file containing URLs urls.txt
echo "https://youtu.be/xxx" > urls.txt
echo "https://youtu.be/yyy" >> urls.txt

# Batch transcription
video2text batch -i urls.txt -d ./outputs -m base
```

#### Other commands
```bash
# View configuration
video2text config

# Download model
video2text download -m base

# Download all models
video2text download --all
```

### 2. Web API Service

#### Start service
```bash
video2text serve --host 0.0.0.0 --port 8000
```

#### API Endpoints

- `GET /` - Web interface
- `POST /transcribe/url` - Transcribe video link
- `POST /transcribe/file` - Transcribe uploaded file
- `GET /jobs/{job_id}` - Query task status
- `GET /download/{job_id}` - Download transcription result
- `GET /docs` - API documentation

#### Usage Example

```python
import requests

# Transcribe URL
response = requests.post("http://localhost:8000/transcribe/url", json={
    "url": "https://youtu.be/xxx",
    "model": "base",
    "output_format": "txt",
    "force_cpu": False  # Optional: force CPU usage
})
job_id = response.json()["job_id"]

# Query status
status = requests.get(f"http://localhost:8000/jobs/{job_id}")
print(status.json())
```

### 3. GUI Interface

```bash
# Start GUI
video2text gui
```

GUI interface provides:
- 🔗 URL transcription functionality
- 📁 File upload transcription
- 📋 Task management
- ⚙️ Configuration options (including automatic GPU detection)
- 📊 Real-time status updates

## ⚙️ Configuration Options

### Whisper Models
- `tiny`: Fastest, lower accuracy
- `base`: Balance speed and accuracy
- `small`: Good accuracy
- `medium`: High accuracy
- `large`: Highest accuracy
- `large-v2`: Improved large model
- `large-v3`: Latest large model

### Output Formats
- `txt`: Plain text
- `srt`: Subtitle file
- `vtt`: WebVTT format
- `json`: JSON format (includes detailed information)

### Language Support
Supports automatic detection or specify language:
- Chinese (zh)
- English (en)
- Japanese (ja)
- Korean (ko)
- French (fr)
- German (de)
- Spanish (es)
- Russian (ru)
- Arabic (ar)
- And 99 other languages

## 📦 Dependencies

### System Dependencies
- Python 3.8+
- FFmpeg (for audio processing)

### Python Dependencies
- openai-whisper
- yt-dlp
- ffmpeg-python
- fastapi
- streamlit
- click
- pydantic
- etc.

### Optional Dependencies
- CUDA (GPU acceleration)
- torch (GPU version)

## 🔧 Development

### Project Structure
```
video2text/
├── video2text/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── downloader.py      # Video download and audio extraction
│   ├── transcriber.py     # Whisper transcription
│   ├── api.py            # FastAPI service
│   ├── gui.py            # Streamlit GUI
│   └── cli.py            # Command line interface
├── main.py               # Main entry point
├── pyproject.toml        # Project configuration
└── README.md            # Documentation
```

### Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black video2text/

# Type checking
mypy video2text/
```

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

## 📄 License

MIT License

## 🆘 Troubleshooting

### Common Issues

1. **FFmpeg not installed**
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. **GPU acceleration not working**
   ```bash
   # Check if GPU is available
   video2text config
   
   # If shows "GPU available: No", install CUDA version of PyTorch
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Download failed**
   - Check network connection
   - Try using proxy
   - Update yt-dlp: `pip install -U yt-dlp`

4. **Out of memory**
   - Use smaller models (tiny/base)
   - Process shorter audio segments

### Getting Help

- View command help: `video2text --help`
- View API documentation: http://localhost:8000/docs
- Submit Issues: [GitHub Issues](https://github.com/your-repo/video2text/issues)

## 🎯 Roadmap

- [ ] Support more video websites
- [ ] Add translation functionality
- [ ] Support real-time transcription
- [ ] Add speech recognition confidence
- [ ] Support speaker separation
- [ ] Add web interface theme customization
- [ ] Support Docker deployment

---

**Video2Text** - Making video transcription simple and efficient! 🚀
