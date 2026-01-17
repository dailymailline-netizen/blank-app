# P2P NFS Setup Guide for Stream & Upload Hub

## Overview

This guide covers setting up a peer-to-peer NFS infrastructure for distributed video and notepad synchronization across multiple Stream & Upload Hub instances.

---

## Architecture Diagram

```
                    Central NFS Server
                    ┌─────────────────┐
                    │  /exports/data  │
                    │  - videos/      │
                    │  - notes/       │
                    └────────┬────────┘
                             │ (NFS protocol)
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │  Instance A │  │ Instance B  │  │ Instance C  │
    │ (Peer Node) │  │ (Peer Node) │  │ (Peer Node) │
    │  :6881      │  │  :6881      │  │  :6881      │
    │ (Avahi/mDNS)│  │ (Avahi/mDNS)│  │ (Avahi/mDNS)│
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                    P2P Gossip Protocol
                    (Sync Events)
```

---

## Prerequisites

- **Linux servers** (Ubuntu 20.04+ recommended)
- **Network connectivity** (LAN/WAN with <100ms latency)
- **NFS kernel module** (included in most Linux distros)
- **Root/sudo access** on all machines
- **At least 50GB** disk space per instance (for local cache)

---

## Part 1: NFS Server Setup

### Step 1: Install NFS Server

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nfs-kernel-server nfs-common

# On RHEL/CentOS
sudo yum install -y nfs-utils
```

### Step 2: Create NFS Export Directories

```bash
# Create shared directories
sudo mkdir -p /mnt/nfs/videos
sudo mkdir -p /mnt/nfs/notes
sudo mkdir -p /mnt/nfs/analytics

# Set permissions
sudo chown -R nobody:nogroup /mnt/nfs
sudo chmod -R 755 /mnt/nfs
```

### Step 3: Configure NFS Exports

Edit `/etc/exports`:

```bash
sudo nano /etc/exports
```

Add these lines:

```
# NFS exports for Stream & Upload Hub
/mnt/nfs/videos         *(rw,sync,no_subtree_check,no_all_squash,anonuid=65534,anongid=65534)
/mnt/nfs/notes          *(rw,sync,no_subtree_check,no_all_squash,anonuid=65534,anongid=65534)
/mnt/nfs/analytics      *(rw,sync,no_subtree_check,no_all_squash,anonuid=65534,anongid=65534)

# For production (restrict to specific subnet):
# /mnt/nfs/videos       192.168.1.0/24(rw,sync,no_subtree_check)
# /mnt/nfs/notes        192.168.1.0/24(rw,sync,no_subtree_check)
```

**Options explained:**
- `rw` – Read/write access
- `sync` – Write immediately (safer than async)
- `no_subtree_check` – Faster, safer for most cases
- `no_all_squash` – Allow non-root users to write

### Step 4: Export and Start NFS

```bash
# Apply exports
sudo exportfs -a

# Start NFS services
sudo systemctl start nfs-kernel-server
sudo systemctl enable nfs-kernel-server  # Auto-start on boot

# Verify
sudo exportfs -v
# Output should show all exports
```

### Step 5: Configure Firewall

```bash
# Open NFS ports
sudo ufw allow 111/tcp 111/udp   # Portmapper
sudo ufw allow 2049/tcp 2049/udp  # NFS
sudo ufw allow 20048/tcp 20048/udp # Mountd
```

---

## Part 2: NFS Client Setup (Per Instance)

### Step 1: Install NFS Client

```bash
# On Ubuntu/Debian
sudo apt-get install -y nfs-common

# On RHEL/CentOS
sudo yum install -y nfs-utils
```

### Step 2: Create Mount Points

```bash
sudo mkdir -p /data/videos
sudo mkdir -p /data/notes
sudo mkdir -p /data/analytics

# Set permissions
sudo chmod 755 /data/videos /data/notes /data/analytics
```

### Step 3: Mount NFS Shares

```bash
# Replace <NFS_SERVER_IP> with actual server IP
NFS_SERVER_IP="192.168.1.100"

sudo mount -t nfs -o rw,hard,intr,rsize=8192,wsize=8192 \
  $NFS_SERVER_IP:/mnt/nfs/videos /data/videos

sudo mount -t nfs -o rw,hard,intr,rsize=8192,wsize=8192 \
  $NFS_SERVER_IP:/mnt/nfs/notes /data/notes

sudo mount -t nfs -o rw,hard,intr,rsize=8192,wsize=8192 \
  $NFS_SERVER_IP:/mnt/nfs/analytics /data/analytics

