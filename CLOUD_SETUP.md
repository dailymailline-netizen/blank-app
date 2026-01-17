# Cloud Integration Setup Guide

This guide covers setting up Stream & Upload Hub with cloud storage, P2P networking, and the community notepad feature.

---

## Quick Start

### Option 1: Local Storage (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Default configuration uses local filesystem storage. Visit http://localhost:8501

---

### Option 2: AWS S3 (Production)

#### Prerequisites
- AWS account with S3 bucket created
- AWS credentials (Access Key + Secret Key)

#### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
STORAGE_BACKEND=s3
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
AWS_ACCESS_KEY=your-access-key
AWS_SECRET_KEY=your-secret-key
```

3. **Load environment:**
```bash
export $(cat .env | xargs)
```

4. **Run the app:**
```bash
streamlit run streamlit_app.py
```

The app will now use S3 for video storage while keeping notes locally (or on NFS for multi-instance).

---

### Option 3: P2P NFS (Multi-Instance Collaboration)

#### Prerequisites
- NFS server set up (see [P2P_NFS_SETUP.md](P2P_NFS_SETUP.md))
- All instances on same network
- Avahi/mDNS installed and running

#### Setup

1. **Mount NFS on each instance:**
```bash
sudo mount -t nfs <nfs-server-ip>:/mnt/nfs/notes /data/notes
sudo mount -t nfs <nfs-server-ip>:/mnt/nfs/videos /data/videos
```

2. **Create `.env` file:**
```bash
STORAGE_BACKEND=local
P2P_ENABLED=true
P2P_NODE_NAME=stream-hub-$(hostname)
NOTEPAD_STORAGE_PATH=/data/notes
```

3. **Run the app:**
```bash
streamlit run streamlit_app.py
```

Instances will auto-discover each other and sync notes via P2P protocol.

---

## Storage Architecture Comparison

| Feature | Local | AWS S3 | NFS | Hybrid |
|---------|-------|--------|-----|--------|
| **Setup Complexity** | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Complex | ⭐⭐⭐⭐ Very Complex |
| **Multi-Instance** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cost** | Free (disk) | $0.023/GB | $200+/month | Hybrid |
| **Scalability** | 1 instance | Unlimited | ~10-20 instances | Unlimited |
| **Data Redundancy** | ❌ None | ✅ Built-in | ⚠️ NFS RAID | ✅ Both |
| **CDN Support** | ❌ No | ✅ CloudFront | ❌ No | ✅ S3+CF |
| **P2P Notes** | ❌ Single | ⚠️ External | ✅ Built-in | ✅ Built-in |

---

## Community Notepad Features

### Creating & Managing Notes

1. **Create Note**
   - Title (required)
   - Content (supports markdown)
   - Tags (comma-separated, optional)

2. **Share & Collaborate**
   - Toggle between private/shared
   - Version tracking (auto-increment)
   - Contributor list
   - Full sync history

3. **Search**
   - Full-text search in title & content
   - Tag-based filtering
   - Recent activity sorting

### P2P Sync

When P2P is enabled:
- New/updated notes sync to all connected peers
- Automatic peer discovery via mDNS
- Conflict resolution via version numbers
- Sync queue tracks pending changes

### API Usage

```python
from community_notepad import CommunityNotepad

notepad = CommunityNotepad("path/to/storage")

# Create
note_id = notepad.create_note("Title", "Content", ["tag1", "tag2"])

# Share
notepad.share_note(note_id)

# Search
results = notepad.search_notes("keyword")

# Get sync history
history = notepad.get_sync_history(limit=50)
```

---

## Docker Deployment

### Single Instance with S3

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
```

Build & run:

```bash
docker build -t stream-hub:latest .

docker run -e STORAGE_BACKEND=s3 \
  -e AWS_S3_BUCKET=my-bucket \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY=xxx \
  -e AWS_SECRET_KEY=xxx \
  -p 8501:8501 \
  stream-hub:latest
```

### Multi-Instance with NFS

Use `docker-compose-p2p.yml` (included in repo):

```bash
docker-compose -f docker-compose-p2p.yml up -d
```

This starts:
- 3 Streamlit instances (ports 8501-8503)
- Nginx load balancer (port 80)
- All instances share NFS mount for notes

Access via: http://localhost

---

## Environment Variables

### Storage Backend

```
STORAGE_BACKEND=local|s3          # Required: storage type
AWS_S3_BUCKET=bucket-name         # For S3
AWS_REGION=us-east-1              # For S3
AWS_ACCESS_KEY=xxx                # For S3 (optional, uses IAM role if not set)
AWS_SECRET_KEY=xxx                # For S3 (optional, uses IAM role if not set)
```

