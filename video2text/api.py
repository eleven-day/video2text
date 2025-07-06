"""FastAPI backend service for Video2Text."""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import aiofiles
import uuid
from datetime import datetime

from .config import (
    WhisperModel, OutputFormat, TranscriptionConfig, 
    DownloadConfig, get_config, update_config
)
from .transcriber import transcribe_audio, transcribe_from_url, TranscriptionResult
from .downloader import process_local_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Video2Text API",
    description="Video and audio transcription service using OpenAI Whisper",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for transcription jobs
transcription_jobs: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class TranscriptionRequest(BaseModel):
    """Request model for URL transcription."""
    url: HttpUrl
    model: WhisperModel = WhisperModel.BASE
    language: Optional[str] = None
    output_format: OutputFormat = OutputFormat.TXT
    force_cpu: bool = False


class TranscriptionResponse(BaseModel):
    """Response model for transcription results."""
    job_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None


class JobStatus(BaseModel):
    """Job status model."""
    job_id: str
    status: str
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None


class ConfigResponse(BaseModel):
    """Configuration response model."""
    transcription: Dict[str, Any]
    download: Dict[str, Any]
    temp_dir: str
    log_level: str
    max_workers: int


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video2Text API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Video2Text Transcription Service</h1>
            <p>Supports video link and local file transcription</p>
            
            <h2>URL Transcription</h2>
            <form id="urlForm">
                <div class="form-group">
                    <label for="url">Video Link:</label>
                    <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
                </div>
                <div class="form-group">
                    <label for="model">Model:</label>
                    <select id="model" name="model">
                        <option value="tiny">tiny</option>
                        <option value="base" selected>base</option>
                        <option value="small">small</option>
                        <option value="medium">medium</option>
                        <option value="large">large</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="format">Output Format:</label>
                    <select id="format" name="format">
                        <option value="txt" selected>TXT</option>
                        <option value="srt">SRT</option>
                        <option value="vtt">VTT</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="force_cpu" name="force_cpu" value="true">
                        Force CPU Usage (Disable GPU Acceleration)
                    </label>
                </div>
                <button type="submit">Start Transcription</button>
            </form>
            
            <h2>File Upload Transcription</h2>
            <form id="fileForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Select File:</label>
                    <input type="file" id="file" name="file" accept="audio/*,video/*" required>
                </div>
                <div class="form-group">
                    <label for="fileModel">Model:</label>
                    <select id="fileModel" name="model">
                        <option value="tiny">tiny</option>
                        <option value="base" selected>base</option>
                        <option value="small">small</option>
                        <option value="medium">medium</option>
                        <option value="large">large</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="fileFormat">Output Format:</label>
                    <select id="fileFormat" name="format">
                        <option value="txt" selected>TXT</option>
                        <option value="srt">SRT</option>
                        <option value="vtt">VTT</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="fileForceCpu" name="force_cpu" value="true">
                        Force CPU Usage (Disable GPU Acceleration)
                    </label>
                </div>
                <button type="submit">Upload and Transcribe</button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
            
            <h2>API Documentation</h2>
            <p><a href="/docs" target="_blank">Swagger UI</a> | <a href="/redoc" target="_blank">ReDoc</a></p>
        </div>
        
        <script>
            // Handle URL form submission
            document.getElementById('urlForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                showResult('Processing...', 'info');
                
                try {
                    const response = await fetch('/transcribe/url', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    
                    if (response.ok) {
                        pollJobStatus(result.job_id);
                    } else {
                        showResult('Error: ' + result.detail, 'error');
                    }
                } catch (error) {
                    showResult('Request failed: ' + error.message, 'error');
                }
            });
            
            // Handle file form submission
            document.getElementById('fileForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                
                showResult('Uploading...', 'info');
                
                try {
                    const response = await fetch('/transcribe/file', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    
                    if (response.ok) {
                        pollJobStatus(result.job_id);
                    } else {
                        showResult('Error: ' + result.detail, 'error');
                    }
                } catch (error) {
                    showResult('Request failed: ' + error.message, 'error');
                }
            });
            
            // Poll job status
            async function pollJobStatus(jobId) {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/jobs/${jobId}`);
                        const job = await response.json();
                        
                        if (job.status === 'completed') {
                            clearInterval(interval);
                            showResult(`Transcription completed!<br><a href="${job.download_url}" download>Download Result</a>`, 'success');
                        } else if (job.status === 'failed') {
                            clearInterval(interval);
                            showResult('Transcription failed: ' + job.message, 'error');
                        } else {
                            showResult('Transcribing: ' + job.message, 'info');
                        }
                    } catch (error) {
                        clearInterval(interval);
                        showResult('Status query failed: ' + error.message, 'error');
                    }
                }, 2000);
            }
            
            // Show result
            function showResult(message, type) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = message;
                resultDiv.style.display = 'block';
                resultDiv.style.backgroundColor = type === 'error' ? '#f8d7da' : type === 'success' ? '#d4edda' : '#d1ecf1';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/transcribe/url", response_model=TranscriptionResponse)
async def transcribe_url(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """Transcribe audio from video URL."""
    job_id = str(uuid.uuid4())
    
    # Create transcription config
    config = TranscriptionConfig(
        model=request.model,
        language=request.language,
        output_format=request.output_format,
        force_cpu=request.force_cpu
    )
    
    # Initialize job
    transcription_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "message": "Job created",
        "created_at": datetime.now(),
        "completed_at": None,
        "result": None,
        "download_url": None
    }
    
    # Start background task
    background_tasks.add_task(process_url_transcription, job_id, str(request.url), config)
    
    return TranscriptionResponse(
        job_id=job_id,
        status="pending",
        message="Transcription job started"
    )


@app.post("/transcribe/file", response_model=TranscriptionResponse)
async def transcribe_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: WhisperModel = Form(WhisperModel.BASE),
    language: Optional[str] = Form(None),
    output_format: OutputFormat = Form(OutputFormat.TXT),
    force_cpu: bool = Form(False)
):
    """Transcribe uploaded audio/video file."""
    job_id = str(uuid.uuid4())
    
    # Create transcription config
    config = TranscriptionConfig(
        model=model,
        language=language,
        output_format=output_format,
        force_cpu=force_cpu
    )
    
    # Save uploaded file
    temp_dir = Path(get_config().temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / f"{job_id}_{file.filename}"
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize job
    transcription_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "message": "File uploaded",
        "created_at": datetime.now(),
        "completed_at": None,
        "result": None,
        "download_url": None
    }
    
    # Start background task
    background_tasks.add_task(process_file_transcription, job_id, str(file_path), config)
    
    return TranscriptionResponse(
        job_id=job_id,
        status="pending",
        message="Transcription job started"
    )


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get transcription job status."""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = transcription_jobs[job_id]
    return JobStatus(**job)


@app.get("/jobs", response_model=List[JobStatus])
async def list_jobs():
    """List all transcription jobs."""
    return [JobStatus(**job) for job in transcription_jobs.values()]


@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download transcription result."""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = transcription_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if not job["download_url"]:
        raise HTTPException(status_code=404, detail="Download file not found")
    
    file_path = job["download_url"].replace("/download/", "")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/octet-stream'
    )


@app.get("/config", response_model=ConfigResponse)
async def get_config_endpoint():
    """Get current configuration."""
    config = get_config()
    return ConfigResponse(
        transcription=config.transcription.dict(),
        download=config.download.dict(),
        temp_dir=config.temp_dir,
        log_level=config.log_level,
        max_workers=config.max_workers
    )


@app.post("/config")
async def update_config_endpoint(config_data: Dict[str, Any]):
    """Update configuration."""
    try:
        update_config(**config_data)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update config: {str(e)}")


# Background tasks
async def process_url_transcription(job_id: str, url: str, config: TranscriptionConfig):
    """Background task to process URL transcription."""
    try:
        # Update job status
        transcription_jobs[job_id]["status"] = "processing"
        transcription_jobs[job_id]["message"] = "Downloading and transcribing..."
        
        # Transcribe
        result = await asyncio.to_thread(transcribe_from_url, url, None, config)
        
        # Save result to file
        output_dir = Path(get_config().temp_dir) / "results"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{job_id}.{config.output_format.value}"
        
        from .transcriber import OutputWriter
        output_path = OutputWriter.write_result(result, str(output_file), config.output_format)
        
        # Update job status
        transcription_jobs[job_id].update({
            "status": "completed",
            "message": "Transcription completed successfully",
            "completed_at": datetime.now(),
            "result": result.to_dict(),
            "download_url": f"/download/{job_id}"
        })
        
    except Exception as e:
        logger.error(f"Transcription failed for job {job_id}: {str(e)}")
        transcription_jobs[job_id].update({
            "status": "failed",
            "message": str(e),
            "completed_at": datetime.now()
        })


async def process_file_transcription(job_id: str, file_path: str, config: TranscriptionConfig):
    """Background task to process file transcription."""
    try:
        # Update job status
        transcription_jobs[job_id]["status"] = "processing"
        transcription_jobs[job_id]["message"] = "Processing file..."
        
        # Process file (extract audio if needed)
        audio_path = await asyncio.to_thread(process_local_file, file_path)
        
        # Transcribe
        transcription_jobs[job_id]["message"] = "Transcribing audio..."
        result = await asyncio.to_thread(transcribe_audio, audio_path, None, config)
        
        # Save result to file
        output_dir = Path(get_config().temp_dir) / "results"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{job_id}.{config.output_format.value}"
        
        from .transcriber import OutputWriter
        output_path = OutputWriter.write_result(result, str(output_file), config.output_format)
        
        # Update job status
        transcription_jobs[job_id].update({
            "status": "completed",
            "message": "Transcription completed successfully",
            "completed_at": datetime.now(),
            "result": result.to_dict(),
            "download_url": f"/download/{job_id}"
        })
        
        # Clean up temporary files
        try:
            os.remove(file_path)
            if audio_path != file_path:
                os.remove(audio_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {str(e)}")
            
    except Exception as e:
        logger.error(f"Transcription failed for job {job_id}: {str(e)}")
        transcription_jobs[job_id].update({
            "status": "failed",
            "message": str(e),
            "completed_at": datetime.now()
        })


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Video2Text API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 