"""
Complete Streamlit UI for Live Crowd Prediction - Working Version
Bhai, yeh original working version hai with Main Entrance functionality
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
import base64
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
        
        st.sidebar.markdown("---")
        
        # System Status
        st.sidebar.subheader("🔴 System Status")
        
        if 'monitoring_active' not in st.session_state:
            st.session_state['monitoring_active'] = False
        
        # Webcam status display
        if st.session_state.get('webcam_active', False):
            st.sidebar.success("🔴 **LIVE:** Webcam Analysis Active")
            st.sidebar.info("📹 Go to Live Monitoring → Webcam")
        else:
            st.sidebar.info("📹 Webcam Analysis: Inactive")
            st.sidebar.info("👆 Go to Live Monitoring to start webcam")
        
        # Central Nervous System status
        if st.sidebar.button("🧠 Start Central Nervous System"):
            try:
                start_central_monitoring({'cam_entrance_main': 0})
                st.session_state['cns_active'] = True
                st.sidebar.success("✅ Central Nervous System started!")
            except Exception as e:
                st.sidebar.error(f"❌ CNS Error: {str(e)}")
        
        if st.session_state.get('cns_active', False):
            st.sidebar.success("🧠 **CNS:** Active")
            if st.sidebar.button("⏹️ Stop CNS"):
                stop_central_monitoring()
                st.session_state['cns_active'] = False
                st.sidebar.info("⏹️ CNS stopped!")

    def live_monitoring_page(self):
        """Live monitoring main page"""
        st.header("🎥 Live Video Feed & Crowd Prediction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Video Analysis")
            
            # Video source selection
            video_source_type = st.selectbox(
                "Video Source",
                ["Webcam", "Upload Video File", "IP Camera"]
            )
            
            # Webcam analysis
            if video_source_type == "Webcam":
                st.subheader("📹 Live Webcam Analysis")
                
                # Webcam controls
                col_webcam1, col_webcam2, col_webcam3 = st.columns(3)
                
                with col_webcam1:
                    if st.button("🚀 Start Webcam Analysis", type="primary"):
                        st.session_state['webcam_active'] = True
                        st.success("✅ Webcam analysis started!")
                
                with col_webcam2:
                    if st.button("⏹️ Stop Webcam"):
                        st.session_state['webcam_active'] = False
                        st.info("⏹️ Webcam analysis stopped!")
                
                with col_webcam3:
                    if st.button("📸 Capture & Analyze"):
                        with st.spinner("📸 Capturing and analyzing webcam frame..."):
                            analysis_result = self.capture_and_analyze_webcam()
                            if analysis_result:
                                st.session_state['latest_webcam_analysis'] = analysis_result
                                st.success("✅ Frame captured and analyzed!")
                
                # Show webcam status
                if st.session_state.get('webcam_active', False):
                    st.info("🔴 **LIVE:** Webcam analysis is running")
                    
                    # Auto-refresh analysis every few seconds
                    if st.button("🔄 Refresh Analysis"):
                        with st.spinner("🔄 Analyzing current webcam frame..."):
                            analysis_result = self.capture_and_analyze_webcam()
                            if analysis_result:
                                st.session_state['latest_webcam_analysis'] = analysis_result
                else:
                    st.info("📹 Click 'Start Webcam Analysis' to begin live monitoring")
                
                # Display latest analysis
                if 'latest_webcam_analysis' in st.session_state:
                    analysis = st.session_state['latest_webcam_analysis']
                    
                    st.subheader("📊 Current Webcam Analysis")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("People Count", analysis.get('people_count', 0))
                    with col_b:
                        st.metric("Density Score", f"{analysis.get('density_score', 0)}/10")
                    with col_c:
                        st.metric("Alert Level", analysis.get('alert_level', 'normal').upper())
                    
                    # Additional metrics
                    col_d, col_e, col_f = st.columns(3)
                    
                    with col_d:
                        st.metric("Velocity", f"{analysis.get('velocity_estimate', 0):.1f} m/s")
                    with col_e:
                        st.metric("Flow Efficiency", f"{analysis.get('flow_efficiency', 5)}/10")
                    with col_f:
                        st.metric("Safety Score", f"{analysis.get('safety_score', 5)}/10")
                    
                    # Show analysis time
                    st.info(f"🕐 **Last Analysis:** {analysis.get('analysis_time', 'Unknown')}")
                    
                    # Show predictions
                    if analysis.get('predictions'):
                        st.subheader("🔮 15-20 Minute Predictions")
                        predictions = analysis['predictions']
                        
                        col_pred1, col_pred2 = st.columns(2)
                        with col_pred1:
                            st.metric("Predicted People", predictions.get('predicted_people_15min', 0))
                            st.metric("Growth Rate", f"{predictions.get('growth_percentage', 0):+.1f}%")
                        with col_pred2:
                            st.metric("Bottleneck Risk", f"{predictions.get('bottleneck_probability', 0)}%")
                            if predictions.get('bottleneck_eta_minutes'):
                                st.metric("Bottleneck ETA", f"{predictions['bottleneck_eta_minutes']} min")
                    
                    # Show crowd flow visualization
                    if analysis.get('flow_direction'):
                        flow_emoji = {
                            'north': '⬆️', 'south': '⬇️', 'east': '➡️', 
                            'west': '⬅️', 'mixed': '🔄', 'stationary': '⏸️'
                        }
                        flow_dir = analysis['flow_direction']
                        st.info(f"🌊 **Crowd Flow:** {flow_emoji.get(flow_dir, '❓')} {flow_dir.title()}")
                else:
                    st.info("📸 Click 'Capture & Analyze' to get webcam analysis")
            
            # Video file upload
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
                if uploaded_video and st.button("🚀 Start Video Analysis", type="primary"):
                    with st.spinner("🔄 Analyzing uploaded video..."):
                        # Simulate analysis
                        time.sleep(2)
                        
                        # Generate analysis using Gemini AI
                        analysis_result = self.analyze_uploaded_video_with_gemini(uploaded_video, venue_lat, venue_lng, venue_name)
                        
                        st.session_state['uploaded_video_analysis'] = analysis_result
                        st.success("✅ Video analysis complete!")
            
            # IP Camera
            elif video_source_type == "IP Camera":
                st.subheader("📱 IP Camera Analysis")
                
                # Check if IP cameras are configured
                if 'ip_camera_config' in st.session_state and st.session_state['ip_camera_config']:
                    ip_cameras = st.session_state['ip_camera_config']
                    
                    st.info(f"📹 **{len(ip_cameras)} IP Camera(s) Configured**")
                    
                    # Select camera to analyze
                    camera_options = {f"{config['name']} - {config['location']}": cam_id 
                                    for cam_id, config in ip_cameras.items()}
                    
                    selected_display = st.selectbox("Select IP Camera to Analyze", list(camera_options.keys()))
                    selected_camera_id = camera_options[selected_display]
                    selected_config = ip_cameras[selected_camera_id]
                    
                    st.info(f"📍 **Selected:** {selected_config['name']} at {selected_config['location']}")
                    st.info(f"🌐 **URL:** {selected_config['url']}")
                    
                    # IP Camera controls
                    col_ip1, col_ip2, col_ip3 = st.columns(3)
                    
                    with col_ip1:
                        if st.button("🚀 Start IP Camera Analysis", type="primary"):
                            st.session_state['ip_camera_active'] = selected_camera_id
                            st.success(f"✅ Started analyzing {selected_config['name']}!")
                    
                    with col_ip2:
                        if st.button("⏹️ Stop IP Camera"):
                            if 'ip_camera_active' in st.session_state:
                                del st.session_state['ip_camera_active']
                            st.info("⏹️ IP camera analysis stopped!")
                    
                    with col_ip3:
                        if st.button("📸 Capture & Analyze IP Camera"):
                            with st.spinner(f"📸 Capturing from {selected_config['name']}..."):
                                analysis_result = self.capture_and_analyze_ip_camera(selected_config)
                                if analysis_result:
                                    st.session_state[f'ip_analysis_{selected_camera_id}'] = analysis_result
                                    st.success("✅ IP camera frame captured and analyzed!")
                    
                    # Display latest IP camera analysis
                    analysis_key = f'ip_analysis_{selected_camera_id}'
                    if analysis_key in st.session_state:
                        analysis = st.session_state[analysis_key]
                        
                        st.subheader(f"📊 {selected_config['name']} - Live Analysis")
                        
                        # Show connection status
                        if analysis.get('connection_successful'):
                            st.success(f"✅ **Connected:** {selected_config['url']}")
                        else:
                            st.error(f"❌ **Connection Failed:** {analysis.get('error_message', 'Unknown error')}")
                            return
                        
                        # Main metrics
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("People Count", analysis.get('people_count', 0))
                        with col_b:
                            st.metric("Density Score", f"{analysis.get('density_score', 0)}/10")
                        with col_c:
                            st.metric("Alert Level", analysis.get('alert_level', 'normal').upper())
                        
                        # Show Gemini AI predictions
                        if analysis.get('predictions'):
                            st.subheader("🔮 Gemini AI Predictions (15-20 Minutes)")
                            predictions = analysis['predictions']
                            
                            col_pred1, col_pred2 = st.columns(2)
                            with col_pred1:
                                st.metric("Predicted People", predictions.get('predicted_people_15min', 0))
                                st.metric("Growth Rate", f"{predictions.get('growth_percentage', 0):+.1f}%")
                            with col_pred2:
                                st.metric("Bottleneck Risk", f"{predictions.get('bottleneck_probability', 0)}%")
                                if predictions.get('bottleneck_eta_minutes'):
                                    st.metric("Bottleneck ETA", f"{predictions['bottleneck_eta_minutes']} min")
                    else:
                        st.info("📸 Click 'Capture & Analyze IP Camera' to get analysis")
                
                else:
                    st.warning("⚠️ **No IP Cameras Configured**")
                    st.info("👆 Go to **IP Camera Setup** page to configure your cameras first")
        
        with col2:
            st.subheader("🔮 Predictions & Alerts")
            
            if st.session_state.get('monitoring_active', False):
                status = get_live_crowd_status()
                prediction = status.get('latest_prediction')
                
                if prediction:
                    st.info(f"🕐 Next Prediction: {datetime.now().strftime('%H:%M')}")
                    
                    col_e, col_f = st.columns(2)
                    with col_e:
                        st.metric("Predicted People", prediction.get('predicted_people_count', 0))
                    with col_f:
                        st.metric("Predicted Density", f"{prediction.get('predicted_density', 0)}/10")
                    
                    # Trends
                    people_trend = prediction.get('people_trend', 'stable')
                    st.write(f"📈 Trend: {people_trend.title()}")
                    
                    # Risk
                    bottleneck_risk = prediction.get('bottleneck_risk', 'low')
                    risk_color = "🔴" if bottleneck_risk == 'high' else "🟡" if bottleneck_risk == 'medium' else "🟢"
                    st.write(f"{risk_color} Risk: {bottleneck_risk.title()}")
                else:
                    st.info("🔮 Generating predictions...")
            else:
                st.info("👆 Start monitoring to see predictions")

    def central_nervous_system_page(self):
        """Central Nervous System main page"""
        st.header("🧠 Central Nervous System - Multi-Camera Analysis")
        
        # Always show AI Analysis Features prominently
        st.markdown("---")
        st.subheader("🤖 AI Analysis Features - Always Active")
        
        col_ai1, col_ai2, col_ai3, col_ai4 = st.columns(4)
        
        with col_ai1:
            st.info("**🧠 Dynamic Risk Assessment**\n• No manual rules\n• AI-driven decisions\n• Real-time adaptation")
        
        with col_ai2:
            st.info("**📍 Location-Specific Predictions**\n• GPS coordinates with alerts\n• Venue-aware analysis\n• Precise positioning")
        
        with col_ai3:
            st.info("**📊 Confidence Scoring**\n• AI analysis reliability\n• Prediction accuracy\n• Trust indicators")
        
        with col_ai4:
            st.info("**💡 Contextual Recommendations**\n• Location-based actions\n• Situation-aware advice\n• Smart suggestions")
        
        # Always show Video Analysis & Prediction Timeline
        st.markdown("---")
        st.subheader("⏱️ AI Analysis Timeline - Continuous Processing")
        
        col_time1, col_time2 = st.columns(2)
        
        with col_time1:
            st.success("**🎥 1-Minute Video Analysis**\n• Gemini AI processes video segments\n• Real-time crowd detection\n• Continuous monitoring\n• Live density calculation")
        
        with col_time2:
            st.warning("**🔮 15-20 Minute Predictions**\n• AI forecasts bottleneck chances\n• Future crowd state analysis\n• Proactive alert generation\n• Risk probability assessment")
        
        st.info("""
        **Central Nervous System Features:**
        - Multiple camera feeds simultaneously
        - Real-time crowd density, flow, velocity tracking
        - Bottleneck prediction with location mapping
        - Cross-location convergence analysis
        - Precise GPS coordinates for each alert
        """)
        
        # Test Mode Button for Demo
        st.markdown("---")
        st.subheader("🧪 Test Mode - Demo System")
        
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🚨 Activate Test Mode", type="primary"):
                self.add_test_data()
                st.success("✅ Test data activated!")
        
        with col_test2:
            if st.button("🔄 Clear Test Data"):
                if 'test_mode_active' in st.session_state:
                    del st.session_state['test_mode_active']
                    del st.session_state['test_camera_details']
                st.info("🧹 Test data cleared!")
        
        # Show test status
        if st.session_state.get('test_mode_active', False):
            st.info("🧪 **Test Mode Active** - Showing simulated camera data")
            
            # Get test data
            camera_details = st.session_state.get('test_camera_details', {})
            
            if camera_details:
                st.subheader("📹 Individual Camera Analysis & Predictions")
                
                for camera_id, data in camera_details.items():
                    if data:
                        location_name = data.get('camera_location', {}).get('location', camera_id)
                        
                        st.markdown(f"### 📹 {location_name}")
                        
                        # Current metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("👥 People Count", data.get('people_count', 0))
                        with col2:
                            st.metric("📊 Density Score", f"{data.get('density_score', 0)}/10")
                        with col3:
                            alert_level = data.get('alert_level', 'normal')
                            alert_color = "🔴" if alert_level == 'critical' else "🟡" if alert_level == 'warning' else "🟢"
                            st.metric("🚨 Alert Level", f"{alert_color} {alert_level.upper()}")
                        with col4:
                            st.metric("🌊 Flow Direction", data.get('flow_direction', 'unknown').title())
                        
                        # Predictions
                        st.markdown("#### 🔮 15-20 Minute Predictions")
                        
                        col_pred1, col_pred2, col_pred3 = st.columns(3)
                        
                        with col_pred1:
                            predicted_people = data.get('predicted_people_15min', 0)
                            current_people = data.get('people_count', 0)
                            st.metric("Predicted People", predicted_people, delta=f"{predicted_people - current_people:+d}")
                        
                        with col_pred2:
                            st.metric("Growth Rate", f"{data.get('growth_percentage', 0):+.1f}%")
                        
                        with col_pred3:
                            st.metric("Bottleneck Risk", f"{data.get('bottleneck_probability', 0)}%")
                        
                        # Location info
                        location = data.get('camera_location', {})
                        if location:
                            st.info(f"📍 **Location:** {location.get('location', 'Unknown')} | **Coordinates:** {location.get('lat', 0):.6f}°N, {location.get('lng', 0):.6f}°E")
                        
                        st.markdown("---")

    def ip_camera_setup_page(self):
        """IP Camera Setup page"""
        st.header("📱 IP Camera Setup - Phone Integration")
        
        st.info("""
        **Setup Instructions:**
        1. Install "IP Webcam" app on your Android phone
        2. Start the server in the app
        3. Note the IP address shown (e.g., 192.168.1.100:8080)
        4. Enter the details below
        """)
        
        # Camera configuration
        st.subheader("📹 Camera Configuration")
        
        num_cameras = st.slider("Number of IP Cameras", 1, 6, 2)
        
        camera_configs = {}
        for i in range(num_cameras):
            st.subheader(f"📱 Camera {i+1} Setup")
            
            col1, col2 = st.columns(2)
            
            with col1:
                camera_name = st.text_input(f"Camera {i+1} Name", f"IP_Camera_{i+1}", key=f"cam_name_{i}")
                ip_address = st.text_input(f"IP Address", "192.168.1.100", key=f"ip_{i}", help="Enter valid IP like 192.168.1.100")
                port = st.text_input(f"Port", "8080", key=f"port_{i}", help="Usually 8080 for IP Webcam app")
            
            with col2:
                location_name = st.text_input(f"Location Name", f"Location_{i+1}", key=f"loc_name_{i}")
                latitude = st.number_input(f"Latitude", value=13.0358, format="%.6f", key=f"lat_{i}")
                longitude = st.number_input(f"Longitude", value=77.6431, format="%.6f", key=f"lng_{i}")
            
            # Camera URL display and copy option
            camera_url = f"http://{ip_address}:{port}/video"
            st.text_input(f"Camera {i+1} URL", camera_url, key=f"url_display_{i}", disabled=True)
            
            # Copy URL and connection test buttons
            col_test1, col_test2, col_test3 = st.columns(3)
            
            with col_test1:
                if st.button(f"📋 Copy URL", key=f"copy_{i}"):
                    st.success(f"✅ Camera {i+1} URL ready to copy!")
                    st.text_area(
                        f"Camera {i+1} URL (Select All & Copy):",
                        camera_url,
                        height=60,
                        key=f"copy_area_{i}",
                        help="Select all text and copy (Ctrl+A, then Ctrl+C)"
                    )
            
            with col_test2:
                if st.button(f"🌐 Open in Browser", key=f"browser_{i}"):
                    st.markdown(f'<a href="{camera_url}" target="_blank">🔗 Click here to open camera feed</a>', unsafe_allow_html=True)
                    st.info(f"**Direct Link:** {camera_url}")
            
            with col_test3:
                if st.button(f"🔍 Test Connection", key=f"test_{i}"):
                    with st.spinner(f"Testing connection to {camera_url}..."):
                        try:
                            import requests
                            response = requests.get(f"http://{ip_address}:{port}/", timeout=5)
                            if response.status_code == 200:
                                st.success(f"✅ Camera {i+1} connected successfully!")
                                st.info(f"🌐 **Working URL:** {camera_url}")
                            else:
                                st.error(f"❌ Camera {i+1} connection failed (Status: {response.status_code})")
                        except Exception as e:
                            st.error(f"❌ Connection error: {e}")
                            st.warning("💡 **Troubleshooting Tips:**")
                            st.write("• Make sure IP Webcam app is running on your phone")
                            st.write("• Check if phone and computer are on same WiFi network")
                            st.write("• Verify IP address and port number")
                            st.write("• Try accessing the URL in your browser first")
            
            camera_configs[f"cam_ip_{i+1}"] = {
                'name': camera_name,
                'url': f"http://{ip_address}:{port}/video",
                'location': location_name,
                'lat': latitude,
                'lng': longitude
            }
        
        # Save configuration
        if st.button("💾 Save Camera Configuration", type="primary"):
            st.session_state['ip_camera_config'] = camera_configs
            st.success("✅ Camera configuration saved!")
            
            # Show saved config
            st.subheader("📋 Saved Configuration")
            for cam_id, config in camera_configs.items():
                st.write(f"**{config['name']}**: {config['location']} ({config['lat']:.6f}, {config['lng']:.6f})")

    def add_test_data(self):
        """Add test data for demonstration"""
        current_time = datetime.now()
        
        test_camera_details = {
            'cam_entrance_main': {
                'people_count': 45,
                'density_score': 6,
                'alert_level': 'warning',
                'flow_direction': 'north',
                'velocity_estimate': 1.2,
                'flow_efficiency': 7,
                'camera_location': {
                    'location': 'Main Entrance',
                    'lat': 13.0360,
                    'lng': 77.6430,
                    'bottleneck_risk': 'high'
                },
                'predicted_people_15min': 65,
                'growth_percentage': 44.4,
                'bottleneck_probability': 75,
                'analysis_time': current_time.strftime('%H:%M:%S')
            },
            'cam_hall1_entry': {
                'people_count': 32,
                'density_score': 4,
                'alert_level': 'normal',
                'flow_direction': 'east',
                'velocity_estimate': 1.8,
                'flow_efficiency': 8,
                'camera_location': {
                    'location': 'Hall 1 Entry',
                    'lat': 13.0358,
                    'lng': 77.6432,
                    'bottleneck_risk': 'medium'
                },
                'predicted_people_15min': 38,
                'growth_percentage': 18.8,
                'bottleneck_probability': 35,
                'analysis_time': current_time.strftime('%H:%M:%S')
            },
            'cam_food_court': {
                'people_count': 78,
                'density_score': 8,
                'alert_level': 'critical',
                'flow_direction': 'mixed',
                'velocity_estimate': 0.8,
                'flow_efficiency': 4,
                'camera_location': {
                    'location': 'Food Court',
                    'lat': 13.0354,
                    'lng': 77.6428,
                    'bottleneck_risk': 'very_high'
                },
                'predicted_people_15min': 95,
                'growth_percentage': 21.8,
                'bottleneck_probability': 90,
                'analysis_time': current_time.strftime('%H:%M:%S')
            }
        }
        
        st.session_state['test_mode_active'] = True
        st.session_state['test_camera_details'] = test_camera_details

    def capture_and_analyze_webcam(self) -> Dict:
        """Capture frame from webcam and analyze it using Gemini AI"""
        try:
            # Initialize webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Could not access webcam. Please check if camera is connected and not being used by another application.")
                return None
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                st.error("❌ Could not capture frame from webcam")
                return None
            
            # Convert frame to base64 for Gemini API
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Analyze with Gemini AI
            analysis_result = self.analyze_frame_with_gemini(frame_base64)
            
            # Add timestamp and additional data
            analysis_result['analysis_time'] = datetime.now().strftime('%H:%M:%S')
            analysis_result['frame_captured'] = True
            
            return analysis_result
            
        except Exception as e:
            st.error(f"❌ Webcam capture error: {str(e)}")
            return None

    def capture_and_analyze_ip_camera(self, camera_config: Dict) -> Dict:
        """Capture frame from IP camera and analyze it using Gemini AI"""
        try:
            camera_url = camera_config['url']
            camera_name = camera_config['name']
            location = camera_config['location']
            
            st.info(f"🌐 Connecting to {camera_name} at {camera_url}...")
            
            # Initialize IP camera connection
            cap = cv2.VideoCapture(camera_url)
            
            if not cap.isOpened():
                error_msg = f"Could not connect to IP camera at {camera_url}"
                st.error(f"❌ {error_msg}")
                return {
                    'connection_successful': False,
                    'error_message': error_msg,
                    'analysis_time': datetime.now().strftime('%H:%M:%S')
                }
            
            st.success(f"✅ Connected to {camera_name}!")
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                error_msg = f"Could not capture frame from {camera_name}"
                st.error(f"❌ {error_msg}")
                return {
                    'connection_successful': False,
                    'error_message': error_msg,
                    'analysis_time': datetime.now().strftime('%H:%M:%S')
                }
            
            st.info(f"📸 Frame captured from {camera_name}, analyzing with Gemini AI...")
            
            # Convert frame to base64 for Gemini API
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Analyze with Gemini AI (enhanced prompt for IP camera)
            analysis_result = self.analyze_ip_camera_frame_with_gemini(frame_base64, camera_config)
            
            # Add connection and timestamp data
            analysis_result['connection_successful'] = True
            analysis_result['analysis_time'] = datetime.now().strftime('%H:%M:%S')
            analysis_result['camera_name'] = camera_name
            analysis_result['camera_location'] = location
            analysis_result['camera_url'] = camera_url
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"IP camera capture error: {str(e)}"
            st.error(f"❌ {error_msg}")
            return {
                'connection_successful': False,
                'error_message': error_msg,
                'analysis_time': datetime.now().strftime('%H:%M:%S')
            }

    def analyze_frame_with_gemini(self, frame_base64: str) -> Dict:
        """Analyze webcam frame using Gemini AI"""
        try:
            # Create prompt for Gemini AI
            prompt = """
            Analyze this webcam image for crowd analysis. Provide detailed numerical analysis including:
            
            1. People count (estimate number of people visible)
            2. Density score (1-10 scale, where 10 is extremely crowded)
            3. Flow direction (north/south/east/west/mixed/stationary)
            4. Alert level (normal/caution/warning/critical)
            5. Velocity estimate (0-5 m/s average movement speed)
            6. Flow efficiency (1-10 scale)
            7. Safety score (1-10 scale, 10 being safest)
            8. Bottleneck probability (0-100%)
            9. Growth prediction for next 15-20 minutes
            10. Safety risks and recommendations
            
            Respond in JSON format:
            {
                "people_count": <number>,
                "density_score": <1-10>,
                "flow_direction": "<direction>",
                "alert_level": "<level>",
                "velocity_estimate": <0-5>,
                "flow_efficiency": <1-10>,
                "safety_score": <1-10>,
                "predictions": {
                    "predicted_people_15min": <number>,
                    "growth_percentage": <percentage>,
                    "bottleneck_probability": <0-100>,
                    "bottleneck_eta_minutes": <number or null>
                },
                "safety_risks": ["<risk1>", "<risk2>"],
                "recommendations": ["<rec1>", "<rec2>"]
            }
            
            Base your analysis on visible crowd density, movement patterns, and spacing between people.
            """
            
            # Send to Gemini API
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": frame_base64
                            }
                        }
                    ]
                }]
            }
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
            
            response = requests.post(gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON response
                try:
                    analysis_data = json.loads(ai_response)
                    return analysis_data
                except json.JSONDecodeError:
                    # If JSON parsing fails, create fallback analysis
                    return self.create_fallback_analysis()
            else:
                st.error(f"❌ Gemini API error: {response.status_code}")
                return self.create_fallback_analysis()
                
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            return self.create_fallback_analysis()

    def analyze_ip_camera_frame_with_gemini(self, frame_base64: str, camera_config: Dict) -> Dict:
        """Analyze IP camera frame using Gemini AI with enhanced prompts"""
        try:
            camera_name = camera_config['name']
            location = camera_config['location']
            
            # Enhanced prompt specifically for IP camera analysis
            prompt = f"""
            You are analyzing a live IP camera feed from {camera_name} located at {location}.
            This is a real-time crowd management system requiring accurate predictions.
            
            Analyze this IP camera frame and provide comprehensive crowd intelligence:
            
            REQUIRED ANALYSIS:
            1. PEOPLE_COUNT: Count exact number of people visible in the frame
            2. DENSITY_SCORE: Rate crowd density 1-10 (1=empty, 5=moderate, 10=dangerously packed)
            3. FLOW_DIRECTION: Primary crowd movement (north/south/east/west/mixed/stationary)
            4. ALERT_LEVEL: Safety assessment (normal/caution/warning/critical)
            5. VELOCITY_ESTIMATE: Average movement speed in m/s (0-5 scale)
            6. FLOW_EFFICIENCY: How smoothly crowd moves (1-10, 10=perfect flow)
            7. SAFETY_SCORE: Overall safety rating (1-10, 10=completely safe)
            
            PREDICTIONS (15-20 MINUTES):
            8. PREDICTED_PEOPLE_15MIN: Forecast people count based on current trends
            9. GROWTH_PERCENTAGE: Expected crowd growth/decline percentage
            10. BOTTLENECK_PROBABILITY: Risk of bottleneck formation (0-100%)
            11. BOTTLENECK_ETA_MINUTES: Time until bottleneck if probability > 50%
            
            SAFETY ASSESSMENT:
            12. SAFETY_RISKS: List immediate safety concerns
            13. RECOMMENDATIONS: Actionable crowd management suggestions
            
            CONTEXT: This is {camera_name} at {location}. Consider:
            - Current crowd patterns and density
            - Movement flow and direction
            - Potential congestion points
            - Safety risks and bottleneck indicators
            - Typical crowd behavior at this location type
            
            Respond ONLY in this JSON format:
            {{
                "people_count": <number>,
                "density_score": <1-10>,
                "flow_direction": "<direction>",
                "alert_level": "<level>",
                "velocity_estimate": <0-5>,
                "flow_efficiency": <1-10>,
                "safety_score": <1-10>,
                "predictions": {{
                    "predicted_people_15min": <number>,
                    "growth_percentage": <percentage>,
                    "bottleneck_probability": <0-100>,
                    "bottleneck_eta_minutes": <number or null>
                }},
                "safety_risks": ["<risk1>", "<risk2>"],
                "recommendations": ["<rec1>", "<rec2>"],
                "analysis_confidence": <0.0-1.0>,
                "camera_specific_notes": "<observations about this specific location>"
            }}
            
            Be precise and realistic in your analysis. Base predictions on visible crowd patterns.
            """
            
            # Send to Gemini API
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": frame_base64
                            }
                        }
                    ]
                }]
            }
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
            
            response = requests.post(gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON response
                try:
                    # Clean the response to extract JSON
                    if '```json' in ai_response:
                        json_text = ai_response.split('```json')[1].split('```')[0].strip()
                    elif '{' in ai_response:
                        json_text = ai_response[ai_response.find('{'):ai_response.rfind('}')+1]
                    else:
                        json_text = ai_response
                    
                    analysis_data = json.loads(json_text)
                    
                    # Add source information
                    analysis_data['analysis_source'] = 'gemini_ai'
                    analysis_data['camera_name'] = camera_name
                    analysis_data['camera_location'] = location
                    
                    return analysis_data
                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ JSON parsing error: {e}")
                    # If JSON parsing fails, create fallback analysis
                    return self.create_fallback_ip_camera_analysis(camera_config)
            else:
                st.error(f"❌ Gemini API error: {response.status_code}")
                return self.create_fallback_ip_camera_analysis(camera_config)
                
        except Exception as e:
            st.error(f"❌ IP Camera analysis error: {str(e)}")
            return self.create_fallback_ip_camera_analysis(camera_config)

    def analyze_uploaded_video_with_gemini(self, uploaded_video, venue_lat: float, venue_lng: float, venue_name: str) -> Dict:
        """Analyze uploaded video using Gemini AI"""
        try:
            # For uploaded video, we'll simulate Gemini analysis
            # In real implementation, you would extract frames and send to Gemini
            prompt = f"""
            Analyze this uploaded video for crowd management at {venue_name or 'Unknown Venue'}.
            Location coordinates: {venue_lat:.6f}, {venue_lng:.6f}
            
            Based on typical venue characteristics and location, provide realistic crowd analysis:
            
            VENUE ANALYSIS:
            1. PEOPLE_COUNT: Realistic crowd size for this venue type
            2. DENSITY_SCORE: Crowd density 1-10
            3. FLOW_DIRECTION: Primary crowd movement
            4. VELOCITY_ESTIMATE: Average movement speed 0-5 m/s
            5. FLOW_EFFICIENCY: Movement efficiency 1-10
            6. BOTTLENECK_RISK: Risk level (low/medium/high)
            7. SAFETY_SCORE: Overall safety 1-10
            
            VENUE CONTEXT:
            - Venue: {venue_name or 'Unknown Venue'}
            - Location: {venue_lat:.6f}, {venue_lng:.6f}
            - Analysis Time: {datetime.now().strftime('%H:%M')}
            
            Respond ONLY in JSON format:
            {{
                "people_count": <number>,
                "density_score": <1-10>,
                "flow_direction": "<direction>",
                "velocity_estimate": <0-5>,
                "flow_efficiency": <1-10>,
                "bottleneck_risk": "<risk>",
                "safety_score": <1-10>,
                "analysis_confidence": <0.0-1.0>,
                "venue_notes": "<venue-specific observations>"
            }}
            """
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
            
            response = requests.post(gemini_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                try:
                    if '```json' in ai_response:
                        json_text = ai_response.split('```json')[1].split('```')[0].strip()
                    elif '{' in ai_response:
                        json_text = ai_response[ai_response.find('{'):ai_response.rfind('}')+1]
                    else:
                        json_text = ai_response
                    
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    return self.create_fallback_analysis()
            else:
                return self.create_fallback_analysis()
                
        except Exception as e:
            st.error(f"Video analysis error: {e}")
            return self.create_fallback_analysis()

    def create_fallback_analysis(self) -> Dict:
        """Create fallback analysis when AI analysis fails"""
        return {
            "people_count": 10,
            "density_score": 3,
            "flow_direction": "mixed",
            "alert_level": "normal",
            "velocity_estimate": 1.0,
            "flow_efficiency": 6,
            "safety_score": 7,
            "predictions": {
                "predicted_people_15min": 12,
                "growth_percentage": 20.0,
                "bottleneck_probability": 15,
                "bottleneck_eta_minutes": None
            },
            "safety_risks": ["Analysis system unavailable"],
            "recommendations": ["Manual monitoring recommended"]
        }

    def create_fallback_ip_camera_analysis(self, camera_config: Dict) -> Dict:
        """Create fallback analysis for IP camera when AI analysis fails"""
        return {
            "people_count": 5,
            "density_score": 2,
            "flow_direction": "unknown",
            "alert_level": "normal",
            "velocity_estimate": 1.0,
            "flow_efficiency": 6,
            "safety_score": 7,
            "predictions": {
                "predicted_people_15min": 6,
                "growth_percentage": 20.0,
                "bottleneck_probability": 10,
                "bottleneck_eta_minutes": None
            },
            "safety_risks": ["Analysis system unavailable"],
            "recommendations": ["Check camera connection", "Retry analysis"],
            "analysis_confidence": 0.2,
            "camera_specific_notes": f"Fallback analysis for {camera_config['name']}",
            "analysis_source": "fallback"
        }

# Main app
if __name__ == "__main__":
    app = CrowdPredictionUI()
    app.run()