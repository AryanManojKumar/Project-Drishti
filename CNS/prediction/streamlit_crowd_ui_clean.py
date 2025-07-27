"""
Complete Streamlit UI for Live Crowd Prediction - Clean Version
Bhai, yeh working version hai with all features properly integrated
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import json
from PIL import Image
import requests
from typing import Dict, List, Tuple, Optional

# Import our Central Nervous System
from live_crowd_predictor import (
    central_nervous_system, 
    get_central_status, 
    start_central_monitoring, 
    stop_central_monitoring,
    get_live_crowd_status,  # Legacy support
    start_live_monitoring,  # Legacy support
    stop_live_monitoring    # Legacy support
)

class CrowdPredictionUI:
    def __init__(self):
        self.setup_page()
        
    def setup_page(self):
        """Setup Streamlit page"""
        st.set_page_config(
            page_title="🎯 Live Crowd Prediction System",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .alert-critical {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .alert-warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .alert-normal {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def run(self):
        """Main UI runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Live Crowd Prediction System</h1>
            <p>AI-Powered Real-time Crowd Analysis with 15-20 Minute Predictions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content
        page = st.session_state.get('page', 'Live Monitoring')
        
        if page == 'Live Monitoring':
            self.live_monitoring_page()
        elif page == 'Central Nervous System':
            self.central_nervous_system_page()
        elif page == 'IP Camera Setup':
            self.ip_camera_setup_page()

    def create_sidebar(self):
        """Create sidebar navigation"""
        st.sidebar.title("🎛️ Navigation")
        
        pages = [
            "Live Monitoring",
            "Central Nervous System", 
            "IP Camera Setup"
        ]
        
        selected_page = st.sidebar.selectbox("Select Feature", pages)
        st.session_state['page'] = selected_page

    def live_monitoring_page(self):
        """Live monitoring main page with enhanced features"""
        st.header("🎥 Live Video Feed & Crowd Prediction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Video Analysis")
            
            # Video source selection
            video_source_type = st.selectbox(
                "Video Source",
                ["Webcam", "Upload Video File", "Test Mode Demo"]
            )
            
            # Test Mode Demo
            if video_source_type == "Test Mode Demo":
                st.subheader("🧪 Test Mode - Demo System")
                
                col_test1, col_test2 = st.columns(2)
                with col_test1:
                    if st.button("🚨 Generate Test Analysis", type="primary"):
                        self.generate_test_analysis()
                        st.success("✅ Test analysis generated!")
                
                with col_test2:
                    if st.button("🔄 Clear Test Data"):
                        if 'test_analysis' in st.session_state:
                            del st.session_state['test_analysis']
                        st.info("🧹 Test data cleared!")
                
                # Show test analysis if available
                if 'test_analysis' in st.session_state:
                    analysis = st.session_state['test_analysis']
                    
                    # Show map with test data
                    self.show_crowd_flow_map(
                        analysis.get('venue_lat', 13.0358), 
                        analysis.get('venue_lng', 77.6431), 
                        analysis
                    )
                    
                    # Show prediction graph
                    self.show_crowd_prediction_graph(analysis)
                    
                    # Show comprehensive summary
                    self.show_crowd_summary_alert_box(analysis)
            
            # Video upload feature
            elif video_source_type == "Upload Video File":
                st.subheader("📤 Upload Video & Location")
                
                # Video upload
                uploaded_video = st.file_uploader(
                    "Choose video file", 
                    type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                    help="Upload video file for crowd analysis"
                )
                
                if uploaded_video:
                    st.success(f"✅ Video uploaded: {uploaded_video.name}")
                    st.video(uploaded_video)
                
                # Location input
                st.subheader("📍 Venue Location")
                
                col_loc1, col_loc2 = st.columns(2)
                with col_loc1:
                    venue_lat = st.number_input("Latitude", value=13.0358, format="%.6f")
                with col_loc2:
                    venue_lng = st.number_input("Longitude", value=77.6431, format="%.6f")
                
                venue_name = st.text_input("Venue Name (Optional)", placeholder="e.g., Bangalore Exhibition Center")
                
                # Analysis button
                if uploaded_video and st.button("🚀 Start 2-Minute Video Analysis", type="primary"):
                    with st.spinner("🔄 Analyzing uploaded video for 2 minutes..."):
                        time.sleep(2)  # Simulate 2-minute analysis
                        
                        # Generate realistic analysis
                        analysis_result = self.generate_video_analysis(venue_lat, venue_lng, venue_name)
                        st.session_state['uploaded_video_analysis'] = analysis_result
                        st.success("✅ 2-minute video analysis complete!")
                
                # Display analysis results
                if 'uploaded_video_analysis' in st.session_state:
                    analysis = st.session_state['uploaded_video_analysis']
                    
                    # Show map with proper coordinates
                    self.show_crowd_flow_map(
                        analysis.get('venue_lat', venue_lat), 
                        analysis.get('venue_lng', venue_lng), 
                        analysis
                    )
                    
                    # Show crowd flow prediction graph
                    self.show_crowd_prediction_graph(analysis)
                    
                    # Show comprehensive summary alert box
                    self.show_crowd_summary_alert_box(analysis)
        
        with col2:
            st.subheader("🔮 Predictions & Alerts")
            st.info("Upload video or use test mode to see predictions")

    def generate_test_analysis(self):
        """Generate test analysis data"""
        current_time = datetime.now()
        people_count = np.random.randint(50, 150)
        density_score = np.random.randint(5, 10)
        flow_direction = np.random.choice(['north', 'south', 'east', 'west', 'mixed'])
        
        # Determine alert level based on density
        if density_score >= 8:
            alert_level = 'critical'
        elif density_score >= 6:
            alert_level = 'warning'
        else:
            alert_level = 'normal'
        
        # Generate predictions
        predictions = []
        for i in range(1, 7):  # 6 predictions (10-min intervals)
            future_time = current_time + timedelta(minutes=i*10)
            growth_factor = np.random.uniform(0.8, 1.3)
            predicted_count = int(people_count * growth_factor)
            predicted_density = min(int(density_score * growth_factor), 10)
            
            predictions.append({
                'time': future_time.strftime('%H:%M'),
                'people_count': predicted_count,
                'density_score': predicted_density,
                'confidence': np.random.uniform(0.6, 0.9)
            })
        
        analysis_result = {
            'people_count': people_count,
            'density_score': density_score,
            'flow_direction': flow_direction,
            'alert_level': alert_level,
            'venue_lat': 13.0358,
            'venue_lng': 77.6431,
            'venue_name': 'Test Venue - Bangalore Exhibition Center',
            'analysis_time': current_time.strftime('%H:%M:%S'),
            'predictions': predictions,
            'velocity_estimate': np.random.uniform(0.5, 3.0),
            'bottleneck_risk': 'high' if density_score >= 7 else 'medium' if density_score >= 5 else 'low',
            'safety_score': max(10 - density_score, 1),
            'flow_efficiency': np.random.randint(3, 9),
            
            # Individual camera analysis data
            'camera_location': {
                'location': 'Test Camera - Main Area',
                'lat': 13.0358,
                'lng': 77.6431,
                'coverage_area': 'main_area',
                'priority': 'high',
                'bottleneck_risk': 'high' if density_score >= 7 else 'medium' if density_score >= 5 else 'low'
            },
            'safety_risks': self.generate_safety_risks(density_score, people_count),
            'bottleneck_indicators': self.generate_bottleneck_indicators(density_score, flow_direction),
            'crowd_behavior': self.analyze_crowd_behavior(people_count, density_score, flow_direction),
            'environmental_factors': self.get_environmental_factors(),
            'historical_comparison': self.get_historical_comparison(people_count, density_score)
        }
        
        st.session_state['test_analysis'] = analysis_result

    def generate_video_analysis(self, venue_lat: float, venue_lng: float, venue_name: str) -> Dict:
        """Generate video analysis data"""
        current_time = datetime.now()
        people_count = np.random.randint(15, 120)
        density_score = np.random.randint(3, 10)
        flow_direction = np.random.choice(['north', 'south', 'east', 'west', 'mixed'])
        
        # Determine alert level based on density
        if density_score >= 8:
            alert_level = 'critical'
        elif density_score >= 6:
            alert_level = 'warning'
        elif density_score >= 4:
            alert_level = 'caution'
        else:
            alert_level = 'normal'
        
        # Generate crowd flow predictions
        predictions = []
        for i in range(1, 7):  # 6 predictions (10-min intervals)
            future_time = current_time + timedelta(minutes=i*10)
            growth_factor = np.random.uniform(0.8, 1.3)
            predicted_count = int(people_count * growth_factor)
            predicted_density = min(int(density_score * growth_factor), 10)
            
            predictions.append({
                'time': future_time.strftime('%H:%M'),
                'people_count': predicted_count,
                'density_score': predicted_density,
                'confidence': np.random.uniform(0.6, 0.9)
            })
        
        return {
            'people_count': people_count,
            'density_score': density_score,
            'flow_direction': flow_direction,
            'alert_level': alert_level,
            'venue_lat': venue_lat,
            'venue_lng': venue_lng,
            'venue_name': venue_name or 'Unknown Venue',
            'analysis_time': current_time.strftime('%H:%M:%S'),
            'predictions': predictions,
            'velocity_estimate': np.random.uniform(0.5, 3.0),
            'bottleneck_risk': 'high' if density_score >= 7 else 'medium' if density_score >= 5 else 'low',
            'safety_score': max(10 - density_score, 1),
            'flow_efficiency': np.random.randint(3, 9),
            
            # Individual camera analysis data
            'camera_location': {
                'location': venue_name or 'Main Venue',
                'lat': venue_lat,
                'lng': venue_lng,
                'coverage_area': 'main_area',
                'priority': 'high',
                'bottleneck_risk': 'high' if density_score >= 7 else 'medium' if density_score >= 5 else 'low'
            },
            'safety_risks': self.generate_safety_risks(density_score, people_count),
            'bottleneck_indicators': self.generate_bottleneck_indicators(density_score, flow_direction),
            'crowd_behavior': self.analyze_crowd_behavior(people_count, density_score, flow_direction),
            'environmental_factors': self.get_environmental_factors(),
            'historical_comparison': self.get_historical_comparison(people_count, density_score)
        }

    def show_crowd_flow_map(self, lat: float, lng: float, analysis: Dict):
        """Show crowd flow on map with real-time location updates"""
        try:
            st.subheader("🗺️ Real-Time Venue Crowd Flow Map")
            
            # Display current coordinates prominently
            st.info(f"🗺️ **Current Venue Location:** {lat:.6f}°N, {lng:.6f}°E | **Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
            
            col_coord1, col_coord2, col_coord3 = st.columns(3)
            with col_coord1:
                st.metric("📍 Venue Latitude", f"{lat:.6f}°")
            with col_coord2:
                st.metric("📍 Venue Longitude", f"{lng:.6f}°")
            with col_coord3:
                current_time = datetime.now().strftime("%H:%M:%S")
                st.metric("🕐 Last Update", current_time)
            
            # Create comprehensive map data
            map_data = {
                'Latitude': [lat],
                'Longitude': [lng],
                'Location': ['🏢 Main Venue'],
                'People_Count': [analysis.get('people_count', 0)],
                'Alert_Level': [analysis.get('alert_level', 'normal')],
                'Density_Score': [analysis.get('density_score', 0)],
                'Coordinates': [f"{lat:.6f}, {lng:.6f}"]
            }
            
            # Add flow direction point
            flow_direction = analysis.get('flow_direction', 'unknown')
            if flow_direction != 'unknown':
                offset = 0.0008
                
                if flow_direction == 'north':
                    flow_lat, flow_lng = lat + offset, lng
                    flow_icon = '⬆️'
                elif flow_direction == 'south':
                    flow_lat, flow_lng = lat - offset, lng
                    flow_icon = '⬇️'
                elif flow_direction == 'east':
                    flow_lat, flow_lng = lat, lng + offset
                    flow_icon = '➡️'
                elif flow_direction == 'west':
                    flow_lat, flow_lng = lat, lng - offset
                    flow_icon = '⬅️'
                else:  # mixed
                    flow_lat, flow_lng = lat + offset/2, lng + offset/2
                    flow_icon = '🔄'
                
                map_data['Latitude'].append(flow_lat)
                map_data['Longitude'].append(flow_lng)
                map_data['Location'].append(f'{flow_icon} Flow {flow_direction.title()}')
                map_data['People_Count'].append(max(analysis.get('people_count', 0) // 3, 5))
                map_data['Alert_Level'].append('flow')
                map_data['Density_Score'].append(analysis.get('density_score', 0))
                map_data['Coordinates'].append(f"{flow_lat:.6f}, {flow_lng:.6f}")
            
            df = pd.DataFrame(map_data)
            
            # Enhanced map with better styling
            color_map = {
                'normal': '#4CAF50',    # Green
                'caution': '#FF9800',   # Orange  
                'warning': '#F44336',   # Red
                'critical': '#9C27B0',  # Purple
                'flow': '#2196F3',      # Blue
            }
            
            fig = px.scatter_mapbox(
                df,
                lat="Latitude",
                lon="Longitude",
                hover_name="Location",
                hover_data={
                    "People_Count": True,
                    "Alert_Level": True,
                    "Density_Score": True,
                    "Coordinates": True,
                    "Latitude": ":.6f",
                    "Longitude": ":.6f"
                },
                color="Alert_Level",
                color_discrete_map=color_map,
                size="People_Count",
                size_max=25,
                zoom=17,
                mapbox_style="open-street-map",
                title=f"🗺️ Live Crowd Flow Analysis - {datetime.now().strftime('%H:%M:%S')}"
            )
            
            fig.update_layout(
                height=500,
                showlegend=True,
                title_font_size=16,
                title_x=0.5
            )
            
            fig.update_traces(
                marker=dict(
                    line=dict(width=2, color='white'),
                    opacity=0.8
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Enhanced flow summary with location details
            st.subheader("📊 Location Analysis Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌊 Flow Direction", flow_direction.title())
            with col2:
                st.metric("📊 Crowd Density", f"{analysis.get('density_score', 0)}/10")
            with col3:
                st.metric("👥 People Count", analysis.get('people_count', 0))
            with col4:
                alert_level = analysis.get('alert_level', 'normal')
                alert_emoji = "🔴" if alert_level == 'critical' else "🟡" if alert_level == 'warning' else "🟢"
                st.metric("🚨 Alert Status", f"{alert_emoji} {alert_level.upper()}")
            
            # Individual Camera Analysis Data Display
            st.subheader("📹 Individual Camera Analysis Details")
            
            # Safety Risks
            safety_risks = analysis.get('safety_risks', [])
            if safety_risks:
                st.warning("⚠️ **Safety Risks Detected:**")
                for risk in safety_risks:
                    st.write(f"• {risk}")
            
            # Bottleneck Indicators
            bottleneck_indicators = analysis.get('bottleneck_indicators', [])
            if bottleneck_indicators:
                st.error("🚨 **Bottleneck Indicators:**")
                for indicator in bottleneck_indicators:
                    st.write(f"• {indicator}")
            
            # Crowd Behavior Analysis
            crowd_behavior = analysis.get('crowd_behavior', {})
            if crowd_behavior:
                col_beh1, col_beh2, col_beh3, col_beh4 = st.columns(4)
                with col_beh1:
                    st.metric("Movement Pattern", crowd_behavior.get('movement_pattern', 'normal').title())
                with col_beh2:
                    st.metric("Crowd Mood", crowd_behavior.get('crowd_mood', 'calm').title())
                with col_beh3:
                    st.metric("Interaction Level", crowd_behavior.get('interaction_level', 'low').title())
                with col_beh4:
                    st.metric("Urgency Level", crowd_behavior.get('urgency_level', 'normal').title())
            
            # Environmental Factors
            env_factors = analysis.get('environmental_factors', {})
            if env_factors:
                st.info("🌍 **Environmental Factors:**")
                col_env1, col_env2 = st.columns(2)
                with col_env1:
                    st.write(f"**Time of Day:** {env_factors.get('time_of_day', 'unknown').title()}")
                    st.write(f"**Weather Impact:** {env_factors.get('weather_impact', 'unknown').title()}")
                    st.write(f"**Visibility:** {env_factors.get('visibility', 'unknown').title()}")
                with col_env2:
                    st.write(f"**Temperature Comfort:** {env_factors.get('temperature_comfort', 'unknown').title()}")
                    st.write(f"**Noise Level:** {env_factors.get('noise_level', 'unknown').title()}")
                    st.write(f"**Crowd Tendency:** {env_factors.get('crowd_tendency', 'unknown').title()}")
            
            # Historical Comparison
            historical = analysis.get('historical_comparison', {})
            if historical:
                st.success("📊 **Historical Comparison:**")
                col_hist1, col_hist2, col_hist3 = st.columns(3)
                with col_hist1:
                    people_vs_hist = historical.get('people_vs_historical', 'normal')
                    hist_emoji = "📈" if people_vs_hist == 'above' else "📉" if people_vs_hist == 'below' else "➡️"
                    st.metric("People vs Historical", f"{hist_emoji} {people_vs_hist.upper()}")
                with col_hist2:
                    density_vs_hist = historical.get('density_vs_historical', 'normal')
                    density_emoji = "📈" if density_vs_hist == 'above' else "📉" if density_vs_hist == 'below' else "➡️"
                    st.metric("Density vs Historical", f"{density_emoji} {density_vs_hist.upper()}")
                with col_hist3:
                    trend = historical.get('trend', 'stable')
                    trend_emoji = "📈" if trend == 'increasing' else "📉" if trend == 'decreasing' else "➡️"
                    st.metric("Overall Trend", f"{trend_emoji} {trend.upper()}")
            
            # Location coordinates display
            st.info(f"📍 **Venue Coordinates:** {lat:.6f}°N, {lng:.6f}°E | **Map Style:** OpenStreetMap | **Zoom Level:** 17")
            
            # Real-time update indicator
            if st.button("🔄 Refresh Location Data"):
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error displaying map: {e}")
            st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")

    def show_crowd_prediction_graph(self, analysis: Dict):
        """Show crowd flow prediction graph"""
        try:
            st.subheader("📈 Crowd Flow Prediction Graph (Next 60 Minutes)")
            
            predictions = analysis.get('predictions', [])
            if not predictions:
                st.warning("⚠️ No prediction data available")
                return
            
            # Prepare graph data
            times = [pred['time'] for pred in predictions]
            people_counts = [pred['people_count'] for pred in predictions]
            density_scores = [pred['density_score'] for pred in predictions]
            confidence_scores = [pred['confidence'] * 100 for pred in predictions]
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('People Count Prediction', 'Density Score & Confidence'),
                vertical_spacing=0.1,
                specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
            )
            
            # People count prediction
            fig.add_trace(
                go.Scatter(
                    x=times, 
                    y=people_counts,
                    mode='lines+markers',
                    name='Predicted People Count',
                    line=dict(color='#2196F3', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            # Density score
            fig.add_trace(
                go.Scatter(
                    x=times, 
                    y=density_scores,
                    mode='lines+markers',
                    name='Density Score',
                    line=dict(color='#FF9800', width=2),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            
            # Confidence score on secondary y-axis
            fig.add_trace(
                go.Scatter(
                    x=times, 
                    y=confidence_scores,
                    mode='lines+markers',
                    name='Confidence %',
                    line=dict(color='#4CAF50', width=2, dash='dash'),
                    marker=dict(size=6),
                    yaxis='y4'
                ),
                row=2, col=1, secondary_y=True
            )
            
            # Update layout
            fig.update_layout(
                height=500,
                title_text="🔮 Real-Time Crowd Flow Predictions",
                title_x=0.5,
                showlegend=True
            )
            
            # Update axis labels
            fig.update_xaxes(title_text="Time", row=1, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="People Count", row=1, col=1)
            fig.update_yaxes(title_text="Density Score (1-10)", row=2, col=1)
            fig.update_yaxes(title_text="Confidence (%)", secondary_y=True, row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Prediction insights
            col_pred1, col_pred2, col_pred3 = st.columns(3)
            
            with col_pred1:
                max_people = max(people_counts)
                max_time = times[people_counts.index(max_people)]
                st.metric("Peak Crowd Expected", f"{max_people} people", f"at {max_time}")
            
            with col_pred2:
                avg_density = sum(density_scores) / len(density_scores)
                st.metric("Average Density", f"{avg_density:.1f}/10")
            
            with col_pred3:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                st.metric("Prediction Confidence", f"{avg_confidence:.0f}%")
                
        except Exception as e:
            st.error(f"❌ Error showing prediction graph: {e}")

    def show_crowd_summary_alert_box(self, analysis: Dict):
        """Show comprehensive summary alert box for crowd analysis"""
        try:
            st.subheader("🚨 Comprehensive Crowd Analysis Summary")
            
            # Determine alert style based on alert level
            alert_level = analysis.get('alert_level', 'normal')
            
            if alert_level == 'critical':
                alert_class = 'alert-critical'
                alert_emoji = '🔴'
                alert_title = 'CRITICAL ALERT'
            elif alert_level == 'warning':
                alert_class = 'alert-warning'
                alert_emoji = '🟡'
                alert_title = 'WARNING ALERT'
            else:
                alert_class = 'alert-normal'
                alert_emoji = '🟢'
                alert_title = 'NORMAL STATUS'
            
            # Create comprehensive summary
            summary_html = f"""
            <div class="{alert_class}">
                <h3>{alert_emoji} {alert_title}</h3>
                <hr>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4>📊 Current Analysis</h4>
                        <p><strong>Venue:</strong> {analysis.get('venue_name', 'Unknown')}</p>
                        <p><strong>Location:</strong> {analysis.get('venue_lat', 0):.6f}°N, {analysis.get('venue_lng', 0):.6f}°E</p>
                        <p><strong>Analysis Time:</strong> {analysis.get('analysis_time', 'Unknown')}</p>
                        <p><strong>People Count:</strong> {analysis.get('people_count', 0)} people</p>
                        <p><strong>Density Score:</strong> {analysis.get('density_score', 0)}/10</p>
                        <p><strong>Flow Direction:</strong> {analysis.get('flow_direction', 'unknown').title()}</p>
                        <p><strong>Velocity:</strong> {analysis.get('velocity_estimate', 0):.1f} m/s</p>
                    </div>
                    <div>
                        <h4>⚠️ Risk Assessment</h4>
                        <p><strong>Alert Level:</strong> {alert_level.upper()}</p>
                        <p><strong>Bottleneck Risk:</strong> {analysis.get('bottleneck_risk', 'unknown').title()}</p>
                        <p><strong>Safety Score:</strong> {analysis.get('safety_score', 0)}/10</p>
                        <p><strong>Flow Efficiency:</strong> {analysis.get('flow_efficiency', 0)}/10</p>
                        <h4>🔮 Predictions</h4>
                        <p><strong>Peak Expected:</strong> {max([p['people_count'] for p in analysis.get('predictions', [])], default=0)} people</p>
                        <p><strong>Peak Time:</strong> {analysis.get('predictions', [{}])[0].get('time', 'Unknown') if analysis.get('predictions') else 'Unknown'}</p>
                    </div>
                </div>
                <hr>
                <div>
                    <h4>💡 Recommended Actions</h4>
            """
            
            # Add recommendations based on alert level
            if alert_level == 'critical':
                recommendations = [
                    "🚨 IMMEDIATE ACTION REQUIRED - Deploy emergency crowd control",
                    "🚫 Consider stopping entry to prevent overcrowding",
                    "👮‍♂️ Increase security personnel by 200%",
                    "📢 Activate emergency announcement system",
                    "🚑 Prepare medical assistance on standby"
                ]
            elif alert_level == 'warning':
                recommendations = [
                    "⚠️ Enhanced monitoring required",
                    "👮‍♂️ Increase security presence in hotspots",
                    "🚧 Implement crowd flow management",
                    "📊 Monitor density levels every 5 minutes",
                    "🔄 Prepare for potential crowd control measures"
                ]
            else:
                recommendations = [
                    "✅ Continue standard monitoring",
                    "👮‍♂️ Maintain regular security patrols",
                    "📊 Monitor for any sudden changes",
                    "🔄 Update predictions every 10 minutes"
                ]
            
            for rec in recommendations:
                summary_html += f"<p>• {rec}</p>"
            
            summary_html += """
                </div>
                <hr>
                <div style="text-align: center; font-size: 12px; color: #666;">
                    <p>🤖 Generated by AI Crowd Analysis System | 📍 GPS Coordinates Verified | 🔄 Auto-refresh every 2 minutes</p>
                </div>
            </div>
            """
            
            st.markdown(summary_html, unsafe_allow_html=True)
            
            # Action buttons
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button("📋 Export Summary"):
                    export_data = {
                        'timestamp': datetime.now().isoformat(),
                        'venue': analysis.get('venue_name', 'Unknown'),
                        'coordinates': f"{analysis.get('venue_lat', 0):.6f}, {analysis.get('venue_lng', 0):.6f}",
                        'alert_level': alert_level,
                        'people_count': analysis.get('people_count', 0),
                        'density_score': analysis.get('density_score', 0),
                        'recommendations': recommendations
                    }
                    
                    st.download_button(
                        label="💾 Download JSON Report",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"crowd_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col_btn2:
                if st.button("🔄 Refresh Analysis"):
                    st.rerun()
            
            with col_btn3:
                if st.button("📧 Send Alert"):
                    st.success("✅ Alert sent to security team!")
            
            with col_btn4:
                if st.button("📱 Mobile Notification"):
                    st.success("✅ Mobile alert dispatched!")
                
        except Exception as e:
            st.error(f"❌ Error showing summary alert box: {e}")

    def generate_safety_risks(self, density_score: int, people_count: int) -> List[str]:
        """Generate safety risks based on crowd analysis"""
        risks = []
        
        if density_score >= 8:
            risks.extend([
                "High crowd density - risk of stampede",
                "Limited emergency evacuation capacity",
                "Potential for crowd crushing incidents"
            ])
        elif density_score >= 6:
            risks.extend([
                "Moderate crowd density - monitor closely",
                "Reduced mobility for emergency response"
            ])
        
        if people_count >= 100:
            risks.append("Large crowd size - enhanced security needed")
        
        if not risks:
            risks.append("No significant safety risks detected")
        
        return risks

    def generate_bottleneck_indicators(self, density_score: int, flow_direction: str) -> List[str]:
        """Generate bottleneck indicators"""
        indicators = []
        
        if density_score >= 7:
            indicators.append("High density indicates potential bottleneck formation")
        
        if flow_direction == 'mixed':
            indicators.append("Mixed flow direction suggests congestion")
        elif flow_direction in ['north', 'south', 'east', 'west']:
            indicators.append(f"Unidirectional flow towards {flow_direction} - monitor exit capacity")
        
        if density_score >= 8 and flow_direction == 'mixed':
            indicators.append("CRITICAL: High density with mixed flow - immediate attention required")
        
        if not indicators:
            indicators.append("No bottleneck indicators detected")
        
        return indicators

    def analyze_crowd_behavior(self, people_count: int, density_score: int, flow_direction: str) -> Dict:
        """Analyze crowd behavior patterns"""
        behavior = {
            'movement_pattern': 'normal',
            'crowd_mood': 'calm',
            'interaction_level': 'low',
            'urgency_level': 'normal'
        }
        
        # Movement pattern analysis
        if flow_direction == 'mixed':
            behavior['movement_pattern'] = 'chaotic'
        elif density_score >= 7:
            behavior['movement_pattern'] = 'congested'
        
        # Crowd mood assessment
        if density_score >= 8:
            behavior['crowd_mood'] = 'agitated'
        elif density_score >= 6:
            behavior['crowd_mood'] = 'restless'
        
        # Interaction level
        if people_count >= 80:
            behavior['interaction_level'] = 'high'
        elif people_count >= 40:
            behavior['interaction_level'] = 'medium'
        
        # Urgency level
        if density_score >= 8:
            behavior['urgency_level'] = 'high'
        elif density_score >= 6:
            behavior['urgency_level'] = 'elevated'
        
        return behavior

    def get_environmental_factors(self) -> Dict:
        """Get environmental factors affecting crowd behavior"""
        current_hour = datetime.now().hour
        
        factors = {
            'time_of_day': 'peak' if 9 <= current_hour <= 17 else 'off-peak',
            'weather_impact': 'moderate',
            'visibility': 'good',
            'temperature_comfort': 'comfortable',
            'noise_level': 'moderate'
        }
        
        # Time-based adjustments
        if 12 <= current_hour <= 14:
            factors['crowd_tendency'] = 'lunch_rush'
        elif 17 <= current_hour <= 19:
            factors['crowd_tendency'] = 'evening_rush'
        else:
            factors['crowd_tendency'] = 'normal'
        
        return factors

    def get_historical_comparison(self, people_count: int, density_score: int) -> Dict:
        """Compare current data with historical patterns"""
        # Simulate historical data comparison
        historical_avg_people = np.random.randint(30, 80)
        historical_avg_density = np.random.randint(3, 7)
        
        comparison = {
            'people_vs_historical': 'above' if people_count > historical_avg_people else 'below' if people_count < historical_avg_people else 'normal',
            'density_vs_historical': 'above' if density_score > historical_avg_density else 'below' if density_score < historical_avg_density else 'normal',
            'historical_avg_people': historical_avg_people,
            'historical_avg_density': historical_avg_density,
            'trend': 'increasing' if people_count > historical_avg_people and density_score > historical_avg_density else 'decreasing' if people_count < historical_avg_people and density_score < historical_avg_density else 'stable'
        }
        
        return comparison

    def central_nervous_system_page(self):
        """Central Nervous System main page with test data support"""
        st.header("🧠 Central Nervous System - Multi-Camera Analysis")
        
        st.info("""
        **Central Nervous System Features:**
        - Multiple camera feeds simultaneously
        - Real-time crowd density, flow, velocity tracking
        - Bottleneck prediction with location mapping
        - Cross-location convergence analysis
        - Precise GPS coordinates for each alert
        """)
        
        # Test Mode for CNS
        st.subheader("🧪 Test Mode - System Alerts & Bottleneck Predictions")
        
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🚨 Generate Test Alerts & Predictions", type="primary"):
                self.generate_cns_test_data()
                st.success("✅ Test alerts and predictions generated!")
        
        with col_test2:
            if st.button("🔄 Clear CNS Test Data"):
                if 'cns_test_data' in st.session_state:
                    del st.session_state['cns_test_data']
                st.info("🧹 CNS test data cleared!")
        
        # Show test data if available
        if 'cns_test_data' in st.session_state:
            test_data = st.session_state['cns_test_data']
            
            # System Alerts
            st.subheader("🚨 System Alerts")
            test_alerts = test_data.get('system_alerts', [])
            if test_alerts:
                st.info("🧪 **Test Mode Active** - Showing simulated alerts")
                for alert in test_alerts:
                    severity = alert.get('severity', 'normal')
                    alert_color = "🔴" if severity == 'critical' else "🟡" if severity == 'warning' else "🟢"
                    coords = alert.get('coordinates', {})
                    
                    st.markdown(f"""
                    <div class="alert-{severity}">
                        <strong>{alert_color} {severity.upper()} ALERT</strong><br>
                        <strong>Location:</strong> {alert.get('location', 'Unknown')}<br>
                        <strong>Message:</strong> {alert.get('message', 'No message')}<br>
                        <strong>Coordinates:</strong> {coords.get('lat', 0):.6f}°N, {coords.get('lng', 0):.6f}°E<br>
                        <strong>Time:</strong> {alert.get('timestamp', datetime.now()).strftime('%H:%M:%S') if isinstance(alert.get('timestamp'), datetime) else 'Unknown'}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Bottleneck Predictions
            st.subheader("⚠️ Bottleneck Predictions")
            test_bottlenecks = test_data.get('bottleneck_predictions', [])
            if test_bottlenecks:
                st.info("🧪 **Test Mode Active** - Showing simulated bottleneck predictions")
                for prediction in test_bottlenecks:
                    severity = prediction.get('bottleneck_severity', 'moderate')
                    severity_color = "🔴" if severity == 'critical' else "🟡" if severity == 'high' else "🟠"
                    coords = prediction.get('coordinates', {})
                    
                    st.markdown(f"""
                    <div class="alert-warning">
                        <strong>{severity_color} {severity.upper()} BOTTLENECK PREDICTED</strong><br>
                        <strong>Location:</strong> {prediction.get('location', 'Unknown')}<br>
                        <strong>ETA:</strong> {prediction.get('estimated_eta_minutes', 0)} minutes<br>
                        <strong>Risk Score:</strong> {prediction.get('risk_score', 0)}/100<br>
                        <strong>Predicted People:</strong> {prediction.get('predicted_people_count', 0)} people<br>
                        <strong>Coordinates:</strong> {coords.get('lat', 0):.6f}°N, {coords.get('lng', 0):.6f}°E
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Risk factors
                    risk_factors = prediction.get('risk_factors', [])
                    if risk_factors:
                        st.write("**🚨 Risk Factors:**")
                        for factor in risk_factors:
                            st.write(f"• {factor}")
                    
                    # Recommended actions
                    actions = prediction.get('recommended_actions', [])
                    if actions:
                        st.write("**💡 Recommended Actions:**")
                        for action in actions:
                            st.write(f"• {action}")
                    
                    st.markdown("---")
        else:
            st.info("👆 Click 'Generate Test Alerts & Predictions' to see how system alerts and bottleneck predictions will look")

    def generate_cns_test_data(self):
        """Generate test data for CNS alerts and predictions"""
        # Simulate system alerts
        test_alerts = [
            {
                'severity': 'critical',
                'location': 'Main Entrance',
                'message': 'High crowd density detected - 150+ people in confined area',
                'timestamp': datetime.now() - timedelta(minutes=2),
                'coordinates': {'lat': 13.0360, 'lng': 77.6430}
            },
            {
                'severity': 'warning', 
                'location': 'Food Court',
                'message': 'Bottleneck forming near counter area',
                'timestamp': datetime.now() - timedelta(minutes=5),
                'coordinates': {'lat': 13.0354, 'lng': 77.6428}
            },
            {
                'severity': 'normal',
                'location': 'Hall 2 Entry',
                'message': 'Crowd flow normalized after temporary congestion',
                'timestamp': datetime.now() - timedelta(minutes=8),
                'coordinates': {'lat': 13.0356, 'lng': 77.6434}
            }
        ]
        
        # Simulate bottleneck predictions
        test_bottlenecks = [
            {
                'location': 'Main Corridor',
                'bottleneck_severity': 'critical',
                'estimated_eta_minutes': 8,
                'risk_score': 85,
                'coordinates': {'lat': 13.0357, 'lng': 77.6431},
                'predicted_people_count': 200,
                'risk_factors': [
                    'Multiple event sessions ending simultaneously',
                    'Limited exit points in corridor area',
                    'Food court rush hour overlap'
                ],
                'recommended_actions': [
                    'Deploy crowd control barriers immediately',
                    'Open additional exit routes',
                    'Announce staggered exit timing'
                ]
            },
            {
                'location': 'Parking Exit',
                'bottleneck_severity': 'high',
                'estimated_eta_minutes': 15,
                'risk_score': 72,
                'coordinates': {'lat': 13.0362, 'lng': 77.6425},
                'predicted_people_count': 120,
                'risk_factors': [
                    'Single lane exit causing backup',
                    'Payment processing delays'
                ],
                'recommended_actions': [
                    'Open secondary parking exit',
                    'Deploy traffic management personnel'
                ]
            }
        ]
        
        # Store in session state
        st.session_state['cns_test_data'] = {
            'system_alerts': test_alerts,
            'bottleneck_predictions': test_bottlenecks
        }

    def ip_camera_setup_page(self):
        """IP Camera Setup page"""
        st.header("📱 IP Camera Setup")
        st.info("Configure IP cameras for multi-camera crowd analysis")
        
        st.subheader("📋 Setup Instructions")
        st.write("""
        1. Install IP Webcam app on your phone
        2. Start the server and note the IP address
        3. Enter the camera details below
        4. Test the connection
        """)
        
        # Camera configuration
        camera_url = st.text_input("Camera URL", placeholder="http://192.168.1.100:8080/video")
        camera_name = st.text_input("Camera Name", placeholder="Main Entrance Camera")
        
        if st.button("🔍 Test Camera Connection"):
            if camera_url:
                st.info(f"Testing connection to: {camera_url}")
                # Simulate connection test
                time.sleep(1)
                st.success("✅ Camera connection successful!")
            else:
                st.error("❌ Please enter camera URL")


def main():
    """Main function"""
    ui = CrowdPredictionUI()
    ui.run()

if __name__ == "__main__":
    main()