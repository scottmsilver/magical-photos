# Google Photos Integration Plan 📸✨

## Overview

Add a web UI that allows users to browse their Google Photos library, select photos, and generate magical Harry Potter-style animated portraits directly from their cloud photo collection.

## Architecture

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Web UI        │
│  (Streamlit)    │
└────────┬────────┘
         │
         ├──────────────────┐
         v                  v
┌─────────────────┐   ┌──────────────────┐
│ Google Photos   │   │ Magical Photo    │
│     API         │   │   Generator      │
│  (OAuth 2.0)    │   │  (existing)      │
└────────┬────────┘   └──────────────────┘
         │                      │
         v                      v
   User's Photos          Animated Videos
```

## Technology Stack

### New Dependencies

```python
# requirements-web.txt
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.111.0
streamlit==1.29.0
streamlit-oauth==0.1.0
pillow==10.1.0
requests==2.31.0
python-dotenv==1.0.0
```

### Google Photos Library API

- **Authentication**: OAuth 2.0
- **Scope**: `https://www.googleapis.com/auth/photoslibrary.readonly`
- **Base URL Validity**: 60 minutes
- **Rate Limits**: Standard Google API quotas

## Implementation Phases

### Phase 1: Google Photos API Integration (2-3 hours)

#### 1.1 Setup Google Cloud Project

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or use existing
3. Enable "Photos Library API"
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8501` (for local dev)
5. Download `client_secret.json`

**Configuration:**
```bash
# .env additions
GOOGLE_PHOTOS_CLIENT_ID=your_client_id
GOOGLE_PHOTOS_CLIENT_SECRET=your_client_secret
GOOGLE_PHOTOS_REDIRECT_URI=http://localhost:8501
```

#### 1.2 Create Google Photos Client

**File: `src/integrations/__init__.py`**
```python
"""Integration modules for external services."""
```

**File: `src/integrations/google_photos_client.py`**

Key features:
- OAuth 2.0 authentication flow
- Token management (refresh, expiry)
- Photo library access methods
- Thumbnail and full-resolution downloads
- Album listing and filtering
- Search capabilities (date, people, location)

**Core Methods:**
```python
class GooglePhotosClient:
    def __init__(self, credentials_path: str)
    def authenticate(self) -> bool
    def get_auth_url(self) -> str
    def handle_oauth_callback(self, code: str) -> credentials
    def list_albums(self, page_size: int = 50) -> List[Album]
    def list_photos(self, album_id: str = None, page_size: int = 50) -> List[MediaItem]
    def search_photos(self, filters: dict) -> List[MediaItem]
    def get_photo_metadata(self, media_item_id: str) -> dict
    def download_photo(self, media_item: MediaItem, output_dir: str) -> str
    def get_thumbnail_url(self, media_item: MediaItem, size: int = 200) -> str
```

**Data Models:**
```python
@dataclass
class MediaItem:
    id: str
    filename: str
    mime_type: str
    creation_time: datetime
    width: int
    height: int
    base_url: str
    thumbnail_url: str

@dataclass
class Album:
    id: str
    title: str
    media_items_count: int
    cover_photo_url: str
```

### Phase 2: Web UI with Streamlit (3-4 hours)

#### 2.1 Application Structure

```
src/web/
├── app.py                      # Main Streamlit application
├── auth.py                     # OAuth flow management
├── session_state.py            # Session state helpers
└── components/
    ├── __init__.py
    ├── photo_browser.py        # Photo grid display
    ├── photo_selector.py       # Selection UI
    ├── settings_panel.py       # Animation configuration
    ├── progress_tracker.py     # Generation progress
    └── video_player.py         # Result preview
