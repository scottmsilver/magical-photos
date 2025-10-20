#!/usr/bin/env python3
"""Test script to see Gemini analysis output."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api.gemini_analyzer import GeminiAnalyzer
from src.utils.config import Config

# Load config
config = Config.from_env()

# Create analyzer
analyzer = GeminiAnalyzer(api_key=config.google_api_key)

# Analyze image
print("=" * 70)
print("🔮 Gemini Image Analysis")
print("=" * 70)

analysis = analyzer.analyze_for_animation("joy.jpg")

print("\n📊 ANALYSIS RESULTS:")
print(f"\nPEOPLE:\n{analysis.get('people', 'N/A')}")
print(f"\nOBJECTS:\n{', '.join(analysis.get('objects', []))}")
print(f"\nSETTING:\n{analysis.get('setting', 'N/A')}")
print(f"\n✨ MAGICAL ACTION SUGGESTIONS:")
for i, action in enumerate(analysis.get("magical_actions", []), 1):
    print(f"{i}. {action}")

print("\n" + "=" * 70)
print("🪄 Generating Contextual Prompt")
print("=" * 70)

prompt = analyzer.generate_magical_prompt("joy.jpg", intensity="moderate")
print(f"\nGENERATED PROMPT:\n{prompt}")
print("\n" + "=" * 70)
