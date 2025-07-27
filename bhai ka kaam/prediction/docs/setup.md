# Setup Guide

## Prerequisites

### 1. GCP Account and Project
- Google Cloud Platform account with billing enabled
- New GCP project created for this system
- Project ID noted for configuration

### 2. Required APIs
The following GCP APIs must be enabled:
- Vertex AI API
- Pub/Sub API
- Cloud Functions API
- Firestore API
- BigQuery API
- Cloud Storage API
- Dataflow API
- Cloud Run API
- Maps API

### 3. Development Environment
- Python 3.8 or higher
- Google Cloud SDK installed and configured
- Terraform (for infrastructure deployment)
- Docker (optional, for containerization)

### 4. Authentication
Set up authentication using one of these methods:
```bash
# Option 1: Service Account Key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

# Option 2: gcloud auth (for development)
gcloud auth application-default login
```

## Installation Steps

### 1. Clone and Setup Python Environment
```bash
git clone <repository-url>
cd crowd-bottleneck-predictor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file:
```bash
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GOOGLE_MAPS_API_KEY=your-maps-api-key
VERTEX_AI_LOCATION=us-central1
```

### 3. Deploy Infrastructure with Terraform
```bash
cd deployment/terraform
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"
```

### 4. Initialize BigQuery Tables
```bash
python scripts/init_bigquery.py
```

### 5. Deploy Cloud Functions
```bash
gcloud functions deploy process-video-stream \
  --runtime python39 \
  --trigger-topic video-stream-data \
  --source ./functions/video-processor

gcloud functions deploy process-device-locations \
  --runtime python39 \
  --trigger-topic device-location-data \
  --source ./functions/location-processor
```

### 6. Train Initial Forecasting Model
```bash
python scripts/train_initial_model.py
```

## Configuration

### Monitoring Zones
Define your monitoring zones in Firestore:
```python
# Example zone configuration
zone_config = {
    'zone_id': 'entrance_main',
    'name': 'Main Entrance',
    'coordinates': {
        'lat': 40.7128,
        'lng': -74.0060
    },
    'grid_bounds': {
        'north': 40.7130,
        'south': 40.7126,
        'east': -74.0058,
        'west': -74.0062
    }
}
```

### Camera Setup
Configure video sources:
```python
camera_config = {
    'camera_id': 'cam_001',
    'zone_id': 'entrance_main',
    'stream_url': 'rtmp://camera-stream-url',
    'resolution': '1920x1080',
    'fps': 30
}
```

## Testing

### 1. Test Video Processing
```bash
python -m src.vision_processor --test-mode
```

### 2. Test Device Location Processing
```bash
python -m src.device_location_processor --simulate-data
```

### 3. Test Forecasting
```bash
python -m src.forecasting_model --predict-test
```

## Monitoring and Maintenance

### 1. Set up Monitoring
- Configure Cloud Monitoring alerts
- Set up log aggregation
- Monitor API quotas and costs

### 2. Data Retention
- Configure automatic cleanup of old location data
- Set BigQuery table expiration policies
- Monitor storage costs

### 3. Model Retraining
- Schedule periodic model retraining
- Monitor model performance metrics
- Update prediction thresholds as needed

## Security Considerations

### 1. Data Privacy
- Ensure device location data is anonymized
- Implement proper data retention policies
- Comply with local privacy regulations

### 2. Access Control
- Use IAM roles for service access
- Implement API authentication
- Secure video stream endpoints

### 3. Network Security
- Use VPC for internal communication
- Implement proper firewall rules
- Secure external API endpoints

## Troubleshooting

### Common Issues
1. **API Quota Exceeded**: Check quotas in GCP Console
2. **Authentication Errors**: Verify service account permissions
3. **Model Training Failures**: Check data quality and format
4. **Real-time Processing Delays**: Monitor Pub/Sub message backlogs

### Performance Optimization
1. **Batch Processing**: Use Dataflow for large-scale processing
2. **Caching**: Implement Redis for frequently accessed data
3. **Auto-scaling**: Configure Cloud Run auto-scaling
4. **Cost Optimization**: Use preemptible instances where appropriate