```

#### 2.2 Main Application Flow

**File: `src/web/app.py`**

**Pages:**
1. **Authentication** → Connect to Google Photos
2. **Browse** → View albums and photos
3. **Select** → Choose photo and configure options
4. **Generate** → Create magical animation
5. **Results** → Preview and download

**Session State Management:**
```python
# Session state variables
st.session_state.authenticated = False
st.session_state.credentials = None
st.session_state.photos_client = None
st.session_state.selected_album = None
st.session_state.selected_photo = None
st.session_state.generated_video = None
st.session_state.page = "auth"
```

#### 2.3 UI Components

**Photo Browser Component:**
- Grid layout (4 columns)
- Lazy loading for performance
- Thumbnail display with metadata
- Pagination support
- Album filtering

**Settings Panel:**
- Intensity slider (subtle/moderate/dramatic)
- Gemini analysis toggle
- B&W preprocessing options
- Loop creation toggle
- Duration selector

**Progress Tracker:**
- Step-by-step progress display
- Real-time status updates
- Estimated time remaining
- Cancellation support

### Phase 3: Integration & Polish (2-3 hours)

#### 3.1 Connect to Existing Generator

**Integration Points:**
```python
# In app.py
from src.video_generator import VideoGenerator
from src.api.gemini_analyzer import GeminiAnalyzer

# Use existing generation code
generator = VideoGenerator(backend="veo", google_api_key=config.google_api_key)
output_path = generator.generate_video(
    image_path=downloaded_photo_path,
    prompt=prompt,
    duration=duration,
    # ... other options
)
```

#### 3.2 Temporary File Management

```python
import tempfile
from pathlib import Path

class TempFileManager:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="magical_photos_"))

    def save_photo(self, photo_data: bytes, filename: str) -> str
    def cleanup(self) -> None

# Auto-cleanup on session end
@st.cache_resource
def get_temp_manager():
    return TempFileManager()
```

#### 3.3 Error Handling

**Common Scenarios:**
- OAuth failures → Clear instructions for retry
- Rate limit exceeded → Show wait time, retry button
- Photo download failures → Fallback options
- Generation errors → Detailed error messages

### Phase 4: Testing & Validation (1-2 hours)

#### 4.1 Test Cases

- [ ] OAuth flow works correctly
- [ ] Photos load with thumbnails
- [ ] Album filtering works
- [ ] Photo selection persists
- [ ] Video generation succeeds
- [ ] Download works
- [ ] Session state maintained
- [ ] Error handling graceful

#### 4.2 Edge Cases

- [ ] Large photo collections (1000+ photos)
- [ ] Slow network connections
- [ ] Token expiration during use
- [ ] Multiple simultaneous generations
- [ ] Browser refresh handling

## Security Considerations

### OAuth Security

1. **Client Secret Protection:**
```python
# .gitignore additions
client_secret.json
credentials/
*.token
```

2. **Token Storage:**
- Use Streamlit session state (memory only)
- No persistent storage of tokens
- Tokens expire after 60 minutes

3. **HTTPS Requirements:**
- Production must use HTTPS
- Google requires HTTPS for OAuth redirects
- Use ngrok for local testing with real OAuth

### Privacy & Data Handling

- **No Photo Storage**: Photos downloaded temporarily, deleted after processing
- **No User Data**: Don't store user information
- **Audit Logging**: Log API calls for debugging (not photo content)

## Deployment

### Local Development

```bash
# Setup
pip install -r requirements-web.txt

# Configure OAuth
cp client_secret.json credentials/

# Run
streamlit run src/web/app.py
```

### Production Options

#### Option 1: Streamlit Cloud (Recommended)
**Pros:**
- Free tier available
- Direct GitHub integration
- Automatic SSL/HTTPS
- Easy secrets management

**Steps:**
1. Push to GitHub
2. Connect Streamlit Cloud account
3. Add secrets in dashboard
4. Deploy

#### Option 2: Google Cloud Run
**Pros:**
- Serverless, auto-scaling
- Good Google API integration
- Pay per use

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-web.txt ./
RUN pip install -r requirements.txt -r requirements-web.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/web/app.py", "--server.port=8501"]
```

#### Option 3: Heroku
**Pros:**
- Simple deployment
- Free tier available
- Add-ons ecosystem

**Procfile:**
```
web: streamlit run src/web/app.py --server.port=$PORT
```

## User Experience Flow

### 1. First Time User

```
Landing Page
    ↓
[Connect Google Photos Button]
    ↓
Google OAuth Consent Screen
    ↓
Grant Permissions
    ↓
Redirect to Photo Browser
    ↓
Browse Albums/Photos
    ↓
Select Photo
    ↓
Configure Options
    ↓
[Generate Magic Button]
    ↓
Progress Indicator
    ↓
Video Preview
    ↓
[Download Button]
```

