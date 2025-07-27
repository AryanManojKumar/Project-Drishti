"""
Complete Map + Video Crowd Analysis System
Bhai, yeh file tera map aur video dono ko analyze karega
"""

import cv2
import requests
import json
import base64
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os

class CompleteCrowdAnalyzer:
    def __init__(self):
        self.gemini_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={self.gemini_key}"
    
    def complete_crowd_analysis(self, 
                              map_image_path: str,
                              video_source: int = 0,
                              location_coords: Optional[Tuple[float, float]] = None,
                              analysis_duration: int = 30) -> Dict:
        """
        Complete analysis - Map + Video + Real-time data
        
        Args:
            map_image_path: Tera map screenshot path
            video_source: 0 for webcam, or video file path
            location_coords: (lat, lng) coordinates
            analysis_duration: Video analysis duration in seconds
            
        Returns:
            Complete crowd analysis report
        """
        print("🚀 Starting Complete Crowd Analysis...")
        
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_type': 'complete_map_video_analysis',
            'map_analysis': {},
            'video_analysis': {},
            'realtime_data': {},
            'combined_insights': {},
            'recommendations': [],
            'alert_level': 'normal'
        }
        
        try:
            # 1. Map Analysis
            print("📍 Analyzing map image...")
            map_analysis = self._analyze_map_comprehensive(map_image_path)
            result['map_analysis'] = map_analysis
            
            # 2. Video Analysis
            print("🎥 Analyzing video stream...")
            video_analysis = self._analyze_video_stream(video_source, analysis_duration)
            result['video_analysis'] = video_analysis
            
            # 3. Real-time Maps Data
            if location_coords:
                print("🌍 Getting real-time location data...")
                realtime_data = self._get_comprehensive_location_data(location_coords[0], location_coords[1])
                result['realtime_data'] = realtime_data
            
            # 4. Combine all insights
            print("🧠 Generating combined insights...")
            combined_insights = self._combine_all_insights(map_analysis, video_analysis, result.get('realtime_data', {}))
            result['combined_insights'] = combined_insights
            
            # 5. Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(result)
            result['recommendations'] = recommendations
            
            # 6. Determine alert level
            result['alert_level'] = self._determine_alert_level(result)
            
            print("✅ Analysis complete!")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error: {e}")
            return result
    
    def _analyze_map_comprehensive(self, image_path: str) -> Dict:
        """Comprehensive map analysis with Gemini"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            prompt = """
            Analyze this map/venue layout image for crowd management. Provide detailed analysis:
            
            1. CROWD DENSITY AREAS:
               - Identify high-density zones
               - Mark potential overcrowding spots
               - Rate density level (1-10)
            
            2. FLOW ANALYSIS:
               - Entry/exit points
               - Bottlenecks and choke points
               - Natural crowd flow paths
               - Emergency evacuation routes
            
            3. INFRASTRUCTURE:
               - Barriers and boundaries
               - Open spaces vs confined areas
               - Accessibility points
            
            4. RISK ASSESSMENT:
               - High-risk areas for crowd incidents
               - Safety concerns
               - Monitoring priority zones
            
            Respond in JSON format with these exact keys:
            {
                "density_zones": ["list of high density areas"],
                "density_rating": 5,
                "entry_exit_points": ["list of access points"],
                "bottlenecks": ["list of potential bottlenecks"],
                "flow_paths": ["natural crowd movement paths"],
                "emergency_routes": ["evacuation routes"],
                "high_risk_areas": ["areas needing attention"],
                "safety_score": 7,
                "monitoring_priorities": ["top areas to monitor"],
                "venue_type": "description of venue",
                "capacity_estimate": "estimated capacity",
                "recommendations": ["specific recommendations"]
            }
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON response
                try:
                    if '```json' in text:
                        json_text = text.split('```json')[1].split('```')[0].strip()
                    elif '{' in text:
                        json_text = text[text.find('{'):text.rfind('}')+1]
                    else:
                        json_text = text
                    
                    analysis = json.loads(json_text)
                    analysis['analysis_source'] = 'gemini_comprehensive'
                    analysis['image_analyzed'] = True
                    return analysis
                    
                except json.JSONDecodeError:
                    return {
                        'raw_analysis': text,
                        'density_rating': 5,
                        'safety_score': 5,
                        'analysis_source': 'gemini_text_only',
                        'parsing_error': True
                    }
            else:
                return {'error': 'Map analysis failed', 'status_code': response.status_code}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_video_stream(self, video_source, duration: int) -> Dict:
        """Video stream analysis for crowd counting and flow"""
        try:
            cap = cv2.VideoCapture(video_source)
            
            if not cap.isOpened():
                return {'error': 'Cannot open video source'}
            
            frame_count = 0
            people_counts = []
            flow_data = []
            previous_centers = []
            
            start_time = datetime.now()
            
            print(f"📹 Recording for {duration} seconds...")
            
            while (datetime.now() - start_time).seconds < duration:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Analyze every 5th frame to save processing time
                if frame_count % 5 == 0:
                    # Resize for faster processing
                    frame_resized = cv2.resize(frame, (640, 480))
                    
                    # Get people count using Gemini
                    people_count = self._count_people_in_frame(frame_resized)
                    people_counts.append(people_count)
                    
                    # Simple flow analysis (mock implementation)
                    current_centers = self._detect_movement_centers(frame_resized)
                    if previous_centers:
                        flow = self._calculate_flow(previous_centers, current_centers)
                        flow_data.append(flow)
                    previous_centers = current_centers
                    
                    print(f"Frame {frame_count}: {people_count} people detected")
            
            cap.release()
            
            # Calculate statistics
            avg_people = np.mean(people_counts) if people_counts else 0
            max_people = max(people_counts) if people_counts else 0
            avg_flow = np.mean([f['velocity'] for f in flow_data]) if flow_data else 0
            
            return {
                'duration_seconds': duration,
                'frames_analyzed': len(people_counts),
                'average_people_count': round(avg_people, 1),
                'max_people_count': max_people,
                'people_count_trend': people_counts[-5:] if len(people_counts) >= 5 else people_counts,
                'average_flow_velocity': round(avg_flow, 2),
                'crowd_stability': 'stable' if len(set(people_counts[-3:])) <= 2 else 'fluctuating',
                'analysis_source': 'video_stream'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _count_people_in_frame(self, frame) -> int:
        """Single frame mein people count karta hai"""
        try:
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Count the number of people in this image. Respond with only the number, nothing else."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(self.gemini_url, json=payload, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Extract number
                import re
                numbers = re.findall(r'\d+', text)
                return int(numbers[0]) if numbers else 0
            else:
                return 0
                
        except Exception:
            return 0
    
    def _detect_movement_centers(self, frame) -> List[Tuple[int, int]]:
        """Simple movement detection (mock implementation)"""
        # This is a simplified version - in practice, use proper object detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple contour detection for movement
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centers = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter small contours
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centers.append((cx, cy))
        
        return centers[:10]  # Limit to 10 centers
    
    def _calculate_flow(self, prev_centers: List[Tuple], curr_centers: List[Tuple]) -> Dict:
        """Calculate flow between frames"""
        if not prev_centers or not curr_centers:
            return {'velocity': 0, 'direction': 'stationary'}
        
        # Simple flow calculation
        velocities = []
        for curr in curr_centers:
            if prev_centers:
                closest_prev = min(prev_centers, key=lambda p: np.linalg.norm(np.array(curr) - np.array(p)))
                velocity = np.linalg.norm(np.array(curr) - np.array(closest_prev))
                velocities.append(velocity)
        
        avg_velocity = np.mean(velocities) if velocities else 0
        
        return {
            'velocity': float(avg_velocity),
            'direction': 'moving' if avg_velocity > 5 else 'stationary'
        }
    
    def _get_comprehensive_location_data(self, lat: float, lng: float) -> Dict:
        """Comprehensive location-based crowd data"""
        try:
            # Multiple API calls for comprehensive data
            places_data = self._get_nearby_places_data(lat, lng)
            traffic_data = self._get_traffic_data(lat, lng)
            
            return {
                'places_analysis': places_data,
                'traffic_analysis': traffic_data,
                'location_crowd_score': self._calculate_location_crowd_score(places_data, traffic_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_nearby_places_data(self, lat: float, lng: float) -> Dict:
        """Nearby places analysis"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 1000,
                'key': self.maps_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                return {
                    'total_places': len(places),
                    'high_rated': len([p for p in places if p.get('rating', 0) >= 4.5]),
                    'popular_places': len([p for p in places if p.get('user_ratings_total', 0) > 500]),
                    'place_types': list(set([t for p in places for t in p.get('types', [])]))[:10]
                }
            else:
                return {'error': 'Places API failed'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_traffic_data(self, lat: float, lng: float) -> Dict:
        """Traffic analysis around location"""
        # This would use Google Maps Directions API for traffic data
        # Simplified implementation
        return {
            'traffic_level': 'moderate',
            'congestion_score': 6,
            'peak_hours': ['08:00-10:00', '17:00-19:00']
        }
    
    def _calculate_location_crowd_score(self, places_data: Dict, traffic_data: Dict) -> int:
        """Calculate overall location crowd score"""
        score = 0
        
        # Places factor
        total_places = places_data.get('total_places', 0)
        popular_places = places_data.get('popular_places', 0)
        
        if total_places > 0:
            places_score = (popular_places / total_places) * 50
            score += places_score
        
        # Traffic factor
        congestion = traffic_data.get('congestion_score', 0)
        score += congestion * 5
        
        return min(int(score), 100)
    
    def _combine_all_insights(self, map_analysis: Dict, video_analysis: Dict, realtime_data: Dict) -> Dict:
        """Combine all analysis results"""
        insights = {
            'overall_crowd_level': 'unknown',
            'risk_assessment': 'low',
            'confidence_score': 0,
            'key_findings': [],
            'data_sources_used': []
        }
        
        scores = []
        
        # Map analysis score
        if 'density_rating' in map_analysis:
            map_score = map_analysis['density_rating'] * 10
            scores.append(map_score)
            insights['data_sources_used'].append('map_analysis')
            insights['key_findings'].append(f"Map density rating: {map_analysis['density_rating']}/10")
        
        # Video analysis score
        if 'average_people_count' in video_analysis:
            video_score = min(video_analysis['average_people_count'] * 5, 100)
            scores.append(video_score)
            insights['data_sources_used'].append('video_analysis')
            insights['key_findings'].append(f"Average people count: {video_analysis['average_people_count']}")
        
        # Real-time data score
        if 'location_crowd_score' in realtime_data:
            location_score = realtime_data['location_crowd_score']
            scores.append(location_score)
            insights['data_sources_used'].append('realtime_data')
            insights['key_findings'].append(f"Location crowd score: {location_score}/100")
        
        # Calculate overall score
        if scores:
            overall_score = sum(scores) / len(scores)
            insights['confidence_score'] = len(scores) * 0.33  # Higher confidence with more data sources
            
            # Categorize crowd level
            if overall_score >= 80:
                insights['overall_crowd_level'] = 'CRITICAL'
                insights['risk_assessment'] = 'high'
            elif overall_score >= 60:
                insights['overall_crowd_level'] = 'HIGH'
                insights['risk_assessment'] = 'medium'
            elif overall_score >= 40:
                insights['overall_crowd_level'] = 'MEDIUM'
                insights['risk_assessment'] = 'low'
            else:
                insights['overall_crowd_level'] = 'LOW'
                insights['risk_assessment'] = 'minimal'
        
        return insights
    
    def _generate_comprehensive_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        combined_insights = analysis_result.get('combined_insights', {})
        crowd_level = combined_insights.get('overall_crowd_level', 'LOW')
        
        # General recommendations based on crowd level
        if crowd_level == 'CRITICAL':
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED",
                "Deploy emergency crowd control measures",
                "Consider stopping entry to prevent overcrowding",
                "Activate emergency response protocols",
                "Increase security personnel by 200%"
            ])
        elif crowd_level == 'HIGH':
            recommendations.extend([
                "⚠️ HIGH ALERT - Enhanced monitoring needed",
                "Increase security presence in identified hotspots",
                "Implement crowd flow management",
                "Prepare for potential crowd control measures"
            ])
        elif crowd_level == 'MEDIUM':
            recommendations.extend([
                "📊 MODERATE - Continue active monitoring",
                "Maintain standard security protocols",
                "Monitor identified bottlenecks closely"
            ])
        else:
            recommendations.extend([
                "✅ NORMAL - Standard monitoring sufficient",
                "Continue regular security patrols"
            ])
        
        # Specific recommendations from map analysis
        map_analysis = analysis_result.get('map_analysis', {})
        if 'bottlenecks' in map_analysis:
            for bottleneck in map_analysis['bottlenecks'][:3]:
                recommendations.append(f"🎯 Monitor bottleneck: {bottleneck}")
        
        # Video-based recommendations
        video_analysis = analysis_result.get('video_analysis', {})
        if video_analysis.get('crowd_stability') == 'fluctuating':
            recommendations.append("📈 Crowd numbers fluctuating - maintain flexible response")
        
        return recommendations
    
    def _determine_alert_level(self, analysis_result: Dict) -> str:
        """Determine overall alert level"""
        combined_insights = analysis_result.get('combined_insights', {})
        crowd_level = combined_insights.get('overall_crowd_level', 'LOW')
        
        alert_mapping = {
            'CRITICAL': 'emergency',
            'HIGH': 'warning',
            'MEDIUM': 'caution',
            'LOW': 'normal'
        }
        
        return alert_mapping.get(crowd_level, 'normal')

# Main function to use
def analyze_complete_crowd_situation(map_image_path: str, 
                                   video_source: int = 0,
                                   lat: float = None, 
                                   lng: float = None,
                                   duration: int = 30) -> Dict:
    """
    Bhai, yeh main function hai - complete analysis ke liye
    
    Args:
        map_image_path: Tera map screenshot path
        video_source: 0 for webcam, video file path for recorded video
        lat, lng: Location coordinates (optional)
        duration: Video analysis duration in seconds
    
    Returns:
        Complete crowd analysis report
    """
    analyzer = CompleteCrowdAnalyzer()
    coords = (lat, lng) if lat and lng else None
    return analyzer.complete_crowd_analysis(map_image_path, video_source, coords, duration)

# Test function
if __name__ == "__main__":
    print("🎯 Complete Crowd Analysis System")
    print("=" * 50)
    
    # Test with your screenshot
    map_path = "src/Screenshot 2025-07-23 064906.png"
    
    # Check if file exists
    if os.path.exists(map_path):
        print(f"📍 Using map: {map_path}")
        
        # Run complete analysis
        result = analyze_complete_crowd_situation(
            map_image_path=map_path,
            video_source=0,  # Webcam
            duration=15  # 15 seconds analysis
        )
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Alert Level: {result['alert_level'].upper()}")
        
        if 'combined_insights' in result:
            insights = result['combined_insights']
            print(f"Overall Crowd Level: {insights['overall_crowd_level']}")
            print(f"Risk Assessment: {insights['risk_assessment']}")
            print(f"Confidence Score: {insights['confidence_score']:.2f}")
            print(f"Data Sources: {', '.join(insights['data_sources_used'])}")
        
        if 'recommendations' in result:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'][:5], 1):
                print(f"{i}. {rec}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    else:
        print(f"❌ Map file not found: {map_path}")
        print("Please check the file path and try again.")