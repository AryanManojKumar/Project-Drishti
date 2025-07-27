# 🎯 Drishti Guard - Complete CNS Integration

## Overview
Complete integration between your Central Nervous System (CNS) backend and Next.js frontend with real-time data flow.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   FastAPI Bridge │────│  CNS Analysis   │
│  (Frontend)    │    │   (API Layer)    │    │   (Backend)     │
│                │    │                  │    │                 │
│ • Volunteer    │    │ • REST APIs      │    │ • IP Camera     │
│   Dashboard    │    │ • WebSockets     │    │ • Crowd Analysis│
│ • Live Alerts  │◄───┤ • Data Transform │◄───┤ • AI Processing │
│ • CNS Insights │    │ • CORS Support   │    │ • Predictions   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Method 1: Automatic Startup (Recommended)
```bash
# Run the automated startup script
start_drishti_system.bat
```

### Method 2: Manual Setup

#### 1. Start Backend
```bash
cd "bhai ka kaam/prediction"
pip install -r requirements-fastapi.txt
uvicorn fastapi_bridge:app --reload --port=8000
```

#### 2. Start Frontend
```bash
cd ui
npm install
npm run dev
```

#### 3. Test Integration
```bash
python test_integration.py
```

## 📊 Data Flow Integration

### 1. CNS Analysis → JSON Extraction

**File:** `cns_data_extractor.py`

```python
# Extracts CNS output into structured JSON
insights = cns_data_extractor.extract_crowd_safety_insights()
alerts = cns_data_extractor.extract_live_anomaly_alerts()
analysis = cns_data_extractor.extract_live_feed_analysis()
```

### 2. FastAPI Endpoints

**File:** `fastapi_bridge.py`

```python
# API endpoints for frontend consumption
@app.get("/api/cns/crowd-insights")    # → Crowd & Safety Insights
@app.get("/api/cns/anomaly-alerts")    # → Live Anomaly Alerts  
@app.get("/api/cns/feed-analysis")     # → Live Feed Analysis
@app.post("/api/cns/start-analysis")   # → Start IP Camera Analysis
```

### 3. Frontend Integration

**File:** `src/app/volunteer/page.tsx`

```typescript
// Real-time data loading with proper destructuring
const { getCrowdSafetyInsights, getLiveAnomalyAlerts } = useDrishtiAPI();

// Data flows to specific UI sections:
// • crowdInsights → "Crowd & Safety Insights" section
// • liveAnomalies → "Live Anomaly Alerts" section
```

## 🎯 Frontend Sections Mapping

### 1. **Crowd & Safety Insights**
- **Source:** `GET /api/cns/crowd-insights`
- **Data:** AI predictions, bottleneck analysis, venue-wide insights
- **Updates:** Every 30 seconds

```json
{
  "insights": [
    {
      "type": "CNS",
      "title": "High Traffic Prediction", 
      "description": "AI predicts high crowd density...",
      "location": "Main Entrance",
      "people_count": 15,
      "priority": "high"
    }
  ]
}
```

### 2. **Live Anomaly Alerts**
- **Source:** `GET /api/cns/anomaly-alerts`
- **Data:** Overcrowding detection, unusual movement patterns
- **Updates:** Real-time via WebSocket + polling

```json
{
  "alerts": [
    {
      "type": "Anomaly",
      "title": "Overcrowding Detected",
      "description": "Unusual crowd density forming...",
      "location": "Main Stage, East Entrance",
      "density_score": 8.5
    }
  ]
}
```

### 3. **Live Feed Analysis**
- **Source:** `GET /api/cns/feed-analysis`
- **Data:** Venue overview, camera details, predictions
- **Updates:** Continuous analysis

```json
{
  "analysis_data": {
    "venue_overview": {
      "total_people_detected": 45,
      "average_density": 6.2,
      "overall_status": "moderate_density"
    },
    "camera_details": [...],
    "predictions": {
      "bottleneck_risks": [...],
      "flow_recommendations": [...]
    }
  }
}
```

## 🔧 Configuration

### IP Camera Setup
Update in `fastapi_bridge.py` or send via API:

```json
{
  "camera_1": {
    "name": "Main Entrance Camera",
    "location": "Main Entrance", 
    "url": "http://192.168.0.119:8080/video",
    "latitude": 13.0358,
    "longitude": 77.6431,
    "priority": "high"
  }
}
```

### Environment Variables
**File:** `ui/.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_DEBUG_MODE=true
```

## 🧪 Testing

### Full Integration Test
```bash
python test_integration.py
```

### Individual Endpoints
```bash
python test_integration.py endpoints
```

### Manual Testing
1. **Start Analysis:** Click "Start Analysis" in volunteer dashboard
2. **Verify Data:** Check browser console for CNS data loading
3. **Live Updates:** Wait 30 seconds for automatic refresh

## 📱 Frontend Features

### Volunteer Dashboard (`/volunteer`)
- **My Dispatches:** Manual dispatch management
- **Live Anomaly Alerts:** Real-time CNS anomaly detection
- **Crowd & Safety Insights:** AI-powered predictions and analysis
- **Connection Status:** Live backend connection indicator
- **Start Analysis Button:** Trigger CNS analysis

### Real-time Updates
- **Polling:** Every 30 seconds for fresh data
- **WebSocket:** For instant notifications (future enhancement)
- **Error Handling:** Graceful fallback to cached data

## 🔍 Debugging

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### Check CNS Status
```bash
curl http://localhost:8000/api/cns/status
```

### Check Live Data
```bash
curl http://localhost:8000/api/cns/crowd-insights
curl http://localhost:8000/api/cns/anomaly-alerts
```

### Frontend Console
Open browser dev tools and check:
- Network requests to API endpoints
- Console logs for data loading
- React component state updates

## 🚨 Troubleshooting

### Backend Issues
1. **Port 8000 in use:** Change port in startup commands
2. **Missing dependencies:** Run `pip install -r requirements-fastapi.txt`
3. **CNS not starting:** Check IP camera URL in configuration

### Frontend Issues
1. **API connection failed:** Verify backend is running on port 8000
2. **No data loading:** Check CORS settings in `fastapi_bridge.py`
3. **TypeScript errors:** Ensure all types are properly cast

### Integration Issues
1. **No CNS data:** Click "Start Analysis" and wait 30 seconds
2. **Stale data:** Check if CNS analysis is actively running
3. **Connection errors:** Verify both servers are running

## 📈 Performance

### Optimization Settings
- **API polling:** 30-second intervals (configurable)
- **Data caching:** Client-side caching with fallbacks
- **Error recovery:** Automatic retry with exponential backoff

### Production Deployment
1. **Backend:** Deploy to Heroku/DigitalOcean/AWS
2. **Frontend:** Deploy to Firebase/Vercel/Netlify
3. **Environment:** Update API URLs in production env vars

## 🎉 Success Indicators

✅ **Backend:** FastAPI docs accessible at `http://localhost:8000/docs`
✅ **Frontend:** Volunteer dashboard loads at `http://localhost:3000/volunteer`
✅ **Integration:** "Start Analysis" button triggers CNS and loads live data
✅ **Real-time:** Data refreshes every 30 seconds with new insights
✅ **Error Handling:** Graceful fallbacks when CNS data unavailable

Your Drishti Guard system is now fully integrated! 🚀
