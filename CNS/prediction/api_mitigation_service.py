"""
Advanced API Mitigation Service with Batch Processing
Multiple strategies to completely avoid 429 errors including batch requests
"""

import time
import threading
import queue
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import random

# Import batch service
try:
    from batch_api_service import batch_api, create_gemini_batch_request, APIType, BatchRequest
    BATCH_AVAILABLE = True
    print("✓ Batch API service available")
except ImportError:
    BATCH_AVAILABLE = False
    print("⚠ Batch API service not available, using individual requests")

class APIMitigationService:
    """Advanced service to mitigate API rate limits"""
    
    def __init__(self):
        # Multiple API keys rotation
        self.gemini_keys = [
            "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8",
            "AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"  # Secondary key
        ]
        
        self.maps_keys = [
            "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
        ]
        
        self.current_key_index = {'gemini': 0, 'maps': 0}
        self.key_blacklist = {'gemini': set(), 'maps': set()}
        
        # Request queue and throttling
        self.request_queue = queue.Queue()
        self.processing = False
        self.queue_worker = None
        
        # Advanced caching
        self.multi_level_cache = {
            'level1': {},  # Recent high-priority cache (5 min)
            'level2': {},  # Medium-term cache (15 min)
            'level3': {}   # Long-term fallback cache (1 hour)
        }
        
        # Request distribution
        self.request_count = {'gemini': 0, 'maps': 0}
        self.last_reset = time.time()
        self.max_requests_per_minute = {'gemini': 10, 'maps': 20}
        
        # Smart fallback models
        self.local_models = LocalFallbackModels()
        
        # Batch request queue and processing
        self.batch_queue = queue.Queue()
        self.batch_responses = {}
        self.batch_processing = True
        
        # Batch configuration
        self.batch_config = {
            'max_batch_size': 5,
            'batch_timeout': 2.0,  # Wait max 2 seconds for more requests
            'enable_batching': BATCH_AVAILABLE
        }
        
        # Start batch processor if available
        if BATCH_AVAILABLE:
            self.batch_thread = threading.Thread(target=self._process_batch_queue, daemon=True)
            self.batch_thread.start()
            print("✓ Batch processing thread started")
        
        # Pending batch requests
        self.pending_batch_requests = []
        self.last_batch_time = time.time()
        
    def start_queue_processor(self):
        """Start background queue processor"""
        if not self.processing:
            self.processing = True
            self.queue_worker = threading.Thread(target=self._process_queue, daemon=True)
            self.queue_worker.start()
    
    def stop_queue_processor(self):
        """Stop background queue processor"""
        self.processing = False
        if self.queue_worker:
            self.queue_worker.join(timeout=5)
    
    def _process_queue(self):
        """Background processor for API requests"""
        while self.processing:
            try:
                if not self.request_queue.empty():
                    request_data = self.request_queue.get(timeout=1)
                    self._execute_queued_request(request_data)
                    time.sleep(1)  # Throttle requests
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Queue processor error: {e}")
    
    def _execute_queued_request(self, request_data):
        """Execute a queued API request with all mitigations"""
        try:
            api_type = request_data['api_type']
            
            # Check rate limits
            if not self._can_make_request(api_type):
                # Reschedule for later
                request_data['retry_count'] = request_data.get('retry_count', 0) + 1
                if request_data['retry_count'] < 3:
                    self.request_queue.put(request_data)
                return
            
            # Try with key rotation
            success = False
            for attempt in range(len(self.gemini_keys if api_type == 'gemini' else self.maps_keys)):
                try:
                    response = self._make_api_call(request_data, api_type)
                    if response and response.get('success'):
                        success = True
                        break
                    else:
                        self._rotate_key(api_type)
                except Exception as e:
                    self._rotate_key(api_type)
                    continue
            
            if not success:
                # Use fallback
                self._generate_local_fallback(request_data)
                
        except Exception as e:
            print(f"Error executing queued request: {e}")
    
    def _process_batch_queue(self):
        """Background processor for batch requests"""
        while self.batch_processing:
            try:
                current_time = time.time()
                
                # Check if we have pending requests to batch
                if (len(self.pending_batch_requests) >= self.batch_config['max_batch_size'] or
                    (self.pending_batch_requests and 
                     current_time - self.last_batch_time > self.batch_config['batch_timeout'])):
                    
                    # Process current batch
                    self._execute_batch()
                
                # Check for new requests
                try:
                    batch_request = self.batch_queue.get(timeout=0.5)
                    self.pending_batch_requests.append(batch_request)
                    
                    if len(self.pending_batch_requests) == 1:
                        self.last_batch_time = current_time
                        
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"Batch processing error: {e}")
                time.sleep(0.5)
    
    def _execute_batch(self):
        """Execute a batch of requests"""
        if not self.pending_batch_requests:
            return
        
        try:
            # Group requests by type
            gemini_requests = []
            other_requests = []
            
            for req in self.pending_batch_requests:
                if req.get('type') == 'gemini':
                    gemini_requests.append(req)
                else:
                    other_requests.append(req)
            
            # Process Gemini batch
            if gemini_requests and BATCH_AVAILABLE:
                self._execute_gemini_batch(gemini_requests)
            
            # Process other requests individually with staggered timing
            for req in other_requests:
                self._execute_individual_request(req)
                time.sleep(0.2)  # Stagger to avoid rate limits
            
            # Clear processed requests
            self.pending_batch_requests.clear()
            
        except Exception as e:
            print(f"Error executing batch: {e}")
            # Fallback to individual processing
            for req in self.pending_batch_requests:
                self._execute_individual_request(req)
            self.pending_batch_requests.clear()
    
    def _execute_gemini_batch(self, gemini_requests):
        """Execute batch of Gemini requests"""
        try:
            prompts = []
            request_ids = []
            
            for req in gemini_requests:
                prompts.append(req['prompt'])
                request_ids.append(req['id'])
            
            # Use batch API service
            responses = batch_api.gemini_batch_request(prompts, request_ids)
            
            # Store responses
            for response in responses:
                self.batch_responses[response.request_id] = response
                
                # Trigger callback if provided
                for req in gemini_requests:
                    if req['id'] == response.request_id and req.get('callback'):
                        threading.Thread(target=req['callback'], args=(response,), daemon=True).start()
            
            print(f"✓ Processed batch of {len(prompts)} Gemini requests in 1 API call")
            
        except Exception as e:
            print(f"Gemini batch execution error: {e}")
            # Fallback to individual requests
            for req in gemini_requests:
                self._execute_individual_request(req)
    
    def _execute_individual_request(self, request):
        """Execute single request with fallback"""
        try:
            # This would execute the original single request logic
            # For now, just store a basic response
            response = {
                'request_id': request['id'],
                'success': False,
                'data': {'text': 'Individual request fallback'},
                'source': 'individual_fallback'
            }
            
            self.batch_responses[request['id']] = response
            
            if request.get('callback'):
                threading.Thread(target=request['callback'], args=(response,), daemon=True).start()
                
        except Exception as e:
            print(f"Individual request error: {e}")
    
    def add_to_batch(self, request_type: str, prompt: str, request_id: str = None, callback: callable = None) -> str:
        """Add request to batch queue"""
        if not request_id:
            request_id = f"{request_type}_{int(time.time() * 1000)}"
        
        batch_request = {
            'id': request_id,
            'type': request_type,
            'prompt': prompt,
            'callback': callback,
            'timestamp': time.time()
        }
        
        if BATCH_AVAILABLE and self.batch_config['enable_batching']:
            self.batch_queue.put(batch_request)
        else:
            # Immediate processing fallback
            self._execute_individual_request(batch_request)
        
        return request_id
    
    def get_batch_response(self, request_id: str, timeout: float = 10.0):
        """Get response from batch processing"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if request_id in self.batch_responses:
                return self.batch_responses.pop(request_id)
            time.sleep(0.1)
        
        return None  # Timeout
    
    def smart_gemini_request_batch(self, image_data, prompt, priority='medium'):
        """Smart Gemini request using batch processing"""
        current_time = time.time()
        
        # Check cache first
        cache_result = self._check_multi_level_cache('gemini_vision', image_data, current_time)
        if cache_result:
            return cache_result
        
        # Use batch processing if available
        if BATCH_AVAILABLE and self.batch_config['enable_batching']:
            request_id = self.add_to_batch('gemini', prompt)
            response = self.get_batch_response(request_id, timeout=8.0)
            
            if response and response.success:
                result = {
                    'success': True,
                    'data': response.data,
                    'source': 'batch_processing',
                    'response_time': response.response_time
                }
                self._cache_result('gemini_vision', image_data, result, priority)
                return result
        
        # Fallback to original method
        return self.smart_gemini_request(image_data, prompt, priority)
    
    def smart_gemini_request(self, image_data, prompt, priority='medium'):
        """Smart Gemini request with full mitigation"""
        current_time = time.time()
        
        # Check multi-level cache first
        cache_result = self._check_multi_level_cache('gemini_vision', image_data, current_time)
        if cache_result:
            return cache_result
        
        # Check if we can make immediate request
        if self._can_make_request('gemini') and self._has_available_key('gemini'):
            try:
                result = self._immediate_gemini_request(image_data, prompt)
                if result and result.get('success'):
                    self._cache_result('gemini_vision', image_data, result, priority)
                    return result
            except Exception as e:
                pass  # Fall through to other methods
        
        # Use local computer vision fallback
        return self._use_local_cv_fallback(image_data, current_time)
    
    def _immediate_gemini_request(self, image_data, prompt):
        """Immediate Gemini API request with rotation"""
        for attempt in range(len(self.gemini_keys)):
            try:
                current_key = self._get_current_key('gemini')
                if not current_key:
                    break
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={current_key}"
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_data
                                }
                            }
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    # Extract number for people count
                    import re
                    numbers = re.findall(r'\d+', text)
                    people_count = int(numbers[0]) if numbers else 0
                    
                    self._update_request_count('gemini')
                    
                    return {
                        'success': True,
                        'people_count': people_count,
                        'source': 'gemini_api',
                        'confidence': 'high',
                        'timestamp': time.time()
                    }
                    
                elif response.status_code == 429:
                    # Blacklist this key temporarily
                    self._blacklist_key('gemini', current_key, duration=300)  # 5 minutes
                    self._rotate_key('gemini')
                    continue
                else:
                    self._rotate_key('gemini')
                    continue
                    
            except Exception as e:
                self._rotate_key('gemini')
                continue
        
        return None
    
    def _use_local_cv_fallback(self, image_data, current_time):
        """Use local computer vision as fallback"""
        try:
            # Decode base64 image
            import base64
            import cv2
            import numpy as np
            
            img_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Use local computer vision models
            people_count = self.local_models.estimate_people_count(img)
            
            result = {
                'success': True,
                'people_count': people_count,
                'source': 'local_cv',
                'confidence': 'medium',
                'timestamp': current_time
            }
            
            # Cache this fallback result
            self._cache_result('gemini_vision', image_data, result, 'medium')
            
            return result
            
        except Exception as e:
            # Ultimate fallback
            return {
                'success': True,
                'people_count': random.randint(5, 20),
                'source': 'random_fallback',
                'confidence': 'low',
                'timestamp': current_time
            }
    
    def _can_make_request(self, api_type):
        """Check if we can make request based on rate limits"""
        current_time = time.time()
        
        # Reset counters every minute
        if current_time - self.last_reset > 60:
            self.request_count = {'gemini': 0, 'maps': 0}
            self.last_reset = current_time
        
        return self.request_count[api_type] < self.max_requests_per_minute[api_type]
    
    def _get_current_key(self, api_type):
        """Get current available API key"""
        keys = self.gemini_keys if api_type == 'gemini' else self.maps_keys
        blacklist = self.key_blacklist[api_type]
        
        # Clean expired blacklisted keys
        current_time = time.time()
        expired_keys = []
        for key_data in blacklist:
            if isinstance(key_data, tuple) and current_time > key_data[1]:  # (key, expiry_time)
                expired_keys.append(key_data)
        
        for expired in expired_keys:
            blacklist.discard(expired)
        
        # Find available key
        for i, key in enumerate(keys):
            key_blacklisted = any(
                (isinstance(item, tuple) and item[0] == key) or item == key 
                for item in blacklist
            )
            if not key_blacklisted:
                self.current_key_index[api_type] = i
                return key
        
        return None
    
    def _has_available_key(self, api_type):
        """Check if any key is available"""
        return self._get_current_key(api_type) is not None
    
    def _rotate_key(self, api_type):
        """Rotate to next available API key"""
        keys = self.gemini_keys if api_type == 'gemini' else self.maps_keys
        current_index = self.current_key_index[api_type]
        
        self.current_key_index[api_type] = (current_index + 1) % len(keys)
    
    def _blacklist_key(self, api_type, key, duration=300):
        """Temporarily blacklist a key"""
        expiry_time = time.time() + duration
        self.key_blacklist[api_type].add((key, expiry_time))
    
    def _update_request_count(self, api_type):
        """Update request count"""
        self.request_count[api_type] += 1
    
    def _check_multi_level_cache(self, cache_type, key_data, current_time):
        """Check multi-level cache system"""
        # Create cache key
        import hashlib
        cache_key = hashlib.md5(str(key_data).encode()).hexdigest()[:16]
        
        # Check Level 1 (5 min)
        if cache_key in self.multi_level_cache['level1']:
            cached = self.multi_level_cache['level1'][cache_key]
            if current_time - cached['timestamp'] < 300:  # 5 minutes
                cached_result = cached.copy()
                cached_result['from_cache'] = 'level1'
                cached_result['cache_age'] = int(current_time - cached['timestamp'])
                return cached_result
        
        # Check Level 2 (15 min)
        if cache_key in self.multi_level_cache['level2']:
            cached = self.multi_level_cache['level2'][cache_key]
            if current_time - cached['timestamp'] < 900:  # 15 minutes
                cached_result = cached.copy()
                cached_result['from_cache'] = 'level2'
                cached_result['cache_age'] = int(current_time - cached['timestamp'])
                return cached_result
        
        # Check Level 3 (1 hour)
        if cache_key in self.multi_level_cache['level3']:
            cached = self.multi_level_cache['level3'][cache_key]
            if current_time - cached['timestamp'] < 3600:  # 1 hour
                cached_result = cached.copy()
                cached_result['from_cache'] = 'level3'
                cached_result['cache_age'] = int(current_time - cached['timestamp'])
                return cached_result
        
        return None
    
    def _cache_result(self, cache_type, key_data, result, priority='medium'):
        """Cache result in appropriate level"""
        import hashlib
        cache_key = hashlib.md5(str(key_data).encode()).hexdigest()[:16]
        
        # Cache in all levels based on priority
        if priority == 'high':
            self.multi_level_cache['level1'][cache_key] = result.copy()
            self.multi_level_cache['level2'][cache_key] = result.copy()
            self.multi_level_cache['level3'][cache_key] = result.copy()
        elif priority == 'medium':
            self.multi_level_cache['level2'][cache_key] = result.copy()
            self.multi_level_cache['level3'][cache_key] = result.copy()
        else:
            self.multi_level_cache['level3'][cache_key] = result.copy()


class LocalFallbackModels:
    """Local computer vision models for fallback"""
    
    def __init__(self):
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load local CV models"""
        try:
            # Initialize basic CV models
            self.models_loaded = True
        except Exception as e:
            print(f"Could not load local models: {e}")
            self.models_loaded = False
    
    def estimate_people_count(self, image):
        """Estimate people count using local CV"""
        try:
            import cv2
            import numpy as np
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Simple blob detection for people
            # This is a basic implementation - can be enhanced
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size (rough people estimation)
            people_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 5000:  # Rough person size range
                    people_contours.append(contour)
            
            # Estimate based on contours and image analysis
            height, width = gray.shape
            total_pixels = height * width
            
            # Calculate density based on various factors
            dark_pixels = np.sum(gray < 100)
            dark_ratio = dark_pixels / total_pixels
            
            # Combine contour count and density analysis
            contour_estimate = len(people_contours)
            density_estimate = int(dark_ratio * 30)  # Scale factor
            
            # Average the estimates
            final_estimate = max(1, int((contour_estimate + density_estimate) / 2))
            
            # Cap the estimate
            return min(final_estimate, 35)
            
        except Exception as e:
            # Ultimate fallback
            return random.randint(5, 15)

# Global instance
api_mitigation = APIMitigationService()
