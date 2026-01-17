# Cloud Architecture & Storage Guide

## Overview

Stream & Upload Hub now supports multiple storage backends and peer-to-peer distributed storage for scalable video and note management.

---

## Storage Architecture

### 1. Pluggable Storage Backends

The app uses an **abstraction layer** (`storage_backend.py`) supporting multiple backends:

#### Local Storage
```python
from storage_backend import StorageFactory

storage = StorageFactory.create_backend("local", base_path="./uploads")
storage.upload_file("local_video.mp4", "videos/my_video.mp4")
```

**When to use:** Development, single-instance deployments, NFS mounts

#### AWS S3
```python
storage = StorageFactory.create_backend(
    "s3",
    bucket_name="my-bucket",
    region="us-east-1",
    aws_access_key="...",
    aws_secret_key="..."
)
```

**When to use:** Multi-instance deployments, CDN distribution, long-term archival

**Configuration:** `.env` or `config.py`
```
STORAGE_BACKEND=s3
AWS_S3_BUCKET=my-stream-hub-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY=xxxxx
AWS_SECRET_KEY=xxxxx
```

---

## P2P NFS Architecture

### Peer-to-Peer Network Topology

```
                    ┌─────────────┐
                    │   Peer A    │ (Instance 1)
                    │  :6881      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼─────┐ ┌────▼─────┐ ┌──▼──────┐
         │  Peer B  │ │  Peer C  │ │ Peer D  │
         │ :6881    │ │ :6881    │ │ :6881   │
         └──────────┘ └──────────┘ └─────────┘
         
    Shared Note/Video Database (Sync Log)
    ├── notes/
    │   ├── {note_id}.json (versioned)
    │   └── {note_id}.json
    └── sync_log.json (tracks changes)
```

### How P2P NFS Works

1. **Node Registration**
   - Each instance registers itself with a port (default: 6881)
   - Nodes discover peers via local network broadcast (mDNS) or configuration

2. **Note Synchronization**
   - When a note is created/updated, it's queued for sync
   - `P2PPeerManager` broadcasts changes to all peers
   - Each peer stores copy in local `community_notes/` directory

3. **Conflict Resolution**
   - Version numbers track updates (auto-increment)
   - Last-write-wins for simple conflicts
   - Full sync history in `sync_log.json`

### Setup P2P NFS (Using NFS + Bonjour)

#### Step 1: Mount Shared NFS
```bash
# On NFS server (Ubuntu/Linux)
sudo apt-get install nfs-kernel-server
sudo mkdir -p /mnt/shared/notes
sudo chown nobody:nogroup /mnt/shared/notes

# Add to /etc/exports
/mnt/shared/notes *(rw,sync,no_subtree_check)
sudo exportfs -a

# On client instances
sudo apt-get install nfs-common
sudo mkdir -p /mnt/notes
sudo mount -t nfs <server-ip>:/mnt/shared/notes /mnt/notes
```

#### Step 2: Enable P2P in Config
```python
# config.py
P2P_ENABLED = True
P2P_PORT = 6881
P2P_NODE_NAME = f"stream-hub-{socket.gethostname()}"
NOTEPAD_STORAGE_PATH = "/mnt/notes"  # Shared NFS mount
```

#### Step 3: Install Peer Discovery (Avahi/mDNS)
```bash
sudo apt-get install avahi-daemon
# Services will auto-discover on local network
```

#### Step 4: Run App
```bash
streamlit run streamlit_app.py
# App will:
# 1. Register as P2P node
# 2. Discover peers on network
# 3. Sync notes automatically
```

---

## Production Deployment Patterns

### Pattern 1: Single Instance + Local Storage
```
┌──────────────────┐
│  Streamlit App   │
│  + Local FS      │
│  (/uploads)      │
└──────────────────┘
       ↓
   Suitable for: <100GB videos, single user/team
```

**Setup:**
```bash
STORAGE_BACKEND=local
```

---

