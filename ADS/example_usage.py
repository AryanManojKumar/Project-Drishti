#!/usr/bin/env python3
"""
Example usage of the Video Anomaly Detection System
This script demonstrates how to use the system for different scenarios
"""

import os
import time
from video_anomaly_detector import VideoAnomalyDetector, AnomalyCategory, SeverityLevel
from config import Config

def main():
    print("🎥 Video Anomaly Detection System - Example Usage")
    print("=" * 60)
    
    # Check if API key is configured
    if Config.GEMINI_API_KEY == 'AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8':
        print("❌ Please configure your Gemini API key in config.py or .env file")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize the detector
    print("🔧 Initializing anomaly detector...")
    detector = VideoAnomalyDetector(
        api_key=Config.GEMINI_API_KEY,
        model_name=Config.GEMINI_MODEL
    )
    
    print("✅ Detector initialized successfully!")
    print(f"📊 Model: {Config.GEMINI_MODEL}")
    print(f"⏱️  Analysis interval: {Config.ANALYSIS_INTERVAL} seconds")
    print(f"🎯 Confidence threshold: {Config.CONFIDENCE_THRESHOLD}")
    
    print("\n" + "=" * 60)
    print("🚀 STARTING LIVE MONITORING")
    print("=" * 60)
    print("📹 Video source: Default camera (0)")
    print("🔍 Monitoring for anomalies in large-scale events...")
    print("\nDetectable anomaly categories:")
    
    for i, category in enumerate(AnomalyCategory, 1):
        print(f"  {i:2d}. {category.value.replace('_', ' ').title()}")
    
    print(f"\nSeverity levels: 1-Low → 5-Emergency")
    print("\nControls:")
    print("  • Press 'q' to quit monitoring")
    print("  • Press 's' to save current reports")
    print("  • Emergency alerts (Level 4+) will be highlighted")
    
    print("\n" + "-" * 60)
    input("Press ENTER to start monitoring (make sure camera is connected)...")
    
    try:
        # Start monitoring with default camera
        detector.start_live_monitoring(video_source=0)
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        print("\nTroubleshooting tips:")
        print("  • Check if camera is connected and not used by other apps")
        print("  • Try different video source (1, 2, etc.) for external cameras")
        print("  • Verify your Gemini API key is valid and has quota")
        
    finally:
        # Display final statistics
        print("\n" + "=" * 60)
        print("📊 FINAL MONITORING STATISTICS")
        print("=" * 60)
        
        stats = detector.get_statistics()
        print(f"Total anomalies detected: {stats['total_anomalies']}")
        
        if stats['total_anomalies'] > 0:
            print(f"High priority incidents: {stats['high_priority_count']}")
            print(f"Latest anomaly: {stats['latest_anomaly']}")
            
            print("\nCategory breakdown:")
            for category, count in stats.get('categories', {}).items():
                print(f"  • {category.replace('_', ' ').title()}: {count}")
            
            print("\nSeverity distribution:")
            for severity, count in stats.get('severity_distribution', {}).items():
                print(f"  • {severity}: {count}")
                
            # Save final report
            detector.save_reports()
            print(f"\n💾 Reports saved to file")
        else:
            print("No anomalies detected during this session.")
        
        print("\n🎯 System performance:")
        print(f"  • Analysis interval: {Config.ANALYSIS_INTERVAL}s")
        print(f"  • Frame quality: {Config.FRAME_QUALITY}%")
        print(f"  • Model used: {Config.GEMINI_MODEL}")

def test_with_video_file():
    """Example of using a video file instead of live camera"""
    print("\n" + "=" * 60)
    print("📁 TESTING WITH VIDEO FILE")
    print("=" * 60)
    
    video_path = input("Enter path to video file (or press ENTER to skip): ").strip()
    
    if not video_path:
        print("Skipping video file test")
        return
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
    
    try:
        print(f"🎬 Processing video: {video_path}")
        detector.start_live_monitoring(video_source=video_path)
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")

if __name__ == "__main__":
    try:
        main()
        
        # Optional: Test with video file
        if input("\nTest with video file? (y/N): ").lower().startswith('y'):
            test_with_video_file()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")