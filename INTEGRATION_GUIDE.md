# Drishti Guard - Complete Integration Guide

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   FastAPI Bridge │────│  Streamlit Logic │
│  (Firebase)    │    │   (Heroku/VPS)   │    │   (Background)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Deployment Steps

### 1. Backend Deployment (FastAPI Bridge)

#### Option A: Deploy to Heroku
```bash
# In your prediction folder
cd "c:\Users\Aryan\Desktop\version control\nf2\bhai ka kaam\prediction"

# Install FastAPI requirements
pip install -r requirements-fastapi.txt

# Create Procfile
echo "web: uvicorn fastapi_bridge:app --host=0.0.0.0 --port=$PORT" > Procfile

# Deploy to Heroku
heroku create drishti-guard-api
heroku config:set PYTHON_VERSION=3.9.16
git add .
git commit -m "Add FastAPI bridge"
git push heroku main
```

#### Option B: Deploy to DigitalOcean/VPS
```bash
# On your server
sudo apt update
sudo apt install python3-pip nginx

# Clone your repo
git clone your-repo
cd prediction

# Install dependencies
pip3 install -r requirements-fastapi.txt

# Run with systemd
sudo nano /etc/systemd/system/drishti-api.service
```

**Service file content:**
```ini
[Unit]
Description=Drishti Guard API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/prediction
Environment=PATH=/usr/bin
ExecStart=/usr/local/bin/uvicorn fastapi_bridge:app --host=0.0.0.0 --port=8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable drishti-api
sudo systemctl start drishti-api
```

### 2. Frontend Configuration

#### Update API URLs
```bash
# In your UI folder
cd "c:\Users\Aryan\Desktop\version control\nf2\ui"

# Create production environment
echo "NEXT_PUBLIC_API_URL=https://your-api-domain.com" > .env.production
echo "NEXT_PUBLIC_WS_URL=wss://your-api-domain.com" >> .env.production
```

#### Build and Deploy to Firebase
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase (if not done)
firebase init hosting

# Build the project
npm run build

# Deploy to Firebase
firebase deploy
```

### 3. CORS Configuration

Update your FastAPI CORS settings in `fastapi_bridge.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.firebaseapp.com",
        "https://your-app.web.app",
        "https://your-custom-domain.com",
        "http://localhost:3000",  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 Development Workflow

### Local Development Setup

1. **Start Backend:**
```bash
cd "c:\Users\Aryan\Desktop\version control\nf2\bhai ka kaam\prediction"
pip install -r requirements-fastapi.txt
uvicorn fastapi_bridge:app --reload --port=8000
```

2. **Start Frontend:**
```bash
cd "c:\Users\Aryan\Desktop\version control\nf2\ui"
npm run dev
```

3. **Test Integration:**
```bash
# Test API health
curl http://localhost:8000/api/health

# Test WebSocket
# Use browser dev tools or WebSocket testing tool
```

### Alternative Integration Options

#### Option 1: Streamlit as Microservice (Current Recommendation)
- Convert core Streamlit functions to FastAPI endpoints
- Keep Streamlit running in background for heavy processing
- Use FastAPI as the API gateway
- **Pros:** Minimal code changes, better performance, real-time capabilities
- **Cons:** Additional deployment complexity

#### Option 2: Direct Streamlit API
```python
# Add to your existing Streamlit app
import streamlit as st
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

# Create FastAPI app alongside Streamlit
api = FastAPI()
api.add_middleware(CORSMiddleware, allow_origins=["*"])

@api.get("/api/sos")
def create_sos():
    # Your SOS logic here
    return {"status": "success"}

# Run both servers
if __name__ == "__main__":
    import uvicorn
    threading.Thread(
        target=lambda: uvicorn.run(api, host="0.0.0.0", port=8001),
        daemon=True
    ).start()
    st.run()
```

#### Option 3: Serverless Functions
Convert backend to Vercel/Netlify functions:

```typescript
// api/sos.ts (Vercel)
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // Handle SOS creation
    res.status(200).json({ success: true })
  }
}
```

## 📱 Mobile App Integration

For mobile apps, use the same API endpoints:

```javascript
// React Native example
const createSOS = async (location) => {
  const response = await fetch('https://your-api-domain.com/api/sos/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      location: location,
      emergency_type: 'general',
      timestamp: new Date().toISOString(),
    }),
  });
  return response.json();
};
```

## 🔐 Security Considerations

1. **API Authentication:**
```python
# Add to FastAPI
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

@app.get("/api/protected")
async def protected_route(token: str = Depends(security)):
    # Verify JWT token
    payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
    return {"user": payload}
```

2. **Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/sos/create")
@limiter.limit("5/minute")
async def create_sos(request: Request):
    # Limited to 5 SOS requests per minute
    pass
```

3. **Input Validation:**
```python
from pydantic import BaseModel, validator

class SOSRequest(BaseModel):
    user_id: str
    location: Dict[str, float]
    
    @validator('location')
    def validate_location(cls, v):
        if 'lat' not in v or 'lng' not in v:
            raise ValueError('Location must have lat and lng')
        if not (-90 <= v['lat'] <= 90):
            raise ValueError('Invalid latitude')
        if not (-180 <= v['lng'] <= 180):
            raise ValueError('Invalid longitude')
        return v
```

## 📊 Monitoring and Analytics

1. **API Monitoring:**
```python
import logging
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

2. **Error Tracking:**
```bash
# Install Sentry
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

## 🧪 Testing

```bash
# Backend tests
pytest tests/

# Frontend tests
npm run test

# Integration tests
npm run test:e2e
```

## 📈 Performance Optimization

1. **Caching:**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="drishti-cache")

@cache(expire=300)  # Cache for 5 minutes
async def get_crowd_insights():
    # Expensive operation
    pass
```

2. **Database Connection Pooling:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
)
```

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors:**
   - Ensure correct origin URLs in CORS settings
   - Check for trailing slashes in URLs

2. **WebSocket Connection Failed:**
   - Verify WebSocket URL uses `ws://` or `wss://`
   - Check firewall settings

3. **API Not Found:**
   - Verify backend is running on correct port
   - Check environment variables

4. **Real-time Updates Not Working:**
   - Ensure WebSocket connections are established
   - Check browser console for connection errors

### Debug Commands:
```bash
# Check API health
curl https://your-api-domain.com/api/health

# Test WebSocket connection
wscat -c wss://your-api-domain.com/ws/volunteer/test-id

# Check logs
heroku logs --tail -a drishti-guard-api
```

This setup gives you a production-ready integration between your Next.js frontend and Streamlit backend with real-time capabilities! 🎯
