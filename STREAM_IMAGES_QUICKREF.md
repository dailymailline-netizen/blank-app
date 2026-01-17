# Stream Images - Quick Reference Card

## Installation

```bash
# 1. Ensure files are in place
ls /workspaces/blank-app/stream_images.py           # ✅ Core system
ls /workspaces/blank-app/stream_images_ui.py        # ✅ UI components

# 2. Install dependency
pip install pillow

# 3. Verify syntax
python3 -m py_compile stream_images.py stream_images_ui.py
```

---

## Configuration (config.py)

```python
# Image settings
MAX_STREAM_IMAGES_PER_STREAM = 50              # Per-stream limit
MAX_IMAGE_UPLOAD_SIZE_MB = 20                 # Max file size
IMAGE_CACHE_MAX_MEMORY_MB = 500               # Memory cache limit
IMAGE_CACHE_TTL_HOURS = 24                    # Cache lifetime

# Directories (auto-created)
STREAM_IMAGES_DIR = BASE_DIR / "stream_images"
IMAGE_CACHE_DIR = BASE_DIR / "image_cache"

# Allowed formats
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
```

---

## Basic API Usage

### Initialize (Singleton Pattern)
```python
from stream_images_ui import get_image_manager

manager = get_image_manager()  # Cached, reused across app reruns
```

### Upload Image
```python
image_id = manager.upload_stream_image(
    stream_id="stream-001",
    image_data=file_bytes,
    filename="photo.jpg",
    visibility=ImageVisibility.PUBLIC,  # or PRIVATE
    title="Stream Photo",
    description="Optional description",
    page="stream_details"  # For cache organization
)
```

### Get Visible Images
```python
# As viewer (public only)
images = manager.get_stream_images(
    stream_id="stream-001",
    user_id="viewer-123",
    is_owner=False,
    page="stream_gallery"
)

# As owner (all)
images = manager.get_stream_images(
    stream_id="stream-001",
    user_id="owner-456",
    is_owner=True,
    page="stream_gallery"
)
```

### Delete Image
```python
manager.delete_stream_image(stream_id="stream-001", image_id="img-uuid")
```

### Get Statistics
```python
# Image stats
stats = manager.get_image_stats("stream-001")
# → {"total": 50, "public": 40, "private": 10, "total_size_mb": 250, "most_viewed": 125}

# Cache stats
cache_stats = manager.cache.get_cache_stats()
# → {"memory_used_mb": 450, "memory_max_mb": 500, "cached_items": 87, "ttl_hours": 24}
```

---

## Streamlit UI Components

### Import
```python
from stream_images_ui import (
    get_image_manager,
    render_stream_image_uploader,
    render_stream_images_gallery,
    render_page_cache_manager,
    get_cached_image_display,
    get_stream_image_stats
)
```

### Upload Widget
```python
image_id = render_stream_image_uploader(
    stream_id="stream-001",
    is_owner=True,  # Only show for owner
    page="stream_details"
)
```

### Gallery Display
```python
render_stream_images_gallery(
    stream_id="stream-001",
    is_owner=is_owner,
    user_id=user_id,
    page="stream_gallery"
)
```

### Cache Management (Sidebar)
```python
render_page_cache_manager(page="stream_gallery")
```

### Image Browser (Multiple Streams)
```python
render_stream_image_browser(page="stream_browser")
```

---

## Streamlit Caching Decorators

### Already Implemented
```python
@st.cache_resource  # Singleton manager
def get_image_manager() -> StreamImageManager:
    return StreamImageManager(...)

@st.cache_data(ttl=3600)  # 1-hour cache for display strings
def get_cached_image_display(image_id: str, stream_id: str, page: str) -> Optional[str]:
    return base64_encoded_image

@st.cache_data(ttl=1800)  # 30-min cache for stats
def get_stream_image_stats(stream_id: str, page: str) -> dict:
    return manager.get_image_stats(stream_id)
```

---

## Cache Behavior

### Memory Cache Lifecycle
```
Upload Image
    ↓
Add to Memory + Disk
    ↓
Access within 24h → Memory cache hit (fast)
    ↓
After 24h TTL → Expired, reload from disk
    ↓
Memory > 90% → LRU eviction (oldest 20%)
    ↓
After eviction → Disk cache preserved
```

### Page-Scoped Cache
```
Page A (stream_details)  → Isolated cache namespace "stream_details:image_id"
Page B (stream_gallery)  → Isolated cache namespace "stream_gallery:image_id"
Page C (settings)        → No image cache

Benefits:
- No cross-page interference
- Independent memory limits
- Faster cache lookups
```

---

## Access Control

