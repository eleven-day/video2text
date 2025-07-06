#!/usr/bin/env python3
"""Video2Text Quick Installation Script"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description=""):
    """Run command and handle errors"""
    print(f"🔧 {description}")
    print(f"   Executing: {' '.join(cmd)}")
    
    try:
        # Handle encoding issues on Windows
        encoding = 'utf-8' if platform.system() != 'Windows' else 'gbk'
        
        # Try UTF-8 first, fallback to system encoding
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of failing
            )
        except UnicodeDecodeError:
            # Fallback to system encoding
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding=encoding,
                errors='replace'
            )
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        
        # Handle stderr encoding safely
        if e.stderr:
            try:
                stderr_text = e.stderr.strip() if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='replace').strip()
                print(f"   Error message: {stderr_text}")
            except:
                print(f"   Error message: [Unable to decode error message]")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python version too low, requires Python 3.8 or higher")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version check passed: {version.major}.{version.minor}.{version.micro}")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        encoding = 'utf-8' if platform.system() != 'Windows' else 'gbk'
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True, 
            check=True,
            encoding=encoding,
            errors='replace'
        )
        print("✅ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ FFmpeg not installed")
        return False
    except Exception:
        print("⚠️ FFmpeg check failed")
        return False


def install_ffmpeg():
    """Install FFmpeg"""
    system = platform.system().lower()
    
    if system == "windows":
        print("📋 Windows FFmpeg installation instructions:")
        print("   1. Visit https://ffmpeg.org/download.html")
        print("   2. Download Windows version")
        print("   3. Extract to any directory")
        print("   4. Add ffmpeg.exe directory to system PATH")
        print("   5. Re-run this installation script")
        return False
    
    elif system == "darwin":  # macOS
        print("🍎 Trying to install FFmpeg using Homebrew...")
        if run_command(["brew", "install", "ffmpeg"], "Installing FFmpeg"):
            return True
        else:
            print("📋 macOS FFmpeg installation instructions:")
            print("   1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("   2. Run: brew install ffmpeg")
            return False
    
    elif system == "linux":
        print("🐧 Trying to install FFmpeg...")
        # Try different package managers
        for cmd in [["apt", "install", "-y", "ffmpeg"], 
                   ["yum", "install", "-y", "ffmpeg"],
                   ["dnf", "install", "-y", "ffmpeg"],
                   ["pacman", "-S", "--noconfirm", "ffmpeg"]]:
            if run_command(["sudo"] + cmd, f"Installing FFmpeg using {cmd[0]}"):
                return True
        
        print("📋 Linux FFmpeg installation instructions:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   CentOS/RHEL: sudo yum install ffmpeg")
        print("   Fedora: sudo dnf install ffmpeg")
        print("   Arch: sudo pacman -S ffmpeg")
        return False
    
    return False


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      "Upgrading pip"):
        print("⚠️ pip upgrade failed, continuing...")
    
    # Install project dependencies
    if run_command([sys.executable, "-m", "pip", "install", "-e", "."], 
                  "Installing Video2Text and its dependencies"):
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Dependencies installation failed")
        return False


def download_models():
    """Download Whisper models"""
    print("📥 Downloading Whisper models...")
    
    # Download base model
    try:
        import whisper
        print("🔄 Downloading base model...")
        whisper.load_model("base")
        print("✅ Base model download completed")
        
        # Ask if user wants to download more models
        response = input("Do you want to download other models? (tiny/small/medium/large) [Enter to skip]: ").strip()
        if response:
            models = response.split()
            for model in models:
                if model in ["tiny", "small", "medium", "large", "large-v2", "large-v3"]:
                    print(f"🔄 Downloading {model} model...")
                    whisper.load_model(model)
                    print(f"✅ {model} model download completed")
                else:
                    print(f"⚠️ Unknown model: {model}")
        
        return True
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        return False


def main():
    """Main installation process"""
    print("🎥 Video2Text Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("🔧 Installing FFmpeg...")
        if not install_ffmpeg():
            print("⚠️ FFmpeg installation failed, please install manually and re-run")
            print("   Video2Text requires FFmpeg to process audio/video files")
            response = input("Continue installing Python dependencies? (y/N): ").strip().lower()
            if response != 'y':
                sys.exit(1)
    
    # Install Python dependencies
    if not install_dependencies():
        print("❌ Installation failed")
        sys.exit(1)
    
    # Download models
    try:
        download_models()
    except Exception as e:
        print(f"⚠️ Model download failed: {e}")
        print("   You can download models later using 'video2text download' command")
    
    # Installation complete
    print("\n🎉 Video2Text installation completed!")
    print("\n📋 Usage:")
    print("   • View help: video2text --help")
    print("   • View configuration: video2text config")
    print("   • Transcribe URL: video2text url -u 'https://youtu.be/xxx'")
    print("   • Transcribe file: video2text file -f 'audio.mp3'")
    print("   • Force CPU: video2text file -f 'audio.mp3' --force-cpu")
    print("   • Start API: video2text serve")
    print("   • Start GUI: video2text gui")
    print("\n💡 Tip: GPU will be auto-detected, no manual configuration needed")
    print("🚀 Start using Video2Text!")


if __name__ == "__main__":
    main() 