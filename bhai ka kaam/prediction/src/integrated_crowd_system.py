"""Integrated crowd management system combining video, device locations, and Maps API data."""

import os
import json
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our components
from .gemini_vision_processor import GeminiCrowdVisionProcessor
from .device_location_processor_simple import DeviceLocationProcessor
from .maps_crowd_analyzer import MapsCrowdAnalyzer
from .gemini_forecasting_model import GeminiBottleneckForecaster

class IntegratedCrowdManagementSystem:
    """
    Comprehensive crowd management system that combines:
    1. Video analysis (Gemini Vision)
    2. Device location data
    3. Google Maps crowd/traffic data
    4. AI-powered predictions
    """
    
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', 'project-dishti')
        
        # Initialize all components
        self.vision_processor = GeminiCrowdVisionProcessor()
        self.location_processor = DeviceLocationProcessor()
        self.maps_analyzer = MapsCrowdAnalyzer()
        self.forecaster = GeminiBottleneckForecaster()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_zone_comprehensive(self, zone_config: Dict) -> Dict:
        """
        Perform comprehensive crowd analysis for a specific zone using all data sources.
        
        Args:
            zone_config: Zone configuration with location and video source
            
        Returns:
            Comprehensive analysis results
        """
        zone_id = zone_config['zone_id']
        lat = zone_config['coordinates']['lat']
        lng = zone_config['coordinates']['lng']
        
        self.logger.info(f"Starting comprehensive analysis for zone: {zone_id}")
        
        analysis_result = {
            'zone_id': zone_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data_sources': {},
            'integrated_metrics': {},
            'predictions': {},
            'recommendations': []
        }
        
        try:
            # 1. VIDEO ANALYSIS (if video source available)
            if 'video_source' in zone_config:
                self.logger.info(f"Analyzing video feed for zone {zone_id}...")
                video_analysis = self._analyze_video_source(zone_config['video_source'])
                analysis_result['data_sources']['video_analysis'] = video_analysis
            
            # 2. DEVICE LOCATION ANALYSIS
            self.logger.info(f"Analyzing device locations for zone {zone_id}...")
            device_analysis = self._analyze_device_locations(lat, lng, zone_config.get('radius', 100))
            analysis_result['data_sources']['device_locations'] = device_analysis
            
            # 3. GOOGLE MAPS ANALYSIS
            self.logger.info(f"Analyzing Maps data for zone {zone_id}...")
            maps_analysis = self.maps_analyzer.analyze_area_crowd_factors(lat, lng, zone_config.get('radius', 500))
            analysis_result['data_sources']['maps_data'] = maps_analysis
            
            # 4. INTEGRATE ALL DATA SOURCES
            integrated_metrics = self._integrate_data_sources(analysis_result['data_sources'])
            analysis_result['integrated_metrics'] = integrated_metrics
            
            # 5. GENERATE AI PREDICTIONS
            predictions = self._generate_integrated_predictions(analysis_result)
            analysis_result['predictions'] = predictions
            
            # 6. GENERATE RECOMMENDATIONS
            recommendations = self._generate_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            self.logger.info(f"Comprehensive analysis completed for zone {zone_id}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            analysis_result['error'] = str(e)
            return analysis_result
    
    def _analyze_video_source(self, video_source: str) -> Dict:
        """Analyze video source using Gemini Vision."""
        try:
            import cv2
            import numpy as np
            
            # Capture a frame from video source
            cap = cv2.VideoCapture(video_source)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize frame for faster processing
                frame_resized = cv2.resize(frame, (640, 480))
                
                # Analyze with Gemini Vision
                analysis = self.vision_processor.detect_people_with_gemini(frame_resized)
                return analysis
            else:
                return {'error': 'Could not capture video frame', 'person_count': 0}
                
        except Exception as e:
            return {'error': f'Video analysis failed: {e}', 'person_count': 0}
    
    def _analyze_device_locations(self, lat: float, lng: float, radius: int) -> Dict:
        """Analyze device location density around a point."""
        try:
            # Simulate device location analysis
            # In a real system, this would query actual device location data
            
            # For demo, generate some sample device data
            import random
            device_count = random.randint(10, 50)
            
            return {
                'device_count': device_count,
                'density_per_100m': device_count / (radius / 100),
                'location': {'lat': lat, 'lng': lng},
                'radius': radius,
                'data_source': 'simulated_device_locations'
            }
            
        except Exception as e:
            return {'error': f'Device location analysis failed: {e}', 'device_count': 0}
    
    def _integrate_data_sources(self, data_sources: Dict) -> Dict:
        """Integrate data from all sources into unified metrics."""
        integrated = {
            'total_crowd_indicators': 0,
            'confidence_score': 0,
            'data_source_count': 0,
            'crowd_density_score': 0,
            'movement_patterns': {},
            'external_factors': {}
        }
        
        crowd_scores = []
        confidence_weights = []
        
        # Process video analysis data
        video_data = data_sources.get('video_analysis', {})
        if video_data and 'person_count' in video_data:
            person_count = video_data.get('person_count', 0)
            crowd_scores.append(min(person_count * 2, 100))  # Scale to 0-100
            confidence_weights.append(0.4)  # High confidence for direct observation
            integrated['data_source_count'] += 1
            
            # Extract movement patterns
            integrated['movement_patterns']['video_based'] = {
                'density_level': video_data.get('density_level', 'unknown'),
                'movement_speed': video_data.get('movement_speed', 'unknown'),
                'bottleneck_areas': video_data.get('bottleneck_areas', [])
            }
        
        # Process device location data
        device_data = data_sources.get('device_locations', {})
        if device_data and 'device_count' in device_data:
            device_count = device_data.get('device_count', 0)
            crowd_scores.append(min(device_count * 1.5, 100))  # Scale to 0-100
            confidence_weights.append(0.3)  # Medium confidence
            integrated['data_source_count'] += 1
        
        # Process Maps API data
        maps_data = data_sources.get('maps_data', {})
        if maps_data and 'composite_crowd_score' in maps_data:
            maps_score = maps_data['composite_crowd_score'].get('composite_score', 0)
            crowd_scores.append(maps_score)
            confidence_weights.append(0.3)  # Medium confidence
            integrated['data_source_count'] += 1
            
            # Extract external factors
            integrated['external_factors'] = {
                'nearby_busy_places': maps_data.get('crowd_factors', {}).get('places_density', {}).get('total_busy_places', 0),
                'traffic_level': maps_data.get('crowd_factors', {}).get('traffic_density', {}).get('average_traffic_level', 0),
                'transit_accessibility': maps_data.get('crowd_factors', {}).get('transit_accessibility', {}).get('transit_accessibility_score', 0)
            }
        
        # Calculate integrated metrics
        if crowd_scores and confidence_weights:
            # Weighted average of crowd scores
            integrated['crowd_density_score'] = sum(
                score * weight for score, weight in zip(crowd_scores, confidence_weights)
            ) / sum(confidence_weights)
            
            # Confidence based on number of data sources and their reliability
            integrated['confidence_score'] = min(
                (integrated['data_source_count'] / 3.0) * 0.8 + 0.2, 1.0
            )
        
        # Categorize overall crowd level
        crowd_score = integrated['crowd_density_score']
        if crowd_score >= 80:
            integrated['crowd_category'] = 'critical'
        elif crowd_score >= 60:
            integrated['crowd_category'] = 'high'
        elif crowd_score >= 40:
            integrated['crowd_category'] = 'medium'
        else:
            integrated['crowd_category'] = 'low'
        
        return integrated
    
    def _generate_integrated_predictions(self, analysis_result: Dict) -> Dict:
        """Generate predictions using integrated data."""
        try:
            # Prepare data for Gemini forecasting
            integrated_metrics = analysis_result.get('integrated_metrics', {})
            
            current_data = {
                'zones': {
                    analysis_result['zone_id']: {
                        'person_count': analysis_result.get('data_sources', {}).get('video_analysis', {}).get('person_count', 0),
                        'density': integrated_metrics.get('crowd_density_score', 0) / 20,  # Convert to density scale
                        'device_count': analysis_result.get('data_sources', {}).get('device_locations', {}).get('device_count', 0),
                        'flow_velocity': 1.0,  # Default value
                        'external_factors': integrated_metrics.get('external_factors', {})
                    }
                }
            }
            
            # Generate predictions using Gemini
            predictions = self.forecaster.predict_bottlenecks_with_gemini(current_data)
            
            return {
                'bottleneck_predictions': predictions,
                'prediction_method': 'integrated_gemini_ai',
                'data_sources_used': integrated_metrics.get('data_source_count', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating integrated predictions: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        integrated_metrics = analysis_result.get('integrated_metrics', {})
        crowd_category = integrated_metrics.get('crowd_category', 'low')
        crowd_score = integrated_metrics.get('crowd_density_score', 0)
        
        # Basic recommendations based on crowd level
        if crowd_category == 'critical':
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED: Deploy additional staff",
                "🚨 Consider crowd control measures",
                "🚨 Prepare for potential evacuation procedures",
                "📢 Issue public announcements to manage flow"
            ])
        elif crowd_category == 'high':
            recommendations.extend([
                "⚠️ Increase monitoring frequency",
                "⚠️ Deploy additional security personnel",
                "📊 Monitor crowd flow patterns closely",
                "🚶 Consider alternative route suggestions"
            ])
        elif crowd_category == 'medium':
            recommendations.extend([
                "👀 Continue regular monitoring",
                "📈 Track crowd growth trends",
                "🔄 Prepare contingency plans"
            ])
        else:
            recommendations.extend([
                "✅ Normal monitoring sufficient",
                "📊 Continue data collection"
            ])
        
        # Specific recommendations based on data sources
        video_data = analysis_result.get('data_sources', {}).get('video_analysis', {})
        if video_data.get('bottleneck_areas'):
            recommendations.append(f"🚧 Address bottleneck areas: {', '.join(video_data['bottleneck_areas'])}")
        
        maps_data = analysis_result.get('data_sources', {}).get('maps_data', {})
        traffic_level = maps_data.get('crowd_factors', {}).get('traffic_density', {}).get('average_traffic_level', 0)
        if traffic_level > 50:
            recommendations.append("🚗 High traffic detected - consider traffic management")
        
        return recommendations
    
    def run_continuous_monitoring(self, zones_config: List[Dict], interval_minutes: int = 5):
        """Run continuous monitoring for multiple zones."""
        import time
        
        self.logger.info(f"Starting continuous monitoring for {len(zones_config)} zones")
        
        try:
            while True:
                for zone_config in zones_config:
                    self.logger.info(f"Analyzing zone: {zone_config['zone_id']}")
                    
                    # Perform comprehensive analysis
                    analysis = self.analyze_zone_comprehensive(zone_config)
                    
                    # Log key metrics
                    integrated_metrics = analysis.get('integrated_metrics', {})
                    self.logger.info(
                        f"Zone {zone_config['zone_id']}: "
                        f"Crowd Score: {integrated_metrics.get('crowd_density_score', 0):.1f}, "
                        f"Category: {integrated_metrics.get('crowd_category', 'unknown')}, "
                        f"Confidence: {integrated_metrics.get('confidence_score', 0):.2f}"
                    )
                    
                    # Check for critical situations
                    if integrated_metrics.get('crowd_category') in ['critical', 'high']:
                        self.logger.warning(f"⚠️ HIGH CROWD DENSITY in zone {zone_config['zone_id']}")
                        for rec in analysis.get('recommendations', []):
                            self.logger.warning(f"   {rec}")
                
                # Wait for next interval
                self.logger.info(f"Waiting {interval_minutes} minutes until next analysis...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("Continuous monitoring stopped by user")
    
    def test_integrated_system(self):
        """Test the integrated system with sample data."""
        print("Testing Integrated Crowd Management System...")
        
        # Sample zone configuration
        test_zone = {
            'zone_id': 'test_entrance',
            'name': 'Test Entrance Area',
            'coordinates': {'lat': 40.7580, 'lng': -73.9855},  # Times Square
            'radius': 200,
            'video_source': 0  # Webcam
        }
        
        try:
            print(f"Analyzing zone: {test_zone['zone_id']}")
            analysis = self.analyze_zone_comprehensive(test_zone)
            
            print("✅ Integrated system test successful!")
            
            # Print key results
            integrated_metrics = analysis.get('integrated_metrics', {})
            print(f"📊 Crowd Density Score: {integrated_metrics.get('crowd_density_score', 0):.1f}/100")
            print(f"📊 Crowd Category: {integrated_metrics.get('crowd_category', 'unknown')}")
            print(f"📊 Confidence Score: {integrated_metrics.get('confidence_score', 0):.2f}")
            print(f"📊 Data Sources Used: {integrated_metrics.get('data_source_count', 0)}/3")
            
            print("\n🎯 Recommendations:")
            for rec in analysis.get('recommendations', []):
                print(f"   {rec}")
            
            return True
            
        except Exception as e:
            print(f"❌ Integrated system test failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    system = IntegratedCrowdManagementSystem()
    system.test_integrated_system()