### ImageVisibility Enum
```python
ImageVisibility.PUBLIC      # Visible to all
ImageVisibility.PRIVATE     # Owner only
ImageVisibility.SUBSCRIBERS # Subscribers only (future)
```

### Enforcement
```
get_stream_images(is_owner=False) → Filter to PUBLIC only
get_stream_images(is_owner=True)  → Return all
```

---

## Directory Structure

```
project_root/
├── stream_images/
│   ├── stream-001/              # Images for stream-001
│   │   ├── uuid_photo.jpg       # Original (5 MB)
│   │   ├── uuid_thumb.jpg       # Thumbnail (50 KB)
│   │   └── ...
│   ├── stream-002/              # Images for stream-002
│   │   └── ...
│   └── images_metadata.json     # All metadata index
│
├── image_cache/
│   ├── cache_metadata.json      # Cache metadata
│   ├── stream_details_image_id.img
│   └── ...
│
├── stream_images.py             # Core system
├── stream_images_ui.py          # UI components
└── config.py                    # Settings
```

---

## Common Patterns

### In streamlit_app.py

```python
# Initialization
import streamlit as st
from stream_images_ui import render_stream_images_gallery

# Session state not needed (manager is cached via @st.cache_resource)

# In your page
if page == "Live Stream":
    st.title("🔴 Live Stream")
    
    # Upload (owner)
    if is_owner:
        render_stream_image_uploader(stream_id, is_owner=True, page="stream")
    
    # Display (all)
    render_stream_images_gallery(stream_id, is_owner, user_id, page="stream")
    
    # Manage (sidebar)
    render_page_cache_manager(page="stream")
```

---

## Performance Tips

### Reduce Memory Usage
```python
# In .env
export IMAGE_CACHE_MAX_MEMORY_MB=300  # Lower from 500
```

### Faster Access (Longer TTL)
```python
export IMAGE_CACHE_TTL_HOURS=72  # 3 days instead of 1
```

### Optimize for Videos
```python
# In stream_manager.py - Auto-generate thumbnail
from stream_images import StreamImageManager, ImageVisibility

manager = get_image_manager()
thumbnail = create_thumbnail_from_video(video_path, timestamp=5)
manager.upload_stream_image(
    stream_id=stream_id,
    image_data=thumbnail,
    filename="auto_thumbnail.jpg",
    visibility=ImageVisibility.PUBLIC,
    page="stream_auto"
)
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Images missing | Memory evicted | Check disk cache, reload |
| Slow load | Disk cache miss | Increase TTL or add SSD |
| Private image visible | is_owner=True incorrectly | Verify user ownership |
| Cache grows huge | LRU broken | Check config, restart |
| Out of memory | Cache limit too high | Lower IMAGE_CACHE_MAX_MEMORY_MB |

---

## Monitoring

### Check Cache Health
```python
manager = get_image_manager()
stats = manager.cache.get_cache_stats()

print(f"Memory: {stats['memory_used_mb']}/{stats['memory_max_mb']} MB")
print(f"Items: {stats['cached_items']}")
print(f"TTL: {stats['ttl_hours']}h")
```

### Monitor in Streamlit
```python
with st.sidebar.expander("Cache Stats"):
    manager = get_image_manager()
    cache_stats = manager.cache.get_cache_stats()
    st.metric("Memory", f"{cache_stats['memory_used_mb']} MB")
    st.metric("Items", cache_stats['cached_items'])
```

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `stream_images.py` | Core classes | 460 |
| `stream_images_ui.py` | Streamlit UI | 350 |
| `STREAM_IMAGES.md` | Full docs | 350 |
| `STREAM_IMAGES_INTEGRATION.md` | Integration guide | 300 |
| `STREAM_IMAGES_COMPLETE.md` | Summary | 400 |

---

## Cheat Sheet

```python
# Import
from stream_images_ui import get_image_manager, render_stream_images_gallery

# Use
manager = get_image_manager()
manager.upload_stream_image(stream_id, image_bytes, filename, visibility, page=page)
images = manager.get_stream_images(stream_id, user_id, is_owner, page=page)
render_stream_images_gallery(stream_id, is_owner, user_id, page=page)

# Cache
manager.cache.get_cache_stats()          # Monitor memory
manager.cache.clear_page_cache(page)    # Clear specific page
st.cache_data.clear()                    # Clear all Streamlit cache
```

---

## Support

**For detailed info:**
- `STREAM_IMAGES.md` – Full feature documentation
- `STREAM_IMAGES_INTEGRATION.md` – Step-by-step setup
- `STREAM_IMAGES_COMPLETE.md` – Implementation summary

**For API details:**
- `stream_images.py` – Source code with docstrings
- `stream_images_ui.py` – UI functions with examples

---

**Version:** 1.0.0 | **Status:** Production Ready ✅