# Verify mounts
mount | grep nfs
```

### Step 4: Make Mounts Persistent

Edit `/etc/fstab`:

```bash
sudo nano /etc/fstab
```

Add these lines:

```
# NFS mounts for Stream & Upload Hub
192.168.1.100:/mnt/nfs/videos   /data/videos    nfs   rw,hard,intr,rsize=8192,wsize=8192  0 0
192.168.1.100:/mnt/nfs/notes    /data/notes     nfs   rw,hard,intr,rsize=8192,wsize=8192  0 0
192.168.1.100:/mnt/nfs/analytics /data/analytics nfs   rw,hard,intr,rsize=8192,wsize=8192  0 0
```

Verify with:
```bash
sudo mount -a  # Test all mounts in fstab
```

---

## Part 3: Avahi/mDNS Peer Discovery

### Step 1: Install Avahi

```bash
# All instances (server + clients)
sudo apt-get install -y avahi-daemon avahi-utils

# Start service
sudo systemctl start avahi-daemon
sudo systemctl enable avahi-daemon
```

### Step 2: Create Avahi Service File

Create `/etc/avahi/services/stream-hub.service`:

```bash
sudo nano /etc/avahi/services/stream-hub.service
```

Add:

```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Stream Hub %h</name>
  <service>
    <type>_stream-hub._tcp</type>
    <port>6881</port>
    <txt-record>version=1.0</txt-record>
    <txt-record>node_name=%h</txt-record>
  </service>
</service-group>
```

Restart Avahi:
```bash
sudo systemctl restart avahi-daemon
```

### Step 3: Verify Peer Discovery

```bash
# List all discovered Stream Hub peers
avahi-browse -r -t _stream-hub._tcp

# Output example:
# + wlp3s0 IPv4 stream-hub-instance-a       _stream-hub._tcp     local
# + wlp3s0 IPv4 stream-hub-instance-b       _stream-hub._tcp     local
```

---

## Part 4: Application Configuration

### Update config.py

```python
# config.py

import os
from pathlib import Path

# Storage paths (now on NFS)
UPLOAD_DIR = Path("/data/videos")
STREAMS_DIR = Path("/data/videos/streams")
LOGS_DIR = Path("logs")  # Local, not shared
TEMP_DIR = Path("temp")  # Local, not shared
NOTEPAD_STORAGE_PATH = Path("/data/notes")

# Storage backend
STORAGE_BACKEND = "local"  # With NFS mount
AWS_S3_BUCKET = None  # Not used with NFS

# P2P & Community Settings
P2P_ENABLED = True
P2P_PORT = 6881
P2P_NODE_NAME = os.getenv("HOSTNAME", "stream-hub-default")
P2P_HEARTBEAT_INTERVAL = 5  # seconds

COMMUNITY_NOTEPAD_ENABLED = True
NOTEPAD_AUTO_SYNC = True
NOTEPAD_MAX_SIZE_MB = 100  # Per note
```

### Environment Setup (.env)

```bash
# .env (create in app directory)
P2P_ENABLED=true
P2P_NODE_NAME=stream-hub-instance-a
NOTEPAD_AUTO_SYNC=true
NFS_SERVER=192.168.1.100
```

---

## Part 5: Docker Compose for Multi-Instance Setup

Create `docker-compose-p2p.yml`:

```yaml
version: '3.8'

services:
  streamlit-1:
    image: stream-hub:latest
    container_name: stream-hub-1
    ports:
      - "8501:8501"
      - "6881:6881"
    volumes:
      - /data/videos:/app/uploads
      - /data/notes:/app/community_notes
      - /data/analytics:/app/analytics
    environment:
      - P2P_ENABLED=true
      - P2P_NODE_NAME=stream-hub-1
      - HOSTNAME=stream-hub-1
    networks:
      - stream-hub-network
    depends_on:
      - nfs-server

  streamlit-2:
    image: stream-hub:latest
    container_name: stream-hub-2
    ports:
      - "8502:8501"
      - "6882:6881"
    volumes:
      - /data/videos:/app/uploads
      - /data/notes:/app/community_notes
      - /data/analytics:/app/analytics
    environment:
      - P2P_ENABLED=true
      - P2P_NODE_NAME=stream-hub-2
      - HOSTNAME=stream-hub-2
    networks:
      - stream-hub-network
    depends_on:
      - nfs-server

  streamlit-3:
    image: stream-hub:latest
    container_name: stream-hub-3
    ports:
      - "8503:8501"
      - "6883:6881"
    volumes:
      - /data/videos:/app/uploads
      - /data/notes:/app/community_notes
      - /data/analytics:/app/analytics
    environment:
      - P2P_ENABLED=true
      - P2P_NODE_NAME=stream-hub-3
      - HOSTNAME=stream-hub-3
    networks:
      - stream-hub-network
    depends_on:
      - nfs-server

  nginx:
    image: nginx:latest
    container_name: stream-hub-lb
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - stream-hub-network
    depends_on:
      - streamlit-1
      - streamlit-2
      - streamlit-3

