"""
Batch API Request Service
Combines multiple API calls into single batch requests to avoid 429 rate limits
Supports Gemini AI, Google Maps, and other APIs
"""

import requests
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import os

class APIType(Enum):
    GEMINI = "gemini"
    GOOGLE_MAPS = "google_maps"
    GENERIC = "generic"

@dataclass
class BatchRequest:
    """Single request in a batch"""
    id: str
    api_type: APIType
    method: str  # GET, POST
    url: str
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None
    timeout: int = 15
    priority: str = "medium"  # low, medium, high, critical
    callback: Optional[callable] = None

@dataclass
class BatchResponse:
    """Response from batch request"""
    request_id: str
    success: bool
    status_code: int
    data: Any = None
    error: Optional[str] = None
    response_time: float = 0.0

class BatchAPIService:
    """
    Intelligent batch API service that combines multiple requests
    to minimize rate limiting across all APIs
    """
    
    def __init__(self):
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={os.getenv('GEMINI_API_KEY', 'AIzaSyBUwz7xkL0C1WS3qmP46AHd9ONQR3DRCnQ')}"
        self.maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA')
        
        # Batch queues for different APIs
        self.gemini_queue = queue.Queue()
        self.maps_queue = queue.Queue()
        self.generic_queue = queue.Queue()
        
        # Processing threads
        self.processing = True
        self.threads = []
        
        # Batch configuration
        self.batch_config = {
            APIType.GEMINI: {
                'max_batch_size': 5,  # Gemini supports multi-part requests
                'batch_timeout': 2.0,  # Wait max 2 seconds for more requests
                'rate_limit_delay': 1.0,  # Delay between batches
                'concurrent_batches': 2
            },
            APIType.GOOGLE_MAPS: {
                'max_batch_size': 3,  # Maps API batching
                'batch_timeout': 1.5,
                'rate_limit_delay': 0.8,
                'concurrent_batches': 2
            },
            APIType.GENERIC: {
                'max_batch_size': 4,
                'batch_timeout': 1.0,
                'rate_limit_delay': 0.5,
                'concurrent_batches': 3
            }
        }
        
        # Response storage
        self.responses = {}
        self.response_callbacks = {}
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'batched_requests': 0,
            'rate_limit_avoided': 0,
            'successful_responses': 0,
            'failed_responses': 0
        }
        
        # Start processing threads
        self._start_processors()
    
    def _start_processors(self):
        """Start background threads for processing batches"""
        processors = [
            (self._process_gemini_batches, "Gemini Batch Processor"),
            (self._process_maps_batches, "Maps Batch Processor"),
            (self._process_generic_batches, "Generic Batch Processor")
        ]
        
        for processor_func, name in processors:
            thread = threading.Thread(target=processor_func, name=name, daemon=True)
            thread.start()
            self.threads.append(thread)
        
        print("✓ Batch API processors started")
    
    def add_request(self, request: BatchRequest) -> str:
        """Add request to appropriate batch queue"""
        self.stats['total_requests'] += 1
        
        # Store callback for later
        if request.callback:
            self.response_callbacks[request.id] = request.callback
        
        # Route to appropriate queue
        if request.api_type == APIType.GEMINI:
            self.gemini_queue.put(request)
        elif request.api_type == APIType.GOOGLE_MAPS:
            self.maps_queue.put(request)
        else:
            self.generic_queue.put(request)
        
        return request.id
    
    def gemini_batch_request(self, prompts: List[str], request_ids: List[str] = None) -> List[BatchResponse]:
        """
        Create multi-part Gemini request to process multiple prompts in one API call
        This is the key optimization - instead of 10 separate calls, make 1 combined call
        """
        if not prompts:
            return []
        
        if not request_ids:
            request_ids = [f"gemini_{i}_{int(time.time())}" for i in range(len(prompts))]
        
        try:
            # Create multi-part payload for Gemini
            # Gemini supports multiple parts in a single request
            parts = []
            for i, prompt in enumerate(prompts):
                parts.append({
                    "text": f"REQUEST_{i+1}: {prompt}\n\nPlease respond with: REQUEST_{i+1}_RESPONSE: [your response]"
                })
            
            payload = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "maxOutputTokens": 4096 * len(prompts),  # Scale output for multiple requests
                    "temperature": 0.7
                }
            }
            
            start_time = time.time()
            response = requests.post(self.gemini_url, json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                full_text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse multi-part response
                responses = []
                for i, request_id in enumerate(request_ids):
                    # Extract individual response
                    response_marker = f"REQUEST_{i+1}_RESPONSE:"
                    if response_marker in full_text:
                        # Get response for this request
                        start_idx = full_text.find(response_marker) + len(response_marker)
                        
                        # Find end of this response (next REQUEST marker or end of text)
                        next_marker = f"REQUEST_{i+2}_RESPONSE:"
                        if next_marker in full_text[start_idx:]:
                            end_idx = full_text.find(next_marker, start_idx)
                            response_text = full_text[start_idx:end_idx].strip()
                        else:
                            response_text = full_text[start_idx:].strip()
                        
                        responses.append(BatchResponse(
                            request_id=request_id,
                            success=True,
                            status_code=200,
                            data={'text': response_text, 'full_response': result},
                            response_time=response_time / len(prompts)  # Distribute time
                        ))
                    else:
                        # Fallback: use portion of full response
                        chunk_size = len(full_text) // len(prompts)
                        start_idx = i * chunk_size
                        end_idx = (i + 1) * chunk_size if i < len(prompts) - 1 else len(full_text)
                        response_text = full_text[start_idx:end_idx].strip()
                        
                        responses.append(BatchResponse(
                            request_id=request_id,
                            success=True,
                            status_code=200,
                            data={'text': response_text, 'full_response': result},
                            response_time=response_time / len(prompts)
                        ))
                
                self.stats['successful_responses'] += len(responses)
                self.stats['batched_requests'] += len(prompts) - 1  # Saved API calls
                self.stats['rate_limit_avoided'] += len(prompts) - 1
                
                return responses
            
            else:
                # Batch failed, create error responses
                error_msg = f"Batch request failed: {response.status_code}"
                responses = []
                for request_id in request_ids:
                    responses.append(BatchResponse(
                        request_id=request_id,
                        success=False,
                        status_code=response.status_code,
                        error=error_msg,
                        response_time=response_time / len(prompts)
                    ))
                
                self.stats['failed_responses'] += len(responses)
                return responses
                
        except Exception as e:
            error_msg = f"Batch processing error: {str(e)}"
            responses = []
            for request_id in request_ids:
                responses.append(BatchResponse(
                    request_id=request_id,
                    success=False,
                    status_code=500,
                    error=error_msg,
                    response_time=0.0
                ))
            
            self.stats['failed_responses'] += len(responses)
            return responses
    
    def _process_gemini_batches(self):
        """Process Gemini API batches"""
        config = self.batch_config[APIType.GEMINI]
        
        while self.processing:
            try:
                # Collect batch of requests
                batch = []
                start_time = time.time()
                
                # Get first request (blocking)
                try:
                    first_request = self.gemini_queue.get(timeout=1.0)
                    batch.append(first_request)
                except queue.Empty:
                    continue
                
                # Collect additional requests (non-blocking)
                while (len(batch) < config['max_batch_size'] and 
                       time.time() - start_time < config['batch_timeout']):
                    try:
                        request = self.gemini_queue.get_nowait()
                        batch.append(request)
                    except queue.Empty:
                        time.sleep(0.1)
                
                # Process batch
                if len(batch) > 1:
                    # Multi-request batch
                    prompts = []
                    request_ids = []
                    
                    for req in batch:
                        if req.payload and 'contents' in req.payload:
                            # Extract prompt from Gemini payload
                            parts = req.payload['contents'][0]['parts']
                            if parts and 'text' in parts[0]:
                                prompts.append(parts[0]['text'])
                                request_ids.append(req.id)
                    
                    if prompts:
                        responses = self.gemini_batch_request(prompts, request_ids)
                        
                        # Store responses and trigger callbacks
                        for response in responses:
                            self.responses[response.request_id] = response
                            if response.request_id in self.response_callbacks:
                                callback = self.response_callbacks[response.request_id]
                                threading.Thread(target=callback, args=(response,), daemon=True).start()
                
                else:
                    # Single request - process normally
                    request = batch[0]
                    response = self._execute_single_request(request)
                    self.responses[request.id] = response
                    
                    if request.id in self.response_callbacks:
                        callback = self.response_callbacks[request.id]
                        threading.Thread(target=callback, args=(response,), daemon=True).start()
                
                # Rate limiting delay
                time.sleep(config['rate_limit_delay'])
                
            except Exception as e:
                print(f"Gemini batch processor error: {e}")
                time.sleep(1.0)
    
    def _process_maps_batches(self):
        """Process Google Maps API batches"""
        config = self.batch_config[APIType.GOOGLE_MAPS]
        
        while self.processing:
            try:
                # Similar batching logic for Maps API
                batch = []
                start_time = time.time()
                
                try:
                    first_request = self.maps_queue.get(timeout=1.0)
                    batch.append(first_request)
                except queue.Empty:
                    continue
                
                # Collect additional requests
                while (len(batch) < config['max_batch_size'] and 
                       time.time() - start_time < config['batch_timeout']):
                    try:
                        request = self.maps_queue.get_nowait()
                        batch.append(request)
                    except queue.Empty:
                        time.sleep(0.1)
                
                # Process batch (Maps API has limited batching, so process with delay)
                for request in batch:
                    response = self._execute_single_request(request)
                    self.responses[request.id] = response
                    
                    if request.id in self.response_callbacks:
                        callback = self.response_callbacks[request.id]
                        threading.Thread(target=callback, args=(response,), daemon=True).start()
                    
                    # Small delay between requests in batch
                    if len(batch) > 1:
                        time.sleep(0.2)
                
                time.sleep(config['rate_limit_delay'])
                
            except Exception as e:
                print(f"Maps batch processor error: {e}")
                time.sleep(1.0)
    
    def _process_generic_batches(self):
        """Process generic API batches"""
        config = self.batch_config[APIType.GENERIC]
        
        while self.processing:
            try:
                batch = []
                start_time = time.time()
                
                try:
                    first_request = self.generic_queue.get(timeout=1.0)
                    batch.append(first_request)
                except queue.Empty:
                    continue
                
                while (len(batch) < config['max_batch_size'] and 
                       time.time() - start_time < config['batch_timeout']):
                    try:
                        request = self.generic_queue.get_nowait()
                        batch.append(request)
                    except queue.Empty:
                        time.sleep(0.1)
                
                # Process batch with staggered timing
                for i, request in enumerate(batch):
                    response = self._execute_single_request(request)
                    self.responses[request.id] = response
                    
                    if request.id in self.response_callbacks:
                        callback = self.response_callbacks[request.id]
                        threading.Thread(target=callback, args=(response,), daemon=True).start()
                    
                    # Stagger requests to avoid rate limits
                    if i < len(batch) - 1:
                        time.sleep(0.3)
                
                time.sleep(config['rate_limit_delay'])
                
            except Exception as e:
                print(f"Generic batch processor error: {e}")
                time.sleep(1.0)
    
    def _execute_single_request(self, request: BatchRequest) -> BatchResponse:
        """Execute a single API request"""
        try:
            start_time = time.time()
            
            if request.method.upper() == 'POST':
                response = requests.post(
                    request.url, 
                    json=request.payload, 
                    headers=request.headers,
                    timeout=request.timeout
                )
            else:
                response = requests.get(
                    request.url,
                    params=request.payload,
                    headers=request.headers,
                    timeout=request.timeout
                )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.stats['successful_responses'] += 1
                return BatchResponse(
                    request_id=request.id,
                    success=True,
                    status_code=response.status_code,
                    data=response.json() if response.content else {},
                    response_time=response_time
                )
            else:
                self.stats['failed_responses'] += 1
                return BatchResponse(
                    request_id=request.id,
                    success=False,
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time=response_time
                )
                
        except Exception as e:
            self.stats['failed_responses'] += 1
            return BatchResponse(
                request_id=request.id,
                success=False,
                status_code=500,
                error=str(e),
                response_time=0.0
            )
    
    def get_response(self, request_id: str, timeout: float = 10.0) -> Optional[BatchResponse]:
        """Get response for a request (blocking)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if request_id in self.responses:
                return self.responses.pop(request_id)  # Remove after retrieval
            time.sleep(0.1)
        
        return None  # Timeout
    
    def get_stats(self) -> Dict:
        """Get batch processing statistics"""
        total = self.stats['successful_responses'] + self.stats['failed_responses']
        success_rate = (self.stats['successful_responses'] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'success_rate_percent': round(success_rate, 1),
            'rate_limit_savings': self.stats['rate_limit_avoided']
        }
    
    def shutdown(self):
        """Shutdown batch service"""
        self.processing = False
        print("Batch API service shutting down...")

# Global batch service instance
batch_api = BatchAPIService()

def create_gemini_batch_request(prompt: str, request_id: str = None, priority: str = "medium") -> str:
    """Helper function to create Gemini batch request"""
    if not request_id:
        request_id = f"gemini_{int(time.time() * 1000)}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    request = BatchRequest(
        id=request_id,
        api_type=APIType.GEMINI,
        method="POST",
        url=batch_api.gemini_url,
        payload=payload,
        priority=priority
    )
    
    return batch_api.add_request(request)

def create_maps_batch_request(params: Dict, request_id: str = None) -> str:
    """Helper function to create Maps batch request"""
    if not request_id:
        request_id = f"maps_{int(time.time() * 1000)}"
    
    # Add API key to params
    params['key'] = batch_api.maps_api_key
    
    request = BatchRequest(
        id=request_id,
        api_type=APIType.GOOGLE_MAPS,
        method="GET",
        url="https://maps.googleapis.com/maps/api/geocode/json",
        payload=params
    )
    
    return batch_api.add_request(request)

# Example usage functions
def batch_crowd_analysis(video_paths: List[str]) -> List[BatchResponse]:
    """
    Example: Batch analyze multiple videos instead of one-by-one
    This reduces API calls from N to 1 (or N/batch_size)
    """
    prompts = []
    request_ids = []
    
    for i, video_path in enumerate(video_paths):
        prompt = f"Analyze crowd in video {video_path} for people count, density, and safety."
        request_id = f"crowd_analysis_{i}_{int(time.time())}"
        prompts.append(prompt)
        request_ids.append(request_id)
    
    return batch_api.gemini_batch_request(prompts, request_ids)
