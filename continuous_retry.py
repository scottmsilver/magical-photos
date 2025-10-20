#!/usr/bin/env python3
"""
Continuous retry script for testing Veo 3.1 API access.
Runs attempts every 5 minutes until successful.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api.veo3_client import Veo3Client, VideoGenerationError
from src.prompts.prompt_builder import build_harry_potter_prompt
from src.utils.config import Config, setup_logging

# Configuration
RETRY_INTERVAL_SECONDS = 300  # 5 minutes between attempts
MAX_ATTEMPTS = None  # Run indefinitely (set to a number to limit)
IMAGE_PATH = "joy.jpg"
DURATION = 8


def main():
    # Load config
    config = Config.from_env()
    setup_logging(config)

    print("=" * 70)
    print("🧙 Veo 3.1 Continuous Retry Script")
    print("=" * 70)
    print(f"Image: {IMAGE_PATH}")
    print(f"Duration: {DURATION} seconds")
    print(f"Retry interval: {RETRY_INTERVAL_SECONDS} seconds ({RETRY_INTERVAL_SECONDS // 60} minutes)")
    print(f"Max attempts: {'Unlimited' if MAX_ATTEMPTS is None else MAX_ATTEMPTS}")
    print("=" * 70)
    print()

    # Initialize client
    client = Veo3Client(api_key=config.google_api_key, model_name=config.model_name)

    # Build prompt
    prompt = build_harry_potter_prompt(
        photo_type="portrait", intensity="subtle", duration=DURATION, custom_elements=["gentle smile"]
    )

    attempt = 0
    while True:
        attempt += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'=' * 70}")
        print(f"🔄 Attempt #{attempt} at {timestamp}")
        print(f"{'=' * 70}\n")

        try:
            # Try to generate video
            output_path = client.generate_video(
                image_path=IMAGE_PATH, prompt=prompt, output_path=f"output/joy_attempt_{attempt}.mp4", timeout=300
            )

            # SUCCESS!
            print("\n" + "=" * 70)
            print("✅ SUCCESS! Video generated successfully!")
            print("=" * 70)
            print(f"Output: {output_path}")
            print(f"Total attempts: {attempt}")
            print(f"Time: {timestamp}")
            print("=" * 70)
            return 0

        except VideoGenerationError as e:
            error_msg = str(e)

            # Check if it's a 502 error (expected)
            if "502" in error_msg or "Bad Gateway" in error_msg:
                print(f"⏳ Still getting 502 errors (expected - service is new)")
            else:
                print(f"❌ Error: {error_msg}")

            # Check if we should continue
            if MAX_ATTEMPTS is not None and attempt >= MAX_ATTEMPTS:
                print(f"\n⚠️  Reached maximum attempts ({MAX_ATTEMPTS}). Stopping.")
                return 1

            # Wait before next attempt
            next_attempt_time = datetime.now().timestamp() + RETRY_INTERVAL_SECONDS
            next_attempt_str = datetime.fromtimestamp(next_attempt_time).strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n⏰ Next attempt in {RETRY_INTERVAL_SECONDS // 60} minutes at {next_attempt_str}")
            print(f"   (Press Ctrl+C to stop)\n")

            try:
                time.sleep(RETRY_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Stopping.")
                print(f"Total attempts: {attempt}")
                return 1

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print(f"Total attempts: {attempt}")
            return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting.")
        sys.exit(1)
