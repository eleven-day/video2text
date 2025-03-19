# Contributing to Video2Text

Thank you for your interest in contributing to Video2Text! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Check the issue tracker to see if the bug has already been reported
- If not, create a new issue with a descriptive title and detailed information:
  - Steps to reproduce the issue
  - Expected behavior
  - Actual behavior
  - Screenshots if applicable
  - Environment information (OS, browser, Python version, etc.)

### Suggesting Enhancements

- Check if the enhancement has already been suggested
- Create a new issue with a clear title and detailed description
- Explain why this enhancement would be useful to most Video2Text users

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Commit your changes with clear, descriptive commit messages
6. Push to your fork and submit a pull request to the `main` branch
7. Wait for review and address any requested changes

## Development Setup

1. Install prerequisites:
   - Python 3.8+
   - Node.js 14+
   - FFmpeg

2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/video2text.git
   cd video2text
   ```

3. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

5. Start the development servers:
   ```bash
   # In one terminal (backend)
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn main:app --reload

   # In another terminal (frontend)
   cd frontend
   npm start
   ```

## Coding Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write descriptive commit messages
- Add tests for new features
- Update documentation when necessary

## Testing

- Run backend tests:
  ```bash
  cd backend
  pytest
  ```

- Run frontend tests:
  ```bash
  cd frontend
  npm test
  ```

## Documentation

- Update the README.md if necessary
- Document new features, API endpoints, or configuration options
- Add comments to complex code sections

Thank you for contributing to Video2Text!
