"""
Prompt builder for Harry Potter style animated portraits.

This module generates prompts optimized for creating subtle,
magical portrait animations reminiscent of Harry Potter photographs.
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class AnimationIntensity(Enum):
    """Animation intensity levels."""

    SUBTLE = "subtle"
    MODERATE = "moderate"
    DRAMATIC = "dramatic"


class PhotoType(Enum):
    """Types of photos to animate."""

    PORTRAIT = "portrait"
    GROUP = "group"
    LANDSCAPE = "landscape"
    PET = "pet"
    FORMAL = "formal"


class PromptBuilder:
    """Builder for Harry Potter style animation prompts."""

    # Base components for HP-style animations
    BASE_QUALITIES = [
        "vintage wizarding portrait aesthetic",
        "seamlessly looping animation",
        "maintains original photo composition and colors",
        "cinematic quality with rich detail",
    ]

    # Always include these - subject maintaining eye contact
    CORE_REQUIREMENTS = [
        "at least one person looking directly at camera throughout",
        "maintaining steady eye contact with viewer",
    ]

    SUBTLE_MOVEMENTS = [
        "gentle breathing",
        "occasional natural blink while maintaining gaze",
        "slight knowing smile forming",
        "eyebrows raising expressively",
        "subtle head tilt or nod of acknowledgment",
        "shoulders shifting slightly",
        "chin lifting thoughtfully",
        "small amused expression",
        "sly sideways glance at viewer",
        "coy smile appearing briefly",
        "eyes narrowing with mischief",
    ]

    MODERATE_MOVEMENTS = [
        "slow turn to face camera directly",
        "gentle wave or greeting gesture",
        "crossing or uncrossing arms",
        "adjusting glasses or clothing",
        "touching face thoughtfully",
        "leaning forward with interest",
        "amused reaction to something off-camera",
        "finger to lips in conspiratorial gesture",
        "hand through hair casually",
        "playful wink directed at viewer",
        "secretive glance around before looking back",
        "beckoning gesture to viewer",
    ]

    DRAMATIC_MOVEMENTS = [
        "animated conversation or storytelling gestures",
        "laughing or reacting expressively",
        "dramatic arm movements",
        "pointing at something with enthusiasm",
        "hands gesturing emphatically",
        "surprised or delighted reactions",
        "theatrical magical gesture or flourish",
        "exaggerated wink or knowing look",
        "breaking into sudden unexpected laughter",
        "challenging stare directly at viewer",
        "beckoning viewer closer conspiratorially",
    ]

    # Emotional expressions for more dynamic portraits
    EMOTIONAL_EXPRESSIONS = [
        "expression shifting from serious to amused",
        "eyebrows raising in surprise or recognition",
        "subtle frown forming then relaxing",
        "corners of mouth twitching with suppressed smile",
        "eyes widening with sudden interest",
        "skeptical look crossing their face",
        "flash of anger or annoyance in eyes",
        "moment of thoughtful contemplation",
        "recognition dawning across their features",
        "trying to maintain composure but smiling through",
    ]

    # Furtive interactions with the viewer
    VIEWER_INTERACTIONS = [
        "sly knowing glance directly at camera",
        "coy smile as if sharing a secret",
        "quick furtive look around before making eye contact",
        "conspiratorial lean toward viewer",
        "subtle nod of acknowledgment to viewer",
        "raising eyebrows meaningfully at camera",
        "slight smirk directed at viewer",
        "beckoning gesture inviting viewer closer",
        "putting finger to lips as if shushing viewer",
        "quick playful wink at camera",
        "looking away then back with knowing expression",
        "skeptical or challenging look at viewer",
    ]

    # Physical object interaction movements
    OBJECT_INTERACTIONS = [
        "reaching out and grabbing a nearby object",
        "picking up an item and examining it with wonder",
        "holding an object up and making it glow magically",
        "conjuring sparkles or light from their hands",
        "making an object levitate with a hand gesture",
        "touching an object and causing it to transform",
        "pulling something from their pocket or clothing",
        "waving hand to create magical wisps or smoke",
        "extending hand causing magical energy to emanate",
        "gesturing at object making it respond magically",
        "tossing and catching a small glowing object",
        "creating magical symbols or shapes in the air",
    ]

    # Multi-person interaction movements
    GROUP_INTERACTIONS = [
        "subjects glancing at each other knowingly",
        "one whispering to another while one maintains camera contact",
        "gentle nudging or touching shoulders",
        "sharing a quiet laugh together",
        "one pointing something out to the other",
        "exchanging meaningful glances",
        "playful interaction between subjects",
        "conspiratorial looks between people",
        "one person reacting to another's gesture",
        "subjects appearing to converse quietly",
    ]

    ENVIRONMENTAL_EFFECTS = [
        "subtle lighting shifts creating depth",
        "gentle movement in hair or fabric",
        "atmospheric depth and natural shadows",
        "vintage photograph character",
        "classic portrait aesthetic",
    ]

    def __init__(self, duration: int = 8):
        """
        Initialize prompt builder.

        Args:
            duration: Video duration in seconds (default: 8)
        """
        self.duration = duration
        logger.debug(f"PromptBuilder initialized with duration: {duration}s")

    def build_prompt(
        self,
        photo_type: PhotoType = PhotoType.PORTRAIT,
        intensity: AnimationIntensity = AnimationIntensity.SUBTLE,
        custom_elements: Optional[list[str]] = None,
        include_audio: bool = False,
    ) -> str:
        """
        Build a Harry Potter style animation prompt.

        Args:
            photo_type: Type of photo being animated
            intensity: Animation intensity level
            custom_elements: Optional list of custom animation elements
            include_audio: Whether to include audio suggestions

        Returns:
            Formatted prompt string for video generation
        """
        prompt_parts = []

        # Add photo type specific intro
        prompt_parts.append(self._get_photo_intro(photo_type))

        # Add base qualities (includes black and white, no frames)
        prompt_parts.append(", ".join(self.BASE_QUALITIES))

        # ALWAYS add core requirements (direct camera gaze)
        prompt_parts.append(", ".join(self.CORE_REQUIREMENTS))

        # Add movements based on intensity
        movements = self._get_movements(intensity, photo_type)
        if custom_elements:
            movements.extend(custom_elements)
        prompt_parts.append(", ".join(movements))

        # Add environmental effects for vintage feel
        if intensity != AnimationIntensity.DRAMATIC:
            prompt_parts.append(", ".join(self.ENVIRONMENTAL_EFFECTS[:2]))

        # Add duration constraint
        prompt_parts.append(f"{self.duration} seconds duration")

        # Add stability and looping instructions
        prompt_parts.append(
            "smooth seamless loop from end back to beginning, "
            "keep background static, "
            "preserve original photograph character and quality"
        )

        # Add audio if requested
        if include_audio:
            prompt_parts.append("ambient magical sound atmosphere")

        prompt = ". ".join(prompt_parts) + "."

        logger.debug(f"Built prompt: {prompt[:100]}...")
        return prompt

    def _get_photo_intro(self, photo_type: PhotoType) -> str:
        """
        Get introductory text based on photo type.

        Args:
            photo_type: Type of photo

        Returns:
            Introductory prompt text
        """
        intros = {
            PhotoType.PORTRAIT: "Animate this as a living wizarding portrait photograph",
            PhotoType.GROUP: "Animate this as a living wizarding group photograph with subjects interacting",
            PhotoType.LANDSCAPE: "Transform this into a living magical scene",
            PhotoType.PET: "Bring this to life as a magical creature portrait",
            PhotoType.FORMAL: "Animate as a distinguished wizarding portrait",
        }
        return intros.get(photo_type, intros[PhotoType.PORTRAIT])

    def _get_movements(self, intensity: AnimationIntensity, photo_type: PhotoType = PhotoType.PORTRAIT) -> list[str]:
        """
        Get movement descriptions based on intensity and photo type.

        Args:
            intensity: Animation intensity level
            photo_type: Type of photo (to add group interactions if GROUP)

        Returns:
            List of movement descriptions
        """
        movements = []

        # Get base movements based on intensity
        if intensity == AnimationIntensity.SUBTLE:
            movements = self.SUBTLE_MOVEMENTS[:3]  # Use first 3 subtle movements
            # Add subtle viewer interactions and emotions
            movements.extend(self.VIEWER_INTERACTIONS[:2])
            movements.extend(self.EMOTIONAL_EXPRESSIONS[:2])
        elif intensity == AnimationIntensity.MODERATE:
            movements = self.MODERATE_MOVEMENTS[:3]  # Use first 3 moderate movements
            # Add moderate viewer interactions and emotions
            movements.extend(self.VIEWER_INTERACTIONS[2:5])
            movements.extend(self.EMOTIONAL_EXPRESSIONS[2:5])
        else:  # DRAMATIC
            movements = self.DRAMATIC_MOVEMENTS[:4]  # Use first 4 dramatic movements
            # Add dramatic viewer interactions and emotions
            movements.extend(self.VIEWER_INTERACTIONS[5:8])
            movements.extend(self.EMOTIONAL_EXPRESSIONS[5:8])

        # Add group interactions if it's a group photo
        if photo_type == PhotoType.GROUP:
            movements.extend(self.GROUP_INTERACTIONS[:3])

        return movements

    def build_simple_prompt(self, description: str) -> str:
        """
        Build a simple custom prompt with HP styling.

        Args:
            description: Simple description of desired animation

        Returns:
            Formatted prompt string
        """
        return (
            f"Animate this photograph as a magical Harry Potter style portrait. "
            f"{description}. "
            f"Maintain cinematic quality, magical atmosphere, "
            f"keep background static, preserve original photo details. "
            f"{self.duration} seconds duration."
        )


def build_harry_potter_prompt(
    photo_type: str = "portrait",
    intensity: str = "subtle",
    duration: int = 8,
    custom_elements: Optional[list[str]] = None,
) -> str:
    """
    Convenience function to build Harry Potter style prompt.

    Args:
        photo_type: Type of photo (portrait, group, landscape, pet, formal)
        intensity: Animation intensity (subtle, moderate, dramatic)
        duration: Video duration in seconds
        custom_elements: Optional custom animation elements

    Returns:
        Formatted prompt string

    Example:
        >>> prompt = build_harry_potter_prompt("portrait", "subtle", 5)
        >>> print(prompt)
        Animate this portrait as a magical Harry Potter photograph...
    """
    try:
        photo_enum = PhotoType[photo_type.upper()]
    except KeyError:
        logger.warning(f"Invalid photo_type: {photo_type}, using PORTRAIT")
        photo_enum = PhotoType.PORTRAIT

    try:
        intensity_enum = AnimationIntensity[intensity.upper()]
    except KeyError:
        logger.warning(f"Invalid intensity: {intensity}, using SUBTLE")
        intensity_enum = AnimationIntensity.SUBTLE

    builder = PromptBuilder(duration=duration)
    return builder.build_prompt(photo_type=photo_enum, intensity=intensity_enum, custom_elements=custom_elements)
