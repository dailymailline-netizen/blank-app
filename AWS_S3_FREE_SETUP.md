# AWS S3 Free Tier Setup Guide

This guide walks you through setting up free AWS S3 storage for persistent video & stream storage on Streamlit Cloud.

---

## 1. Create Free AWS Account

1. Go to: https://aws.amazon.com/free
2. Click **"Create a free account"**
3. Enter email, password, and account name
4. Add payment method (required, but you won't be charged for free tier)
5. Complete phone verification
6. Select **"Basic Support Plan"** (free)

**Free Tier Includes (12 months):**
- 5 GB S3 storage
- 20,000 GET requests
- 2,000 PUT requests

Perfect for development & testing!ttps://console.aws.amazon.com/s3

---

## 2. Create S3 Bucket

1. Log into AWS Console: h
2. Click **"Create bucket"**
3. **Bucket name:** `blank-app-videos-{your-username}` (must be globally unique)
4. **Region:** Select closest to you (e.g., `us-east-1`)
5. **Block Public Access:** Leave default (checked)
6. Click **"Create bucket"**

✅ Bucket created!

---

## 3. Create IAM User (Secure Access Keys)

⚠️ **Never use root AWS credentials in code!** Use IAM user instead.

1. Go to: https://console.aws.amazon.com/iam/
2. Click **"Users"** → **"Create user"**
3. **User name:** `streamlit-app`
4. Click **"Next"**
5. Click **"Attach policies directly"**
6. Search for and select: **AmazonS3FullAccess**
7. Click **"Next"** → **"Create user"**

✅ User created!

---

## 4. Generate Access Keys

1. Click on the user **`streamlit-app`**
2. Go to **"Security credentials"** tab
3. Scroll to **"Access keys"** → Click **"Create access key"**
4. Select **"Third-party service"**
5. Accept terms → Click **"Create access key"**
6. **Copy:**
   - Access Key ID
   - Secret Access Key
7. Click **"Done"**

⚠️ **Save these securely!** You won't see them again.

---

## 5. Add Secrets to Streamlit Cloud

1. Go to your deployed app: https://streamlit.io/cloud
2. Click your app → **"Manage app"**
3. Go to **"Secrets"** tab
4. Paste this code:

```toml
STORAGE_BACKEND = "s3"
AWS_S3_BUCKET = "blank-app-videos-{your-username}"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY = "your-access-key-id-here"
AWS_SECRET_KEY = "your-secret-access-key-here"
```

5. Click **"Save"**
6. Streamlit Cloud will **auto-restart** your app

✅ App now uses S3 for persistent storage!

---

## 6. Verify S3 Connection

After restart, your app should:
- ✅ Store uploads in S3 (not local filesystem)
- ✅ Persist across app restarts/redeployments
- ✅ Show S3 usage in AWS Console

Check AWS Console → S3 → Your bucket to see uploaded videos.

---

## 7. Monitor Free Tier Usage

1. Go to: https://console.aws.amazon.com/billing/home
2. Click **"Free Tier"** in left menu
3. Track your usage:
   - S3 Storage
   - Number of requests

**Alert:** AWS will email you if approaching limits.

---

## Estimated Costs (Beyond Free Tier)

| Action | Cost |
|--------|------|
| 1 GB S3 storage | $0.023/month |
| 10,000 GET requests | $0.004 |
| 1,000 PUT requests | $0.005 |

**Example:** 10 videos (5 GB) + moderate usage = ~$0.15/month

---

## Troubleshooting

**Q: "Invalid credentials" error?**  
A: Double-check Access Key ID & Secret Key in Streamlit Cloud secrets (no extra spaces).

**Q: Can't upload to S3?**  
A: 
1. Verify bucket name is correct
2. Check IAM user has AmazonS3FullAccess policy
3. Verify region matches bucket region

**Q: Want to delete bucket?**  
A: AWS Console → S3 → Select bucket → Delete (must be empty first)

---

## Next Steps

✅ Streamlit Cloud app running with AWS S3 storage  
✅ Free tier covers development & testing  
✅ Persistent video storage across deployments  

Enjoy your deployed app! 🚀

---

## Quick Reference

| What | Where |
|------|-------|
| S3 Console | https://console.aws.amazon.com/s3 |
| IAM Users | https://console.aws.amazon.com/iam/users |
| Billing | https://console.aws.amazon.com/billing/home |
| Streamlit Cloud | https://streamlit.io/cloud |
| Your App | https://[app-name].streamlit.app |
