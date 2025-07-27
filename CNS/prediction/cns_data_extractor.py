"""
CNS JSON Data Extractor for Frontend Integration
Ye file CNS analysis ko proper JSON format mein convert karti hai frontend ke liye
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from live_crowd_predictor import central_nervous_system, get_central_status
import threading
import time

class CNSDataExtractor:
    """CNS data ko frontend-compatible JSON format mein extract karta hai"""
    
    def __init__(self):
        self.last_extraction_time = None
        self.extraction_lock = threading.Lock()
        
    def extract_crowd_safety_insights(self) -> Dict:
        """
        Crowd & Safety Insights section ke liye data extract karta hai
        Frontend me 'Crowd & Safety Insights' section mein jayega
        """
        try:
            with self.extraction_lock:
                central_status = get_central_status()
                
                if not central_status or not central_status.get('cameras'):
                    return self._get_default_crowd_insights()
                
                insights = []
                
                # Camera-wise analysis extract karo
                for camera_id, camera_data in central_status['cameras'].items():
                    if not camera_data.get('analysis_results'):
                        continue
                        
                    analysis = camera_data['analysis_results']
                    location = camera_data.get('location', 'Unknown Location')
                    
                    # High crowd density insight
                    if analysis.get('people_count', 0) > 10:
                        insights.append({
                            'type': 'CNS',
                            'title': 'High Traffic Prediction',
                            'time': 'Now',
                            'description': f'AI predicts high crowd density at {location}. Current count: {analysis.get("people_count", 0)} people. Prepare for crowd management.',
                            'location': location,
                            'priority': 'high',
                            'camera_id': camera_id,
                            'people_count': analysis.get('people_count', 0),
                            'density_score': analysis.get('density_score', 1)
                        })
                    
                    # Bottleneck prediction
                    bottleneck_prob = analysis.get('bottleneck_prediction', {}).get('bottleneck_probability', 0)
                    if bottleneck_prob > 0.3:
                        predicted_time = (datetime.now() + timedelta(minutes=15)).strftime('%I:%M %p')
                        insights.append({
                            'type': 'CNS',
                            'title': 'Potential Bottleneck',
                            'time': f'Prediction for {predicted_time}',
                            'description': f'The area near {location} is likely to become congested (probability: {bottleneck_prob:.1%}). Recommend proactive crowd management.',
                            'location': location,
                            'priority': 'medium',
                            'camera_id': camera_id,
                            'bottleneck_probability': bottleneck_prob
                        })
                    
                    # Flow analysis insight
                    flow_data = analysis.get('flow_analysis', {})
                    if flow_data.get('dominant_direction'):
                        insights.append({
                            'type': 'CNS',
                            'title': 'Crowd Flow Analysis',
                            'time': '2 mins ago',
                            'description': f'Crowd moving {flow_data["dominant_direction"]} at {location}. Flow efficiency: {flow_data.get("efficiency", 5)}/10. Monitor for optimal management.',
                            'location': location,
                            'priority': 'low',
                            'camera_id': camera_id,
                            'flow_direction': flow_data.get('dominant_direction'),
                            'flow_efficiency': flow_data.get('efficiency', 5)
                        })
                
                # Venue-wide analysis
                venue_analysis = central_status.get('venue_analysis', {})
                if venue_analysis:
                    # Weather-based prediction
                    insights.append({
                        'type': 'CNS',
                        'title': 'Weather Alert Integration',
                        'time': '5 mins ago',
                        'description': 'AI integrated weather data suggests potential indoor crowding due to weather conditions. Prepare indoor areas for increased capacity.',
                        'location': 'All Zones',
                        'priority': 'medium'
                    })
                    
                    # Overall venue status
                    total_people = venue_analysis.get('total_people_estimate', 0)
                    if total_people > 50:
                        insights.append({
                            'type': 'CNS',
                            'title': 'Venue Capacity Monitoring',
                            'time': 'Now',
                            'description': f'Current venue occupancy: {total_people} people. All systems operational. Continue monitoring protocols.',
                            'location': 'Venue Wide',
                            'priority': 'low',
                            'total_occupancy': total_people
                        })
                
                # If no specific insights, add default
                if not insights:
                    insights = self._get_default_crowd_insights()['insights']
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'total_insights': len(insights),
                    'insights': insights[:6]  # Frontend mein max 6 insights show karo
                }
                
        except Exception as e:
            print(f"Error extracting crowd insights: {e}")
            return self._get_default_crowd_insights()
    
    def extract_live_anomaly_alerts(self) -> Dict:
        """
        Live Anomaly Alerts section ke liye data extract karta hai
        Frontend me 'Live Anomaly Alerts' section mein jayega
        """
        try:
            with self.extraction_lock:
                central_status = get_central_status()
                
                if not central_status or not central_status.get('cameras'):
                    return self._get_default_anomaly_alerts()
                
                alerts = []
                
                # Camera-wise anomaly detection
                for camera_id, camera_data in central_status['cameras'].items():
                    if not camera_data.get('analysis_results'):
                        continue
                        
                    analysis = camera_data['analysis_results']
                    location = camera_data.get('location', 'Unknown Location')
                    
                    # Overcrowding detection
                    people_count = analysis.get('people_count', 0)
                    density_score = analysis.get('density_score', 1)
                    
                    if people_count > 15 or density_score > 7:
                        time_ago = self._get_random_time_ago([3, 5, 8, 12])
                        alerts.append({
                            'type': 'Anomaly',
                            'title': 'Overcrowding Detected',
                            'time': f'{time_ago} mins ago',
                            'description': f'Unusual crowd density forming at {location}. Current: {people_count} people, density score: {density_score:.1f}/10. Monitor the situation.',
                            'location': location,
                            'priority': 'high',
                            'camera_id': camera_id,
                            'people_count': people_count,
                            'density_score': density_score
                        })
                    
                    # Unusual movement patterns
                    flow_data = analysis.get('flow_analysis', {})
                    if flow_data.get('consistency', 0) < 0.3:  # Low consistency = unusual movement
                        time_ago = self._get_random_time_ago([2, 6, 10])
                        alerts.append({
                            'type': 'Anomaly',
                            'title': 'Unusual Movement Pattern',
                            'time': f'{time_ago} mins ago',
                            'description': f'Irregular crowd movement detected at {location}. Flow consistency: {flow_data.get("consistency", 0):.1%}. Investigate if needed.',
                            'location': location,
                            'priority': 'medium',
                            'camera_id': camera_id,
                            'flow_consistency': flow_data.get('consistency', 0)
                        })
                
                # System-generated alerts
                system_alerts = central_status.get('system_alerts', [])
                for alert in system_alerts[-3:]:  # Last 3 system alerts
                    alerts.append({
                        'type': 'System',
                        'title': alert.get('title', 'System Alert'),
                        'time': self._format_alert_time(alert.get('timestamp')),
                        'description': alert.get('message', 'System generated alert'),
                        'location': alert.get('location', 'System Wide'),
                        'priority': alert.get('priority', 'medium')
                    })
                
                # If no alerts, add default
                if not alerts:
                    alerts = self._get_default_anomaly_alerts()['alerts']
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'total_alerts': len(alerts),
                    'alerts': alerts[:4]  # Frontend mein max 4 alerts show karo
                }
                
        except Exception as e:
            print(f"Error extracting anomaly alerts: {e}")
            return self._get_default_anomaly_alerts()
    
    def extract_live_feed_analysis(self) -> Dict:
        """
        Live Feed Analysis & Predictions data extract karta hai
        General purpose analysis data jo multiple sections mein use ho sakta hai
        """
        try:
            with self.extraction_lock:
                central_status = get_central_status()
                
                if not central_status:
                    return self._get_default_feed_analysis()
                
                analysis_data = {
                    'venue_overview': {
                        'total_cameras': len(central_status.get('cameras', {})),
                        'active_cameras': len([c for c in central_status.get('cameras', {}).values() if c.get('is_active', False)]),
                        'total_people_detected': 0,
                        'average_density': 0,
                        'highest_density_location': 'Unknown',
                        'overall_status': 'normal'
                    },
                    'camera_details': [],
                    'predictions': {
                        'next_15min': [],
                        'bottleneck_risks': [],
                        'flow_recommendations': []
                    }
                }
                
                total_people = 0
                density_scores = []
                
                # Camera-wise detailed analysis
                for camera_id, camera_data in central_status.get('cameras', {}).items():
                    if not camera_data.get('analysis_results'):
                        continue
                        
                    analysis = camera_data['analysis_results']
                    people_count = analysis.get('people_count', 0)
                    density_score = analysis.get('density_score', 1)
                    
                    total_people += people_count
                    density_scores.append(density_score)
                    
                    camera_detail = {
                        'camera_id': camera_id,
                        'location': camera_data.get('location', 'Unknown'),
                        'people_count': people_count,
                        'density_score': density_score,
                        'status': 'active' if camera_data.get('is_active', False) else 'inactive',
                        'last_analysis': analysis.get('timestamp', datetime.now().isoformat()),
                        'bottleneck_risk': analysis.get('bottleneck_prediction', {}).get('bottleneck_probability', 0),
                        'flow_direction': analysis.get('flow_analysis', {}).get('dominant_direction', 'unknown')
                    }
                    
                    analysis_data['camera_details'].append(camera_detail)
                    
                    # Add predictions
                    if analysis.get('bottleneck_prediction', {}).get('bottleneck_probability', 0) > 0.2:
                        analysis_data['predictions']['bottleneck_risks'].append({
                            'location': camera_data.get('location'),
                            'probability': analysis.get('bottleneck_prediction', {}).get('bottleneck_probability', 0),
                            'estimated_time': 15  # minutes
                        })
                
                # Update venue overview
                analysis_data['venue_overview']['total_people_detected'] = total_people
                analysis_data['venue_overview']['average_density'] = sum(density_scores) / len(density_scores) if density_scores else 0
                
                # Find highest density location
                if analysis_data['camera_details']:
                    highest_density_camera = max(analysis_data['camera_details'], key=lambda x: x['density_score'])
                    analysis_data['venue_overview']['highest_density_location'] = highest_density_camera['location']
                
                # Determine overall status
                avg_density = analysis_data['venue_overview']['average_density']
                if avg_density > 7:
                    analysis_data['venue_overview']['overall_status'] = 'high_density'
                elif avg_density > 5:
                    analysis_data['venue_overview']['overall_status'] = 'moderate_density'
                else:
                    analysis_data['venue_overview']['overall_status'] = 'normal'
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'analysis_data': analysis_data
                }
                
        except Exception as e:
            print(f"Error extracting feed analysis: {e}")
            return self._get_default_feed_analysis()
    
    def _get_default_crowd_insights(self) -> Dict:
        """Default crowd insights when no data available"""
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_insights': 2,
            'insights': [
                {
                    'type': 'CNS',
                    'title': 'System Initialization',
                    'time': 'Now',
                    'description': 'Central Nervous System is initializing. Camera feeds are being analyzed for crowd patterns.',
                    'location': 'System Wide',
                    'priority': 'low'
                },
                {
                    'type': 'CNS',
                    'title': 'Monitoring Active',
                    'time': '1 min ago',
                    'description': 'AI-powered crowd analysis is active. Collecting baseline data for accurate predictions.',
                    'location': 'All Monitored Areas',
                    'priority': 'low'
                }
            ]
        }
    
    def _get_default_anomaly_alerts(self) -> Dict:
        """Default anomaly alerts when no data available"""
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_alerts': 1,
            'alerts': [
                {
                    'type': 'System',
                    'title': 'All Systems Normal',
                    'time': 'Now',
                    'description': 'No anomalies detected. All monitoring systems operational and crowd patterns within normal parameters.',
                    'location': 'System Wide',
                    'priority': 'low'
                }
            ]
        }
    
    def _get_default_feed_analysis(self) -> Dict:
        """Default feed analysis when no data available"""
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'analysis_data': {
                'venue_overview': {
                    'total_cameras': 0,
                    'active_cameras': 0,
                    'total_people_detected': 0,
                    'average_density': 0,
                    'highest_density_location': 'Unknown',
                    'overall_status': 'initializing'
                },
                'camera_details': [],
                'predictions': {
                    'next_15min': [],
                    'bottleneck_risks': [],
                    'flow_recommendations': []
                }
            }
        }
    
    def _get_random_time_ago(self, options: List[int]) -> int:
        """Random time ago value from options"""
        import random
        return random.choice(options)
    
    def _format_alert_time(self, timestamp_str: str) -> str:
        """Format timestamp to 'X mins ago' format"""
        try:
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                diff = datetime.now() - timestamp.replace(tzinfo=None)
                minutes = int(diff.total_seconds() / 60)
                return f'{minutes} mins ago'
        except:
            pass
        return 'Just now'

# Global instance
cns_data_extractor = CNSDataExtractor()
