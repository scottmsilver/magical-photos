# Python Development Guidelines for Harry Potter Photo Frame Project

## Project Context
This is a Python-based AI application that transforms static photos into Harry Potter-style animated portraits using Google's Veo 3 API and potentially OpenAI's Sora API.

---

## Development Standards

### Python Version
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.10+
- Use type hints throughout the codebase

### Code Style
- Follow PEP 8 style guide
- Use Black for code formatting (line length: 88)
- Use isort for import sorting
- Use pylint/flake8 for linting
- Write docstrings for all functions, classes, and modules (Google style)

### Project Structure
```
harryphoto2/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── veo3_client.py      # Veo 3 API integration
│   │   └── sora_client.py      # Sora API integration (future)
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── image_processor.py  # Image preprocessing
│   │   └── video_processor.py  # Video post-processing
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── prompt_builder.py   # Animation prompt generation
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── file_handler.py     # File I/O operations
├── tests/
│   ├── __init__.py
│   ├── test_veo3_client.py
│   └── test_prompt_builder.py
├── examples/
│   └── single_photo_example.py
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
├── PLAN.md
└── AGENTS.md
```

---

## Dependencies Management

### Virtual Environment Setup (REQUIRED)

**IMPORTANT**: Always use a virtual environment for this project to avoid dependency conflicts.

#### Creating Virtual Environment
```bash
# Using venv (built-in)
python3 -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### Alternative: Using virtualenv or conda
```bash
# Using virtualenv
virtualenv venv
source venv/bin/activate

# Using conda
conda create -n harryphoto python=3.10
conda activate harryphoto
```

### Core Dependencies
```txt
google-generativeai>=0.3.0  # Veo 3 API
pillow>=10.0.0              # Image processing
python-dotenv>=1.0.0        # Environment variables
requests>=2.31.0            # HTTP requests
```

### Development Dependencies
```txt
pytest>=7.4.0               # Testing framework
black>=23.0.0               # Code formatting
isort>=5.12.0               # Import sorting
pylint>=2.17.0              # Linting
mypy>=1.5.0                 # Type checking
```

### Installation
```bash
# 1. Create and activate virtual environment (see above)

# 2. Install production dependencies
pip install -r requirements.txt

# 3. Install development dependencies (optional)
pip install -r requirements-dev.txt

# 4. Verify installation
pip list
```

---

## Configuration Management

### Environment Variables
Store sensitive data in `.env` file (never commit to git):

```bash
# .env
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Future use

# Optional settings
OUTPUT_DIR=./output
DEFAULT_VIDEO_DURATION=8
LOG_LEVEL=INFO
```

### Configuration File Structure
```python
# src/utils/config.py
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

