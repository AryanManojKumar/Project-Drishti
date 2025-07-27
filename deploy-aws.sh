#!/bin/bash

# AWS ECS Deployment Script for Drishti Guard
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY_FRONTEND="drishti-guard-frontend"
ECR_REPOSITORY_BACKEND="drishti-guard-backend"
ECS_CLUSTER="drishti-guard-cluster"
ECS_SERVICE_FRONTEND="drishti-guard-frontend-service"
ECS_SERVICE_BACKEND="drishti-guard-backend-service"

echo "🚀 Starting Drishti Guard deployment to AWS ECS..."

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Create ECR repositories if they don't exist
echo "📦 Creating ECR repositories..."
aws ecr create-repository --repository-name $ECR_REPOSITORY_FRONTEND --region $AWS_REGION || true
aws ecr create-repository --repository-name $ECR_REPOSITORY_BACKEND --region $AWS_REGION || true

# Build and push frontend
echo "🏗️ Building and pushing frontend..."
cd ui
docker build -t $ECR_REPOSITORY_FRONTEND .
docker tag $ECR_REPOSITORY_FRONTEND:latest $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:latest
docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:latest
cd ..

# Build and push backend
echo "🏗️ Building and pushing backend..."
docker build -f Dockerfile.backend -t $ECR_REPOSITORY_BACKEND .
docker tag $ECR_REPOSITORY_BACKEND:latest $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest
docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest

# Create ECS cluster
echo "🖥️ Creating ECS cluster..."
aws ecs create-cluster --cluster-name $ECS_CLUSTER --region $AWS_REGION || true

echo "✅ Deployment completed! Next steps:"
echo "1. Create ECS task definitions in AWS Console"
echo "2. Create ECS services"
echo "3. Configure load balancer"
echo "4. Set up domain and SSL certificate"
