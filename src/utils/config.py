"""
Configuration management for Harry Potter Photo Frame project.

Handles loading configuration from environment variables and provides
a centralized configuration object.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration."""

    google_api_key: str
    openai_api_key: Optional[str] = None
    output_dir: str = "./output"
    video_duration: int = 8
    log_level: str = "INFO"
    model_name: str = "veo-3.1-generate-preview"
    max_workers: int = 5

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")

        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            logger.warning(f"Invalid log level: {self.log_level}. Using INFO.")
            self.log_level = "INFO"

        logger.debug(f"Configuration initialized: output_dir={self.output_dir}")

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """
        Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file (defaults to .env in cwd)

        Returns:
            Config instance

        Raises:
            ValueError: If required configuration is missing
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Read environment variables
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. " "Please set it in .env file or environment variables."
            )

        return cls(
            google_api_key=google_api_key,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            video_duration=int(os.getenv("DEFAULT_VIDEO_DURATION", "8")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            model_name=os.getenv("MODEL_NAME", "veo-3.1-generate-preview"),
            max_workers=int(os.getenv("MAX_WORKERS", "5")),
        )

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Config instance
        """
        return cls(**config_dict)


def setup_logging(config: Config) -> None:
    """
    Set up logging configuration.

    Args:
        config: Configuration object
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info(f"Logging configured at {config.log_level} level")
