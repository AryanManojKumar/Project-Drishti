#!/usr/bin/env python3
"""Initialize the crowd management system."""

import os
import sys
import logging
from google.cloud import bigquery
from google.cloud import firestore
from google.cloud import pubsub_v1

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import Config

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def initialize_bigquery_tables():
    """Initialize BigQuery tables with proper schemas."""
    logger = logging.getLogger(__name__)
    client = bigquery.Client(project=Config.PROJECT_ID)
    
    # Crowd measurements table schema
    crowd_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("zone_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("person_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("density", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("device_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("flow_velocity", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("flow_direction", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("hour_of_day", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("day_of_week", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("is_weekend", "BOOLEAN", mode="NULLABLE"),
    ]
    
    # Predictions table schema
    predictions_schema = [
        bigquery.SchemaField("prediction_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("forecast_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("zone_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("bottleneck_probability", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("predicted_density", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("alert_level", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("requires_intervention", "BOOLEAN", mode="REQUIRED"),
    ]
    
    # Create tables
    tables = [
        (Config.CROWD_DATA_TABLE, crowd_schema),
        (Config.PREDICTIONS_TABLE, predictions_schema)
    ]
    
    for table_name, schema in tables:
        table_id = f"{Config.PROJECT_ID}.{Config.DATASET_ID}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = client.create_table(table, exists_ok=True)
            logger.info(f"Created/verified table {table_id}")
        except Exception as e:
            logger.error(f"Error creating table {table_id}: {e}")

def initialize_firestore_collections():
    """Initialize Firestore collections with sample data."""
    logger = logging.getLogger(__name__)
    db = firestore.Client(project=Config.PROJECT_ID)
    
    # Sample monitoring zones
    sample_zones = [
        {
            'zone_id': 'entrance_main',
            'name': 'Main Entrance',
            'coordinates': {'lat': 40.7128, 'lng': -74.0060},
            'grid_bounds': {
                'north': 40.7130, 'south': 40.7126,
                'east': -74.0058, 'west': -74.0062
            },
            'capacity': 500,
            'alert_threshold': 400
        },
        {
            'zone_id': 'food_court',
            'name': 'Food Court Area',
            'coordinates': {'lat': 40.7125, 'lng': -74.0065},
            'grid_bounds': {
                'north': 40.7127, 'south': 40.7123,
                'east': -74.0063, 'west': -74.0067
            },
            'capacity': 300,
            'alert_threshold': 240
        }
    ]
    
    # Create zones collection
    zones_ref = db.collection(Config.ZONES_COLLECTION)
    for zone in sample_zones:
        try:
            zones_ref.document(zone['zone_id']).set(zone)
            logger.info(f"Created zone: {zone['zone_id']}")
        except Exception as e:
            logger.error(f"Error creating zone {zone['zone_id']}: {e}")

def verify_pubsub_topics():
    """Verify Pub/Sub topics exist."""
    logger = logging.getLogger(__name__)
    publisher = pubsub_v1.PublisherClient()
    
    topics = [
        Config.VIDEO_STREAM_TOPIC,
        Config.DEVICE_LOCATION_TOPIC,
        Config.PREDICTION_TOPIC
    ]
    
    for topic_name in topics:
        topic_path = publisher.topic_path(Config.PROJECT_ID, topic_name)
        try:
            publisher.get_topic(request={"topic": topic_path})
            logger.info(f"Verified topic: {topic_name}")
        except Exception as e:
            logger.warning(f"Topic {topic_name} may not exist: {e}")

def main():
    """Main initialization function."""
    logger = setup_logging()
    logger.info("Starting system initialization...")
    
    # Check environment variables
    required_env_vars = ['GCP_PROJECT_ID']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    try:
        # Initialize components
        logger.info("Initializing BigQuery tables...")
        initialize_bigquery_tables()
        
        logger.info("Initializing Firestore collections...")
        initialize_firestore_collections()
        
        logger.info("Verifying Pub/Sub topics...")
        verify_pubsub_topics()
        
        logger.info("System initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()