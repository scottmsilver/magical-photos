"""
Video Generator using Veo 3.1 for Harry Potter style animations.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Video generator using Veo 3.1."""

    def __init__(
        self,
        google_api_key: str,
        veo_model_name: str = "veo-3.1-generate-preview",
    ):
        """
        Initialize video generator.

        Args:
            google_api_key: Google API key (required for Veo)
            veo_model_name: Veo model name
        """
        self.google_api_key = google_api_key
        self.veo_model_name = veo_model_name
        self.veo_client = None

        logger.info(f"VideoGenerator initialized with model: {veo_model_name}")

    def _init_veo(self):
        """Initialize Veo 3.1 client (lazy loading)."""
        if self.veo_client is None:
            from src.api.veo3_client import Veo3Client

            logger.info("Initializing Veo 3.1 client...")
            self.veo_client = Veo3Client(api_key=self.google_api_key, model_name=self.veo_model_name)

    def generate_video(
        self,
        image_path: str,
        prompt: str,
        output_path: Optional[str] = None,
        duration: int = 8,
        **kwargs,
    ) -> str:
        """
        Generate video from image using Veo 3.1.

        Args:
            image_path: Path to input image
            prompt: Animation description prompt
            output_path: Optional output path
            duration: Desired video duration in seconds
            **kwargs: Additional parameters

        Returns:
            Path to generated video

        Raises:
            Exception: If video generation fails
        """
        logger.info("Generating video with Veo 3.1...")

        self._init_veo()

        return self.veo_client.generate_video(
            image_path=image_path, prompt=prompt, output_path=output_path, timeout=kwargs.get("timeout", 300)
        )

    def get_backend_info(self) -> dict:
        """
        Get information about Veo backend.

        Returns:
            Dictionary with backend info
        """
        return {
            "backend": "veo-3.1",
            "model": self.veo_model_name,
            "veo_available": self.google_api_key is not None,
        }