@dataclass
class Config:
    google_api_key: str
    output_dir: str = "./output"
    video_duration: int = 8
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        return cls(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            video_duration=int(os.getenv("DEFAULT_VIDEO_DURATION", "8")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
```

---

## API Integration Guidelines

### Veo 3 Client Pattern
```python
# src/api/veo3_client.py
from typing import Optional
import google.generativeai as genai

class Veo3Client:
    """Client for Google Veo 3 API video generation."""

    def __init__(self, api_key: str):
        """Initialize Veo 3 client with API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('veo-3')

    async def generate_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 8
    ) -> str:
        """
        Generate video from image using Veo 3.

        Args:
            image_path: Path to input image
            prompt: Animation description prompt
            duration: Video duration in seconds

        Returns:
            Path to generated video file
        """
        # Implementation here
        pass
```

### Error Handling
- Use custom exceptions for API errors
- Implement retry logic with exponential backoff
- Log all API interactions
- Validate inputs before API calls

```python
# src/api/exceptions.py
class APIError(Exception):
    """Base exception for API errors."""
    pass

class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass

class InvalidImageError(APIError):
    """Raised when image is invalid or unsupported."""
    pass
```

---

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external API calls
- Aim for >80% code coverage

```python
# tests/test_prompt_builder.py
import pytest
from src.prompts.prompt_builder import build_hp_prompt

def test_build_hp_prompt_basic():
    prompt = build_hp_prompt("portrait")
    assert "subtle" in prompt.lower()
    assert "portrait" in prompt.lower()
```

### Integration Tests
- Test API integration with mock responses
- Test end-to-end workflow with sample images

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_veo3_client.py
```

---

## Logging

### Logging Configuration
```python
# src/utils/logger.py
import logging
from typing import Optional

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

---

## Security Best Practices

### API Key Management
- **NEVER** hardcode API keys in source code
- Use environment variables or secret management tools
- Add `.env` to `.gitignore`
- Provide `.env.example` with dummy values

### Input Validation
- Validate image file types (JPEG, PNG)
- Check file size limits before uploading
- Sanitize file paths to prevent directory traversal
- Validate user-provided prompts

---

## Performance Considerations

### Image Processing
- Resize large images before API upload
- Compress images to reduce bandwidth
- Support batch processing with async/await

### API Usage
- Implement request queuing for batch operations
- Use connection pooling
- Cache results when appropriate
- Monitor API quota usage

```python
# Example async batch processing
import asyncio
from typing import List

async def process_photos_batch(
    photos: List[str],
    max_concurrent: int = 5
) -> List[str]:
    """Process multiple photos concurrently with rate limiting."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(photo: str) -> str:
        async with semaphore:
            return await process_single_photo(photo)

    return await asyncio.gather(
        *[process_with_semaphore(photo) for photo in photos]
    )
```

---

## Git Workflow

### Branching Strategy
- `main` - production-ready code
- `develop` - integration branch
- `feature/*` - new features
- `bugfix/*` - bug fixes

### Commit Messages
Follow conventional commits:
```
feat: add Veo 3 API integration
fix: handle invalid image format error
docs: update API configuration guide
test: add unit tests for prompt builder
```

### Files to Ignore (.gitignore)
```gitignore
# Environment
.env
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# IDE
.vscode/
.idea/
*.swp

# Output
output/
*.mp4
*.mov

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

## Documentation Standards

### Docstring Format (Google Style)
```python
def generate_animation_prompt(
    photo_type: str,
    intensity: str = "subtle",
    duration: int = 8
) -> str:
    """
    Generate an animation prompt for Harry Potter style effect.

    Args:
        photo_type: Type of photo (portrait, group, landscape)
        intensity: Animation intensity (subtle, moderate, dramatic)
        duration: Desired video duration in seconds

    Returns:
        Formatted prompt string for video generation API

    Raises:
        ValueError: If photo_type is not supported

    Examples:
        >>> generate_animation_prompt("portrait", "subtle", 5)
        "Subtle portrait animation, gentle breathing..."
    """
    pass
```

### README Structure
- Project overview
- Installation instructions
- Quick start guide
- Configuration options
- API documentation
- Contributing guidelines
- License information

---

## Agent-Specific Instructions

### When Writing Code
1. Always add type hints
2. Write docstrings for all public functions
3. Include error handling
4. Add logging for important operations
5. Write unit tests for new functionality

### When Reviewing Code
1. Check for security issues (API key exposure)
2. Verify error handling is comprehensive
3. Ensure code follows PEP 8
4. Validate that tests cover new code
5. Check for performance bottlenecks

### When Adding Dependencies
1. Specify minimum version in requirements.txt
2. Document why the dependency is needed
3. Check for license compatibility
4. Verify package is actively maintained

### When Working with APIs
1. Never commit API keys
2. Implement rate limiting
3. Add retry logic for transient failures
4. Log all API requests/responses (sanitized)
5. Handle all documented error codes

---

## Resources

### Python Best Practices
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Real Python Tutorials](https://realpython.com/)

### API Documentation
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Veo 3 Video Generation](https://ai.google.dev/gemini-api/docs/video)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)

---

## Questions for Development Team

Before starting implementation:
1. Do we have a Google Cloud API key with Veo 3 access?
2. What is our expected daily photo processing volume?
3. Do we need a web UI or is CLI sufficient for MVP?
4. What video output formats are required (MP4, MOV, etc.)?
5. Should we support video looping/seamless playback?
