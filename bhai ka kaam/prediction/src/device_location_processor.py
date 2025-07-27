"""Device location data processing for crowd density estimation."""

import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud import pubsub_v1
import geohash2

from .config import Config

class DeviceLocationProcessor:
    """Processes device location data for crowd density estimation."""
    
    def __init__(self):
        self.config = Config()
        self.db = firestore.Client(project=self.config.PROJECT_ID)
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        self.topic_path = self.publisher.topic_path(
            self.config.PROJECT_ID,
            self.config.DEVICE_LOCATION_TOPIC
        )
        
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
        import hashlib
        return hashlib.sha256(device_id.encode()).hexdigest()[:16]
    
    def _assign_to_grid(self, lat: float, lon: float) -> str:
        """Assign coordinates to monitoring grid."""
        # Simple grid assignment based on lat/lon
        # In practice, you'd use a more sophisticated spatial indexing system
        grid_lat = round(lat * 1000) // 10  # ~100m grid
        grid_lon = round(lon * 1000) // 10
        return f"grid_{grid_lat}_{grid_lon}"
    
    def aggregate_device_counts(self, time_window_minutes: int = 5) -> Dict[str, int]:
        """
        Aggregate device counts per grid for recent time window.
        
        Args:
            time_window_minutes: Time window for aggregation
            
        Returns:
            Dictionary mapping grid_id to device count
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Query Firestore for recent device locations
        locations_ref = self.db.collection(self.config.DEVICE_LOCATIONS_COLLECTION)
        query = locations_ref.where('processed_at', '>=', cutoff_time.isoformat())
        
        grid_counts = {}
        
        try:
            docs = query.stream()
            for doc in docs:
                data = doc.to_dict()
                grid_id = data.get('grid_id')
                
                if grid_id:
                    grid_counts[grid_id] = grid_counts.get(grid_id, 0) + 1
            
            self.logger.info(f"Aggregated {len(grid_counts)} grids with device data")
            
        except Exception as e:
            self.logger.error(f"Error aggregating device counts: {e}")
        
        return grid_counts
    
    def store_location_data(self, processed_data: Dict):
        """Store processed location data in Firestore."""
        try:
            doc_ref = self.db.collection(self.config.DEVICE_LOCATIONS_COLLECTION).document()
            doc_ref.set(processed_data)
            
        except Exception as e:
            self.logger.error(f"Error storing location data: {e}")
    
    def publish_aggregated_counts(self, grid_counts: Dict[str, int]):
        """Publish aggregated device counts to Pub/Sub."""
        try:
            message_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'grid_counts': grid_counts,
                'data_type': 'device_aggregation'
            }
            
            message_json = json.dumps(message_data).encode('utf-8')
            future = self.publisher.publish(self.topic_path, message_json)
            future.result()
            
            self.logger.info(f"Published device counts for {len(grid_counts)} grids")
            
        except Exception as e:
            self.logger.error(f"Failed to publish device counts: {e}")
    
    def cleanup_old_data(self, retention_hours: int = 24):
        """Clean up old location data to maintain privacy and storage efficiency."""
        cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
        
        try:
            locations_ref = self.db.collection(self.config.DEVICE_LOCATIONS_COLLECTION)
            old_docs = locations_ref.where('processed_at', '<', cutoff_time.isoformat()).stream()
            
            batch = self.db.batch()
            count = 0
            
            for doc in old_docs:
                batch.delete(doc.reference)
                count += 1
                
                # Commit in batches of 500 (Firestore limit)
                if count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            if count % 500 != 0:
                batch.commit()
            
            self.logger.info(f"Cleaned up {count} old location records")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")