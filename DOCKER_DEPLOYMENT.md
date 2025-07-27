# 🚀 Drishti Guard Cloud Deployment Guide

## 🐳 Docker Deployment Options

### 1. Local Docker Testing

```bash
# Test locally with Docker Compose
.\test-docker.bat

# Or manually:
docker-compose up --build
```

### 2. AWS ECS Deployment

**Prerequisites:**
- AWS CLI configured
- Docker installed
- AWS account with ECS permissions

```bash
# Make script executable
chmod +x deploy-aws.sh

# Deploy to AWS ECS
./deploy-aws.sh
```

**What it does:**
- Creates ECR repositories
- Builds and pushes Docker images
- Creates ECS cluster
- Sets up container services

### 3. Google Cloud Run Deployment

**Prerequisites:**
- Google Cloud SDK installed
- Docker installed
- GCP project with billing enabled

```bash
# Update project ID in deploy-gcp.sh
# Make script executable
chmod +x deploy-gcp.sh

# Deploy to Google Cloud Run
./deploy-gcp.sh
```

**Benefits:**
- Serverless - pay only for usage
- Auto-scaling
- Built-in load balancing
- HTTPS by default

### 4. Azure Container Instances

**Prerequisites:**
- Azure CLI installed
- Docker installed
- Azure subscription

```bash
# Make script executable
chmod +x deploy-azure.sh

# Deploy to Azure
./deploy-azure.sh
```

## 🔧 Configuration

### Environment Variables

Create `.env` files for different environments:

**Backend (.env):**
```env
GEMINI_API_KEY=your_gemini_api_key_here
PYTHONUNBUFFERED=1
CAMERA_IP=192.168.0.119:8080
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=production
```

### Production Optimizations

1. **Enable SSL/HTTPS**
   - Add SSL certificates to nginx.conf
   - Update environment variables for HTTPS URLs

2. **Database Configuration**
   - Add persistent storage for analytics
   - Configure Redis for caching

3. **Monitoring**
   - Add health checks
   - Configure logging
   - Set up alerts

## 📊 Resource Requirements

### Minimum Requirements:
- **Frontend**: 512MB RAM, 0.5 CPU
- **Backend**: 2GB RAM, 1 CPU
- **Storage**: 5GB for logs and temp files

### Recommended Production:
- **Frontend**: 1GB RAM, 1 CPU
- **Backend**: 4GB RAM, 2 CPU
- **Storage**: 20GB SSD

## 🛡️ Security Considerations

1. **API Keys**: Store in cloud secret managers
2. **Network**: Use VPC/firewall rules
3. **HTTPS**: Always use SSL in production
4. **Authentication**: Implement proper auth tokens
5. **CORS**: Configure proper CORS policies

## 📈 Scaling

### Horizontal Scaling:
- Multiple frontend instances behind load balancer
- Backend auto-scaling based on CPU/memory
- Database read replicas

### Vertical Scaling:
- Increase container resources
- Optimize Docker images
- Use multi-stage builds

## 🔍 Monitoring & Debugging

### Health Checks:
- Frontend: `http://localhost:3000/api/health`
- Backend: `http://localhost:8000/api/health`

### Logs:
```bash
# Docker Compose logs
docker-compose logs -f

# Individual service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Common Issues:

1. **Port conflicts**: Check if ports 3000/8000 are free
2. **Memory issues**: Increase container memory limits
3. **API connectivity**: Verify network between containers
4. **CORS errors**: Check nginx.conf CORS headers

## 🚀 Quick Start Commands

```bash
# Build everything
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker-compose down -v --rmi all
```

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify environment variables
3. Test network connectivity
4. Review resource usage

Your Drishti Guard system is now ready for cloud deployment! 🚀
