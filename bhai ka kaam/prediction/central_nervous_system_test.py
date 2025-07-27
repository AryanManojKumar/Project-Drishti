"""
Central Nervous System Test Script
Bhai, yeh simple test script hai jo tumhare system ko run karega
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from live_crowd_predictor import CentralNervousSystem
import time

def test_central_nervous_system():
    """Central Nervous System ko test karta hai"""
    print("🧠 Testing Central Nervous System...")
    
    # Create instance
    cns = CentralNervousSystem()
    
    # Test with multiple cameras (using same webcam for demo)
    camera_config = {
        'cam_entrance_main': 0,    # Main entrance
        'cam_corridor_main': 0,    # Corridor (same webcam for demo)
        'cam_hall1_entry': 0       # Hall 1 entry (same webcam for demo)
    }
    
    try:
        # Start central nervous system
        cns.start_central_nervous_system(camera_config)
        
        print("\n✅ Central Nervous System started successfully!")
        print("📊 Monitoring for 60 seconds...")
        print("Press Ctrl+C to stop early\n")
        
        # Run for 60 seconds with status updates every 10 seconds
        for i in range(6):
            time.sleep(10)
            
            try:
                status = cns.get_central_nervous_system_status()
                
                print(f"\n🧠 Status Update {i+1}/6:")
                print("=" * 50)
                
                # Summary
                summary = status.get('summary', {})
                print(f"📈 Overall Status: {summary.get('overall_status', 'unknown').upper()}")
                print(f"👥 Total People: {summary.get('total_people_in_venue', 0)}")
                print(f"📹 Active Cameras: {status.get('active_cameras', 0)}/{status.get('total_cameras_configured', 0)}")
                
                # Current situation
                situation = status.get('current_situation', {})
                location_mapping = situation.get('location_mapping', {})
                if location_mapping:
                    print(f"🏢 Venue Status: {location_mapping.get('venue_status', {}).get('status', 'unknown')}")
                    print(f"⚠️  Critical Locations: {len(location_mapping.get('critical_locations', []))}")
                
                # Alerts
                alerts = status.get('system_alerts', [])
                if alerts:
                    print(f"🚨 Active Alerts: {len(alerts)}")
                    for alert in alerts[-2:]:  # Show last 2 alerts
                        print(f"   - {alert.get('severity', 'unknown').upper()}: {alert.get('message', 'Unknown alert')}")
                else:
                    print("✅ No active alerts")
                
                # Bottlenecks
                bottlenecks = status.get('bottleneck_predictions', [])
                if bottlenecks:
                    print(f"⚠️  Bottleneck Predictions: {len(bottlenecks)}")
                    for bottleneck in bottlenecks[-2:]:  # Show last 2 predictions
                        location = bottleneck.get('location', 'Unknown')
                        eta = bottleneck.get('estimated_eta_minutes', 0)
                        severity = bottleneck.get('bottleneck_severity', 'unknown')
                        print(f"   - {severity.upper()}: {location} in {eta} minutes")
                else:
                    print("✅ No bottleneck predictions")
                
                # Flow map
                flow_map = situation.get('crowd_flow_map', {})
                if flow_map:
                    print(f"📊 Active Locations: {len(flow_map)}")
                    for location, data in list(flow_map.items())[:3]:  # Show first 3 locations
                        people = data.get('people_count', 0)
                        density = data.get('density_score', 0)
                        location_name = data.get('location_name', location)
                        print(f"   - {location_name}: {people} people (density: {density}/10)")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Status error: {e}")
        
        print("\n🎉 Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        # Stop the system
        print("\n🛑 Stopping Central Nervous System...")
        cns.stop_central_nervous_system()
        print("✅ System stopped successfully")

if __name__ == "__main__":
    test_central_nervous_system()