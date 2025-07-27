#!/bin/bash

# Azure Container Instances Deployment Script for Drishti Guard
set -e

# Configuration
RESOURCE_GROUP="drishti-guard-rg"
LOCATION="eastus"
ACR_NAME="drishtigaurd"
CONTAINER_GROUP_NAME="drishti-guard-app"

echo "🚀 Starting Drishti Guard deployment to Azure Container Instances..."

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "🏗️ Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Login to ACR
echo "🔐 Logging into ACR..."
az acr login --name $ACR_NAME

# Build and push backend
echo "🏗️ Building and pushing backend..."
az acr build --registry $ACR_NAME --image drishti-backend:latest -f Dockerfile.backend .

# Build and push frontend
echo "🏗️ Building and pushing frontend..."
cd ui
az acr build --registry $ACR_NAME --image drishti-frontend:latest .
cd ..

# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create container group
echo "🚀 Creating container group..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_GROUP_NAME \
  --image $ACR_SERVER/drishti-frontend:latest \
  --registry-login-server $ACR_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label drishti-guard \
  --ports 80 3000 8000 \
  --location $LOCATION

echo "✅ Deployment completed!"
echo "🌐 Access your app at: http://drishti-guard.${LOCATION}.azurecontainer.io"
