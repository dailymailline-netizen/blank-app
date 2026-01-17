# Integration Guide: Adding Stream Images to streamlit_app.py

This guide shows how to integrate the new Stream Image Management system into your Streamlit application.

---

## Step 1: Add Cache Manager to Session State

**In `streamlit_app.py` initialization (top of file):**

```python
import streamlit as st
from stream_images_ui import (
    get_image_manager,
    render_stream_image_uploader,
    render_stream_images_gallery,
    render_page_cache_manager
)

# Initialize session state (existing pattern)
if 'uploaded_videos' not in st.session_state:
    st.session_state.uploaded_videos = []
if 'streams' not in st.session_state:
    st.session_state.streams = []

# NEW: Image manager (singleton, cached)
# No need to add to session_state - use get_image_manager() which is cached
```

---

## Step 2: Update Live Stream Page

**Replace the existing "Live Stream" page with:**

```python
def page_live_stream():
    """Live Stream page with image management"""
    st.title("🔴 Live Stream")
    
    tab1, tab2, tab3 = st.tabs(["Stream Control", "Stream Images", "Gallery"])
    
    # ========== TAB 1: Stream Control ==========
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            stream_name = st.text_input("Stream Name", key="stream_name_input")
            resolution = st.selectbox("Resolution", config.SUPPORTED_RESOLUTIONS)
        
        with col2:
            stream_description = st.text_area("Description", key="stream_desc_input")
            bitrate = st.selectbox("Bitrate", config.SUPPORTED_BITRATES)
        
        if st.button("🟢 Start Stream"):
            if stream_name:
                stream_info = {
                    "name": stream_name,
                    "description": stream_description,
                    "resolution": resolution,
                    "bitrate": bitrate,
                    "started_at": datetime.now().isoformat(),
                    "status": "active"
                }
                st.session_state.streams.append(stream_info)
                st.success(f"✅ Stream '{stream_name}' started!")
                st.rerun()
            else:
                st.error("Please enter a stream name")
        
        st.divider()
        
        # Display active streams
        if st.session_state.streams:
            st.subheader("Active Streams")
            for idx, stream in enumerate(st.session_state.streams):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{stream['name']}** - {stream['resolution']} @ {stream['bitrate']}")
                with col2:
                    if st.button("🛑 Stop", key=f"stop_stream_{idx}"):
                        stream["status"] = "stopped"
                        st.rerun()
    
    # ========== TAB 2: Upload Images ==========
    with tab2:
        if st.session_state.streams:
            stream_idx = st.selectbox(
                "Select Stream",
                range(len(st.session_state.streams)),
                format_func=lambda i: st.session_state.streams[i]['name']
            )
            
            stream_id = f"stream_{stream_idx}_{st.session_state.streams[stream_idx]['started_at']}"
            
            st.write(f"**Uploading images for:** {st.session_state.streams[stream_idx]['name']}")
            
            # Image uploader widget
            render_stream_image_uploader(
                stream_id=stream_id,
                is_owner=True,
                page="stream_details"
            )
        else:
            st.info("Start a stream first to upload images")
    
    # ========== TAB 3: Image Gallery ==========
    with tab3:
        if st.session_state.streams:
            stream_idx = st.selectbox(
                "Select Stream to View",
                range(len(st.session_state.streams)),
                format_func=lambda i: st.session_state.streams[i]['name'],
                key="stream_gallery_select"
            )
            
            stream_id = f"stream_{stream_idx}_{st.session_state.streams[stream_idx]['started_at']}"
            
            # Image gallery with caching
            render_stream_images_gallery(
                stream_id=stream_id,
                is_owner=True,
                user_id="owner",
                page="stream_gallery"
            )
        else:
            st.info("No active streams")
    
    # Cache management controls
    render_page_cache_manager(page="stream")
```

---

## Step 3: Update Settings Page

**Add image cache info to Settings page:**

