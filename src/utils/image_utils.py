"""
Image utilities for preprocessing images before video generation.

This module provides utilities for resizing, cropping, and padding images
to match target aspect ratios without distortion.
"""

import logging
from pathlib import Path
from typing import Literal, Tuple

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def get_aspect_ratio_dimensions(aspect_ratio: str, base_size: int = 1280) -> Tuple[int, int]:
    """
    Get width and height for a given aspect ratio.

    Args:
        aspect_ratio: Aspect ratio string (e.g., "16:9", "9:16", "1:1", "4:3")
        base_size: Base size for calculation (default: 1280)

    Returns:
        Tuple of (width, height)
    """
    ratios = {
        "16:9": (16, 9),
        "9:16": (9, 16),
        "4:3": (4, 3),
        "3:4": (3, 4),
        "1:1": (1, 1),
    }

    if aspect_ratio not in ratios:
        raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")

    w_ratio, h_ratio = ratios[aspect_ratio]

    # Calculate dimensions based on the aspect ratio
    if w_ratio >= h_ratio:
        # Landscape or square
        width = base_size
        height = int(base_size * h_ratio / w_ratio)
    else:
        # Portrait
        height = base_size
        width = int(base_size * w_ratio / h_ratio)

    return width, height


def fit_image_to_aspect_ratio(
    input_path: str,
    target_aspect_ratio: str,
    output_path: str = None,
    mode: Literal["pad", "crop"] = "pad",
    background_color: Tuple[int, int, int] = (0, 0, 0),
) -> str:
    """
    Fit an image to a target aspect ratio using padding or cropping.

    Args:
        input_path: Path to input image
        target_aspect_ratio: Target aspect ratio (e.g., "16:9", "9:16")
        output_path: Path for output image (default: adds _fitted suffix)
        mode: "pad" to add letterboxing, "crop" to intelligently crop
        background_color: RGB color for padding (default: black)

    Returns:
        Path to processed image

    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If aspect ratio is unsupported
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Generate output path
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_fitted_{target_aspect_ratio.replace(':', 'x')}.jpg")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Fitting image to {target_aspect_ratio} using {mode} mode...")

    # Open image
    with Image.open(input_file) as img:
        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        source_width, source_height = img.size
        source_aspect = source_width / source_height

        # Calculate target dimensions
        target_width, target_height = get_aspect_ratio_dimensions(
            target_aspect_ratio, base_size=max(source_width, source_height)
        )
        target_aspect = target_width / target_height

        logger.debug(
            f"Source: {source_width}x{source_height} (aspect: {source_aspect:.2f}), "
            f"Target: {target_width}x{target_height} (aspect: {target_aspect:.2f})"
        )

        if mode == "pad":
            # PAD MODE: Add letterboxing/pillarboxing to preserve entire image
            result = pad_to_aspect_ratio(img, target_width, target_height, background_color)

        elif mode == "crop":
            # CROP MODE: Center crop to target aspect ratio
            result = crop_to_aspect_ratio(img, target_aspect)

        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'pad' or 'crop'")

        # Save the result
        result.save(output_file, "JPEG", quality=95)
        logger.info(f"Fitted image saved to: {output_path}")

    return str(output_file)


def pad_to_aspect_ratio(
    img: Image.Image,
    target_width: int,
    target_height: int,
    background_color: Tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """
    Add padding to image to match target dimensions without cropping.

    Args:
        img: PIL Image to pad
        target_width: Target width
        target_height: Target height
        background_color: RGB color for padding

    Returns:
        Padded PIL Image
    """
    source_width, source_height = img.size
    source_aspect = source_width / source_height
    target_aspect = target_width / target_height

    # Calculate scaling to fit image within target dimensions
    if source_aspect > target_aspect:
        # Image is wider - scale to fit width
        scale = target_width / source_width
    else:
        # Image is taller - scale to fit height
        scale = target_height / source_height

    new_width = int(source_width * scale)
    new_height = int(source_height * scale)

    # Resize image
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create canvas with target dimensions
    canvas = Image.new("RGB", (target_width, target_height), background_color)

    # Center the resized image on canvas
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    canvas.paste(resized, (x_offset, y_offset))

    logger.debug(f"Padded {source_width}x{source_height} to {target_width}x{target_height}")
    return canvas


def crop_to_aspect_ratio(img: Image.Image, target_aspect: float) -> Image.Image:
    """
    Center crop image to target aspect ratio.

    Args:
        img: PIL Image to crop
        target_aspect: Target aspect ratio (width/height)

    Returns:
        Cropped PIL Image
    """
    source_width, source_height = img.size
    source_aspect = source_width / source_height

    if source_aspect > target_aspect:
        # Image is wider - crop width
        new_width = int(source_height * target_aspect)
        new_height = source_height
        x_offset = (source_width - new_width) // 2
        y_offset = 0
    else:
        # Image is taller - crop height
        new_width = source_width
        new_height = int(source_width / target_aspect)
        x_offset = 0
        y_offset = (source_height - new_height) // 2

    cropped = img.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))
    logger.debug(f"Cropped from {source_width}x{source_height} to {new_width}x{new_height}")
    return cropped


def convert_to_black_and_white(
    input_path: str,
    output_path: str = None,
    method: Literal["grayscale", "high_contrast", "vintage"] = "high_contrast",
) -> str:
    """
    Convert image to black and white.

    Args:
        input_path: Path to input image
        output_path: Path for output image (default: adds _bw suffix)
        method: Conversion method:
            - "grayscale": Simple grayscale conversion
            - "high_contrast": Enhanced contrast B&W (recommended)
            - "vintage": Vintage photograph look with slight sepia tint then B&W

    Returns:
        Path to black and white image

    Raises:
        FileNotFoundError: If input image doesn't exist
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Generate output path
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_bw.jpg")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting to black and white using {method} method...")

    with Image.open(input_file) as img:
        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        if method == "grayscale":
            # Simple grayscale
            bw_img = img.convert("L").convert("RGB")

        elif method == "high_contrast":
            # Enhanced contrast B&W (classic portrait style)
            from PIL import ImageEnhance

            # Convert to grayscale
            bw_img = img.convert("L")

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(bw_img)
            bw_img = enhancer.enhance(1.3)  # Increase contrast by 30%

            # Slight brightness adjustment
            enhancer = ImageEnhance.Brightness(bw_img)
            bw_img = enhancer.enhance(1.05)

            # Convert back to RGB for compatibility
            bw_img = bw_img.convert("RGB")

        elif method == "vintage":
            # Vintage photograph look
            from PIL import ImageEnhance

            # Convert to grayscale
            bw_img = img.convert("L")

            # Add slight grain effect by reducing sharpness
            enhancer = ImageEnhance.Sharpness(bw_img)
            bw_img = enhancer.enhance(0.8)

            # Adjust contrast for vintage look
            enhancer = ImageEnhance.Contrast(bw_img)
            bw_img = enhancer.enhance(1.2)

            # Convert to RGB
            bw_img = bw_img.convert("RGB")

        else:
            raise ValueError(f"Unknown method: {method}")

        # Save result
        bw_img.save(output_file, "JPEG", quality=95)
        logger.info(f"Black and white image saved to: {output_path}")

    return str(output_file)
