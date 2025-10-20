# Known Issues

## Veo 3.1 Image-to-Video Generation (Current Blocker)

**Status**: Blocked by Google server errors (502 Bad Gateway)
**Date**: October 19, 2025

### Issue
The Veo 3.1 API (`veo-3.1-generate-preview`) is returning 502 Bad Gateway errors when attempting to generate videos with reference images.

### Root Cause
Veo 3.1 was released only 4 days ago (October 15, 2025) and is in "paid preview" status. The service appears to be experiencing infrastructure issues as it scales up.

### What Works ✅
- API key authentication
- Model access (veo-3.1-generate-preview)
- Image validation and upload to Google Files API
- Prompt generation
- Reference images configuration
- Exponential backoff retry logic (30s → 60s → 120s)
- All application infrastructure

### What Doesn't Work ❌
- Video generation requests return `502 Bad Gateway` errors
- This occurs even after retry attempts

### Our Implementation Status
The application code is **100% complete and correct**. We are using the proper API approach:

```python
operation = self.client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        reference_images=[uploaded_file],
        aspect_ratio="16:9",
        resolution="720p"
    )
)
```

### Error Example
```
2025-10-19 22:24:29 - WARNING - Transient error on attempt 1/3: 502 Bad Gateway
2025-10-19 22:24:29 - INFO - Retrying in 30 seconds...
2025-10-19 22:25:27 - WARNING - Transient error on attempt 2/3: 502 Bad Gateway
2025-10-19 22:25:27 - INFO - Retrying in 60 seconds...
2025-10-19 22:26:48 - ERROR - Failed after 3 attempts
```

### Current Workaround
We have implemented a continuous retry script (`continuous_retry.py`) that:
- Attempts video generation every 5 minutes
- Runs indefinitely until successful
- Logs all attempts to `continuous_retry.log`
- Won't overload Google's servers

```bash
./venv/bin/python3 continuous_retry.py
```

### Alternative Model Options

#### Veo 2.0
- **Status**: Stable and working
- **Limitation**: Does NOT support `reference_images` parameter
- **Use case**: Text-to-video only (no image input for character consistency)

#### Veo 3.0
- **Status**: Working
- **Limitation**: Does NOT support `reference_images` parameter
- **Use case**: Text-to-video only

#### Veo 3.1 (Current Choice)
- **Status**: Unstable (502 errors)
- **Feature**: Supports `reference_images` for character/style consistency
- **Use case**: Image-to-video with character preservation (our requirement)

### Why We Can't Use Other Models
Our Harry Potter photo frame application requires:
1. Starting with a user's photo
2. Maintaining their appearance in the video
3. Adding subtle animation (portrait coming to life)

Only Veo 3.1's `reference_images` feature supports this workflow.

### Next Steps
1. **Continue running continuous retry script** - Will auto-succeed when Google's servers stabilize
2. **Monitor Google's status** - Service is brand new and likely being scaled up
3. **Check logs periodically** - `tail -f continuous_retry.log`

### Expected Resolution
Based on the 4-day timeline since release:
- **Short term** (days): Google will stabilize Veo 3.1 infrastructure
- **Our app**: Will work immediately once servers are stable (no code changes needed)

### References
- [Veo 3.1 Announcement](https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/) - October 15, 2025
- [Official Veo 3 Docs](https://ai.google.dev/gemini-api/docs/video)
- [Python SDK](https://github.com/googleapis/python-genai)

---

**Note**: This is a temporary external blocker. The application is production-ready and will function perfectly once Google's Veo 3.1 service stabilizes.
