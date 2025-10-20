# Harry Potter Photo Frame Generator 🪄

Transform static photos into magical Harry Potter-style animated portraits using Google's Veo 3.1 and Gemini Vision AI.

## ✨ Features

### 🎨 **Multiple Animation Backends**
- **Veo 3.1** (Cloud): High-quality video generation with Google's latest AI model
- **Stable Video Diffusion** (Local): GPU-based generation for offline use
- **Auto Mode**: Tries Veo first, falls back to SVD

### 🧙 **Intelligent Contextual Magic**
- **Gemini Vision Analysis**: Automatically identifies people, objects, and settings in photos
- **Contextual Prompts**: Generates magical animations based on actual objects in the scene
- **Smart Interactions**: People acknowledge the viewer, interact with each other, and animate existing objects
- **No Additions**: Only animates what's already in the photo - no fake objects added

### 🖼️ **Image Processing**
- **Black & White Conversion**: Three methods (grayscale, high_contrast, vintage)
- **Aspect Ratio Fitting**: Automatic letterboxing to prevent distortion
- **Multiple Formats**: Supports JPG, PNG, WEBP

### 🎬 **Video Features**
- **Seamless Looping**: FFmpeg crossfade for perfect loops
- **Direct Camera Gaze**: Subjects maintain eye contact with viewer
- **Interactive Portraits**: People whisper, gesture, and acknowledge the camera
- **8-Second Duration**: Perfect for digital photo frames

### ⚡ **Rate Limiting**
- **Automatic Quota Management**: Tracks API usage and waits when needed
- **Persistent State**: Remembers usage across sessions
- **Smart Retry**: Handles transient API errors with exponential backoff

## 🚀 Installation

### Prerequisites

- Python 3.12+
- Google API key with access to Gemini and Veo 3.1 APIs
- (Optional) NVIDIA GPU for local SVD generation

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd harryphoto2
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

## 📖 Usage

### Basic Usage

Generate an animated portrait with all magical features:

```bash
python examples/generate_video.py photo.jpg \
  --backend veo \
  --preprocess-bw \
  --use-gemini-prompt \
  --intensity moderate \
  --loop
```

### Command-Line Options

#### Backend Selection
- `--backend auto` - Try Veo, fallback to SVD (default)
- `--backend veo` - Force Veo 3.1 (cloud)
- `--backend svd` - Force Stable Video Diffusion (local GPU)

#### Photo Processing
- `--preprocess-bw` - Convert to black & white before processing
- `--bw-method [grayscale|high_contrast|vintage]` - B&W conversion method (default: high_contrast)

#### Animation Style
- `--photo-type [portrait|group|landscape|pet|formal]` - Type of photo
- `--intensity [subtle|moderate|dramatic]` - Animation intensity
- `--duration SECONDS` - Video duration (default: 8)

#### Prompts
- `--use-gemini-prompt` - Use Gemini to analyze image and generate contextual prompts
- `--custom-elements "element1" "element2"` - Add custom animation elements

#### Output
- `--output PATH` - Output video path
- `--loop` - Create seamlessly looping version
- `--loop-crossfade DURATION` - Crossfade duration in seconds (default: 0.5)

#### SVD Options (when using SVD backend)
- `--fps RATE` - Frames per second (default: 7)
- `--motion STRENGTH` - Motion strength 0-255 (default: 127)

### Examples

**Full magical generation with Gemini analysis:**
```bash
python examples/generate_video.py portrait.jpg \
  --backend veo \
  --preprocess-bw \
  --bw-method high_contrast \
  --use-gemini-prompt \
  --intensity moderate \
  --loop \
  --output magical_portrait.mp4
```

**Quick generation with default settings:**
```bash
python examples/generate_video.py photo.jpg
```

**Local GPU generation:**
```bash
python examples/generate_video.py photo.jpg \
  --backend svd \
  --fps 7 \
  --motion 127
```

**Check rate limit status:**
```bash
python check_rate_limit.py
```

## 🎭 How It Works

