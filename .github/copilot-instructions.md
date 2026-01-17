# Copilot Instructions for Stream & Upload Hub

## Project Overview

**Stream & Upload Hub** is a Streamlit-based video management application with three core systems:
1. **Upload System** – Multi-format video file uploads with metadata tracking
2. **Streaming System** – Live stream creation and management with configurable settings
3. **Video Library** – Browsable, playable video archive

This is a single-page Streamlit app (not a traditional backend service), so architecture is UI-centric with session state management and persistent JSON-based storage.

---

## Architecture & Key Components

### Data Flow
```
User Upload → save_uploaded_file() → uploads/ dir + session_state
Live Stream → StreamManager.create_stream() → streams/ dir (JSON) + session_state
Video Library → get_video_files() → read from uploads/ dir
```

### Critical Design Patterns

**Session State Management** (streamlit_app.py:15-20)
- `st.session_state.uploaded_videos` – List of upload metadata dicts
- `st.session_state.streams` – List of stream metadata dicts
- Session state is ephemeral (lost on rerun); persistent data uses JSON files

**Dual Storage Strategy**
- **Session State** – Fast, in-memory for current session (videos, streams)
- **File System** – Persistent storage:
  - `uploads/` – Actual video files
  - `streams/` – Stream metadata as JSON (`{stream_id}.json`)

**Multi-Page Navigation**
- Single `streamlit_app.py` file with radio selector switching between pages
- Pages: Home, Upload Video, Live Stream, Video Library, Settings

### Key Files & Responsibilities

| File | Role | Critical Concepts |
|------|------|-------------------|
| `streamlit_app.py` | UI/Pages | Session state, file upload widget, radio navigation, `st.rerun()` triggers |
| `config.py` | Constants | Paths (UPLOAD_DIR, STREAMS_DIR), limits (MAX_UPLOAD_SIZE_MB), features (ENABLE_* flags) |
| `stream_manager.py` | Stream Logic | `StreamManager` (CRUD), `VideoProcessor` (cv2-based metadata), `AnalyticsTracker` |
| `utils.py` | Helpers | Video metadata (cv2), file validation, JSON I/O, directory utilities |

---

## Developer Workflows

