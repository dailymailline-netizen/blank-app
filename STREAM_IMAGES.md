# Stream Image Management & Intelligent Caching

## Overview

Enhanced live streaming with private/public image management and intelligent per-page memory caching. Each stream can have multiple images (photos/thumbnails) with configurable visibility and automatic cache optimization.

---

## Features

### 1. **Private/Public Image Management**

- **Public Images**: Visible to all viewers
- **Private Images**: Visible only to stream owner
- **Future**: Subscriber-only images
- **Metadata**: Title, description, dimensions, view count, upload timestamp

### 2. **Intelligent Memory Caching**

**Cache Layers:**
- **Memory Cache** – Fast in-memory storage with LRU eviction
- **Disk Cache** – Persistent backup for recovery
- **Page-Scoped Cache** – Separate cache per page/section

**Cache Strategy:**
- Max memory configurable (default: 500 MB)
- TTL-based expiration (default: 24 hours)
- LRU eviction removes oldest 20% when memory full
- Automatic thumbnail generation (200x200 px)

**Memory Efficiency:**
- Base64 encoding caches image strings (not binary)
- Per-page isolation prevents cache collisions
- Streamlit `@st.cache_resource` singleton pattern
- `@st.cache_data` 1-hour TTL for display strings

### 3. **Per-Page Cache Management**

Each page can independently manage its cache:
- Stream Details Page – Cache stream-specific images
- Stream Gallery Page – Cache browsable images  
- Stream Browser Page – Cache multi-stream indexes

No cache interference between pages.

---

## Architecture

### Core Components

#### `StreamImage` Class
```python
StreamImage(
    image_id: str,              # UUID
    stream_id: str,             # Parent stream
    filename: str,              # Original filename
    file_path: str,             # Disk path
    visibility: ImageVisibility, # PUBLIC | PRIVATE | SUBSCRIBERS
    title: str,                 # User-provided title
    description: str,           # User-provided description
)
```

**Attributes:**
- `size_bytes`: File size
- `dimensions`: (width, height) tuple
- `thumbnail_path`: Path to auto-generated thumbnail
- `view_count`: Number of times viewed
- `created_at`: ISO timestamp
- `last_accessed`: Last view timestamp

#### `StreamImageCache` Class
```python
StreamImageCache(
    cache_dir: Path,           # Cache directory
    max_memory_mb: int = 500,  # Max memory limit
    ttl_hours: int = 24        # Expiration time
)
```

**Methods:**
- `cache_image(image_id, image_data, page)` – Add to cache
- `get_image(image_id, page)` – Retrieve from cache
- `clear_page_cache(page)` – Clear page-specific cache
- `get_cache_stats()` – Cache statistics

#### `StreamImageManager` Class
```python
StreamImageManager(
    images_dir: Path,  # Base directory for all images
    cache_dir: Path    # Cache directory
)
```

**Methods:**
- `upload_stream_image(stream_id, image_data, filename, visibility, title, description, page)` – Upload image
- `get_stream_images(stream_id, user_id, is_owner, page)` – Get visible images with access control
- `delete_stream_image(stream_id, image_id)` – Delete image
- `get_image_stats(stream_id)` – Stream image statistics

### Directory Structure
```
stream_images/
├── {stream_id}/
│   ├── {image_id}_original.jpg        # Full resolution
│   ├── {image_id}_thumb.jpg           # Thumbnail (200x200)
│   └── ...
└── images_metadata.json               # Metadata index

image_cache/
├── cache_metadata.json                # Cache metadata
├── {page}_{image_id}.img             # Cached image (disk backup)
└── ...
```

---

## Usage

### 1. **Upload Stream Image**

```python
from stream_images import StreamImageManager, ImageVisibility
from config import STREAM_IMAGES_DIR, IMAGE_CACHE_DIR
import pathlib

# Initialize manager
manager = StreamImageManager(STREAM_IMAGES_DIR, IMAGE_CACHE_DIR)

# Upload image
image_id = manager.upload_stream_image(
    stream_id="stream-123",
    image_data=image_bytes,
    filename="photo.jpg",
    visibility=ImageVisibility.PUBLIC,
    title="Live Event Photo",
    description="Captured during stream",
    page="stream_details"
)
```

### 2. **Get Visible Images (with Access Control)**

