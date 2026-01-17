# Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run streamlit_app.py
```

### Step 3: Open in Browser
Navigate to `http://localhost:8501`

---

## Application Overview

### 🏠 Home Page
- View dashboard with statistics
- See total uploads and active streams
- Quick navigation to all features

### 📤 Upload Video Page
- Drag and drop video files (up to 500MB)
- Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V
- Track upload history with metadata

### 📡 Live Stream Page
- Create and manage live streams
- Configure resolution (720p, 1080p, 4K)
- Select bitrate (2.5-12 Mbps)
- Monitor active streams
- Stop streams when done

### 📚 Video Library
- Browse all uploaded videos
- Play videos directly in the app
- View file information

### ⚙️ Settings
- Configure upload size limits
- Set stream timeout duration
- Clear session data
- View storage information

---

## File Structure

```
uploads/       - All uploaded video files
streams/       - Stream configuration and metadata
logs/          - Application logs
temp/          - Temporary processing files
```

---

## Configuration

Edit `config.py` to customize:
- Maximum upload size
- Supported file types
- Default stream settings
- Auto-cleanup settings

---

## API Reference

### Import Utilities
```python
from utils import get_video_metadata, format_file_size
from stream_manager import StreamManager, VideoProcessor
from config import UPLOAD_DIR, STREAMS_DIR
```

### Common Operations

**Get Video Metadata:**
```python
metadata = get_video_metadata('/path/to/video.mp4')
```

**Format File Size:**
```python
size_str = format_file_size(1024000)  # Returns "1000.00 KB"
```

**Create Stream:**
```python
manager = StreamManager(STREAMS_DIR)
stream_id = manager.create_stream("My Stream", "Description", "1080p", "5000 kbps")
```

---

## Troubleshooting

### App won't start
```bash
pip install --upgrade -r requirements.txt
streamlit run streamlit_app.py --logger.level=debug
```

### Upload issues
- Check available disk space
- Verify file format is supported
- Try a smaller file first

### Stream lag
- Reduce bitrate in stream settings
- Lower resolution
- Close other browser tabs

---

## Features

✅ Video upload with history tracking
✅ Live streaming with configurable settings
✅ Video library with playback
✅ Stream management and monitoring
✅ Session-based state management
✅ Extensible architecture

---

## Next Steps

1. Upload your first video
2. Create a test stream
3. Explore the video library
4. Customize settings
5. Check out advanced features in `stream_manager.py`

---

For more information, see [README.md](README.md)
