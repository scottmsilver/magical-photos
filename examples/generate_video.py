#!/usr/bin/env python3
"""
Generate Harry Potter style animated video from a photo using Veo 3.1.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prompts.prompt_builder import build_harry_potter_prompt
from src.utils.config import Config, setup_logging
from src.video_generator import VideoGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate Harry Potter style animated video from photo using Veo 3.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (uses Gemini image analysis by default)
  %(prog)s portrait.jpg

  # Custom settings
  %(prog)s portrait.jpg --intensity dramatic --output my_video.mp4

  # Disable Gemini and use standard prompt builder
  %(prog)s portrait.jpg --no-gemini-prompt
        """,
    )

    parser.add_argument("image", help="Path to input image")

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
        "--no-loop",
        action="store_true",
        help="Disable seamless looping video with crossfade (default: False, looping is enabled by default)",
    )

    parser.add_argument(
        "--loop-crossfade",
        type=float,
        default=0.5,
        help="Crossfade duration for looping in seconds (default: 0.5)",
    )

    parser.add_argument(
        "--use-veo-loop-frames",
        action="store_true",
        help="Use Veo's first/last frame feature for perfect looping (Veo backend only, default: False)",
    )

    parser.add_argument(
        "--no-gemini-prompt",
        action="store_true",
        help="Disable Gemini image analysis and use standard prompt builder instead (default: False, Gemini is used by default)",
    )

    parser.add_argument(
        "--no-bw",
        action="store_true",
        help="Disable black & white post-processing, keep color video (default: False, B&W conversion is enabled by default)",
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

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show all prompts and analysis but don't generate video (default: False)",
    )

    args = parser.parse_args()

    # Load config
    config = Config.from_env()
    setup_logging(config)

    print("=" * 70)
    print("🧙 Harry Potter Photo Frame Generator")
    print("=" * 70)
    print(f"Backend: Veo 3.1")
    print(f"Image: {args.image}")
    print(f"Type: {args.photo_type}")
    print(f"Intensity: {args.intensity}")
    print(f"Duration: {args.duration}s")
    print("=" * 70)
    print()

    # Initialize video generator
    try:
        generator = VideoGenerator(google_api_key=config.google_api_key)

        # Show backend info
        info = generator.get_backend_info()
        print("Backend Information:")
        print(f"  Backend: {info['backend']}")
        print(f"  Model: {info['model']}")
        print(f"  Veo available: {'✅' if info['veo_available'] else '❌'}")
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

    # Build prompt (use Gemini by default unless --no-gemini-prompt is specified)
    if not args.no_gemini_prompt:
        print("🔮 Using Gemini to analyze image and generate contextual prompt...")
        print("=" * 70)

        from src.api.gemini_analyzer import GeminiAnalyzer

        try:
            analyzer = GeminiAnalyzer(api_key=config.google_api_key)

            # Show the analysis prompt being sent
            print("\n📝 Analysis Prompt Being Sent to Gemini:")
            print("-" * 70)
            analysis_prompt = """Analyze this photograph for creating a magical Harry Potter-style animated portrait.

Please identify:

1. PEOPLE: Describe each person (appearance, clothing, position, expression)
2. OBJECTS: List specific objects they could interact with (in hands, nearby, in background)
3. SETTING: Describe the location/environment
4. MAGICAL INTERACTIONS: Suggest 5-7 SUBTLE creative magical actions ONLY using objects already in the photo:
   - SUBTLE movements: objects gently floating, swaying, or shifting position
   - Existing objects subtly transforming or changing
   - Objects responding to gestures in understated ways
   - Things already in the photo coming alive with MINIMAL animation
   - People interacting with each other (whispering, gesturing, glancing, small smiles)
   - People turning to face the camera and speaking/gesturing to the viewer
   - People acknowledging the camera viewer's presence with subtle expressions
   - AVOID: Magical dust, sparkles, glowing lights, obvious magical effects, wisps, or auras
   - IMPORTANT: Do NOT suggest adding new objects, creatures, or elements that aren't in the photo
   - EMPHASIS: Keep effects vintage and understated, like old magical photographs

Be specific about which EXISTING objects they should interact with and how people interact with each other and the viewer!

Format your response as:
PEOPLE: [descriptions]
OBJECTS: [list specific items]
SETTING: [description]
MAGICAL_ACTIONS: [numbered list of 5-7 specific SUBTLE magical interactions]"""
            print(analysis_prompt)
            print("-" * 70)

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
            print("\n📝 Prompt Generation Request Being Sent to Gemini:")
            print("-" * 70)
            prompt_request = f"""Based on this image analysis, create a detailed animation prompt for Veo video generation.

ANALYSIS:
People: {analysis.get('people', 'person in photo')}
Objects: {analysis.get('objects', 'various objects')}
Setting: {analysis.get('setting', 'scene')}
Suggested magical actions: {analysis.get('magical_actions', [])}

IMPORTANT INSTRUCTION STYLE:
- Write as SPECIFIC INSTRUCTIONS to a video generator, not a general description
- Use definite articles: "THE blonde woman", "THE man in the blue shirt", "THE book on the table", "THE dog", "THE cat"
- NOT: "a person smiles" but "the blonde woman smiles at the camera"
- NOT: "someone waves" but "the tall man in the grey suit waves his right hand"
- Be CONCRETE and SPECIFIC about who does what, referencing their appearance from the analysis
- CRITICAL: MAXIMIZE interactions between ALL characters (people, animals, pets, etc.)
- If there are multiple people/animals, they MUST interact frequently - looking at each other, touching, gesturing, reacting
- Animals should interact with people and other animals
- Create a sense of CONNECTION and RELATIONSHIP between all subjects

Create a {args.intensity} animation prompt with these requirements:
1. Maintains the original photo's colors and aesthetic - vintage photograph style
2. NO FRAMES or BORDERS - photograph only
3. Use SPECIFIC references: "the [hair color] [man/woman] with [clothing/feature]" does [action]
4. At least one person ALWAYS looking directly at camera throughout - specify WHICH person by their appearance
5. Include 2-3 of the suggested magical interactions - be specific about WHICH objects and WHO interacts with them
6. MANDATORY: If multiple people/animals/characters are present, they MUST interact extensively:
   - "the woman in red leans toward the bearded man and whispers in his ear"
   - "the golden retriever nuzzles against the man's leg while he pets its head"
   - "the woman glances at the man, who smiles back at her"
   - "the cat rubs against the child's arm as the child reaches to pet it"
   - Specify WHO does WHAT to WHOM using their specific descriptions
7. Describe viewer interactions specifically: "the blonde woman turns her gaze to the camera and smirks"
8. Balance interactions: mix character-to-character AND character-to-viewer interactions
9. Seamlessly loops from end to beginning
10. Keeps background mostly static
11. 8 seconds duration
12. CRITICAL: DO NOT add any new objects or creatures that aren't already visible in the photo
13. ONLY animate or make magical the objects, people, and elements that are ALREADY in the photo
14. Objects can move subtly, shift position, or interact, but nothing new should appear
15. SUBTLETY IS KEY: Avoid magical dust, sparkles, glowing lights, wisps, auras, or obvious magical effects
16. Keep all effects UNDERSTATED and VINTAGE - like subtle movements in an old magical photograph
17. Focus on expressions, gestures, small movements, and natural interactions rather than flashy effects

Write ONLY the animation prompt as specific video generation instructions. Use "the [specific person]" language throughout!"""
            print(prompt_request)
            print("-" * 70)
            print()

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

    print(f"\n📜 Final Prompt for Veo:")
    print("=" * 70)
    print(prompt)
    print("=" * 70)
    print()

    # Check for dry-run mode
    if args.dry_run:
        print("=" * 70)
        print("🔍 DRY RUN MODE - Skipping video generation")
        print("=" * 70)
        print("\nAll prompts and analysis shown above.")
        print("Remove --dry-run flag to actually generate the video.")
        return 0

    # Generate video with retry logic for "No video in response" errors
    max_retries = 3
    retry_delay = 60  # Wait 1 minute between retries

    try:
        print("🎬 Starting video generation...\n")

        for attempt in range(max_retries):
            try:
                output_path = generator.generate_video(
                    image_path=working_image_path,
                    prompt=prompt,
                    output_path=args.output,
                    duration=args.duration,
                    use_loop_frames=args.use_veo_loop_frames,
                )
                break  # Success!
            except Exception as e:
                error_msg = str(e)
                if "No video in response" in error_msg and attempt < max_retries - 1:
                    print(f"\n⚠️  Veo returned no video (attempt {attempt + 1}/{max_retries})")
                    print(f"   This is a known Veo API issue - retrying in {retry_delay} seconds...")
                    print("=" * 70)
                    time.sleep(retry_delay)
                else:
                    raise  # Re-raise if not retryable or last attempt

        print()
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"✅ Color video saved to: {output_path}")

        # Create B&W version by default (unless --no-bw)
        bw_output = None
        if not args.no_bw:
            print("=" * 70)
            print("🎨 Creating black & white version...")
            print("=" * 70)
            from src.utils.video_utils import convert_video_to_bw

            try:
                bw_output = output_path.replace(".mp4", "_bw.mp4")
                convert_video_to_bw(output_path, bw_output, method=args.bw_method)
                print(f"✅ B&W video saved to: {bw_output}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to create B&W version: {e}")
                print("   (Color video is still available)")
                bw_output = None

        # Create looping versions (unless --no-loop)
        if not args.no_loop:
            print("=" * 70)
            print("🔁 Creating seamless loops...")
            print("=" * 70)
            from src.utils.video_utils import create_looping_video

            # Loop the color version
            try:
                color_loop_path = create_looping_video(
                    output_path,
                    output_path=output_path.replace(".mp4", "_loop.mp4"),
                    crossfade_duration=args.loop_crossfade,
                )
                print(f"✅ Color looping video saved to: {color_loop_path}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to create color looping video: {e}")

            # Loop the B&W version if it was created
            if bw_output:
                try:
                    bw_loop_path = create_looping_video(
                        bw_output,
                        output_path=bw_output.replace(".mp4", "_loop.mp4"),
                        crossfade_duration=args.loop_crossfade,
                    )
                    print(f"✅ B&W looping video saved to: {bw_loop_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to create B&W looping video: {e}")

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
