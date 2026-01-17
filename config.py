"""
Configuration settings for Stream & Upload Hub
"""

from pathlib import Path

# Application Settings
APP_NAME = "Stream & Upload Hub"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A comprehensive platform for video uploads and streaming"

# Directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
STREAMS_DIR = BASE_DIR / "streams"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"
STREAM_IMAGES_DIR = BASE_DIR / "stream_images"
IMAGE_CACHE_DIR = BASE_DIR / "image_cache"
USERS_DIR = BASE_DIR / "users"
USERS_HISTORY_DIR = BASE_DIR / "users" / "history"

# File Upload Settings
MAX_UPLOAD_SIZE_MB = 500  # Maximum file size in MB
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.flac', '.m4a'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

# User Settings (8-Point Stats System)
MAX_WATCH_HISTORY_ENTRIES = 1000
ENABLE_USER_ANALYTICS = True
USER_SUBSCRIPTION_DAYS = 365  # Default subscription length

# Stream Image Settings
MAX_STREAM_IMAGES_PER_STREAM = 50
MAX_IMAGE_UPLOAD_SIZE_MB = 20
IMAGE_CACHE_MAX_MEMORY_MB = 500
IMAGE_CACHE_TTL_HOURS = 24

# Streaming Settings
DEFAULT_RESOLUTION = "1080p"
DEFAULT_BITRATE = "5000 kbps"
STREAM_TIMEOUT_MINUTES = 120  # Stream timeout in minutes
SUPPORTED_RESOLUTIONS = ["720p", "1080p", "4K", "2K", "480p"]
SUPPORTED_BITRATES = ["1000 kbps", "2500 kbps", "5000 kbps", "8000 kbps", "12000 kbps"]

# Video Processing
VIDEO_CODEC = "h264"
AUDIO_CODEC = "aac"
CONTAINER_FORMAT = "mp4"

# Stream Types
STREAM_TYPES = ["RTMP", "HLS", "DASH"]
DEFAULT_STREAM_TYPE = "HLS"

# UI Settings
THEME_COLOR = "#FF0000"  # Red for streaming/live
SIDEBAR_WIDTH = 300

# Database Settings (if needed)
USE_DATABASE = False
DATABASE_PATH = BASE_DIR / "app_data.db"

# Logging Settings
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "app.log"

# Auto-cleanup Settings
AUTO_CLEANUP_ENABLED = True
CLEANUP_AGE_DAYS = 7  # Clean files older than 7 days

# Feature Flags
ENABLE_LIVE_RECORDING = True
ENABLE_VOD = True
ENABLE_TRANSCODING = False  # Requires ffmpeg
ENABLE_ANALYTICS = True
ENABLE_USER_AUTH = False

# API Settings
API_ENABLED = False
API_PORT = 8000
API_HOST = "0.0.0.0"

# Storage Backend Configuration
STORAGE_BACKEND = "local"  # Options: "local", "s3"
AWS_REGION = "us-east-1"
AWS_S3_BUCKET = "stream-upload-hub"  # Will use env var AWS_S3_BUCKET if set
AWS_ACCESS_KEY = None  # Will use env vars if not set
AWS_SECRET_KEY = None  # Will use env vars if not set

# P2P NFS / Community Settings
P2P_ENABLED = False  # Enable peer-to-peer file sharing
P2P_PORT = 6881  # Port for P2P connections
P2P_NODE_NAME = "stream-hub-node"  # Local node identifier

# Community Notepad Settings
COMMUNITY_NOTEPAD_ENABLED = True
NOTEPAD_STORAGE_PATH = BASE_DIR / "community_notes"
NOTEPAD_MAX_SIZE_MB = 10
NOTEPAD_AUTO_SYNC = True  # Auto-sync with peers if P2P enabled

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
STREAMS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
NOTEPAD_STORAGE_PATH.mkdir(exist_ok=True)
