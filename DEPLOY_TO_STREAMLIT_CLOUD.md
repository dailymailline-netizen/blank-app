# 🚀 Deploy to Streamlit Cloud - Complete Guide

Your **Stream & Upload Hub** is ready to deploy! This guide covers all 3 steps:
1. ✅ GitHub Repository (Already done!)
2. 🎬 Deploy to Streamlit Cloud
3. 🔒 Configure AWS S3 Storage (for persistence)

---

## Quick Deploy (2 minutes)

### Step 1: Go to Streamlit Cloud
Visit: https://streamlit.io/cloud

### Step 2: Sign in with GitHub
- Click **"Sign in"** or **"New app"**
- Click **"GitHub"** → Authorize Streamlit
- Select your account

### Step 3: Deploy Your App
1. Click **"New app"**
2. Fill in:
   - **Repository:** `dailymailline-netizen/blank-app`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
3. Click **"Deploy"**

✨ **That's it!** Your app is live in ~30 seconds.

**Your public URL:** `https://[random-name].streamlit.app`

---

## What You Get (Free Tier)

| Feature | Limit |
|---------|-------|
| **Active Apps** | 3 apps |
| **Memory** | 1 GB per app |
| **CPU** | Shared |
| **Storage** | Ephemeral (local files deleted on restart) |
| **URL** | Public HTTPS |
| **Domain** | Streamlit subdomain (custom domains require paid) |
| **Custom Secrets** | Yes (via Secrets Manager) |

---

## ⚠️ Important: Local Storage Doesn't Persist

By default, your app stores uploads in a local `uploads/` folder. On Streamlit Cloud:
- ✅ Local storage works for testing
- ❌ Files are lost when app restarts or redeploys
- ❌ Can't scale to multiple instances

**Solution:** Use AWS S3 for persistent storage (see next section).

---

## 🔒 Enable Persistent Storage with AWS S3

### Option A: Quick Setup (Recommended for Free Tier)

1. **Create free AWS account:**
   https://aws.amazon.com/free

2. **Follow the S3 setup guide:**
   See `AWS_S3_FREE_SETUP.md` in this repo

3. **Add secrets to your Streamlit Cloud app:**
   - Go to https://streamlit.io/cloud
   - Click your app → **"Manage app"** → **"Secrets"**
   - Paste:
   ```toml
   STORAGE_BACKEND = "s3"
   AWS_S3_BUCKET = "your-bucket-name"
   AWS_REGION = "us-east-1"
   AWS_ACCESS_KEY = "your-access-key"
   AWS_SECRET_KEY = "your-secret-key"
   ```
   - Click **"Save"**

4. **Done!** Your app now uses S3 (persistent storage)

### Option B: Stay Local (Development Only)
- Keep default: `STORAGE_BACKEND = "local"`
- Accepts temporary uploads
- Simpler, but data doesn't persist

---

## 📋 Pre-Deployment Checklist

Before clicking "Deploy" on Streamlit Cloud:

- ✅ Code pushed to GitHub (`git push origin main`)
- ✅ `requirements.txt` includes all dependencies
- ✅ `streamlit_app.py` is the entry point
- ✅ `.gitignore` excludes `uploads/`, `streams/`, `temp/`
- ✅ No hardcoded API keys in code (use Secrets instead)

Your repo already meets all these! ✨

---

## Deployment Architecture

```
GitHub (Your Code)
    ↓
Streamlit Cloud (Runs Your App)
    ↓
AWS S3 (Stores Videos & Streams)
    ↓
User Browser (Views App at https://[name].streamlit.app)
```

---

## Managing Your Deployed App

### View Logs
1. Streamlit Cloud dashboard
2. Click your app
3. Click **"Manage app"** → **"View logs"**

### Redeploy Latest Code
- Push to GitHub → Auto-redeploy in ~30 seconds
- No manual action needed!

### Stop/Delete App
- Click app → **"Settings"** → **"Delete app"** or **"Pause"**

### View App Status
- Green dot = Running ✅
- Orange dot = Starting
- Red dot = Error ❌

Check logs if your app isn't running.

---

## Troubleshooting

### "ImportError: No module named X"
- Add missing package to `requirements.txt`
- Push to GitHub
- Streamlit Cloud auto-rebuilds

### "Can't upload videos"
- Check local storage path exists
- Or switch to S3 (see AWS setup)

### "App starts but shows blank"
- Check logs for Python errors
- Verify `streamlit_app.py` syntax

### "S3 access denied"
- Verify AWS credentials in Secrets
- Ensure IAM user has `AmazonS3FullAccess` policy
- Check bucket name matches

---

## Scaling Beyond Free Tier

When you need more:

| Limit | Upgrade |
|-------|---------|
| 1 GB RAM | Streamlit Cloud Pro ($5/app/month) |
| 3 Apps | Streamlit Cloud Pro ($5/app/month) |
| Custom domain | Streamlit Cloud Pro ($5/app/month) |
| 5 GB S3 storage | AWS ($0.023/GB/month) |

---

## Advanced: Local Testing Before Deploy

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Test with Streamlit Cloud settings
```bash
# Create .streamlit/secrets.toml locally (same as deployed)
# Then run:
streamlit run streamlit_app.py
```

### 3. Verify S3 connection (if using AWS)
Upload a file and check your S3 bucket in AWS Console.

---

## 🎉 You're Ready!

1. Visit: https://streamlit.io/cloud
2. Click "New app"
3. Deploy from: `dailymailline-netizen/blank-app`
4. Share your public URL with friends!

**Need help?**
- Streamlit docs: https://docs.streamlit.io/
- Streamlit Cloud FAQ: https://docs.streamlit.io/streamlit-community-cloud/get-started
- AWS Free Tier: https://docs.aws.amazon.com/free/

---

## One-Click Deployment Summary

**Manual steps once:**
1. Create AWS account (5 min)
2. Create S3 bucket (2 min)
3. Create IAM user + access keys (3 min)
4. Deploy to Streamlit Cloud (2 min)
5. Add AWS secrets to Streamlit Cloud (1 min)

**Total time:** ~15 minutes → Fully deployed app with persistent storage ✅

**After that:** Just `git push` and your app auto-updates! 🚀
