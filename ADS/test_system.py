#!/usr/bin/env python3
"""
Test script for Video Anomaly Detection System
This script helps you test the system with different video sources
"""

import os
import sys
from video_anomaly_detector import VideoAnomalyDetector
from config import Config

def test_with_camera():
    """Test with live camera"""
    print("🎥 Testing with Live Camera")
    print("=" * 50)
    
    detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
    
    try:
        print("📹 Starting live camera monitoring...")
        print("🔍 Analysis will occur every 3 seconds")
        print("📊 Watch the terminal for detailed logs!")
        print("\nControls:")
        print("  • Press 'q' in video window to quit")
        print("  • Press 's' to save reports")
        print("\n" + "-" * 50)
        
        detector.start_live_monitoring(0)  # Use default camera
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        print("\nTroubleshooting:")
        print("  • Check if camera is connected")
        print("  • Close other apps using the camera")
        print("  • Try camera index 1 or 2 for external cameras")

def test_with_video_file(video_path):
    """Test with MP4 file"""
    print(f"🎬 Testing with Video File: {video_path}")
    print("=" * 50)
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
    
    try:
        print("📹 Starting video file analysis...")
        print("🔍 Analysis will occur every 3 seconds")
        print("📊 Watch the terminal for detailed logs!")
        print(f"📁 File: {os.path.basename(video_path)}")
        print("\nControls:")
        print("  • Press 'q' in video window to quit")
        print("  • Press 's' to save reports")
        print("\n" + "-" * 50)
        
        detector.start_live_monitoring(video_path)
        return True
        
    except Exception as e:
        print(f"❌ Video file test failed: {e}")
        print("\nTroubleshooting:")
        print("  • Check if video file is valid")
        print("  • Ensure file format is supported (MP4, AVI, MOV, etc.)")
        print("  • Try a different video file")
        return False

def main():
    print("🚀 Video Anomaly Detection System - Test Suite")
    print("=" * 60)
    
    # Check API key
    if Config.GEMINI_API_KEY == 'your_api_key_here':
        print("❌ Please configure your Gemini API key first!")
        print("   Edit the .env file and add your API key")
        return
    
    print("✅ API Key configured")
    print(f"🤖 Model: {Config.GEMINI_MODEL}")
    print(f"⏱️  Analysis interval: {Config.ANALYSIS_INTERVAL} seconds")
    
    while True:
        print("\n" + "=" * 60)
        print("Choose test option:")
        print("1. Test with Live Camera")
        print("2. Test with MP4 File")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            test_with_camera()
            
        elif choice == '2':
            video_path = input("Enter path to MP4 file: ").strip()
            if video_path:
                test_with_video_file(video_path)
            else:
                print("❌ No file path provided")
                
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")