### Pattern 2: Multi-Instance + S3
```
        ┌──────────────────────────────────┐
        │     AWS CloudFront (CDN)         │
        │     (caches video streams)       │
        └────────────┬─────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐      ┌───▼────┐      ┌───▼────┐
│Instance│      │Instance│      │Instance│
│   #1   │      │   #2   │      │   #3   │
│(st_app)│      │(st_app)│      │(st_app)│
└───┬────┘      └───┬────┘      └───┬────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
              ┌──────▼──────┐
              │  AWS S3     │
              │  Bucket     │
              └─────────────┘
              
    Metadata: PostgreSQL / DynamoDB
    Session: Redis / ElastiCache
```

**Setup:**
```bash
STORAGE_BACKEND=s3
AWS_S3_BUCKET=my-production-bucket
AWS_REGION=us-east-1

# With Docker + Nginx Load Balancer
docker-compose up -d  # Runs 3 instances behind Nginx
```

**Cost Estimate:**
- S3 Storage: $0.023/GB/month
- S3 Transfer: $0.09/GB (outbound)
- CloudFront: $0.085/GB (streaming CDN)
- Total for 1TB: ~$120-150/month

---

### Pattern 3: Hybrid + P2P NFS
```
    NFS Server (Central)
    ├── /mnt/notes
    │   ├── notes/ (synced via P2P)
    │   └── sync_log.json
    
    ┌─────────────┬─────────────┬─────────────┐
    │             │             │             │
┌───▼──┐     ┌───▼──┐     ┌───▼──┐     ┌───▼──┐
│Inst#1│     │Inst#2│     │Inst#3│     │Inst#4│
│ P2P  │─────────┬─────────┬──────────┘ P2P  │
│Peer  │         │         │            Peer │
└──────┘     └───┬──┘     └───┬──┘         └──────┘
             (all mount /mnt/notes)
             
    Videos: Local cache + S3 fallback
    Notes: NFS + P2P sync
```

**Setup:**
```bash
STORAGE_BACKEND=local  # With NFS mount for cache
P2P_ENABLED=True
P2P_NODE_NAME="stream-hub-$(hostname)"
NOTEPAD_STORAGE_PATH=/mnt/notes  # Shared NFS
```

---

## Community Notepad Integration

### Features

- **Collaborative notes** with version tracking
- **P2P synchronization** across instances
- **Shared/private** notes
- **Search** by title, content, or tags
- **Analytics** tracking

### Usage

```python
from community_notepad import CommunityNotepad, P2PPeerManager

# Create notepad instance
notepad = CommunityNotepad("community_notes/")

# Create note
note_id = notepad.create_note("API Docs", "# My API Documentation", tags=["api", "docs"])

# Share with community
notepad.share_note(note_id)

# Setup P2P sync
peers = P2PPeerManager("my-node", port=6881)
peers.register_peer("peer-b", "192.168.1.102:6881")
peers.sync_to_peers(note_id, notepad.get_note(note_id))

# Search community notes
results = notepad.search_notes("API")
```

---

## Scaling Considerations

### Bottlenecks & Solutions

| Bottleneck | Cause | Solution |
|---|---|---|
| Video streaming lag | Bandwidth/CDN coverage | Use CloudFront + regional S3 replicas |
| Note sync conflicts | Concurrent edits | Implement OT (Operational Transform) or CRDT |
| Storage cost | Large video library | Archive old videos; use Glacier for cold storage |
| P2P network overhead | Broadcasting to many peers | Implement gossip protocol; limit sync frequency |

### Monitoring

**Key metrics to track:**
- Upload/download latency
- P2P peer discovery time
- Storage backend latency (S3, NFS)
- Note sync conflicts/failures
- CDN cache hit ratio

---

## Migration Path

### Step 1: Local to NFS
```bash
# Mount NFS
sudo mount -t nfs <server-ip>:/exports/videos /data/uploads
# Update config
UPLOAD_DIR = "/data/uploads"
```

### Step 2: Add S3 Backup
```python
# config.py
STORAGE_BACKEND = "s3"
```

### Step 3: Enable P2P
```python
P2P_ENABLED = True
```

---

## References

- **NFS Setup:** https://ubuntu.com/server/docs/service-nfs
- **Avahi/mDNS:** https://www.avahi.org/
- **AWS S3:** https://docs.aws.amazon.com/s3/
- **Distributed Systems:** https://en.wikipedia.org/wiki/Gossip_protocol
