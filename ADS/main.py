#!/usr/bin/env python3
"""
Video Anomaly Detection System - Main Entry Point
A comprehensive AI-powered video analysis system using Gemini 2.0 Flash

Usage:
    python main.py                    # Interactive menu
    python main.py --web             # Start web interface
    python main.py --camera          # Start camera monitoring
    python main.py --video <path>    # Analyze video file

"""

import os
import sys
import argparse
import threading
import time
from datetime import datetime
import webbrowser
from pathlib import Path

# Import our modules
from video_anomaly_detector import VideoAnomalyDetector
from config import Config
import web_interface

class VideoAnomalySystem:
    def __init__(self):
        self.detector = None
        self.web_app = None
        self.monitoring_thread = None
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking system requirements...")
        
        # Check API key
        if Config.GEMINI_API_KEY == 'your_api_key_here' or not Config.GEMINI_API_KEY:
            print("❌ Gemini API key not configured!")
            print("   Please edit the .env file and add your API key")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        
        # Check uploads directory
        if not os.path.exists('uploads'):
            print("📁 Creating uploads directory...")
            os.makedirs('uploads')
        
        # Check templates directory
        if not os.path.exists('templates'):
            print("❌ Templates directory not found!")
            return False
        
        print("✅ All requirements met!")
        return True
    
    def print_banner(self):
        """Print system banner"""
        print("=" * 80)
        print("🎥 VIDEO ANOMALY DETECTION SYSTEM")
        print("   Powered by Gemini 2.0 Flash Vision AI")
        print("=" * 80)
        print(f"🤖 Model: {Config.GEMINI_MODEL}")
        print(f"⏱️  Analysis Interval: {Config.ANALYSIS_INTERVAL} seconds")
        print(f"🎯 Confidence Threshold: {Config.CONFIDENCE_THRESHOLD}")
        print(f"🏟️  Event Type: {Config.EVENT_TYPE}")
        print(f"👥 Venue Capacity: {Config.VENUE_CAPACITY:,}")
        print("=" * 80)
    
    def start_web_interface(self, auto_open=True):
        """Start the web interface"""
        print("🌐 Starting web interface...")
        print("   Dashboard: http://localhost:5000")
        print("   Features:")
        print("   • Real-time anomaly alerts")
        print("   • MP4 file upload")
        print("   • Live analysis logs")
        print("   • Statistics dashboard")
        print("   • Emergency notifications")
        
        if auto_open:
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open('http://localhost:5000')
                except:
                    pass
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the Flask-SocketIO app
        web_interface.socketio.run(
            web_interface.app, 
            debug=False, 
            host='0.0.0.0', 
            port=5000,
            use_reloader=False
        )
    
    def start_camera_monitoring(self, camera_index=0):
        """Start live camera monitoring"""
        print(f"📹 Starting live camera monitoring (Camera {camera_index})...")
        print("🔍 Analysis will occur every 3 seconds")
        print("📊 Watch the terminal for detailed logs!")
        print("\nDetectable anomaly categories:")
        
        categories = [
            "Crowd Control", "Security Threats", "Medical Emergencies",
            "Fire Hazards", "Structural Damage", "Weather Emergencies",
            "Vehicle Incidents", "Equipment Failures", "Unauthorized Access",
            "Violence/Aggression", "Stampede Risk", "Evacuation Scenarios"
        ]
        
        for i, category in enumerate(categories, 1):
            print(f"  {i:2d}. {category}")
        
        print(f"\nSeverity levels: 1-Low → 5-Emergency")
        print("\nControls:")
        print("  • Press 'q' in video window to quit")
        print("  • Press 's' to save current reports")
        print("  • Press Ctrl+C in terminal to stop")
        
        print("\n" + "-" * 60)
        input("Press ENTER to start monitoring (make sure camera is connected)...")
        
        try:
            self.detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
            self.detector.start_live_monitoring(camera_index)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Camera monitoring failed: {e}")
            print("\nTroubleshooting tips:")
            print("  • Check if camera is connected and not used by other apps")
            print("  • Try different camera index (1, 2, etc.) for external cameras")
            print("  • Verify your Gemini API key is valid and has quota")
        finally:
            self.print_final_stats()
    
    def analyze_video_file(self, video_path):
        """Analyze a video file"""
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        print(f"🎬 Starting video file analysis...")
        print(f"📁 File: {os.path.basename(video_path)}")
        print(f"📍 Path: {video_path}")
        print("🔍 Analysis will occur every 3 seconds")
        print("📊 Watch the terminal for detailed logs!")
        
        print("\nControls:")
        print("  • Press 'q' in video window to quit")
        print("  • Press 's' to save current reports")
        print("  • Press Ctrl+C in terminal to stop")
        
        print("\n" + "-" * 60)
        
        try:
            self.detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
            self.detector.start_live_monitoring(video_path)
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Analysis stopped by user")
        except Exception as e:
            print(f"❌ Video analysis failed: {e}")
            print("\nTroubleshooting tips:")
            print("  • Check if video file is valid and not corrupted")
            print("  • Ensure file format is supported (MP4, AVI, MOV, etc.)")
            print("  • Try a different video file")
            print("  • Verify your Gemini API key is valid and has quota")
            return False
        finally:
            self.print_final_stats()
    

    
    def print_final_stats(self):
        """Print final statistics"""
        if self.detector:
            print("\n" + "=" * 60)
            print("📊 FINAL ANALYSIS STATISTICS")
            print("=" * 60)
            
            stats = self.detector.get_statistics()
            print(f"Total anomalies detected: {stats['total_anomalies']}")
            
            if stats['total_anomalies'] > 0:
                print(f"High priority incidents: {stats['high_priority_count']}")
                print(f"Latest anomaly: {stats['latest_anomaly']}")
                
                if stats.get('categories'):
                    print("\nCategory breakdown:")
                    for category, count in stats['categories'].items():
                        print(f"  • {category.replace('_', ' ').title()}: {count}")
                
                if stats.get('severity_distribution'):
                    print("\nSeverity distribution:")
                    for severity, count in stats['severity_distribution'].items():
                        print(f"  • {severity}: {count}")
                
                print(f"\n💾 Reports have been saved automatically")
            else:
                print("No anomalies detected during this session.")
            
            print(f"\n🎯 System performance:")
            print(f"  • Analysis interval: {Config.ANALYSIS_INTERVAL}s")
            print(f"  • Frame quality: {Config.FRAME_QUALITY}%")
            print(f"  • Model used: {Config.GEMINI_MODEL}")
    
    def start_admin_panel(self, auto_open=True):
        """Start the admin panel"""
        print("🛡️  Starting Admin Panel...")
        print("   Dashboard: http://localhost:5001")
        print("   Features:")
        print("   • Real-time incident monitoring")
        print("   • Volunteer management & assignment")
        print("   • Situation analysis & reporting")
        print("   • Resource allocation tracking")
        print("   • Emergency response coordination")
        
        if auto_open:
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open('http://localhost:5001')
                except:
                    pass
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the admin panel
        try:
            import admin_panel
            admin_panel.socketio.run(
                admin_panel.app, 
                debug=False, 
                host='0.0.0.0', 
                port=5001,
                use_reloader=False
            )
        except ImportError:
            print("❌ Admin panel module not found!")
            print("   Make sure admin_panel.py exists in the current directory")
        except Exception as e:
            print(f"❌ Failed to start admin panel: {e}")

    def start_integrated_system(self, auto_open=True):
        """Start the integrated system with admin panel as default"""
        print("🚀 Starting Integrated Video Anomaly Detection System...")
        print("   Admin Panel: http://localhost:5001 (Primary Interface)")
        print("   Video Analysis: http://localhost:5000 (Analysis Interface)")
        print("   Features:")
        print("   • Comprehensive admin dashboard")
        print("   • Real-time incident monitoring")
        print("   • Volunteer management & assignment")
        print("   • Video analysis integration")
        print("   • MP4 upload and live camera support")
        
        if auto_open:
            # Open admin panel by default
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open('http://localhost:5001')
                except:
                    pass
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Start both services
        try:
            # Start video analysis service in background
            def start_video_service():
                try:
                    import web_interface
                    web_interface.socketio.run(
                        web_interface.app, 
                        debug=False, 
                        host='0.0.0.0', 
                        port=5000,
                        use_reloader=False
                    )
                except Exception as e:
                    print(f"❌ Failed to start video analysis service: {e}")
            
            # Start admin panel service in foreground
            def start_admin_service():
                try:
                    import admin_panel
                    admin_panel.socketio.run(
                        admin_panel.app, 
                        debug=False, 
                        host='0.0.0.0', 
                        port=5001,
                        use_reloader=False
                    )
                except Exception as e:
                    print(f"❌ Failed to start admin panel: {e}")
            
            # Start video service in background thread
            video_thread = threading.Thread(target=start_video_service, daemon=True)
            video_thread.start()
            
            # Give video service time to start
            time.sleep(3)
            print("✅ Video Analysis Service started on port 5000")
            print("🚀 Starting Admin Panel on port 5001...")
            
            # Start admin service in main thread
            start_admin_service()
            
        except ImportError as e:
            print(f"❌ Required modules not found: {e}")
            print("   Make sure admin_panel.py and web_interface.py exist")
        except Exception as e:
            print(f"❌ Failed to start integrated system: {e}")

    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            print("\n" + "=" * 60)
            print("🎯 VIDEO ANOMALY DETECTION SYSTEM")
            print("=" * 60)
            print("Choose an option:")
            print("1. 🚀 Start Integrated System (Admin + Video Analysis)")
            print("2. 🛡️  Start Admin Panel Only")
            print("3. 🌐 Start Video Analysis Only")
            print("4. 📹 Live Camera Monitoring")
            print("5. 🎬 Analyze Video File")
            print("6. ⚙️  Show Configuration")
            print("7. 📖 Show Help")
            print("8. �  Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.start_integrated_system()
                break
            elif choice == '2':
                self.start_admin_panel()
                break
            elif choice == '3':
                self.start_web_interface()
                break
            elif choice == '4':
                camera_index = input("Enter camera index (0 for default, 1 for external): ").strip()
                try:
                    camera_index = int(camera_index) if camera_index else 0
                except ValueError:
                    camera_index = 0
                self.start_camera_monitoring(camera_index)
                break
            elif choice == '5':
                video_path = input("Enter path to video file: ").strip()
                if video_path:
                    self.analyze_video_file(video_path)
                else:
                    print("❌ No file path provided")
                break
            elif choice == '6':
                self.show_configuration()
            elif choice == '7':
                self.show_help()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-8.")
    
    def show_configuration(self):
        """Show current configuration"""
        print("\n" + "=" * 60)
        print("⚙️  CURRENT CONFIGURATION")
        print("=" * 60)
        print(f"🤖 Gemini Model: {Config.GEMINI_MODEL}")
        print(f"🔑 API Key: {'✅ Configured' if Config.GEMINI_API_KEY != 'your_api_key_here' else '❌ Not configured'}")
        print(f"⏱️  Analysis Interval: {Config.ANALYSIS_INTERVAL} seconds")
        print(f"🖼️  Frame Quality: {Config.FRAME_QUALITY}%")
        print(f"🎯 Confidence Threshold: {Config.CONFIDENCE_THRESHOLD}")
        print(f"⚠️  High Priority Threshold: {Config.HIGH_PRIORITY_THRESHOLD}")
        print(f"💾 Save Alerts to File: {Config.SAVE_ALERTS_TO_FILE}")
        print(f"🏟️  Event Type: {Config.EVENT_TYPE}")
        print(f"👥 Venue Capacity: {Config.VENUE_CAPACITY:,}")
        print(f"🔒 Security Level: {Config.SECURITY_LEVEL}")
        print("\n📝 To modify configuration, edit the .env file")
    
    def show_help(self):
        """Show help information"""
        print("\n" + "=" * 60)
        print("📖 HELP & USAGE GUIDE")
        print("=" * 60)
        print("🌐 WEB INTERFACE:")
        print("   • Upload MP4 files for analysis")
        print("   • Real-time monitoring dashboard")
        print("   • View analysis logs and statistics")
        print("   • Emergency alert notifications")
        
        print("\n📹 CAMERA MONITORING:")
        print("   • Live analysis of camera feed")
        print("   • Real-time anomaly detection")
        print("   • Detailed terminal logging")
        print("   • Automatic report generation")
        
        print("\n🎬 VIDEO FILE ANALYSIS:")
        print("   • Analyze pre-recorded videos")
        print("   • Supported formats: MP4, AVI, MOV, MKV, WMV, FLV")
        print("   • Frame-by-frame analysis")
        print("   • Comprehensive reporting")
        
        print("\n🚨 ANOMALY CATEGORIES:")
        categories = [
            "Crowd Control", "Security Threats", "Medical Emergencies",
            "Fire Hazards", "Structural Damage", "Weather Emergencies",
            "Vehicle Incidents", "Equipment Failures", "Unauthorized Access",
            "Violence/Aggression", "Stampede Risk", "Evacuation Scenarios"
        ]
        for i, category in enumerate(categories, 1):
            print(f"   {i:2d}. {category}")
        
        print("\n📊 SEVERITY LEVELS:")
        print("   1. Low - Minor issues, preventive measures needed")
        print("   2. Medium - Moderate concern, monitoring required")
        print("   3. High - Serious situation, immediate attention needed")
        print("   4. Critical - Dangerous situation, emergency response required")
        print("   5. Emergency - Life-threatening, immediate evacuation needed")
        
        print("\n🔧 TROUBLESHOOTING:")
        print("   • Ensure Gemini API key is configured in .env file")
        print("   • Check camera permissions and connections")
        print("   • Verify video file formats and integrity")
        print("   • Monitor API quota and rate limits")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Video Anomaly Detection System powered by Gemini 2.0 Flash",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive menu
  python main.py --web             # Start web interface
  python main.py --camera          # Start camera monitoring
  python main.py --camera 1        # Use external camera
  python main.py --video video.mp4 # Analyze video file

        """
    )
    
    parser.add_argument('--web', action='store_true', 
                       help='Start web interface')
    parser.add_argument('--camera', nargs='?', const=0, type=int, metavar='INDEX',
                       help='Start camera monitoring (optional camera index)')
    parser.add_argument('--video', type=str, metavar='PATH',
                       help='Analyze video file')

    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t auto-open browser for web interface')
    
    args = parser.parse_args()
    
    # Initialize system
    system = VideoAnomalySystem()
    system.print_banner()
    
    # Check requirements
    if not system.check_requirements():
        sys.exit(1)
    
    try:
        # Handle command line arguments
        if args.web:
            system.start_web_interface(auto_open=not args.no_browser)
        elif args.camera is not None:
            system.start_camera_monitoring(args.camera)
        elif args.video:
            system.analyze_video_file(args.video)

        else:
            # Start integrated system by default (admin panel + video analysis)
            print("🚀 Starting integrated system by default...")
            print("   Use --web for video analysis only")
            print("   Use python admin_panel.py for admin panel only")
            system.start_integrated_system(auto_open=not args.no_browser)
            
    except KeyboardInterrupt:
        print("\n🛑 System interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")
    finally:
        print("\n👋 Thank you for using Video Anomaly Detection System!")

if __name__ == "__main__":
    main()