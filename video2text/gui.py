"""Streamlit GUI for Video2Text."""

import streamlit as st
import requests
import time
import os
from pathlib import Path
import json
from typing import Optional, Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="Video2Text Transcription Tool",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """Check if API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def submit_url_transcription(url: str, model: str, language: Optional[str], output_format: str, force_cpu: bool) -> Optional[str]:
    """Submit URL transcription job."""
    try:
        payload = {
            "url": url,
            "model": model,
            "output_format": output_format,
            "force_cpu": force_cpu
        }
        if language:
            payload["language"] = language
            
        response = requests.post(f"{API_BASE_URL}/transcribe/url", json=payload)
        if response.status_code == 200:
            return response.json()["job_id"]
        else:
            st.error(f"Submission failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def submit_file_transcription(file_content: bytes, filename: str, model: str, language: Optional[str], output_format: str, force_cpu: bool) -> Optional[str]:
    """Submit file transcription job."""
    try:
        files = {"file": (filename, file_content)}
        data = {
            "model": model,
            "output_format": output_format,
            "force_cpu": force_cpu
        }
        if language:
            data["language"] = language
            
        response = requests.post(f"{API_BASE_URL}/transcribe/file", files=files, data=data)
        if response.status_code == 200:
            return response.json()["job_id"]
        else:
            st.error(f"Submission failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status."""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Status query failed: {str(e)}")
        return None

def download_result(job_id: str) -> Optional[bytes]:
    """Download transcription result."""
    try:
        response = requests.get(f"{API_BASE_URL}/download/{job_id}")
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None

def get_all_jobs() -> list:
    """Get all transcription jobs."""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Failed to get job list: {str(e)}")
        return []

