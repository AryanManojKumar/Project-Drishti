"""Vertex AI Vision processing for crowd analysis."""

import cv2
import numpy as np
from typing import Dict, List, Tuple
from google.cloud import aiplatform
from google.cloud import pubsub_v1
import json
import logging
from datetime import datetime

from .config import Config

class CrowdVisionProcessor:
    """Processes video streams using Vertex AI Vision for crowd analysis."""
    
    def __init__(self):
        self.config = Config()
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            self.config.PROJECT_ID, 
            self.config.VIDEO_STREAM_TOPIC
        )
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.config.PROJECT_ID,
            location=self.config.VERTEX_AI_LOCATION
        )
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_people_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect people in a video frame using Vertex AI Vision.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            List of detected person objects with bounding boxes
        """
        # Convert frame to format suitable for Vertex AI
        # This would typically involve calling a deployed model endpoint
        
        # Placeholder for actual Vertex AI Vision API call
        # In practice, you'd use the Vision API or a custom trained model
        detections = self._mock_person_detection(frame)
        
        return detections
    
    def _mock_person_detection(self, frame: np.ndarray) -> List[Dict]:
        """Mock person detection for demonstration."""
        # This would be replaced with actual Vertex AI Vision calls
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
    
    def process_video_stream(self, video_source: str, zone_id: str):
        """
        Process a video stream and publish crowd metrics.
        
        Args:
            video_source: Path or URL to video source
            zone_id: Identifier for the monitoring zone
        """
        cap = cv2.VideoCapture(video_source)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect people in frame
                detections = self.detect_people_in_frame(frame)
                
                # Calculate crowd metrics
                metrics = self.calculate_crowd_metrics(detections, frame.shape[:2])
                metrics['zone_id'] = zone_id
                
                # Publish to Pub/Sub
                self._publish_metrics(metrics)
                
                self.logger.info(f"Processed frame for zone {zone_id}: "
                               f"{metrics['person_count']} people detected")
                
        except Exception as e:
            self.logger.error(f"Error processing video stream: {e}")
        finally:
            cap.release()
    
    def _publish_metrics(self, metrics: Dict):
        """Publish crowd metrics to Pub/Sub."""
        try:
            message_data = json.dumps(metrics).encode('utf-8')
            future = self.publisher.publish(self.topic_path, message_data)
            future.result()  # Wait for publish to complete
            
        except Exception as e:
            self.logger.error(f"Failed to publish metrics: {e}")
    
    def analyze_crowd_flow(self, current_centers: List[Tuple], 
                          previous_centers: List[Tuple]) -> Dict:
        """
        Analyze crowd flow between frames using optical flow principles.
        
        Args:
            current_centers: Current frame person centers
            previous_centers: Previous frame person centers
            
        Returns:
            Flow analysis results
        """
        if not previous_centers or not current_centers:
            return {'flow_vectors': [], 'average_velocity': 0}
        
        # Simple flow calculation (in practice, use more sophisticated tracking)
        flow_vectors = []
        
        # Match closest points between frames (simplified)
        for curr_point in current_centers:
            if previous_centers:
                closest_prev = min(previous_centers, 
                                 key=lambda p: np.linalg.norm(np.array(curr_point) - np.array(p)))
                
                flow_vector = (
                    curr_point[0] - closest_prev[0],
                    curr_point[1] - closest_prev[1]
                )
                flow_vectors.append(flow_vector)
        
        # Calculate average velocity
        if flow_vectors:
            avg_velocity = np.mean([np.linalg.norm(v) for v in flow_vectors])
        else:
            avg_velocity = 0
        
        return {
            'flow_vectors': flow_vectors,
            'average_velocity': float(avg_velocity),
            'flow_direction': self._calculate_dominant_direction(flow_vectors)
        }
    
    def _calculate_dominant_direction(self, flow_vectors: List[Tuple]) -> str:
        """Calculate the dominant flow direction."""
        if not flow_vectors:
            return 'stationary'
        
        # Calculate average flow direction
        avg_x = np.mean([v[0] for v in flow_vectors])
        avg_y = np.mean([v[1] for v in flow_vectors])
        
        # Determine dominant direction
        if abs(avg_x) > abs(avg_y):
            return 'right' if avg_x > 0 else 'left'
        else:
            return 'down' if avg_y > 0 else 'up'