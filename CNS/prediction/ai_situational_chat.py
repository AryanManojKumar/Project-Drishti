"""
AI-Powered Situational Chat System
Bhai, yeh system natural language queries handle karta hai aur Gemini AI se responses deta hai
"""

import streamlit as st
import requests
import json
import base64
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import from live_crowd_predictor for getting central status
try:
    from live_crowd_predictor import get_central_status
except ImportError:
    def get_central_status():
        return {'camera_details': {}, 'bottleneck_predictions': []}

class AISituationalChat:
    """
    AI-Powered Chat System for Situational Awareness
    Natural language queries ko handle karta hai aur Gemini se responses deta hai
    """
    
    def __init__(self):
        self.gemini_key = "AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
        
        # Rate limiting to avoid 429 errors
        self.last_api_call = {}
        self.rate_limit_interval = 60  # 1 minute between calls
        self.cached_responses = {}
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        
        # Function calling support
        self.available_functions = {
            'get_camera_crowd_count': self.get_camera_crowd_count,
            'analyze_security_zones': self.analyze_security_zones,
            'predict_bottlenecks': self.predict_bottlenecks,
            'get_high_risk_areas': self.get_high_risk_areas,
            'get_ip_camera_details': self.get_ip_camera_details
        }

    def get_ip_camera_config(self) -> Dict:
        """IP camera setup se camera names aur config leta hai"""
        try:
            # Check if IP camera config is available from crowd prediction system
            if 'ip_camera_config' in st.session_state:
                ip_config = st.session_state['ip_camera_config']
                camera_feeds = {}
                
                for cam_id, config in ip_config.items():
                    camera_feeds[cam_id] = {
                        'location': config.get('name', config.get('location', cam_id)),
                        'coordinates': {'lat': config.get('lat', 13.0358), 'lng': config.get('lng', 77.6431)},
                        'status': 'active',
                        'url': config.get('url', ''),
                        'last_analysis': None
                    }
                
                return camera_feeds
            else:
                # Default camera config if IP setup not available
                return {
                    'cam_entrance_main': {
                        'location': 'Main Entrance',
                        'coordinates': {'lat': 13.0360, 'lng': 77.6430},
                        'status': 'active',
                        'last_analysis': None
                    },
                    'cam_hall1_entry': {
                        'location': 'Hall 1 Entry', 
                        'coordinates': {'lat': 13.0358, 'lng': 77.6432},
                        'status': 'active',
                        'last_analysis': None
                    },
                    'cam_food_court': {
                        'location': 'Food Court',
                        'coordinates': {'lat': 13.0354, 'lng': 77.6428},
                        'status': 'active', 
                        'last_analysis': None
                    },
                    'cam_corridor_main': {
                        'location': 'Main Corridor',
                        'coordinates': {'lat': 13.0357, 'lng': 77.6431},
                        'status': 'active',
                        'last_analysis': None
                    }
                }
        except Exception as e:
            st.error(f"Error getting IP camera config: {e}")
            return {}

    def setup_ui(self):
        """Setup Streamlit UI for chat interface"""
        st.set_page_config(
            page_title="🤖 AI Situational Chat",
            page_icon="🤖",
            layout="wide"
        )
        
        # Custom CSS for chat interface with readable white text
        st.markdown("""
        <style>
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            color: white !important;
        }
        .user-message {
            background: #1976d2;
            border-left: 4px solid #0d47a1;
            color: white !important;
        }
        .ai-message {
            background: #7b1fa2;
            border-left: 4px solid #4a148c;
            color: white !important;
        }
        .ai-message h1, .ai-message h2, .ai-message h3, .ai-message h4, .ai-message h5, .ai-message h6 {
            color: #ffeb3b !important;
            font-weight: bold;
        }
        .ai-message p, .ai-message li, .ai-message span, .ai-message div {
            color: white !important;
        }
        .ai-message strong {
            color: #ffeb3b !important;
        }
        .section-header {
            background: #fff3e0;
            padding: 0.5rem;
            border-radius: 5px;
            border-left: 3px solid #ff9800;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def get_current_situation_data(self) -> Dict:
        """Get current input sources and generate fresh situational analysis"""
        try:
            import numpy as np
            
            # Initialize situation data structure
            situation_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'input_sources': {},
                'live_analysis': {},
                'overall_status': 'normal',
                'venue_summary': {},
                'alerts': [],
                'bottlenecks': []
            }
            
            # Get active input sources from main UI
            active_sources = self.get_active_input_sources()
            
            if not active_sources:
                situation_data['input_sources'] = {'status': 'No active sources detected'}
                return situation_data
            
            # Process each active input source
            for source_id, source_info in active_sources.items():
                # Generate fresh situational analysis for each source
                fresh_analysis = self.generate_fresh_situational_analysis(source_info)
                
                # Only get 15-20 min predictions from existing system (reuse this part)
                predictions_15_20min = self.get_crowd_flow_predictions(source_info)
                
                # Combine fresh analysis with predictions
                situation_data['input_sources'][source_id] = {
                    'source_type': source_info['type'],
                    'source_name': source_info['name'],
                    'location': source_info['location'],
                    'coordinates': source_info.get('coordinates', {}),
                    'fresh_analysis': fresh_analysis,
                    'predictions_15_20min': predictions_15_20min,
                    'last_updated': datetime.now().strftime('%H:%M:%S')
                }
            
            # Generate overall venue summary
            situation_data['venue_summary'] = self.generate_venue_summary(situation_data['input_sources'])
            
            return situation_data
            
        except Exception as e:
            st.error(f"Error getting situation data: {e}")
            return {'error': str(e)}

    def get_active_input_sources(self) -> Dict:
        """Detect active input sources from main UI system"""
        active_sources = {}
        
        try:
            # Check for active webcam
            if st.session_state.get('webcam_active', False):
                active_sources['webcam_main'] = {
                    'type': 'webcam',
                    'name': 'Main Webcam',
                    'location': 'Webcam Feed',
                    'coordinates': {'lat': 13.0358, 'lng': 77.6431},
                    'status': 'active'
                }
            
            # Check for active IP cameras
            if st.session_state.get('ip_camera_active'):
                active_camera_id = st.session_state['ip_camera_active']
                if 'ip_camera_config' in st.session_state:
                    ip_config = st.session_state['ip_camera_config']
                    if active_camera_id in ip_config:
                        camera_config = ip_config[active_camera_id]
                        active_sources[active_camera_id] = {
                            'type': 'ip_camera',
                            'name': camera_config['name'],
                            'location': camera_config['location'],
                            'coordinates': {'lat': camera_config['lat'], 'lng': camera_config['lng']},
                            'url': camera_config['url'],
                            'status': 'active'
                        }
            
            # Check for uploaded video analysis
            if 'uploaded_video_analysis' in st.session_state:
                analysis = st.session_state['uploaded_video_analysis']
                active_sources['uploaded_video'] = {
                    'type': 'video_file',
                    'name': 'Uploaded Video',
                    'location': analysis.get('venue_name', 'Video Analysis'),
                    'coordinates': {'lat': analysis.get('venue_lat', 13.0358), 'lng': analysis.get('venue_lng', 77.6431)},
                    'status': 'analyzed'
                }
            
            # Check for Central Nervous System cameras
            if st.session_state.get('cns_active', False):
                cns_status = get_central_status()
                camera_details = cns_status.get('camera_details', {})
                for cam_id, data in camera_details.items():
                    if data:
                        active_sources[f'cns_{cam_id}'] = {
                            'type': 'cns_camera',
                            'name': data.get('camera_location', {}).get('location', cam_id),
                            'location': data.get('camera_location', {}).get('location', cam_id),
                            'coordinates': data.get('camera_location', {}),
                            'status': 'monitoring'
                        }
            
            return active_sources
            
        except Exception as e:
            st.error(f"Error detecting input sources: {e}")
            return {}

    def generate_fresh_situational_analysis(self, source_info: Dict) -> Dict:
        """Generate fresh situational analysis using Gemini AI for each input source"""
        try:
            source_type = source_info['type']
            source_name = source_info['name']
            location = source_info['location']
            
            # Capture fresh frame/data based on source type
            if source_type == 'webcam':
                frame_data = self.capture_webcam_for_analysis()
            elif source_type == 'ip_camera':
                frame_data = self.capture_ip_camera_for_analysis(source_info)
            elif source_type == 'video_file':
                frame_data = self.get_video_analysis_data()
            elif source_type == 'cns_camera':
                frame_data = self.get_cns_camera_data(source_info)
            else:
                return {'error': 'Unknown source type'}
            
            if not frame_data:
                return {'error': 'Could not capture data from source'}
            
            # Generate fresh situational analysis with Gemini AI
            situational_prompt = f"""
            You are analyzing live input from {source_name} at {location} for situational awareness.
            
            Generate a comprehensive situational summary including:
            
            1. IMMEDIATE SITUATION:
            - Current crowd state and behavior
            - Density and movement patterns
            - Any immediate concerns or observations
            
            2. SAFETY ASSESSMENT:
            - Current safety level (1-10)
            - Immediate risks or hazards
            - Safety recommendations
            
            3. CROWD DYNAMICS:
            - Movement patterns and flow
            - Congestion points
            - Behavioral observations
            
            4. OPERATIONAL STATUS:
            - Current capacity utilization
            - Flow efficiency
            - Any operational issues
            
            5. CONTEXTUAL INSIGHTS:
            - Location-specific observations
            - Environmental factors
            - Crowd composition notes
            
            Respond in JSON format:
            {{
                "immediate_situation": {{
                    "people_count": <number>,
                    "density_level": "<low/medium/high/critical>",
                    "movement_status": "<stationary/slow/normal/fast>",
                    "crowd_behavior": "<calm/active/agitated/mixed>",
                    "key_observations": ["<observation1>", "<observation2>"]
                }},
                "safety_assessment": {{
                    "safety_level": <1-10>,
                    "immediate_risks": ["<risk1>", "<risk2>"],
                    "safety_recommendations": ["<rec1>", "<rec2>"],
                    "emergency_readiness": "<low/medium/high>"
                }},
                "crowd_dynamics": {{
                    "primary_flow_direction": "<direction>",
                    "congestion_points": ["<point1>", "<point2>"],
                    "flow_efficiency": <1-10>,
                    "behavioral_patterns": ["<pattern1>", "<pattern2>"]
                }},
                "operational_status": {{
                    "capacity_utilization": <percentage>,
                    "operational_efficiency": <1-10>,
                    "resource_needs": ["<need1>", "<need2>"],
                    "staff_deployment": "<adequate/insufficient/excessive>"
                }},
                "contextual_insights": {{
                    "location_factors": ["<factor1>", "<factor2>"],
                    "environmental_conditions": "<description>",
                    "crowd_composition": "<description>",
                    "notable_events": ["<event1>", "<event2>"]
                }},
                "analysis_confidence": <0.0-1.0>,
                "analysis_timestamp": "{datetime.now().strftime('%H:%M:%S')}"
            }}
            
            Base this analysis on the current visual data and provide actionable insights.
            """
            
            # Send to Gemini AI
            if frame_data.get('frame_base64'):
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": situational_prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": frame_data['frame_base64']
                                }
                            }
                        ]
                    }]
                }
            else:
                # Text-only analysis if no frame available
                payload = {
                    "contents": [{
                        "parts": [{"text": situational_prompt + f"\n\nAnalyze based on available data: {frame_data}"}]
                    }]
                }
            
            response = requests.post(self.gemini_url, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                try:
                    # Parse JSON response
                    if '```json' in ai_response:
                        json_text = ai_response.split('```json')[1].split('```')[0].strip()
                    elif '{' in ai_response:
                        json_text = ai_response[ai_response.find('{'):ai_response.rfind('}')+1]
                    else:
                        json_text = ai_response
                    
                    analysis = json.loads(json_text)
                    analysis['source_name'] = source_name
                    analysis['location'] = location
                    return analysis
                    
                except json.JSONDecodeError:
                    return self.create_fallback_situational_analysis(source_info)
            else:
                return self.create_fallback_situational_analysis(source_info)
                
        except Exception as e:
            st.error(f"Error generating situational analysis: {e}")
            return self.create_fallback_situational_analysis(source_info)

    def capture_webcam_for_analysis(self) -> Dict:
        """Capture fresh frame from webcam for situational analysis"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'frame_base64': frame_base64,
                'source': 'webcam',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        except:
            return None

    def capture_ip_camera_for_analysis(self, source_info: Dict) -> Dict:
        """Capture fresh frame from IP camera for situational analysis"""
        try:
            camera_url = source_info.get('url')
            if not camera_url:
                return None
            
            cap = cv2.VideoCapture(camera_url)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'frame_base64': frame_base64,
                'source': 'ip_camera',
                'camera_url': camera_url,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        except:
            return None

    def get_video_analysis_data(self) -> Dict:
        """Get data from uploaded video analysis"""
        try:
            if 'uploaded_video_analysis' in st.session_state:
                analysis = st.session_state['uploaded_video_analysis']
                return {
                    'source': 'video_file',
                    'analysis_data': analysis,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            return None
        except:
            return None

    def get_cns_camera_data(self, source_info: Dict) -> Dict:
        """Get data from CNS camera"""
        try:
            from live_crowd_predictor import get_central_status
            status = get_central_status()
            camera_details = status.get('camera_details', {})
            
            # Extract camera ID from source_info name
            cam_id = source_info['name'].replace('cns_', '')
            if cam_id in camera_details:
                return {
                    'source': 'cns_camera',
                    'camera_data': camera_details[cam_id],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            return None
        except:
            return None

    def get_crowd_flow_predictions(self, source_info: Dict) -> Dict:
        """Get 15-20 minute crowd flow predictions (reuse from existing system)"""
        try:
            source_type = source_info['type']
            
            # Get predictions based on source type
            if source_type == 'webcam' and 'latest_webcam_analysis' in st.session_state:
                analysis = st.session_state['latest_webcam_analysis']
                return analysis.get('predictions', {})
            
            elif source_type == 'ip_camera':
                # Get IP camera analysis
                camera_id = None
                for key in st.session_state.keys():
                    if key.startswith('ip_analysis_') and source_info['name'] in key:
                        analysis = st.session_state[key]
                        return analysis.get('predictions', {})
            
            elif source_type == 'video_file' and 'uploaded_video_analysis' in st.session_state:
                analysis = st.session_state['uploaded_video_analysis']
                return analysis.get('predictions', {})
            
            elif source_type == 'cns_camera':
                # Get CNS predictions
                from live_crowd_predictor import get_central_status
                status = get_central_status()
                predictions = status.get('bottleneck_predictions', [])
                if predictions:
                    return predictions[0]  # Return first prediction
            
            # Fallback: generate basic predictions
            return {
                'predicted_people_15min': 0,
                'growth_percentage': 0,
                'bottleneck_probability': 0,
                'bottleneck_eta_minutes': None
            }
            
        except Exception as e:
            return {'error': f'Prediction error: {e}'}

    def generate_venue_summary(self, input_sources: Dict) -> Dict:
        """Generate overall venue summary from all input sources"""
        try:
            total_people = 0
            total_sources = len(input_sources)
            high_risk_sources = 0
            active_alerts = 0
            
            for source_id, source_data in input_sources.items():
                if source_data.get('fresh_analysis'):
                    analysis = source_data['fresh_analysis']
                    
                    # Extract people count
                    immediate = analysis.get('immediate_situation', {})
                    people_count = immediate.get('people_count', 0)
                    total_people += people_count
                    
                    # Check risk levels
                    safety = analysis.get('safety_assessment', {})
                    safety_level = safety.get('safety_level', 10)
                    if safety_level <= 5:
                        high_risk_sources += 1
                    
                    # Check for alerts
                    risks = safety.get('immediate_risks', [])
                    if risks and risks != ['No immediate risks detected']:
                        active_alerts += 1
            
            return {
                'total_active_sources': total_sources,
                'total_people_detected': total_people,
                'high_risk_sources': high_risk_sources,
                'active_alerts': active_alerts,
                'overall_safety_status': 'critical' if high_risk_sources > 0 else 'warning' if active_alerts > 0 else 'normal',
                'venue_capacity_estimate': total_people,
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            return {'error': f'Summary generation error: {e}'}

    def create_fallback_situational_analysis(self, source_info: Dict) -> Dict:
        """Create fallback analysis when AI analysis fails"""
        return {
            "immediate_situation": {
                "people_count": 0,
                "density_level": "unknown",
                "movement_status": "unknown",
                "crowd_behavior": "unknown",
                "key_observations": ["Analysis unavailable"]
            },
            "safety_assessment": {
                "safety_level": 5,
                "immediate_risks": ["Analysis system unavailable"],
                "safety_recommendations": ["Manual monitoring recommended"],
                "emergency_readiness": "unknown"
            },
            "crowd_dynamics": {
                "primary_flow_direction": "unknown",
                "congestion_points": ["Unable to detect"],
                "flow_efficiency": 5,
                "behavioral_patterns": ["Analysis unavailable"]
            },
            "operational_status": {
                "capacity_utilization": 0,
                "operational_efficiency": 5,
                "resource_needs": ["System diagnostics"],
                "staff_deployment": "unknown"
            },
            "contextual_insights": {
                "location_factors": ["Analysis system offline"],
                "environmental_conditions": "Unknown",
                "crowd_composition": "Unknown",
                "notable_events": ["System fallback mode"]
            },
            "analysis_confidence": 0.1,
            "analysis_timestamp": datetime.now().strftime('%H:%M:%S'),
            "source_name": source_info.get('name', 'Unknown'),
            "location": source_info.get('location', 'Unknown')
        }

    def predict_peak_time(self, current_people: int, predicted_people: int) -> str:
        """Peak time prediction karta hai"""
        if predicted_people > current_people:
            growth_rate = (predicted_people - current_people) / current_people
            if growth_rate > 0.3:
                return "Next 10-15 minutes"
            elif growth_rate > 0.1:
                return "Next 15-20 minutes"
            else:
                return "Gradual increase expected"
        else:
            return "Peak may have passed"

    def get_gemini_predictions(self, location: str, people_count: int, density_score: int, velocity: float, camera_data: Dict) -> Dict:
        """Gemini AI se predictions get karta hai - no hardcoded values"""
        try:
            # Create prompt for Gemini to predict crowd behavior
            prediction_prompt = f"""
            You are an AI crowd analysis expert. Analyze the current crowd situation and provide numerical predictions.
            
            CURRENT SITUATION AT {location}:
            - Current People Count: {people_count}
            - Current Density Score: {density_score}/10
            - Current Velocity: {velocity:.1f} m/s
            - Flow Direction: {camera_data.get('flow_direction', 'unknown')}
            - Flow Efficiency: {camera_data.get('flow_efficiency', 5)}/10
            - Alert Level: {camera_data.get('alert_level', 'normal')}
            - Safety Risks: {', '.join(camera_data.get('safety_risks', []))}
            - Bottleneck Indicators: {', '.join(camera_data.get('bottleneck_indicators', []))}
            
            PREDICT THE FOLLOWING FOR NEXT 15-20 MINUTES:
            1. Predicted people count (based on current trends)
            2. Predicted density score (1-10)
            3. Crowd growth (positive/negative number)
            4. Growth percentage
            5. Bottleneck probability (0-100%)
            6. Bottleneck ETA in minutes (if probability > 50%)
            7. Predicted flow efficiency (1-10)
            8. Peak time prediction
            9. Evacuation time estimate
            10. Capacity utilization percentage
            11. Risk score (0-100)
            
            RESPOND ONLY IN THIS JSON FORMAT (no other text):
            {{
                "predicted_people_15min": <number>,
                "predicted_density_15min": <number 1-10>,
                "crowd_growth": <number>,
                "growth_percentage": <number>,
                "bottleneck_probability": <number 0-100>,
                "bottleneck_eta_minutes": <number or null>,
                "predicted_flow_efficiency": <number 1-10>,
                "peak_time_prediction": "<text>",
                "evacuation_time_estimate": "<text>",
                "capacity_utilization": <number 0-100>,
                "risk_score": <number 0-100>,
                "congestion_level": "<HIGH/MEDIUM/LOW>",
                "movement_status": "<BLOCKED/SLOW/NORMAL>"
            }}
            
            Base your predictions on:
            - Current crowd density and flow patterns
            - Velocity and movement efficiency
            - Safety risks and bottleneck indicators
            - Typical crowd behavior patterns
            - Location-specific factors
            
            Be realistic and data-driven in your predictions.
            """
            
            # Send to Gemini API
            payload = {
                "contents": [{
                    "parts": [{"text": prediction_prompt}]
                }]
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON response
                try:
                    predictions = json.loads(ai_response)
                    return predictions
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract numbers from text
                    return self.extract_predictions_from_text(ai_response, people_count, density_score)
            else:
                # Fallback: return current values if API fails
                return {
                    'predicted_people_15min': people_count,
                    'predicted_density_15min': density_score,
                    'crowd_growth': 0,
                    'growth_percentage': 0,
                    'bottleneck_probability': 0,
                    'bottleneck_eta_minutes': None,
                    'predicted_flow_efficiency': camera_data.get('flow_efficiency', 5)
                }
                
        except Exception as e:
            st.error(f"Error getting Gemini predictions: {e}")
            # Return current values as fallback
            return {
                'predicted_people_15min': people_count,
                'predicted_density_15min': density_score,
                'crowd_growth': 0,
                'growth_percentage': 0,
                'bottleneck_probability': 0,
                'bottleneck_eta_minutes': None,
                'predicted_flow_efficiency': camera_data.get('flow_efficiency', 5)
            }

    def extract_predictions_from_text(self, text: str, current_people: int, current_density: int) -> Dict:
        """Text se predictions extract karta hai agar JSON parsing fail ho jaye"""
        try:
            import re
            
            predictions = {
                'predicted_people_15min': current_people,
                'predicted_density_15min': current_density,
                'crowd_growth': 0,
                'growth_percentage': 0,
                'bottleneck_probability': 0,
                'bottleneck_eta_minutes': None,
                'predicted_flow_efficiency': 5
            }
            
            # Extract numbers using regex
            people_match = re.search(r'predicted_people_15min["\s]*:[\s]*([0-9]+)', text)
            if people_match:
                predictions['predicted_people_15min'] = int(people_match.group(1))
            
            density_match = re.search(r'predicted_density_15min["\s]*:[\s]*([0-9]+)', text)
            if density_match:
                predictions['predicted_density_15min'] = int(density_match.group(1))
            
            bottleneck_match = re.search(r'bottleneck_probability["\s]*:[\s]*([0-9]+)', text)
            if bottleneck_match:
                predictions['bottleneck_probability'] = int(bottleneck_match.group(1))
            
            return predictions
            
        except Exception:
            return {
                'predicted_people_15min': current_people,
                'predicted_density_15min': current_density,
                'crowd_growth': 0,
                'growth_percentage': 0,
                'bottleneck_probability': 0,
                'bottleneck_eta_minutes': None,
                'predicted_flow_efficiency': 5
            }

    def calculate_evacuation_time(self, people_count: int, velocity: float) -> str:
        """Evacuation time estimate karta hai"""
        if velocity > 0:
            # Simple calculation: people / (velocity * 60) assuming 1 person per second at 1 m/s
            evacuation_minutes = max(people_count / (velocity * 30), 2)  # Minimum 2 minutes
            return f"{evacuation_minutes:.0f} minutes"
        else:
            return "Unable to calculate (blocked flow)"

    def query_gemini_ai(self, user_query: str, situation_data: Dict) -> str:
        """Gemini AI se natural language query process karta hai with comprehensive numerical data"""
        try:
            # Create comprehensive prompt for Gemini with detailed numerical data
            venue_summary = situation_data.get('venue_summary', {})
            
            prompt = f"""
            You are an AI assistant for a crowd management and security system. A commander/volunteer is asking you a question about the current situation.
            
            VENUE-WIDE SUMMARY:
            - Timestamp: {situation_data.get('timestamp', 'Unknown')}
            - Overall Status: {situation_data.get('overall_status', 'normal').upper()}
            - Total Current People: {venue_summary.get('total_current_people', 0)}
            - Total Predicted People (15-20 min): {venue_summary.get('total_predicted_people_15min', 0)}
            - Venue Growth Expected: {venue_summary.get('venue_growth', 0)} people ({venue_summary.get('venue_growth_percentage', 0):.1f}%)
            - Average Density: {venue_summary.get('average_density', 0):.1f}/10
            - Average Velocity: {venue_summary.get('average_velocity', 0):.1f} m/s
            - High Risk Locations: {venue_summary.get('high_risk_locations', 0)}
            - Overcrowded Locations: {venue_summary.get('overcrowded_locations', 0)}
            - Blocked Flow Locations: {venue_summary.get('blocked_locations', 0)}
            - Overall Capacity Utilization: {venue_summary.get('overall_capacity_utilization', 0):.1f}%
            
            DETAILED CAMERA-WISE ANALYSIS:
            """
            
            # Add comprehensive camera details with predictions
            for camera_id, data in situation_data.get('cameras', {}).items():
                prompt += f"""
            
            📹 {data['location']} (Camera ID: {camera_id}):
            
            CURRENT STATUS:
            - People Count: {data['people_count']}
            - Density Score: {data['density_score']}/10
            - Alert Level: {data['alert_level'].upper()}
            - Flow Direction: {data['flow_direction']}
            - Velocity: {data['velocity']:.1f} m/s
            - Flow Efficiency: {data['flow_efficiency']}/10
            - Congestion Level: {data.get('congestion_level', 'UNKNOWN')}
            - Movement Status: {data.get('movement_status', 'UNKNOWN')}
            - Capacity Utilization: {data.get('capacity_utilization', 0):.1f}%
            - Risk Score: {data.get('risk_score', 0):.1f}/100
            
            15-20 MINUTE PREDICTIONS:
            - Predicted People: {data.get('predicted_people_15min', 0)} (Growth: {data.get('crowd_growth', 0):+d} people)
            - Growth Percentage: {data.get('growth_percentage', 0):+.1f}%
            - Predicted Density: {data.get('predicted_density_15min', 0)}/10
            - Bottleneck Probability: {data.get('bottleneck_probability', 0)}%
            - Bottleneck ETA: {data.get('bottleneck_eta_minutes', 'N/A')} minutes
            - Predicted Flow Efficiency: {data.get('predicted_flow_efficiency', 0)}/10
            - Peak Time Prediction: {data.get('peak_time_prediction', 'Unknown')}
            - Evacuation Time Estimate: {data.get('evacuation_time_estimate', 'Unknown')}
            
            SAFETY & RISKS:
            - Safety Risks: {', '.join(data['safety_risks']) if data['safety_risks'] else 'None identified'}
            - Bottleneck Indicators: {', '.join(data['bottleneck_indicators']) if data['bottleneck_indicators'] else 'None detected'}
            - Analysis Confidence: {data.get('analysis_confidence', 0):.0%}
            - Last Updated: {data.get('last_updated', 'Unknown')}
            """
            
            # Add detailed alerts with numerical data
            if situation_data.get('alerts'):
                prompt += f"""
            
            🚨 ACTIVE ALERTS WITH NUMERICAL DATA:
            """
                for alert in situation_data['alerts']:
                    prompt += f"""
            - Location: {alert['location']}
            - Alert Level: {alert['level'].upper()}
            - Current People: {alert['people_count']}
            - Current Density: {alert['density']}/10
            - Current Velocity: {alert['velocity']:.1f} m/s
            - Predicted People (15-20 min): {alert['predicted_people']}
            - Growth Rate: {alert['growth_rate']:+.1f}%
            - Bottleneck Risk: {alert['bottleneck_risk']}%
            - Capacity Exceeded: {'YES' if alert['capacity_exceeded'] else 'NO'}
            - Immediate Action Required: {'YES' if alert['immediate_action_required'] else 'NO'}
            """
            
            # Add detailed bottleneck predictions
            if situation_data.get('bottlenecks'):
                prompt += f"""
            
            ⚠️ BOTTLENECK PREDICTIONS WITH NUMERICAL DATA:
            """
                for bottleneck in situation_data['bottlenecks']:
                    prompt += f"""
            - Location: {bottleneck['location']}
            - Risk Level: {bottleneck['risk_level'].upper()}
            - Bottleneck Probability: {bottleneck['probability']}%
            - ETA: {bottleneck['eta_minutes']} minutes
            - Current People: {bottleneck['current_people']}
            - Predicted People: {bottleneck['predicted_people']}
            - Flow Efficiency: {bottleneck['flow_efficiency']}/10
            - Recommended Capacity: {bottleneck['recommended_capacity']} people
            - Indicators: {', '.join(bottleneck['indicators'])}
            """
            
            prompt += f"""
            
            USER QUERY: "{user_query}"
            
            INSTRUCTIONS:
            1. Answer the user's query using the comprehensive numerical data provided above
            2. Include specific numbers, percentages, and predictions in your response
            3. Structure your response with clear sections using markdown headers
            4. Keep each camera location separate - DO NOT mix camera feed outputs
            5. Highlight critical numerical thresholds and alert conditions
            6. Provide actionable insights with specific numerical targets
            7. Use the prediction data to forecast future conditions
            8. Include growth rates, bottleneck probabilities, and time estimates
            9. Reference capacity utilization and risk scores when relevant
            10. Use emojis for better readability but keep professional tone
            
            RESPONSE STRUCTURE:
            ## 📊 Current Numerical Status
            ## 🔮 15-20 Minute Predictions
            ## 📍 Location-Specific Analysis (separate each camera)
            ## 🚨 Critical Alerts & Numerical Thresholds
            ## ⚠️ Bottleneck Predictions & Probabilities
            ## 💡 Numerical Recommendations & Action Items
            
            IMPORTANT: Always include specific numbers, percentages, people counts, time estimates, and probability scores in your response. Make it data-driven and actionable.
            """
            
            # Send to Gemini API
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                return ai_response
            else:
                return f"❌ Error: Unable to get AI response (Status: {response.status_code})"
                
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

    def display_chat_interface(self):
        """Chat interface display karta hai"""
        st.title("🤖 AI Situational Chat System")
        st.markdown("**Natural Language Queries for Crowd Management & Security**")
        
        # System status
        situation_data = self.get_current_situation_data()
        
        col_status1, col_status2, col_status3, col_status4 = st.columns(4)
        
        with col_status1:
            st.metric("🏢 Total People", situation_data.get('total_people', 0))
        
        with col_status2:
            status = situation_data.get('overall_status', 'normal')
            status_color = "🔴" if status == 'critical' else "🟡" if status == 'warning' else "🟢"
            st.metric("📊 Overall Status", f"{status_color} {status.upper()}")
        
        with col_status3:
            st.metric("📹 Active Cameras", len(situation_data.get('cameras', {})))
        
        with col_status4:
            st.metric("🚨 Active Alerts", len(situation_data.get('alerts', [])))
        
        st.markdown("---")
        
        # Chat history display
        st.subheader("💬 Chat History")
        
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state['chat_history']:
                if message['type'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong> {message['content']}
                        <br><small>🕐 {message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>🤖 AI Assistant:</strong><br>
                        {message['content']}
                        <br><small>🕐 {message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        st.subheader("💭 Ask AI Assistant")
        
        # Example queries
        st.markdown("**💡 Example Queries:**")
        example_queries = [
            "Summarize security concerns in all zones",
            "What's the current status of Main Entrance?",
            "Are there any bottlenecks forming?",
            "Which locations need immediate attention?",
            "Give me a complete situational overview",
            "What are the crowd flow patterns right now?"
        ]
        
        cols = st.columns(3)
        for i, query in enumerate(example_queries):
            with cols[i % 3]:
                if st.button(f"💬 {query}", key=f"example_{i}"):
                    self.process_user_query(query, situation_data)
                    st.rerun()
        
        # Manual query input
        user_query = st.text_input(
            "🔍 Enter your query:",
            placeholder="e.g., Summarize security concerns in the West Zone",
            key="user_query_input"
        )
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            if st.button("📤 Send Query", type="primary") and user_query:
                self.process_user_query(user_query, situation_data)
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear Chat"):
                st.session_state['chat_history'] = []
                st.rerun()

    def process_user_query(self, query: str, situation_data: Dict):
        """User query process karta hai aur response generate karta hai"""
        try:
            # Add user message to chat history
            st.session_state['chat_history'].append({
                'type': 'user',
                'content': query,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Get AI response
            with st.spinner("🤖 AI is analyzing the situation..."):
                ai_response = self.query_gemini_ai(query, situation_data)
            
            # Add AI response to chat history
            st.session_state['chat_history'].append({
                'type': 'ai',
                'content': ai_response,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
        except Exception as e:
            st.error(f"Error processing query: {e}")

    def get_camera_crowd_count(self, camera_id: str = None) -> Dict:
        """Get current people count from specific camera or all cameras"""
        try:
            ip_camera_config = st.session_state.get('ip_camera_config', {})
            
            if camera_id and camera_id in ip_camera_config:
                # Get specific camera data
                camera_config = ip_camera_config[camera_id]
                
                # For demo purposes, simulate crowd count analysis
                import random
                people_count = random.randint(5, 35)
                density_level = "LOW" if people_count < 15 else "MEDIUM" if people_count < 25 else "HIGH"
                
                return {
                    'camera_id': camera_id,
                    'location': camera_config.get('location', 'Unknown'),
                    'people_count': people_count,
                    'density_level': density_level,
                    'status': 'active',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Get all cameras data
                all_cameras_data = {}
                for cam_id, cam_config in ip_camera_config.items():
                    import random
                    people_count = random.randint(5, 35)
                    density_level = "LOW" if people_count < 15 else "MEDIUM" if people_count < 25 else "HIGH"
                    
                    all_cameras_data[cam_id] = {
                        'location': cam_config.get('location', 'Unknown'),
                        'people_count': people_count,
                        'density_level': density_level,
                        'status': 'active'
                    }
                
                return {
                    'total_cameras': len(ip_camera_config),
                    'cameras_data': all_cameras_data,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def analyze_security_zones(self) -> Dict:
        """Analyze security status across all zones"""
        try:
            ip_camera_config = st.session_state.get('ip_camera_config', {})
            
            zones_analysis = {}
            total_risk_score = 0
            
            for cam_id, cam_config in ip_camera_config.items():
                location = cam_config.get('location', 'Unknown')
                
                # Simulate security analysis
                import random
                people_count = random.randint(5, 35)
                risk_factors = []
                
                # Calculate risk score
                risk_score = 0
                if people_count > 25:
                    risk_score += 30
                    risk_factors.append("High crowd density")
                elif people_count > 15:
                    risk_score += 15
                    risk_factors.append("Moderate crowd density")
                
                # Add location-based risk factors
                if 'entrance' in location.lower():
                    risk_score += 20
                    risk_factors.append("High traffic area")
                elif 'food' in location.lower() or 'court' in location.lower():
                    risk_score += 15
                    risk_factors.append("Congestion-prone area")
                
                risk_level = "HIGH" if risk_score > 40 else "MEDIUM" if risk_score > 20 else "LOW"
                
                zones_analysis[cam_id] = {
                    'location': location,
                    'people_count': people_count,
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'risk_factors': risk_factors,
                    'recommendations': self.get_zone_recommendations(risk_level, location)
                }
                
                total_risk_score += risk_score
            
            overall_risk = "HIGH" if total_risk_score > 120 else "MEDIUM" if total_risk_score > 60 else "LOW"
            
            return {
                'overall_risk_level': overall_risk,
                'total_risk_score': total_risk_score,
                'zones_count': len(zones_analysis),
                'zones_analysis': zones_analysis,
                'timestamp': datetime.now().isoformat(),
                'summary': f"Security analysis completed for {len(zones_analysis)} zones. Overall risk: {overall_risk}"
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def predict_bottlenecks(self, time_horizon_minutes: int = 20) -> Dict:
        """Predict potential bottleneck areas"""
        try:
            ip_camera_config = st.session_state.get('ip_camera_config', {})
            
            bottleneck_predictions = []
            
            for cam_id, cam_config in ip_camera_config.items():
                location = cam_config.get('location', 'Unknown')
                
                # Simulate bottleneck prediction
                import random
                current_count = random.randint(5, 35)
                
                # Calculate bottleneck probability based on location type and current count
                bottleneck_probability = 0
                
                if 'entrance' in location.lower():
                    bottleneck_probability = min(70 + (current_count * 2), 95)
                elif 'food' in location.lower() or 'court' in location.lower():
                    bottleneck_probability = min(50 + (current_count * 1.5), 90)
                elif 'corridor' in location.lower():
                    bottleneck_probability = min(60 + (current_count * 1.8), 93)
                else:
                    bottleneck_probability = min(30 + current_count, 80)
                
                if bottleneck_probability > 50:
                    eta_minutes = random.randint(5, time_horizon_minutes)
                    predicted_count = current_count + random.randint(10, 25)
                    
                    bottleneck_predictions.append({
                        'camera_id': cam_id,
                        'location': location,
                        'current_count': current_count,
                        'predicted_count': predicted_count,
                        'bottleneck_probability': round(bottleneck_probability, 1),
                        'eta_minutes': eta_minutes,
                        'severity': 'HIGH' if bottleneck_probability > 75 else 'MEDIUM',
                        'recommended_actions': self.get_bottleneck_actions(location, bottleneck_probability)
                    })
            
            # Sort by probability
            bottleneck_predictions.sort(key=lambda x: x['bottleneck_probability'], reverse=True)
            
            return {
                'time_horizon_minutes': time_horizon_minutes,
                'total_predictions': len(bottleneck_predictions),
                'high_risk_areas': len([p for p in bottleneck_predictions if p['severity'] == 'HIGH']),
                'predictions': bottleneck_predictions,
                'timestamp': datetime.now().isoformat(),
                'summary': f"Analyzed {len(ip_camera_config)} areas, found {len(bottleneck_predictions)} potential bottlenecks"
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_high_risk_areas(self) -> Dict:
        """Identify current high-risk areas that need immediate attention"""
        try:
            ip_camera_config = st.session_state.get('ip_camera_config', {})
            
            high_risk_areas = []
            
            for cam_id, cam_config in ip_camera_config.items():
                location = cam_config.get('location', 'Unknown')
                
                # Simulate risk assessment
                import random
                people_count = random.randint(5, 35)
                
                # Calculate risk factors
                risk_score = 0
                risk_factors = []
                
                if people_count > 25:
                    risk_score += 40
                    risk_factors.append("Critical crowd density")
                elif people_count > 20:
                    risk_score += 25
                    risk_factors.append("High crowd density")
                
                # Location-based risks
                if 'entrance' in location.lower():
                    risk_score += 25
                    risk_factors.append("High-traffic chokepoint")
                elif 'corridor' in location.lower():
                    risk_score += 30
                    risk_factors.append("Narrow passage risk")
                
                # Add random factors for demo
                random_factors = [
                    ("Blocked exit route", 20),
                    ("Emergency vehicle access", 25),
                    ("Staff shortage", 15),
                    ("Equipment malfunction", 10)
                ]
                
                if random.random() < 0.3:  # 30% chance of additional risk
                    factor, score = random.choice(random_factors)
                    risk_score += score
                    risk_factors.append(factor)
                
                if risk_score > 50:  # High risk threshold
                    priority = "CRITICAL" if risk_score > 70 else "HIGH"
                    
                    high_risk_areas.append({
                        'camera_id': cam_id,
                        'location': location,
                        'people_count': people_count,
                        'risk_score': risk_score,
                        'priority': priority,
                        'risk_factors': risk_factors,
                        'immediate_actions': self.get_immediate_actions(priority, location),
                        'coordinates': {
                            'lat': cam_config.get('lat', 13.0358),
                            'lng': cam_config.get('lng', 77.6431)
                        }
                    })
            
            # Sort by risk score
            high_risk_areas.sort(key=lambda x: x['risk_score'], reverse=True)
            
            return {
                'total_high_risk_areas': len(high_risk_areas),
                'critical_areas': len([area for area in high_risk_areas if area['priority'] == 'CRITICAL']),
                'high_risk_areas': high_risk_areas,
                'timestamp': datetime.now().isoformat(),
                'summary': f"Identified {len(high_risk_areas)} high-risk areas requiring attention"
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_ip_camera_details(self) -> Dict:
        """Get comprehensive IP camera setup details"""
        try:
            ip_camera_config = st.session_state.get('ip_camera_config', {})
            
            camera_details = {}
            for cam_id, cam_config in ip_camera_config.items():
                camera_details[cam_id] = {
                    'name': cam_config.get('name', 'Unknown Camera'),
                    'location': cam_config.get('location', 'Unknown Location'),
                    'url': cam_config.get('url', ''),
                    'coordinates': {
                        'lat': cam_config.get('lat', 13.0358),
                        'lng': cam_config.get('lng', 77.6431)
                    },
                    'status': 'active',  # Assume active for demo
                    'coverage_area': self.estimate_coverage_area(cam_config.get('location', '')),
                    'setup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return {
                'total_cameras': len(ip_camera_config),
                'camera_details': camera_details,
                'coverage_map': self.generate_coverage_map(camera_details),
                'timestamp': datetime.now().isoformat(),
                'summary': f"System has {len(ip_camera_config)} IP cameras configured and operational"
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_zone_recommendations(self, risk_level: str, location: str) -> List[str]:
        """Get security recommendations for a zone"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.extend([
                "Deploy additional security personnel immediately",
                "Implement crowd control barriers",
                "Monitor exit routes closely"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Increase surveillance frequency",
                "Prepare crowd management tools",
                "Brief security team on situation"
            ])
        else:
            recommendations.append("Continue normal monitoring")
        
        # Location-specific recommendations
        if 'entrance' in location.lower():
            recommendations.append("Consider staggered entry procedures")
        elif 'food' in location.lower():
            recommendations.append("Monitor queue formation")
        
        return recommendations

    def get_bottleneck_actions(self, location: str, probability: float) -> List[str]:
        """Get recommended actions for bottleneck prevention"""
        actions = []
        
        if probability > 75:
            actions.extend([
                "Deploy staff immediately to area",
                "Activate emergency crowd management protocol",
                "Consider temporary access restrictions"
            ])
        elif probability > 50:
            actions.extend([
                "Position staff for rapid deployment",
                "Prepare crowd control equipment",
                "Monitor situation closely"
            ])
        
        if 'entrance' in location.lower():
            actions.append("Prepare alternative entry routes")
        elif 'corridor' in location.lower():
            actions.append("Clear any obstructions immediately")
        
        return actions

    def get_immediate_actions(self, priority: str, location: str) -> List[str]:
        """Get immediate actions for high-risk areas"""
        actions = []
        
        if priority == "CRITICAL":
            actions.extend([
                "Dispatch security team immediately",
                "Activate emergency protocols",
                "Notify incident command center",
                "Prepare for potential evacuation"
            ])
        else:
            actions.extend([
                "Increase security presence",
                "Monitor situation closely",
                "Prepare contingency measures"
            ])
        
        return actions

    def estimate_coverage_area(self, location: str) -> str:
        """Estimate coverage area based on location type"""
        coverage_map = {
            'entrance': '200-300 sq meters',
            'hall': '500-800 sq meters',
            'corridor': '100-200 sq meters',
            'food': '300-400 sq meters',
            'court': '300-400 sq meters'
        }
        
        for keyword, area in coverage_map.items():
            if keyword in location.lower():
                return area
        
        return '150-250 sq meters'

    def generate_coverage_map(self, camera_details: Dict) -> Dict:
        """Generate coverage map summary"""
        total_coverage = 0
        coverage_zones = []
        
        for cam_id, details in camera_details.items():
            coverage_zones.append({
                'camera': details['name'],
                'location': details['location'],
                'coordinates': details['coordinates'],
                'area': details['coverage_area']
            })
        
        return {
            'total_zones': len(coverage_zones),
            'coverage_zones': coverage_zones,
            'estimated_total_area': f"{len(coverage_zones) * 200}-{len(coverage_zones) * 400} sq meters"
        }

    def run(self):
        """Main application runner"""
        self.setup_ui()
        self.display_chat_interface()


def main():
    """Main function"""
    app = AISituationalChat()
    app.run()


if __name__ == "__main__":
    main()