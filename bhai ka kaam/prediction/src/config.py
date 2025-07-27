"""Configuration settings for the crowd management system."""

import os
from typing import Dict, Any

class Config:
    """Main configuration class."""
    
    # GCP Project Settings
    PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'project-dishti')
    REGION = os.getenv('GCP_REGION', 'us-central1')
    
    # Vertex AI Settings
    VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    VISION_MODEL_ENDPOINT = os.getenv('VISION_MODEL_ENDPOINT')
    FORECASTING_MODEL_ENDPOINT = os.getenv('FORECASTING_MODEL_ENDPOINT')
    
    # Pub/Sub Topics
    VIDEO_STREAM_TOPIC = 'video-stream-data'
    DEVICE_LOCATION_TOPIC = 'device-location-data'
    PREDICTION_TOPIC = 'bottleneck-predictions'
    
    # BigQuery Settings
    DATASET_ID = 'crowd_analytics'
    CROWD_DATA_TABLE = 'crowd_measurements'
    PREDICTIONS_TABLE = 'bottleneck_predictions'
    
    # Firestore Collections
    DEVICE_LOCATIONS_COLLECTION = 'device_locations'
    ZONES_COLLECTION = 'monitoring_zones'
    
    # Grid Configuration
    GRID_SIZE_METERS = 50  # Size of each monitoring grid in meters
    PREDICTION_WINDOW_MINUTES = 20  # How far ahead to predict
    
    # Thresholds
    BOTTLENECK_DENSITY_THRESHOLD = 4.0  # people per square meter
    ALERT_PROBABILITY_THRESHOLD = 0.7   # probability threshold for alerts
    
    # Maps API
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    @classmethod
    def get_pubsub_config(cls) -> Dict[str, Any]:
        """Get Pub/Sub configuration."""
        return {
            'project_id': cls.PROJECT_ID,
            'topics': {
                'video_stream': cls.VIDEO_STREAM_TOPIC,
                'device_location': cls.DEVICE_LOCATION_TOPIC,
                'predictions': cls.PREDICTION_TOPIC
            }
        }
    
    @classmethod
    def get_bigquery_config(cls) -> Dict[str, Any]:
        """Get BigQuery configuration."""
        return {
            'project_id': cls.PROJECT_ID,
            'dataset_id': cls.DATASET_ID,
            'tables': {
                'crowd_data': cls.CROWD_DATA_TABLE,
                'predictions': cls.PREDICTIONS_TABLE
            }
        }