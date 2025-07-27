"""
Complete Crowd Analysis System - Main Application
Public Safety ke liye comprehensive crowd monitoring system
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
import os
import base64
from PIL import Image
import requests

# Import our analysis modules
from map_crowd_analyzer import analyze_complete_crowd_situation
from crowd_predictor import get_crowd_density

class CrowdAnalysisUI:
    def __init__(self):
        self.setup_page()
        self.analysis_history = []
        
    def setup_page(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title="🎯 Crowd Analysis System",
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
        .metric-card {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #FF6B6B;
        }
        .alert-critical {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            border-radius: 5px;
        }
        .alert-warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 1rem;
            border-radius: 5px;
        }
        .alert-normal {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
            padding: 1rem;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

    def run(self):
        """Main application runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Advanced Crowd Analysis System</h1>
            <p>Real-time Public Safety Monitoring with AI-powered Anomaly Detection</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content based on selection
        page = st.session_state.get('page', 'Dashboard')
        
        if page == 'Dashboard':
            self.dashboard_page()
        elif page == 'Live Analysis':
            self.live_analysis_page()
        elif page == 'Map Analysis':
            self.map_analysis_page()
        elif page == 'Anomaly Detection':
            self.anomaly_detection_page()
        elif page == 'Historical Data':
            self.historical_data_page()

    def create_sidebar(self):
        """Create sidebar navigation"""
        st.sidebar.title("🎛️ Navigation")
        
        pages = [
            "Dashboard",
            "Live Analysis", 
            "Map Analysis",
            "Anomaly Detection",
            "Historical Data"
        ]
        
        selected_page = st.sidebar.selectbox("Select Page", pages)
        st.session_state['page'] = selected_page
        
        st.sidebar.markdown("---")
        
        # Quick Settings
        st.sidebar.subheader("⚙️ Quick Settings")
        st.session_state['alert_threshold'] = st.sidebar.slider(
            "Alert Threshold", 1, 10, 7
        )
        st.session_state['analysis_interval'] = st.sidebar.selectbox(
            "Analysis Interval", [5, 10, 15, 30, 60]
        )
        
        # Emergency Controls
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚨 Emergency Controls")
        
        if st.sidebar.button("🚨 EMERGENCY ALERT", type="primary"):
            st.sidebar.error("🚨 EMERGENCY ALERT ACTIVATED!")
            st.balloons()
        
        if st.sidebar.button("📢 Send Alert to Security"):
            st.sidebar.success("✅ Alert sent to security team!")

    def dashboard_page(self):
        """Main dashboard with overview"""
        st.header("📊 Real-time Dashboard")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🎯 Current Crowd Level",
                value="MEDIUM",
                delta="↑ 15% from last hour"
            )
        
        with col2:
            st.metric(
                label="👥 People Count",
                value="127",
                delta="↑ 23 from 5 min ago"
            )
        
        with col3:
            st.metric(
                label="⚡ Flow Velocity",
                value="2.3 m/s",
                delta="↓ 0.5 m/s"
            )
        
        with col4:
            st.metric(
                label="🚨 Alert Status",
                value="NORMAL",
                delta="No anomalies"
            )
        
        # Real-time charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Crowd Density Over Time")
            # Generate sample data
            times = pd.date_range(start=datetime.now() - timedelta(hours=2), 
                                end=datetime.now(), freq='5min')
            density_data = np.random.randint(20, 80, len(times))
            
            fig = px.line(x=times, y=density_data, 
                         title="Crowd Density Trend",
                         labels={'x': 'Time', 'y': 'Density Score'})
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Critical Threshold")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🌊 Flow Direction Analysis")
            # Flow direction pie chart
            flow_data = {
                'Direction': ['North', 'South', 'East', 'West', 'Stationary'],
                'Count': [25, 30, 20, 15, 10]
            }
            fig = px.pie(values=flow_data['Count'], names=flow_data['Direction'],
                        title="Crowd Flow Directions")
            st.plotly_chart(fig, use_container_width=True)
        
        # Live feed simulation
        st.subheader("📹 Live Camera Feeds")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image("https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Camera+1", 
                    caption="Main Entrance")
        with col2:
            st.image("https://via.placeholder.com/300x200/4ECDC4/FFFFFF?text=Camera+2", 
                    caption="Central Area")
        with col3:
            st.image("https://via.placeholder.com/300x200/45B7D1/FFFFFF?text=Camera+3", 
                    caption="Exit Points")

    def live_analysis_page(self):
        """Live analysis with video processing"""
        st.header("🎥 Live Crowd Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Video Analysis")
            
            # Video source selection
            video_source_type = st.selectbox(
                "Select Video Source",
                ["Webcam", "Upload Video File", "IP Camera"]
            )
            
            video_source = 0  # Default
            uploaded_video = None
            
            # Handle video upload
            if video_source_type == "Upload Video File":
                uploaded_video = st.file_uploader(
                    "Upload Video File", 
                    type=['mp4', 'avi', 'mov', 'mkv'],
                    help="Upload a video file for crowd analysis"
                )
                
                if uploaded_video is not None:
                    # Save uploaded video temporarily
                    temp_video_path = f"temp_video_{int(time.time())}.mp4"
                    with open(temp_video_path, "wb") as f:
                        f.write(uploaded_video.read())
                    video_source = temp_video_path
                    
                    # Display video info
                    st.info(f"📹 Video uploaded: {uploaded_video.name}")
                    st.video(uploaded_video)
            
            elif video_source_type == "IP Camera":
                ip_url = st.text_input("IP Camera URL", placeholder="http://192.168.1.100:8080/video")
                if ip_url:
                    video_source = ip_url
            
            analysis_duration = st.slider("Analysis Duration (seconds)", 10, 120, 30)
            
            # Analysis button
            can_analyze = (video_source_type == "Webcam" or 
                          (video_source_type == "Upload Video File" and uploaded_video is not None) or
                          (video_source_type == "IP Camera" and ip_url))
            
            if st.button("🚀 Start Analysis", type="primary", disabled=not can_analyze):
                with st.spinner("🔄 Analyzing video..."):
                    try:
                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # For uploaded video, analyze the entire video
                        if video_source_type == "Upload Video File":
                            status_text.text("Analyzing uploaded video...")
                            progress_bar.progress(0.5)
                        else:
                            # Live analysis with progress
                            for i in range(analysis_duration):
                                progress_bar.progress((i + 1) / analysis_duration)
                                status_text.text(f"Analyzing... {i+1}/{analysis_duration} seconds")
                                time.sleep(1)
                        
                        # Get analysis results
                        result = get_crowd_density(video_source=video_source)
                        
                        # Clean up temp file
                        if video_source_type == "Upload Video File" and os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        
                        progress_bar.progress(1.0)
                        status_text.text("Analysis complete!")
                        
                        # Display results
                        st.success("✅ Analysis Complete!")
                        
                        # Metrics
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("People Count", result.get('people_count', 0))
                        with col_b:
                            st.metric("Density Score", f"{result.get('density_score', 0)}/100")
                        with col_c:
                            st.metric("Alert Level", result.get('alert_status', 'normal').upper())
                        
                        # Store in session state for other pages
                        st.session_state['latest_analysis'] = result
                        
                        # Enhanced results display
                        if 'video_analysis' in result:
                            video_data = result['video_analysis']
                            st.subheader("📊 Detailed Video Analysis")
                            
                            col_d, col_e = st.columns(2)
                            with col_d:
                                st.write("**Analysis Details:**")
                                st.write(f"• Source: {video_source_type}")
                                st.write(f"• Duration: {analysis_duration}s")
                                st.write(f"• Timestamp: {result.get('timestamp', 'N/A')}")
                            
                            with col_e:
                                st.write("**Crowd Metrics:**")
                                st.write(f"• Density Category: {result.get('crowd_level', 'Unknown')}")
                                st.write(f"• Alert Status: {result.get('alert_status', 'normal').title()}")
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {e}")
                        # Clean up temp file on error
                        if video_source_type == "Upload Video File" and 'temp_video_path' in locals() and os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
        
        with col2:
            st.subheader("⚡ Real-time Metrics")
            
            # Real-time metrics placeholder
            if 'latest_analysis' in st.session_state:
                result = st.session_state['latest_analysis']
                
                # Alert status
                alert_status = result.get('alert_status', 'normal')
                if alert_status == 'emergency':
                    st.markdown('<div class="alert-critical">🚨 CRITICAL ALERT</div>', 
                              unsafe_allow_html=True)
                elif alert_status == 'warning':
                    st.markdown('<div class="alert-warning">⚠️ WARNING</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-normal">✅ NORMAL</div>', 
                              unsafe_allow_html=True)
                
                # Detailed metrics
                st.json(result)
            else:
                st.info("👆 Start analysis to see real-time metrics")

    def map_analysis_page(self):
        """Map-based crowd analysis with density overlay"""
        st.header("🗺️ Map-based Crowd Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📍 Upload Map/Venue Layout")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload map image", 
                type=['png', 'jpg', 'jpeg'],
                help="Upload a map or venue layout image for analysis"
            )
            
            # Location coordinates
            st.subheader("📍 Location Coordinates (Optional)")
            col_lat, col_lng = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=28.6139, format="%.6f")
            with col_lng:
                longitude = st.number_input("Longitude", value=77.2090, format="%.6f")
            
            # Analysis options
            st.subheader("🎛️ Analysis Options")
            include_video = st.checkbox("Include Video Analysis", value=False, 
                                      help="Combine map analysis with video analysis for better accuracy")
            
            if include_video:
                video_duration = st.slider("Video Analysis Duration (seconds)", 10, 60, 20)
            
            show_density_overlay = st.checkbox("Show Density Overlay", value=True,
                                             help="Display color-coded density zones on the map")
            
            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Map", use_column_width=True)
                
                if st.button("🔍 Analyze Map", type="primary"):
                    with st.spinner("🔄 Analyzing map layout..."):
                        try:
                            # Save uploaded file temporarily
                            temp_path = f"temp_map_{int(time.time())}.png"
                            image.save(temp_path)
                            
                            # Run map analysis
                            video_source = 0 if include_video else None
                            duration = video_duration if include_video else 0
                            
                            result = analyze_complete_crowd_situation(
                                map_image_path=temp_path,
                                video_source=video_source,
                                lat=latitude,
                                lng=longitude,
                                duration=duration
                            )
                            
                            # Create density overlay if requested
                            overlay_path = None
                            if show_density_overlay:
                                from src.map_density_overlay import create_map_overlay
                                video_analysis = result.get('video_analysis') if include_video else None
                                overlay_path = create_map_overlay(temp_path, result, video_analysis)
                            
                            # Clean up temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            
                            # Store results
                            st.session_state['map_analysis_result'] = result
                            st.session_state['map_overlay_path'] = overlay_path
                            st.success("✅ Map analysis complete!")
                            
                        except Exception as e:
                            st.error(f"❌ Error analyzing map: {e}")
            else:
                # Use default screenshot if available
                default_map = "src/Screenshot 2025-07-23 064906.png"
                if os.path.exists(default_map):
                    st.info("💡 Using default map for demo")
                    if st.button("🔍 Analyze Default Map"):
                        with st.spinner("🔄 Analyzing default map..."):
                            try:
                                video_source = 0 if include_video else None
                                duration = video_duration if include_video else 0
                                
                                result = analyze_complete_crowd_situation(
                                    map_image_path=default_map,
                                    video_source=video_source,
                                    lat=latitude,
                                    lng=longitude,
                                    duration=duration
                                )
                                
                                # Create density overlay if requested
                                overlay_path = None
                                if show_density_overlay:
                                    from src.map_density_overlay import create_map_overlay
                                    video_analysis = result.get('video_analysis') if include_video else None
                                    overlay_path = create_map_overlay(default_map, result, video_analysis)
                                
                                st.session_state['map_analysis_result'] = result
                                st.session_state['map_overlay_path'] = overlay_path
                                st.success("✅ Analysis complete!")
                                
                            except Exception as e:
                                st.error(f"❌ Error analyzing map: {e}")
        
        with col2:
            st.subheader("📊 Map Analysis Results")
            
            if 'map_analysis_result' in st.session_state:
                result = st.session_state['map_analysis_result']
                
                # Alert level
                alert_level = result.get('alert_level', 'normal')
                if alert_level == 'emergency':
                    st.error("🚨 EMERGENCY LEVEL")
                elif alert_level == 'warning':
                    st.warning("⚠️ WARNING LEVEL")
                elif alert_level == 'caution':
                    st.warning("⚠️ CAUTION LEVEL")
                else:
                    st.success("✅ NORMAL LEVEL")
                
                # Map analysis details
                if 'map_analysis' in result:
                    map_data = result['map_analysis']
                    
                    # Key metrics
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if 'density_rating' in map_data:
                            st.metric("Density Rating", f"{map_data['density_rating']}/10")
                    with col_b:
                        if 'safety_score' in map_data:
                            st.metric("Safety Score", f"{map_data['safety_score']}/10")
                    
                    # Video analysis metrics (if included)
                    if 'video_analysis' in result:
                        video_data = result['video_analysis']
                        st.subheader("🎥 Video Analysis")
                        col_c, col_d = st.columns(2)
                        with col_c:
                            st.metric("People Count", video_data.get('people_count', 0))
                        with col_d:
                            st.metric("Video Density", f"{video_data.get('density_score', 0)}/100")
                    
                    # High-risk areas
                    if 'high_risk_areas' in map_data and map_data['high_risk_areas']:
                        st.subheader("⚠️ High Risk Areas")
                        for area in map_data['high_risk_areas'][:5]:
                            st.write(f"• {area}")
                    
                    # Bottlenecks
                    if 'bottlenecks' in map_data and map_data['bottlenecks']:
                        st.subheader("🚧 Bottlenecks")
                        for bottleneck in map_data['bottlenecks'][:5]:
                            st.write(f"• {bottleneck}")
                
                # Recommendations
                if 'recommendations' in result:
                    st.subheader("💡 Recommendations")
                    for rec in result['recommendations'][:5]:
                        st.write(f"• {rec}")
            else:
                st.info("👆 Upload and analyze a map to see results")
        
        # Display density overlay if available
        if 'map_overlay_path' in st.session_state and st.session_state['map_overlay_path']:
            overlay_path = st.session_state['map_overlay_path']
            if os.path.exists(overlay_path):
                st.subheader("🎨 Crowd Density Overlay")
                st.image(overlay_path, caption="Map with Crowd Density Zones", use_column_width=True)
                
                # Density legend explanation
                st.markdown("""
                **Density Zone Legend:**
                - 🔴 **Red (Critical)**: Extremely high crowd density - immediate attention required
                - 🟠 **Orange (High)**: High crowd density - enhanced monitoring needed  
                - 🟡 **Yellow (Medium)**: Moderate crowd density - standard monitoring
                - 🟢 **Green (Low)**: Low crowd density - normal conditions
                """)
                
                # Download button for overlay
                with open(overlay_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Density Overlay",
                        data=file.read(),
                        file_name=f"crowd_density_overlay_{int(time.time())}.png",
                        mime="image/png"
                    )

    def anomaly_detection_page(self):
        """Anomaly detection and alerts"""
        st.header("🔍 Anomaly Detection System")
        
        # Anomaly detection settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚙️ Detection Settings")
            
            # Thresholds
            crowd_threshold = st.slider("Crowd Density Threshold", 1, 10, 7)
            velocity_threshold = st.slider("Flow Velocity Threshold (m/s)", 0.5, 5.0, 2.0)
            duration_threshold = st.slider("Anomaly Duration (seconds)", 5, 60, 15)
            
            # Anomaly types to detect
            st.subheader("🎯 Anomaly Types")
            detect_overcrowding = st.checkbox("Overcrowding", value=True)
            detect_stampede = st.checkbox("Stampede Risk", value=True)
            detect_bottleneck = st.checkbox("Bottleneck Formation", value=True)
            detect_unusual_flow = st.checkbox("Unusual Flow Patterns", value=True)
            detect_loitering = st.checkbox("Loitering/Stationary Crowds", value=True)
        
        with col2:
            st.subheader("🚨 Current Anomalies")
            
            # Simulate anomaly detection
            anomalies = self.generate_sample_anomalies()
            
            for anomaly in anomalies:
                severity = anomaly['severity']
                if severity == 'critical':
                    st.error(f"🚨 CRITICAL: {anomaly['description']}")
                elif severity == 'warning':
                    st.warning(f"⚠️ WARNING: {anomaly['description']}")
                else:
                    st.info(f"ℹ️ INFO: {anomaly['description']}")
                
                # Anomaly details
                with st.expander(f"Details - {anomaly['type']}"):
                    st.write(f"**Location:** {anomaly['location']}")
                    st.write(f"**Time:** {anomaly['timestamp']}")
                    st.write(f"**Confidence:** {anomaly['confidence']}%")
                    st.write(f"**Recommended Action:** {anomaly['action']}")
        
        # Anomaly timeline
        st.subheader("📈 Anomaly Timeline")
        
        # Generate timeline data
        timeline_data = self.generate_anomaly_timeline()
        
        fig = px.scatter(timeline_data, 
                        x='timestamp', 
                        y='severity_score',
                        color='type',
                        size='confidence',
                        hover_data=['location', 'description'],
                        title="Anomaly Detection Timeline")
        
        fig.add_hline(y=7, line_dash="dash", line_color="red", 
                     annotation_text="Critical Threshold")
        fig.add_hline(y=5, line_dash="dash", line_color="orange", 
                     annotation_text="Warning Threshold")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Anomaly statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Anomalies (24h)", "23", delta="↑ 5")
        with col2:
            st.metric("Critical Alerts", "3", delta="↑ 1")
        with col3:
            st.metric("False Positives", "2", delta="↓ 1")

    def historical_data_page(self):
        """Historical data analysis"""
        st.header("📚 Historical Data Analysis")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Generate historical data
        historical_data = self.generate_historical_data(start_date, end_date)
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_crowd = historical_data['crowd_density'].mean()
            st.metric("Avg Crowd Density", f"{avg_crowd:.1f}")
        
        with col2:
            max_crowd = historical_data['crowd_density'].max()
            st.metric("Peak Crowd Level", f"{max_crowd:.1f}")
        
        with col3:
            total_anomalies = len(historical_data[historical_data['anomaly'] == True])
            st.metric("Total Anomalies", total_anomalies)
        
        with col4:
            avg_flow = historical_data['flow_velocity'].mean()
            st.metric("Avg Flow Velocity", f"{avg_flow:.1f} m/s")
        
        # Historical charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Crowd Density Trends")
            fig = px.line(historical_data, 
                         x='timestamp', 
                         y='crowd_density',
                         title="Crowd Density Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🌊 Flow Velocity Trends")
            fig = px.line(historical_data, 
                         x='timestamp', 
                         y='flow_velocity',
                         title="Flow Velocity Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap of crowd patterns
        st.subheader("🔥 Crowd Pattern Heatmap")
        
        # Create hourly heatmap data
        historical_data['hour'] = historical_data['timestamp'].dt.hour
        historical_data['day'] = historical_data['timestamp'].dt.day_name()
        
        heatmap_data = historical_data.pivot_table(
            values='crowd_density', 
            index='day', 
            columns='hour', 
            aggfunc='mean'
        )
        
        fig = px.imshow(heatmap_data, 
                       title="Crowd Density by Day and Hour",
                       labels=dict(x="Hour of Day", y="Day of Week", color="Density"))
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📊 Raw Data")
        st.dataframe(historical_data, use_container_width=True)

    def generate_sample_anomalies(self):
        """Generate sample anomaly data"""
        return [
            {
                'type': 'Overcrowding',
                'severity': 'critical',
                'description': 'Crowd density exceeds safe limits in main entrance',
                'location': 'Main Entrance - Zone A',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'confidence': 95,
                'action': 'Deploy additional security, restrict entry'
            },
            {
                'type': 'Unusual Flow',
                'severity': 'warning',
                'description': 'Irregular crowd movement pattern detected',
                'location': 'Central Plaza - Zone C',
                'timestamp': (datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S'),
                'confidence': 78,
                'action': 'Monitor closely, prepare crowd control'
            },
            {
                'type': 'Bottleneck',
                'severity': 'info',
                'description': 'Minor bottleneck forming at exit point',
                'location': 'Exit Gate 2',
                'timestamp': (datetime.now() - timedelta(minutes=10)).strftime('%H:%M:%S'),
                'confidence': 65,
                'action': 'Guide crowd flow, open additional exits'
            }
        ]

    def generate_anomaly_timeline(self):
        """Generate anomaly timeline data"""
        times = pd.date_range(start=datetime.now() - timedelta(hours=6), 
                            end=datetime.now(), freq='30min')
        
        data = []
        anomaly_types = ['Overcrowding', 'Bottleneck', 'Unusual Flow', 'Stampede Risk']
        locations = ['Zone A', 'Zone B', 'Zone C', 'Main Entrance', 'Exit Gate']
        
        for i, time in enumerate(times):
            if np.random.random() > 0.7:  # 30% chance of anomaly
                data.append({
                    'timestamp': time,
                    'type': np.random.choice(anomaly_types),
                    'location': np.random.choice(locations),
                    'severity_score': np.random.randint(3, 10),
                    'confidence': np.random.randint(60, 100),
                    'description': f"Anomaly detected at {time.strftime('%H:%M')}"
                })
        
        return pd.DataFrame(data)

    def generate_historical_data(self, start_date, end_date):
        """Generate historical data"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        data = []
        for timestamp in date_range:
            # Simulate realistic crowd patterns
            hour = timestamp.hour
            if 8 <= hour <= 10 or 17 <= hour <= 19:  # Rush hours
                base_density = np.random.normal(7, 1.5)
            elif 12 <= hour <= 14:  # Lunch time
                base_density = np.random.normal(6, 1)
            else:
                base_density = np.random.normal(4, 1)
            
            data.append({
                'timestamp': timestamp,
                'crowd_density': max(1, min(10, base_density)),
                'flow_velocity': np.random.normal(2, 0.5),
                'people_count': int(np.random.normal(100, 30)),
                'anomaly': np.random.random() > 0.9  # 10% chance of anomaly
            })
        
        return pd.DataFrame(data)

def main():
    """Main application entry point"""
    app = CrowdAnalysisUI()
    app.run()

if __name__ == "__main__":
    main()