networks:
  stream-hub-network:
    driver: bridge
```

Start with:
```bash
docker-compose -f docker-compose-p2p.yml up -d
```

---

## Part 6: Monitoring & Health Checks

### Monitor NFS Mounts

```bash
# Check mount status
df -h /data/videos /data/notes

# Monitor NFS operations
nfsstat -m

# Check NFS server exports
showmount -e 192.168.1.100

# Real-time NFS stats
nfsstat -s  # Server stats
nfsstat -c  # Client stats
```

### Monitor P2P Connectivity

Add to `streamlit_app.py`:

```python
import socket
import streamlit as st
from community_notepad import P2PPeerManager

# P2P Health Check
@st.cache_resource
def init_p2p():
    manager = P2PPeerManager(
        socket.gethostname(),
        port=6881
    )
    return manager

if st.sidebar.checkbox("Show P2P Stats"):
    manager = init_p2p()
    st.write("**Connected Peers:**")
    for peer in manager.get_peers():
        st.write(f"- {peer['id']} ({peer['address']})")
```

### Health Check Endpoint

```bash
# Test NFS health
nc -zv 192.168.1.100 2049

# Test Avahi/mDNS
avahi-resolve -n stream-hub-instance-a.local
```

---

## Part 7: Troubleshooting

### NFS Mount Fails

```bash
# Check server is exporting
showmount -e <NFS_SERVER_IP>

# Check firewall
sudo ufw status

# Check mount with verbose output
sudo mount -vvv -t nfs <NFS_SERVER_IP>:/mnt/nfs/videos /data/videos
```

### Peers Don't Discover

```bash
# Verify Avahi is running
sudo systemctl status avahi-daemon

# Check service publication
avahi-browse -a  # All services

# Restart if needed
sudo systemctl restart avahi-daemon
```

### NFS Performance Slow

```bash
# Optimize mount options in /etc/fstab
# Try larger rsize/wsize:
192.168.1.100:/mnt/nfs/videos /data/videos nfs rw,hard,intr,rsize=131072,wsize=131072 0 0

# Monitor I/O
iostat -x 1

# Check network
iperf3 -c <nfs_server>
```

### Permission Denied on NFS

```bash
# Check NFS export options
sudo cat /etc/exports

# Check local mount permissions
ls -la /data/videos

# Fix permissions
sudo chmod 755 /data/videos
sudo chown $USER:$USER /data/videos
```

---

## Performance Tuning

### NFS Server

```bash
# Edit /etc/default/nfs-kernel-server
RPCNFSDARGS="-N 2 -U -t 16"  # Increase thread count

# Increase max connections
sysctl -w net.core.somaxconn=1024
```

### Client Mount Options

Best for low-latency LAN:
```
rw,hard,intr,rsize=131072,wsize=131072,tcp,noatime
```

Best for high-latency WAN:
```
rw,soft,intr,rsize=8192,wsize=8192,tcp
```

---

## Backup & Disaster Recovery

### Automated NFS Backup

```bash
#!/bin/bash
# /usr/local/bin/nfs-backup.sh

BACKUP_DIR="/backups/stream-hub"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup NFS shares
rsync -avz /data/videos $BACKUP_DIR/videos_$DATE
rsync -avz /data/notes $BACKUP_DIR/notes_$DATE
rsync -avz /data/analytics $BACKUP_DIR/analytics_$DATE

# Keep only last 30 days
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
# Backup daily at 2 AM
0 2 * * * /usr/local/bin/nfs-backup.sh
```

---

## References

- **NFS Setup:** https://ubuntu.com/server/docs/service-nfs
- **Avahi Documentation:** https://www.avahi.org/
- **NFS Performance Tuning:** https://nfs.readthedocs.io/en/latest/
- **mDNS/Bonjour:** https://datatracker.ietf.org/doc/html/rfc6762
