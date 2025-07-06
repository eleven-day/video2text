"""Main entry point for Video2Text application."""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from video2text.cli import main as cli_main


def main():
    """Main entry point with basic usage information."""
    print("🎥 Video2Text Transcription Tool")
    print("=" * 50)
    print()
    print("This is a video and audio transcription tool based on OpenAI Whisper.")
    print()
    print("📋 Usage:")
    print("1. Command line tool: video2text --help")
    print("2. API server: video2text serve")
    print("3. GUI interface: video2text gui")
    print()
    print("🚀 Quick start:")
    print("• Transcribe YouTube video: video2text url -u 'https://youtu.be/xxx'")
    print("• Transcribe local file: video2text file -f 'audio.mp3'")
    print("• Start web service: video2text serve")
    print("• Start GUI interface: video2text gui")
    print()
    print("📚 More help:")
    print("• View all commands: video2text --help")
    print("• View command details: video2text <command> --help")
    print("• API documentation: http://localhost:8000/docs (after starting service)")
    print()
    print("🔧 To use CLI directly, run: video2text --help")
    print()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("💡 Tip: Run 'video2text --help' to see all available commands")
    else:
        # Pass through to CLI
        cli_main()


if __name__ == "__main__":
    main()
