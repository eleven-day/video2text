# Video2Text Converter

This application converts videos to text by either extracting subtitles or transcribing the audio using Whisper.

## Features

- Upload local video files or provide video URLs
- Extract embedded subtitles (SRT) if available
- Transcribe audio using OpenAI's Whisper API or local Whisper model
- Support for multiple languages
- Simple and intuitive UI

## Prerequisites

- Python 3.8+
- Node.js 14+
- FFmpeg installed and available in PATH
- OpenAI API key (optional, for using OpenAI's Whisper API)

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. If you want to use the local Whisper model, uncomment the line in requirements.txt and run:
   ```
   pip install openai-whisper
   ```

6. Set environment variables:
   - If using OpenAI API: `set OPENAI_API_KEY=your_api_key` (Windows) or `export OPENAI_API_KEY=your_api_key` (Linux/Mac)

7. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The application will be available at http://localhost:3000

## Usage

1. Choose whether to upload a video file or provide a URL
2. Configure transcription settings:
   - Choose language or leave as "auto" for automatic detection
   - Toggle whether to use OpenAI API or local Whisper model
3. Submit and wait for processing to complete
4. View, copy, or download the transcribed text

## How It Works

1. User uploads a video or provides a URL
2. Backend extracts subtitles from the video if available
3. If no subtitles are found, audio is extracted and sent to Whisper for transcription
4. The transcribed text is returned to the frontend for display

## License

MIT
