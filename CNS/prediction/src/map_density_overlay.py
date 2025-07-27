"""
Map Density Overlay System
Bhai, yeh file map par color-coded density zones dikhayega
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import json
import base64
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import requests
from datetime import datetime

class MapDensityOverlay:
    def __init__(self):
        self.gemini_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
        
        # Color mapping for density levels
        self.density_colors = {
            'low': (0, 255, 0),      # Green
            'medium': (255, 255, 0),  # Yellow
            'high': (255, 165, 0),    # Orange
            'critical': (255, 0, 0)   # Red
        }
        
        # Transparency levels
        self.overlay_alpha = 0.6

    def create_density_overlay(self, 
                             map_image_path: str,
                             crowd_analysis: Dict,
                             video_analysis: Dict = None) -> str:
        """
        Create density overlay on map image
        
        Args:
            map_image_path: Path to original map image
            crowd_analysis: Analysis results from map analysis
            video_analysis: Optional video analysis results
            
        Returns:
            Path to overlay image
        """
        try:
            # Load original map
            original_map = cv2.imread(map_image_path)
            if original_map is None:
                raise ValueError(f"Could not load map image: {map_image_path}")
            
            height, width = original_map.shape[:2]
            
            # Create overlay image
            overlay = original_map.copy()
            
            # Get density zones from analysis
            density_zones = self._extract_density_zones(crowd_analysis, video_analysis)
            
            # Create zone coordinates
            zone_coordinates = self._generate_zone_coordinates(density_zones, width, height)
            
            # Draw density zones
            overlay_with_zones = self._draw_density_zones(overlay, zone_coordinates)
            
            # Add legend
            final_image = self._add_density_legend(overlay_with_zones)
            
            # Add analysis info
            final_image = self._add_analysis_info(final_image, crowd_analysis, video_analysis)
            
            # Save overlay image
            output_path = f"density_overlay_{int(datetime.now().timestamp())}.png"
            cv2.imwrite(output_path, final_image)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating density overlay: {e}")
            return map_image_path  # Return original if overlay fails

    def _extract_density_zones(self, crowd_analysis: Dict, video_analysis: Dict = None) -> Dict:
        """Extract density information from analysis results"""
        
        zones = {
            'high_density_areas': [],
            'medium_density_areas': [],
            'low_density_areas': [],
            'critical_areas': []
        }
        
        # From map analysis
        if 'map_analysis' in crowd_analysis:
            map_data = crowd_analysis['map_analysis']
            
            # Extract density zones
            if 'density_zones' in map_data:
                density_zones = map_data['density_zones']
                zones['high_density_areas'].extend(density_zones.get('high_density', []))
                zones['medium_density_areas'].extend(density_zones.get('medium_density', []))
                zones['low_density_areas'].extend(density_zones.get('low_density', []))
            
            # High-risk areas become critical
            if 'risk_assessment' in map_data:
                risk_areas = map_data['risk_assessment'].get('high_risk_areas', [])
                zones['critical_areas'].extend(risk_areas)
            
            # Bottlenecks are high density
            if 'flow_analysis' in map_data:
                bottlenecks = map_data['flow_analysis'].get('bottlenecks', [])
                zones['high_density_areas'].extend(bottlenecks)
        
        # From video analysis
        if video_analysis:
            video_density = video_analysis.get('density_score', 0)
            people_count = video_analysis.get('people_count', 0)
            
            # Add video-based zones
            if video_density >= 80:
                zones['critical_areas'].append(f"Video feed area (Density: {video_density})")
            elif video_density >= 60:
                zones['high_density_areas'].append(f"Video feed area (Density: {video_density})")
            elif video_density >= 40:
                zones['medium_density_areas'].append(f"Video feed area (Density: {video_density})")
            else:
                zones['low_density_areas'].append(f"Video feed area (Density: {video_density})")
        
        return zones

    def _generate_zone_coordinates(self, density_zones: Dict, width: int, height: int) -> Dict:
        """Generate coordinates for density zones on the map"""
        
        zone_coords = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Divide map into grid for zone placement
        grid_rows = 6
        grid_cols = 8
        cell_width = width // grid_cols
        cell_height = height // grid_rows
        
        # Assign zones to grid cells based on analysis
        zone_assignments = self._assign_zones_to_grid(density_zones, grid_rows, grid_cols)
        
        # Convert grid assignments to pixel coordinates
        for zone_type, cells in zone_assignments.items():
            for row, col in cells:
                x1 = col * cell_width
                y1 = row * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                
                zone_coords[zone_type].append({
                    'coords': (x1, y1, x2, y2),
                    'center': (x1 + cell_width//2, y1 + cell_height//2)
                })
        
        return zone_coords

    def _assign_zones_to_grid(self, density_zones: Dict, rows: int, cols: int) -> Dict:
        """Assign density zones to grid cells"""
        
        assignments = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Strategic zone placement based on typical venue layouts
        
        # Critical zones (entrances, exits, narrow areas)
        critical_areas = len(density_zones.get('critical_areas', []))
        if critical_areas > 0:
            # Main entrance (bottom center)
            assignments['critical'].extend([(rows-1, cols//2-1), (rows-1, cols//2)])
            # Side exits
            assignments['critical'].extend([(rows//2, 0), (rows//2, cols-1)])
        
        # High density zones (main areas, popular spots)
        high_areas = len(density_zones.get('high_density_areas', []))
        if high_areas > 0:
            # Central areas
            center_row, center_col = rows//2, cols//2
            assignments['high'].extend([
                (center_row-1, center_col-1), (center_row-1, center_col),
                (center_row, center_col-1), (center_row, center_col)
            ])
            # Near entrances
            assignments['high'].extend([(rows-2, cols//2-1), (rows-2, cols//2)])
        
        # Medium density zones (transition areas)
        medium_areas = len(density_zones.get('medium_density_areas', []))
        if medium_areas > 0:
            # Around high density areas
            assignments['medium'].extend([
                (1, 1), (1, cols-2), (rows-3, 1), (rows-3, cols-2),
                (rows//2-1, 1), (rows//2+1, cols-2)
            ])
        
        # Low density zones (outer areas, less popular spots)
        low_areas = len(density_zones.get('low_density_areas', []))
        if low_areas > 0:
            # Corners and edges
            assignments['low'].extend([
                (0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1),
                (0, cols//2), (rows//2, cols//4), (rows//2, 3*cols//4)
            ])
        
        # Remove duplicates and ensure within bounds
        for zone_type in assignments:
            assignments[zone_type] = list(set(assignments[zone_type]))
            assignments[zone_type] = [(r, c) for r, c in assignments[zone_type] 
                                    if 0 <= r < rows and 0 <= c < cols]
        
        return assignments

    def _draw_density_zones(self, image: np.ndarray, zone_coordinates: Dict) -> np.ndarray:
        """Draw colored density zones on the image"""
        
        overlay = image.copy()
        
        # Create separate overlay for transparency
        color_overlay = np.zeros_like(image)
        
        # Draw zones in order: low -> medium -> high -> critical
        zone_order = ['low', 'medium', 'high', 'critical']
        
        for zone_type in zone_order:
            if zone_type in zone_coordinates:
                color = self.density_colors.get(zone_type, (128, 128, 128))
                
                for zone in zone_coordinates[zone_type]:
                    x1, y1, x2, y2 = zone['coords']
                    
                    # Draw filled rectangle
                    cv2.rectangle(color_overlay, (x1, y1), (x2, y2), color, -1)
                    
                    # Draw border
                    border_color = tuple(max(0, c - 50) for c in color)
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), border_color, 2)
        
        # Blend overlay with original image
        result = cv2.addWeighted(overlay, 1 - self.overlay_alpha, color_overlay, self.overlay_alpha, 0)
        
        return result

    def _add_density_legend(self, image: np.ndarray) -> np.ndarray:
        """Add density legend to the image"""
        
        height, width = image.shape[:2]
        
        # Legend dimensions
        legend_width = 200
        legend_height = 150
        legend_x = width - legend_width - 20
        legend_y = 20
        
        # Draw legend background
        cv2.rectangle(image, 
                     (legend_x, legend_y), 
                     (legend_x + legend_width, legend_y + legend_height),
                     (255, 255, 255), -1)
        
        cv2.rectangle(image, 
                     (legend_x, legend_y), 
                     (legend_x + legend_width, legend_y + legend_height),
                     (0, 0, 0), 2)
        
        # Legend title
        cv2.putText(image, "Crowd Density", 
                   (legend_x + 10, legend_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Legend items
        legend_items = [
            ("Critical", self.density_colors['critical']),
            ("High", self.density_colors['high']),
            ("Medium", self.density_colors['medium']),
            ("Low", self.density_colors['low'])
        ]
        
        y_offset = 45
        for label, color in legend_items:
            # Color box
            cv2.rectangle(image,
                         (legend_x + 10, legend_y + y_offset),
                         (legend_x + 30, legend_y + y_offset + 15),
                         color, -1)
            
            cv2.rectangle(image,
                         (legend_x + 10, legend_y + y_offset),
                         (legend_x + 30, legend_y + y_offset + 15),
                         (0, 0, 0), 1)
            
            # Label
            cv2.putText(image, label,
                       (legend_x + 40, legend_y + y_offset + 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            y_offset += 25
        
        return image

    def _add_analysis_info(self, image: np.ndarray, crowd_analysis: Dict, video_analysis: Dict = None) -> np.ndarray:
        """Add analysis information to the image"""
        
        height, width = image.shape[:2]
        
        # Info box dimensions
        info_width = 300
        info_height = 120
        info_x = 20
        info_y = 20
        
        # Draw info background
        cv2.rectangle(image,
                     (info_x, info_y),
                     (info_x + info_width, info_y + info_height),
                     (255, 255, 255), -1)
        
        cv2.rectangle(image,
                     (info_x, info_y),
                     (info_x + info_width, info_y + info_height),
                     (0, 0, 0), 2)
        
        # Title
        cv2.putText(image, "Analysis Results",
                   (info_x + 10, info_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Analysis info
        y_offset = 45
        
        # Alert level
        alert_level = crowd_analysis.get('alert_level', 'normal').upper()
        alert_color = (0, 255, 0) if alert_level == 'NORMAL' else (0, 165, 255) if alert_level == 'CAUTION' else (0, 255, 255) if alert_level == 'WARNING' else (0, 0, 255)
        
        cv2.putText(image, f"Alert: {alert_level}",
                   (info_x + 10, info_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, alert_color, 2)
        y_offset += 20
        
        # Map analysis info
        if 'map_analysis' in crowd_analysis:
            map_data = crowd_analysis['map_analysis']
            
            if 'density_rating' in map_data:
                cv2.putText(image, f"Map Density: {map_data['density_rating']}/10",
                           (info_x + 10, info_y + y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                y_offset += 15
            
            if 'safety_score' in map_data:
                cv2.putText(image, f"Safety Score: {map_data['safety_score']}/10",
                           (info_x + 10, info_y + y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                y_offset += 15
        
        # Video analysis info
        if video_analysis:
            cv2.putText(image, f"People Count: {video_analysis.get('people_count', 0)}",
                       (info_x + 10, info_y + y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            y_offset += 15
            
            cv2.putText(image, f"Video Density: {video_analysis.get('density_score', 0)}/100",
                       (info_x + 10, info_y + y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(image, timestamp,
                   (info_x + 10, info_y + info_height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (128, 128, 128), 1)
        
        return image

    def create_interactive_density_map(self, 
                                     map_image_path: str,
                                     crowd_analysis: Dict,
                                     video_analysis: Dict = None) -> Dict:
        """
        Create interactive density map data for web display
        
        Returns:
            Dictionary with map data and zone information
        """
        try:
            # Load original map
            with open(map_image_path, 'rb') as f:
                map_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get density zones
            density_zones = self._extract_density_zones(crowd_analysis, video_analysis)
            
            # Create interactive map data
            interactive_data = {
                'map_image': map_data,
                'density_zones': density_zones,
                'analysis_info': {
                    'alert_level': crowd_analysis.get('alert_level', 'normal'),
                    'timestamp': datetime.now().isoformat(),
                    'map_analysis': crowd_analysis.get('map_analysis', {}),
                    'video_analysis': video_analysis or {}
                },
                'zone_colors': self.density_colors,
                'recommendations': crowd_analysis.get('recommendations', [])
            }
            
            return interactive_data
            
        except Exception as e:
            print(f"Error creating interactive density map: {e}")
            return {}

# Helper function for easy usage
def create_map_overlay(map_image_path: str, 
                      crowd_analysis: Dict,
                      video_analysis: Dict = None) -> str:
    """
    Easy function to create density overlay
    
    Args:
        map_image_path: Path to map image
        crowd_analysis: Analysis results
        video_analysis: Optional video analysis
        
    Returns:
        Path to overlay image
    """
    overlay_creator = MapDensityOverlay()
    return overlay_creator.create_density_overlay(map_image_path, crowd_analysis, video_analysis)

def create_interactive_map_data(map_image_path: str,
                               crowd_analysis: Dict,
                               video_analysis: Dict = None) -> Dict:
    """
    Easy function to create interactive map data
    
    Args:
        map_image_path: Path to map image
        crowd_analysis: Analysis results
        video_analysis: Optional video analysis
        
    Returns:
        Interactive map data
    """
    overlay_creator = MapDensityOverlay()
    return overlay_creator.create_interactive_density_map(map_image_path, crowd_analysis, video_analysis)

# Test function
if __name__ == "__main__":
    # Test with sample data
    sample_analysis = {
        'alert_level': 'warning',
        'map_analysis': {
            'density_rating': 7,
            'safety_score': 6,
            'density_zones': {
                'high_density': ['Main entrance', 'Central stage area'],
                'medium_density': ['Side corridors', 'Food court'],
                'low_density': ['Outer areas', 'Parking zones']
            },
            'risk_assessment': {
                'high_risk_areas': ['Narrow exit', 'Bottleneck near stage']
            }
        }
    }
    
    sample_video = {
        'people_count': 45,
        'density_score': 72,
        'alert_status': 'warning'
    }
    
    map_path = "src/Screenshot 2025-07-23 064906.png"
    
    if os.path.exists(map_path):
        print("Creating density overlay...")
        overlay_path = create_map_overlay(map_path, sample_analysis, sample_video)
        print(f"Overlay created: {overlay_path}")
        
        print("Creating interactive map data...")
        interactive_data = create_interactive_map_data(map_path, sample_analysis, sample_video)
        print("Interactive data created successfully!")
    else:
        print(f"Map file not found: {map_path}")