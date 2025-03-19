from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from typing import Optional
import uuid
import tempfile

from services.video_processor import VideoProcessor
from models.transcription_request import TranscriptionRequest, TranscriptionSettings

app = FastAPI(title="Video2Text API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Video2Text API is running"}

@app.post("/upload/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_openai_api: bool = Form(False),
    language: Optional[str] = Form("auto")
):
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create settings object
    settings = TranscriptionSettings(
        use_openai_api=use_openai_api,
        language=language
    )
    
    # Process the video in the background
    processor = VideoProcessor()
    background_tasks.add_task(
        processor.process_video,
        file_path,
        job_id,
        settings
    )
    
    return {"job_id": job_id, "message": "Video processing started"}

@app.post("/upload/url")
async def upload_url(
    background_tasks: BackgroundTasks,
    request: TranscriptionRequest
):
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Process the video in the background
    processor = VideoProcessor()
    background_tasks.add_task(
        processor.process_video_url,
        request.url,
        job_id,
        request.settings
    )
    
    return {"job_id": job_id, "message": "Video processing started"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    result_path = os.path.join(RESULTS_DIR, f"{job_id}.txt")
    error_path = os.path.join(RESULTS_DIR, f"{job_id}.error")
    
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as f:
            text = f.read()
        return {"status": "completed", "text": text}
    elif os.path.exists(error_path):
        with open(error_path, "r", encoding="utf-8") as f:
            error = f.read()
        return {"status": "error", "error": error}
    else:
        return {"status": "processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
