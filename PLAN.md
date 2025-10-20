# Harry Potter Photo Frame Project Plan

## Overview
Create a Python application that transforms static photos into Harry Potter-style animated portraits using AI video generation tools (Veo 3 and Sora).

---

## Research Findings

### Available AI Video Generation Tools

#### 1. Veo 3/3.1 (Google)
- Available via Gemini API (official Python SDK)
- Excellent at preserving original photo style and quality
- Supports image-to-video with 8-second clips
- Best for subtle, realistic animations
- **Public API access available** ✓

#### 2. Sora 2 (OpenAI)
- API access is **restricted** (invitation-only as of Oct 2025)
- Available via Azure OpenAI for approved developers
- Excellent at natural portrait animations (blinking, subtle movements)
- Better for realistic physics and expressions
- **Limited availability** ✗

#### 3. Alternative Tools
- Cutout.Pro, VEED.IO, Dzine, EaseMate
- Various free/paid options
- Generally simpler but less control over output quality

### Key Techniques for Harry Potter Effect

The goal is **subtle, living portrait animations** (not dramatic movements):
- Gentle head movements, blinking, slight smiles
- Hair movement with realistic physics
- Avoid "uncanny valley" through subtlety
- Keep background static (like in HP movies)

### Best Practices

1. **Stylization over hyperrealism** - slight artistic treatment works better
2. **Subtle animations** - micro-expressions, gentle movements
3. **Short loops** (3-8 seconds) that can repeat seamlessly
4. **Motion prompts matter** - specific descriptions like "gentle breathing, occasional blink, slight smile"

---

## Implementation Plan

### Phase 1: Single Photo Prototype
1. Set up development environment (Python 3.8+)
2. Implement Veo 3 integration (primary choice - publicly accessible)
   - Install `google-generativeai` SDK
   - Set up API authentication
3. Create basic script to:
   - Accept single photo input
   - Generate subtle animation prompt (Harry Potter style)
   - Call Veo 3 API for video generation
   - Download and save result
4. Test with sample portraits

### Phase 2: Prompt Engineering
5. Develop effective prompts for Harry Potter aesthetic:
   - "Subtle portrait animation, gentle breathing, occasional blink, slight head tilt, hair moving softly in breeze, maintain regal wizarding photograph aesthetic"
6. Test variations for different photo types (formal, casual, group photos)
7. Add prompt customization options

### Phase 3: Batch Processing
8. Extend to process multiple photos from album/directory
9. Add progress tracking and error handling
10. Implement output organization (maintain original filenames, structured folders)

### Phase 4: Output & Display
11. Generate looping video files (MP4)
12. Optional: Create digital frame display interface
13. Optional: Add physical display guide (TV-based frame setup)

### Future Enhancements (Optional)
- Fallback to Sora API when/if access becomes available
- Quality comparison between different models
- Web UI for easier photo upload
- Custom frame overlays (ornate borders)
- Audio options (ambient wizarding world sounds)

---

## Technical Stack

- **Language**: Python 3.8+
- **Primary API**: Google Veo 3 via Gemini API
- **Libraries**:
  - `google-generativeai` - Veo 3 API integration
  - `requests` - HTTP requests
  - `PIL/Pillow` - Image handling
  - `python-dotenv` - Environment variable management
- **Fallback**: Azure OpenAI (Sora) if credentials available

---

## Resources & References

### Documentation
- [Google Gemini API - Video Generation](https://ai.google.dev/gemini-api/docs/video)
- [Veo 3 Colab Notebook](https://colab.research.google.com/github/GoogleCloudPlatform/generative-ai/blob/main/vision/getting-started/veo3_video_generation.ipynb)
- [AI/ML API - Veo 3 Image-to-Video](https://docs.aimlapi.com/api-references/video-models/google/veo-3-image-to-video)

### Tutorials
- [DataCamp - Veo 3 Guide](https://www.datacamp.com/tutorial/veo-3)
- [MIT Tech Review - Harry Potter Style Photos](https://www.technologyreview.com/2018/12/21/138176/machine-vision-creates-harry-potter-style-magic-photos/)

---

## Current Status

**Recommendation**: Start with **Veo 3** as it's publicly accessible and well-documented. The main limitation is that Sora 2 API access is restricted, making Veo 3 the more practical choice for immediate development.

**Next Steps**: Begin Phase 1 - Single Photo Prototype
