# 🎯 Live Crowd Prediction System

An advanced AI-powered real-time crowd monitoring and prediction system that analyzes live video feeds and predicts crowd bottlenecks 15-20 minutes in advance. Built for public safety, event management, and proactive crowd control.

## 🚀 Key Features

### 🎥 Real-time Video Analysis
- **AI-Powered People Counting**: Uses Gemini AI for accurate crowd detection
- **Crowd Density Calculation**: Real-time density scoring (0-100 scale)
- **Flow Pattern Analysis**: Tracks crowd movement and velocity
- **Anomaly Detection**: Identifies unusual crowd behavior patterns

### 🗺️ Map-Based Analysis
- **Venue Layout Analysis**: Analyzes maps/floor plans for crowd capacity
- **Bottleneck Detection**: Identifies potential choke points
- **Risk Zone Mapping**: Highlights high-risk areas for crowd incidents
- **Emergency Route Planning**: Evaluates evacuation paths

### 🌍 Location Intelligence
- **Google Maps Integration**: Real-time location-based crowd factors
- **Traffic Pattern Analysis**: Correlates traffic with crowd density
- **Nearby Places Impact**: Analyzes influence of surrounding venues
- **Historical Data Integration**: Learns from past crowd patterns

### 🔍 Advanced Anomaly Detection
- **Multi-layered Detection**: Combines video, map, and location data
- **Stampede Risk Assessment**: Early warning for dangerous situations
- **Unusual Flow Detection**: Identifies abnormal crowd movements
- **Overcrowding Alerts**: Automatic threshold-based warnings

### 📊 Comprehensive UI
- **Real-time Dashboard**: Live monitoring with interactive charts
- **Historical Analysis**: Trend analysis and pattern recognition
- **Alert Management**: Centralized alert system with severity levels
- **Report Generation**: Detailed analysis reports for stakeholders

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Webcam or video input device
- Google API keys (Gemini AI, Google Maps)

### Installation

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd crowd-analysis-system
```

2. **Install Dependencies**:
```bash
# Basic requirements
pip install -r requirements-basic.txt

# For UI (optional)
pip install -r requirements-ui.txt
```

3. **Configure API Keys**:
```bash
# Edit .env file with your keys
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_MAPS_API_KEY=your_maps_key_here
```

### 🎯 Usage Options

#### Option 1: Live Crowd Prediction UI (NEW!)
```bash
streamlit run streamlit_crowd_ui.py
```
**Features:**
- 🎥 Live video feed analysis with AI
- 🔮 15-20 minute crowd predictions
- 🗺️ Real-time Maps API integration
- 🏢 Bangalore Exhibition Center test mode
- 📊 Zone-wise crowd monitoring

#### Option 2: Complete Analysis
```bash
python run_analysis.py
```
This runs the unified system with map analysis, video analysis, and anomaly detection.

#### Option 3: Live Prediction Test
```bash
python live_crowd_predictor.py
```
Test the live prediction system with webcam.

## 📋 System Components

### Core Analysis Modules
- **`run_analysis.py`** - Main analysis orchestrator
- **`main.py`** - Streamlit web UI
- **`map_crowd_analyzer.py`** - Complete crowd analysis engine
- **`crowd_predictor.py`** - Simple crowd prediction
- **`src/enhanced_crowd_analyzer.py`** - Advanced analysis with anomaly detection

### Supporting Modules
- **`src/vision_processor.py`** - Video processing
- **`src/maps_crowd_analyzer.py`** - Google Maps integration
- **`src/gemini_vision_processor.py`** - AI vision processing
- **`src/forecasting_model.py`** - Predictive modeling

## 🎮 How to Use

### 1. Complete Analysis
```bash
python run_analysis.py
```

**What it does:**
- Analyzes your map screenshot for crowd zones
- Records video from webcam for people counting
- Combines both analyses for comprehensive insights
- Detects anomalies and generates recommendations
- Saves detailed results to JSON file

### 2. Web Interface
```bash
streamlit run main.py
```

**Features:**
- **Dashboard**: Real-time metrics and charts
- **Live Analysis**: Video analysis with webcam
- **Map Analysis**: Upload and analyze venue layouts
- **Anomaly Detection**: Real-time anomaly monitoring
- **Historical Data**: Trend analysis and reporting

### 3. API Usage
```python
from map_crowd_analyzer import analyze_complete_crowd_situation

# Complete analysis
result = analyze_complete_crowd_situation(
    map_image_path="venue_map.jpg",
    video_source=0,  # webcam
    lat=28.6139,     # latitude
    lng=77.2090,     # longitude
    duration=30      # seconds
)

