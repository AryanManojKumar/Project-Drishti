"""
Map Integration for Crowd Density Analysis
Bhai, yeh file tera map ko system mein integrate karega
"""

import cv2
import requests
import json
import base64
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class MapCrowdIntegrator:
    def __init__(self):
        self.gemini_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
    
    def analyze_map_with_crowd_overlay(self, map_image_path: str, 
                                     location_coords: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Tera map image ko analyze karta hai crowd density ke liye
        
        Args:
            map_image_path: Path to your map screenshot/image
            location_coords: (lat, lng) if you know the coordinates
            
        Returns:
            Complete crowd analysis with map integration
        """
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'map_analysis': {},
            'crowd_hotspots': [],
            'density_zones': {},
            'recommendations': []
        }
        
        try:
            # 1. Analyze the map image
            map_analysis = self._analyze_map_image(map_image_path)
            result['map_analysis'] = map_analysis
            
            # 2. If coordinates provided, get real-time data
            if location_coords:
                real_time_data = self._get_realtime_crowd_data(location_coords[0], location_coords[1])
                result['realtime_data'] = real_time_data
            
            # 3. Identify crowd hotspots from map
            hotspots = self._identify_crowd_hotspots(map_analysis)
            result['crowd_hotspots'] = hotspots
            
            # 4. Create density zones
            density_zones = self._create_density_zones(map_analysis, hotspots)
            result['density_zones'] = density_zones
            
            # 5. Generate recommendations
            recommendations = self._generate_crowd_recommendations(result)
            result['recommendations'] = recommendations
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _analyze_map_image(self, image_path: str) -> Dict:
        """Map image ko Gemini se analyze karta hai"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Gemini prompt for map analysis
            prompt = """
            Analyze this map image for crowd density and flow patterns. Please provide:
            1. Identify any crowded areas or gatherings
            2. Spot potential bottlenecks or narrow passages
            3. Find entry/exit points
            4. Identify high-traffic zones
            5. Suggest crowd flow directions
            6. Rate overall crowd density (1-10 scale)
            
            Respond in JSON format with these keys:
            - crowded_areas: list of areas with high crowd
            - bottlenecks: potential problem areas
            - entry_exit_points: main access points
            - traffic_zones: high traffic areas
            - flow_directions: suggested crowd flow
            - density_rating: 1-10 scale
            - observations: general observations
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
            
            response = requests.post(self.gemini_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Try to parse JSON response
                try:
                    # Clean the response to extract JSON
                    if '```json' in text:
                        json_text = text.split('```json')[1].split('```')[0].strip()
                    else:
                        json_text = text
                    
                    analysis = json.loads(json_text)
                    analysis['source'] = 'gemini_map_analysis'
                    return analysis
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return raw text
                    return {
                        'raw_analysis': text,
                        'source': 'gemini_map_analysis',
                        'density_rating': 5  # default
                    }
            else:
                return {'error': 'Gemini API failed', 'status_code': response.status_code}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_realtime_crowd_data(self, lat: float, lng: float) -> Dict:
        """Real-time crowd data from Google Maps"""
        try:
            # Nearby places for crowd indicators
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 1000,  # 1km radius
                'type': 'establishment',
                'key': self.maps_key
            }
            
            response = requests.get(places_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                # Analyze places for crowd indicators
                crowd_indicators = {
                    'total_places': len(places),
                    'high_rated_places': len([p for p in places if p.get('rating', 0) >= 4.5]),
                    'busy_places': len([p for p in places if p.get('user_ratings_total', 0) > 100]),
                    'crowd_score': 0
                }
                
                # Calculate crowd score
                if crowd_indicators['total_places'] > 0:
                    crowd_score = (
                        (crowd_indicators['high_rated_places'] * 0.4) +
                        (crowd_indicators['busy_places'] * 0.6)
                    ) / crowd_indicators['total_places'] * 100
                    
                    crowd_indicators['crowd_score'] = round(crowd_score, 1)
                
                return crowd_indicators
            else:
                return {'error': 'Maps API failed'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_crowd_hotspots(self, map_analysis: Dict) -> List[Dict]:
        """Map analysis se crowd hotspots identify karta hai"""
        hotspots = []
        
        # Extract from Gemini analysis
        crowded_areas = map_analysis.get('crowded_areas', [])
        traffic_zones = map_analysis.get('traffic_zones', [])
        
        # Combine and create hotspot objects
        all_areas = crowded_areas + traffic_zones
        
        for i, area in enumerate(all_areas):
            hotspot = {
                'id': f"hotspot_{i+1}",
                'description': area if isinstance(area, str) else str(area),
                'priority': 'high' if i < 3 else 'medium',  # First 3 are high priority
                'type': 'crowded_area' if area in crowded_areas else 'traffic_zone'
            }
            hotspots.append(hotspot)
        
        return hotspots
    
    def _create_density_zones(self, map_analysis: Dict, hotspots: List[Dict]) -> Dict:
        """Density zones create karta hai"""
        density_rating = map_analysis.get('density_rating', 5)
        
        zones = {
            'high_density': {
                'count': len([h for h in hotspots if h['priority'] == 'high']),
                'areas': [h['description'] for h in hotspots if h['priority'] == 'high'],
                'risk_level': 'critical' if density_rating >= 8 else 'high'
            },
            'medium_density': {
                'count': len([h for h in hotspots if h['priority'] == 'medium']),
                'areas': [h['description'] for h in hotspots if h['priority'] == 'medium'],
                'risk_level': 'moderate'
            },
            'overall_density': {
                'rating': density_rating,
                'category': self._categorize_density(density_rating)
            }
        }
        
        return zones
    
    def _categorize_density(self, rating: int) -> str:
        """Density rating ko category mein convert karta hai"""
        if rating >= 9:
            return 'CRITICAL'
        elif rating >= 7:
            return 'HIGH'
        elif rating >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_crowd_recommendations(self, analysis_result: Dict) -> List[str]:
        """Crowd management recommendations generate karta hai"""
        recommendations = []
        
        density_zones = analysis_result.get('density_zones', {})
        overall_rating = density_zones.get('overall_density', {}).get('rating', 5)
        
        # Based on density rating
        if overall_rating >= 8:
            recommendations.extend([
                "🚨 CRITICAL: Immediate crowd control measures needed",
                "Deploy additional security personnel to high-density areas",
                "Consider restricting entry to prevent overcrowding",
                "Set up emergency evacuation routes"
            ])
        elif overall_rating >= 6:
            recommendations.extend([
                "⚠️ HIGH ALERT: Monitor crowd movement closely",
                "Increase security presence in identified hotspots",
                "Implement crowd flow management",
                "Prepare contingency plans"
            ])
        else:
            recommendations.extend([
                "✅ NORMAL: Continue regular monitoring",
                "Maintain standard security protocols",
                "Keep emergency plans ready"
            ])
        
        # Specific hotspot recommendations
        hotspots = analysis_result.get('crowd_hotspots', [])
        high_priority_spots = [h for h in hotspots if h['priority'] == 'high']
        
        if high_priority_spots:
            recommendations.append(f"Focus on {len(high_priority_spots)} high-priority areas")
            for spot in high_priority_spots[:3]:  # Top 3
                recommendations.append(f"• Monitor: {spot['description']}")
        
        return recommendations

# Easy-to-use function
def analyze_map_for_crowds(map_image_path: str, lat: float = None, lng: float = None) -> Dict:
    """
    Bhai, bas yeh function call kar!
    
    Args:
        map_image_path: Tera map screenshot ka path
        lat, lng: Location coordinates (optional)
    
    Returns:
        Complete crowd analysis
    """
    integrator = MapCrowdIntegrator()
    coords = (lat, lng) if lat and lng else None
    return integrator.analyze_map_with_crowd_overlay(map_image_path, coords)

# Test function
if __name__ == "__main__":
    # Test with your screenshot
    map_path = "src/Screenshot 2025-07-23 064906.png"
    
    print("Analyzing your map for crowd density...")
    result = analyze_map_for_crowds(map_path)
    
    print(f"\n📊 CROWD ANALYSIS RESULTS:")
    print(f"Timestamp: {result['timestamp']}")
    
    if 'density_zones' in result:
        overall = result['density_zones']['overall_density']
        print(f"Overall Density: {overall['rating']}/10 ({overall['category']})")
    
    if 'crowd_hotspots' in result:
        print(f"\n🎯 HOTSPOTS IDENTIFIED: {len(result['crowd_hotspots'])}")
        for hotspot in result['crowd_hotspots'][:3]:
            print(f"• {hotspot['description']} ({hotspot['priority']} priority)")
    
    if 'recommendations' in result:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in result['recommendations'][:5]:
            print(f"• {rec}")
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")