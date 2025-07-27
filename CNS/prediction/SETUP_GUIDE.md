# Complete Setup Guide (No Terraform Required)

This guide will help you set up the entire system without Terraform.

## Step 1: Install Google Cloud SDK

1. Download from: https://cloud.google.com/sdk/docs/install
2. Run the installer and follow the prompts
3. Restart your terminal/PowerShell

## Step 2: Set Up Your GCP Project

```powershell
# Initialize gcloud (this will open browser for authentication)
gcloud init

# Create a new project (or use existing one)
gcloud projects create your-project-id
gcloud config set project your-project-id
```

**Important**: Enable billing for your project at https://console.cloud.google.com/billing

## Step 3: Set Up Authentication

```powershell
gcloud auth application-default login
```

## Step 4: Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install all required packages
pip install -r requirements-basic.txt
```

## Step 5: Update Configuration

Edit the `.env` file with your actual project ID:
```
GCP_PROJECT_ID=your-actual-project-id
GCP_REGION=us-central1
VERTEX_AI_LOCATION=us-central1
```

## Step 6: Deploy GCP Infrastructure (No Terraform!)

Run the automated setup script:

```powershell
python scripts/setup_gcp_infrastructure.py
```

This script will:
- ✅ Enable all required GCP APIs
- ✅ Create Pub/Sub topics
- ✅ Create BigQuery dataset and tables
- ✅ Set up Firestore database
- ✅ Create Cloud Storage bucket
- ✅ Initialize sample monitoring zones

## Step 7: Initialize the System

```powershell
python scripts/init_system.py
```

## Step 8: Test the System

```powershell
python test_system.py
```

## Step 9: Run the Full System

### Option A: Run Individual Components

**Terminal 1 - Vision Processing:**
```powershell
python -c "
from src.vision_processor import CrowdVisionProcessor
processor = CrowdVisionProcessor()
processor.process_video_stream('0', 'entrance_main')
"
```

**Terminal 2 - Device Location Processing:**
```powershell
python -c "
from src.device_location_processor import DeviceLocationProcessor
import time
processor = DeviceLocationProcessor()
while True:
    counts = processor.aggregate_device_counts()
    processor.publish_aggregated_counts(counts)
    time.sleep(300)
"
```

**Terminal 3 - Forecasting:**
```powershell
python -c "
from src.forecasting_model import BottleneckForecaster
import time
forecaster = BottleneckForecaster()
while True:
    current_data = {'zones': {'entrance_main': {'person_count': 10, 'density': 2.0, 'device_count': 15}}}
    predictions = forecaster.predict_bottlenecks(current_data)
    print(f'Generated {len(predictions)} predictions')
    time.sleep(300)
"
```

### Option B: Test Individual Components

```powershell
# Test vision processing
python -m src.vision_processor_simple

# Test location processing  
python -m src.device_location_processor_simple
```

## Troubleshooting

### Authentication Errors
```powershell
gcloud auth application-default login
gcloud config set project your-project-id
```

### API Not Enabled
```powershell
gcloud services enable [service-name].googleapis.com
```

### Import Errors
```powershell
pip install [missing-package-name]
```

### Permission Errors
Make sure your account has the necessary permissions:
- Project Owner or Editor role
- Billing account linked to project

## What Gets Created

The setup script creates:
- **Pub/Sub Topics**: video-stream-data, device-location-data, bottleneck-predictions
- **BigQuery Dataset**: crowd_analytics with tables for measurements and predictions
- **Firestore Database**: With sample monitoring zones
- **Storage Bucket**: For model artifacts
- **Sample Data**: Monitoring zones for testing

## Next Steps

After successful setup:
1. Connect real video sources (cameras/drones)
2. Integrate mobile app for device location data
3. Train custom Vertex AI models
4. Set up monitoring and alerting
5. Build dashboard for visualization

No Terraform required! 🎉