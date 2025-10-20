"""
Stable Video Diffusion (SVD) Client for local GPU-based video generation.

This module provides a client for running Stable Video Diffusion locally
on your GPU to generate animated videos from static images.
"""

import logging
from pathlib import Path
from typing import Optional

import imageio
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video, load_image
from PIL import Image

logger = logging.getLogger(__name__)


class SVDClientError(Exception):
    """Base exception for SVDClient errors."""

    pass


class ModelLoadError(SVDClientError):
    """Raised when model loading fails."""

    pass


class VideoGenerationError(SVDClientError):
    """Raised when video generation fails."""

    pass


class InvalidImageError(SVDClientError):
    """Raised when image is invalid or unsupported."""

    pass


class SVDClient:
    """Client for Stable Video Diffusion local GPU generation."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE_MB = 50
    DEFAULT_MODEL = "stabilityai/stable-video-diffusion-img2vid"  # Base model for 12GB GPUs

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        torch_dtype: torch.dtype = torch.float16,
    ):
        """
        Initialize SVD client.

        Args:
            model_name: HuggingFace model ID (default: SVD img2vid-xt)
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
            torch_dtype: Torch data type for inference (float16 for GPU)

        Raises:
            ModelLoadError: If model loading fails
        """
        # Auto-detect device if not specified
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Auto-detected device: {device}")

        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = "cpu"

        self.device = device
        self.model_name = model_name
        self.torch_dtype = torch_dtype if device == "cuda" else torch.float32

        logger.info(f"Initializing SVD client on {device} with {self.torch_dtype}")

        try:
            # Load the pipeline
            logger.info(f"Loading model: {model_name} (this may take a few minutes on first run)")
            self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                model_name, torch_dtype=self.torch_dtype, variant="fp16" if device == "cuda" else None
            )
            self.pipeline.to(device)

            # Enable memory optimizations if on CUDA
            if device == "cuda":
                logger.info("Enabling GPU memory optimizations")
                self.pipeline.enable_model_cpu_offload()
                # Enable attention slicing for lower VRAM usage (critical for 12GB GPUs)
                self.pipeline.enable_attention_slicing()
                # Enable forward chunking to reduce memory usage to <8GB
                self.pipeline.unet.enable_forward_chunking()
                logger.info("Enabled attention slicing and forward chunking to reduce VRAM to <8GB")

            logger.info("SVD client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to load SVD model: {e}")
            raise ModelLoadError(f"Failed to load model {model_name}: {e}") from e

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
        output_path: Optional[str] = None,
        num_frames: int = 14,  # Base model generates 14 frames (vs 25 for XT)
        num_inference_steps: int = 25,
        fps: int = 7,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
        decode_chunk_size: int = 2,  # Lower value = less VRAM (can reduce to <8GB)
    ) -> str:
        """
        Generate video from image using Stable Video Diffusion.

        Args:
            image_path: Path to input image
            output_path: Optional path for output video (auto-generated if None)
            num_frames: Number of frames to generate (default: 25 for ~3.5s at 7fps)
            num_inference_steps: Number of denoising steps (default: 25)
            fps: Frames per second for output video (default: 7)
            motion_bucket_id: Motion strength (0-255, default 127 = moderate motion)
            noise_aug_strength: Noise augmentation (0.0-1.0, default 0.02)
            decode_chunk_size: Frames to decode at once (lower = less VRAM)

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
            output_path = str(Path("output") / f"{image_file.stem}_svd_animated.mp4")
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting SVD video generation for: {image_path}")
        logger.info(f"Frames: {num_frames}, FPS: {fps}, Steps: {num_inference_steps}")
        logger.info(f"Motion strength: {motion_bucket_id}/255")

        try:
            # Load and preprocess image
            logger.info("Loading and preprocessing image...")
            image = load_image(str(image_file))

            # Resize to optimal resolution (1024x576 for SVD)
            image = image.resize((1024, 576))

            # Generate video frames
            logger.info("Generating video frames (this may take 3-5 minutes)...")

            with torch.inference_mode():
                frames = self.pipeline(
                    image,
                    num_frames=num_frames,
                    num_inference_steps=num_inference_steps,
                    motion_bucket_id=motion_bucket_id,
                    noise_aug_strength=noise_aug_strength,
                    decode_chunk_size=decode_chunk_size,
                ).frames[0]

            logger.info(f"Generated {len(frames)} frames")

            # Save video
            logger.info("Encoding video...")
            export_to_video(frames, str(output_file), fps=fps)

            logger.info(f"Video saved to: {output_path}")
            logger.info(f"Duration: {len(frames)/fps:.2f} seconds")

            return str(output_file)

        except VideoGenerationError:
            raise
        except InvalidImageError:
            raise
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise VideoGenerationError(f"Failed to generate video: {e}") from e

    def get_gpu_memory_info(self) -> dict:
        """
        Get GPU memory usage information.

        Returns:
            Dictionary with memory stats (if CUDA available)
        """
        if not torch.cuda.is_available():
            return {"available": False}

        return {
            "available": True,
            "device_name": torch.cuda.get_device_name(0),
            "total_memory_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
            "allocated_gb": torch.cuda.memory_allocated(0) / 1024**3,
            "reserved_gb": torch.cuda.memory_reserved(0) / 1024**3,
        }
