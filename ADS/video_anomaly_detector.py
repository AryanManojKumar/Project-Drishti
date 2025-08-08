import cv2
import base64
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from dataclasses import dataclass
from enum import Enum
import threading

class AnomalyCategory(Enum):
    CROWD_CONTROL = "crowd_control"
    SECURITY_THREAT = "security_threat"
    MEDICAL_EMERGENCY = "medical_emergency"
    FIRE_HAZARD = "fire_hazard"
    STRUCTURAL_DAMAGE = "structural_damage"
    WEATHER_EMERGENCY = "weather_emergency"
    VEHICLE_INCIDENT = "vehicle_incident"
    EQUIPMENT_FAILURE = "equipment_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    VIOLENCE_AGGRESSION = "violence_aggression"
    STAMPEDE_RISK = "stampede_risk"
    EVACUATION_NEEDED = "evacuation_needed"

class SeverityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class AnomalyReport:
    timestamp: str
    category: AnomalyCategory
    severity: SeverityLevel
    situation_overview: str
    severity_assessment: str
    hazard_analysis: str
    immediate_actions: List[str]
    equipment_required: List[str]
    de_escalation_strategy: str
    resolution_method: str
    confidence_score: float
    location_description: str

class VideoAnomalyDetector:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

        self.anomaly_reports = []
        self.is_monitoring = False
        self.last_analysis_time = 0
        self.analysis_interval = 3  # Analyze every 3 seconds
    

        
    def get_anomaly_detection_prompt(self) -> str:
        return """
        Analyze this image for safety anomalies at a large event. Look for:
        - Crowd control issues (overcrowding, bottlenecks, panic)
        - Security threats (suspicious items, weapons, unauthorized access)
        - Medical emergencies (collapsed people, injuries)
        - Fire/safety hazards (smoke, flames, structural damage)
        - Violence or aggressive behavior
        - Equipment failures or dangerous conditions

        Respond ONLY with valid JSON:
        If anomaly found: {"anomaly_detected": true, "category": "crowd_control", "severity": 3, "confidence": 85, "location": "center area", "situation_overview": "Brief description", "severity_assessment": "Why this level", "hazard_analysis": "Risks", "immediate_actions": ["action1", "action2"], "equipment_required": ["item1"], "de_escalation_strategy": "How to resolve", "resolution_method": "Solution steps"}

        If no anomaly: {"anomaly_detected": false}

        Categories: crowd_control, security_threat, medical_emergency, fire_hazard, structural_damage, weather_emergency, vehicle_incident, equipment_failure, unauthorized_access, violence_aggression, stampede_risk, evacuation_needed

        Severity: 1=Low, 2=Medium, 3=High, 4=Critical, 5=Emergency
        """
    
    def encode_frame(self, frame) -> str:
        """Encode frame to base64 for API transmission"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode('utf-8')
    
    def analyze_frame(self, frame) -> Optional[Dict]:
        """Analyze single frame for anomalies using Gemini"""
        try:
            encoded_frame = self.encode_frame(frame)
            
            response = self.model.generate_content([
                self.get_anomaly_detection_prompt(),
                {
                    "mime_type": "image/jpeg",
                    "data": encoded_frame
                }
            ])
            
            if not response or not response.text:
                print(f"   ⚠️  Empty response from Gemini API")
                return {"anomaly_detected": False, "error": "Empty API response"}
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            
            # Handle potential markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Try to parse JSON
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError as json_error:
                print(f"   ⚠️  JSON parsing error: {json_error}")
                print(f"   📝 Raw response: {response_text[:200]}...")
                
                # Try to extract JSON from text if it's embedded
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        return result
                    except:
                        pass
                
                # Return safe default
                return {"anomaly_detected": False, "error": f"JSON parsing failed: {str(json_error)}"}
            
        except Exception as e:
            print(f"   ❌ Error analyzing frame: {e}")
            return {"anomaly_detected": False, "error": str(e)}
    
    def process_anomaly_detection(self, detection_result: Dict, frame) -> Optional[AnomalyReport]:
        """Process detection result and create anomaly report"""
        if not detection_result.get('anomaly_detected', False):
            return None
        
        try:
            category = AnomalyCategory(detection_result['category'].lower())
            severity = SeverityLevel(detection_result['severity'])
            
            report = AnomalyReport(
                timestamp=datetime.now().isoformat(),
                category=category,
                severity=severity,
                situation_overview=detection_result['situation_overview'],
                severity_assessment=detection_result['severity_assessment'],
                hazard_analysis=detection_result['hazard_analysis'],
                immediate_actions=detection_result['immediate_actions'],
                equipment_required=detection_result['equipment_required'],
                de_escalation_strategy=detection_result['de_escalation_strategy'],
                resolution_method=detection_result['resolution_method'],
                confidence_score=detection_result['confidence'] / 100.0,
                location_description=detection_result['location']
            )
            
            return report
            
        except Exception as e:
            print(f"Error processing anomaly detection: {e}")
            return None
    
    def format_report_for_ui(self, report: AnomalyReport) -> Dict:
        """Format anomaly report for UI consumption"""
        return {
            "id": f"anomaly_{int(time.time())}",
            "timestamp": report.timestamp,
            "category": report.category.value.replace('_', ' ').title(),
            "severity": {
                "level": report.severity.value,
                "label": report.severity.name,
                "color": self.get_severity_color(report.severity)
            },
            "confidence": f"{report.confidence_score:.1%}",
            "location": report.location_description,
            "summary": {
                "situation_overview": report.situation_overview,
                "severity_assessment": report.severity_assessment,
                "hazard_analysis": report.hazard_analysis,
                "immediate_actions": report.immediate_actions,
                "equipment_required": report.equipment_required,
                "de_escalation_strategy": report.de_escalation_strategy,
                "resolution_method": report.resolution_method
            },
            "alert_level": self.get_alert_level(report.severity),
            "requires_immediate_action": report.severity.value >= 3
        }
    
    def get_severity_color(self, severity: SeverityLevel) -> str:
        """Get color code for severity level"""
        colors = {
            SeverityLevel.LOW: "#28a745",      # Green
            SeverityLevel.MEDIUM: "#ffc107",   # Yellow
            SeverityLevel.HIGH: "#fd7e14",     # Orange
            SeverityLevel.CRITICAL: "#dc3545", # Red
            SeverityLevel.EMERGENCY: "#6f42c1" # Purple
        }
        return colors.get(severity, "#6c757d")
    
    def get_alert_level(self, severity: SeverityLevel) -> str:
        """Get alert level for UI notifications"""
        if severity.value <= 2:
            return "info"
        elif severity.value == 3:
            return "warning"
        elif severity.value == 4:
            return "danger"
        else:
            return "emergency"
    
    def start_live_monitoring(self, video_source=0):
        """Start live video monitoring"""
        self.is_monitoring = True
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            raise Exception(f"Cannot open video source: {video_source}")
        
        print("🔴 Live anomaly detection started...")
        print("Press 'q' to quit, 's' to save current reports")
        
        try:
            while self.is_monitoring:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                # Display frame
                cv2.imshow('Live Anomaly Detection', frame)
                
                # Analyze frame at intervals
                current_time = time.time()
                if current_time - self.last_analysis_time >= self.analysis_interval:
                    self.last_analysis_time = current_time
                    
                    # Analyze in separate thread to avoid blocking
                    threading.Thread(
                        target=self._analyze_frame_async,
                        args=(frame.copy(),),
                        daemon=True
                    ).start()
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_reports()
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.is_monitoring = False
            print("🟢 Monitoring stopped")
    
    def get_scene_description_prompt(self) -> str:
        """Get prompt for scene description"""
        return """
        Describe what you see in this video frame in 1-2 sentences. Focus on:
        - Number of people visible
        - Main activities happening
        - Environment/location type
        - Overall scene atmosphere
        
        Keep it brief and factual. Example: "A crowded outdoor concert venue with approximately 200 people gathered near the main stage. Most attendees appear calm and engaged with the performance."
        """
    
    def get_scene_description(self, frame) -> str:
        """Get a brief description of what's happening in the scene"""
        try:
            encoded_frame = self.encode_frame(frame)
            
            response = self.model.generate_content([
                self.get_scene_description_prompt(),
                {
                    "mime_type": "image/jpeg",
                    "data": encoded_frame
                }
            ])
            
            return response.text.strip()
            
        except Exception as e:
            return f"Scene description unavailable: {str(e)}"

    def _analyze_frame_async(self, frame):
        """Analyze frame asynchronously"""
        analysis_start_time = time.time()
        current_timestamp = datetime.now().isoformat()
        current_time_str = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n🔍 [{current_time_str}] ANALYZING FRAME...")
        print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
        
        # Get scene description first
        print(f"   🎬 Getting scene description...")
        scene_description = self.get_scene_description(frame)
        print(f"   📝 Scene: {scene_description}")
        
        # Then analyze for anomalies with retry logic
        print(f"   🔍 Analyzing for anomalies...")
        detection_result = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"   📡 API call attempt {attempt + 1}/{max_retries}...")
                detection_result = self.analyze_frame(frame)
                
                if detection_result and not detection_result.get('error'):
                    print(f"   ✅ API call successful!")
                    break
                elif detection_result and detection_result.get('error'):
                    print(f"   ⚠️  API returned error: {detection_result['error']}")
                    if attempt < max_retries - 1:
                        print(f"   🔄 Retrying in 2 seconds...")
                        time.sleep(2)
                else:
                    print(f"   ⚠️  No response from API")
                    if attempt < max_retries - 1:
                        print(f"   🔄 Retrying in 2 seconds...")
                        time.sleep(2)
                        
            except Exception as e:
                print(f"   ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"   🔄 Retrying in 2 seconds...")
                    time.sleep(2)
        
        analysis_duration = time.time() - analysis_start_time
        print(f"   Analysis completed in {analysis_duration:.2f}s")
        
        # Prepare log data
        log_data = {
            "timestamp": current_timestamp,
            "frame_size": f"{frame.shape[1]}x{frame.shape[0]}",
            "analysis_duration": f"{analysis_duration:.2f}",
            "model_used": self.model_name,  # Use actual model name (gemini-2.0-flash)
            "scene_description": scene_description,
            "anomaly_detected": False,
            "total_anomalies": len(self.anomaly_reports),
            "error": None
        }
        
        if detection_result:
            if detection_result.get('error'):
                print(f"   ❌ API Error: {detection_result['error']}")
                log_data["error"] = detection_result['error']
            elif detection_result.get('anomaly_detected'):
                report = self.process_anomaly_detection(detection_result, frame)
                if report:
                    self.anomaly_reports.append(report)
                    ui_report = self.format_report_for_ui(report)
                    
                    # Update log data with anomaly info
                    log_data.update({
                        "anomaly_detected": True,
                        "category": ui_report['category'],
                        "severity_level": ui_report['severity']['level'],
                        "severity_label": ui_report['severity']['label'],
                        "confidence": detection_result.get('confidence', 0),
                        "location": ui_report['location'],
                        "total_anomalies": len(self.anomaly_reports)
                    })
                    
                    # Print detailed alert
                    print(f"\n🚨 ANOMALY DETECTED 🚨")
                    print(f"   Timestamp: {current_time_str}")
                    print(f"   Category: {ui_report['category']}")
                    print(f"   Severity: {ui_report['severity']['label']} ({ui_report['severity']['level']}/5)")
                    print(f"   Confidence: {ui_report['confidence']}")
                    print(f"   Location: {ui_report['location']}")
                    print(f"   Overview: {report.situation_overview}")
                    print(f"   Immediate Actions: {', '.join(report.immediate_actions[:2])}...")
                    print("=" * 60)
                    
                    # Send to UI
                    self._send_to_ui(ui_report)
                else:
                    print(f"   ❌ Failed to process anomaly detection")
                    log_data["error"] = "Failed to process anomaly detection"
            else:
                print(f"   ✅ No anomalies detected - Scene appears normal")
        else:
            print(f"   ❌ Analysis failed - No response from Gemini API after {max_retries} attempts")
            log_data["error"] = f"Analysis failed after {max_retries} attempts"
        
        print(f"   Total anomalies so far: {len(self.anomaly_reports)}")
        print("-" * 40)
        
        # Send log data to UI
        self._send_log_to_ui(log_data)
    
    def _send_to_ui(self, ui_report: Dict):
        """Send report to UI and admin panel"""
        # Save to JSON file for UI consumption
        with open(f"anomaly_alerts.json", "w") as f:
            json.dump({
                "latest_alert": ui_report,
                "all_reports": [self.format_report_for_ui(r) for r in self.anomaly_reports]
            }, f, indent=2)
        
        # Send to admin panel
        try:
            import requests
            requests.post('http://localhost:5001/api/receive-incident', 
                         json=ui_report, timeout=2)
        except:
            pass  # Fail silently if admin panel not available
    
    def _send_log_to_ui(self, log_data: Dict):
        """Send log data to UI via WebSocket"""
        # Save to logs file for API consumption
        try:
            with open("analysis_logs.json", "w") as f:
                json.dump(log_data, f, indent=2)
            
            # Try to send via WebSocket if available
            try:
                import requests
                requests.post('http://localhost:5000/api/send-log', json=log_data, timeout=1)
            except:
                pass  # Fail silently if WebSocket not available
                
        except Exception as e:
            print(f"Failed to save log data: {e}")
    
    def save_reports(self):
        """Save all reports to file"""
        if not self.anomaly_reports:
            print("No reports to save")
            return
        
        filename = f"anomaly_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ui_reports = [self.format_report_for_ui(report) for report in self.anomaly_reports]
        
        with open(filename, 'w') as f:
            json.dump(ui_reports, f, indent=2)
        
        print(f"💾 Saved {len(ui_reports)} reports to {filename}")
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        if not self.anomaly_reports:
            return {"total_anomalies": 0}
        
        category_counts = {}
        severity_counts = {}
        
        for report in self.anomaly_reports:
            cat = report.category.value
            sev = report.severity.name
            
            category_counts[cat] = category_counts.get(cat, 0) + 1
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return {
            "total_anomalies": len(self.anomaly_reports),
            "categories": category_counts,
            "severity_distribution": severity_counts,
            "high_priority_count": len([r for r in self.anomaly_reports if r.severity.value >= 3]),
            "latest_anomaly": self.anomaly_reports[-1].timestamp if self.anomaly_reports else None
        }