### P2P & Notepad

```
P2P_ENABLED=true|false            # Enable peer discovery
P2P_NODE_NAME=node-identifier     # Custom node name
P2P_PORT=6881                      # P2P discovery port
NOTEPAD_AUTO_SYNC=true|false      # Auto-sync notes to peers
NOTEPAD_STORAGE_PATH=/data/notes  # Where to store notes
```

### Other

```
UPLOAD_DIR=/data/uploads           # Video upload directory
STREAMS_DIR=/data/streams          # Stream metadata directory
STREAMLIT_SERVER_PORT=8501         # Streamlit port
```

---

## Troubleshooting

### S3 Connection Issues

```bash
# Test AWS credentials
aws s3 ls --region us-east-1

# Check boto3 installation
python -c "import boto3; print(boto3.__version__)"

# Enable debug logging
export AWS_DEBUG=true
```

### NFS Mount Issues

```bash
# Check mount status
df -h /data/notes

# Verify NFS server exports
showmount -e <nfs-server-ip>

# Remount if stuck
sudo umount /data/notes
sudo mount -t nfs <nfs-server-ip>:/mnt/nfs/notes /data/notes
```

### P2P Peer Discovery

```bash
# Verify Avahi is running
sudo systemctl status avahi-daemon

# List discovered services
avahi-browse -r _stream-hub._tcp

# If peers aren't discovered, check firewall
sudo ufw allow 5353/udp  # mDNS
```

### Permission Denied Errors

```bash
# For local storage
chmod 755 uploads/ streams/ community_notes/

# For NFS mounts
sudo chmod 755 /data/videos /data/notes

# For Docker volumes
sudo chown -R nobody:nogroup /path/to/volume
```

---

## Performance Tuning

### NFS Performance

```python
# config.py
# Use larger block sizes for better throughput
NFS_RSIZE = 131072      # 128KB
NFS_WSIZE = 131072      # 128KB
NFS_TIMEO = 600         # 60 seconds before retry
```

### S3 Performance

```python
# config.py
S3_MAX_BANDWIDTH = "100MB"  # Limit upload speed
S3_MULTIPART_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks
```

### Notepad Sync

```python
# config.py
P2P_SYNC_INTERVAL = 5       # Sync every 5 seconds
P2P_SYNC_BATCH_SIZE = 50    # Batch sync up to 50 notes
```

---

## Migration Guide

### From Local to S3

1. **Backup local videos:**
```bash
tar -czf backup_local.tar.gz uploads/
```

2. **Upload to S3:**
```bash
aws s3 sync uploads/ s3://my-bucket/uploads/
```

3. **Update config:**
```
STORAGE_BACKEND=s3
AWS_S3_BUCKET=my-bucket
```

4. **Restart app:**
```bash
streamlit run streamlit_app.py
```

### From S3 to NFS

1. **Download from S3:**
```bash
aws s3 sync s3://my-bucket/uploads/ uploads/
```

2. **Upload to NFS:**
```bash
rsync -avz uploads/ <nfs-server>:/mnt/nfs/videos/
```

3. **Update config:**
```
STORAGE_BACKEND=local
UPLOAD_DIR=/data/videos
```

4. **Mount NFS on client:**
```bash
sudo mount -t nfs <nfs-server>:/mnt/nfs/videos /data/videos
```

---

## Monitoring & Logs

### Check logs

```bash
# Streamlit logs
tail -f logs/streamlit.log

# Storage backend logs
tail -f logs/storage.log

# P2P sync logs
tail -f logs/p2p_sync.log
```

### Monitor performance

```python
# Add to streamlit app (in developer mode)
st.write("**Storage Backend:** " + STORAGE_BACKEND)
st.write("**P2P Status:** " + ("Enabled" if P2P_ENABLED else "Disabled"))
```

---

## Support & Resources

- **Streamlit:** https://docs.streamlit.io
- **AWS S3:** https://docs.aws.amazon.com/s3/
- **NFS Setup:** https://ubuntu.com/server/docs/service-nfs
- **Avahi:** https://www.avahi.org/
- **Project Issues:** Check GitHub repository

---

## Next Steps

1. ✅ Choose storage backend (local/S3/NFS)
2. ✅ Configure environment variables
3. ✅ Install dependencies
4. ✅ Run the application
5. ✅ Test community notepad
6. ✅ Enable P2P (optional)
7. ✅ Deploy to production

Refer to [CLOUD_ARCHITECTURE.md](CLOUD_ARCHITECTURE.md) for detailed architectural information.
