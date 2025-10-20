"""
Video utilities for post-processing generated videos.

This module provides utilities for creating looping videos,
crossfading, and other video enhancements.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def create_looping_video(
    input_path: str,
    output_path: Optional[str] = None,
    crossfade_duration: float = 0.5,
    num_loops: int = 1,
) -> str:
    """
    Create a seamlessly looping video using crossfade.

    Args:
        input_path: Path to input video
        output_path: Path for output video (default: adds _loop suffix)
        crossfade_duration: Duration of crossfade in seconds (default: 0.5)
        num_loops: Number of times to loop (default: 1, meaning 2 total plays)

    Returns:
        Path to looping video

    Raises:
        FileNotFoundError: If input video doesn't exist
        RuntimeError: If ffmpeg processing fails
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    # Generate output path
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_loop{input_file.suffix}")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating looping video with {crossfade_duration}s crossfade...")

    try:
        # Get video duration
        duration_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_file),
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        logger.debug(f"Video duration: {duration}s")

        # Calculate crossfade timing
        fade_start = duration - crossfade_duration

        # Build the loop with crossfade
        # For a seamless loop, we overlap the end with the beginning using crossfade
        filter_complex = (
            f"[0:v]split[v1][v2];"
            f"[v1]trim=0:{fade_start},setpts=PTS-STARTPTS[main];"
            f"[v2]trim={fade_start}:{duration},setpts=PTS-STARTPTS[fade_out];"
            f"[0:v]trim=0:{crossfade_duration},setpts=PTS-STARTPTS[fade_in];"
            f"[fade_out][fade_in]xfade=transition=fade:duration={crossfade_duration}:offset=0[xf];"
            f"[main][xf]concat=n=2:v=1:a=0"
        )

        # If multiple loops requested, repeat the pattern
        if num_loops > 1:
            filter_complex += f"[base];[base]loop={num_loops}:1:0"

        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            str(input_file),
            "-filter_complex",
            filter_complex,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-y",
            str(output_file),
        ]

        logger.debug(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)

        logger.info(f"Looping video created: {output_path}")
        return str(output_file)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg error: {error_msg}")
        raise RuntimeError(f"Failed to create looping video: {error_msg}") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def create_simple_loop(input_path: str, output_path: Optional[str] = None, num_loops: int = 3) -> str:
    """
    Create a simple repeating loop without crossfade.

    Args:
        input_path: Path to input video
        output_path: Path for output video (default: adds _loop suffix)
        num_loops: Number of times to repeat the video (default: 3)

    Returns:
        Path to looped video

    Raises:
        FileNotFoundError: If input video doesn't exist
        RuntimeError: If ffmpeg processing fails
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    # Generate output path
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_loop{input_file.suffix}")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating simple loop ({num_loops} repetitions)...")

    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-stream_loop",
            str(num_loops - 1),
            "-i",
            str(input_file),
            "-c",
            "copy",
            "-y",
            str(output_file),
        ]

        logger.debug(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)

        logger.info(f"Looped video created: {output_path}")
        return str(output_file)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg error: {error_msg}")
        raise RuntimeError(f"Failed to create looped video: {error_msg}") from e
