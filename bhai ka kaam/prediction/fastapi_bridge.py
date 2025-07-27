"""
FastAPI Bridge for Drishti Guard Backend
Converts Streamlit functionality to REST API endpoints for Next.js integration
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn

# Import your existing Streamlit modules
from live_crowd_predictor import (
    central_nervous_system, 
    get_central_status, 
    start_central_monitoring, 
    stop_central_monitoring
)
from map_crowd_analyzer import analyze_complete_crowd_situation
from crowd_predictor import get_crowd_density
from api_mitigation_service import APIMitigationService
from cns_data_extractor import cns_data_extractor

app = FastAPI(
    title="Drishti Guard API",
    description="AI-powered event security platform backend",
    version="1.0.0"
)

# Enable CORS for Firebase hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-actual-firebase-app.firebaseapp.com",  # Replace with your Firebase app
        "https://your-actual-firebase-app.web.app",          # Replace with your Firebase app
        "http://localhost:3000",  # For development
        "http://localhost:3001",  # Alternative dev port
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
mitigation_service = APIMitigationService()

# Data models
class SOSRequest(BaseModel):
    user_id: str
    location: Dict[str, float]  # {"lat": 40.7128, "lng": -74.0060}
    emergency_type: str
    timestamp: str

class DispatchUpdate(BaseModel):
    dispatch_id: str
    volunteer_id: str
    status: str  # "acknowledged", "en_route", "completed"
    location: Optional[Dict[str, float]] = None

class CrowdAnalysisRequest(BaseModel):
    camera_feed_url: Optional[str] = None
    location: Dict[str, float]
    analysis_type: str = "full"

# Active connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.volunteer_connections: Dict[str, WebSocket] = {}
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_type: str, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_type == "volunteer" and user_id:
            self.volunteer_connections[user_id] = websocket
        elif user_type == "admin":
            self.admin_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, user_type: str, user_id: str = None):
        self.active_connections.remove(websocket)
        
        if user_type == "volunteer" and user_id in self.volunteer_connections:
            del self.volunteer_connections[user_id]
        elif user_type == "admin" and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_volunteers(self, message: str):
        for websocket in self.volunteer_connections.values():
            await websocket.send_text(message)

    async def broadcast_to_admins(self, message: str):
        for websocket in self.admin_connections:
            await websocket.send_text(message)

manager = ConnectionManager()

# In-memory storage (replace with database in production)
active_sos = {}
dispatches = {}
volunteer_locations = {}
crowd_insights = {}

@app.get("/")
async def root():
    return {"message": "Drishti Guard API is running", "status": "healthy"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    central_status = get_central_status()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "central_nervous_system": central_status,
        "services": {
            "crowd_analysis": True,
            "sos_system": True,
            "dispatch_system": True
        }
    }

# SOS Endpoints
@app.post("/api/sos/create")
async def create_sos(sos_request: SOSRequest):
    """Create new SOS alert"""
    try:
        sos_id = f"sos_{int(time.time())}"
        
        sos_data = {
            "id": sos_id,
            "user_id": sos_request.user_id,
            "location": sos_request.location,
            "emergency_type": sos_request.emergency_type,
            "timestamp": sos_request.timestamp,
            "status": "active",
            "assigned_volunteer": None
        }
        
        active_sos[sos_id] = sos_data
        
        # Broadcast to volunteers
        await manager.broadcast_to_volunteers(json.dumps({
            "type": "new_sos",
            "data": sos_data
        }))
        
        # Broadcast to admins
        await manager.broadcast_to_admins(json.dumps({
            "type": "new_sos",
            "data": sos_data
        }))
        
        return {"success": True, "sos_id": sos_id, "message": "SOS alert created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sos/active")
async def get_active_sos():
    """Get all active SOS alerts"""
    return {"sos_alerts": list(active_sos.values())}

# Dispatch Endpoints
@app.post("/api/dispatch/acknowledge")
async def acknowledge_dispatch(update: DispatchUpdate):
    """Volunteer acknowledges dispatch"""
    try:
        if update.dispatch_id in dispatches:
            dispatches[update.dispatch_id]["status"] = "acknowledged"
            dispatches[update.dispatch_id]["volunteer_id"] = update.volunteer_id
            dispatches[update.dispatch_id]["acknowledged_at"] = datetime.now().isoformat()
            
            # Update volunteer location if provided
            if update.location:
                volunteer_locations[update.volunteer_id] = update.location
            
            # Notify admins
            await manager.broadcast_to_admins(json.dumps({
                "type": "dispatch_acknowledged",
                "data": dispatches[update.dispatch_id]
            }))
            
            return {"success": True, "message": "Dispatch acknowledged"}
        else:
            raise HTTPException(status_code=404, detail="Dispatch not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/volunteer/{volunteer_id}/dispatches")
async def get_volunteer_dispatches(volunteer_id: str):
    """Get dispatches for specific volunteer"""
    volunteer_dispatches = [
        dispatch for dispatch in dispatches.values() 
        if dispatch.get("assigned_volunteer") == volunteer_id
    ]
    return {"dispatches": volunteer_dispatches}

# Crowd Analysis Endpoints
@app.post("/api/crowd/analyze")
async def analyze_crowd(request: CrowdAnalysisRequest):
    """Analyze crowd from camera feed or location"""
    try:
        # Use your existing crowd analysis
        if request.camera_feed_url:
            # Analyze from camera feed
            density_result = get_crowd_density(request.camera_feed_url)
        else:
            # Analyze from location data
            density_result = {"density": "medium", "risk_level": "low"}
        
        # Get complete analysis
        analysis_result = analyze_complete_crowd_situation(
            location=request.location,
            additional_data=density_result
        )
        
        # Store insights
        insight_id = f"insight_{int(time.time())}"
        crowd_insights[insight_id] = {
            "id": insight_id,
            "location": request.location,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to admins if high risk
        if analysis_result.get("risk_level") == "high":
            await manager.broadcast_to_admins(json.dumps({
                "type": "high_risk_detected",
                "data": crowd_insights[insight_id]
            }))
        
        return {"success": True, "analysis": analysis_result, "insight_id": insight_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crowd/insights")
async def get_crowd_insights():
    """Get latest crowd insights"""
    return {"insights": list(crowd_insights.values())[-10:]}  # Last 10 insights

# Real-time WebSocket endpoints
@app.websocket("/ws/volunteer/{volunteer_id}")
async def volunteer_websocket(websocket: WebSocket, volunteer_id: str):
    await manager.connect(websocket, "volunteer", volunteer_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "location_update":
                volunteer_locations[volunteer_id] = message["location"]
                
            elif message["type"] == "status_update":
                # Handle volunteer status updates
                await manager.broadcast_to_admins(json.dumps({
                    "type": "volunteer_status",
                    "volunteer_id": volunteer_id,
                    "status": message["status"],
                    "location": volunteer_locations.get(volunteer_id)
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "volunteer", volunteer_id)

@app.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await manager.connect(websocket, "admin")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "create_dispatch":
                # Create new dispatch
                dispatch_id = f"dispatch_{int(time.time())}"
                dispatch_data = {
                    "id": dispatch_id,
                    "type": message.get("dispatch_type", "general"),
                    "description": message.get("description"),
                    "location": message.get("location"),
                    "priority": message.get("priority", "medium"),
                    "created_at": datetime.now().isoformat(),
                    "status": "pending"
                }
                
                dispatches[dispatch_id] = dispatch_data
                
                # Broadcast to volunteers
                await manager.broadcast_to_volunteers(json.dumps({
                    "type": "new_dispatch",
                    "data": dispatch_data
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "admin")

@app.websocket("/ws/attendee/{user_id}")
async def attendee_websocket(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, "attendee", user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "emergency_sos":
                # Handle SOS from attendee
                sos_request = SOSRequest(
                    user_id=user_id,
                    location=message["location"],
                    emergency_type=message.get("emergency_type", "general"),
                    timestamp=datetime.now().isoformat()
                )
                await create_sos(sos_request)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "attendee", user_id)

# Central Nervous System endpoints
@app.post("/api/cns/start")
async def start_monitoring():
    """Start central nervous system monitoring"""
    try:
        result = start_central_monitoring()
        return {"success": True, "message": "Central monitoring started", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cns/stop")
async def stop_monitoring():
    """Stop central nervous system monitoring"""
    try:
        result = stop_central_monitoring()
        return {"success": True, "message": "Central monitoring stopped", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cns/status")
async def get_cns_status():
    """Get central nervous system status"""
    status = get_central_status()
    return {"status": status}

# CNS Data Extraction Endpoints for Frontend Integration
@app.get("/api/cns/crowd-insights")
async def get_crowd_safety_insights():
    """
    Get Crowd & Safety Insights for frontend 'Crowd & Safety Insights' section
    """
    try:
        insights = cns_data_extractor.extract_crowd_safety_insights()
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cns/anomaly-alerts")
async def get_live_anomaly_alerts():
    """
    Get Live Anomaly Alerts for frontend 'Live Anomaly Alerts' section
    """
    try:
        alerts = cns_data_extractor.extract_live_anomaly_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cns/feed-analysis")
async def get_live_feed_analysis():
    """
    Get Live Feed Analysis & Predictions data
    """
    try:
        analysis = cns_data_extractor.extract_live_feed_analysis()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cns/start-analysis")
async def start_cns_analysis(ip_camera_config: Optional[Dict] = None):
    """
    Start CNS analysis with IP camera configuration
    """
    try:
        # Start central monitoring with IP camera config if provided
        if ip_camera_config:
            result = start_central_monitoring(ip_camera_config=ip_camera_config)
        else:
            result = start_central_monitoring()
        
        # Get initial analysis data
        insights = cns_data_extractor.extract_crowd_safety_insights()
        alerts = cns_data_extractor.extract_live_anomaly_alerts()
        feed_analysis = cns_data_extractor.extract_live_feed_analysis()
        
        return {
            "success": True, 
            "message": "CNS analysis started successfully", 
            "cns_status": result,
            "initial_data": {
                "crowd_insights": insights,
                "anomaly_alerts": alerts,
                "feed_analysis": feed_analysis
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_bridge:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