### Adding Features
1. **UI Changes** → Modify relevant page in `streamlit_app.py`
2. **Business Logic** → Add to `stream_manager.py` (streams) or `utils.py` (general)
3. **Configuration** → Update `config.py` constants
4. **Test Locally** → `streamlit run streamlit_app.py` (opens http://localhost:8501)

### Running the App
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Development Tools
```bash
pytest tests/                    # Run tests (requires pytest)
black streamlit_app.py          # Format code
flake8 streamlit_app.py         # Lint code
mypy streamlit_app.py --ignore-missing-imports  # Type check
```

---

## Project-Specific Conventions

### Video Metadata Pattern
All video info stored as dicts with consistent keys:
```python
{
    "name": str,
    "path": str,
    "size": int,
    "uploaded_at": str (ISO timestamp),
    "type": str (MIME type)
}
```
**Where used:** `st.session_state.uploaded_videos`, stream metadata

### Stream Metadata Pattern
```python
{
    "id": str (UUID),
    "name": str,
    "description": str,
    "resolution": str ("720p", "1080p", "4K", "2K", "480p"),
    "bitrate": str ("1000 kbps" to "12000 kbps"),
    "status": str ("active" or "stopped"),
    "created_at": str (ISO timestamp),
    "updated_at": str (ISO timestamp),
    "stats": {...}  # Viewer count, FPS, etc.
}
```
**Where used:** `st.session_state.streams`, `streams/*.json` files, StreamManager

### Video Validation
- Valid extensions: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.m4v`
- Validation function: `validate_video_file()` in utils.py (checks suffix only; add format validation if needed)
- Default limit: 500 MB (`MAX_UPLOAD_SIZE_MB` in config.py)

### Streamlit-Specific Patterns
- **st.rerun()** – Force page refresh after state changes (e.g., after starting/stopping stream)
- **st.session_state** – Persists across reruns within one session; never persists across browser restarts
- **File Uploader** – `st.file_uploader()` returns `UploadedFile` object; save to disk immediately
- **Expanders** – Used for video/stream details (collapsible sections)

---

## Integration Points & Dependencies

### External Dependencies
- **Streamlit** (>=1.28.0) – UI framework
- **OpenCV** (opencv-python >=4.8.0) – Video metadata extraction (`cv2.VideoCapture`)
- **NumPy**, **Pillow** – Image/array processing (optional enhancements)
- **aiofiles** – Async file I/O (not actively used; remove if unused)

### Video Metadata Extraction (OpenCV)
`utils.get_video_metadata()` and `VideoProcessor` class use `cv2.VideoCapture()`:
```python
cap = cv2.VideoCapture(file_path)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
cap.release()
```
**Gotcha:** Ensure file exists on disk before calling (not just in session state).

### JSON Persistence
Streams and analytics saved as JSON in `streams/` directory:
- File name: `{stream_id}.json`
- Serialized via `json.dump()` / `json.load()`
- Always store timestamps as ISO format strings (`datetime.now().isoformat()`)

---

## Common Patterns & Anti-Patterns

✅ **DO:**
- Store file paths as strings or `Path` objects; convert to string when passing to Streamlit
- Use `st.session_state` for temporary UI state; use JSON files for persistent data
- Call `st.rerun()` after modifying session state that affects UI
- Validate file extensions and size before saving

❌ **DON'T:**
- Assume session state persists across browser sessions (it doesn't)
- Save large binary data to session state (keeps in memory)
- Call `cv2.VideoCapture()` on non-existent files without error handling
- Mix Streamlit cache decorators (@st.cache_data) with mutable session state without careful consideration

---

## Cloud & Storage Features (v2.0+)

### Storage Backend Abstraction (`storage_backend.py`)
- **LocalStorageBackend** – File system storage (default, dev-friendly)
- **S3StorageBackend** – AWS S3 integration with boto3
- **StorageFactory** – Factory pattern for backend switching

**Usage Pattern:**
```python
storage = StorageFactory.create_backend(
    "s3",
    bucket_name="my-bucket",
    aws_access_key="...",
    aws_secret_key="..."
)
storage.upload_file("local.mp4", "s3://bucket/video.mp4")
```

### Community Notepad (`community_notepad.py`)
- **CommunityNotepad** – Note CRUD + search + version tracking
- **P2PPeerManager** – Peer discovery & sync coordination
- **NotePadAnalytics** – Usage tracking

**Features:** Shared/private notes, markdown support, tags, version history, P2P sync

### P2P NFS Network
- **Avahi/mDNS** – Automatic peer discovery on local network
- **NFS Mounts** – Shared storage across instances (`/data/notes`, `/data/videos`)
- **Gossip Protocol** – Sync queue broadcasts to all peers
- **Conflict Resolution** – Version numbers + last-write-wins

**Setup:** See `P2P_NFS_SETUP.md` for NFS server/client configuration

### Deployment Patterns

| Pattern | Storage | Notes | Use Case |
|---------|---------|-------|----------|
| **Local Only** | Filesystem | Single instance | Dev, hobby projects |
| **S3 Only** | AWS S3 | Streamed from CDN | Production, multi-instance |
| **NFS+Local** | NFS mount + Local cache | P2P sync via Avahi | Collaborative teams, <20 instances |
| **Hybrid** | NFS + S3 | Videos on S3, notes on NFS | Large-scale, high availability |

---

## Environment Configuration

**Key variables** (see `.env.example`):
- `STORAGE_BACKEND` – "local" or "s3"
- `AWS_S3_BUCKET`, `AWS_REGION` – For S3 backend
- `P2P_ENABLED` – Enable peer discovery
- `NOTEPAD_STORAGE_PATH` – Where to store notes

**Load with:** `export $(cat .env | xargs)`

---

## Notable Features & Gaps

✅ **Implemented (v2.0):**
- AWS S3 storage backend
- Local storage with NFS support
- Community notepad with version tracking
- P2P peer discovery and sync
- Storage abstraction layer

⚠️ **Partial:**
- Analytics system (AnalyticsTracker exists, not fully integrated)
- Video playback (native `st.video()` only)

❌ **Not Yet Implemented:**
- User authentication (`ENABLE_USER_AUTH = False`)
- Video transcoding (`ENABLE_TRANSCODING = False`)
- Operational Transform (OT) for concurrent note editing
- Persistent session state on app restart

---

## References

- **Streamlit:** https://docs.streamlit.io/
- **AWS S3:** https://docs.aws.amazon.com/s3/
- **NFS Setup:** https://ubuntu.com/server/docs/service-nfs
- **Avahi/mDNS:** https://www.avahi.org/
- **Project Docs:** 
  - CLOUD_ARCHITECTURE.md – System design
  - CLOUD_SETUP.md – Quick start guide
  - P2P_NFS_SETUP.md – NFS infrastructure guide
