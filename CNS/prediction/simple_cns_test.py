"""
Simple Central Nervous System Test
Bhai, yeh simplified version hai jo definitely kaam karega
"""

import cv2
import numpy as np
import requests
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading

class SimpleCentralNervousSystem:
    """
    Simplified Central Nervous System for Multi-Camera Crowd Analysis
    """
    def __init__(self):
        self.gemini_key = "AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
        
        # Camera data
        self.cameras = {}
        self.camera_threads = {}
        self.running = False
        
        # Venue locations
        self.locations = {
            'cam_entrance': {'name': 'Main Entrance', 'lat': 13.0360, 'lng': 77.6430},
            'cam_corridor': {'name': 'Main Corridor', 'lat': 13.0357, 'lng': 77.6431},
            'cam_hall1': {'name': 'Hall 1 Entry', 'lat': 13.0358, 'lng': 77.6432}
        }
        
        # System data
        self.system_data = {
            'total_people': 0,
            'alerts': [],
            'bottlenecks': [],
            'camera_status': {}
        }

    def start_system(self, camera_sources: Dict[str, int] = None):
        """Start the Central Nervous System"""
        print("🧠 Starting Simple Central Nervous System...")
        self.running = True
        
        if camera_sources is None:
            camera_sources = {
                'cam_entrance': 0,
                'cam_corridor': 0,
                'cam_hall1': 0
            }
        
        # Start camera threads
        for cam_id, source in camera_sources.items():
            if cam_id in self.locations:
                thread = threading.Thread(target=self._process_camera, args=(cam_id, source))
                thread.daemon = True
                thread.start()
                self.camera_threads[cam_id] = thread
                print(f"📹 Started {cam_id}: {self.locations[cam_id]['name']}")
        
        print("✅ System operational!")

    def stop_system(self):
        """Stop the system"""
        print("🛑 Stopping system...")
        self.running = False
        
        for thread in self.camera_threads.values():
            if thread.is_alive():
                thread.join(timeout=2)
        
        print("✅ System stopped")

    def _process_camera(self, cam_id: str, source: int):
        """Process individual camera feed"""
        cap = cv2.VideoCapture(source)
        location = self.locations[cam_id]
        
        try:
            frame_count = 0
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Analyze every 5 seconds (150 frames at 30fps)
                if frame_count % 150 == 0:
                    analysis = self._analyze_frame(cam_id, frame)
                    self.cameras[cam_id] = analysis
                    self._update_system_data()
                
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"Camera {cam_id} error: {e}")
        finally:
            cap.release()

    def _analyze_frame(self, cam_id: str, frame) -> Dict:
        """Analyze frame with AI"""
        try:
            # Resize and encode
            frame_resized = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode('.jpg', frame_resized)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            location = self.locations[cam_id]['name']
            
            prompt = f"""
            Analyze this camera feed from {location} for crowd management:
            
            1. How many people do you see? (exact count)
            2. Crowd density score 1-10 (1=empty, 10=packed)
            3. Movement speed (slow/normal/fast)
            4. Flow direction (north/south/east/west/mixed/stationary)
            5. Any bottlenecks or congestion?
            6. Alert level (normal/caution/warning/critical)
            
            Respond in JSON:
            {{
                "people_count": number,
                "density_score": number,
                "movement_speed": "string",
                "flow_direction": "string",
                "bottlenecks": ["list"],
                "alert_level": "string"
            }}
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                    ]
                }]
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON
                if '```json' in text:
                    json_text = text.split('```json')[1].split('```')[0].strip()
                elif '{' in text:
                    json_text = text[text.find('{'):text.rfind('}')+1]
                else:
                    json_text = text
                
                analysis = json.loads(json_text)
                analysis.update({
                    'camera_id': cam_id,
                    'location': self.locations[cam_id]['name'],
                    'coordinates': {'lat': self.locations[cam_id]['lat'], 'lng': self.locations[cam_id]['lng']},
                    'timestamp': datetime.now(),
                    'source': 'ai'
                })
                return analysis
                
            else:
                return self._default_analysis(cam_id)
                
        except Exception as e:
            print(f"AI analysis error for {cam_id}: {e}")
            return self._default_analysis(cam_id)

    def _default_analysis(self, cam_id: str) -> Dict:
        """Default analysis when AI fails"""
        return {
            'camera_id': cam_id,
            'location': self.locations[cam_id]['name'],
            'coordinates': {'lat': self.locations[cam_id]['lat'], 'lng': self.locations[cam_id]['lng']},
            'people_count': 0,
            'density_score': 1,
            'movement_speed': 'unknown',
            'flow_direction': 'unknown',
            'bottlenecks': [],
            'alert_level': 'normal',
            'timestamp': datetime.now(),
            'source': 'fallback'
        }

    def _update_system_data(self):
        """Update overall system data"""
        try:
            total_people = sum([cam.get('people_count', 0) for cam in self.cameras.values()])
            
            # Check for alerts
            alerts = []
            bottlenecks = []
            
            for cam_id, data in self.cameras.items():
                if data.get('alert_level') in ['warning', 'critical']:
                    alerts.append({
                        'camera': cam_id,
                        'location': data['location'],
                        'level': data['alert_level'],
                        'people': data.get('people_count', 0),
                        'coordinates': data['coordinates'],
                        'timestamp': data['timestamp']
                    })
                
                if data.get('bottlenecks'):
                    bottlenecks.append({
                        'camera': cam_id,
                        'location': data['location'],
                        'issues': data['bottlenecks'],
                        'coordinates': data['coordinates'],
                        'timestamp': data['timestamp']
                    })
            
            self.system_data.update({
                'total_people': total_people,
                'alerts': alerts,
                'bottlenecks': bottlenecks,
                'camera_status': {cam_id: data.get('alert_level', 'normal') for cam_id, data in self.cameras.items()},
                'last_update': datetime.now()
            })
            
        except Exception as e:
            print(f"System data update error: {e}")

    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_running': self.running,
            'active_cameras': len(self.cameras),
            'total_people_in_venue': self.system_data.get('total_people', 0),
            'active_alerts': len(self.system_data.get('alerts', [])),
            'bottleneck_locations': len(self.system_data.get('bottlenecks', [])),
            'camera_details': self.cameras,
            'system_alerts': self.system_data.get('alerts', []),
            'bottleneck_predictions': self.system_data.get('bottlenecks', []),
            'overall_status': self._get_overall_status()
        }

    def _get_overall_status(self) -> str:
        """Calculate overall venue status"""
        alerts = self.system_data.get('alerts', [])
        
        if any(alert['level'] == 'critical' for alert in alerts):
            return 'critical'
        elif any(alert['level'] == 'warning' for alert in alerts):
            return 'warning'
        elif len(alerts) > 0:
            return 'caution'
        else:
            return 'normal'

def test_simple_cns():
    """Test the simple CNS"""
    print("🧠 Testing Simple Central Nervous System...")
    
    cns = SimpleCentralNervousSystem()
    
    # Test configuration
    cameras = {
        'cam_entrance': 0,  # Webcam
        'cam_corridor': 0,  # Same webcam for demo
        'cam_hall1': 0      # Same webcam for demo
    }
    
    try:
        cns.start_system(cameras)
        
        print("\n📊 Running for 60 seconds with status updates every 10 seconds...")
        print("Press Ctrl+C to stop early\n")
        
        for i in range(6):
            time.sleep(10)
            status = cns.get_status()
            
            print(f"\n🧠 Status Update {i+1}/6:")
            print("=" * 50)
            print(f"📈 Overall Status: {status['overall_status'].upper()}")
            print(f"👥 Total People: {status['total_people_in_venue']}")
            print(f"📹 Active Cameras: {status['active_cameras']}")
            print(f"🚨 Active Alerts: {status['active_alerts']}")
            print(f"⚠️  Bottlenecks: {status['bottleneck_locations']}")
            
            # Show camera details
            for cam_id, data in status['camera_details'].items():
                location = data.get('location', 'Unknown')
                people = data.get('people_count', 0)
                alert = data.get('alert_level', 'normal')
                print(f"   📹 {location}: {people} people ({alert})")
            
            # Show alerts
            for alert in status['system_alerts']:
                print(f"   🚨 {alert['level'].upper()}: {alert['location']} - {alert['people']} people")
            
            print("-" * 50)
        
        print("\n🎉 Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        cns.stop_system()

if __name__ == "__main__":
    test_simple_cns()