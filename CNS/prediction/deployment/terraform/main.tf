# Terraform configuration for GCP infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "pubsub.googleapis.com",
    "cloudfunctions.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "dataflow.googleapis.com",
    "run.googleapis.com",
    "maps-backend.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# Pub/Sub Topics
resource "google_pubsub_topic" "video_stream" {
  name = "video-stream-data"
}

resource "google_pubsub_topic" "device_location" {
  name = "device-location-data"
}

resource "google_pubsub_topic" "predictions" {
  name = "bottleneck-predictions"
}

# BigQuery Dataset
resource "google_bigquery_dataset" "crowd_analytics" {
  dataset_id = "crowd_analytics"
  location   = var.region
  
  description = "Dataset for crowd analytics and predictions"
}

# BigQuery Tables
resource "google_bigquery_table" "crowd_data" {
  dataset_id = google_bigquery_dataset.crowd_analytics.dataset_id
  table_id   = "crowd_measurements"
  
  schema = jsonencode([
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "zone_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "person_count"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "density"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "device_count"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "flow_velocity"
      type = "FLOAT"
      mode = "NULLABLE"
    }
  ])
}

resource "google_bigquery_table" "predictions" {
  dataset_id = google_bigquery_dataset.crowd_analytics.dataset_id
  table_id   = "bottleneck_predictions"
  
  schema = jsonencode([
    {
      name = "prediction_time"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "zone_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "bottleneck_probability"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "alert_level"
      type = "STRING"
      mode = "REQUIRED"
    }
  ])
}

# Cloud Storage Bucket for model artifacts
resource "google_storage_bucket" "model_artifacts" {
  name     = "${var.project_id}-crowd-model-artifacts"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
}

# Firestore Database
resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Output important resource names
output "pubsub_topics" {
  value = {
    video_stream    = google_pubsub_topic.video_stream.name
    device_location = google_pubsub_topic.device_location.name
    predictions     = google_pubsub_topic.predictions.name
  }
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.crowd_analytics.dataset_id
}

output "storage_bucket" {
  value = google_storage_bucket.model_artifacts.name
}