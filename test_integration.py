"""
Complete Integration Test for CNS + Frontend
Run this to test the complete flow from CNS analysis to frontend display
"""

import sys
import time
import requests
import json
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_cns_integration():
    """Complete integration test for CNS system"""
    
    print("🧪 DRISHTI GUARD INTEGRATION TEST")
    print("=" * 50)
    
    # Step 1: Test Backend Health
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            health_data = response.json()
            print(f"   - Central Nervous System: {health_data.get('central_nervous_system', 'Unknown')}")
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Step 2: Start CNS Analysis
    print("\n2. Starting CNS Analysis...")
    try:
        # IP camera configuration for testing
        ip_camera_config = {
            "camera_1": {
                "name": "Main Entrance Camera",
                "location": "Main Entrance",
                "url": "http://192.168.0.119:8080/video",  # Your IP camera
                "latitude": 13.0358,
                "longitude": 77.6431,
                "priority": "high",
                "bottleneck_risk": "high"
            }
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/cns/start-analysis",
            json={"ip_camera_config": ip_camera_config}
        )
        
        if response.status_code == 200:
            print("✅ CNS Analysis started")
            start_data = response.json()
            print(f"   - Success: {start_data.get('success', False)}")
            print(f"   - Message: {start_data.get('message', 'Unknown')}")
        else:
            print("❌ Failed to start CNS analysis")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ CNS start failed: {e}")
    
    # Step 3: Wait for analysis to process
    print("\n3. Waiting for analysis to process...")
    time.sleep(5)
    
    # Step 4: Test Crowd Insights Endpoint
    print("\n4. Testing Crowd & Safety Insights...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/cns/crowd-insights")
        if response.status_code == 200:
            insights_data = response.json()
            print("✅ Crowd insights retrieved")
            print(f"   - Success: {insights_data.get('success', False)}")
            print(f"   - Total insights: {insights_data.get('total_insights', 0)}")
            
            # Display sample insights
            insights = insights_data.get('insights', [])
            for i, insight in enumerate(insights[:2]):  # Show first 2
                print(f"   - Insight {i+1}: {insight.get('title', 'No title')}")
                print(f"     Location: {insight.get('location', 'Unknown')}")
                print(f"     Description: {insight.get('description', 'No description')[:60]}...")
        else:
            print("❌ Failed to get crowd insights")
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Crowd insights test failed: {e}")
    
    # Step 5: Test Live Anomaly Alerts
    print("\n5. Testing Live Anomaly Alerts...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/cns/anomaly-alerts")
        if response.status_code == 200:
            alerts_data = response.json()
            print("✅ Anomaly alerts retrieved")
            print(f"   - Success: {alerts_data.get('success', False)}")
            print(f"   - Total alerts: {alerts_data.get('total_alerts', 0)}")
            
            # Display sample alerts
            alerts = alerts_data.get('alerts', [])
            for i, alert in enumerate(alerts[:2]):  # Show first 2
                print(f"   - Alert {i+1}: {alert.get('title', 'No title')}")
                print(f"     Type: {alert.get('type', 'Unknown')}")
                print(f"     Location: {alert.get('location', 'Unknown')}")
        else:
            print("❌ Failed to get anomaly alerts")
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Anomaly alerts test failed: {e}")
    
    # Step 6: Test Live Feed Analysis
    print("\n6. Testing Live Feed Analysis...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/cns/feed-analysis")
        if response.status_code == 200:
            analysis_data = response.json()
            print("✅ Feed analysis retrieved")
            print(f"   - Success: {analysis_data.get('success', False)}")
            
            # Display venue overview
            venue_data = analysis_data.get('analysis_data', {}).get('venue_overview', {})
            print(f"   - Total cameras: {venue_data.get('total_cameras', 0)}")
            print(f"   - Active cameras: {venue_data.get('active_cameras', 0)}")
            print(f"   - Total people detected: {venue_data.get('total_people_detected', 0)}")
            print(f"   - Overall status: {venue_data.get('overall_status', 'Unknown')}")
        else:
            print("❌ Failed to get feed analysis")
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Feed analysis test failed: {e}")
    
    # Step 7: Test Frontend Connection (if available)
    print("\n7. Testing Frontend Connection...")
    try:
        import urllib.request
        urllib.request.urlopen(FRONTEND_URL, timeout=3)
        print("✅ Frontend is accessible")
        print(f"   - URL: {FRONTEND_URL}")
        print("   - Navigate to /volunteer to see live CNS data")
    except Exception as e:
        print(f"⚠️  Frontend not accessible: {e}")
        print(f"   - Make sure to run: npm run dev in the UI folder")
    
    # Step 8: Test CNS Status
    print("\n8. Testing CNS Status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/cns/status")
        if response.status_code == 200:
            status_data = response.json()
            print("✅ CNS status retrieved")
            
            # Display system status
            cns_status = status_data.get('status', {})
            if isinstance(cns_status, dict):
                print(f"   - System active: {cns_status.get('is_active', False)}")
                if 'cameras' in cns_status:
                    print(f"   - Total cameras configured: {len(cns_status['cameras'])}")
        else:
            print("❌ Failed to get CNS status")
    except Exception as e:
        print(f"❌ CNS status test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST COMPLETE")
    print("\n📋 NEXT STEPS:")
    print("1. Start backend: uvicorn fastapi_bridge:app --reload --port=8000")
    print("2. Start frontend: npm run dev (in UI folder)")
    print("3. Open browser: http://localhost:3000/volunteer")
    print("4. Click 'Start Analysis' to see live CNS data")
    print("\n🚀 Your Drishti Guard system is ready!")
    
    return True

def test_individual_endpoints():
    """Test individual endpoints for debugging"""
    print("\n🔍 INDIVIDUAL ENDPOINT TESTS")
    print("-" * 30)
    
    endpoints = [
        "/api/health",
        "/api/cns/status", 
        "/api/cns/crowd-insights",
        "/api/cns/anomaly-alerts",
        "/api/cns/feed-analysis"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{endpoint}: {status}")
        except Exception as e:
            print(f"{endpoint}: ❌ ERROR - {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "endpoints":
        test_individual_endpoints()
    else:
        test_cns_integration()
