"""
Large Scale Concert Crowd Density Mapper
Example: Coldplay Ahmedabad Concert at Narendra Modi Stadium
"""

import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import folium
from folium import plugins
import time

class ConcertCrowdMapper:
    def __init__(self):
        # Tera API keys
        self.gemini_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
        
        # Coldplay Ahmedabad Concert - Narendra Modi Stadium
        self.venue_config = {
            'name': 'Coldplay Concert - Narendra Modi Stadium',
            'center_lat': 23.0937,
            'center_lng': 72.5950,
            'venue_radius': 800,  # meters
            'grid_size': 50,      # 50x50 meter grids
            'capacity': 132000    # Stadium capacity
        }
    
    def create_venue_grid(self):
        """Concert venue ko grid mein divide karta hai"""
        center_lat = self.venue_config['center_lat']
        center_lng = self.venue_config['center_lng']
        radius = self.venue_config['venue_radius']
        grid_size = self.venue_config['grid_size']
        
        # Calculate grid boundaries
        # 1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat)
        lat_per_meter = 1 / 111000
        lng_per_meter = 1 / (111000 * np.cos(np.radians(center_lat)))
        
        # Grid dimensions
        grid_radius_lat = radius * lat_per_meter
        grid_radius_lng = radius * lng_per_meter
        
        # Create grid points
        num_grids = int(2 * radius / grid_size)
        
        grids = []
        grid_id = 1
        
        for i in range(num_grids):
            for j in range(num_grids):
                # Calculate grid center
                lat_offset = (i - num_grids/2) * grid_size * lat_per_meter
                lng_offset = (j - num_grids/2) * grid_size * lng_per_meter
                
                grid_lat = center_lat + lat_offset
                grid_lng = center_lng + lng_offset
                
                # Check if grid is within venue radius
                distance = self._calculate_distance(center_lat, center_lng, grid_lat, grid_lng)
                
                if distance <= radius:
                    grid_info = {
                        'grid_id': f'G{grid_id:03d}',
                        'center_lat': grid_lat,
                        'center_lng': grid_lng,
                        'bounds': {
                            'north': grid_lat + (grid_size/2) * lat_per_meter,
                            'south': grid_lat - (grid_size/2) * lat_per_meter,
                            'east': grid_lng + (grid_size/2) * lng_per_meter,
                            'west': grid_lng - (grid_size/2) * lng_per_meter
                        },
                        'zone_type': self._determine_zone_type(distance, radius),
                        'max_capacity': self._estimate_grid_capacity(distance, radius)
                    }
                    grids.append(grid_info)
                    grid_id += 1
        
        print(f"✅ Created {len(grids)} grids for {self.venue_config['name']}")
        return grids
    
    def _determine_zone_type(self, distance_from_center, total_radius):
        """Grid ka zone type determine karta hai"""
        ratio = distance_from_center / total_radius
        
        if ratio <= 0.3:
            return 'main_stage'      # Main stage area
        elif ratio <= 0.5:
            return 'premium_zone'    # Premium seating
        elif ratio <= 0.7:
            return 'general_zone'    # General admission
        else:
            return 'outer_zone'      # Parking/facilities
    
    def _estimate_grid_capacity(self, distance_from_center, total_radius):
        """Grid ki estimated capacity calculate karta hai"""
        zone_type = self._determine_zone_type(distance_from_center, total_radius)
        
        # People per 50x50m grid based on zone
        capacity_map = {
            'main_stage': 800,      # High density near stage
            'premium_zone': 600,    # Medium-high density
            'general_zone': 400,    # Medium density
            'outer_zone': 100       # Low density (facilities)
        }
        
        return capacity_map.get(zone_type, 200)
    
    def get_real_time_crowd_data(self, grids):
        """Har grid ke liye real-time crowd data fetch karta hai"""
        print("🔄 Fetching real-time crowd data from Google APIs...")
        
        crowd_data = []
        
        for i, grid in enumerate(grids):
            print(f"Analyzing grid {i+1}/{len(grids)}: {grid['grid_id']}")
            
            # Get crowd data for this grid
            grid_crowd = self._analyze_grid_crowd(grid)
            
            crowd_data.append({
                'grid_id': grid['grid_id'],
                'zone_type': grid['zone_type'],
                'max_capacity': grid['max_capacity'],
                'current_crowd': grid_crowd['estimated_people'],
                'crowd_density': grid_crowd['density_percentage'],
                'crowd_level': grid_crowd['crowd_level'],
                'nearby_activity': grid_crowd['nearby_activity'],
                'traffic_factor': grid_crowd['traffic_factor'],
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Rate limiting - Google APIs have limits
            time.sleep(0.5)
        
        return crowd_data
    
    def _analyze_grid_crowd(self, grid):
        """Individual grid ka crowd analysis karta hai"""
        lat = grid['center_lat']
        lng = grid['center_lng']
        
        try:
            # 1. Nearby places analysis
            places_data = self._get_nearby_places_activity(lat, lng)
            
            # 2. Traffic analysis
            traffic_data = self._get_traffic_density(lat, lng)
            
            # 3. Estimate crowd based on multiple factors
            estimated_crowd = self._estimate_grid_crowd(grid, places_data, traffic_data)
            
            return estimated_crowd
            
        except Exception as e:
            print(f"Error analyzing grid {grid['grid_id']}: {e}")
            return self._default_crowd_data()
    
    def _get_nearby_places_activity(self, lat, lng):
        """Grid ke nearby places ka activity check karta hai"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 100,  # Small radius for grid-level analysis
                'key': self.maps_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                # Calculate activity score
                total_places = len(places)
                high_rated_places = len([p for p in places if p.get('rating', 0) > 4.0])
                busy_places = len([p for p in places if p.get('user_ratings_total', 0) > 100])
                
                activity_score = min((high_rated_places + busy_places) * 10, 100)
                
                return {
                    'total_places': total_places,
                    'activity_score': activity_score,
                    'high_rated_places': high_rated_places
                }
            else:
                return {'total_places': 0, 'activity_score': 0, 'high_rated_places': 0}
                
        except Exception as e:
            return {'total_places': 0, 'activity_score': 0, 'high_rated_places': 0}
    
    def _get_traffic_density(self, lat, lng):
        """Grid area ka traffic density check karta hai"""
        try:
            # Create nearby points for traffic analysis
            nearby_points = [
                (lat + 0.001, lng),      # North
                (lat - 0.001, lng),      # South
                (lat, lng + 0.001),      # East
                (lat, lng - 0.001)       # West
            ]
            
            traffic_levels = []
            
            for dest_lat, dest_lng in nearby_points:
                url = "https://maps.googleapis.com/maps/api/directions/json"
                params = {
                    'origin': f"{lat},{lng}",
                    'destination': f"{dest_lat},{dest_lng}",
                    'departure_time': 'now',
                    'traffic_model': 'best_guess',
                    'key': self.maps_key
                }
                
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('routes'):
                        route = data['routes'][0]
                        leg = route['legs'][0]
                        
                        duration_normal = leg['duration']['value']
                        duration_traffic = leg.get('duration_in_traffic', {}).get('value', duration_normal)
                        
                        traffic_ratio = duration_traffic / max(duration_normal, 1)
                        traffic_levels.append(traffic_ratio)
            
            avg_traffic = np.mean(traffic_levels) if traffic_levels else 1.0
            traffic_score = min((avg_traffic - 1.0) * 100, 100)
            
            return {'traffic_score': max(traffic_score, 0)}
            
        except Exception as e:
            return {'traffic_score': 0}
    
    def _estimate_grid_crowd(self, grid, places_data, traffic_data):
        """Grid ka final crowd estimate karta hai"""
        max_capacity = grid['max_capacity']
        zone_type = grid['zone_type']
        
        # Base crowd based on zone type and time
        current_hour = datetime.now().hour
        
        # Concert timing factors
        if 18 <= current_hour <= 23:  # Concert time
            base_factor = 0.8  # High crowd expected
        elif 16 <= current_hour <= 18:  # Pre-concert
            base_factor = 0.6
        elif 23 <= current_hour <= 24:  # Post-concert
            base_factor = 0.4
        else:
            base_factor = 0.2  # Off hours
        
        # Zone-specific multipliers
        zone_multipliers = {
            'main_stage': 1.0,
            'premium_zone': 0.8,
            'general_zone': 0.9,
            'outer_zone': 0.3
        }
        
        zone_factor = zone_multipliers.get(zone_type, 0.5)
        
        # External factors
        activity_factor = places_data['activity_score'] / 100
        traffic_factor = min(traffic_data['traffic_score'] / 50, 1.0)
        
        # Final calculation
        crowd_factor = (base_factor * zone_factor) + (activity_factor * 0.2) + (traffic_factor * 0.1)
        estimated_people = int(max_capacity * min(crowd_factor, 1.0))
        
        density_percentage = (estimated_people / max_capacity) * 100
        
        # Determine crowd level
        if density_percentage >= 90:
            crowd_level = 'CRITICAL'
        elif density_percentage >= 70:
            crowd_level = 'HIGH'
        elif density_percentage >= 50:
            crowd_level = 'MEDIUM'
        else:
            crowd_level = 'LOW'
        
        return {
            'estimated_people': estimated_people,
            'density_percentage': round(density_percentage, 1),
            'crowd_level': crowd_level,
            'nearby_activity': places_data['activity_score'],
            'traffic_factor': traffic_data['traffic_score']
        }
    
    def _default_crowd_data(self):
        """Default crowd data when API fails"""
        return {
            'estimated_people': 0,
            'density_percentage': 0,
            'crowd_level': 'UNKNOWN',
            'nearby_activity': 0,
            'traffic_factor': 0
        }
    
    def create_crowd_heatmap(self, crowd_data):
        """Interactive crowd density heatmap banata hai"""
        print("🗺️ Creating interactive crowd density map...")
        
        # Create base map
        center_lat = self.venue_config['center_lat']
        center_lng = self.venue_config['center_lng']
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=16,
            tiles='OpenStreetMap'
        )
        
        # Add venue boundary
        venue_circle = folium.Circle(
            location=[center_lat, center_lng],
            radius=self.venue_config['venue_radius'],
            color='black',
            weight=3,
            fill=False,
            popup=f"{self.venue_config['name']}<br>Capacity: {self.venue_config['capacity']:,}"
        )
        venue_circle.add_to(m)
        
        # Color mapping for crowd levels
        color_map = {
            'CRITICAL': '#FF0000',  # Red
            'HIGH': '#FF8C00',      # Orange
            'MEDIUM': '#FFD700',    # Yellow
            'LOW': '#32CD32',       # Green
            'UNKNOWN': '#808080'    # Gray
        }
        
        # Add grid squares with crowd data
        for data in crowd_data:
            # Find corresponding grid
            grid = next((g for g in self.grids if g['grid_id'] == data['grid_id']), None)
            if not grid:
                continue
            
            bounds = grid['bounds']
            color = color_map.get(data['crowd_level'], '#808080')
            
            # Create rectangle for grid
            rectangle = folium.Rectangle(
                bounds=[[bounds['south'], bounds['west']], 
                       [bounds['north'], bounds['east']]],
                color=color,
                weight=2,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                popup=f"""
                <b>Grid: {data['grid_id']}</b><br>
                Zone: {data['zone_type']}<br>
                People: {data['current_crowd']}/{data['max_capacity']}<br>
                Density: {data['crowd_density']}%<br>
                Level: {data['crowd_level']}<br>
                Time: {data['timestamp']}
                """
            )
            rectangle.add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <b>Crowd Density Levels</b><br>
        <i class="fa fa-square" style="color:#FF0000"></i> CRITICAL (90%+)<br>
        <i class="fa fa-square" style="color:#FF8C00"></i> HIGH (70-89%)<br>
        <i class="fa fa-square" style="color:#FFD700"></i> MEDIUM (50-69%)<br>
        <i class="fa fa-square" style="color:#32CD32"></i> LOW (<50%)<br>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        map_filename = f"coldplay_concert_crowd_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(map_filename)
        
        print(f"✅ Interactive map saved as: {map_filename}")
        return map_filename
    
    def generate_crowd_report(self, crowd_data):
        """Detailed crowd analysis report generate karta hai"""
        total_people = sum(data['current_crowd'] for data in crowd_data)
        total_capacity = sum(data['max_capacity'] for data in crowd_data)
        overall_density = (total_people / total_capacity) * 100 if total_capacity > 0 else 0
        
        # Count grids by crowd level
        level_counts = {}
        for data in crowd_data:
            level = data['crowd_level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Critical areas
        critical_grids = [data for data in crowd_data if data['crowd_level'] == 'CRITICAL']
        high_grids = [data for data in crowd_data if data['crowd_level'] == 'HIGH']
        
        report = f"""
🎵 COLDPLAY AHMEDABAD CONCERT - CROWD ANALYSIS REPORT
{'='*60}
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📍 Venue: {self.venue_config['name']}
👥 Total Capacity: {total_capacity:,} people
👥 Current Crowd: {total_people:,} people
📊 Overall Density: {overall_density:.1f}%

GRID ANALYSIS:
{'='*30}
Total Grids Monitored: {len(crowd_data)}
🔴 Critical Grids: {level_counts.get('CRITICAL', 0)}
🟠 High Density Grids: {level_counts.get('HIGH', 0)}
🟡 Medium Density Grids: {level_counts.get('MEDIUM', 0)}
🟢 Low Density Grids: {level_counts.get('LOW', 0)}

CRITICAL AREAS REQUIRING IMMEDIATE ATTENTION:
{'='*50}
"""
        
        if critical_grids:
            for grid in critical_grids:
                report += f"🚨 {grid['grid_id']}: {grid['current_crowd']}/{grid['max_capacity']} people ({grid['crowd_density']}%)\n"
        else:
            report += "✅ No critical areas detected\n"
        
        report += f"""
HIGH DENSITY AREAS TO MONITOR:
{'='*35}
"""
        
        if high_grids:
            for grid in high_grids:
                report += f"⚠️ {grid['grid_id']}: {grid['current_crowd']}/{grid['max_capacity']} people ({grid['crowd_density']}%)\n"
        else:
            report += "✅ No high density areas\n"
        
        print(report)
        
        # Save report to file
        report_filename = f"crowd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved as: {report_filename}")
        return report
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """Distance calculate karta hai (meters mein)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth radius in meters
        
        return c * r
    
    def run_full_analysis(self):
        """Complete concert crowd analysis run karta hai"""
        print(f"🎵 Starting Coldplay Concert Crowd Analysis...")
        print(f"📍 Venue: {self.venue_config['name']}")
        print(f"📊 Capacity: {self.venue_config['capacity']:,} people")
        print("="*60)
        
        # Step 1: Create venue grid
        print("1️⃣ Creating venue grid...")
        self.grids = self.create_venue_grid()
        
        # Step 2: Get real-time crowd data
        print("2️⃣ Fetching real-time crowd data...")
        crowd_data = self.get_real_time_crowd_data(self.grids)
        
        # Step 3: Create heatmap
        print("3️⃣ Creating crowd density heatmap...")
        map_file = self.create_crowd_heatmap(crowd_data)
        
        # Step 4: Generate report
        print("4️⃣ Generating crowd analysis report...")
        report = self.generate_crowd_report(crowd_data)
        
        print("="*60)
        print("✅ ANALYSIS COMPLETE!")
        print(f"🗺️ Interactive Map: {map_file}")
        print("🌐 Open the HTML file in your browser to view the crowd heatmap")
        
        return {
            'grids': self.grids,
            'crowd_data': crowd_data,
            'map_file': map_file,
            'report': report
        }

# Simple function to run analysis
def analyze_concert_crowd():
    """Bas yeh function call kar bhai!"""
    mapper = ConcertCrowdMapper()
    return mapper.run_full_analysis()

# Test function
if __name__ == "__main__":
    print("🎵 COLDPLAY AHMEDABAD CONCERT CROWD MAPPER")
    print("="*50)
    
    # Run full analysis
    results = analyze_concert_crowd()
    
    print("\n🎯 QUICK SUMMARY:")
    print(f"✅ Analyzed {len(results['grids'])} grid areas")
    print(f"🗺️ Interactive map created: {results['map_file']}")
    print("🌐 Open the HTML file to see the live crowd heatmap!")