```python
def page_settings():
    """Settings page with cache info"""
    st.title("⚙️ Settings")
    
    # ... existing settings ...
    
    st.divider()
    st.subheader("📸 Image Cache Settings")
    
    manager = get_image_manager()
    cache_stats = manager.cache.get_cache_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Memory Used", f"{cache_stats['memory_used_mb']} MB")
    with col2:
        st.metric("Memory Max", f"{cache_stats['memory_max_mb']} MB")
    with col3:
        st.metric("Cached Items", cache_stats['cached_items'])
    with col4:
        st.metric("TTL", f"{cache_stats['ttl_hours']}h")
    
    if st.button("Clear Image Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
        st.rerun()
    
    # Configuration info
    st.write("**Configuration:**")
    st.code(f"""
MAX_STREAM_IMAGES_PER_STREAM = {config.MAX_STREAM_IMAGES_PER_STREAM}
MAX_IMAGE_UPLOAD_SIZE_MB = {config.MAX_IMAGE_UPLOAD_SIZE_MB}
IMAGE_CACHE_MAX_MEMORY_MB = {config.IMAGE_CACHE_MAX_MEMORY_MB}
IMAGE_CACHE_TTL_HOURS = {config.IMAGE_CACHE_TTL_HOURS}
    """)
```

---

## Step 4: Create Complete Example

Here's a complete minimal example to paste into `streamlit_app.py`:

```python
"""
Complete Stream & Upload Hub with Image Management
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# Configuration
import config
from stream_manager import StreamManager
from utils import get_video_files
from stream_images_ui import (
    get_image_manager,
    render_stream_image_uploader,
    render_stream_images_gallery,
    render_page_cache_manager
)

# Page config
st.set_page_config(page_title="Stream & Upload Hub", layout="wide")

# Initialize session state
if 'uploaded_videos' not in st.session_state:
    st.session_state.uploaded_videos = []
if 'streams' not in st.session_state:
    st.session_state.streams = []

# Sidebar navigation
st.sidebar.title("🎬 Stream & Upload Hub")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Upload Video", "Live Stream", "Video Library", "Settings"]
)

# ========== HOME PAGE ==========
if page == "Home":
    st.title("🎬 Stream & Upload Hub")
    st.write("Manage your videos, streams, and images all in one place.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Uploaded Videos", len(st.session_state.uploaded_videos))
    with col2:
        st.metric("Active Streams", len([s for s in st.session_state.streams if s['status'] == 'active']))
    with col3:
        manager = get_image_manager()
        total_images = sum(len(imgs) for imgs in manager.stream_images.values())
        st.metric("Stream Images", total_images)

# ========== UPLOAD VIDEO PAGE ==========
elif page == "Upload Video":
    st.title("📤 Upload Video")
    
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=list(config.ALLOWED_VIDEO_EXTENSIONS)
    )
    
    if uploaded_file:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / (1024*1024):.2f} MB")
        
        if st.button("Upload"):
            upload_dir = config.UPLOAD_DIR
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.uploaded_videos.append({
                "name": uploaded_file.name,
                "path": str(file_path),
                "size": uploaded_file.size,
                "uploaded_at": datetime.now().isoformat()
            })
            
            st.success("✅ Video uploaded!")

# ========== LIVE STREAM PAGE (WITH IMAGES) ==========
elif page == "Live Stream":
    st.title("🔴 Live Stream")
    
    tab1, tab2, tab3 = st.tabs(["Stream Control", "Upload Images", "Gallery"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            stream_name = st.text_input("Stream Name")
            resolution = st.selectbox("Resolution", config.SUPPORTED_RESOLUTIONS)
        with col2:
            stream_desc = st.text_area("Description")
            bitrate = st.selectbox("Bitrate", config.SUPPORTED_BITRATES)
        
        if st.button("🟢 Start Stream"):
            if stream_name:
                stream_id = f"stream_{len(st.session_state.streams)}_{datetime.now().isoformat()}"
                stream_info = {
                    "id": stream_id,
                    "name": stream_name,
                    "description": stream_desc,
                    "resolution": resolution,
                    "bitrate": bitrate,
                    "started_at": datetime.now().isoformat(),
                    "status": "active"
                }
                st.session_state.streams.append(stream_info)
                st.success("✅ Stream started!")
                st.rerun()
        
        st.divider()
        if st.session_state.streams:
            st.subheader("Active Streams")
            for idx, s in enumerate(st.session_state.streams):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{s['name']}** – {s['resolution']} @ {s['bitrate']}")
                with col2:
                    if st.button("Stop", key=f"stop_{idx}"):
                        s['status'] = 'stopped'
                        st.rerun()
    
    with tab2:
        if st.session_state.streams:
            active = [s for s in st.session_state.streams if s['status'] == 'active']
            if active:
                stream_idx = st.selectbox(
                    "Select Stream",
                    range(len(active)),
                    format_func=lambda i: active[i]['name']
                )
                stream_id = active[stream_idx]['id']
                
                render_stream_image_uploader(
                    stream_id=stream_id,
                    is_owner=True,
                    page="stream_details"
                )
            else:
                st.info("No active streams")
        else:
            st.info("No streams. Create one above.")
    
    with tab3:
        if st.session_state.streams:
            all_streams = st.session_state.streams
            if all_streams:
                stream_idx = st.selectbox(
                    "Select Stream",
                    range(len(all_streams)),
                    format_func=lambda i: all_streams[i]['name'],
                    key="gallery_select"
                )
                stream_id = all_streams[stream_idx]['id']
                
                render_stream_images_gallery(
                    stream_id=stream_id,
                    is_owner=True,
                    page="stream_gallery"
                )
    
    render_page_cache_manager(page="stream")

# ========== VIDEO LIBRARY PAGE ==========
elif page == "Video Library":
    st.title("📺 Video Library")
    
    if st.session_state.uploaded_videos:
        for video in st.session_state.uploaded_videos:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{video['name']}** – {video['size']/(1024*1024):.2f} MB")
                st.caption(f"Uploaded: {video['uploaded_at'][:10]}")
            with col2:
                st.write("")
    else:
        st.info("No videos uploaded yet")

# ========== SETTINGS PAGE ==========
elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("📸 Image Cache")
    manager = get_image_manager()
    cache_stats = manager.cache.get_cache_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Memory", f"{cache_stats['memory_used_mb']} MB")
    with col2:
        st.metric("Max", f"{cache_stats['memory_max_mb']} MB")
    with col3:
        st.metric("Items", cache_stats['cached_items'])
    with col4:
        st.metric("TTL", f"{cache_stats['ttl_hours']}h")
    
    if st.button("🧹 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
        st.rerun()
```

