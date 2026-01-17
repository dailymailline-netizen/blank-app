"""
Utility functions for Stream & Upload Hub
"""

import os
from pathlib import Path
from datetime import datetime
import json


def get_video_metadata(file_path):
    """Extract metadata from video file."""
    try:
        import cv2
        
        cap = cv2.VideoCapture(file_path)
        metadata = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration_seconds": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        cap.release()
        return metadata
    except Exception as e:
        return {"error": str(e)}


def format_file_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_video_file(file_path):
    """Validate if file is a valid video."""
    valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    file_ext = Path(file_path).suffix.lower()
    return file_ext in valid_extensions


def create_stream_metadata(stream_info):
    """Create metadata file for stream."""
    metadata = {
        **stream_info,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    return metadata


def save_stream_config(stream_info, save_path):
    """Save stream configuration to JSON file."""
    try:
        with open(save_path, 'w') as f:
            json.dump(stream_info, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving stream config: {e}")
        return False


def load_stream_config(config_path):
    """Load stream configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading stream config: {e}")
        return None


def get_directory_size(path):
    """Calculate total size of directory."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total += os.path.getsize(filepath)
    return total


def clean_old_files(directory, days=7):
    """Remove files older than specified days."""
    import time
    from pathlib import Path
    
    now = time.time()
    cutoff = now - (days * 86400)
    removed_count = 0
    
    for file_path in Path(directory).glob('*'):
        if file_path.is_file():
            if os.path.getctime(file_path) < cutoff:
                os.remove(file_path)
                removed_count += 1
    
    return removed_count
