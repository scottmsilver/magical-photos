#!/usr/bin/env python3
"""
Example script for generating a single Harry Potter style animated portrait.

This script demonstrates how to use the harryphoto2 library to animate
a single photo with Harry Potter magical photograph styling.

Usage:
    python examples/single_photo_example.py path/to/photo.jpg

    # With custom intensity
    python examples/single_photo_example.py path/to/photo.jpg --intensity moderate

    # With custom duration
    python examples/single_photo_example.py path/to/photo.jpg --duration 5
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.veo3_client import Veo3Client, Veo3ClientError
from src.prompts.prompt_builder import build_harry_potter_prompt
from src.utils.config import Config, setup_logging


def main():
    """Main function for single photo animation."""
    parser = argparse.ArgumentParser(description="Animate a photo with Harry Potter style magic")
    parser.add_argument("image_path", help="Path to the image file to animate")
    parser.add_argument(
        "--intensity",
        choices=["subtle", "moderate", "dramatic"],
        default="subtle",
        help="Animation intensity (default: subtle)",
    )
    parser.add_argument(
        "--photo-type",
        choices=["portrait", "group", "landscape", "pet", "formal"],
        default="portrait",
        help="Type of photo (default: portrait)",
    )
    parser.add_argument("--duration", type=int, default=8, help="Video duration in seconds (default: 8)")
    parser.add_argument("--output", help="Output video path (default: auto-generated)")
    parser.add_argument("--custom-prompt", help="Use a custom animation description instead of preset")

    args = parser.parse_args()

    try:
        # Load configuration
        print("Loading configuration...")
        config = Config.from_env()
        setup_logging(config)

        # Verify image exists
        image_path = Path(args.image_path)
        if not image_path.exists():
            print(f"Error: Image file not found: {args.image_path}")
            return 1

        print(f"Image: {image_path}")
        print(f"Intensity: {args.intensity}")
        print(f"Photo Type: {args.photo_type}")
        print(f"Duration: {args.duration}s")
        print()

        # Build prompt
        if args.custom_prompt:
            print(f"Using custom prompt: {args.custom_prompt}")
            prompt = args.custom_prompt
        else:
            print("Building Harry Potter style animation prompt...")
            prompt = build_harry_potter_prompt(
                photo_type=args.photo_type, intensity=args.intensity, duration=args.duration
            )
            print(f"Prompt: {prompt[:100]}...")
        print()

        # Initialize Veo3 client
        print("Initializing Veo 3 API client...")
        client = Veo3Client(api_key=config.google_api_key, model_name=config.model_name)
        print()

        # Generate video
        print("Starting video generation...")
        print("This may take a few minutes. Please wait...")
        print()

        output_path = client.generate_video(image_path=str(image_path), prompt=prompt, output_path=args.output)

        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Video saved to: {output_path}")
        print()
        print("Your magical Harry Potter style portrait is ready!")
        return 0

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your GOOGLE_API_KEY to the .env file")
        return 1

    except Veo3ClientError as e:
        print(f"\nAPI Error: {e}")
        print("\nPlease check:")
        print("1. Your API key is valid")
        print("2. You have access to Veo 3 API")
        print("3. Your internet connection is stable")
        return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130

    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        print("\nPlease report this issue if it persists.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