### 1. Image Preprocessing
- Converts to black & white (optional)
- Detects aspect ratio and adds letterboxing if needed
- Fits to 16:9 for Veo compatibility

### 2. Gemini Analysis (Optional)
- Analyzes image to identify people, objects, and setting
- Generates list of magical interaction suggestions
- Creates contextual animation prompt based on actual scene content
- **Example Output:**
  - People: "Woman with sunglasses, wearing jacket"
  - Objects: "Sunglasses, lion in background, tall grass"
  - Magical Actions: "Sunglasses slide down nose, lion's eyes glow, grass sways"

### 3. Video Generation
- **Veo 3.1**: Sends prompt and reference image to Google's API
- **SVD**: Uses local GPU with Stable Video Diffusion model
- Polls for completion (typically 60-90 seconds for Veo)

### 4. Post-Processing
- Downloads generated video
- Creates looping version with crossfade (optional)

### 5. Rate Limiting
- Tracks Veo API calls (10 per minute limit)
- Automatically waits when quota exhausted
- Persists state across runs

## 📁 Project Structure

```
harryphoto2/
├── src/
│   ├── api/
│   │   ├── gemini_analyzer.py    # Gemini Vision analysis
│   │   └── veo3_client.py         # Veo 3.1 API client
│   ├── prompts/
│   │   └── prompt_builder.py      # Harry Potter style prompts
│   ├── utils/
│   │   ├── config.py              # Configuration management
│   │   ├── image_utils.py         # Image preprocessing
│   │   ├── video_utils.py         # Video post-processing
│   │   └── rate_limiter.py        # API rate limiting
│   └── video_generator.py         # Main generation orchestrator
├── examples/
│   └── generate_video.py          # CLI interface
├── check_rate_limit.py            # Rate limit status checker
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required: Google API key with Gemini & Veo access
GOOGLE_API_KEY=your_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
```

### Rate Limits

**Veo 3.1 API (per project):**
- 10 requests per minute
- Daily quota varies by plan (check Google Cloud Console)

**Gemini Vision API:**
- Separate quota from Veo
- Not tracked by rate limiter (only Veo calls are tracked)

## 💰 API Quotas and Billing

- Veo 3.1 is in **paid preview** - check your Google Cloud billing
- Rate limits reset at midnight Pacific time
- Check quotas: Google Cloud Console → Vertex AI → Quotas
- Request quota increases if needed

## 🔧 Troubleshooting

### "429 RESOURCE_EXHAUSTED" Error
- You've hit the API quota limit
- Check status: `python check_rate_limit.py`
- Wait for quota reset (per-minute or daily)
- Verify billing in Google Cloud Console

### "No video in response" Error
- Prompt may be too complex - try `--intensity subtle`
- Image may trigger content filters
- Retry with simpler prompt

### Aspect Ratio Distortion
- System automatically adds letterboxing
- Portrait images fitted to 16:9 with black bars
- Preserves entire image without cropping

### Rate Limiter Not Working
- Delete `.google_api_rate_limit` to reset
- Check that only Veo calls are being tracked (not Gemini)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- **Google Gemini & Veo 3.1**: AI models powering the magic
- **Stable Video Diffusion**: Alternative local generation
- **FFmpeg**: Video processing and looping
- **J.K. Rowling**: Inspiration from the Harry Potter universe

## 🔒 Safety & Privacy

⚠️ **Important:**
- Personal photos are excluded from git by default
- Never commit `.env` file with API keys
- Rate limit state (`.google_api_rate_limit`) is excluded
- Check `.gitignore` before committing

## 🚧 Future Enhancements

- [ ] Add more animation styles beyond Harry Potter
- [ ] Support for color photos (not just B&W)
- [ ] Batch processing multiple photos
- [ ] Web interface for easier use
- [ ] Custom prompt templates
- [ ] Video quality settings
- [ ] Support for other aspect ratios (9:16, 4:3)

## 💬 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with ✨ magic and 🧙 AI**
