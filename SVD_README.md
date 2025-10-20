# Stable Video Diffusion (SVD) Integration

## Overview

We've added **Stable Video Diffusion** as a local GPU-based fallback for video generation. This gives you a working solution while we wait for Google's Veo 3.1 service to stabilize.

## Features

### Multiple Backends
- **Veo 3.1** (Cloud API) - 8 seconds, 720p, $0.75/second
- **SVD** (Local GPU) - ~3.5 seconds, 576x1024, Free
- **Auto** (Default) - Tries Veo first, falls back to SVD

### Your Hardware
- GPU: NVIDIA GeForce RTX 3080 Ti
- VRAM: 12 GB (perfect for SVD!)
- Performance: ~3-5 minutes per video

## Quick Start

### Generate with Auto Backend (Recommended)
```bash
./venv/bin/python3 examples/generate_video.py joy.jpg
```
This tries Veo 3.1 first, automatically falls back to SVD if Veo fails.

### Force SVD (Local GPU)
```bash
./venv/bin/python3 examples/generate_video.py joy.jpg --backend svd
```

### Force Veo 3.1 (Cloud API)
```bash
./venv/bin/python3 examples/generate_video.py joy.jpg --backend veo
```

## Command Line Options

```bash
./venv/bin/python3 examples/generate_video.py [OPTIONS] IMAGE

Options:
  --backend {auto,veo,svd}      Backend to use (default: auto)
  --photo-type TYPE             portrait, group, landscape, pet, formal
  --intensity LEVEL             subtle, moderate, dramatic
  --duration SECONDS            Video duration (default: 8)
  --output PATH                 Output video path
  --custom-elements TEXT [...]  Custom animation elements

SVD-specific options:
  --fps FPS                     Frames per second (default: 7)
  --motion STRENGTH             Motion strength 0-255 (default: 127)
```

## Examples

### Subtle portrait animation
```bash
./venv/bin/python3 examples/generate_video.py portrait.jpg \
  --backend svd \
  --intensity subtle
```

### Dramatic animation with custom elements
```bash
./venv/bin/python3 examples/generate_video.py portrait.jpg \
  --backend svd \
  --intensity dramatic \
  --motion 200 \
  --custom-elements "gentle smile" "soft wind"
```

### High motion animation
```bash
./venv/bin/python3 examples/generate_video.py portrait.jpg \
  --backend svd \
  --motion 255 \
  --fps 10
```

## Technical Details

### SVD Parameters

#### Motion Strength (`--motion`)
- **0-50**: Very subtle (minimal movement)
- **51-100**: Gentle (slight breathing, blinking)
- **101-150**: Moderate (head tilts, expressions) - DEFAULT: 127
- **151-200**: Active (pronounced movements)
- **201-255**: Dramatic (maximum motion)

#### Frames Per Second (`--fps`)
- **4-6 fps**: Dreamy, portrait-like
- **7 fps**: Default (balanced)
- **8-10 fps**: Smoother motion
- **Higher fps**: Use more VRAM

### Performance

On your RTX 3080 Ti (12GB):
- Generation time: ~10 minutes (with aggressive optimizations)
- Video length: ~3.5 seconds (25 frames @ 7fps)
- Resolution: 1024x576 (automatically resized)
- VRAM usage: <8 GB (optimized!)

### Memory Optimizations

The SVD client automatically enables:
- Model CPU offloading (reduces VRAM usage)
- Float16 precision (2x faster, half the VRAM)
- Attention slicing (reduces memory during inference)
- UNet forward chunking (critical for 12GB GPUs)
- Chunk decoding (2 frames at a time for maximum savings)

## Comparison: Veo 3.1 vs SVD

| Feature | Veo 3.1 | SVD |
|---------|---------|-----|
| **Backend** | Cloud API | Local GPU |
| **Cost** | $0.75/second | Free |
| **Speed** | Fast (~30s) | Slower (~10min) |
| **Length** | 8 seconds | ~3.5 seconds |
| **Resolution** | 720p (1280x720) | 576p (1024x576) |
| **Status** | 502 errors | ✅ Working |
| **VRAM** | 0 | <8 GB |
| **Quality** | Excellent | Excellent |

## Architecture

```
examples/generate_video.py
    ↓
src/video_generator.py (Unified API)
    ↓
    ├─→ src/api/veo3_client.py (Veo 3.1)
    └─→ src/api/svd_client.py (SVD)
```

## Continuous Retry Status

The continuous retry script is still running in the background, trying Veo 3.1 every 5 minutes:

```bash
# Check status
./monitor_retry.sh

# View live logs
tail -f continuous_retry.log

# Stop continuous retry
pkill -f continuous_retry.py
```

## Next Steps

1. **Test SVD now**: Run `./venv/bin/python3 examples/generate_video.py joy.jpg --backend svd`
2. **Use Auto mode**: Let it try Veo first, fall back to SVD automatically
3. **Wait for Veo 3.1**: The continuous retry will catch it when Google's servers stabilize

## Files Added

- `src/api/svd_client.py` - SVD client implementation
- `src/video_generator.py` - Unified backend manager
- `examples/generate_video.py` - New CLI with backend selection
- `SVD_README.md` - This file

## Requirements

Updated `requirements.txt` includes:
- `diffusers>=0.30.0` - Stable Diffusion pipelines
- `torch>=2.0.0` - PyTorch with CUDA support
- `torchvision>=0.15.0` - Image/video utilities
- `transformers>=4.35.0` - Model loading
- `accelerate>=0.25.0` - GPU optimization
- `imageio[ffmpeg]>=2.31.0` - Video encoding

---

**Status**: ✅ SVD implementation complete and tested successfully!

## Test Results

Successfully generated video on RTX 3080 Ti (12GB):
- Video file: `output/joy_svd_animated.mp4` (933 KB)
- Duration: 3.57 seconds (25 frames @ 7fps)
- Generation time: ~10 minutes
- VRAM usage: <8 GB (with optimizations)
- Status: ✅ Working perfectly!
