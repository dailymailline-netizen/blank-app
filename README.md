# 🎥 Stream & Upload Hub v2.0

A comprehensive Streamlit-based application framework for **video uploads, streaming, and collaborative note management** with cloud storage and P2P networking support.

**✨ New in v2.0:** AWS S3 storage • P2P NFS • Community notepad • Multi-instance deployment

## Features

### 📤 Video Upload
- Multi-format support (MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V)
- Drag-and-drop interface
- File validation and metadata extraction
- Multi-backend storage (Local, AWS S3)

### 📡 Live Streaming  
- Create and manage live streams
- Configurable resolution (720p, 1080p, 4K, 2K, 480p)
- Bitrate selection (1-12 Mbps)
- Real-time stream status monitoring

### 📚 Video Library
- Browse all uploaded videos
- In-app video playback
- File information and statistics
- Cross-instance availability (with S3)

### 📝 Community Notepad ⭐ NEW
- Collaborative note-taking with version tracking
- Private/shared note management
- Full-text search (title, content, tags)
- P2P synchronization across instances
- Contributor tracking and sync history

### ☁️ Cloud Storage ⭐ NEW
- **AWS S3 Integration** – Global video distribution with CloudFront CDN
- **Local Storage** – Development and edge deployments
- **NFS Support** – Team collaboration with shared storage
- **Storage Abstraction** – Switch backends with config change

### 🔗 P2P Networking ⭐ NEW
- Automatic peer discovery (Avahi/mDNS)
- Distributed note synchronization
- Conflict-free sync via version numbers
- Works across LAN/WAN with optional coordinator

## Architecture

```
Streamlit UI Layer
    ↓
Storage Abstraction (Local/S3/NFS)
    ↓
┌─────────────────────┬──────────────┬─────────────────┐
│ Video Storage       │ Stream Mgmt  │ Community Notes │
├─────────────────────┼──────────────┼─────────────────┤
│ Local FS / S3 / NFS │ JSON files   │ P2P Sync Queue  │
└─────────────────────┴──────────────┴─────────────────┘
```

## Quick Start

### Option 1: Local (Development)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option 2: AWS S3 (Production)
```bash
export STORAGE_BACKEND=s3
export AWS_S3_BUCKET=your-bucket
export AWS_REGION=us-east-1
streamlit run streamlit_app.py
```

### Option 3: Multi-Instance with P2P
```bash
# See P2P_NFS_SETUP.md for full infrastructure guide
export P2P_ENABLED=true
export STORAGE_BACKEND=local
docker-compose -f docker-compose-p2p.yml up -d
```

**📖 For detailed setup:** See [CLOUD_SETUP.md](CLOUD_SETUP.md)

## Project Structure

```
blank-app/
├── streamlit_app.py           # Multi-page Streamlit UI
├── config.py                  # Configuration (with cloud settings)
├── storage_backend.py         # Storage abstraction layer ⭐
├── community_notepad.py       # P2P notepad system ⭐
├── stream_manager.py          # Stream lifecycle management
├── utils.py                   # Helper functions
├── requirements.txt           # Python dependencies
│
├── CLOUD_SETUP.md            # Quick start guide ⭐
├── CLOUD_ARCHITECTURE.md     # System design ⭐
├── P2P_NFS_SETUP.md          # Infrastructure guide ⭐
├── IMPLEMENTATION_SUMMARY.md # Build overview ⭐
│
├── docker-compose-p2p.yml    # Multi-instance deployment ⭐
├── nginx.conf                # Load balancer config ⭐
├── deploy.sh                 # Deployment automation ⭐
├── .env.example              # Configuration template ⭐
│
├── uploads/                  # Video storage (auto-created)
├── streams/                  # Stream metadata (auto-created)
├── community_notes/          # Shared notes (auto-created) ⭐
└── logs/                     # Application logs (auto-created)
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- 2GB+ disk space (more for video storage)

### Setup

1. **Clone/navigate to project:**
```bash
cd blank-app
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Edit with your settings
export $(cat .env | xargs)
```

5. **Run the application:**
```bash
streamlit run streamlit_app.py
```
Access at `http://localhost:8501`

### Using Deployment Script
```bash
./deploy.sh                    # Interactive setup
./deploy.sh docker            # Docker deployment
./deploy.sh help              # Show options
```

## Usage

### Application Pages

**Home** 🏠
- Dashboard with statistics
- Overview of uploads, streams, and notes
- Quick navigation

**Upload Video** 📤
- Drag-and-drop video upload
- Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V
- Max size: 500 MB (configurable)
- Upload history with metadata

**Live Stream** 📡
- Create and manage live streams
- Resolution: 720p, 1080p, 4K, 2K, 480p
- Bitrate: 1-12 Mbps
- Real-time status monitoring
- Start/stop controls

**Video Library** 📚
- Browse all uploaded videos
- In-app playback
- File information and statistics
- Works across instances (with S3)

