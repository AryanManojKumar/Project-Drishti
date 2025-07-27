"""
Simple script to run complete crowd analysis
Bhai, yeh script sab kuch ek saath run karega
"""

import os
import json
import time
from datetime import datetime
from typing import Dict

# Import our analysis modules
try:
    from map_crowd_analyzer import analyze_complete_crowd_situation
    from crowd_predictor import get_crowd_density
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are present")
    exit(1)

def run_complete_analysis():
    """Run complete unified analysis with all features"""
    
    print("🎯 Complete Unified Crowd Analysis System")
    print("=" * 60)
    print("Public Safety Monitoring with AI-powered Analysis")
    print("Real Maps Data + Video Analysis + Map Analysis + Density Overlay")
    print("=" * 60)
    
    # Configuration
    map_path = "src/Screenshot 2025-07-23 064906.png"
    video_source = 0  # Webcam
    analysis_duration = 20  # seconds
    
    # Location coordinates (Delhi example)
    latitude = 28.6139
    longitude = 77.2090
    
    try:
        # Import unified analyzer
        from unified_crowd_analyzer import run_unified_analysis
        
        print("🚀 Starting Unified Analysis...")
        print("This will combine:")
        print("• 🗺️ Map analysis with venue layout")
        print("• 🎥 Real-time video analysis")
        print("• 🌍 Google Maps crowd data")
        print("• 🎨 Color-coded density overlay")
        print("• 🔍 Advanced anomaly detection")
        print()
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        print("🔴 Analysis started!")
        
        # Run unified analysis
        results = run_unified_analysis(
            map_image_path=map_path if os.path.exists(map_path) else None,
            video_source=video_source,
            location_coords=(latitude, longitude),
            analysis_duration=analysis_duration
        )
        
        print("\n" + "="*60)
        print("📊 UNIFIED ANALYSIS RESULTS")
        print("="*60)
        
        # Display unified results
        display_unified_results(results)
        
        # Save results
        save_unified_results(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during unified analysis: {e}")
        return {'error': str(e), 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

def display_unified_results(results: Dict):
    """Display unified analysis results"""
    
    try:
        # Basic info
        print(f"⏰ Analysis Time: {results.get('analysis_timestamp', 'Unknown')}")
        print(f"📊 Data Sources: {', '.join(results.get('input_sources', []))}")
        print(f"🎯 Confidence Score: {results.get('confidence_score', 0):.2f}")
        
        # Final assessment
        final_assessment = results.get('final_assessment', {})
        if final_assessment:
            print(f"\n🎯 FINAL ASSESSMENT:")
            print(f"   Status: {final_assessment.get('overall_status', 'Unknown')}")
            print(f"   Severity: {final_assessment.get('severity_level', 0)}/10")
            print(f"   Next Review: {final_assessment.get('next_review_time', 'Unknown')}")
        
        # Unified metrics
        unified_metrics = results.get('unified_metrics', {})
        if unified_metrics:
            print(f"\n📊 UNIFIED METRICS:")
            print(f"   👥 Total People Estimate: {unified_metrics.get('total_people_estimate', 0)}")
            print(f"   📈 Crowd Density Score: {unified_metrics.get('crowd_density_score', 0):.1f}%")
            print(f"   ⚠️ Safety Risk Score: {unified_metrics.get('safety_risk_score', 0):.1f}%")
            print(f"   🌊 Flow Efficiency: {unified_metrics.get('flow_efficiency_score', 0):.1f}%")
            print(f"   🏢 Venue Utilization: {unified_metrics.get('venue_capacity_utilization', 0):.1f}%")
            print(f"   🚨 Alert Level: {unified_metrics.get('alert_level', 'normal').upper()}")
        
        # Combined insights
        combined_insights = results.get('combined_insights', {})
        if combined_insights:
            print(f"\n🧠 SITUATION SUMMARY:")
            print(f"   {combined_insights.get('crowd_situation_summary', 'No summary available')}")
            
            # Key findings
            key_findings = combined_insights.get('key_findings', [])
            if key_findings:
                print(f"\n🔍 KEY FINDINGS:")
                for i, finding in enumerate(key_findings[:5], 1):
                    print(f"   {i}. {finding}")
            
            # Risk assessment
            risk_assessment = combined_insights.get('risk_assessment', {})
            if risk_assessment:
                print(f"\n⚠️ RISK ASSESSMENT:")
                print(f"   Risk Level: {risk_assessment.get('overall_risk_level', 'Unknown')}")
                print(f"   Risk Score: {risk_assessment.get('risk_score', 0):.1f}/100")
                print(f"   Mitigation Priority: {risk_assessment.get('mitigation_priority', 'Unknown')}")
            
            # Location hotspots
            location_hotspots = combined_insights.get('location_hotspots', [])
            if location_hotspots:
                print(f"\n🔥 CROWD HOTSPOTS:")
                for i, hotspot in enumerate(location_hotspots[:3], 1):
                    print(f"   {i}. {hotspot.get('name', 'Unknown')}: {hotspot.get('estimated_people', 0)} people ({hotspot.get('level', 'unknown')} level)")
        
        # Actionable recommendations
        recommendations = results.get('actionable_recommendations', [])
        if recommendations:
            print(f"\n💡 ACTIONABLE RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:8], 1):
                print(f"   {i}. {rec}")
        
        # Individual analyses summary
        individual_analyses = results.get('individual_analyses', {})
        if individual_analyses:
            print(f"\n📋 INDIVIDUAL ANALYSIS SUMMARY:")
            
            if 'video_analysis' in individual_analyses:
                video = individual_analyses['video_analysis']
                print(f"   🎥 Video: {video.get('people_count', 0)} people, {video.get('density_score', 0)}/100 density")
            
            if 'maps_crowd_data' in individual_analyses:
                maps_data = individual_analyses['maps_crowd_data']
                print(f"   🌍 Maps: {maps_data.get('total_estimated_people', 0)} estimated people in area")
            
            if 'map_analysis' in individual_analyses:
                map_data = individual_analyses['map_analysis']
                if 'map_analysis' in map_data:
                    map_info = map_data['map_analysis']
                    print(f"   🗺️ Map: {map_info.get('density_rating', 0)}/10 density, {map_info.get('safety_score', 0)}/10 safety")
        
        # Density overlay info
        overlay_path = results.get('density_overlay_path')
        if overlay_path:
            print(f"\n🎨 DENSITY OVERLAY:")
            print(f"   Color-coded map created: {overlay_path}")
            print(f"   🔴 Red: Critical density zones")
            print(f"   🟠 Orange: High density zones")
            print(f"   🟡 Yellow: Medium density zones")
            print(f"   🟢 Green: Low density zones")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Error displaying results: {e}")

def save_unified_results(results: Dict):
    """Save unified results to file"""
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"unified_crowd_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Complete unified results saved to: {filename}")
        
        # Also save a summary file
        summary_filename = f"analysis_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write("UNIFIED CROWD ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            # Basic info
            f.write(f"Analysis Time: {results.get('analysis_timestamp', 'Unknown')}\n")
            f.write(f"Data Sources: {', '.join(results.get('input_sources', []))}\n")
            f.write(f"Confidence Score: {results.get('confidence_score', 0):.2f}\n\n")
            
            # Final assessment
            final_assessment = results.get('final_assessment', {})
            if final_assessment:
                f.write("FINAL ASSESSMENT:\n")
                f.write(f"Status: {final_assessment.get('overall_status', 'Unknown')}\n")
                f.write(f"Severity: {final_assessment.get('severity_level', 0)}/10\n\n")
            
            # Unified metrics
            unified_metrics = results.get('unified_metrics', {})
            if unified_metrics:
                f.write("UNIFIED METRICS:\n")
                f.write(f"Total People Estimate: {unified_metrics.get('total_people_estimate', 0)}\n")
                f.write(f"Crowd Density Score: {unified_metrics.get('crowd_density_score', 0):.1f}%\n")
                f.write(f"Alert Level: {unified_metrics.get('alert_level', 'normal').upper()}\n\n")
            
            # Recommendations
            recommendations = results.get('actionable_recommendations', [])
            if recommendations:
                f.write("TOP RECOMMENDATIONS:\n")
                for i, rec in enumerate(recommendations[:5], 1):
                    f.write(f"{i}. {rec}\n")
        
        print(f"📄 Analysis summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def combine_analysis_results(map_analysis, video_analysis):
    """Combine map and video analysis results"""
    
    combined = {
        'overall_crowd_score': 0,
        'risk_level': 'low',
        'confidence': 0,
        'data_sources': [],
        'key_metrics': {}
    }
    
    scores = []
    
    # Map analysis contribution
    if map_analysis and 'map_analysis' in map_analysis:
        map_data = map_analysis['map_analysis']
        
        if 'density_rating' in map_data:
            map_score = map_data['density_rating'] * 10
            scores.append(map_score)
            combined['data_sources'].append('map_analysis')
            combined['key_metrics']['map_density_rating'] = map_data['density_rating']
        
        if 'safety_score' in map_data:
            combined['key_metrics']['map_safety_score'] = map_data['safety_score']
    
    # Video analysis contribution
    if video_analysis:
        video_score = video_analysis.get('density_score', 0)
        if video_score > 0:
            scores.append(video_score)
            combined['data_sources'].append('video_analysis')
            combined['key_metrics']['video_density_score'] = video_score
            combined['key_metrics']['people_count'] = video_analysis.get('people_count', 0)
    
    # Calculate overall score
    if scores:
        combined['overall_crowd_score'] = sum(scores) / len(scores)
        combined['confidence'] = len(scores) * 0.5  # Higher confidence with more data sources
        
        # Categorize risk level
        if combined['overall_crowd_score'] >= 80:
            combined['risk_level'] = 'critical'
        elif combined['overall_crowd_score'] >= 60:
            combined['risk_level'] = 'high'
        elif combined['overall_crowd_score'] >= 40:
            combined['risk_level'] = 'medium'
        else:
            combined['risk_level'] = 'low'
    
    return combined

def detect_anomalies_simple(combined_analysis):
    """Simple anomaly detection based on combined analysis"""
    
    anomalies = []
    
    overall_score = combined_analysis.get('overall_crowd_score', 0)
    people_count = combined_analysis.get('key_metrics', {}).get('people_count', 0)
    
    # High crowd density anomaly
    if overall_score >= 80:
        anomalies.append({
            'type': 'critical_crowd_density',
            'severity': 'critical',
            'description': f'Crowd density score ({overall_score:.1f}) exceeds critical threshold',
            'recommendation': 'Immediate crowd control measures required',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    elif overall_score >= 60:
        anomalies.append({
            'type': 'high_crowd_density',
            'severity': 'warning',
            'description': f'Crowd density score ({overall_score:.1f}) is elevated',
            'recommendation': 'Enhanced monitoring and security presence needed',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    # High people count anomaly
    if people_count > 50:
        anomalies.append({
            'type': 'high_people_count',
            'severity': 'warning',
            'description': f'High number of people detected ({people_count})',
            'recommendation': 'Monitor crowd movement and prepare crowd management',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    # Low confidence anomaly
    confidence = combined_analysis.get('confidence', 0)
    if confidence < 0.3:
        anomalies.append({
            'type': 'low_confidence',
            'severity': 'info',
            'description': f'Analysis confidence is low ({confidence:.2f})',
            'recommendation': 'Verify with additional data sources',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    return anomalies

def generate_recommendations(combined_analysis, anomalies):
    """Generate actionable recommendations"""
    
    recommendations = []
    
    risk_level = combined_analysis.get('risk_level', 'low')
    overall_score = combined_analysis.get('overall_crowd_score', 0)
    
    # Risk-based recommendations
    if risk_level == 'critical':
        recommendations.extend([
            "🚨 CRITICAL: Deploy emergency crowd control immediately",
            "🚫 Consider restricting venue access to prevent overcrowding",
            "📢 Activate emergency communication systems",
            "👮 Increase security personnel by 200%",
            "🚪 Ensure all emergency exits are clear and accessible"
        ])
    elif risk_level == 'high':
        recommendations.extend([
            "⚠️ HIGH ALERT: Enhance security presence in all areas",
            "👁️ Implement continuous crowd monitoring",
            "📋 Review and prepare emergency procedures",
            "🚧 Set up crowd flow management barriers if needed"
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            "📊 MODERATE: Continue active monitoring",
            "👮 Maintain standard security protocols",
            "📱 Keep communication channels open with security team"
        ])
    else:
        recommendations.extend([
            "✅ NORMAL: Continue routine monitoring",
            "📋 Maintain standard operating procedures"
        ])
    
    # Anomaly-specific recommendations
    for anomaly in anomalies:
        if anomaly['severity'] in ['critical', 'warning']:
            recommendations.append(f"🎯 {anomaly['type'].replace('_', ' ').title()}: {anomaly['recommendation']}")
    
    return recommendations

def determine_alert_level(combined_analysis, anomalies):
    """Determine overall alert level"""
    
    risk_level = combined_analysis.get('risk_level', 'low')
    critical_anomalies = [a for a in anomalies if a['severity'] == 'critical']
    warning_anomalies = [a for a in anomalies if a['severity'] == 'warning']
    
    if risk_level == 'critical' or critical_anomalies:
        return 'emergency'
    elif risk_level == 'high' or len(warning_anomalies) >= 2:
        return 'warning'
    elif risk_level == 'medium' or warning_anomalies:
        return 'caution'
    else:
        return 'normal'

def display_final_results(results):
    """Display comprehensive final results"""
    
    print("\n" + "=" * 60)
    print("📊 FINAL ANALYSIS RESULTS")
    print("=" * 60)
    
    # Basic info
    print(f"⏰ Analysis Time: {results['timestamp']}")
    print(f"🚨 Alert Level: {results['alert_level'].upper()}")
    
    # Combined analysis
    combined = results.get('combined_results', {})
    if combined:
        print(f"\n🧠 COMBINED ANALYSIS:")
        print(f"   Overall Crowd Score: {combined.get('overall_crowd_score', 0):.1f}/100")
        print(f"   Risk Level: {combined.get('risk_level', 'unknown').upper()}")
        print(f"   Confidence: {combined.get('confidence', 0):.2f}")
        print(f"   Data Sources: {', '.join(combined.get('data_sources', []))}")
        
        # Key metrics
        metrics = combined.get('key_metrics', {})
        if metrics:
            print(f"\n📊 KEY METRICS:")
            for key, value in metrics.items():
                formatted_key = key.replace('_', ' ').title()
                print(f"   {formatted_key}: {value}")
    
    # Anomalies
    anomalies = results.get('anomalies_detected', [])
    if anomalies:
        print(f"\n🔍 ANOMALIES DETECTED ({len(anomalies)}):")
        for i, anomaly in enumerate(anomalies, 1):
            severity_icon = "🚨" if anomaly['severity'] == 'critical' else "⚠️" if anomaly['severity'] == 'warning' else "ℹ️"
            print(f"   {i}. {severity_icon} {anomaly['type'].replace('_', ' ').title()}")
            print(f"      {anomaly['description']}")
    else:
        print(f"\n✅ NO ANOMALIES DETECTED")
    
    # Recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)

def save_results(results):
    """Save results to JSON file"""
    
    try:
        filename = f"crowd_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def test_density_overlay():
    """Test density overlay feature"""
    print("\n🎨 Testing Density Overlay Feature")
    print("-" * 40)
    
    try:
        from src.map_density_overlay import create_map_overlay
        
        # Sample analysis data
        sample_analysis = {
            'alert_level': 'warning',
            'map_analysis': {
                'density_rating': 7,
                'safety_score': 6,
                'density_zones': {
                    'high_density': ['Main entrance', 'Central stage area'],
                    'medium_density': ['Side corridors', 'Food court'],
                    'low_density': ['Outer areas', 'Parking zones']
                },
                'risk_assessment': {
                    'high_risk_areas': ['Narrow exit', 'Bottleneck near stage']
                },
                'flow_analysis': {
                    'bottlenecks': ['Exit gate 2', 'Main corridor']
                }
            }
        }
        
        sample_video = {
            'people_count': 45,
            'density_score': 72,
            'alert_status': 'warning'
        }
        
        map_path = "src/Screenshot 2025-07-23 064906.png"
        
        if os.path.exists(map_path):
            print("📍 Creating density overlay...")
            overlay_path = create_map_overlay(map_path, sample_analysis, sample_video)
            
            if overlay_path and os.path.exists(overlay_path):
                print(f"✅ Density overlay created: {overlay_path}")
                print("🎨 Features included:")
                print("   • Color-coded density zones (Red/Orange/Yellow/Green)")
                print("   • Analysis information overlay")
                print("   • Density legend")
                print("   • Alert level indicators")
                return overlay_path
            else:
                print("⚠️ Overlay creation failed, using original map")
                return map_path
        else:
            print(f"❌ Map file not found: {map_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing density overlay: {e}")
        return None

def main():
    """Enhanced main function with multiple options"""
    
    print("🎯 Advanced Crowd Analysis System")
    print("=" * 60)
    print("Public Safety Monitoring with AI-powered Analysis")
    print("=" * 60)
    print()
    print("Available Options:")
    print("1. 🚀 Complete Analysis (Map + Video + Anomaly Detection)")
    print("2. 🗺️ Map Analysis Only (Quick)")
    print("3. 🎥 Video Analysis Only")
    print("4. 🎨 Test Density Overlay Feature")
    print("5. 🌐 Launch Web UI")
    print("6. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                print("\n🚀 Starting Complete Analysis...")
                results = run_complete_analysis()
                
                if 'error' not in results:
                    print("\n🎉 Complete analysis finished successfully!")
                    
                    # Test density overlay
                    print("\n🎨 Creating density overlay...")
                    overlay_path = test_density_overlay()
                    if overlay_path:
                        print(f"📸 Density overlay saved: {overlay_path}")
                else:
                    print(f"\n❌ Analysis failed: {results['error']}")
                
                break
                
            elif choice == '2':
                print("\n🗺️ Starting Map Analysis Only...")
                map_path = "src/Screenshot 2025-07-23 064906.png"
                
                if os.path.exists(map_path):
                    from map_crowd_analyzer import analyze_complete_crowd_situation
                    
                    result = analyze_complete_crowd_situation(
                        map_image_path=map_path,
                        video_source=None,
                        duration=0
                    )
                    
                    print("✅ Map Analysis Complete!")
                    if 'map_analysis' in result:
                        map_data = result['map_analysis']
                        print(f"📊 Density Rating: {map_data.get('density_rating', 'N/A')}/10")
                        print(f"🛡️ Safety Score: {map_data.get('safety_score', 'N/A')}/10")
                        print(f"🚨 Alert Level: {result.get('alert_level', 'normal').upper()}")
                    
                    # Create overlay
                    overlay_path = test_density_overlay()
                    if overlay_path:
                        print(f"🎨 Density overlay created: {overlay_path}")
                else:
                    print(f"❌ Map file not found: {map_path}")
                
                break
                
            elif choice == '3':
                print("\n🎥 Starting Video Analysis Only...")
                print("📹 This will use your webcam for 15 seconds...")
                
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm == 'y':
                    from crowd_predictor import get_crowd_density
                    
                    result = get_crowd_density(video_source=0)
                    
                    print("✅ Video Analysis Complete!")
                    print(f"👥 People Count: {result.get('people_count', 0)}")
                    print(f"📊 Density Score: {result.get('density_score', 0)}/100")
                    print(f"🚨 Alert Status: {result.get('alert_status', 'normal').upper()}")
                else:
                    print("Video analysis cancelled.")
                
                break
                
            elif choice == '4':
                print("\n🎨 Testing Density Overlay Feature...")
                overlay_path = test_density_overlay()
                
                if overlay_path:
                    print(f"✅ Test completed! Check the overlay image: {overlay_path}")
                    print("🎨 The overlay includes:")
                    print("   • Red zones: Critical density areas")
                    print("   • Orange zones: High density areas")
                    print("   • Yellow zones: Medium density areas")
                    print("   • Green zones: Low density areas")
                    print("   • Analysis information panel")
                    print("   • Color legend")
                else:
                    print("❌ Overlay test failed")
                
                break
                
            elif choice == '5':
                print("\n🌐 Launching Web UI...")
                print("📋 Prerequisites:")
                print("1. Install UI requirements: pip install -r requirements-ui.txt")
                print("2. Run command: streamlit run main.py")
                print()
                print("🚀 Web UI Features:")
                print("• 📊 Real-time Dashboard")
                print("• 🎥 Live Video Analysis (with file upload)")
                print("• 🗺️ Map Analysis with Density Overlay")
                print("• 🔍 Anomaly Detection System")
                print("• 📚 Historical Data Analysis")
                print()
                
                launch = input("Install requirements and launch now? (y/n): ").strip().lower()
                if launch == 'y':
                    try:
                        import subprocess
                        print("📦 Installing requirements...")
                        subprocess.run(["pip", "install", "-r", "requirements-ui.txt"], check=True)
                        print("🚀 Launching Streamlit...")
                        subprocess.run(["streamlit", "run", "main.py"])
                    except Exception as e:
                        print(f"❌ Error launching UI: {e}")
                        print("💡 Manual steps:")
                        print("1. pip install -r requirements-ui.txt")
                        print("2. streamlit run main.py")
                
                break
                
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()