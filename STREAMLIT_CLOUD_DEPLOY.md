# Deploy to Streamlit Community Cloud

**This is the fastest & easiest way to deploy your Stream & Upload Hub for FREE.**

## Prerequisites
- GitHub account (free)
- Streamlit account (link your GitHub)

## Step-by-Step Deployment

### 1. Prepare Your Repository
```bash
# Make sure your code is committed
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. Create `streamlit/secrets.toml` (Optional - for environment vars)
Create `.streamlit/secrets.toml` in your repo root:
```toml
STORAGE_BACKEND = "local"
```

### 3. Go to Streamlit Cloud
1. Visit: https://streamlit.io/cloud
2. Click **"New app"**
3. Connect your GitHub account
4. Select:
   - **Repository:** dailymailline-netizen/blank-app
   - **Branch:** main
   - **Main file path:** streamlit_app.py

### 4. Configure (Optional)
- Click **"Advanced settings"** if needed
- Set Python version: 3.9+
- Keep defaults for memory/CPU

### 5. Deploy!
Click **"Deploy"** - Streamlit Cloud will:
- Install requirements.txt automatically
- Start your app
- Give you a public URL

**Your app URL will be:** `https://[random-name].streamlit.app`

---

## Features You Get (Free Tier)
✅ Free HTTPS URL  
✅ Custom domain support (optional)  
✅ Automatic restarts  
✅ 3 active apps max  
✅ 1GB memory per app  
✅ Public or private (GitHub auth required for private)  

## Known Limitations
⚠️ Local file storage (uploads/, streams/) will be wiped on redeploy  
💡 **Solution:** Switch to S3 storage for persistence  

## Upgrade to Persistent Storage (Optional)

### Use AWS S3 (Free tier eligible)
1. Create AWS account: https://aws.amazon.com/free
2. Create S3 bucket
3. Update `.streamlit/secrets.toml`:
```toml
STORAGE_BACKEND = "s3"
AWS_S3_BUCKET = "your-bucket-name"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY = "your-key"
AWS_SECRET_KEY = "your-secret"
```

4. Redeploy on Streamlit Cloud

---

## Troubleshooting

**Q: App won't start?**  
A: Check the Logs in Streamlit Cloud dashboard → click "Manage app" → "View logs"

**Q: Missing dependencies?**  
A: Ensure all imports in streamlit_app.py are in requirements.txt

**Q: Can't access uploaded files?**  
A: Local storage is ephemeral. Switch to S3 for persistence (see above).

**Q: Want a custom domain?**  
A: Streamlit Cloud premium feature. Use Vercel + API server as alternative.

---

## Next Steps
1. ✅ Push code to GitHub
2. ✅ Deploy to Streamlit Cloud
3. ✅ Share public URL with team
4. (Optional) Upgrade to S3 storage for persistence
