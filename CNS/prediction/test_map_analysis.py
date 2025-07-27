"""
Quick test script for your map analysis
Bhai, yeh script tera screenshot analyze karega
"""

import os
from map_crowd_analyzer import analyze_complete_crowd_situation

def test_your_map():
    """Test function for your specific map"""
    
    print("🎯 Testing Your Map for Crowd Analysis")
    print("=" * 50)
    
    # Your screenshot path
    map_path = "src/Screenshot 2025-07-23 064906.png"
    
    # Check if file exists
    if not os.path.exists(map_path):
        print(f"❌ Screenshot not found at: {map_path}")
        print("Please check if the file exists.")
        return
    
    print(f"📍 Found your map: {map_path}")
    print("🚀 Starting analysis...")
    
    try:
        # Run analysis (without video for quick test)
        result = analyze_complete_crowd_situation(
            map_image_path=map_path,
            video_source=None,  # Skip video for quick test
            duration=0  # No video analysis
        )
        
        print("\n" + "="*60)
        print("📊 YOUR MAP ANALYSIS RESULTS")
        print("="*60)
        
        # Basic info
        print(f"⏰ Analysis Time: {result['timestamp']}")
        print(f"🚨 Alert Level: {result['alert_level'].upper()}")
        
        # Map analysis details
        if 'map_analysis' in result and result['map_analysis']:
            map_data = result['map_analysis']
            print(f"\n📍 MAP ANALYSIS:")
            
            if 'density_rating' in map_data:
                print(f"   Density Rating: {map_data['density_rating']}/10")
            
            if 'safety_score' in map_data:
                print(f"   Safety Score: {map_data['safety_score']}/10")
            
            if 'venue_type' in map_data:
                print(f"   Venue Type: {map_data['venue_type']}")
            
            if 'capacity_estimate' in map_data:
                print(f"   Estimated Capacity: {map_data['capacity_estimate']}")
            
            # High-risk areas
            if 'high_risk_areas' in map_data and map_data['high_risk_areas']:
                print(f"\n⚠️  HIGH RISK AREAS:")
                for i, area in enumerate(map_data['high_risk_areas'][:5], 1):
                    print(f"   {i}. {area}")
            
            # Bottlenecks
            if 'bottlenecks' in map_data and map_data['bottlenecks']:
                print(f"\n🚧 POTENTIAL BOTTLENECKS:")
                for i, bottleneck in enumerate(map_data['bottlenecks'][:5], 1):
                    print(f"   {i}. {bottleneck}")
            
            # Entry/Exit points
            if 'entry_exit_points' in map_data and map_data['entry_exit_points']:
                print(f"\n🚪 ENTRY/EXIT POINTS:")
                for i, point in enumerate(map_data['entry_exit_points'][:5], 1):
                    print(f"   {i}. {point}")
        
        # Combined insights
        if 'combined_insights' in result:
            insights = result['combined_insights']
            print(f"\n🧠 COMBINED INSIGHTS:")
            print(f"   Overall Crowd Level: {insights.get('overall_crowd_level', 'Unknown')}")
            print(f"   Risk Assessment: {insights.get('risk_assessment', 'Unknown')}")
            
            if 'key_findings' in insights and insights['key_findings']:
                print(f"\n🔍 KEY FINDINGS:")
                for finding in insights['key_findings']:
                    print(f"   • {finding}")
        
        # Recommendations
        if 'recommendations' in result and result['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'][:8], 1):
                print(f"   {i}. {rec}")
        
        # Error handling
        if 'error' in result:
            print(f"\n❌ Error occurred: {result['error']}")
        
        print("\n" + "="*60)
        print("✅ Analysis Complete!")
        
        # Save results to file
        import json
        with open('map_analysis_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("📄 Results saved to: map_analysis_results.json")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def test_with_video():
    """Test with video analysis included"""
    
    print("🎥 Testing with Video Analysis")
    print("=" * 40)
    
    map_path = "src/Screenshot 2025-07-23 064906.png"
    
    if not os.path.exists(map_path):
        print(f"❌ Map not found: {map_path}")
        return
    
    print("📹 This will use your webcam for 15 seconds...")
    input("Press Enter to start video analysis (or Ctrl+C to cancel)...")
    
    try:
        result = analyze_complete_crowd_situation(
            map_image_path=map_path,
            video_source=0,  # Webcam
            duration=15  # 15 seconds
        )
        
        print(f"\n📊 COMPLETE ANALYSIS RESULTS:")
        print(f"Alert Level: {result['alert_level'].upper()}")
        
        # Video results
        if 'video_analysis' in result:
            video = result['video_analysis']
            print(f"\n🎥 VIDEO ANALYSIS:")
            print(f"   Average People Count: {video.get('average_people_count', 0)}")
            print(f"   Max People Count: {video.get('max_people_count', 0)}")
            print(f"   Crowd Stability: {video.get('crowd_stability', 'Unknown')}")
        
        # Combined insights
        if 'combined_insights' in result:
            insights = result['combined_insights']
            print(f"\n🧠 FINAL ASSESSMENT:")
            print(f"   Crowd Level: {insights.get('overall_crowd_level', 'Unknown')}")
            print(f"   Risk Level: {insights.get('risk_assessment', 'Unknown')}")
            print(f"   Confidence: {insights.get('confidence_score', 0):.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 Map Crowd Analysis Tester")
    print("Choose an option:")
    print("1. Quick map analysis only")
    print("2. Complete analysis with video")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_your_map()
    elif choice == "2":
        test_with_video()
    else:
        print("Invalid choice. Running quick map analysis...")
        test_your_map()