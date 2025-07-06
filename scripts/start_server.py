#!/usr/bin/env python3
"""Script to start Video2Text API server"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start API server"""
    print("🚀 Starting Video2Text API server...")
    
    # Check if required dependencies are installed
    try:
        import uvicorn
        import fastapi
    except ImportError:
        print("❌ Missing required dependencies, please install first:")
        print("pip install fastapi uvicorn")
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault('PYTHONPATH', str(Path(__file__).parent.parent))
    
    # Start server
    try:
        # Start directly with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "video2text.api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"🌐 Server address: http://localhost:8000")
        print(f"📚 API documentation: http://localhost:8000/docs")
        print(f"🔧 Command: {' '.join(cmd)}")
        print()
        
        subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 