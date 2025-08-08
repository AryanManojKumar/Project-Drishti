# 🎥 Live Video Anomaly Detection System

A real-time video analysis system powered by **Gemini 2.0 Flash** that detects anomalies in large-scale events and generates comprehensive incident reports.

## 🚀 Features

### Real-Time Anomaly Detection
- **Live video feed analysis** using Gemini 2.0 Flash Vision
- **12 comprehensive anomaly categories** for large-scale events
- **5-level severity assessment** (Low → Emergency)
- **Confidence scoring** for each detection
- **Location identification** within video frames

### Comprehensive Incident Reporting
Each anomaly generates a structured report with:
- **Situation Overview** - Brief incident description
- **Severity Assessment** - Risk level justification  
- **Hazard Analysis** - Potential consequences
- **Immediate Actions** - Required response steps
- **Equipment Required** - Necessary resources
- **De-escalation Strategy** - Conflict resolution approach
- **Resolution Method** - Complete solution steps

### Web Dashboard
- **Real-time alerts** with WebSocket updates
- **Emergency modal** for critical incidents (Level 4+)
- **Statistics tracking** and category breakdown
- **Alert history** with detailed summaries
- **Start/stop monitoring** controls

## 📋 Anomaly Categories

The system detects 12 types of anomalies common in large-scale events:

1. **Crowd Control** - Overcrowding, bottlenecks, uncontrolled movement
2. **Security Threat** - Suspicious packages, unauthorized items, weapons
3. **Medical Emergency** - Collapsed persons, injuries, medical distress
4. **Fire Hazard** - Smoke, flames, fire safety violations
5. **Structural Damage** - Damaged barriers, unsafe conditions
6. **Weather Emergency** - Severe weather impact, flooding
7. **Vehicle Incident** - Unauthorized vehicles, accidents, blocked routes
8. **Equipment Failure** - Stage/sound equipment issues
9. **Unauthorized Access** - Restricted area breaches
10. **Violence/Aggression** - Fights, confrontations
11. **Stampede Risk** - Panic indicators, dangerous crowd dynamics
12. **Evacuation Needed** - Situations requiring immediate evacuation

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenCV-compatible camera or video source
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone and install dependencies:**
```bash
git clone <repository-url>
cd video-anomaly-detection
pip install -r requirements.txt
```

2. **Configure API key:**
```bash
# Edit .env file with your Gemini API key
# Set GEMINI_API_KEY=your_actual_api_key
```

3. **Test the system:**
```bash
python main.py
```

## 🎯 Usage

### Command Line Interface
```bash
# Start the integrated system (recommended)
python main.py

# Or start specific components
python main.py --web             # Web interface only
python main.py --camera          # Camera monitoring only
python main.py --video video.mp4 # Analyze video file
```

### Web Dashboard
```bash
# Start the web interface
python web_interface.py

# Open browser to http://localhost:5000
```

### Programmatic Usage
```python
from video_anomaly_detector import VideoAnomalyDetector

# Initialize detector
detector = VideoAnomalyDetector("your_api_key")

# Start monitoring (0 = default camera, or path to video file)
detector.start_live_monitoring(0)

# Get statistics
stats = detector.get_statistics()
print(f"Total anomalies: {stats['total_anomalies']}")
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
ANALYSIS_INTERVAL=3              # Seconds between analyses
FRAME_QUALITY=85                 # JPEG quality (1-100)
HIGH_PRIORITY_THRESHOLD=3        # Severity level for high priority
CONFIDENCE_THRESHOLD=0.7         # Minimum confidence for alerts
```

### Event-Specific Settings
```bash
EVENT_TYPE=concert               # concert, festival, sports, etc.
VENUE_CAPACITY=10000            # Expected attendance
SECURITY_LEVEL=high             # low, medium, high, maximum
```

## 📊 Output Formats

### JSON Alert Structure
```json
{
  "id": "anomaly_1642789123",
  "timestamp": "2024-01-21T15:30:45",
  "category": "Crowd Control",
  "severity": {
    "level": 3,
    "label": "HIGH",
    "color": "#fd7e14"
  },
  "confidence": "87.5%",
  "location": "Main entrance area",
  "summary": {
    "situation_overview": "Large crowd bottleneck forming at main entrance",
    "severity_assessment": "High risk of crowd crush if not addressed",
    "hazard_analysis": "Potential for injuries, panic, evacuation delays",
    "immediate_actions": [
      "Deploy crowd control barriers",
      "Add security personnel to area",
      "Open additional entry points"
    ],
    "equipment_required": [
      "Portable barriers",
      "Megaphones",
      "Additional security staff"
    ],
    "de_escalation_strategy": "Calm crowd with clear announcements, organize orderly flow",
    "resolution_method": "Implement multiple entry lanes, continuous monitoring"
  },
  "requires_immediate_action": true
}
```

### File Outputs
- `anomaly_alerts.json` - Latest alerts for UI consumption
- `anomaly_reports_YYYYMMDD_HHMMSS.json` - Saved session reports

## 🔧 Advanced Features

### Custom Video Sources
```python
# Use external camera
detector.start_live_monitoring(1)  # Camera index 1

# Use video file
detector.start_live_monitoring("path/to/video.mp4")

# Use IP camera stream
detector.start_live_monitoring("rtsp://camera-ip:554/stream")
```

### Real-time Integration
```python
# Override the _send_to_ui method for custom integrations
class CustomDetector(VideoAnomalyDetector):
    def _send_to_ui(self, ui_report):
        # Send to your API/database
        requests.post('https://your-api.com/alerts', json=ui_report)
        
        # Send to Slack/Discord
        send_slack_alert(ui_report)
        
        # Trigger emergency protocols
        if ui_report['severity']['level'] >= 4:
            trigger_emergency_response(ui_report)
```

## 🚨 Emergency Response Integration

For critical alerts (Level 4+), the system can integrate with:
- **Emergency Services** - Automatic 911/emergency dispatch
- **Security Teams** - Real-time notifications
- **Event Management** - Incident command systems
- **Public Address** - Automated announcements
- **Social Media** - Status updates

## 📈 Performance Optimization

### For High-Volume Events
```python
# Adjust analysis frequency
detector.analysis_interval = 5  # Analyze every 5 seconds

# Lower frame quality for faster processing
Config.FRAME_QUALITY = 70

# Use multiple camera feeds
detectors = [
    VideoAnomalyDetector(api_key, "Main Stage"),
    VideoAnomalyDetector(api_key, "Entrance"),
    VideoAnomalyDetector(api_key, "VIP Area")
]
```

## 🔒 Security Considerations

- **API Key Protection** - Store in environment variables
- **Network Security** - Use HTTPS for web dashboard
- **Data Privacy** - Video frames are not stored permanently
- **Access Control** - Implement authentication for dashboard
- **Audit Logging** - Track all anomaly detections

## 🐛 Troubleshooting

### Common Issues

**Camera not detected:**
```bash
# List available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
```

**API quota exceeded:**
- Check your Gemini API usage limits
- Increase `analysis_interval` to reduce API calls

**False positives:**
- Adjust `CONFIDENCE_THRESHOLD` in config
- Fine-tune prompts for your specific event type

**Performance issues:**
- Reduce `FRAME_QUALITY` setting
- Increase `ANALYSIS_INTERVAL`
- Use more powerful hardware

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the example usage scripts

---

**⚠️ Important:** This system is designed to assist human security personnel, not replace them. Always have trained staff monitoring the alerts and making final decisions on emergency responses.