"""Command-line interface for Video2Text."""

import click
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List

from .config import (
    WhisperModel, OutputFormat, TranscriptionConfig, 
    DownloadConfig, get_config, update_config
)
from .transcriber import transcribe_audio, transcribe_from_url, OutputWriter
from .downloader import process_local_file, download_and_extract_audio


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('video2text.log')
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.version_option(version='0.1.0')
def cli(verbose: bool):
    """Video2Text - Video and audio transcription tool using OpenAI Whisper."""
    setup_logging(verbose)


@cli.command()
@click.option('--url', '-u', required=True, help='Video URL to transcribe')
@click.option('--model', '-m', 
              type=click.Choice([m.value for m in WhisperModel]), 
              default=WhisperModel.BASE.value,
              help='Whisper model to use')
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', 'output_format',
              type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.TXT.value,
              help='Output format')
@click.option('--force-cpu', is_flag=True, help='Force CPU usage (disable GPU acceleration)')
@click.option('--temperature', type=float, default=0.0, help='Temperature for sampling')
@click.option('--beam-size', type=int, default=5, help='Beam size for beam search')
@click.option('--best-of', type=int, default=5, help='Number of candidates to consider')
@click.option('--patience', type=float, default=1.0, help='Patience for beam search')
def url(url: str, model: str, language: Optional[str], output: Optional[str], 
        output_format: str, force_cpu: bool, temperature: float, beam_size: int, 
        best_of: int, patience: float):
    """Transcribe audio from video URL."""
    try:
        click.echo(f"🎥 Starting transcription from URL: {url}")
        
        # Create transcription config
        config = TranscriptionConfig(
            model=WhisperModel(model),
            language=language,
            output_format=OutputFormat(output_format),
            force_cpu=force_cpu,
            temperature=temperature,
            beam_size=beam_size,
            best_of=best_of,
            patience=patience
        )
        
        # Show GPU status
        if config.is_gpu_available():
            click.echo("🚀 GPU available, will use GPU acceleration")
        else:
            if force_cpu:
                click.echo("💻 Forced CPU mode")
            else:
                click.echo("💻 GPU not available, using CPU mode")
        
        # Transcribe
        with click.progressbar(length=100, label='Transcribing...') as bar:
            result = transcribe_from_url(url, output, config)
            bar.update(100)
        
        # Generate output filename if not specified
        if not output:
            output = f"transcription_{result.metadata.get('model', 'unknown')}.{output_format}"
        
        # Write result
        output_path = OutputWriter.write_result(result, output, config.output_format)
        
        click.echo(f"✅ Transcription completed!")
        click.echo(f"📄 Output file: {output_path}")
        click.echo(f"🌐 Language: {result.language}")
        click.echo(f"⏱️ Duration: {result.metadata.get('duration', 0):.1f}s")
        
    except Exception as e:
        click.echo(f"❌ Transcription failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, 
              type=click.Path(exists=True), help='Audio/video file to transcribe')
@click.option('--model', '-m', 
              type=click.Choice([m.value for m in WhisperModel]), 
              default=WhisperModel.BASE.value,
              help='Whisper model to use')
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'output_format',
              type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.TXT.value,
              help='Output format')
