"""Vertex AI Vision processing for crowd analysis - Simplified version."""

import numpy as np
import os
from typing import Dict, List, Tuple
import json
import logging
from datetime import datetime

class CrowdVisionProcessor:
    """Processes video streams for crowd analysis."""
    
    def __init__(self):
        # Get project ID from environment variable
        self.project_id = os.getenv('GCP_PROJECT_ID', 'your-actual-project-id')
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_people_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect people in a video frame.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            List of detected person objects with bounding boxes
        """
        # Mock detection for demonstration
        detections = self._mock_person_detection(frame)
        return detections
    
    def _mock_person_detection(self, frame: np.ndarray) -> List[Dict]:
        """Mock person detection for demonstration."""
        height, width = frame.shape[:2]
        
        # Simulate some detections
        mock_detections = [
            {
                'bbox': [100, 100, 150, 200],  # x1, y1, x2, y2
                'confidence': 0.85,
                'class': 'person'
            },
            {
                'bbox': [200, 120, 250, 220],
                'confidence': 0.92,
                'class': 'person'
            }
        ]
        
        return mock_detections
    
    def calculate_crowd_metrics(self, detections: List[Dict], 
                              frame_shape: Tuple[int, int]) -> Dict:
        """
        Calculate crowd density and flow metrics from detections.
        
        Args:
            detections: List of person detections
            frame_shape: (height, width) of the frame
            
        Returns:
            Dictionary with crowd metrics
        """
        person_count = len(detections)
        frame_area = frame_shape[0] * frame_shape[1]
        
        # Calculate density (people per unit area)
        density = person_count / (frame_area / 10000)  # normalize to reasonable scale
        
        # Calculate center points for flow analysis
        centers = []
        for detection in detections:
            bbox = detection['bbox']
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            centers.append((center_x, center_y))
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'person_count': person_count,
            'density': density,
            'centers': centers,
            'frame_dimensions': frame_shape
        }
        
        return metrics
    
    def test_functionality(self):
        """Test basic functionality without GCP dependencies."""
        print("Testing vision processing...")
        
        # Create a simple test frame (black image)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        try:
            # Test detection
            detections = self.detect_people_in_frame(test_frame)
            print(f"Successfully detected {len(detections)} people in test frame")
            
            # Test metrics calculation
            metrics = self.calculate_crowd_metrics(detections, test_frame.shape[:2])
            print(f"Calculated metrics:")
            print(f"  Person count: {metrics['person_count']}")
            print(f"  Density: {metrics['density']:.4f}")
            return True
        except Exception as e:
            print(f"Error in vision processing: {e}")
            return False

# Simple test function
if __name__ == "__main__":
    processor = CrowdVisionProcessor()
    processor.test_functionality()