def main():
    """Main Streamlit application."""
    st.title("🎥 Video2Text Transcription Tool")
    st.markdown("**Supports video link and local file transcription using OpenAI Whisper technology**")
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to API server. Please ensure the backend service is running (python -m video2text.api)")
        st.info("Start backend service: `uvicorn video2text.api:app --reload`")
        return
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration Options")
    
    # Model selection
    model = st.sidebar.selectbox(
        "Select Whisper Model",
        ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        index=1,
        help="Larger models have higher accuracy but longer processing time"
    )
    
    # Language selection
    language_options = {
        "Auto-detect": None,
        "Chinese": "zh",
        "English": "en",
        "Japanese": "ja",
        "Korean": "ko",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Russian": "ru",
        "Arabic": "ar"
    }
    
    selected_language = st.sidebar.selectbox(
        "Select Language",
        list(language_options.keys()),
        index=0,
        help="Select the primary language of the audio, or choose auto-detect"
    )
    language = language_options[selected_language]
    
    # Output format
    output_format = st.sidebar.selectbox(
        "Output Format",
        ["txt", "srt", "vtt", "json"],
        index=0,
        help="Select the output format for transcription results"
    )
    
    # GPU option
    force_cpu = st.sidebar.checkbox(
        "Force CPU Usage",
        value=False,
        help="Disable GPU acceleration and force CPU transcription (GPU will be auto-detected)"
    )
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔗 URL Transcription", "📁 File Transcription", "📋 Task Management"])
    
    with tab1:
        st.header("Transcribe from Video Link")
        st.markdown("Supports mainstream video websites like YouTube")
        
        url = st.text_input(
            "Video Link",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Enter video link, supports YouTube and other websites"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Start Transcription", key="url_submit"):
                if url:
                    with st.spinner("Submitting transcription task..."):
                        job_id = submit_url_transcription(url, model, language, output_format, force_cpu)
                        if job_id:
                            st.session_state.current_job_id = job_id
                            st.success(f"Task submitted! Job ID: {job_id}")
                            st.rerun()
                else:
                    st.error("Please enter a video link")
        
        with col2:
            if st.button("🔄 Refresh Status", key="url_refresh"):
                st.rerun()
    
    with tab2:
        st.header("Transcribe from Local File")
        st.markdown("Supports common audio and video formats")
        
        uploaded_file = st.file_uploader(
            "Select File",
            type=['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'mp4', 'avi', 'mkv', 'mov', 'wmv'],
            help="Supported audio formats: MP3, WAV, FLAC, AAC, OGG, M4A\nVideo formats: MP4, AVI, MKV, MOV, WMV"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📤 Upload and Transcribe", key="file_submit"):
                if uploaded_file is not None:
                    with st.spinner("Uploading file and submitting transcription task..."):
                        job_id = submit_file_transcription(
                            uploaded_file.read(),
                            uploaded_file.name,
                            model,
                            language,
                            output_format,
                            force_cpu
                        )
                        if job_id:
                            st.session_state.current_job_id = job_id
                            st.success(f"Task submitted! Job ID: {job_id}")
                            st.rerun()
                else:
                    st.error("Please select a file to transcribe")
        
        with col2:
            if st.button("🔄 Refresh Status", key="file_refresh"):
                st.rerun()
    
    with tab3:
        st.header("Task Management")
        
        # Show current job status
        if hasattr(st.session_state, 'current_job_id'):
            st.subheader("Current Task Status")
            job_status = get_job_status(st.session_state.current_job_id)
            if job_status:
                status_color = {
                    "pending": "🟡",
                    "processing": "🔵",
                    "completed": "🟢",
                    "failed": "🔴"
                }.get(job_status["status"], "⚪")
                
                st.write(f"{status_color} **Status**: {job_status['status']}")
                st.write(f"**Message**: {job_status['message']}")
                st.write(f"**Created**: {job_status['created_at']}")
                
                if job_status["status"] == "completed":
                    st.success("Transcription completed!")
                    
                    # Display result
                    if job_status.get("result"):
                        result = job_status["result"]
                        st.subheader("Transcription Result")
                        
                        # Show basic info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Language", result.get("language", "Unknown"))
                        with col2:
                            st.metric("Duration", f"{result.get('metadata', {}).get('duration', 0):.1f}s")
                        with col3:
                            st.metric("Model", result.get('metadata', {}).get('model', 'Unknown'))
                        
                        # Show transcription text
                        st.subheader("Transcription Text")
                        st.text_area("", result.get("text", ""), height=200, key="result_text")
                        
                        # Download button
                        if st.button("📥 Download Result File"):
                            content = download_result(st.session_state.current_job_id)
                            if content:
                                st.download_button(
                                    label="Click to Download",
                                    data=content,
                                    file_name=f"transcription_{st.session_state.current_job_id}.{output_format}",
                                    mime="text/plain"
                                )
                
                elif job_status["status"] == "failed":
                    st.error(f"Transcription failed: {job_status['message']}")
                
                elif job_status["status"] in ["pending", "processing"]:
                    st.info("Task is being processed, please wait...")
                    # Auto-refresh every 3 seconds for active jobs
                    time.sleep(3)
                    st.rerun()
        
        # Show all jobs
        st.subheader("All Tasks")
        all_jobs = get_all_jobs()
        
        if all_jobs:
            for job in sorted(all_jobs, key=lambda x: x["created_at"], reverse=True):
                with st.expander(f"Task {job['job_id'][:8]}... - {job['status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Status**: {job['status']}")
                        st.write(f"**Created**: {job['created_at']}")
                        if job.get('completed_at'):
                            st.write(f"**Completed**: {job['completed_at']}")
                    with col2:
                        st.write(f"**Message**: {job['message']}")
                        if job['status'] == 'completed':
                            if st.button(f"View Result", key=f"view_{job['job_id']}"):
                                st.session_state.current_job_id = job['job_id']
                                st.rerun()
        else:
            st.info("No task records available")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Video2Text Transcription Tool | Based on OpenAI Whisper | 
            <a href='http://localhost:8000/docs' target='_blank'>API Documentation</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 