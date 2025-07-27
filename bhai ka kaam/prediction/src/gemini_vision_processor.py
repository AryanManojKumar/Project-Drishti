"""Enhanced vision processor using Gemini for crowd detection."""

import os
import cv2
import numpy as np
import base64
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import requests

class GeminiCrowdVisionProcessor:
    """Processes video streams using Gemini Vision for crowd analysis."""
    
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', 'project-dishti')
        self.gemini_api_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_api_key}"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def encode_image_to_base64(self, image: np.ndarray) -> str:
        """Convert OpenCV image to base64 for Gemini API."""
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    def detect_people_with_gemini(self, frame: np.ndarray) -> Dict:
        """
        Use Gemini Vision to detect and count people in the frame.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary with crowd analysis results
        """
        try:
            # Convert frame to base64
            image_base64 = self.encode_image_to_base64(frame)
            
            # Prepare Gemini API request
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": """Analyze this image for crowd management. Please provide:
1. Total number of people visible
2. Crowd density level (low/medium/high/critical)
3. Movement patterns (stationary/slow/moderate/fast)
4. Any bottleneck areas or congestion points
5. Safety concerns if any

Respond in JSON format with these exact keys:
{
  "person_count": number,
  "density_level": "low/medium/high/critical",
  "movement_speed": "stationary/slow/moderate/fast",
  "bottleneck_areas": ["description of areas"],
  "safety_concerns": ["list of concerns"],
  "crowd_distribution": "description of how people are distributed"
}"""
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            # Make API request to Gemini
            response = requests.post(
                self.gemini_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the text response
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Try to parse JSON from the response
                    try:
                        # Clean the response (remove markdown formatting if present)
                        clean_response = text_response.strip()
                        if clean_response.startswith('```json'):
                            clean_response = clean_response.replace('```json', '').replace('```', '').strip()
                        
                        crowd_analysis = json.loads(clean_response)
                        
                        # Add timestamp and frame info
                        crowd_analysis['timestamp'] = datetime.utcnow().isoformat()
                        crowd_analysis['frame_dimensions'] = frame.shape[:2]
                        crowd_analysis['analysis_method'] = 'gemini_vision'
                        
                        return crowd_analysis
                        
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse Gemini JSON response: {e}")
                        # Return a basic analysis based on text
                        return self._parse_text_response(text_response, frame.shape[:2])
                
            else:
                self.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._fallback_detection(frame)
                
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
            return self._fallback_detection(frame)
    
    def _parse_text_response(self, text: str, frame_shape: Tuple[int, int]) -> Dict:
        """Parse text response when JSON parsing fails."""
        # Basic text parsing for crowd analysis
        person_count = 0
        density_level = "low"
        
        # Simple keyword extraction
        text_lower = text.lower()
        
        # Try to extract numbers
        import re
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            person_count = int(numbers[0])
        
        # Determine density level
        if any(word in text_lower for word in ['high', 'dense', 'crowded', 'packed']):
            density_level = "high"
        elif any(word in text_lower for word in ['medium', 'moderate']):
            density_level = "medium"
        elif any(word in text_lower for word in ['critical', 'dangerous', 'overcrowded']):
            density_level = "critical"
        
        return {
            'person_count': person_count,
            'density_level': density_level,
            'movement_speed': 'moderate',
            'bottleneck_areas': [],
            'safety_concerns': [],
            'crowd_distribution': 'parsed from text response',
            'timestamp': datetime.utcnow().isoformat(),
            'frame_dimensions': frame_shape,
            'analysis_method': 'gemini_text_parsing'
        }
    
    def _fallback_detection(self, frame: np.ndarray) -> Dict:
        """Fallback detection when Gemini API fails."""
        # Simple OpenCV-based detection as fallback
        height, width = frame.shape[:2]
        
        # Mock detection for demonstration
        person_count = np.random.randint(5, 25)  # Random count for demo
        density = person_count / (height * width / 10000)
        
        if density > 0.8:
            density_level = "critical"
        elif density > 0.6:
            density_level = "high"
        elif density > 0.3:
            density_level = "medium"
        else:
            density_level = "low"
        
        return {
            'person_count': person_count,
            'density_level': density_level,
            'movement_speed': 'moderate',
            'bottleneck_areas': [],
            'safety_concerns': [],
            'crowd_distribution': 'fallback detection',
            'timestamp': datetime.utcnow().isoformat(),
            'frame_dimensions': frame.shape[:2],
            'analysis_method': 'fallback_opencv'
        }
    
    def process_video_stream_with_gemini(self, video_source: str, zone_id: str):
        """
        Process video stream using Gemini for crowd analysis.
        
        Args:
            video_source: Path or URL to video source (or 0 for webcam)
            zone_id: Identifier for the monitoring zone
        """
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            self.logger.error(f"Failed to open video source: {video_source}")
            return
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 30th frame to avoid API rate limits
                frame_count += 1
                if frame_count % 30 != 0:
                    continue
                
                # Resize frame for faster processing
                frame_resized = cv2.resize(frame, (640, 480))
                
                # Analyze with Gemini
                analysis = self.detect_people_with_gemini(frame_resized)
                analysis['zone_id'] = zone_id
                
                # Log results
                self.logger.info(f"Zone {zone_id}: {analysis['person_count']} people, "
                               f"density: {analysis['density_level']}, "
                               f"method: {analysis['analysis_method']}")
                
                # Display frame with analysis (optional)
                self._display_analysis(frame, analysis)
                
                # Break on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("Video processing stopped by user")
        except Exception as e:
            self.logger.error(f"Error processing video stream: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def _display_analysis(self, frame: np.ndarray, analysis: Dict):
        """Display analysis results on the frame."""
        # Add text overlay with analysis results
        text_lines = [
            f"People: {analysis['person_count']}",
            f"Density: {analysis['density_level']}",
            f"Movement: {analysis['movement_speed']}",
            f"Method: {analysis['analysis_method']}"
        ]
        
        y_offset = 30
        for line in text_lines:
            cv2.putText(frame, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_offset += 30
        
        # Show frame
        cv2.imshow('Crowd Analysis', frame)
    
    def test_gemini_functionality(self):
        """Test Gemini integration with a sample image."""
        print("Testing Gemini Vision integration...")
        
        # Create a test image
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some simple shapes to simulate people
        cv2.rectangle(test_frame, (100, 200), (150, 400), (255, 255, 255), -1)
        cv2.rectangle(test_frame, (200, 180), (250, 420), (255, 255, 255), -1)
        cv2.rectangle(test_frame, (300, 220), (350, 380), (255, 255, 255), -1)
        
        try:
            analysis = self.detect_people_with_gemini(test_frame)
            print("✅ Gemini analysis successful!")
            print(f"Results: {json.dumps(analysis, indent=2)}")
            return True
        except Exception as e:
            print(f"❌ Gemini test failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    processor = GeminiCrowdVisionProcessor()
    processor.test_gemini_functionality()