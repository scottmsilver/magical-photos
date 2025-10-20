"""
Veo 3 API Client for video generation from images.

This module provides a client for interacting with Google's Veo 3 API
to generate animated videos from static images using the new genai.Client API.
"""

import base64
import logging
import time
from pathlib import Path
from typing import Optional

from google import genai

from src.utils.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


class Veo3ClientError(Exception):
    """Base exception for Veo3Client errors."""

    pass


class APIConnectionError(Veo3ClientError):
    """Raised when API connection fails."""

    pass


class VideoGenerationError(Veo3ClientError):
    """Raised when video generation fails."""

    pass


class InvalidImageError(Veo3ClientError):
    """Raised when image is invalid or unsupported."""

    pass


class Veo3Client:
    """Client for Google Veo 3 API video generation."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE_MB = 10

    def __init__(self, api_key: str, model_name: str = "veo-3.1-generate-preview"):
        """
        Initialize Veo 3 client with API key.

        Args:
            api_key: Google API key for Gemini/Veo access
            model_name: Veo model name (default: veo-3.1-generate-preview)

        Raises:
            APIConnectionError: If API configuration fails
        """
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = model_name
            logger.info(f"Veo3Client initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Veo3Client: {e}")
            raise APIConnectionError(f"Failed to configure API: {e}") from e

    def validate_image(self, image_path: str) -> Path:
        """
        Validate image file before processing.

        Args:
            image_path: Path to image file

        Returns:
            Path object of validated image

        Raises:
            InvalidImageError: If image is invalid
        """
        path = Path(image_path)

        if not path.exists():
            raise InvalidImageError(f"Image file not found: {image_path}")

        if not path.is_file():
            raise InvalidImageError(f"Path is not a file: {image_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise InvalidImageError(
                f"Unsupported format: {path.suffix}. " f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise InvalidImageError(f"File too large: {file_size_mb:.2f}MB. " f"Maximum: {self.MAX_FILE_SIZE_MB}MB")

        logger.debug(f"Image validated: {image_path} ({file_size_mb:.2f}MB)")
        return path

    def generate_video(
        self,
        image_path: str,
        prompt: str,
        output_path: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 10,
        aspect_ratio_override: Optional[str] = None,
    ) -> str:
        """
        Generate video from image using Veo 3.

        Args:
            image_path: Path to input image
            prompt: Animation description prompt
            output_path: Optional path for output video (auto-generated if None)
            timeout: Maximum time to wait for generation (seconds)
            poll_interval: Time between status checks (seconds)

        Returns:
            Path to generated video file

        Raises:
            InvalidImageError: If image validation fails
            VideoGenerationError: If video generation fails
        """
        # Validate image
        image_file = self.validate_image(image_path)

        # Prepare output path
        if output_path is None:
            output_path = str(Path("output") / f"{image_file.stem}_animated.mp4")
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting video generation for: {image_path}")
        logger.debug(f"Prompt: {prompt}")

        try:
            # Load image from file with proper MIME type
            logger.info("Loading image file...")
            from google.genai import types
            from PIL import Image as PILImage

            # Determine aspect ratio to use
            if aspect_ratio_override:
                aspect_ratio = aspect_ratio_override
                logger.info(f"Using override aspect ratio: {aspect_ratio}")
            else:
                # Detect aspect ratio from source image
                with PILImage.open(image_file) as img:
                    width, height = img.size
                    aspect = width / height

                    # Map to supported Veo aspect ratios
                    # Note: Some combinations may not be supported with reference images
                    if aspect > 1.2:  # Landscape or wide
                        aspect_ratio = "16:9"
                    elif aspect > 0.83:  # Square-ish or slightly portrait
                        aspect_ratio = "16:9"  # Default to landscape for compatibility
                    else:  # Portrait
                        aspect_ratio = "16:9"  # Default to landscape for compatibility

                    logger.info(f"Source image: {width}x{height} (aspect: {aspect:.2f}) -> Target: {aspect_ratio}")

            # Preprocess image to fit target aspect ratio if needed
            from src.utils.image_utils import fit_image_to_aspect_ratio

            with PILImage.open(image_file) as img:
                width, height = img.size
                current_aspect = width / height
                target_aspect_map = {"16:9": 16 / 9, "9:16": 9 / 16, "4:3": 4 / 3, "1:1": 1}
                target_aspect_value = target_aspect_map.get(aspect_ratio, 16 / 9)

                # Check if preprocessing is needed (allow 5% tolerance)
                if abs(current_aspect - target_aspect_value) / target_aspect_value > 0.05:
                    logger.info(f"Preprocessing image to fit {aspect_ratio} aspect ratio (padding mode)...")
                    processed_image_path = fit_image_to_aspect_ratio(
                        str(image_file), aspect_ratio, mode="pad", background_color=(0, 0, 0)  # Black letterboxing
                    )
                    image_file = Path(processed_image_path)
                    logger.info(f"Using preprocessed image: {image_file}")

            # Use types.Image.from_file() to load the image properly
            image = types.Image.from_file(location=str(image_file))

            logger.info("Requesting video generation with reference image...")

            # Create reference image with proper type (as shown in API examples)
            reference_image = types.VideoGenerationReferenceImage(image=image, reference_type="asset")

            # Retry logic for transient errors (502, 503, etc.)
            max_retries = 3
            retry_delay = 30  # Start with 30 seconds
            operation = None

            for attempt in range(max_retries):
                try:
                    # Check rate limit before making request
                    rate_limiter = get_rate_limiter()
                    rate_limiter.record_request("Veo video generation")

                    operation = self.client.models.generate_videos(
                        model=self.model_name,
                        prompt=prompt,
                        config=types.GenerateVideosConfig(
                            reference_images=[reference_image], aspect_ratio=aspect_ratio, resolution="720p"
                        ),
                    )
                    logger.info(f"Video generation request successful on attempt {attempt + 1}")
                    break  # Success, exit retry loop

                except Exception as e:
                    error_str = str(e)
                    # Check if it's a retryable error (502, 503, 429)
                    if any(
                        code in error_str
                        for code in ["502", "503", "429", "Bad Gateway", "Service Unavailable", "Too Many Requests"]
                    ):
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Transient error on attempt {attempt + 1}/{max_retries}: {error_str[:100]}..."
                            )
                            logger.info(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(f"Failed after {max_retries} attempts")
                            raise VideoGenerationError(f"Failed after {max_retries} retries: {e}") from e
                    else:
                        # Non-retryable error, fail immediately
                        raise

            if operation is None:
                raise VideoGenerationError("Failed to initiate video generation after retries")

            logger.info(f"Operation started: {operation.name}")
            logger.info("Waiting for video generation to complete...")

            # Poll operation status
            start_time = time.time()
            while not operation.done:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise VideoGenerationError(f"Video generation timed out after {timeout} seconds")

                logger.debug(f"Waiting... ({int(elapsed)}s elapsed)")
                time.sleep(poll_interval)
                operation = self.client.operations.get(operation)

            # Check for errors
            if operation.error:
                raise VideoGenerationError(f"Generation failed: {operation.error}")

            if not operation.response:
                raise VideoGenerationError("No response from generation operation")

            # Get generated video
            if not operation.response.generated_videos:
                raise VideoGenerationError("No video in response")

            video = operation.response.generated_videos[0]

            logger.info("Video generated successfully!")
            logger.info("Downloading video...")

            # Download video data from storage (this sets video_bytes property)
            self.client.files.download(file=video)

            # Now save the video to disk
            video.video.save(str(output_file))

            logger.info(f"Video saved to: {output_path}")
            return str(output_file)

        except VideoGenerationError:
            raise
        except InvalidImageError:
            raise
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise VideoGenerationError(f"Failed to generate video: {e}") from e

    def generate_video_async(self, image_path: str, prompt: str, output_path: Optional[str] = None) -> str:
        """
        Generate video asynchronously (returns operation name).

        Note: This returns the operation name that can be polled separately.

        Args:
            image_path: Path to input image
            prompt: Animation description prompt
            output_path: Optional path for output video

        Returns:
            Operation name for polling

        Raises:
            InvalidImageError: If image validation fails
            VideoGenerationError: If video generation request fails
        """
        # Validate image
        image_file = self.validate_image(image_path)

        try:
            # Upload image file to Google's File API
            uploaded_file = self.client.files.upload(file=str(image_file))

            # Start video generation operation with uploaded file
            operation = self.client.models.generate_videos(model=self.model_name, prompt=prompt, image=uploaded_file)

            logger.info(f"Async operation started: {operation.name}")
            return operation.name

        except Exception as e:
            logger.error(f"Async video generation failed: {e}")
            raise VideoGenerationError(f"Failed to start generation: {e}") from e
