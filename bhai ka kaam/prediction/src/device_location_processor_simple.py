"""Device location data processing for crowd density estimation - Simplified version."""

import json
import logging
import os
from typing import Dict, List
from datetime import datetime, timedelta
import hashlib
import geohash2

# Correct import for pubsub
from google.cloud import pubsub_v1

class DeviceLocationProcessor:
    """Processes device location data for crowd density estimation."""
    
    def __init__(self):
        # Get project ID from environment variable
        self.project_id = os.getenv('GCP_PROJECT_ID', 'your-actual-project-id')
        
        # Initialize Pub/Sub client
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(
                self.project_id,
                "device-location-data"
            )
        except Exception as e:
            print(f"Error initializing Pub/Sub: {e}")
            self.publisher = None
            self.topic_path = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_device_location(self, device_data: Dict) -> Dict:
        """
        Process individual device location data.
        
        Args:
            device_data: Device location information
            
        Returns:
            Processed location data with grid assignment
        """
        lat = device_data.get('latitude')
        lon = device_data.get('longitude')
        timestamp = device_data.get('timestamp', datetime.utcnow().isoformat())
        device_id = device_data.get('device_id')
        
        if not all([lat, lon, device_id]):
            raise ValueError("Missing required location data")
        
        # Generate geohash for spatial indexing
        geohash = geohash2.encode(lat, lon, precision=7)  # ~150m precision
        
        # Assign to monitoring grid
        grid_id = self._assign_to_grid(lat, lon)
        
        processed_data = {
            'device_id': self._anonymize_device_id(device_id),
            'latitude': lat,
            'longitude': lon,
            'geohash': geohash,
            'grid_id': grid_id,
            'timestamp': timestamp,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        return processed_data
    
    def _anonymize_device_id(self, device_id: str) -> str:
        """Anonymize device ID for privacy."""
        return hashlib.sha256(device_id.encode()).hexdigest()[:16]
    
    def _assign_to_grid(self, lat: float, lon: float) -> str:
        """Assign coordinates to monitoring grid."""
        # Simple grid assignment based on lat/lon
        grid_lat = round(lat * 1000) // 10  # ~100m grid
        grid_lon = round(lon * 1000) // 10
        return f"grid_{grid_lat}_{grid_lon}"
    
    def test_functionality(self):
        """Test basic functionality without GCP dependencies."""
        print("Testing device location processing...")
        
        # Test with sample location data
        sample_data = {
            'device_id': 'test_device_123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'timestamp': '2025-01-23T10:00:00Z'
        }
        
        try:
            processed = self.process_device_location(sample_data)
            print(f"Successfully processed location data:")
            print(f"  Grid ID: {processed['grid_id']}")
            print(f"  Geohash: {processed['geohash']}")
            print(f"  Anonymized ID: {processed['device_id']}")
            return True
        except Exception as e:
            print(f"Error processing location data: {e}")
            return False

# Simple test function
if __name__ == "__main__":
    processor = DeviceLocationProcessor()
    processor.test_functionality()