import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_api_key_here')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    
    # Video Analysis Settings
    ANALYSIS_INTERVAL = int(os.getenv('ANALYSIS_INTERVAL', '3'))  # seconds
    FRAME_QUALITY = int(os.getenv('FRAME_QUALITY', '85'))  # JPEG quality
    
    # Alert Thresholds
    HIGH_PRIORITY_THRESHOLD = int(os.getenv('HIGH_PRIORITY_THRESHOLD', '3'))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
    
    # Output Settings
    SAVE_ALERTS_TO_FILE = os.getenv('SAVE_ALERTS_TO_FILE', 'true').lower() == 'true'
    API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:3000/api/anomalies')
    
    # Event-Specific Settings
    EVENT_TYPE = os.getenv('EVENT_TYPE', 'large_scale_event')  # concert, festival, sports, etc.
    VENUE_CAPACITY = int(os.getenv('VENUE_CAPACITY', '10000'))
    SECURITY_LEVEL = os.getenv('SECURITY_LEVEL', 'high')  # low, medium, high, maximum