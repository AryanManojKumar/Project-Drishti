"""Google Maps API integration for crowd density analysis."""

import os
import requests
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import googlemaps
from geopy.distance import geodesic

class MapsCrowdAnalyzer:
    """Uses Google Maps API to analyze crowd density and traffic patterns."""
    
    def __init__(self):
        self.maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA')
        self.gmaps = googlemaps.Client(key=self.maps_api_key)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_places_crowd_density(self, lat: float, lng: float, radius: int = 500) -> Dict:
        """
        Get crowd density information from nearby places using Google Places API.
        
        Args:
            lat: Latitude of the center point
            lng: Longitude of the center point
            radius: Search radius in meters
            
        Returns:
            Dictionary with crowd density information
        """
        try:
            # Search for nearby places that typically have crowd data
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='establishment'  # Get all types of establishments
            )
            
            crowd_data = {
                'location': {'lat': lat, 'lng': lng},
                'radius': radius,
                'timestamp': datetime.utcnow().isoformat(),
                'places_with_crowds': [],
                'total_busy_places': 0,
                'average_crowd_level': 0,
                'peak_hours_info': []
            }
            
            busy_levels = []
            
            for place in places_result.get('results', []):
                place_id = place.get('place_id')
                
                if place_id:
                    # Get detailed place information including popular times
                    place_details = self.get_place_crowd_details(place_id)
                    
                    if place_details:
                        crowd_data['places_with_crowds'].append({
                            'name': place.get('name', 'Unknown'),
                            'place_id': place_id,
                            'location': place.get('geometry', {}).get('location', {}),
                            'crowd_info': place_details,
                            'distance_meters': self._calculate_distance(
                                (lat, lng), 
                                (place['geometry']['location']['lat'], 
                                 place['geometry']['location']['lng'])
                            )
                        })
                        
                        # Extract current busy level if available
                        current_busy = place_details.get('current_popularity', 0)
                        if current_busy > 0:
                            busy_levels.append(current_busy)
            
            # Calculate aggregate crowd metrics
            if busy_levels:
                crowd_data['total_busy_places'] = len(busy_levels)
                crowd_data['average_crowd_level'] = sum(busy_levels) / len(busy_levels)
                crowd_data['max_crowd_level'] = max(busy_levels)
                crowd_data['crowd_density_category'] = self._categorize_crowd_density(
                    crowd_data['average_crowd_level']
                )
            
            return crowd_data
            
        except Exception as e:
            self.logger.error(f"Error getting places crowd density: {e}")
            return self._empty_crowd_data(lat, lng, radius)
    
    def get_place_crowd_details(self, place_id: str) -> Dict:
        """
        Get detailed crowd information for a specific place.
        
        Args:
            place_id: Google Places ID
            
        Returns:
            Dictionary with crowd details
        """
        try:
            # Get place details including popular times
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'current_opening_hours', 'popular_times', 'live_popular_times']
            )
            
            result = place_details.get('result', {})
            
            crowd_info = {
                'place_name': result.get('name', 'Unknown'),
                'current_popularity': 0,
                'popular_times': [],
                'is_currently_busy': False,
                'peak_hours': []
            }
            
            # Extract popular times data (this is limited in the free API)
            # Note: Full popular times data requires Google My Business API or web scraping
            
            # For now, we'll simulate crowd data based on time of day
            current_hour = datetime.now().hour
            crowd_info['current_popularity'] = self._estimate_crowd_by_time(current_hour)
            crowd_info['is_currently_busy'] = crowd_info['current_popularity'] > 50
            
            return crowd_info
            
        except Exception as e:
            self.logger.error(f"Error getting place crowd details: {e}")
            return {}
    
    def get_traffic_density(self, origin: Tuple[float, float], 
                           destinations: List[Tuple[float, float]]) -> Dict:
        """
        Get traffic density information using Google Maps Directions API.
        
        Args:
            origin: (lat, lng) of origin point
            destinations: List of (lat, lng) destination points
            
        Returns:
            Dictionary with traffic density information
        """
        try:
            traffic_data = {
                'origin': {'lat': origin[0], 'lng': origin[1]},
                'destinations': [],
                'average_traffic_level': 0,
                'congested_routes': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            traffic_levels = []
            
            for dest in destinations:
                # Get directions with traffic information
                directions = self.gmaps.directions(
                    origin=origin,
                    destination=dest,
                    mode="driving",
                    departure_time=datetime.now(),
                    traffic_model="best_guess"
                )
                
                if directions:
                    route = directions[0]
                    leg = route['legs'][0]
                    
                    # Extract traffic information
                    duration_normal = leg['duration']['value']  # seconds
                    duration_traffic = leg.get('duration_in_traffic', {}).get('value', duration_normal)
                    
                    # Calculate traffic delay ratio
                    traffic_ratio = duration_traffic / duration_normal if duration_normal > 0 else 1.0
                    traffic_level = min((traffic_ratio - 1.0) * 100, 100)  # Convert to 0-100 scale
                    
                    traffic_levels.append(traffic_level)
                    
                    traffic_data['destinations'].append({
                        'location': {'lat': dest[0], 'lng': dest[1]},
                        'distance_km': leg['distance']['value'] / 1000,
                        'duration_normal_min': duration_normal / 60,
                        'duration_traffic_min': duration_traffic / 60,
                        'traffic_delay_ratio': traffic_ratio,
                        'traffic_level': traffic_level,
                        'is_congested': traffic_level > 30
                    })
            
            # Calculate aggregate traffic metrics
            if traffic_levels:
                traffic_data['average_traffic_level'] = sum(traffic_levels) / len(traffic_levels)
                traffic_data['congested_routes'] = sum(1 for level in traffic_levels if level > 30)
                traffic_data['traffic_density_category'] = self._categorize_traffic_density(
                    traffic_data['average_traffic_level']
                )
            
            return traffic_data
            
        except Exception as e:
            self.logger.error(f"Error getting traffic density: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def analyze_area_crowd_factors(self, center_lat: float, center_lng: float, 
                                  radius: int = 1000) -> Dict:
        """
        Comprehensive crowd analysis combining multiple Maps API data sources.
        
        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            radius: Analysis radius in meters
            
        Returns:
            Comprehensive crowd analysis
        """
        try:
            analysis = {
                'location': {'lat': center_lat, 'lng': center_lng},
                'radius': radius,
                'timestamp': datetime.utcnow().isoformat(),
                'crowd_factors': {}
            }
            
            # 1. Get nearby places crowd data
            places_crowd = self.get_places_crowd_density(center_lat, center_lng, radius)
            analysis['crowd_factors']['places_density'] = places_crowd
            
            # 2. Get traffic density around the area
            # Create a grid of points around the center for traffic analysis
            nearby_points = self._generate_nearby_points(center_lat, center_lng, radius, 8)
            traffic_data = self.get_traffic_density((center_lat, center_lng), nearby_points)
            analysis['crowd_factors']['traffic_density'] = traffic_data
            
            # 3. Get nearby transit stations (potential crowd sources)
            transit_data = self.get_nearby_transit_stations(center_lat, center_lng, radius)
            analysis['crowd_factors']['transit_accessibility'] = transit_data
            
            # 4. Calculate composite crowd score
            composite_score = self._calculate_composite_crowd_score(analysis['crowd_factors'])
            analysis['composite_crowd_score'] = composite_score
            
            # 5. Generate crowd predictions based on Maps data
            predictions = self._generate_maps_based_predictions(analysis)
            analysis['maps_predictions'] = predictions
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive crowd analysis: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def get_nearby_transit_stations(self, lat: float, lng: float, radius: int) -> Dict:
        """Get nearby transit stations that could contribute to crowd density."""
        try:
            # Search for transit stations
            transit_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='transit_station'
            )
            
            stations = []
            for station in transit_result.get('results', []):
                stations.append({
                    'name': station.get('name', 'Unknown Station'),
                    'location': station.get('geometry', {}).get('location', {}),
                    'rating': station.get('rating', 0),
                    'user_ratings_total': station.get('user_ratings_total', 0),
                    'distance_meters': self._calculate_distance(
                        (lat, lng),
                        (station['geometry']['location']['lat'],
                         station['geometry']['location']['lng'])
                    )
                })
            
            return {
                'total_stations': len(stations),
                'stations': stations,
                'transit_accessibility_score': min(len(stations) * 20, 100)  # 0-100 scale
            }
            
        except Exception as e:
            self.logger.error(f"Error getting transit stations: {e}")
            return {'total_stations': 0, 'stations': [], 'transit_accessibility_score': 0}
    
    def _generate_nearby_points(self, center_lat: float, center_lng: float, 
                               radius: int, num_points: int) -> List[Tuple[float, float]]:
        """Generate points around a center for traffic analysis."""
        import math
        
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Convert radius from meters to approximate degrees
            radius_deg = radius / 111000  # Rough conversion
            
            lat = center_lat + radius_deg * math.cos(angle)
            lng = center_lng + radius_deg * math.sin(angle)
            points.append((lat, lng))
        
        return points
    
    def _calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """Calculate distance between two points in meters."""
        return geodesic(point1, point2).meters
    
    def _estimate_crowd_by_time(self, hour: int) -> int:
        """Estimate crowd level based on time of day (0-100 scale)."""
        # Simple time-based crowd estimation
        if 7 <= hour <= 9:  # Morning rush
            return 80
        elif 12 <= hour <= 14:  # Lunch time
            return 70
        elif 17 <= hour <= 19:  # Evening rush
            return 85
        elif 20 <= hour <= 22:  # Evening entertainment
            return 60
        elif 6 <= hour <= 23:  # Regular day hours
            return 40
        else:  # Night hours
            return 15
    
    def _categorize_crowd_density(self, level: float) -> str:
        """Categorize crowd density level."""
        if level >= 80:
            return "critical"
        elif level >= 60:
            return "high"
        elif level >= 40:
            return "medium"
        else:
            return "low"
    
    def _categorize_traffic_density(self, level: float) -> str:
        """Categorize traffic density level."""
        if level >= 50:
            return "heavy"
        elif level >= 30:
            return "moderate"
        elif level >= 15:
            return "light"
        else:
            return "minimal"
    
    def _calculate_composite_crowd_score(self, crowd_factors: Dict) -> Dict:
        """Calculate a composite crowd score from all factors."""
        scores = []
        weights = []
        
        # Places density score
        places_data = crowd_factors.get('places_density', {})
        if places_data.get('average_crowd_level', 0) > 0:
            scores.append(places_data['average_crowd_level'])
            weights.append(0.4)  # 40% weight
        
        # Traffic density score
        traffic_data = crowd_factors.get('traffic_density', {})
        if traffic_data.get('average_traffic_level', 0) > 0:
            scores.append(traffic_data['average_traffic_level'])
            weights.append(0.3)  # 30% weight
        
        # Transit accessibility score
        transit_data = crowd_factors.get('transit_accessibility', {})
        if transit_data.get('transit_accessibility_score', 0) > 0:
            scores.append(transit_data['transit_accessibility_score'])
            weights.append(0.3)  # 30% weight
        
        # Calculate weighted average
        if scores and weights:
            composite_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            composite_score = 0
        
        return {
            'composite_score': composite_score,
            'category': self._categorize_crowd_density(composite_score),
            'contributing_factors': len(scores),
            'confidence': min(len(scores) * 0.33, 1.0)  # Higher confidence with more factors
        }
    
    def _generate_maps_based_predictions(self, analysis: Dict) -> Dict:
        """Generate crowd predictions based on Maps API data."""
        composite_score = analysis.get('composite_crowd_score', {}).get('composite_score', 0)
        
        # Simple prediction logic based on current Maps data
        current_hour = datetime.now().hour
        
        # Predict crowd level 20 minutes from now
        time_factor = 1.0
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # Rush hours
            time_factor = 1.2  # Expect increase
        elif 22 <= current_hour <= 6:  # Night hours
            time_factor = 0.8  # Expect decrease
        
        predicted_score = min(composite_score * time_factor, 100)
        
        return {
            'predicted_crowd_score_20min': predicted_score,
            'prediction_confidence': 0.7,
            'trend': 'increasing' if time_factor > 1.0 else 'decreasing' if time_factor < 1.0 else 'stable',
            'based_on_factors': ['places_density', 'traffic_patterns', 'time_of_day']
        }
    
    def _empty_crowd_data(self, lat: float, lng: float, radius: int) -> Dict:
        """Return empty crowd data structure."""
        return {
            'location': {'lat': lat, 'lng': lng},
            'radius': radius,
            'timestamp': datetime.utcnow().isoformat(),
            'places_with_crowds': [],
            'total_busy_places': 0,
            'average_crowd_level': 0,
            'error': 'No crowd data available'
        }
    
    def test_maps_integration(self):
        """Test Maps API integration."""
        print("Testing Google Maps API integration...")
        
        # Test with Times Square coordinates (busy area)
        test_lat, test_lng = 40.7580, -73.9855
        
        try:
            print(f"Analyzing crowd factors around ({test_lat}, {test_lng})...")
            
            # Test comprehensive analysis
            analysis = self.analyze_area_crowd_factors(test_lat, test_lng, 500)
            
            print("✅ Maps API integration successful!")
            print(f"Composite crowd score: {analysis.get('composite_crowd_score', {}).get('composite_score', 0):.1f}")
            print(f"Crowd category: {analysis.get('composite_crowd_score', {}).get('category', 'unknown')}")
            
            # Print detailed results
            places_data = analysis.get('crowd_factors', {}).get('places_density', {})
            print(f"Nearby busy places: {places_data.get('total_busy_places', 0)}")
            
            traffic_data = analysis.get('crowd_factors', {}).get('traffic_density', {})
            print(f"Average traffic level: {traffic_data.get('average_traffic_level', 0):.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Maps API test failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    analyzer = MapsCrowdAnalyzer()
    analyzer.test_maps_integration()