# Video2Text Converter

<div align="center">

![Video2Text Logo](https://img.shields.io/badge/Video2Text-Converter-blue?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.1-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/github/license/yourusername/video2text?style=flat)](LICENSE)

*Convert videos to text easily - extract subtitles or transcribe audio with Whisper AI*

</div>

> An open-source tool that converts video content to text by extracting embedded subtitles or transcribing audio using Whisper AI. Perfect for making video content searchable, accessible, and easier to analyze.

## 📝 Overview

Video2Text is a powerful web application that extracts text from videos through subtitle extraction or audio transcription. The tool uses FFmpeg to process videos and OpenAI's Whisper (both API and local model options) for accurate speech-to-text conversion.

Perfect for:
- Creating searchable transcripts from video content
- Extracting dialogue from movies and TV shows
- Converting lecture videos to study notes
- Making video content accessible

<div align="center">
  <img src="screenshots/demo.gif" alt="Video2Text Demo" width="700">
</div>

## ✨ Features

- **Multiple Input Methods**
  - Upload local video files
  - Provide video URLs for remote processing

- **Smart Processing Pipeline**
  - First attempts to extract embedded subtitles (SRT)
  - Falls back to audio transcription if subtitles aren't available

- **Flexible Transcription Options**
  - OpenAI's Whisper API for cloud-based processing
  - Local Whisper model for offline/private processing
  - Support for multiple languages

- **User-Friendly Interface**
  - Clean, responsive design built with React and Material UI
  - Real-time processing status updates
  - Easy copy and download of results

- **Containerized Deployment**
  - Docker and Docker Compose support for easy deployment

## 🖼️ Screenshots

<div align="center">
  <img src="screenshots/upload-screen.png" alt="Upload Screen" width="45%">
  &nbsp;&nbsp;
  <img src="screenshots/results-screen.png" alt="Results Screen" width="45%">
</div>

## 🛠️ Technology Stack

- **Frontend**:
  - React 18
  - Material UI
  - Axios for API communication

- **Backend**:
  - FastAPI (Python)
  - FFmpeg for video processing
  - Whisper AI for speech recognition
  - OpenAI API integration

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- FFmpeg installed and available in PATH
- OpenAI API key (optional, for cloud transcription)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/video2text.git
   cd video2text
   ```

2. Set up backend environment:
   ```bash
   cd backend
   python -m venv venv
   
   # Activate the virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. Configure OpenAI API (optional):
   ```bash
   # Windows
   set OPENAI_API_KEY=your_api_key
   
   # Linux/Mac
   export OPENAI_API_KEY=your_api_key
   ```

4. For local Whisper model (optional):
   ```bash
   pip install openai-whisper
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to frontend directory and install dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Access the application at http://localhost:3000

### Docker Deployment (Alternative)

```bash
# Create .env file with your OpenAI API key
cp .env.example .env
# Edit the .env file with your actual API key

# Start the services
docker-compose up -d
```

## 📋 API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /upload/file` - Upload and process a video file
- `POST /upload/url` - Process a video from a URL
- `GET /status/{job_id}` - Check the status of a processing job

## 💡 How It Works

1. **Input Handling**: The application accepts video files or URLs.

2. **Processing Pipeline**:
   ```
   Video Input → FFmpeg Subtitle Extraction → If subtitles found → Parse & Return Text
                                           → If no subtitles → Extract Audio → Whisper Transcription
   ```

3. **Background Processing**: All heavy processing happens asynchronously, allowing users to continue using the application.

4. **Status Updates**: Clients poll for job status until completion.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [OpenAI's Whisper](https://github.com/openai/whisper) for the powerful speech recognition model
- [FFmpeg](https://ffmpeg.org/) for video processing capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the efficient backend framework
- [React](https://reactjs.org/) and [Material UI](https://mui.com/) for the frontend interface
