# 🚀 Google Cloud Deployment Guide

## Quick Start (1-Click Deployment)

1. **Run the deployment script:**
   ```cmd
   .\deploy-to-cloud.bat
   ```

2. **Enter your details when prompted:**
   - Google Cloud Project ID
   - Gemini API Key

3. **Wait for deployment** (5-10 minutes)

4. **Access your app** at the provided URLs!

## Prerequisites

### 1. Install Google Cloud CLI
Download and install from: https://cloud.google.com/sdk/docs/install

### 2. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Note down the Project ID

### 3. Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key for deployment

### 4. Enable Billing
- Cloud Run requires billing to be enabled
- You get $300 free credits for new accounts

## Manual Deployment

If you prefer manual control:

```powershell
# Run PowerShell script directly
.\deploy-gcp.ps1 -ProjectId "your-project-id" -GeminiApiKey "your-api-key"
```

## What Gets Deployed

### Services Created:
- **drishti-guard-frontend** - Next.js UI on Cloud Run
- **drishti-guard-backend** - FastAPI + CNS on Cloud Run

### Features:
- ✅ Auto-scaling (0 to 10 instances)
- ✅ HTTPS by default
- ✅ Global CDN
- ✅ Health checks
- ✅ Logging and monitoring
- ✅ Secure secrets management

## Cost Estimation

### Free Tier Included:
- 2 million requests per month
- 180,000 vCPU-seconds per month
- 360,000 GiB-seconds memory per month

### Typical Monthly Cost:
- **Light usage**: $0-5/month
- **Medium usage**: $10-30/month  
- **Heavy usage**: $50-100/month

## Post-Deployment

### Access Your App:
- **Main App**: https://drishti-guard-frontend-xxx-uc.a.run.app
- **Volunteer Dashboard**: .../volunteer
- **API Docs**: https://drishti-guard-backend-xxx-uc.a.run.app/docs

### Configure Custom Domain:
1. Go to Cloud Run service
2. Click "Manage Custom Domains"
3. Add your domain
4. Update DNS records

### Monitor Performance:
```bash
# View logs
gcloud run services logs read drishti-guard-frontend --region us-central1

# Monitor metrics
gcloud run services describe drishti-guard-frontend --region us-central1
```

## Troubleshooting

### Common Issues:

1. **Build fails**:
   - Check Node.js version compatibility
   - Verify package.json dependencies

2. **API key errors**:
   - Verify Gemini API key is correct
   - Check secret manager permissions

3. **Cold starts**:
   - Normal for Cloud Run
   - Consider minimum instances for production

### Get Help:
```bash
# Check service status
gcloud run services list

# View detailed logs
gcloud logging read "resource.type=cloud_run_revision"

# Debug build
gcloud builds list
```

## Cleanup

To remove all services:
```bash
gcloud run services delete drishti-guard-frontend --region us-central1
gcloud run services delete drishti-guard-backend --region us-central1
gcloud secrets delete gemini-api-key
```

Your Drishti Guard system is now running on Google Cloud with enterprise-grade reliability! 🎉
