#!/usr/bin/env python3
"""
Set up GCP infrastructure without Terraform using gcloud commands and Python APIs.
"""

import os
import sys
import subprocess
import logging
from google.cloud import pubsub_v1
from google.cloud import bigquery
from google.cloud import firestore
from google.cloud import storage

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_gcloud_command(command):
    """Run a gcloud command and return the result."""
    logger = logging.getLogger(__name__)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Command succeeded: {command}")
            return True, result.stdout
        else:
            logger.error(f"❌ Command failed: {command}")
            logger.error(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        logger.error(f"❌ Exception running command: {e}")
        return False, str(e)

def enable_apis(project_id):
    """Enable required GCP APIs."""
    logger = logging.getLogger(__name__)
    logger.info("Enabling required GCP APIs...")
    
    apis = [
        "aiplatform.googleapis.com",
        "pubsub.googleapis.com",
        "cloudfunctions.googleapis.com",
        "firestore.googleapis.com",
        "bigquery.googleapis.com",
        "storage.googleapis.com",
        "dataflow.googleapis.com",
        "run.googleapis.com",
        "maps-backend.googleapis.com"
    ]
    
    for api in apis:
        command = f"gcloud services enable {api} --project={project_id}"
        success, output = run_gcloud_command(command)
        if success:
            logger.info(f"✅ Enabled API: {api}")
        else:
            logger.warning(f"⚠️ Failed to enable API: {api}")

def create_pubsub_topics(project_id):
    """Create Pub/Sub topics."""
    logger = logging.getLogger(__name__)
    logger.info("Creating Pub/Sub topics...")
    
    publisher = pubsub_v1.PublisherClient()
    
    topics = [
        "video-stream-data",
        "device-location-data",
        "bottleneck-predictions"
    ]
    
    for topic_name in topics:
        topic_path = publisher.topic_path(project_id, topic_name)
        try:
            publisher.create_topic(request={"name": topic_path})
            logger.info(f"✅ Created topic: {topic_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"✅ Topic already exists: {topic_name}")
            else:
                logger.error(f"❌ Failed to create topic {topic_name}: {e}")

def create_bigquery_dataset_and_tables(project_id):
    """Create BigQuery dataset and tables."""
    logger = logging.getLogger(__name__)
    logger.info("Creating BigQuery dataset and tables...")
    
    client = bigquery.Client(project=project_id)
    
    # Create dataset
    dataset_id = "crowd_analytics"
    dataset_ref = client.dataset(dataset_id)
    
    try:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, exists_ok=True)
        logger.info(f"✅ Created dataset: {dataset_id}")
    except Exception as e:
        logger.error(f"❌ Failed to create dataset: {e}")
        return
    
    # Create crowd measurements table
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
    
    # Create predictions table
    predictions_schema = [
        bigquery.SchemaField("prediction_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("forecast_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("zone_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("bottleneck_probability", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("predicted_density", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("alert_level", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("requires_intervention", "BOOLEAN", mode="REQUIRED"),
    ]
    
    tables = [
        ("crowd_measurements", crowd_schema),
        ("bottleneck_predictions", predictions_schema)
    ]
    
    for table_name, schema in tables:
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = client.create_table(table, exists_ok=True)
            logger.info(f"✅ Created table: {table_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create table {table_name}: {e}")

def create_firestore_database(project_id):
    """Create Firestore database."""
    logger = logging.getLogger(__name__)
    logger.info("Setting up Firestore database...")
    
    # Use gcloud command to create Firestore database
    command = f"gcloud firestore databases create --region=us-central1 --project={project_id}"
    success, output = run_gcloud_command(command)
    
    if success or "already exists" in output.lower():
        logger.info("✅ Firestore database ready")
        
        # Initialize collections with sample data
        try:
            db = firestore.Client(project=project_id)
            
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
            zones_ref = db.collection('monitoring_zones')
            for zone in sample_zones:
                zones_ref.document(zone['zone_id']).set(zone)
                logger.info(f"✅ Created zone: {zone['zone_id']}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore collections: {e}")
    else:
        logger.error("❌ Failed to create Firestore database")

def create_storage_bucket(project_id):
    """Create Cloud Storage bucket for model artifacts."""
    logger = logging.getLogger(__name__)
    logger.info("Creating Cloud Storage bucket...")
    
    client = storage.Client(project=project_id)
    bucket_name = f"{project_id}-crowd-model-artifacts"
    
    try:
        bucket = client.bucket(bucket_name)
        bucket.location = "US-CENTRAL1"
        bucket = client.create_bucket(bucket, location="US-CENTRAL1")
        logger.info(f"✅ Created storage bucket: {bucket_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info(f"✅ Storage bucket already exists: {bucket_name}")
        else:
            logger.error(f"❌ Failed to create storage bucket: {e}")

def main():
    """Main setup function."""
    logger = setup_logging()
    
    # Get project ID from environment or user input
    project_id = os.getenv('GCP_PROJECT_ID')
    if not project_id:
        project_id = input("Enter your GCP Project ID: ").strip()
    
    if not project_id:
        logger.error("❌ Project ID is required")
        sys.exit(1)
    
    logger.info(f"Setting up GCP infrastructure for project: {project_id}")
    
    # Set the project for gcloud
    run_gcloud_command(f"gcloud config set project {project_id}")
    
    try:
        # Step 1: Enable APIs
        enable_apis(project_id)
        
        # Step 2: Create Pub/Sub topics
        create_pubsub_topics(project_id)
        
        # Step 3: Create BigQuery dataset and tables
        create_bigquery_dataset_and_tables(project_id)
        
        # Step 4: Create Firestore database
        create_firestore_database(project_id)
        
        # Step 5: Create Storage bucket
        create_storage_bucket(project_id)
        
        logger.info("🎉 GCP infrastructure setup completed successfully!")
        logger.info("You can now run the crowd management system.")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()