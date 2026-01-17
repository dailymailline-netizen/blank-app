# Deployment Guide

## Stream & Upload Hub - Deployment Instructions

### Local Development

#### Prerequisites
- Python 3.8 or higher
- pip or conda
- 2GB+ disk space

#### Steps

1. **Clone/navigate to project:**
   ```bash
   cd /workspaces/blank-app
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Access the app:**
   - Open browser to `http://localhost:8501`
   - Start uploading videos and creating streams!

---

### Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads streams logs temp

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "streamlit_app.py"]
```

#### Build and run Docker image

```bash
# Build
docker build -t stream-upload-hub:latest .

# Run
docker run -p 8501:8501 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/streams:/app/streams \
  stream-upload-hub:latest
```

---

### Cloud Deployment (Streamlit Cloud)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Stream & Upload Hub framework"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select GitHub repo, branch, and main file
   - Click "Deploy"

3. **Share URL:**
   - Your app will be available at `https://your-app-name.streamlit.app`

---

### Production Considerations

#### Security
- Add authentication in `config.py`
- Enable HTTPS
- Use environment variables for sensitive data
- Implement rate limiting
- Validate all file uploads

#### Performance
- Compress videos during upload
- Use CDN for streaming delivery
- Implement caching strategies
- Monitor disk usage
- Set up auto-cleanup

#### Monitoring
- Enable analytics tracking
- Log all events
- Monitor resource usage
- Set up alerts
- Regular backups

---

### Environment Variables

Create `.env` file for sensitive configuration:

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
MAX_UPLOAD_SIZE=500
ENABLE_AUTH=false
API_KEY=your_api_key_here
DATABASE_URL=your_db_url
```

---

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.11+ |
| RAM | 2 GB | 8 GB |
| Disk | 10 GB | 50+ GB |
| CPU | 2 cores | 4+ cores |
| OS | Linux/macOS/Windows | Linux |

---

### Troubleshooting Deployment

#### Port already in use
```bash
streamlit run streamlit_app.py --server.port 8502
```

#### Memory issues
```bash
# Increase JVM memory
export STREAMLIT_LOGGER_LEVEL=warning
streamlit run streamlit_app.py
```

#### Video codec issues
```bash
# Install ffmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg           # macOS
```

#### Permissions issues
```bash
chmod -R 755 uploads/
chmod -R 755 streams/
chmod -R 755 logs/
```

---

### Monitoring and Maintenance

#### Check application status
```bash
ps aux | grep streamlit
```

#### View logs
```bash
tail -f logs/app.log
```

#### Clean up old files
- Set `AUTO_CLEANUP_ENABLED = True` in config.py
- Adjust `CLEANUP_AGE_DAYS` as needed

#### Database backup
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ streams/
```

---

### Scale Beyond Single Instance

For production with multiple instances:

1. **Use shared storage:**
   - NFS for uploads/streams
   - S3 for video files
   - Redis for session state

2. **Load balancing:**
   - Nginx as reverse proxy
   - Multiple app instances behind it

3. **Database:**
   - PostgreSQL for metadata
   - MongoDB for analytics

4. **Caching:**
   - Redis for stream info
   - CDN for video delivery

---

### SSL/TLS Configuration

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Update Streamlit config
# .streamlit/config.toml
[server]
sslCertFile = "cert.pem"
sslKeyFile = "key.pem"
```

---

### Backup and Recovery

**Automated backup script:**
```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
  /workspaces/blank-app/uploads \
  /workspaces/blank-app/streams \
  /workspaces/blank-app/logs

# Keep only last 30 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete
```

---

### Support and Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **OpenCV Docs:** https://docs.opencv.org
- **GitHub Issues:** Check project repo
- **Stack Overflow:** Tag with `streamlit` and `python`

---

**Version:** 1.0.0
**Last Updated:** 2025-01-17
