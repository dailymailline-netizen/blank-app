"""
Stream & Upload Hub - Usage Examples and Code Snippets
"""

# ============================================================================
# EXAMPLE 1: Using StreamManager to create and manage streams
# ============================================================================

from stream_manager import StreamManager, StreamStats
from pathlib import Path

# Initialize stream manager
streams_dir = Path("streams")
manager = StreamManager(streams_dir)

# Create a new stream
stream_id = manager.create_stream(
    name="Gaming Stream",
    description="Live gaming session",
    resolution="1080p",
    bitrate="8000 kbps"
)
print(f"Created stream: {stream_id}")

# Get stream info
stream_info = manager.get_stream(stream_id)
print(f"Stream status: {stream_info['status']}")

# Update stream statistics
stats = StreamStats(
    viewers=42,
    upload_speed=7.8,
    bitrate=8000.0,
    frames_per_second=60.0,
    duration_seconds=300,
    resolution="1080p"
)
manager.update_stream_stats(stream_id, stats)

# List active streams
active_streams = manager.list_active_streams()
print(f"Active streams: {len(active_streams)}")

# Stop the stream
manager.stop_stream(stream_id)


# ============================================================================
# EXAMPLE 2: Using VideoProcessor to extract video information
# ============================================================================

from stream_manager import VideoProcessor

video_path = "uploads/sample_video.mp4"

# Get video duration
duration = VideoProcessor.get_video_duration(video_path)
print(f"Video duration: {duration} seconds")

# Get video resolution
width, height = VideoProcessor.get_video_resolution(video_path)
print(f"Video resolution: {width}x{height}")

# Create thumbnail
thumbnail_path = "uploads/thumbnail.png"
success = VideoProcessor.create_thumbnail(video_path, thumbnail_path, timestamp=5)
if success:
    print(f"Thumbnail created: {thumbnail_path}")


# ============================================================================
# EXAMPLE 3: Using utility functions for file management
# ============================================================================

from utils import (
    get_video_metadata,
    format_file_size,
    validate_video_file,
    get_directory_size
)

# Validate video file
video_path = "uploads/my_video.mp4"
if validate_video_file(video_path):
    print("✓ Valid video file")

# Get video metadata
metadata = get_video_metadata(video_path)
print(f"Video metadata: {metadata}")

# Format file size nicely
file_size = 1024 * 1024 * 750  # 750 MB
size_str = format_file_size(file_size)
print(f"File size: {size_str}")

# Get directory size
upload_dir_size = get_directory_size("uploads")
print(f"Upload directory size: {format_file_size(upload_dir_size)}")


# ============================================================================
# EXAMPLE 4: Using AnalyticsTracker to monitor user activity
# ============================================================================

from stream_manager import AnalyticsTracker
from pathlib import Path

# Initialize analytics tracker
tracker = AnalyticsTracker(Path("logs"))

# Log stream events
stream_id = "stream_12345"
viewer_id = "user_abc123"

tracker.log_viewer_join(stream_id, viewer_id)
tracker.log_viewer_leave(stream_id, viewer_id, watch_duration=600)

# Log video views
tracker.log_video_view("video_xyz789", duration_watched=300)

# Get stream analytics
analytics = tracker.get_stream_analytics(stream_id)
print(f"Stream analytics: {analytics}")

# Save analytics to file
tracker.save_analytics(Path("logs/analytics.json"))


# ============================================================================
# EXAMPLE 5: Working with application configuration
# ============================================================================

from config import (
    UPLOAD_DIR,
    STREAMS_DIR,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_VIDEO_EXTENSIONS,
    SUPPORTED_RESOLUTIONS,
    SUPPORTED_BITRATES,
    DEFAULT_STREAM_TYPE
)

print(f"Upload directory: {UPLOAD_DIR}")
print(f"Max upload size: {MAX_UPLOAD_SIZE_MB} MB")
print(f"Allowed extensions: {ALLOWED_VIDEO_EXTENSIONS}")
print(f"Supported resolutions: {SUPPORTED_RESOLUTIONS}")
print(f"Default stream type: {DEFAULT_STREAM_TYPE}")


# ============================================================================
# EXAMPLE 6: Streamlit integration example
# ============================================================================

"""
In your Streamlit app, you can use these modules like this:

import streamlit as st
from stream_manager import StreamManager, VideoProcessor
from utils import get_video_metadata, format_file_size
from config import UPLOAD_DIR, STREAMS_DIR

# Initialize managers
stream_manager = StreamManager(STREAMS_DIR)

# File upload
uploaded_file = st.file_uploader("Upload video")
if uploaded_file:
    # Save file
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Get metadata
    metadata = get_video_metadata(str(file_path))
    st.write(f"Duration: {metadata.get('duration_seconds')} seconds")
    
    # Display size
    file_size = format_file_size(uploaded_file.size)
    st.write(f"File size: {file_size}")

# Stream management
with st.form("stream_form"):
    stream_name = st.text_input("Stream name")
    resolution = st.selectbox("Resolution", ["720p", "1080p", "4K"])
    
    if st.form_submit_button("Create Stream"):
        stream_id = stream_manager.create_stream(
            stream_name,
            "Description",
            resolution,
            "5000 kbps"
        )
        st.success(f"Stream created: {stream_id}")
"""


# ============================================================================
# EXAMPLE 7: Custom configuration usage
# ============================================================================

"""
To customize the application, edit config.py:

# Increase max upload size to 2GB
MAX_UPLOAD_SIZE_MB = 2000

# Add custom video extensions
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.webp'}

# Add new resolution support
SUPPORTED_RESOLUTIONS = ["360p", "480p", "720p", "1080p", "2K", "4K", "8K"]

# Add custom bitrates
SUPPORTED_BITRATES = ["500 kbps", "1000 kbps", "2500 kbps", "5000 kbps", "10000 kbps"]

# Enable new features
ENABLE_TRANSCODING = True
ENABLE_USER_AUTH = True
ENABLE_ANALYTICS = True
"""


if __name__ == "__main__":
    print("Stream & Upload Hub - Usage Examples")
    print("=" * 60)
    print("\nTo see these examples in action:")
    print("1. Import the modules: from stream_manager import StreamManager")
    print("2. Follow the examples above")
    print("3. Check streamlit_app.py for full implementation")
    print("\nFor more information, see:")
    print("- README.md")
    print("- QUICKSTART.md")
    print("- PROJECT_SUMMARY.md")
