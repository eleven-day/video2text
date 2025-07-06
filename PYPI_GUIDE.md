# PyPI Packaging and Upload Guide

This guide details how to package and upload the Video2Text project to PyPI.

## Prerequisites

### 1. Install Required Tools

```bash
# Install build and upload tools
pip install build twine

# Or use project dependencies
pip install -e ".[dev]"
```

### 2. Register a PyPI Account

1. **Official PyPI**: https://pypi.org/account/register/
2. **TestPyPI**: https://test.pypi.org/account/register/

### 3. Configure API Token

#### Method 1: Environment Variables (Recommended)
```bash
# Set TestPyPI token
export TESTPYPI_TOKEN="pypi-your-testpypi-token"

# Set PyPI token
export PYPI_TOKEN="pypi-your-pypi-token"
```

#### Method 2: Configuration File
Create a `~/.pypirc` file:
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-pypi-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token
```

## Packaging and Uploading with Scripts

### Method 1: Using Python Scripts (Recommended)

```bash
# Show help
python scripts/build_and_upload.py

# Full process (test)
python scripts/build_and_upload.py --all

# Production release
python scripts/build_and_upload.py --production

# Individual operations
python scripts/build_and_upload.py --clean        # Clean
python scripts/build_and_upload.py --build        # Build
python scripts/build_and_upload.py --check        # Check
python scripts/build_and_upload.py --test-upload  # Upload to TestPyPI
python scripts/build_and_upload.py --upload       # Upload to PyPI
```

### Method 2: Using System Scripts

#### Windows
```cmd
# Double-click or run in command line
scripts\build_and_upload.bat
```

#### Linux/macOS
```bash
# Run script
./scripts/build_and_upload.sh
```

## Manual Steps

### 1. Clean Build Files

```bash
# Remove old build files
rm -rf build/ dist/ *.egg-info/
```

### 2. Update Version Number

Edit the `pyproject.toml` file to update the version number:
```toml
[project]
name = "video2text"
version = "1.0.1"  # Update the version number
```

### 3. Build the Package

```bash
# Build source and wheel packages
python -m build
```

After building, the `dist/` directory will contain:
- `video2text-1.0.1.tar.gz` (source package)
- `video2text-1.0.1-py3-none-any.whl` (wheel package)

### 4. Check the Package

```bash
# Check package integrity
python -m twine check dist/*
```

### 5. Test Upload (Optional)

```bash
# Upload to TestPyPI for testing
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ video2text
```

### 6. Official Upload

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Version Management Strategy

### Semantic Versioning

Follow the [Semantic Versioning](https://semver.org/) specification:
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- `MAJOR`: Incompatible API changes
- `MINOR`: Backward-compatible feature additions
- `PATCH`: Backward-compatible bug fixes

### Version Number Examples

```
1.0.0    # Initial release
1.0.1    # Bug fix
1.1.0    # New feature
2.0.0    # Major change
```

### Pre-release Versions

```
1.0.0a1  # Alpha version
1.0.0b1  # Beta version
1.0.0rc1 # Release Candidate
```

## Release Checklist

### Pre-release Checks

- [ ] Code committed to git
- [ ] Version number updated
- [ ] CHANGELOG updated
- [ ] Tests passed
- [ ] Documentation updated
- [ ] Dependency versions confirmed

### Build Checks

- [ ] Old build files cleaned
- [ ] Build successful
- [ ] Package integrity check passed
- [ ] TestPyPI installation successful

### Post-release Checks

- [ ] PyPI page displays correctly
- [ ] Installation works
- [ ] Functional tests passed
- [ ] Git tag created
- [ ] Release notes published

## Common Issues

### 1. Build Failure

**Problem**: `python -m build` fails  
**Solution**: 
- Check `pyproject.toml` configuration
- Ensure all dependencies are installed
- Check if the file structure is correct

### 2. Upload Failure

**Problem**: `twine upload` fails  
**Solution**:
- Check if the API token is correct
- Ensure the version number is not already used
- Check network connection

### 3. Version Conflict

**Problem**: Version number already exists  
**Solution**:
- Update the version number
- Clean and rebuild
- You cannot overwrite a published version

### 4. Dependency Issues

**Problem**: Missing dependencies after installation  
**Solution**:
- Check the dependencies configuration in `pyproject.toml`
- Ensure all necessary dependencies are listed
- Test installation in a clean environment

## Automated Release

### GitHub Actions

You can configure GitHub Actions for automated release:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Maintenance Suggestions

1. **Regular Updates**: Regularly update dependencies and fix bugs
2. **Documentation Maintenance**: Keep documentation in sync with code
3. **Backward Compatibility**: Try to maintain API backward compatibility
4. **Security Updates**: Fix security vulnerabilities promptly
5. **Community Feedback**: Actively respond to user feedback and issues

## Reference Resources

- [PyPI Official Documentation](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)

---

If you have any questions, please check the project's README.md or submit an issue.