@click.option('--force-cpu', is_flag=True, help='Force CPU usage (disable GPU acceleration)')
@click.option('--temperature', type=float, default=0.0, help='Temperature for sampling')
@click.option('--beam-size', type=int, default=5, help='Beam size for beam search')
@click.option('--best-of', type=int, default=5, help='Number of candidates to consider')
@click.option('--patience', type=float, default=1.0, help='Patience for beam search')
def file(file_path: str, model: str, language: Optional[str], output: Optional[str], 
         output_format: str, force_cpu: bool, temperature: float, beam_size: int, 
         best_of: int, patience: float):
    """Transcribe local audio/video file."""
    try:
        click.echo(f"📁 Starting transcription of file: {file_path}")
        
        # Create transcription config
        config = TranscriptionConfig(
            model=WhisperModel(model),
            language=language,
            output_format=OutputFormat(output_format),
            force_cpu=force_cpu,
            temperature=temperature,
            beam_size=beam_size,
            best_of=best_of,
            patience=patience
        )
        
        # Show GPU status
        if config.is_gpu_available():
            click.echo("🚀 GPU available, will use GPU acceleration")
        else:
            if force_cpu:
                click.echo("💻 Forced CPU mode")
            else:
                click.echo("💻 GPU not available, using CPU mode")
        
        # Process file (extract audio if needed)
        click.echo("🔧 Processing file...")
        audio_path = process_local_file(file_path)
        
        # Transcribe
        with click.progressbar(length=100, label='Transcribing...') as bar:
            result = transcribe_audio(audio_path, None, config)
            bar.update(100)
        
        # Generate output filename if not specified
        if not output:
            input_file = Path(file_path)
            output = f"{input_file.stem}_transcription.{output_format}"
        
        # Write result
        output_path = OutputWriter.write_result(result, output, config.output_format)
        
        # Clean up temporary audio file if it's different from input
        if audio_path != file_path:
            try:
                os.remove(audio_path)
                click.echo(f"🧹 Cleaned up temporary file: {audio_path}")
            except Exception as e:
                click.echo(f"⚠️ Failed to clean up temporary file: {str(e)}", err=True)
        
        click.echo(f"✅ Transcription completed!")
        click.echo(f"📄 Output file: {output_path}")
        click.echo(f"🌐 Language: {result.language}")
        click.echo(f"⏱️ Duration: {result.metadata.get('duration', 0):.1f}s")
        
    except Exception as e:
        click.echo(f"❌ Transcription failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', 'input_file', required=True, 
              type=click.Path(exists=True), help='File containing URLs (one per line)')
@click.option('--output-dir', '-d', default='./outputs', 
              help='Output directory for transcriptions')
@click.option('--model', '-m', 
              type=click.Choice([m.value for m in WhisperModel]), 
              default=WhisperModel.BASE.value,
              help='Whisper model to use')
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--format', 'output_format',
              type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.TXT.value,
              help='Output format')
@click.option('--force-cpu', is_flag=True, help='Force CPU usage (disable GPU acceleration)')
@click.option('--concurrent', '-c', type=int, default=1, 
              help='Number of concurrent transcriptions')
