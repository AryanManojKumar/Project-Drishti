"""
Simple test script to verify the system components work without GCP dependencies.
"""

import numpy as np
import sys
import os

def test_vision_processor():
    """Test the vision processor component."""
    try:
        from src.vision_processor_simple import CrowdVisionProcessor
        
        print("\n=== Testing Vision Processor ===")
        processor = CrowdVisionProcessor()
        success = processor.test_functionality()
        
        if success:
            print("✅ Vision processor test passed!")
        else:
            print("❌ Vision processor test failed!")
        
        return success
    except Exception as e:
        print(f"❌ Error testing vision processor: {e}")
        return False

def test_location_processor():
    """Test the location processor component."""
    try:
        from src.device_location_processor_simple import DeviceLocationProcessor
        
        print("\n=== Testing Location Processor ===")
        processor = DeviceLocationProcessor()
        success = processor.test_functionality()
        
        if success:
            print("✅ Location processor test passed!")
        else:
            print("❌ Location processor test failed!")
        
        return success
    except Exception as e:
        print(f"❌ Error testing location processor: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting system component tests...")
    
    vision_success = test_vision_processor()
    location_success = test_location_processor()
    
    print("\n=== Test Summary ===")
    print(f"Vision Processor: {'✅ PASSED' if vision_success else '❌ FAILED'}")
    print(f"Location Processor: {'✅ PASSED' if location_success else '❌ FAILED'}")
    
    if vision_success and location_success:
        print("\n✅ All tests passed! The system components are working correctly.")
        print("\nYou can now proceed with setting up the GCP infrastructure.")
    else:
        print("\n❌ Some tests failed. Please fix the issues before proceeding.")

if __name__ == "__main__":
    main()