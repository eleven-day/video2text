#!/usr/bin/env python3
"""
Version management script
Used to automatically update the version number in pyproject.toml
"""

import re
import sys
import argparse
from pathlib import Path


def read_version():
    """Read the current version number"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml file does not exist")
        sys.exit(1)
    
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("Error: Could not find version number")
        sys.exit(1)
    
    return match.group(1)


def write_version(new_version):
    """Write the new version number"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    # Replace version number
    new_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"Version updated to: {new_version}")


def parse_version(version_str):
    """Parse version number"""
    # Support semantic versioning: major.minor.patch
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+))?$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    
    major, minor, patch, pre = match.groups()
    return int(major), int(minor), int(patch), pre


def format_version(major, minor, patch, pre=None):
    """Format version number"""
    version = f"{major}.{minor}.{patch}"
    if pre:
        version += f"-{pre}"
    return version


def bump_version(current_version, bump_type):
    """Increase version number"""
    try:
        major, minor, patch, pre = parse_version(current_version)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
        pre = None
    elif bump_type == "minor":
        minor += 1
        patch = 0
        pre = None
    elif bump_type == "patch":
        patch += 1
        pre = None
    else:
        print(f"Error: Unsupported version type: {bump_type}")
        sys.exit(1)
    
    return format_version(major, minor, patch, pre)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Version management tool")
    parser.add_argument("--show", action="store_true", help="Show current version")
    parser.add_argument("--set", metavar="VERSION", help="Set specific version")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], 
                       help="Increase version number (major/minor/patch)")
    
    args = parser.parse_args()
    
    # Switch to project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    import os
    os.chdir(project_dir)
    
    current_version = read_version()
    
    if args.show:
        print(f"Current version: {current_version}")
    elif args.set:
        # Verify version format
        try:
            parse_version(args.set)
            write_version(args.set)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.bump:
        new_version = bump_version(current_version, args.bump)
        print(f"Version updated from {current_version} to {new_version}")
        write_version(new_version)
    else:
        # Show current version and help
        print(f"Current version: {current_version}")
        print()
        parser.print_help()


if __name__ == "__main__":
    main() 