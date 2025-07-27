#!/bin/bash

# Google Cloud Run Deployment Script for Drishti Guard
set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
SERVICE_NAME_FRONTEND="drishti-guard-frontend"
SERVICE_NAME_BACKEND="drishti-guard-backend"

echo "🚀 Starting Drishti Guard deployment to Google Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy backend
echo "🏗️ Building and deploying backend..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME_BACKEND -f Dockerfile.backend .

gcloud run deploy $SERVICE_NAME_BACKEND \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME_BACKEND \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars PYTHONUNBUFFERED=1

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME_BACKEND --region $REGION --format 'value(status.url)')

# Build and deploy frontend
echo "🏗️ Building and deploying frontend..."
cd ui
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME_FRONTEND .

gcloud run deploy $SERVICE_NAME_FRONTEND \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME_FRONTEND \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL

cd ..

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME_FRONTEND --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed!"
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔗 Backend URL: $BACKEND_URL"
echo "📊 Volunteer Dashboard: $FRONTEND_URL/volunteer"