print(f"Alert Level: {result['alert_level']}")
print(f"Recommendations: {result['recommendations']}")
```

## 📊 Analysis Output

### Crowd Metrics
```json
{
  "overall_crowd_score": 65.5,
  "risk_level": "medium",
  "people_count": 23,
  "density_score": 6.8,
  "flow_velocity": 2.3,
  "alert_level": "caution"
}
```

### Anomaly Detection
```json
{
  "anomalies_detected": [
    {
      "type": "high_crowd_density",
      "severity": "warning",
      "description": "Crowd density exceeds normal levels",
      "recommendation": "Increase security presence"
    }
  ]
}
```

### Map Analysis
```json
{
  "venue_type": "Event venue with multiple zones",
  "density_zones": {
    "high_density": ["Main entrance", "Central stage area"],
    "bottlenecks": ["Exit gate 2", "Narrow corridor"]
  },
  "safety_score": 7.2,
  "emergency_routes": ["North exit", "South emergency door"]
}
```

## 🚨 Alert Levels

| Level | Score Range | Description | Action Required |
|-------|-------------|-------------|-----------------|
| **NORMAL** | 0-40 | Standard crowd levels | Routine monitoring |
| **CAUTION** | 41-60 | Elevated crowd density | Enhanced monitoring |
| **WARNING** | 61-80 | High crowd levels | Deploy additional security |
| **EMERGENCY** | 81-100 | Critical crowd density | Immediate intervention |

## 🔧 Configuration

### API Keys Setup
```bash
# .env file
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_MAPS_API_KEY=your_maps_key_here
```

### Analysis Parameters
```python
# Customize analysis settings
ANALYSIS_DURATION = 30  # seconds
ALERT_THRESHOLD = 70    # 0-100 scale
ANOMALY_SENSITIVITY = 2.5  # standard deviations
```

## 🎯 Use Cases

### Event Management
- **Concerts & Festivals**: Monitor crowd density in real-time
- **Sports Events**: Track crowd flow and identify bottlenecks
- **Conferences**: Ensure safe capacity limits

### Public Safety
- **Emergency Response**: Early warning for dangerous situations
- **Crowd Control**: Optimize security deployment
- **Evacuation Planning**: Assess emergency route effectiveness

### Retail & Commercial
- **Shopping Malls**: Monitor customer density
- **Restaurants**: Manage seating capacity
- **Transportation Hubs**: Track passenger flow

## 📈 Advanced Features

### Anomaly Detection Types
- **Overcrowding**: Density exceeds safe limits
- **Stampede Risk**: High velocity + high density
- **Bottleneck Formation**: Flow obstruction detection
- **Unusual Patterns**: Abnormal crowd behavior
- **Loitering Detection**: Stationary crowd identification

### Predictive Analytics
- **Trend Analysis**: Historical pattern recognition
- **Capacity Forecasting**: Predict future crowd levels
- **Risk Modeling**: Assess probability of incidents
- **Flow Optimization**: Suggest crowd management strategies

## 🛡️ Public Safety Integration

### Emergency Response
- **Automated Alerts**: Instant notifications for critical situations
- **Escalation Protocols**: Multi-level alert system
- **Emergency Contacts**: Integration with security teams
- **Incident Logging**: Detailed event documentation

### Compliance & Reporting
- **Safety Audits**: Generate compliance reports
- **Capacity Monitoring**: Track venue capacity limits
- **Historical Analysis**: Long-term safety trends
- **Regulatory Reporting**: Export data for authorities

## 📱 Mobile & Cloud Ready

### Deployment Options
- **Local Installation**: Run on local hardware
- **Cloud Deployment**: Scale with cloud infrastructure
- **Mobile Access**: Web UI works on mobile devices
- **API Integration**: Embed in existing systems

## 🔍 Testing & Validation

### Test Your Setup
```bash
# Quick system test
python test_system.py

# Map analysis test
python test_map_analysis.py

# Complete analysis test
python run_analysis.py
```

### Sample Data
- Uses your screenshot: `src/Screenshot 2025-07-23 064906.png`
- Webcam for real-time analysis
- Sample coordinates for location testing

## 📚 Documentation

- **Setup Guide**: `SETUP_GUIDE.md`
- **API Documentation**: `docs/setup.md`
- **Deployment Guide**: `deployment/terraform/`
- **Configuration Examples**: `.env` file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create GitHub issues for bugs/features
- **Documentation**: Check `docs/` directory
- **Examples**: See `test_*.py` files for usage examples

## 🙏 Acknowledgments

- **Google Gemini AI**: Advanced computer vision capabilities
- **Google Maps API**: Location-based intelligence
- **OpenCV**: Video processing foundation
- **Streamlit**: Interactive web interface
- **Public Safety Community**: Requirements and feedback

---

**⚡ Ready to start? Run `python run_analysis.py` and see your crowd analysis in action!**