"""
Local Preprocessing Module
Bhai, yeh module local computer vision processing karta hai before sending to Gemini
Objects, faces, aur text detect karta hai locally using OpenCV
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import base64
from collections import defaultdict

# Try to import face detection
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("face_recognition not available - using OpenCV face detection")

# Try to import OCR
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("pytesseract not available - OCR disabled")

class LocalPreprocessor:
    """
    Local preprocessing for crowd analysis
    Reduces Gemini API calls by processing locally first
    """
    
    def __init__(self):
        # Load OpenCV models
        self.setup_opencv_models()
        
        # Preprocessing counters
        self.processing_stats = {
            'total_frames_processed': 0,
            'api_calls_saved': 0,
            'local_detections': 0,
            'processing_time_saved': 0
        }
        
        # Detection thresholds
        self.thresholds = {
            'person_confidence': 0.5,
            'face_confidence': 0.7,
            'motion_threshold': 10,
            'crowd_density_threshold': 5,
            'send_to_gemini_threshold': 3  # Send to Gemini only if significant activity
        }
        
        # Cache for similar frames
        self.frame_cache = {}
        self.last_significant_frame = None
        self.last_significant_time = 0
        
    def setup_opencv_models(self):
        """OpenCV models setup karta hai"""
        try:
            # YOLO for object detection
            self.setup_yolo_model()
            
            # Haar cascades for face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
            
            # Background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
            
            print("✅ OpenCV models loaded successfully")
            
        except Exception as e:
            print(f"OpenCV model setup error: {e}")
            self.models_available = False
    
    def setup_yolo_model(self):
        """YOLO model setup - lightweight version"""
        try:
            # Using OpenCV's DNN module with pre-trained COCO model
            # Download these files: yolov3.weights, yolov3.cfg, coco.names
            # For now, using basic detection without external files
            self.yolo_available = False
            print("YOLO model not configured - using basic detection")
            
        except Exception as e:
            print(f"YOLO setup error: {e}")
            self.yolo_available = False
    
    def preprocess_frame(self, frame: np.ndarray, camera_id: str = "default") -> Dict:
        """
        Complete frame preprocessing before sending to Gemini
        Returns: processed data and decision whether to send to Gemini
        """
        start_time = time.time()
        
        try:
            # Basic frame analysis
            frame_analysis = self.analyze_frame_locally(frame)
            
            # Motion detection
            motion_data = self.detect_motion(frame)
            
            # Object detection
            object_data = self.detect_objects_locally(frame)
            
            # Face detection
            face_data = self.detect_faces_locally(frame)
            
            # Text detection (if available)
            text_data = self.detect_text_locally(frame) if OCR_AVAILABLE else {}
            
            # Combine all local analysis
            local_analysis = {
                'timestamp': datetime.now().isoformat(),
                'camera_id': camera_id,
                'frame_analysis': frame_analysis,
                'motion_detection': motion_data,
                'object_detection': object_data,
                'face_detection': face_data,
                'text_detection': text_data,
                'processing_time': time.time() - start_time
            }
            
            # Decision: Should we send this to Gemini?
            gemini_decision = self.should_send_to_gemini(local_analysis, frame)
            
            # Update stats
            self.update_processing_stats(local_analysis, gemini_decision)
            
            return {
                'local_analysis': local_analysis,
                'send_to_gemini': gemini_decision['should_send'],
                'gemini_prompt': gemini_decision.get('optimized_prompt', ''),
                'preprocessed_image': gemini_decision.get('optimized_image', None),
                'confidence_score': gemini_decision.get('confidence', 0.5)
            }
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return {
                'local_analysis': {'error': str(e)},
                'send_to_gemini': True,  # Fallback to Gemini on error
                'gemini_prompt': '',
                'preprocessed_image': frame,
                'confidence_score': 0.1
            }
    
    def analyze_frame_locally(self, frame: np.ndarray) -> Dict:
        """Basic frame analysis using OpenCV"""
        try:
            # Frame properties
            height, width = frame.shape[:2]
            
            # Color analysis
            avg_color = np.mean(frame, axis=(0, 1))
            
            # Brightness analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Contrast analysis
            contrast = np.std(gray)
            
            # Edge detection for activity level
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (height * width)
            
            return {
                'dimensions': {'width': width, 'height': height},
                'brightness': float(brightness),
                'contrast': float(contrast),
                'edge_density': float(edge_density),
                'avg_color': [float(c) for c in avg_color],
                'quality_score': self.calculate_image_quality(brightness, contrast, edge_density)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_motion(self, frame: np.ndarray) -> Dict:
        """Motion detection using background subtraction"""
        try:
            # Apply background subtractor
            fg_mask = self.bg_subtractor.apply(frame)
            
            # Calculate motion level
            motion_pixels = np.sum(fg_mask > 0)
            total_pixels = frame.shape[0] * frame.shape[1]
            motion_percentage = (motion_pixels / total_pixels) * 100
            
            # Find contours for moving objects
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter significant contours
            significant_contours = [c for c in contours if cv2.contourArea(c) > 500]
            
            return {
                'motion_percentage': float(motion_percentage),
                'motion_level': self.categorize_motion_level(motion_percentage),
                'moving_objects_count': len(significant_contours),
                'has_significant_motion': motion_percentage > self.thresholds['motion_threshold']
            }
            
        except Exception as e:
            return {'error': str(e), 'motion_percentage': 0}
    
    def detect_objects_locally(self, frame: np.ndarray) -> Dict:
        """Local object detection using OpenCV"""
        try:
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Simple person detection using contours and shape analysis
            persons_detected = self.detect_person_shapes(gray)
            
            # Vehicle detection (basic)
            vehicles_detected = self.detect_vehicle_shapes(gray)
            
            # Color-based object detection
            colored_objects = self.detect_colored_objects(hsv)
            
            return {
                'persons_estimated': persons_detected,
                'vehicles_estimated': vehicles_detected,
                'colored_objects': colored_objects,
                'total_objects': persons_detected + vehicles_detected + len(colored_objects),
                'crowd_density_estimate': self.estimate_crowd_density(persons_detected, frame.shape)
            }
            
        except Exception as e:
            return {'error': str(e), 'persons_estimated': 0}
    
    def detect_person_shapes(self, gray_frame: np.ndarray) -> int:
        """Detect person-like shapes using contours"""
        try:
            # Edge detection
            edges = cv2.Canny(gray_frame, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            person_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Reasonable person size range
                    # Check aspect ratio
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # Person-like aspect ratio (taller than wide)
                    if 1.5 < aspect_ratio < 4.0:
                        person_count += 1
            
            return person_count
            
        except Exception as e:
            return 0
    
    def detect_vehicle_shapes(self, gray_frame: np.ndarray) -> int:
        """Detect vehicle-like shapes"""
        try:
            # Simple vehicle detection based on rectangular shapes
            edges = cv2.Canny(gray_frame, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            vehicle_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 5000 < area < 100000:  # Vehicle size range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Vehicle-like aspect ratio (wider than tall)
                    if 1.2 < aspect_ratio < 3.0:
                        vehicle_count += 1
            
            return vehicle_count
            
        except Exception:
            return 0
    
    def detect_colored_objects(self, hsv_frame: np.ndarray) -> List[Dict]:
        """Detect objects by color"""
        try:
            colored_objects = []
            
            # Define color ranges (HSV)
            color_ranges = {
                'red': [(0, 50, 50), (10, 255, 255)],
                'blue': [(100, 50, 50), (130, 255, 255)],
                'green': [(40, 50, 50), (80, 255, 255)],
                'yellow': [(20, 50, 50), (40, 255, 255)]
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:  # Minimum object size
                        colored_objects.append({
                            'color': color_name,
                            'area': float(area),
                            'bbox': cv2.boundingRect(contour)
                        })
            
            return colored_objects
            
        except Exception:
            return []
    
    def detect_faces_locally(self, frame: np.ndarray) -> Dict:
        """Face detection using OpenCV"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # OpenCV face detection
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            face_data = {
                'faces_detected': len(faces),
                'face_locations': [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} 
                                 for x, y, w, h in faces],
                'detection_method': 'opencv_haar'
            }
            
            # Enhanced face detection if face_recognition available
            if FACE_RECOGNITION_AVAILABLE and len(faces) > 0:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_data['enhanced_faces'] = len(face_locations)
                    face_data['detection_method'] = 'face_recognition'
                except Exception:
                    pass
            
            return face_data
            
        except Exception as e:
            return {'error': str(e), 'faces_detected': 0}
    
    def detect_text_locally(self, frame: np.ndarray) -> Dict:
        """Text detection using OCR"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Preprocess for better OCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Extract text
            text = pytesseract.image_to_string(gray, config='--psm 6')
            
            # Get text details
            text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Filter confident text detections
            confident_text = []
            for i, conf in enumerate(text_data['conf']):
                if int(conf) > 50:  # Confidence threshold
                    word = text_data['text'][i].strip()
                    if word:
                        confident_text.append({
                            'text': word,
                            'confidence': int(conf),
                            'bbox': {
                                'x': text_data['left'][i],
                                'y': text_data['top'][i],
                                'w': text_data['width'][i],
                                'h': text_data['height'][i]
                            }
                        })
            
            return {
                'text_detected': text.strip(),
                'text_regions': confident_text,
                'has_readable_text': len(confident_text) > 0
            }
            
        except Exception as e:
            return {'error': str(e), 'text_detected': ''}
    
    def should_send_to_gemini(self, local_analysis: Dict, frame: np.ndarray) -> Dict:
        """Decide whether to send frame to Gemini based on local analysis"""
        try:
            score = 0
            reasons = []
            
            # Check motion activity
            motion_data = local_analysis.get('motion_detection', {})
            if motion_data.get('has_significant_motion', False):
                score += 2
                reasons.append("Significant motion detected")
            
            # Check crowd density
            object_data = local_analysis.get('object_detection', {})
            person_count = object_data.get('persons_estimated', 0)
            if person_count >= self.thresholds['crowd_density_threshold']:
                score += 3
                reasons.append(f"High crowd density: {person_count} people")
            elif person_count > 0:
                score += 1
                reasons.append(f"People detected: {person_count}")
            
            # Check face detection
            face_data = local_analysis.get('face_detection', {})
            if face_data.get('faces_detected', 0) > 0:
                score += 1
                reasons.append(f"Faces detected: {face_data['faces_detected']}")
            
            # Check text presence
            text_data = local_analysis.get('text_detection', {})
            if text_data.get('has_readable_text', False):
                score += 1
                reasons.append("Readable text detected")
            
            # Check image quality
            frame_data = local_analysis.get('frame_analysis', {})
            quality_score = frame_data.get('quality_score', 0.5)
            if quality_score < 0.3:
                score -= 1
                reasons.append("Poor image quality")
            
            # Time-based throttling
            current_time = time.time()
            if current_time - self.last_significant_time < 30:  # 30 seconds throttle
                score -= 2
                reasons.append("Recent analysis - throttling")
            
            # Decision logic
            should_send = score >= self.thresholds['send_to_gemini_threshold']
            
            result = {
                'should_send': should_send,
                'confidence': min(score / 10.0, 1.0),
                'score': score,
                'reasons': reasons
            }
            
            if should_send:
                # Generate optimized prompt based on local analysis
                result['optimized_prompt'] = self.generate_optimized_prompt(local_analysis)
                result['optimized_image'] = self.optimize_image_for_gemini(frame, local_analysis)
                self.last_significant_time = current_time
            
            return result
            
        except Exception as e:
            return {
                'should_send': True,  # Default to sending on error
                'confidence': 0.1,
                'error': str(e)
            }
    
    def generate_optimized_prompt(self, local_analysis: Dict) -> str:
        """Generate optimized prompt based on local preprocessing results"""
        try:
            prompt_parts = [
                "You are analyzing a crowd management scene. Local preprocessing has detected:"
            ]
            
            # Add motion information
            motion_data = local_analysis.get('motion_detection', {})
            if motion_data.get('has_significant_motion'):
                prompt_parts.append(f"- Motion Level: {motion_data.get('motion_level', 'unknown')}")
                prompt_parts.append(f"- Motion Percentage: {motion_data.get('motion_percentage', 0):.1f}%")
            
            # Add object information
            object_data = local_analysis.get('object_detection', {})
            person_count = object_data.get('persons_estimated', 0)
            if person_count > 0:
                prompt_parts.append(f"- Estimated People Count: {person_count}")
                prompt_parts.append(f"- Crowd Density: {object_data.get('crowd_density_estimate', 'unknown')}")
            
            # Add face information
            face_data = local_analysis.get('face_detection', {})
            if face_data.get('faces_detected', 0) > 0:
                prompt_parts.append(f"- Faces Detected: {face_data['faces_detected']}")
            
            # Add text information
            text_data = local_analysis.get('text_detection', {})
            if text_data.get('text_detected'):
                prompt_parts.append(f"- Text Found: '{text_data['text_detected']}'")
            
            # Add analysis request
            prompt_parts.extend([
                "",
                "Please verify and enhance this analysis with:",
                "1. Accurate people count and crowd density (1-10)",
                "2. Movement patterns and flow direction",
                "3. Safety risks and bottleneck indicators",
                "4. Alert level (normal/caution/warning/critical)",
                "",
                "Respond in JSON format with detailed crowd analysis."
            ])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            return f"Analyze this crowd scene for people count, density, and safety risks. Local preprocessing error: {e}"
    
    def optimize_image_for_gemini(self, frame: np.ndarray, local_analysis: Dict) -> np.ndarray:
        """Optimize image before sending to Gemini"""
        try:
            # Start with original frame
            optimized = frame.copy()
            
            # Resize for faster processing
            height, width = optimized.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = 800
                new_height = int(height * scale)
                optimized = cv2.resize(optimized, (new_width, new_height))
            
            # Enhance based on local analysis
            frame_data = local_analysis.get('frame_analysis', {})
            brightness = frame_data.get('brightness', 128)
            contrast = frame_data.get('contrast', 50)
            
            # Adjust brightness/contrast if needed
            if brightness < 80:  # Too dark
                optimized = cv2.convertScaleAbs(optimized, alpha=1.2, beta=20)
            elif brightness > 200:  # Too bright
                optimized = cv2.convertScaleAbs(optimized, alpha=0.8, beta=-20)
            
            if contrast < 30:  # Low contrast
                optimized = cv2.convertScaleAbs(optimized, alpha=1.3, beta=0)
            
            return optimized
            
        except Exception:
            return frame
    
    def categorize_motion_level(self, motion_percentage: float) -> str:
        """Categorize motion level"""
        if motion_percentage < 2:
            return 'minimal'
        elif motion_percentage < 10:
            return 'low'
        elif motion_percentage < 25:
            return 'moderate'
        elif motion_percentage < 50:
            return 'high'
        else:
            return 'very_high'
    
    def estimate_crowd_density(self, person_count: int, frame_shape: Tuple) -> str:
        """Estimate crowd density category"""
        height, width = frame_shape[:2]
        area = height * width
        density = person_count / (area / 10000)  # People per 100x100 pixel area
        
        if density < 0.5:
            return 'sparse'
        elif density < 1.0:
            return 'light'
        elif density < 2.0:
            return 'moderate'
        elif density < 4.0:
            return 'dense'
        else:
            return 'very_dense'
    
    def calculate_image_quality(self, brightness: float, contrast: float, edge_density: float) -> float:
        """Calculate overall image quality score"""
        # Normalize values
        brightness_score = 1.0 - abs(brightness - 128) / 128  # Optimal at 128
        contrast_score = min(contrast / 100, 1.0)  # Higher contrast is better
        edge_score = min(edge_density * 10, 1.0)  # More edges indicate detail
        
        # Weighted average
        quality = (brightness_score * 0.3 + contrast_score * 0.4 + edge_score * 0.3)
        return max(0.0, min(1.0, quality))
    
    def update_processing_stats(self, local_analysis: Dict, gemini_decision: Dict):
        """Update preprocessing statistics"""
        self.processing_stats['total_frames_processed'] += 1
        
        if not gemini_decision.get('should_send', True):
            self.processing_stats['api_calls_saved'] += 1
        
        if local_analysis.get('object_detection', {}).get('persons_estimated', 0) > 0:
            self.processing_stats['local_detections'] += 1
        
        processing_time = local_analysis.get('processing_time', 0)
        self.processing_stats['processing_time_saved'] += processing_time
    
    def get_preprocessing_stats(self) -> Dict:
        """Get preprocessing statistics"""
        total_processed = self.processing_stats['total_frames_processed']
        if total_processed == 0:
            return self.processing_stats
        
        stats = self.processing_stats.copy()
        stats['api_call_reduction_percentage'] = (
            (stats['api_calls_saved'] / total_processed) * 100
        )
        stats['local_detection_rate'] = (
            (stats['local_detections'] / total_processed) * 100
        )
        
        return stats
    
    def reset_stats(self):
        """Reset preprocessing statistics"""
        self.processing_stats = {
            'total_frames_processed': 0,
            'api_calls_saved': 0,
            'local_detections': 0,
            'processing_time_saved': 0
        }

# Global preprocessor instance
local_preprocessor = LocalPreprocessor()

def preprocess_frame_for_analysis(frame: np.ndarray, camera_id: str = "default") -> Dict:
    """
    Main function to preprocess frame before sending to Gemini
    Returns: preprocessing results and decision
    """
    return local_preprocessor.preprocess_frame(frame, camera_id)

def get_preprocessing_statistics() -> Dict:
    """Get current preprocessing statistics"""
    return local_preprocessor.get_preprocessing_stats()
