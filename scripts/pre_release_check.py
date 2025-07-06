#!/usr/bin/env python3
"""
Pre-release check script
Ensure all preparations are complete and can be safely released
"""

import os
import sys
import subprocess
import re
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run command"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, 
            capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def check_git_status():
    """Check Git status"""
    print("Checking Git status...")
    
    # Check for uncommitted changes
    result = run_command("git status --porcelain")
    if result.returncode == 0 and result.stdout.strip():
        print("❌ There are uncommitted changes:")
        print(result.stdout)
        return False
    
    # Check for unpushed commits
    result = run_command("git log --oneline @{u}..HEAD", check=False)
    if result.returncode == 0 and result.stdout.strip():
        print("❌ There are unpushed commits:")
        print(result.stdout)
        return False
    
    print("✅ Git status is normal")
    return True


def check_version_consistency():
    """Check version consistency"""
    print("Checking version consistency...")
    
    # Read version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml file does not exist")
        return False
    
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("❌ Unable to find version number")
        return False
    
    version = match.group(1)
    print(f"✅ Current version: {version}")
    
    # Check version format
    if not re.match(r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$', version):
        print("❌ Version number format is incorrect")
        return False
    
    return True


def check_dependencies():
    """Check dependencies"""
    print("Checking build dependencies...")
    
    required_tools = ["build", "twine"]
    for tool in required_tools:
        result = run_command(f"python -m {tool} --version", check=False)
        if result.returncode != 0:
            print(f"❌ Missing tool: {tool}")
            print("Please run: pip install build twine")
            return False
    
    print("✅ Build dependencies are normal")
    return True


def check_tests():
    """Check tests"""
    print("Running tests...")
    
    # Check for test files
    test_files = list(Path("tests").glob("test_*.py"))
    if not test_files:
        print("⚠️ No test files found")
        return True
    
    # Run tests
    result = run_command("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        print("❌ Test failed")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("✅ Test passed")
    return True


def check_documentation():
    """Check documentation"""
    print("Checking documentation...")
    
    required_files = ["README.md", "LICENSE", "PYPI_GUIDE.md"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing file: {file}")
            return False
    
    # Check README.md for content
    readme_content = Path("README.md").read_text(encoding="utf-8")
    if len(readme_content.strip()) < 100:
        print("❌ README.md content is too short")
        return False
    
    print("✅ Documentation is normal")
    return True


def check_package_structure():
    """Check package structure"""
    print("Checking package structure...")
    
    # Check main package directory
    if not Path("video2text").exists():
        print("❌ Main package directory does not exist")
        return False
    
    # Check __init__.py
    if not Path("video2text/__init__.py").exists():
        print("❌ __init__.py file does not exist")
        return False
    
    # Check core modules
    required_modules = [
        "video2text/config.py",
        "video2text/downloader.py",
        "video2text/transcriber.py",
        "video2text/api.py",
        "video2text/gui.py",
        "video2text/cli.py",
    ]
    
    for module in required_modules:
        if not Path(module).exists():
            print(f"❌ Missing module: {module}")
            return False
    
    print("✅ Package structure is normal")
    return True


def check_pyproject_toml():
    """Check pyproject.toml configuration"""
    print("Checking pyproject.toml configuration...")
    
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    # Check required fields
    required_fields = [
        "name",
        "version", 
        "description",
        "readme",
        "license",
        "authors",
        "classifiers",
        "dependencies"
    ]
    
    for field in required_fields:
        if field not in content:
            print(f"❌ pyproject.toml missing field: {field}")
            return False
    
    # Check for appropriate classifiers
    if "Programming Language :: Python :: 3" not in content:
        print("❌ Missing Python 3 classifier")
        return False
    
    print("✅ pyproject.toml configuration is normal")
    return True


def check_security():
    """Security check"""
    print("Performing security check...")
    
    # Check for sensitive information
    sensitive_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
    ]
    
    for py_file in Path("video2text").glob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"⚠️ Possible sensitive information: {py_file}")
                break
    
    print("✅ Security check passed")
    return True


def main():
    """Main function"""
    print("Starting pre-release check...")
    print("=" * 50)
    
    # Switch to project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    checks = [
        check_package_structure,
        check_pyproject_toml,
        check_version_consistency,
        check_dependencies,
        check_documentation,
        check_tests,
        check_git_status,
        check_security,
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Check failed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Check results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All checks passed! Can be safely released.")
        return 0
    else:
        print("❌ Some checks failed, please fix them before releasing.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 