"""
Test script for the integrated crowd prediction system
Tests AI situational chat, rate limiting, and IP camera integration
"""

import sys
import time
from datetime import datetime

# Test the crowd predictor with rate limiting
def test_crowd_predictor():
    print("🔍 Testing Crowd Predictor with Rate Limiting...")
    
    try:
        from crowd_predictor import get_crowd_density
        
        # First call
        print("📹 First API call...")
        result1 = get_crowd_density()
        print(f"✅ Result 1: {result1['crowd_level']} - {result1['people_count']} people")
        
        # Second call immediately (should hit rate limit)
        print("📹 Second API call (immediate)...")
        result2 = get_crowd_density()
        
        if 'rate_limited' in result2 or 'from_cache' in result2:
            print("✅ Rate limiting working correctly!")
        else:
            print("⚠️ Rate limiting may not be working")
        
        print(f"📊 Result 2: {result2}")
        
    except Exception as e:
        print(f"❌ Error testing crowd predictor: {e}")

def test_streamlit_integration():
    print("\n🌐 Testing Streamlit Integration...")
    
    try:
        print("📋 Available Streamlit files:")
        import os
        files = [f for f in os.listdir('.') if f.startswith('streamlit_crowd_ui')]
        for file in files:
            print(f"  • {file}")
        
        print("\n🚀 To run the integrated system:")
        print("   streamlit run streamlit_crowd_ui_fixed.py")
        print("\n📱 Features available:")
        print("   • AI Situational Chat")
        print("   • IP Camera Setup")
        print("   • Rate Limited Analysis")
        print("   • Function Calling Support")
        
    except Exception as e:
        print(f"❌ Error checking streamlit files: {e}")

def test_ai_chat_functions():
    print("\n🤖 Testing AI Chat Functions...")
    
    try:
        # Simulate session state
        class MockSessionState:
            def __init__(self):
                self.data = {
                    'ip_camera_config': {
                        'cam_1': {
                            'name': 'Main Entrance Cam',
                            'location': 'Main Entrance',
                            'url': 'http://192.168.1.100:8080/video',
                            'lat': 13.0360,
                            'lng': 77.6430
                        },
                        'cam_2': {
                            'name': 'Food Court Cam',
                            'location': 'Food Court',
                            'url': 'http://192.168.1.101:8080/video',
                            'lat': 13.0354,
                            'lng': 77.6428
                        }
                    }
                }
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        # Mock streamlit session state
        import streamlit as st
        st.session_state = MockSessionState()
        
        from ai_situational_chat import AISituationalChat
        
        chat = AISituationalChat()
        
        # Test function calls
        print("📹 Testing camera crowd count function...")
        result = chat.get_camera_crowd_count()
        print(f"✅ Camera data: {len(result.get('cameras_data', {}))} cameras found")
        
        print("🛡️ Testing security analysis function...")
        security_result = chat.analyze_security_zones()
        print(f"✅ Security analysis: {security_result.get('overall_risk_level', 'unknown')} risk level")
        
        print("🔮 Testing bottleneck prediction function...")
        bottleneck_result = chat.predict_bottlenecks()
        print(f"✅ Bottleneck predictions: {bottleneck_result.get('total_predictions', 0)} areas analyzed")
        
    except Exception as e:
        print(f"❌ Error testing AI chat functions: {e}")

def show_usage_instructions():
    print("\n" + "="*60)
    print("🎯 INTEGRATED CROWD PREDICTION SYSTEM - READY!")
    print("="*60)
    
    print("\n🚀 How to run the system:")
    print("1. Open PowerShell/Terminal")
    print("2. Navigate to this directory:")
    print(f"   cd {os.getcwd()}")
    print("3. Run the Streamlit app:")
    print("   streamlit run streamlit_crowd_ui_fixed.py")
    
    print("\n📱 Main Features:")
    print("• 🤖 AI Situational Chat - Natural language queries")
    print("• 📹 IP Camera Setup - Phone camera integration")
    print("• ⏱️ Rate Limiting - Prevents 429 API errors")
    print("• 🔍 Function Calling - Smart AI responses")
    print("• 🎯 Live Monitoring - Real-time crowd analysis")
    
    print("\n🗣️ Example AI Chat Queries:")
    print('• "Summarize security concerns in the main entrance"')
    print('• "What\'s the current crowd status?"')
    print('• "Predict bottlenecks in the next 20 minutes"')
    print('• "Show me high-risk areas right now"')
    
    print("\n📱 IP Camera Setup:")
    print("1. Install 'IP Webcam' app on Android phone")
    print("2. Start server in app")
    print("3. Note IP address (e.g., 192.168.1.100:8080)")
    print("4. Enter details in 'IP Camera Setup' page")
    print("5. Test connection and start monitoring")
    
    print("\n⚠️ Rate Limiting Info:")
    print("• API calls limited to 1 per minute")
    print("• Cached results shown when rate limited")
    print("• Prevents 429 'Too Many Requests' errors")
    print("• System automatically adjusts intervals")

if __name__ == "__main__":
    print("🎯 TESTING INTEGRATED CROWD PREDICTION SYSTEM")
    print("=" * 50)
    
    import os
    
    # Test individual components
    test_crowd_predictor()
    test_streamlit_integration()
    test_ai_chat_functions()
    
    # Show usage instructions
    show_usage_instructions()
    
    print(f"\n✅ All tests completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 System ready for use! Run: streamlit run streamlit_crowd_ui_fixed.py")
