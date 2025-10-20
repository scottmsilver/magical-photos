"""
Magical Portrait Gallery - Flask Web Application

Displays animated Harry Potter-style portraits with interaction detection.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, render_template, request, send_from_directory

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["OUTPUT_DIR"] = Path(__file__).parent.parent.parent / "output"


class Portrait:
    """Represents a magical portrait with its video and metadata."""

    def __init__(self, video_path: Path):
        self.video_path = video_path
        self.name = video_path.stem
        self.filename = video_path.name
        self.created = datetime.fromtimestamp(video_path.stat().st_mtime)
        self.is_loop = "_loop" in self.name
        # Keep version info in base_name for display (only strip _loop suffix)
        self.base_name = self.name.replace("_loop", "")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.base_name,
            "filename": self.filename,
            "video_url": f"/videos/{self.filename}",
            "created": self.created.isoformat(),
            "is_looking": False,  # Will be tracked in session
        }


def get_latest_portraits(limit: int = 10) -> List[Portrait]:
    """
    Get the most recent portrait videos.

    Args:
        limit: Maximum number of portraits to return

    Returns:
        List of Portrait objects, sorted by creation time (newest first)
    """
    output_dir = app.config["OUTPUT_DIR"]

    if not output_dir.exists():
        logger.warning(f"Output directory not found: {output_dir}")
        return []

    # Find all video files
    video_files = []
    for ext in ["*.mp4", "*.mov"]:
        video_files.extend(output_dir.glob(ext))

    # Prefer _loop versions for each unique base_name
    portraits_dict = {}
    for video_file in video_files:
        portrait = Portrait(video_file)

        # Use base_name as key (which now includes version info like v2, v3, full_magical)
        # This allows multiple versions of the same person to appear
        if portrait.base_name not in portraits_dict:
            portraits_dict[portrait.base_name] = portrait
        elif portrait.is_loop and not portraits_dict[portrait.base_name].is_loop:
            # Replace non-loop with loop version
            portraits_dict[portrait.base_name] = portrait

    # Sort by creation time, newest first
    portraits = sorted(portraits_dict.values(), key=lambda p: p.created, reverse=True)

    return portraits[:limit]


@app.route("/")
def index():
    """Main gallery page."""
    portraits = get_latest_portraits(limit=10)
    return render_template("gallery.html", portraits=portraits)


@app.route("/api/portraits")
def api_portraits():
    """API endpoint to get portrait list."""
    limit = request.args.get("limit", 10, type=int)
    portraits = get_latest_portraits(limit=limit)
    return jsonify([p.to_dict() for p in portraits])


@app.route("/api/portrait/<portrait_name>/looking", methods=["POST"])
def portrait_looking(portrait_name: str):
    """
    Record that someone is looking at a portrait.

    Future: This will trigger face recognition and personalized responses.
    """
    data = request.json
    is_looking = data.get("is_looking", False)

    logger.info(f"Portrait '{portrait_name}' - Looking: {is_looking}")

    # TODO: Trigger face recognition
    # TODO: Load personalized memories
    # TODO: Adjust animation based on viewer

    return jsonify(
        {
            "status": "success",
            "portrait": portrait_name,
            "is_looking": is_looking,
            "message": f"Portrait notices you!" if is_looking else "Portrait at rest",
        }
    )


@app.route("/videos/<path:filename>")
def serve_video(filename: str):
    """Serve video files from output directory."""
    return send_from_directory(app.config["OUTPUT_DIR"], filename)


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "portraits_count": len(get_latest_portraits()),
            "output_dir": str(app.config["OUTPUT_DIR"]),
        }
    )


def main():
    """Run the Flask development server."""
    import argparse

    parser = argparse.ArgumentParser(description="Magical Portrait Gallery")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default=5000, type=int, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info(f"Starting Magical Portrait Gallery on {args.host}:{args.port}")
    logger.info(f"Output directory: {app.config['OUTPUT_DIR']}")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