**Community Notepad** 📝 ⭐ NEW
- Create collaborative notes
- Share/unshare toggles (private/public)
- Version history tracking
- Search by title, content, or tags
- P2P sync across instances
- Contributor list and sync events

**Settings** ⚙️
- Upload size configuration
- Stream timeout settings
- Storage backend status (Local/S3/NFS)
- S3 connection testing
- P2P network status
- Sync history viewer
- Cloud configuration display

## Storage Backends

### Local Storage (Development)
```bash
STORAGE_BACKEND=local
```
- Videos stored in `uploads/` directory
- Single-instance only
- No setup required

### AWS S3 (Production)
```bash
STORAGE_BACKEND=s3
AWS_S3_BUCKET=my-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY=xxxxx
AWS_SECRET_KEY=xxxxx
```
- Global video distribution
- CloudFront CDN integration
- Multi-instance ready
- Automatic failover

### NFS + P2P (Team)
```bash
STORAGE_BACKEND=local
P2P_ENABLED=true
NOTEPAD_STORAGE_PATH=/mnt/nfs/notes
```
- Shared NFS mount for notes
- Automatic peer discovery (Avahi/mDNS)
- P2P note synchronization
- Up to ~20 instances

## Configuration

### Environment Variables
See `.env.example` for full list:

```bash
# Storage backend
STORAGE_BACKEND=local          # local, s3
AWS_S3_BUCKET=bucket-name      # For S3
AWS_REGION=us-east-1

# P2P Settings
P2P_ENABLED=false
NOTEPAD_AUTO_SYNC=true

# Directories
UPLOAD_DIR=./uploads
NOTEPAD_STORAGE_PATH=./community_notes
```

Load with:
```bash
export $(cat .env | xargs)
streamlit run streamlit_app.py
```

### Python Config
Edit `config.py` to customize:

```python
# File Upload
MAX_UPLOAD_SIZE_MB = 500

# Streaming
DEFAULT_RESOLUTION = "1080p"
DEFAULT_BITRATE = "5000 kbps"

# Notepad
COMMUNITY_NOTEPAD_ENABLED = True
NOTEPAD_MAX_SIZE_MB = 10
```

## Utilities

### Available Functions in `utils.py`

- `get_video_metadata()` - Extract video file metadata
- `format_file_size()` - Convert bytes to human-readable format
- `validate_video_file()` - Validate video file format
- `create_stream_metadata()` - Generate stream metadata
- `save_stream_config()` - Save stream configuration
- `load_stream_config()` - Load stream configuration
- `get_directory_size()` - Calculate directory size
- `clean_old_files()` - Remove old files for maintenance

## Technology Stack

- **Frontend:** Streamlit
- **Video Processing:** OpenCV
- **Image Processing:** Pillow
- **Data Processing:** NumPy
- **Async Support:** aiofiles

## Dependencies

```
streamlit>=1.28.0      # Web framework
opencv-python>=4.8.0   # Video processing
Pillow>=10.0.0         # Image processing
numpy>=1.24.0          # Numerical operations
python-multipart>=0.0.6 # Multipart form data
aiofiles>=23.2.0       # Async file operations
```

## Directory Structure

- **uploads/** - Stores uploaded video files
- **streams/** - Stores stream configuration and data
- **logs/** - Application logs
- **temp/** - Temporary files during processing

## Features Under Development

- [ ] Stream recording to file
- [ ] Video transcoding
- [ ] User authentication
- [ ] REST API
- [ ] Advanced analytics
- [ ] Custom bitrate encoding
- [ ] Multiple stream simultaneous support
- [ ] Stream scheduling

## Troubleshooting

### Application won't start
```bash
pip install -r requirements.txt --upgrade
streamlit run streamlit_app.py
```

### Upload failures
- Check `MAX_UPLOAD_SIZE_MB` in `config.py`
- Verify file format is supported
- Ensure sufficient disk space in uploads directory

### Video playback issues
- Verify video codec is H.264
- Check browser compatibility
- Try different video format

## Performance Tips

1. **Optimize video files** - Use H.264 codec for better compatibility
2. **Manage storage** - Enable auto-cleanup in settings
3. **Monitor streams** - Stop inactive streams to free resources
4. **Batch uploads** - Upload multiple files in sequence

## Future Enhancements

- Cloud storage integration (AWS S3, Google Cloud)
- Advanced video analytics
- Machine learning-based content moderation
- Multi-user support with authentication
- Stream scheduling and automation
- RTMP/HLS protocol support
- CDN integration for streaming

## License

See LICENSE file for details

## Support

For issues, questions, or suggestions, please check the Streamlit documentation at [docs.streamlit.io](https://docs.streamlit.io/)

---

**Version:** 1.0.0  
**Last Updated:** 2025  
**Built with:** Streamlit, OpenCV, Python
