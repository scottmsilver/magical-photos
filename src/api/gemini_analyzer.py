"""
Gemini Image Analyzer for contextual video generation.

This module uses Gemini Vision to analyze images and generate
contextual prompts for magical animations.
"""

import logging
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Analyzer for understanding image content using Gemini Vision."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini analyzer.

        Args:
            api_key: Google API key
            model_name: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        logger.info(f"GeminiAnalyzer initialized with model: {model_name}")

    def analyze_for_animation(self, image_path: str) -> dict:
        """
        Analyze image to identify objects and suggest magical animations.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary containing:
            - people: List of people descriptions
            - objects: List of interactive objects in the scene
            - setting: Description of the setting/background
            - magical_suggestions: List of suggested magical interactions
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Analyzing image for animation potential: {image_path}")

        # Upload image file first
        uploaded_file = self.client.files.upload(file=str(image_file))
        logger.debug(f"Uploaded file: {uploaded_file.name}")

        # Create analysis prompt
        analysis_prompt = """Analyze this photograph for creating a magical Harry Potter-style animated portrait.

Please identify:

1. PEOPLE: Describe each person (appearance, clothing, position, expression)
2. OBJECTS: List specific objects they could interact with (in hands, nearby, in background)
3. SETTING: Describe the location/environment
4. MAGICAL INTERACTIONS: Suggest 5-7 creative magical actions ONLY using objects already in the photo:
   - Making existing objects glow, float, or move
   - Existing objects transforming or changing
   - Objects responding to gestures
   - Things already in the photo coming alive or animating
   - People interacting with each other (whispering, gesturing, glancing)
   - People turning to face the camera and speaking/gesturing to the viewer
   - People acknowledging the camera viewer's presence
   - IMPORTANT: Do NOT suggest adding new objects, creatures, or elements that aren't in the photo

Be specific about which EXISTING objects they should interact with and how people interact with each other and the viewer!

Format your response as:
PEOPLE: [descriptions]
OBJECTS: [list specific items]
SETTING: [description]
MAGICAL_ACTIONS: [numbered list of 5-7 specific magical interactions]"""

        try:
            # Generate analysis
            response = self.client.models.generate_content(
                model=self.model_name, contents=[analysis_prompt, uploaded_file]
            )

            analysis_text = response.text
            logger.debug(f"Gemini analysis:\n{analysis_text}")

            # Parse the response
            parsed = self._parse_analysis(analysis_text)
            logger.info(f"Identified {len(parsed.get('objects', []))} interactive objects")

            return parsed

        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            raise

    def generate_magical_prompt(self, image_path: str, intensity: str = "moderate") -> str:
        """
        Generate a contextual magical animation prompt based on image analysis.

        Args:
            image_path: Path to image file
            intensity: Animation intensity (subtle, moderate, dramatic)

        Returns:
            Customized animation prompt
        """
        # Analyze the image
        analysis = self.analyze_for_animation(image_path)

        # Upload image for prompt generation
        image_file = Path(image_path)
        uploaded_file = self.client.files.upload(file=str(image_file))

        prompt_request = f"""Based on this image analysis, create a detailed animation prompt for Veo video generation:

ANALYSIS:
People: {analysis.get('people', 'person in photo')}
Objects: {analysis.get('objects', 'various objects')}
Setting: {analysis.get('setting', 'scene')}
Suggested magical actions: {analysis.get('magical_actions', [])}

Create a {intensity} animation prompt that:
1. Is in BLACK AND WHITE (monochrome, vintage photograph aesthetic)
2. NO FRAMES or BORDERS - photograph only
3. At least one person ALWAYS looking directly at camera throughout
4. Includes 2-3 of the suggested magical interactions with specific objects
5. If multiple people are present, include interactions between them (glances, gestures, whispers)
6. Consider having someone turn to face the camera and gesture/speak to the viewer
7. People can acknowledge the viewer's presence as if aware they're being watched
8. Seamlessly loops from end to beginning
9. Keeps background mostly static
10. 8 seconds duration
11. CRITICAL: DO NOT add any new objects or creatures that aren't already visible in the photo
12. ONLY animate or make magical the objects, people, and elements that are ALREADY in the photo
13. Objects can move, glow, transform, or interact, but nothing new should appear

Write ONLY the animation prompt, nothing else. Make it specific and magical!"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=[prompt_request, uploaded_file]
            )

            prompt = response.text.strip()
            logger.info("Generated contextual magical prompt")
            logger.debug(f"Prompt: {prompt}")

            return prompt

        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            raise

    def _parse_analysis(self, analysis_text: str) -> dict:
        """
        Parse Gemini's analysis response into structured data.

        Args:
            analysis_text: Raw text response from Gemini

        Returns:
            Parsed dictionary with people, objects, setting, magical_actions
        """
        result = {"people": "", "objects": [], "setting": "", "magical_actions": []}

        lines = analysis_text.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if line.startswith("PEOPLE:"):
                current_section = "people"
                result["people"] = line.replace("PEOPLE:", "").strip()
            elif line.startswith("OBJECTS:"):
                current_section = "objects"
                objects_text = line.replace("OBJECTS:", "").strip()
                if objects_text:
                    result["objects"] = [obj.strip() for obj in objects_text.split(",")]
            elif line.startswith("SETTING:"):
                current_section = "setting"
                result["setting"] = line.replace("SETTING:", "").strip()
            elif line.startswith("MAGICAL_ACTIONS:") or line.startswith("MAGICAL ACTIONS:"):
                current_section = "magical_actions"
            elif current_section == "magical_actions" and (line[0].isdigit() or line.startswith("-")):
                # Extract action (remove numbering)
                action = line.lstrip("0123456789.-) ").strip()
                if action:
                    result["magical_actions"].append(action)
            elif current_section and line:
                # Continue previous section
                if current_section == "people":
                    result["people"] += " " + line
                elif current_section == "setting":
                    result["setting"] += " " + line

        return result
