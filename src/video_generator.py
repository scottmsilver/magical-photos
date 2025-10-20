"""
Unified Video Generator with multiple backend support.

Supports both cloud-based (Veo 3.1) and local GPU-based (SVD) video generation
with automatic fallback logic.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Backend(Enum):
    """Available video generation backends."""

    VEO_3_1 = "veo-3.1"
    SVD = "svd"
    AUTO = "auto"


class VideoGenerator:
    """Unified video generator supporting multiple backends."""

    def __init__(
        self,
        backend: Backend = Backend.AUTO,
        google_api_key: Optional[str] = None,
        veo_model_name: str = "veo-3.1-generate-preview",
        svd_model_name: str = "stabilityai/stable-video-diffusion-img2vid",
    ):
        """
        Initialize video generator.

        Args:
            backend: Which backend to use (AUTO tries Veo first, falls back to SVD)
            google_api_key: Google API key (required for Veo backend)
            veo_model_name: Veo model name
            svd_model_name: SVD model name
        """
        self.backend = backend
        self.google_api_key = google_api_key
        self.veo_model_name = veo_model_name
        self.svd_model_name = svd_model_name

        self.veo_client = None
        self.svd_client = None

        logger.info(f"VideoGenerator initialized with backend: {backend.value}")

    def _init_veo(self):
        """Initialize Veo 3.1 client (lazy loading)."""
        if self.veo_client is None:
            from src.api.veo3_client import Veo3Client

            logger.info("Initializing Veo 3.1 client...")
            self.veo_client = Veo3Client(api_key=self.google_api_key, model_name=self.veo_model_name)

    def _init_svd(self):
        """Initialize SVD client (lazy loading)."""
        if self.svd_client is None:
            from src.api.svd_client import SVDClient

            logger.info("Initializing SVD client...")
            self.svd_client = SVDClient(model_name=self.svd_model_name)

    def generate_video(
        self,
        image_path: str,
        prompt: str,
        output_path: Optional[str] = None,
        duration: int = 8,
        **kwargs,
    ) -> str:
        """
        Generate video from image with automatic backend selection.

        Args:
            image_path: Path to input image
            prompt: Animation description prompt
            output_path: Optional output path
            duration: Desired video duration in seconds
            **kwargs: Additional backend-specific parameters

        Returns:
            Path to generated video

        Raises:
            Exception: If all backends fail
        """
        # Determine which backend to use
        if self.backend == Backend.VEO_3_1:
            return self._generate_with_veo(image_path, prompt, output_path, duration, **kwargs)
        elif self.backend == Backend.SVD:
            return self._generate_with_svd(image_path, output_path, **kwargs)
        elif self.backend == Backend.AUTO:
            return self._generate_auto(image_path, prompt, output_path, duration, **kwargs)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _generate_with_veo(
        self, image_path: str, prompt: str, output_path: Optional[str], duration: int, **kwargs
    ) -> str:
        """Generate video using Veo 3.1."""
        logger.info("Generating video with Veo 3.1...")

        self._init_veo()

        return self.veo_client.generate_video(
            image_path=image_path, prompt=prompt, output_path=output_path, timeout=kwargs.get("timeout", 300)
        )

    def _generate_with_svd(self, image_path: str, output_path: Optional[str], **kwargs) -> str:
        """Generate video using Stable Video Diffusion."""
        logger.info("Generating video with Stable Video Diffusion (local GPU)...")

        self._init_svd()

        # SVD-specific parameters
        num_frames = kwargs.get("num_frames", 25)  # ~3.5 seconds at 7fps
        fps = kwargs.get("fps", 7)
        motion_bucket_id = kwargs.get("motion_bucket_id", 127)  # Moderate motion

        return self.svd_client.generate_video(
            image_path=image_path,
            output_path=output_path,
            num_frames=num_frames,
            fps=fps,
            motion_bucket_id=motion_bucket_id,
        )

    def _generate_auto(self, image_path: str, prompt: str, output_path: Optional[str], duration: int, **kwargs) -> str:
        """
        Auto backend selection: Try Veo first, fall back to SVD on failure.

        This is the recommended mode for production use.
        """
        logger.info("Auto backend mode: trying Veo 3.1 first...")

        if self.google_api_key:
            try:
                # Try Veo 3.1 first
                return self._generate_with_veo(image_path, prompt, output_path, duration, **kwargs)

            except Exception as e:
                logger.warning(f"Veo 3.1 generation failed: {e}")
                logger.info("Falling back to local SVD generation...")

                # Fall back to SVD
                return self._generate_with_svd(image_path, output_path, **kwargs)
        else:
            logger.info("No Google API key provided, using SVD directly")
            return self._generate_with_svd(image_path, output_path, **kwargs)

    def get_backend_info(self) -> dict:
        """
        Get information about available backends.

        Returns:
            Dictionary with backend availability and info
        """
        info = {
            "selected_backend": self.backend.value,
            "veo_available": self.google_api_key is not None,
            "svd_available": True,  # Always available if dependencies installed
        }

        # Check GPU for SVD
        try:
            import torch

            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["gpu_name"] = torch.cuda.get_device_name(0)
                info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
        except ImportError:
            info["cuda_available"] = False

        return info
