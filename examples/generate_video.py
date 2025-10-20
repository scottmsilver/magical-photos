#!/usr/bin/env python3
"""
Generate Harry Potter style animated video from a photo.

Supports multiple backends:
- Veo 3.1 (cloud-based, Google API)
- Stable Video Diffusion (local GPU)
- Auto (tries Veo first, falls back to SVD)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prompts.prompt_builder import build_harry_potter_prompt
from src.utils.config import Config, setup_logging
from src.video_generator import Backend, VideoGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate Harry Potter style animated video from photo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto mode (tries Veo, falls back to SVD)
  %(prog)s portrait.jpg

  # Force SVD (local GPU)
  %(prog)s portrait.jpg --backend svd

  # Force Veo 3.1 (cloud API)
  %(prog)s portrait.jpg --backend veo

  # Custom settings
  %(prog)s portrait.jpg --intensity dramatic --output my_video.mp4
        """,
    )

    parser.add_argument("image", help="Path to input image")

    parser.add_argument(
        "--backend",
        choices=["auto", "veo", "svd"],
        default="auto",
        help="Backend to use (default: auto - tries Veo first, falls back to SVD)",
    )

    parser.add_argument(
        "--photo-type",
        choices=["portrait", "group", "landscape", "pet", "formal"],
        default="portrait",
        help="Type of photo (default: portrait)",
    )

    parser.add_argument(
        "--intensity",
        choices=["subtle", "moderate", "dramatic"],
        default="subtle",
        help="Animation intensity (default: subtle)",
    )

    parser.add_argument("--duration", type=int, default=8, help="Video duration in seconds (default: 8)")

    parser.add_argument("--output", "-o", help="Output video path (default: auto-generated)")

    parser.add_argument(
        "--custom-elements", nargs="+", help='Custom animation elements (e.g., "gentle smile" "soft wind")'
    )

    parser.add_argument(
        "--loop",
        action="store_true",
        help="Create a seamlessly looping video with crossfade (default: False)",
    )

    parser.add_argument(
        "--loop-crossfade",
        type=float,
        default=0.5,
        help="Crossfade duration for looping in seconds (default: 0.5)",
    )

    parser.add_argument(
        "--use-gemini-prompt",
        action="store_true",
        help="Use Gemini to analyze image and generate contextual magical prompt (default: False)",
    )

    parser.add_argument(
        "--preprocess-bw",
        action="store_true",
        help="Convert image to black & white before processing (default: False)",
    )

    parser.add_argument(
        "--bw-method",
        choices=["grayscale", "high_contrast", "vintage"],
        default="high_contrast",
        help="Black & white conversion method (default: high_contrast)",
    )

    # SVD-specific options
    svd_group = parser.add_argument_group("SVD options (when using SVD backend)")
    svd_group.add_argument("--fps", type=int, default=7, help="Frames per second (default: 7)")
    svd_group.add_argument("--motion", type=int, default=127, help="Motion strength 0-255 (default: 127)")

    args = parser.parse_args()

    # Load config
    config = Config.from_env()
    setup_logging(config)

    # Map backend string to enum
    backend_map = {"auto": Backend.AUTO, "veo": Backend.VEO_3_1, "svd": Backend.SVD}
    backend = backend_map[args.backend]

    print("=" * 70)
    print("🧙 Harry Potter Photo Frame Generator")
    print("=" * 70)
    print(f"Backend: {args.backend.upper()}")
    print(f"Image: {args.image}")
    print(f"Type: {args.photo_type}")
    print(f"Intensity: {args.intensity}")
    print(f"Duration: {args.duration}s")
    print("=" * 70)
    print()

    # Initialize video generator
    try:
        generator = VideoGenerator(
            backend=backend, google_api_key=config.google_api_key if backend != Backend.SVD else None
        )

        # Show backend info
        info = generator.get_backend_info()
        print("Backend Information:")
        print(f"  Selected: {info['selected_backend']}")
        print(f"  Veo available: {'✅' if info['veo_available'] else '❌'}")
        print(f"  SVD available: {'✅' if info['svd_available'] else '❌'}")
        if info.get("cuda_available"):
            print(f"  GPU: {info['gpu_name']} ({info['gpu_memory_gb']:.1f} GB)")
        else:
            print("  GPU: Not available (will use CPU)")
        print()

    except Exception as e:
        print(f"❌ Failed to initialize video generator: {e}")
        return 1

    # Preprocess image to B&W if requested
    working_image_path = args.image
    if args.preprocess_bw:
        print("🎨 Converting image to black & white...")
        print("=" * 70)
        from src.utils.image_utils import convert_to_black_and_white

        try:
            bw_image_path = convert_to_black_and_white(
                args.image,
                method=args.bw_method,
            )
            working_image_path = bw_image_path
            print(f"✅ B&W image created: {bw_image_path}")
            print(f"   Method: {args.bw_method}")
            print("=" * 70)
            print()
        except Exception as e:
            print(f"⚠️  B&W conversion failed: {e}")
            print("   Using original color image...")
            print()

    # Build prompt (for Veo backend)
    if args.use_gemini_prompt and backend != Backend.SVD:
        print("🔮 Using Gemini to analyze image and generate contextual prompt...")
        print("=" * 70)

        from src.api.gemini_analyzer import GeminiAnalyzer

        try:
            analyzer = GeminiAnalyzer(api_key=config.google_api_key)

            # First show the analysis
            print("\n📊 Image Analysis:")
            analysis = analyzer.analyze_for_animation(working_image_path)
            print(f"  People: {analysis.get('people', 'N/A')}")
            print(f"  Objects: {', '.join(analysis.get('objects', []))}")
            print(f"  Setting: {analysis.get('setting', 'N/A')}")
            print(f"\n✨ Magical Suggestions:")
            for i, action in enumerate(analysis.get("magical_actions", []), 1):
                print(f"  {i}. {action}")

            print("\n🪄 Generating contextual magical prompt...")
            prompt = analyzer.generate_magical_prompt(working_image_path, intensity=args.intensity)

        except Exception as e:
            print(f"⚠️  Gemini analysis failed: {e}")
            print("   Falling back to standard prompt...")
            prompt = build_harry_potter_prompt(
                photo_type=args.photo_type,
                intensity=args.intensity,
                duration=args.duration,
                custom_elements=args.custom_elements,
            )
    else:
        prompt = build_harry_potter_prompt(
            photo_type=args.photo_type,
            intensity=args.intensity,
            duration=args.duration,
            custom_elements=args.custom_elements,
        )

    print(f"\nGenerated prompt:\n{prompt}\n")
    print("=" * 70)
    print()

    # Generate video
    try:
        print("🎬 Starting video generation...\n")

        output_path = generator.generate_video(
            image_path=working_image_path,
            prompt=prompt,
            output_path=args.output,
            duration=args.duration,
            # SVD-specific kwargs
            fps=args.fps,
            motion_bucket_id=args.motion,
        )

        print()
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"Video saved to: {output_path}")

        # Create looping version if requested
        if args.loop:
            print("=" * 70)
            print("🔁 Creating seamless loop...")
            print("=" * 70)
            from src.utils.video_utils import create_looping_video

            try:
                loop_path = create_looping_video(
                    output_path,
                    crossfade_duration=args.loop_crossfade,
                )
                print(f"Looping video saved to: {loop_path}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to create looping video: {e}")
                print("   (Original non-looping video is still available)")

        print("=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Video generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
