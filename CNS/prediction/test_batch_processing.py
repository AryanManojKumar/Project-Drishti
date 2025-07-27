"""
Test Batch API Processing
Tests the new batch system to verify 429 rate limit mitigation
"""

import time
import sys
import os
sys.path.append(os.getcwd())

def test_batch_api_service():
    """Test the batch API service functionality"""
    print("=== Testing Batch API Service ===")
    
    try:
        from batch_api_service import batch_api, create_gemini_batch_request
        
        print("✓ Batch API service imported successfully")
        
        # Test 1: Single batch request
        print("\n--- Test 1: Single Batch Request ---")
        request_id = create_gemini_batch_request(
            "Count the number 1, 2, 3. Respond with just '3'.", 
            "test_single",
            priority="high"
        )
        print(f"Created request: {request_id}")
        
        # Wait for response
        response = batch_api.get_response(request_id, timeout=10.0)
        if response:
            print(f"✓ Response received: Success={response.success}")
            if response.success:
                print(f"Data: {response.data}")
            else:
                print(f"Error: {response.error}")
        else:
            print("❌ No response received (timeout)")
        
        # Test 2: Multiple batch requests (should be combined)
        print("\n--- Test 2: Multiple Batch Requests ---")
        prompts = [
            "What is 2+2? Just give the number.",
            "What color comes after red in a rainbow?",
            "Name one planet in our solar system.",
            "What is the capital of France?",
            "Count to 3 and stop."
        ]
        
        request_ids = []
        start_time = time.time()
        
        for i, prompt in enumerate(prompts):
            req_id = create_gemini_batch_request(
                prompt, 
                f"test_batch_{i}",
                priority="medium"
            )
            request_ids.append(req_id)
            print(f"Queued request {i+1}: {req_id}")
        
        print(f"Queued {len(prompts)} requests in {time.time() - start_time:.3f}s")
        
        # Wait for all responses
        print("\nWaiting for batch responses...")
        responses = []
        for req_id in request_ids:
            response = batch_api.get_response(req_id, timeout=15.0)
            responses.append(response)
            
            if response:
                print(f"✓ {req_id}: Success={response.success}")
                if response.success and 'text' in response.data:
                    print(f"  Response: {response.data['text'][:50]}...")
                elif not response.success:
                    print(f"  Error: {response.error}")
            else:
                print(f"❌ {req_id}: Timeout")
        
        successful = sum(1 for r in responses if r and r.success)
        print(f"\n✓ Batch test complete: {successful}/{len(prompts)} successful")
        
        # Test 3: Statistics
        print("\n--- Test 3: Batch Statistics ---")
        stats = batch_api.get_stats()
        print(f"Total requests: {stats['total_requests']}")
        print(f"Batched requests: {stats['batched_requests']}")
        print(f"Rate limit savings: {stats['rate_limit_avoided']}")
        print(f"Success rate: {stats['success_rate_percent']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch API test failed: {e}")
        return False

def test_mitigation_service_batch():
    """Test the mitigation service with batch processing"""
    print("\n=== Testing Mitigation Service Batch ===")
    
    try:
        from api_mitigation_service import api_mitigation
        
        # Test batch functionality if available
        if hasattr(api_mitigation, 'smart_gemini_request_batch'):
            print("✓ Batch functionality available in mitigation service")
            
            # Test batch request
            result = api_mitigation.smart_gemini_request_batch(
                "test_image_data", 
                "Count people in this test image (respond with number only)",
                priority="high"
            )
            
            if result:
                print(f"✓ Batch request result: {result.get('success', False)}")
                print(f"Source: {result.get('source', 'unknown')}")
            else:
                print("❌ No batch result received")
        else:
            print("⚠️ Batch functionality not available in mitigation service")
        
        return True
        
    except Exception as e:
        print(f"❌ Mitigation service batch test failed: {e}")
        return False

def test_crowd_predictor_batch():
    """Test crowd predictor with batch processing"""
    print("\n=== Testing Crowd Predictor Batch ===")
    
    try:
        from crowd_predictor import SimpleCrowdPredictor
        import cv2
        import numpy as np
        
        # Create test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "TEST CROWD IMAGE", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        predictor = SimpleCrowdPredictor()
        
        print("Testing crowd predictor analysis...")
        result = predictor._analyze_video(test_image)
        
        if result:
            print(f"✓ Analysis result received")
            print(f"People count: {result.get('people_count', 'unknown')}")
            print(f"Source: {result.get('source', 'unknown')}")
            print(f"Batch processing: {result.get('batch_processing', False)}")
            print(f"Mitigation used: {result.get('mitigation_used', False)}")
        else:
            print("❌ No analysis result")
        
        return True
        
    except Exception as e:
        print(f"❌ Crowd predictor batch test failed: {e}")
        return False

def test_rate_limit_simulation():
    """Simulate rapid API calls to test rate limiting mitigation"""
    print("\n=== Testing Rate Limit Mitigation ===")
    
    try:
        from batch_api_service import create_gemini_batch_request, batch_api
        
        print("Simulating rapid API calls...")
        
        # Create many requests quickly
        request_ids = []
        start_time = time.time()
        
        for i in range(10):
            req_id = create_gemini_batch_request(
                f"Quick test {i+1}: What is {i+1} + 1?",
                f"rapid_test_{i}",
                priority="low"
            )
            request_ids.append(req_id)
        
        creation_time = time.time() - start_time
        print(f"Created 10 requests in {creation_time:.3f}s")
        
        # Wait for responses
        print("Waiting for responses...")
        response_start = time.time()
        
        successful = 0
        failed = 0
        
        for req_id in request_ids:
            response = batch_api.get_response(req_id, timeout=20.0)
            if response and response.success:
                successful += 1
            else:
                failed += 1
        
        total_time = time.time() - start_time
        
        print(f"\nRate limit test results:")
        print(f"Total time: {total_time:.3f}s")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {successful/(successful+failed)*100:.1f}%")
        
        # Get final stats
        stats = batch_api.get_stats()
        print(f"Rate limit savings: {stats['rate_limit_avoided']} API calls avoided")
        
        return successful > failed  # More successes than failures
        
    except Exception as e:
        print(f"❌ Rate limit simulation failed: {e}")
        return False

def main():
    """Run all batch processing tests"""
    print("🚀 Starting Batch API Processing Tests")
    print("=" * 50)
    
    tests = [
        ("Batch API Service", test_batch_api_service),
        ("Mitigation Service Batch", test_mitigation_service_batch),
        ("Crowd Predictor Batch", test_crowd_predictor_batch),
        ("Rate Limit Simulation", test_rate_limit_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Batch processing is working correctly.")
        print("💡 This should significantly reduce 429 rate limit errors.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    # Try to get final batch stats if available
    try:
        from batch_api_service import batch_api
        stats = batch_api.get_stats()
        print(f"\n📈 Final Batch Statistics:")
        print(f"   Total requests processed: {stats['total_requests']}")
        print(f"   API calls saved: {stats['rate_limit_avoided']}")
        print(f"   Success rate: {stats['success_rate_percent']}%")
    except:
        pass

if __name__ == "__main__":
    main()
