#!/usr/bin/env python3
"""Script to start Video2Text GUI"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start GUI interface"""
    print("🎨 Starting Video2Text GUI interface...")
    
    # Check if required dependencies are installed
    try:
        import streamlit
    except ImportError:
        print("❌ Missing required dependencies, please install first:")
        print("pip install streamlit")
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault('PYTHONPATH', str(Path(__file__).parent.parent))
    
    # Get GUI file path
    gui_path = Path(__file__).parent.parent / "video2text" / "gui.py"
    
    if not gui_path.exists():
        print(f"❌ GUI file does not exist: {gui_path}")
        sys.exit(1)
    
    # Start Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit",
            "run", str(gui_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        print(f"🌐 GUI address: http://localhost:8501")
        print(f"🔧 Command: {' '.join(cmd)}")
        print()
        print("💡 Tip: Make sure API server is running (http://localhost:8000)")
        print()
        
        subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        
    except KeyboardInterrupt:
        print("\n👋 GUI stopped")
    except Exception as e:
        print(f"❌ Failed to start GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 