def batch(input_file: str, output_dir: str, model: str, language: Optional[str], 
          output_format: str, force_cpu: bool, concurrent: int):
    """Batch transcribe multiple URLs from file."""
    try:
        # Read URLs from file
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            click.echo("❌ No valid URLs found", err=True)
            sys.exit(1)
        
        click.echo(f"📋 Found {len(urls)} URLs to process")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create transcription config
        config = TranscriptionConfig(
            model=WhisperModel(model),
            language=language,
            output_format=OutputFormat(output_format),
            force_cpu=force_cpu
        )
        
        # Show GPU status
        if config.is_gpu_available():
            click.echo("🚀 GPU available, will use GPU acceleration")
        else:
            if force_cpu:
                click.echo("💻 Forced CPU mode")
            else:
                click.echo("💻 GPU not available, using CPU mode")
        
        # Process URLs
        successful = 0
        failed = 0
        
        with click.progressbar(urls, label='Batch transcribing...') as urls_bar:
            for i, url in enumerate(urls_bar):
                try:
                    click.echo(f"\n🎥 Processing {i+1}/{len(urls)}: {url}")
                    
                    # Generate output filename
                    output_file = os.path.join(output_dir, f"transcription_{i+1:03d}.{output_format}")
                    
                    # Transcribe
                    result = transcribe_from_url(url, output_file, config)
                    
                    click.echo(f"✅ Completed: {output_file}")
                    successful += 1
                    
                except Exception as e:
                    click.echo(f"❌ Failed: {str(e)}", err=True)
                    failed += 1
                    continue
        
        click.echo(f"\n📊 Batch transcription completed!")
        click.echo(f"✅ Successful: {successful}")
        click.echo(f"❌ Failed: {failed}")
        click.echo(f"📁 Output directory: {output_dir}")
        
    except Exception as e:
        click.echo(f"❌ Batch transcription failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration."""
    try:
        app_config = get_config()
        
        # Check GPU availability
        temp_config = TranscriptionConfig()
        gpu_available = temp_config.is_gpu_available()
        
        click.echo("⚙️ Current configuration:")
        click.echo(f"  Transcription model: {app_config.transcription.model.value}")
        click.echo(f"  Output format: {app_config.transcription.output_format.value}")
        click.echo(f"  Force CPU: {app_config.transcription.force_cpu}")
        click.echo(f"  GPU available: {'Yes' if gpu_available else 'No'}")
        click.echo(f"  Language: {app_config.transcription.language or 'Auto-detect'}")
        click.echo(f"  Download directory: {app_config.download.output_dir}")
        click.echo(f"  Temporary directory: {app_config.temp_dir}")
        click.echo(f"  Log level: {app_config.log_level}")
        click.echo(f"  Max worker threads: {app_config.max_workers}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get configuration: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host: str, port: int, reload: bool):
    """Start the FastAPI server."""
    try:
        import uvicorn
        from .api import app
        
        click.echo(f"🚀 Starting API server...")
        click.echo(f"🌐 Address: http://{host}:{port}")
        click.echo(f"📚 API documentation: http://{host}:{port}/docs")
        
        uvicorn.run(app, host=host, port=port, reload=reload)
        
    except ImportError:
        click.echo("❌ Cannot import uvicorn, please install: pip install uvicorn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start server: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='localhost', help='API server host')
@click.option('--port', default=8000, type=int, help='API server port')
def gui(host: str, port: int):
    """Launch the Streamlit GUI."""
    try:
        import streamlit.web.cli as stcli
        import sys
        from pathlib import Path
        
        # Get the path to the GUI module
        gui_path = Path(__file__).parent / 'gui.py'
        
        click.echo(f"🎨 Starting GUI interface...")
        click.echo(f"🌐 Will open in browser: http://localhost:8501")
        click.echo(f"📡 API server: http://{host}:{port}")
        
        # Set environment variable for API URL
        os.environ['API_BASE_URL'] = f"http://{host}:{port}"
        
        # Launch Streamlit
        sys.argv = ["streamlit", "run", str(gui_path)]
        stcli.main()
        
    except ImportError:
        click.echo("❌ Cannot import streamlit, please install: pip install streamlit", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start GUI: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--model', '-m', 
              type=click.Choice([m.value for m in WhisperModel]), 
              help='Download specific Whisper model')
@click.option('--all', 'download_all', is_flag=True, help='Download all models')
def download(model: Optional[str], download_all: bool):
    """Download Whisper models."""
    try:
        import whisper
        
        if download_all:
            models = [m.value for m in WhisperModel]
            click.echo(f"📥 Downloading all models: {', '.join(models)}")
        elif model:
            models = [model]
            click.echo(f"📥 Downloading model: {model}")
        else:
            click.echo("❌ Please specify a model to download or use --all to download all models", err=True)
            sys.exit(1)
        
        for model_name in models:
            try:
                click.echo(f"⬇️ Downloading model: {model_name}")
                whisper.load_model(model_name)
                click.echo(f"✅ Model {model_name} downloaded successfully")
            except Exception as e:
                click.echo(f"❌ Failed to download model {model_name}: {str(e)}", err=True)
        
        click.echo("🎉 Model download completed!")
        
    except ImportError:
        click.echo("❌ Cannot import whisper, please install: pip install openai-whisper", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to download models: {str(e)}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 User interrupted, exiting program")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Program exception: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 