### 2. Returning User

```
Landing Page (if token valid)
    ↓
Automatically load Photo Browser
    ↓
Continue from Browse step
```

## MVP Feature List

### Must-Have (Phase 1)
- ✅ Google Photos OAuth authentication
- ✅ Display photos in grid (latest 50)
- ✅ Select single photo
- ✅ Basic animation settings (intensity)
- ✅ Generate magical video
- ✅ Preview result
- ✅ Download video

### Nice-to-Have (Phase 2)
- Album browsing
- Search by date
- Multiple selection
- Batch processing queue
- Gemini analysis preview
- Save back to Google Photos
- Generation history

### Future Enhancements (Phase 3)
- Face detection for auto-selection
- Smart album suggestions
- Custom animation templates
- Social sharing
- Collaborative albums
- Advanced filters (location, people)

## API Rate Limits & Quotas

### Google Photos API
- **Quota**: 10,000 requests/day (free tier)
- **Photos per request**: 100 (pagination)
- **Base URL validity**: 60 minutes
- **Download size**: Full resolution supported

### Veo API (existing)
- **Rate limit**: 10 requests/minute (tracked by existing rate limiter)
- **Daily quota**: Varies by plan

**Strategy**: Batch photo metadata requests, cache thumbnails in session

## File Structure Changes

```
magical-photos/
├── src/
│   ├── integrations/          # NEW
│   │   ├── __init__.py
│   │   └── google_photos_client.py
│   ├── web/                   # NEW
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── auth.py
│   │   ├── session_state.py
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── photo_browser.py
│   │       ├── photo_selector.py
│   │       ├── settings_panel.py
│   │       ├── progress_tracker.py
│   │       └── video_player.py
│   └── [existing files...]
├── credentials/               # NEW (gitignored)
│   ├── client_secret.json
│   └── .gitkeep
├── requirements-web.txt       # NEW
├── .streamlit/               # NEW
│   └── config.toml
└── [existing files...]
```

## Configuration Files

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#9b59b6"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
font = "sans serif"

[server]
enableXsrfProtection = true
enableCORS = false
port = 8501

[browser]
gatherUsageStats = false
```

### `requirements-web.txt`

```txt
# Google Photos API
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.111.0

# Web Framework
streamlit==1.29.0

# Utilities
pillow==10.1.0
requests==2.31.0
python-dotenv==1.0.0

# Include base requirements
-r requirements.txt
```

## Timeline & Milestones

### Week 1: Core Integration
- **Day 1-2**: Google Photos API client
- **Day 3**: OAuth flow testing
- **Day 4-5**: Basic Streamlit UI

### Week 2: Polish & Deploy
- **Day 1-2**: Integration with existing generator
- **Day 3**: Error handling & edge cases
- **Day 4**: Testing & bug fixes
- **Day 5**: Documentation & deployment

**Total Estimated Time**: 7-10 days (part-time development)

## Success Metrics

- ✅ User can authenticate in < 30 seconds
- ✅ Photo browser loads in < 3 seconds
- ✅ Selection to generation in < 2 clicks
- ✅ Clear progress indication throughout
- ✅ Error messages are actionable
- ✅ Works on mobile browsers

## Next Steps

1. **Immediate**: Create Google Cloud project & enable Photos API
2. **Setup**: Install web dependencies
3. **Develop**: Start with Phase 1 (API client)
4. **Test**: Verify OAuth flow works
5. **Build**: Create basic Streamlit UI
6. **Integrate**: Connect to existing generator
7. **Deploy**: Push to Streamlit Cloud

## Questions to Resolve

- [ ] Should we support multiple photo selection (batch)?
- [ ] Do we need to save generation history?
- [ ] Should we allow saving back to Google Photos?
- [ ] Do we need user accounts/authentication persistence?
- [ ] What's the max video queue size?

---

**Status**: Planning Phase
**Priority**: High
**Complexity**: Medium
**Value**: High (much better UX than CLI)