---

## Step 5: Update Requirements

Add to `requirements.txt`:

```
pillow>=10.0.0
```

This is for image processing (thumbnail generation).

---

## Directory Structure

After integration, your project will have:

```
/workspaces/blank-app/
├── stream_images/           # NEW: Stream image storage
│   └── {stream_id}/
│       ├── {image_id}_original.jpg
│       ├── {image_id}_thumb.jpg
│       └── ...
├── image_cache/             # NEW: Image cache (disk backup)
├── stream_images.py         # NEW: Image manager classes
├── stream_images_ui.py      # NEW: Streamlit UI components
├── streamlit_app.py         # MODIFIED: Add image pages
├── config.py                # MODIFIED: Add image config
└── STREAM_IMAGES.md         # NEW: Documentation
```

---

## Testing

### Test locally:

```bash
cd /workspaces/blank-app
pip install pillow
streamlit run streamlit_app.py
```

### Navigate to:
1. **Live Stream** tab → Start a stream
2. **Upload Images** tab → Upload test image
3. **Gallery** tab → View cached image
4. Check **Settings** → View cache stats

---

## Performance Tips

1. **Adjust Memory Limit** (for servers):
   ```python
   # In config.py
   IMAGE_CACHE_MAX_MEMORY_MB = 1000  # 1 GB for production
   ```

2. **Extend Cache TTL** (for frequently accessed):
   ```python
   IMAGE_CACHE_TTL_HOURS = 72  # 3 days
   ```

3. **Enable S3 Storage** (for scalability):
   ```python
   # In .env
   STORAGE_BACKEND=s3
   AWS_S3_BUCKET=my-bucket
   ```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Cache fills up | LRU eviction auto-triggers; monitor via Settings |
| Images slow to load | Increase TTL or check disk I/O |
| Memory spikes | Use page-scoped caching; clear per-page |
| Private images visible | Verify `is_owner` flag in UI render |

---

## Next Steps

1. ✅ Copy `stream_images.py` and `stream_images_ui.py` to project
2. ✅ Update `config.py` with image settings
3. ✅ Update `streamlit_app.py` with Live Stream page
4. ✅ Add `pillow` to `requirements.txt`
5. ✅ Test locally with `streamlit run streamlit_app.py`
6. ✅ Review STREAM_IMAGES.md for full feature documentation

You're ready to go! 🎉
