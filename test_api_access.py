#!/usr/bin/env python3
"""Test API access to Veo 3."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from google import genai

from src.utils.config import Config, setup_logging


def main():
    # Load config
    config = Config.from_env()
    setup_logging(config)

    client = genai.Client(api_key=config.google_api_key)

    print("Testing API access...\n")

    # Try to list available models
    try:
        print("Fetching available models...")
        models = client.models.list()

        print("\n✅ API Key is valid!\n")
        print("Available models:")
        print("=" * 60)

        video_models = []
        for model in models:
            if "veo" in model.name.lower() or "video" in model.name.lower():
                video_models.append(model.name)
                print(f"  📹 {model.name}")

        if not video_models:
            print("\n⚠️  No video generation models found.")
            print("\nYour API key may not have access to Veo 3.")
            print("\nTo get access:")
            print("  1. Ensure you're on the PAID tier")
            print("  2. Visit: https://ai.google.dev")
            print("  3. Check pricing: https://ai.google.dev/pricing")
            print(f"\n  Current cost: $0.75 per second of video")
            return 1
        else:
            print(f"\n✅ Found {len(video_models)} video generation model(s)!")
            return 0

    except Exception as e:
        print(f"\n❌ Error accessing API: {e}")
        print("\nPlease check:")
        print("  1. Your API key is correct in .env")
        print("  2. You have internet connection")
        return 1


if __name__ == "__main__":
    sys.exit(main())