```python
# Get images for viewer
images = manager.get_stream_images(
    stream_id="stream-123",
    user_id="user-456",
    is_owner=False,  # Not owner, see only public
    page="stream_gallery"
)

# Get images for owner
images = manager.get_stream_images(
    stream_id="stream-123",
    user_id="user-789",
    is_owner=True,   # Owner, see all
    page="stream_details"
)
```

### 3. **Render UI (Streamlit)**

```python
from stream_images_ui import (
    render_stream_image_uploader,
    render_stream_images_gallery,
    render_page_cache_manager
)

# Upload widget (owner only)
image_id = render_stream_image_uploader(
    stream_id="stream-123",
    is_owner=True,
    page="stream_details"
)

# Display gallery
render_stream_images_gallery(
    stream_id="stream-123",
    is_owner=True,
    user_id="user-789",
    page="stream_gallery"
)

# Cache management sidebar
render_page_cache_manager(page="stream_gallery")
```

---

## Configuration

**In `config.py`:**

```python
# Stream Image Settings
MAX_STREAM_IMAGES_PER_STREAM = 50              # Max images per stream
MAX_IMAGE_UPLOAD_SIZE_MB = 20                 # Max file size
IMAGE_CACHE_MAX_MEMORY_MB = 500               # Cache size limit
IMAGE_CACHE_TTL_HOURS = 24                    # Cache expiration

# Directories
STREAM_IMAGES_DIR = BASE_DIR / "stream_images"
IMAGE_CACHE_DIR = BASE_DIR / "image_cache"

# Allowed formats
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
```

**Customize per environment:**

```bash
export IMAGE_CACHE_MAX_MEMORY_MB=1000  # Increase for servers
export IMAGE_CACHE_TTL_HOURS=6         # Shorter TTL for frequent updates
```

---

## Cache Behavior

### Memory Cache Strategy

**Scenario 1: Normal Operation**
1. Image uploaded → cached in memory
2. Viewer accesses → retrieved from memory cache (instant)
3. After 24 hours (TTL) → expired, reload from disk

**Scenario 2: Memory Pressure**
1. New image uploaded, memory at 90% limit
2. System triggers LRU eviction
3. Oldest 20% of cached images removed
4. Disk cache preserved (no data loss)
5. Newly accessed images restore from disk

**Scenario 3: Page Switch**
1. User on Stream Gallery page → uses page-scoped cache
2. User switches to Stream Details page → different cache namespace
3. No memory collision between pages

### Cache Lifetime

```
Image Upload
    ↓
Memory Cache (0-24h)
    ↓
Disk Cache (Permanent backup)
    ↓
Next Access → Restore to Memory
```

---

## Performance Metrics

### Memory Usage

| Scenario | Memory Used | Notes |
|----------|-------------|-------|
| 10 images, 2 MB each | ~20 MB | + metadata overhead |
| 100 images, 5 MB each | 500 MB | At default max |
| With LRU eviction | Stays ≤ 500 MB | Automatic cleanup |

### Access Speed

| Operation | Time | Notes |
|-----------|------|-------|
| Memory cache hit | <10 ms | Instant |
| Disk cache restore | 50-200 ms | File I/O + decode |
| New upload | 500-2000 ms | Resize + thumbnail |

### Disk Usage

| Component | Size | Notes |
|-----------|------|-------|
| Original image (5 MB) | 5 MB | Full resolution |
| Thumbnail (200x200) | 50-100 KB | Auto-generated |
| Metadata (JSON) | <1 KB | Per image |
| Cached image (disk) | Same as original | Backup copy |

---

## Integration with Existing Features

### Storage Backends

Images can be stored in multiple backends via `storage_backend.py`:

```python
from storage_backend import StorageFactory

# Local storage (default)
storage = StorageFactory.create_backend("local")

# AWS S3
storage = StorageFactory.create_backend(
    "s3",
    bucket_name="my-bucket",
    aws_access_key="...",
    aws_secret_key="..."
)

# Save stream image to backend
storage.upload_file(
    local_path="stream_images/stream-123/image-456_original.jpg",
    remote_path=f"s3://bucket/stream-123/image-456.jpg"
)
```

### Stream Manager Integration

Extend `StreamManager` to automatically create images:

```python
# In stream_manager.py
from stream_images import StreamImageManager

class StreamManager:
    def __init__(self):
        self.image_manager = StreamImageManager(
            STREAM_IMAGES_DIR,
            IMAGE_CACHE_DIR
        )
    
    def create_stream_thumbnail_from_video(self, stream_id, video_path):
        """Auto-generate thumbnail from video"""
        thumbnail = self.video_processor.create_thumbnail(
            video_path,
            timestamp=5  # 5 seconds in
        )
        self.image_manager.upload_stream_image(
            stream_id=stream_id,
            image_data=thumbnail,
            filename="auto_thumbnail.jpg",
            visibility=ImageVisibility.PUBLIC,
            title="Stream Thumbnail",
            page="stream_auto"
        )
```

---

## Troubleshooting

### Issue: Cache grows unbounded

**Solution:** LRU eviction is active. Check cache stats:
```python
manager.cache.get_cache_stats()
```

**Adjust config:**
```bash
export IMAGE_CACHE_MAX_MEMORY_MB=300  # Lower limit triggers more eviction
```

### Issue: Images missing after restart

**Normal behavior:** Memory cache cleared on app restart, but disk cache preserves images. Access restores from disk.

**For persistence:** Use S3 backend or enable NFS.

### Issue: Slow image load

**Cause:** Disk cache miss or network latency.

**Solution:** 
1. Verify image files exist on disk
2. Check cache stats: `manager.cache.get_cache_stats()`
3. Increase TTL to keep images longer: `export IMAGE_CACHE_TTL_HOURS=72`

### Issue: Private image visible to all

**Cause:** User flagged as `is_owner=True` when not.

**Solution:** Ensure authentication/authorization before rendering:
```python
# Only show upload if owner
if st.session_state.get("current_user_id") == stream_owner_id:
    render_stream_image_uploader(..., is_owner=True)
```

---

## Examples

### Example 1: Live Event Photo Gallery

```python
import streamlit as st
from stream_images_ui import render_stream_images_gallery, render_page_cache_manager

st.title("Live Event Photos")

stream_id = st.query_params.get("stream", "stream-001")
user_id = st.session_state.get("user_id")

# Show images
render_stream_images_gallery(
    stream_id=stream_id,
    is_owner=False,  # Viewers see public only
    user_id=user_id,
    page="live_event_gallery"
)

# Cache controls
render_page_cache_manager("live_event_gallery")
```

### Example 2: Stream Dashboard with Upload

```python
import streamlit as st
from stream_images_ui import (
    render_stream_image_uploader,
    render_stream_images_gallery,
    render_page_cache_manager
)

st.title(f"Stream: {stream_name}")

# Owner upload section
if is_owner:
    render_stream_image_uploader(
        stream_id=stream_id,
        is_owner=True,
        page="stream_dashboard"
    )
    st.divider()

# Public gallery
render_stream_images_gallery(
    stream_id=stream_id,
    is_owner=is_owner,
    user_id=user_id,
    page="stream_dashboard"
)

# Footer
with st.sidebar:
    render_page_cache_manager("stream_dashboard")
```

---

## Future Enhancements

1. **Subscriber-Only Images** – Partial visibility for premium viewers
2. **Image Search** – Full-text search by title/description
3. **Bulk Upload** – Upload multiple images at once
4. **Image Filters** – Blur sensitive content automatically
5. **CDN Integration** – Serve images from edge locations
6. **WebP Encoding** – Automatic format conversion for optimization
7. **Collaborative Editing** – Multiple users manage images
8. **Analytics** – Per-image engagement metrics

---

## Summary

**Stream Image Management + Intelligent Caching provides:**
- ✅ Private/public access control per image
- ✅ Multi-layer caching (memory + disk)
- ✅ Per-page cache isolation
- ✅ Automatic thumbnail generation
- ✅ LRU memory management
- ✅ Storage backend integration
- ✅ Streamlit UI components
- ✅ Full metadata tracking
- ✅ View analytics per image

**Resource Efficient:**
- Default 500 MB memory limit
- Automatic eviction prevents runaway usage
- Per-page caching reduces cross-page interference
- Thumbnail generation optimizes display

**Production Ready:**
- Comprehensive error handling
- JSON persistence
- Access control enforcement
- Configurable limits and timeouts
