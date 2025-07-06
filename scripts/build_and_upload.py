#!/usr/bin/env python3
"""
PyPI packaging and upload script
Used to package and upload the video2text project to PyPI
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run command and handle errors"""
    print(f"Executing command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        if e.stderr:
            print(f"Error information: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def clean_build():
    """Clean build files"""
    print("Cleaning build files...")
    
    # Clean targets
    clean_targets = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        "video2text/__pycache__",
        "video2text/*.pyc",
        "tests/__pycache__",
        "tests/*.pyc"
    ]
    
    for target in clean_targets:
        if "*" in target:
            # Use glob to match
            import glob
            for path in glob.glob(target):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Deleted directory: {path}")
                else:
                    os.remove(path)
                    print(f"Deleted file: {path}")
        else:
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                    print(f"Deleted directory: {target}")
                else:
                    os.remove(target)
                    print(f"Deleted file: {target}")


def check_requirements():
    """Check if necessary tools are installed"""
    print("Checking necessary tools...")
    
    required_tools = ["build", "twine"]
    missing_tools = []
    
    for tool in required_tools:
        result = run_command(f"python -m {tool} --version", check=False)
        if result.returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"Missing necessary tools: {missing_tools}")
        print("Please run the following command to install:")
        print("pip install build twine")
        sys.exit(1)
    
    print("All necessary tools are installed")


def build_package():
    """Build package"""
    print("Building package...")
    
    # Build source code package and wheel package
    run_command("python -m build")
    
    # Check build results
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Build failed: dist directory does not exist")
        sys.exit(1)
    
    files = list(dist_dir.glob("*"))
    if not files:
        print("Build failed: dist directory is empty")
        sys.exit(1)
    
    print("Build successful, generated files:")
    for file in files:
        print(f"  - {file.name}")


def check_package():
    """Check package integrity"""
    print("Checking package integrity...")
    
    # Use twine to check package
    run_command("python -m twine check dist/*")
    print("Package check passed")


def upload_to_testpypi():
    """Upload to TestPyPI"""
    print("Uploading to TestPyPI...")
    
    # Check if there is a TestPyPI token
    if not os.getenv("TESTPYPI_TOKEN"):
        print("Warning: TESTPYPI_TOKEN environment variable is not set")
        print("Please set TestPyPI API token or manually input username and password")
    
    run_command("python -m twine upload --repository testpypi dist/*")
    print("Upload to TestPyPI successful")


def upload_to_pypi():
    """Upload to PyPI"""
    print("Uploading to PyPI...")
    
    # Check if there is a PyPI token
    if not os.getenv("PYPI_TOKEN"):
        print("Warning: PYPI_TOKEN environment variable is not set")
        print("Please set PyPI API token or manually input username and password")
    
    # Confirm upload
    response = input("确认上传到PyPI? (y/N): ")
    if response.lower() != 'y':
        print("Upload cancelled")
        return
    
    run_command("python -m twine upload dist/*")
    print("Upload to PyPI successful")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PyPI packaging and upload tool")
    parser.add_argument("--clean", action="store_true", help="Clean build files")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--check", action="store_true", help="Check package")
    parser.add_argument("--test-upload", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--upload", action="store_true", help="Upload to PyPI")
    parser.add_argument("--all", action="store_true", help="Execute full process (clean+build+check+TestPyPI)")
    parser.add_argument("--production", action="store_true", help="Production release (clean+build+check+PyPI)")
    
    args = parser.parse_args()
    
    # Switch to project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    print(f"Current working directory: {os.getcwd()}")
    
    # Check necessary tools
    check_requirements()
    
    if args.all:
        # Full process
        clean_build()
        build_package()
        check_package()
        upload_to_testpypi()
    elif args.production:
        # Production release
        clean_build()
        build_package()
        check_package()
        upload_to_pypi()
    else:
        # Single operation
        if args.clean:
            clean_build()
        if args.build:
            build_package()
        if args.check:
            check_package()
        if args.test_upload:
            upload_to_testpypi()
        if args.upload:
            upload_to_pypi()
        
        # If no operation is specified, display help
        if not any([args.clean, args.build, args.check, args.test_upload, args.upload]):
            parser.print_help()


if __name__ == "__main__":
    main() 