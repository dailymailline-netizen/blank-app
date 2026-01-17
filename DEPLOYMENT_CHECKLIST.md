# ✅ Deployment Checklist

Use this checklist to ensure your Streamlit Cloud deployment goes smoothly.

## Pre-Deployment

- [x] Code committed to GitHub branch `main`
- [x] `requirements.txt` includes all dependencies
- [x] `streamlit_app.py` is the entry point
- [x] Python syntax is valid (no import errors)
- [x] `.gitignore` includes `uploads/`, `streams/`, `temp/`, `logs/`
- [x] No hardcoded secrets in code (use `.streamlit/secrets.toml` instead)
- [x] `.streamlit/config.toml` is configured
- [x] `.streamlit/secrets.toml` created with local defaults

## Streamlit Cloud Setup

- [ ] Streamlit account created at https://streamlit.io/cloud
- [ ] GitHub account connected to Streamlit Cloud
- [ ] Repository `dailymailline-netizen/blank-app` is public or you have access

## Deployment Steps

1. [ ] Go to https://streamlit.io/cloud
2. [ ] Click **"New app"**
3. [ ] Select:
   - Repository: `dailymailline-netizen/blank-app`
   - Branch: `main`
   - Main file: `streamlit_app.py`
4. [ ] Click **"Deploy"**
5. [ ] Wait for deployment (~30 seconds)
6. [ ] Check app status (green dot = running)

## After Deployment

- [ ] App is accessible at `https://[random-name].streamlit.app`
- [ ] Home page loads without errors
- [ ] Navigation menu works
- [ ] Test local storage: Upload a test video

## Optional: Enable S3 Storage (Recommended)

1. [ ] Create free AWS account: https://aws.amazon.com/free
2. [ ] Follow guide: `AWS_S3_FREE_SETUP.md`
3. [ ] Get AWS credentials:
   - [ ] Access Key ID
   - [ ] Secret Access Key
4. [ ] Go to deployed app → **Manage app** → **Secrets**
5. [ ] Add:
   ```toml
   STORAGE_BACKEND = "s3"
   AWS_S3_BUCKET = "your-bucket-name"
   AWS_REGION = "us-east-1"
   AWS_ACCESS_KEY = "your-key"
   AWS_SECRET_KEY = "your-secret"
   ```
6. [ ] Click **Save** and wait for auto-restart (~10 seconds)
7. [ ] Verify S3 is working: Upload test video and check AWS S3 console

## Troubleshooting

- [ ] App won't start? Check logs: Click app → **Manage app** → **View logs**
- [ ] Import error? Add package to `requirements.txt` and push to GitHub
- [ ] S3 auth error? Double-check credentials in Secrets (no extra spaces)
- [ ] Upload fails? Make sure S3 bucket name and region are correct

## Deployed App Features

Once live, your app has:
- ✅ Public HTTPS URL
- ✅ Free tier (1 GB RAM, 3 apps max)
- ✅ Auto-deploys when you push to GitHub
- ✅ Persistent storage (if using AWS S3)
- ✅ Shareable URL for team collaboration

## Reference Links

| Item | Link |
|------|------|
| Your Repo | https://github.com/dailymailline-netizen/blank-app |
| Streamlit Cloud | https://streamlit.io/cloud |
| AWS Console | https://console.aws.amazon.com |
| Deployment Guide | See `DEPLOY_TO_STREAMLIT_CLOUD.md` |
| S3 Setup | See `AWS_S3_FREE_SETUP.md` |

---

## Estimated Timeline

| Step | Time |
|------|------|
| AWS account + S3 bucket | 10-15 min |
| Streamlit Cloud deployment | 2-3 min |
| Configure S3 secrets | 1-2 min |
| **Total** | **~15-20 min** |

You're almost there! 🚀
