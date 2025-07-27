"""
Complete Streamlit UI for Live Crowd Prediction
Bhai, yeh complete UI hai with live video feed aur testing features
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
import base64
import re
from typing import Dict, List, Tuple, Optional

# Import our live predictor
from live_crowd_predictor import live_predictor, get_live_crowd_status, start_live_monitoring, stop_live_monitoring

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
        .zone-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            margin: 0.5rem 0;
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
        elif page == 'Bangalore Exhibition Center Test':
            self.bangalore_test_page()
        elif page == 'Analytics Dashboard':
            self.analytics_dashboard()
        elif page == 'Zone Management':
            self.zone_management_page()

    def create_sidebar(self):
        """Create sidebar navigation"""
        st.sidebar.title("🎛️ Navigation")
        
        pages = [
            "Live Monitoring",
            "Bangalore Exhibition Center Test", 
            "Analytics Dashboard",
            "Zone Management"
        ]
        
        selected_page = st.sidebar.selectbox("Select Feature", pages)
        st.session_state['page'] = selected_page
        
        st.sidebar.markdown("---")
        
        # System Status
        st.sidebar.subheader("🔴 System Status")
        
        if 'monitoring_active' not in st.session_state:
            st.session_state['monitoring_active'] = False
        
        if st.sidebar.button("🚀 Start Live Monitoring" if not st.session_state['monitoring_active'] else "⏹️ Stop Monitoring"):
            if not st.session_state['monitoring_active']:
                start_live_monitoring(0)  # Webcam
                st.session_state['monitoring_active'] = True
                st.sidebar.success("✅ Live monitoring started!")
            else:
                stop_live_monitoring()
                st.session_state['monitoring_active'] = False
                st.sidebar.info("⏹️ Live monitoring stopped!")
        
        # Quick status
        if st.session_state['monitoring_active']:
            status = get_live_crowd_status()
            overall = status.get('overall_status', {})
            
            alert_level = overall.get('overall_alert_level', 'normal')
            if alert_level == 'critical':
                st.sidebar.error(f"🚨 CRITICAL ALERT")
            elif alert_level == 'warning':
                st.sidebar.warning(f"⚠️ WARNING")
            elif alert_level == 'caution':
                st.sidebar.warning(f"⚠️ CAUTION")
            else:
                st.sidebar.success(f"✅ NORMAL")
            
            st.sidebar.metric("Total People", overall.get('total_estimated_people', 0))
            st.sidebar.metric("Critical Zones", overall.get('critical_zones', 0))
        
        st.sidebar.markdown("---")
        
        # Settings
        st.sidebar.subheader("⚙️ Settings")
        st.session_state['prediction_interval'] = st.sidebar.slider("Prediction Interval (min)", 15, 30, 18)
        st.session_state['alert_threshold'] = st.sidebar.slider("Alert Threshold", 1, 10, 7)
        st.session_state['auto_refresh'] = st.sidebar.checkbox("Auto Refresh", value=True)

    def live_monitoring_page(self):
        """Live monitoring main page"""
        st.header("🎥 Live Video Feed & Crowd Prediction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Video Analysis")
            
            # Video source selection
            video_source_type = st.selectbox(
                "Video Source",
                ["Webcam", "Upload Video File", "IP Camera", "Drone Feed"]
            )
            
            # Video upload and location input
            uploaded_video = None
            venue_location = None
            venue_info = {}
            
            if video_source_type == "Upload Video File":
                st.subheader("📤 Upload Video & Location")
                
                # Video upload
                uploaded_video = st.file_uploader(
                    "Choose video file", 
                    type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                    help="Upload video file for crowd analysis"
                )
                
                if uploaded_video:
                    st.success(f"✅ Video uploaded: {uploaded_video.name}")
                    
                    # Display video
                    st.video(uploaded_video)
                
                # Location input
                st.subheader("📍 Venue Location")
                
                col_loc1, col_loc2 = st.columns(2)
                with col_loc1:
                    venue_lat = st.number_input("Latitude", value=13.0358, format="%.6f", help="Enter venue latitude")
                with col_loc2:
                    venue_lng = st.number_input("Longitude", value=77.6431, format="%.6f", help="Enter venue longitude")
                
                venue_location = (venue_lat, venue_lng)
                
                # Venue name input
                venue_name = st.text_input("Venue Name (Optional)", placeholder="e.g., Bangalore Exhibition Center")
                
                # Get venue info from Maps API
                if st.button("🔍 Get Venue Information"):
                    with st.spinner("Getting venue information..."):
                        venue_info = self._get_venue_info(venue_lat, venue_lng, venue_name)
                        
                        if venue_info:
                            st.success("✅ Venue information retrieved!")
                            
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.write(f"**Venue:** {venue_info.get('name', 'Unknown')}")
                                st.write(f"**Type:** {venue_info.get('type', 'Unknown')}")
                                st.write(f"**Address:** {venue_info.get('address', 'Unknown')}")
                            
                            with col_info2:
                                st.write(f"**Rating:** {venue_info.get('rating', 'N/A')}")
                                st.write(f"**Capacity Estimate:** {venue_info.get('estimated_capacity', 'Unknown')}")
                                st.write(f"**Crowd Factor:** {venue_info.get('crowd_factor', 'Unknown')}")
                        else:
                            st.warning("⚠️ Could not retrieve venue information")
                
                # Analysis button
                if uploaded_video and venue_location:
                    if st.button("🚀 Start Video Analysis", type="primary"):
                        with st.spinner("🔄 Analyzing uploaded video..."):
                            # Save uploaded video temporarily
                            temp_video_path = f"temp_video_{int(time.time())}.mp4"
                            with open(temp_video_path, "wb") as f:
                                f.write(uploaded_video.read())
                            
                            # Run analysis with location
                            analysis_result = self._analyze_uploaded_video(temp_video_path, venue_location, venue_info)
                            
                            # Store results
                            st.session_state['uploaded_video_analysis'] = analysis_result
                            st.session_state['venue_location'] = venue_location
                            st.session_state['venue_info'] = venue_info
                            
                            # Clean up temp file
                            import os
                            if os.path.exists(temp_video_path):
                                os.remove(temp_video_path)
                            
                            st.success("✅ Video analysis complete!")
            
            # Display uploaded video analysis results
            if 'uploaded_video_analysis' in st.session_state:
                st.subheader("📊 Uploaded Video Analysis Results")
                analysis = st.session_state['uploaded_video_analysis']
                
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric("People Count", analysis.get('people_count', 0))
                with col_res2:
                    st.metric("Density Score", f"{analysis.get('density_score', 0)}/10")
                with col_res3:
                    st.metric("Alert Level", analysis.get('alert_level', 'normal').upper())
                
                # Flow analysis
                if analysis.get('flow_direction'):
                    st.info(f"🌊 Crowd Flow: {analysis['flow_direction'].title()}")
                
                # Predictions
                if analysis.get('prediction_15min'):
                    st.warning(f"🔮 15-min Prediction: {analysis['prediction_15min']}")
                
                # Show venue map with crowd flow
                if 'venue_location' in st.session_state and 'venue_info' in st.session_state:
                    self._show_crowd_flow_map(st.session_state['venue_location'], analysis, st.session_state['venue_info'])
            
            # Video display placeholder
            video_placeholder = st.empty()
            
            # Current frame analysis
            if st.session_state.get('monitoring_active', False):
                status = get_live_crowd_status()
                current_analysis = status.get('current_analysis')
                
                if current_analysis:
                    # Display current frame (if available)
                    if live_predictor.live_data.get('video_feed') is not None:
                        frame = live_predictor.live_data['video_feed']
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(frame_rgb, caption="Live Video Feed", use_column_width=True)
                    
                    # Current analysis metrics
                    st.subheader("📊 Current Analysis")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("People Count", current_analysis.get('people_count', 0))
                    with col_b:
                        st.metric("Density Score", f"{current_analysis.get('density_score', 0)}/10")
                    with col_c:
                        st.metric("Movement", current_analysis.get('movement_type', 'Unknown').title())
                    with col_d:
                        alert_level = current_analysis.get('alert_level', 'normal')
                        st.metric("Alert Level", alert_level.upper())
                    
                    # Flow direction
                    flow_direction = current_analysis.get('flow_direction', 'unknown')
                    st.info(f"🌊 Crowd Flow Direction: {flow_direction.title()}")
                    
                    # Safety concerns
                    safety_concerns = current_analysis.get('safety_concerns', [])
                    if safety_concerns:
                        st.warning("⚠️ Safety Concerns Detected:")
                        for concern in safety_concerns:
                            st.write(f"• {concern}")
                    
                    # Bottlenecks
                    bottlenecks = current_analysis.get('bottlenecks', [])
                    if bottlenecks:
                        st.error("🚧 Bottlenecks Detected:")
                        for bottleneck in bottlenecks:
                            st.write(f"• {bottleneck}")
                
                else:
                    st.info("📹 Waiting for video analysis data...")
            else:
                st.info("👆 Start live monitoring from sidebar to begin analysis")
        
        with col2:
            st.subheader("🔮 15-20 Min Predictions")
            
            if st.session_state.get('monitoring_active', False):
                status = get_live_crowd_status()
                prediction = status.get('latest_prediction')
                
                if prediction:
                    # Prediction metrics
                    pred_time = prediction.get('prediction_time', 'Unknown')
                    if isinstance(pred_time, str):
                        pred_time_str = pred_time
                    else:
                        pred_time_str = pred_time.strftime('%H:%M') if pred_time else 'Unknown'
                    
                    st.info(f"🕐 Prediction for: {pred_time_str}")
                    
                    col_e, col_f = st.columns(2)
                    with col_e:
                        st.metric("Predicted People", prediction.get('predicted_people_count', 0))
                    with col_f:
                        st.metric("Predicted Density", f"{prediction.get('predicted_density', 0)}/10")
                    
                    # Trends
                    people_trend = prediction.get('people_trend', 'stable')
                    density_trend = prediction.get('density_trend', 'stable')
                    
                    trend_color = "🔴" if "increasing" in people_trend else "🟢" if "decreasing" in people_trend else "🟡"
                    st.write(f"{trend_color} People Trend: {people_trend.title()}")
                    
                    trend_color = "🔴" if "increasing" in density_trend else "🟢" if "decreasing" in density_trend else "🟡"
                    st.write(f"{trend_color} Density Trend: {density_trend.title()}")
                    
                    # Bottleneck risk
                    bottleneck_risk = prediction.get('bottleneck_risk', 'low')
                    risk_color = "🔴" if bottleneck_risk == 'high' else "🟡" if bottleneck_risk == 'medium' else "🟢"
                    st.write(f"{risk_color} Bottleneck Risk: {bottleneck_risk.title()}")
                    
                    # Confidence
                    confidence = prediction.get('confidence', 0)
                    st.progress(confidence)
                    st.caption(f"Prediction Confidence: {confidence:.1%}")
                
                else:
                    st.info("🔮 Generating predictions...")
            
            # Recent alerts
            st.subheader("🚨 Recent Alerts")
            
            if st.session_state.get('monitoring_active', False):
                status = get_live_crowd_status()
                alerts = status.get('recent_alerts', [])
                
                if alerts:
                    for alert in alerts[-3:]:  # Last 3 alerts
                        alert_level = alert.get('level', 'normal')
                        alert_time = alert.get('timestamp', datetime.now())
                        alert_message = alert.get('message', 'No message')
                        
                        if alert_level == 'critical':
                            st.error(f"🚨 {alert_time.strftime('%H:%M')} - {alert_message}")
                        elif alert_level == 'warning':
                            st.warning(f"⚠️ {alert_time.strftime('%H:%M')} - {alert_message}")
                        else:
                            st.info(f"ℹ️ {alert_time.strftime('%H:%M')} - {alert_message}")
                else:
                    st.success("✅ No recent alerts")
        
        # Maps Integration Section
        st.markdown("---")
        st.subheader("🗺️ Maps Integration & Zone Analysis")
        
        if st.session_state.get('monitoring_active', False):
            status = get_live_crowd_status()
            zone_analyses = status.get('zone_analyses', {})
            
            if zone_analyses:
                # Zone cards
                cols = st.columns(len(zone_analyses))
                
                for i, (zone_name, zone_data) in enumerate(zone_analyses.items()):
                    with cols[i % len(cols)]:
                        zone_status = zone_data.get('zone_status', 'normal')
                        crowd_estimate = zone_data.get('combined_crowd_estimate', 0)
                        
                        # Zone card styling based on status
                        if zone_status == 'critical':
                            st.markdown(f"""
                            <div class="alert-critical">
                                <h4>🔴 {zone_name.replace('_', ' ').title()}</h4>
                                <p><strong>Status:</strong> {zone_status.upper()}</p>
                                <p><strong>Estimated People:</strong> {crowd_estimate}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif zone_status == 'warning':
                            st.markdown(f"""
                            <div class="alert-warning">
                                <h4>🟡 {zone_name.replace('_', ' ').title()}</h4>
                                <p><strong>Status:</strong> {zone_status.upper()}</p>
                                <p><strong>Estimated People:</strong> {crowd_estimate}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="alert-normal">
                                <h4>🟢 {zone_name.replace('_', ' ').title()}</h4>
                                <p><strong>Status:</strong> {zone_status.upper()}</p>
                                <p><strong>Estimated People:</strong> {crowd_estimate}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Zone recommendations
                        recommendations = zone_data.get('recommendations', [])
                        if recommendations:
                            st.write("**Actions:**")
                            for rec in recommendations:
                                st.write(f"• {rec}")
        
        # Auto refresh
        if st.session_state.get('auto_refresh', False) and st.session_state.get('monitoring_active', False):
            time.sleep(2)
            st.rerun()

    def bangalore_test_page(self):
        """Bangalore Exhibition Center test page"""
        st.header("🏢 Bangalore International Exhibition Center - Test Mode")
        
        st.info("""
        **Test Venue:** Bangalore International Exhibition Center
        **Location:** 13.0358°N, 77.6431°E
        **Purpose:** Testing crowd prediction system with predefined venue zones
        """)
        
        # Venue map (placeholder)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Venue Layout")
            
            # Create a simple venue map visualization
            venue_data = {
                'Zone': ['Main Entrance', 'Hall 1', 'Hall 2', 'Food Court', 'Parking'],
                'Lat': [13.0360, 13.0358, 13.0356, 13.0354, 13.0362],
                'Lng': [77.6430, 77.6432, 77.6434, 77.6428, 77.6425],
                'Capacity': [200, 500, 500, 150, 300]
            }
            
            df = pd.DataFrame(venue_data)
            
            # Create map
            fig = px.scatter_mapbox(
                df, 
                lat="Lat", 
                lon="Lng",
                hover_name="Zone",
                hover_data=["Capacity"],
                color="Capacity",
                size="Capacity",
                color_continuous_scale="Viridis",
                size_max=15,
                zoom=16,
                mapbox_style="open-street-map",
                title="Bangalore Exhibition Center - Zone Layout"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Test Controls")
            
            # Test mode controls
            test_mode = st.selectbox(
                "Test Scenario",
                ["Normal Operations", "High Crowd Event", "Emergency Simulation", "Peak Hours"]
            )
            
            if st.button("🚀 Run Test Scenario"):
                with st.spinner("Running test scenario..."):
                    # Simulate test results based on scenario
                    test_results = self._simulate_test_scenario(test_mode)
                    
                    st.success("✅ Test completed!")
                    
                    # Display test results
                    st.subheader("📊 Test Results")
                    
                    for zone, data in test_results.items():
                        st.write(f"**{zone}:**")
                        st.write(f"• Estimated People: {data['people']}")
                        st.write(f"• Status: {data['status']}")
                        st.write(f"• Alert Level: {data['alert']}")
                        st.write("---")
        
        # Zone-wise analysis
        st.subheader("📊 Zone-wise Analysis")
        
        if st.session_state.get('monitoring_active', False):
            status = get_live_crowd_status()
            zone_analyses = status.get('zone_analyses', {})
            
            # Create zone comparison chart
            if zone_analyses:
                zone_names = list(zone_analyses.keys())
                crowd_estimates = [zone_analyses[zone]['combined_crowd_estimate'] for zone in zone_names]
                
                fig = px.bar(
                    x=[name.replace('_', ' ').title() for name in zone_names],
                    y=crowd_estimates,
                    title="Current Crowd Distribution by Zone",
                    labels={'x': 'Zone', 'y': 'Estimated People'},
                    color=crowd_estimates,
                    color_continuous_scale="RdYlGn_r"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Historical data simulation
        st.subheader("📈 Historical Patterns (Simulated)")
        
        # Generate sample historical data
        hours = list(range(24))
        crowd_patterns = {
            'Main Entrance': [20, 15, 10, 8, 12, 25, 45, 80, 60, 40, 35, 50, 70, 65, 55, 60, 85, 90, 75, 60, 45, 35, 30, 25],
            'Hall 1': [30, 20, 15, 10, 15, 35, 60, 120, 100, 80, 70, 90, 110, 105, 95, 100, 130, 140, 120, 100, 80, 60, 50, 40],
            'Food Court': [10, 5, 3, 2, 5, 15, 25, 40, 35, 30, 45, 80, 90, 85, 70, 75, 85, 80, 60, 40, 25, 20, 15, 12]
        }
        
        fig = go.Figure()
        
        for zone, pattern in crowd_patterns.items():
            fig.add_trace(go.Scatter(
                x=hours,
                y=pattern,
                mode='lines+markers',
                name=zone,
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="24-Hour Crowd Pattern Analysis",
            xaxis_title="Hour of Day",
            yaxis_title="Estimated People",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _simulate_test_scenario(self, scenario: str) -> Dict:
        """Test scenario simulate karta hai"""
        scenarios = {
            "Normal Operations": {
                "Main Entrance": {"people": 25, "status": "normal", "alert": "normal"},
                "Hall 1": {"people": 80, "status": "normal", "alert": "normal"},
                "Hall 2": {"people": 60, "status": "normal", "alert": "normal"},
                "Food Court": {"people": 35, "status": "normal", "alert": "normal"},
                "Parking": {"people": 45, "status": "normal", "alert": "normal"}
            },
            "High Crowd Event": {
                "Main Entrance": {"people": 120, "status": "warning", "alert": "warning"},
                "Hall 1": {"people": 350, "status": "critical", "alert": "critical"},
                "Hall 2": {"people": 280, "status": "warning", "alert": "warning"},
                "Food Court": {"people": 95, "status": "caution", "alert": "caution"},
                "Parking": {"people": 180, "status": "caution", "alert": "caution"}
            },
            "Emergency Simulation": {
                "Main Entrance": {"people": 200, "status": "critical", "alert": "critical"},
                "Hall 1": {"people": 450, "status": "critical", "alert": "critical"},
                "Hall 2": {"people": 380, "status": "critical", "alert": "critical"},
                "Food Court": {"people": 120, "status": "warning", "alert": "warning"},
                "Parking": {"people": 250, "status": "warning", "alert": "warning"}
            },
            "Peak Hours": {
                "Main Entrance": {"people": 85, "status": "caution", "alert": "caution"},
                "Hall 1": {"people": 220, "status": "warning", "alert": "warning"},
                "Hall 2": {"people": 180, "status": "caution", "alert": "caution"},
                "Food Court": {"people": 75, "status": "normal", "alert": "normal"},
                "Parking": {"people": 120, "status": "normal", "alert": "normal"}
            }
        }
        
        return scenarios.get(scenario, scenarios["Normal Operations"])

    def analytics_dashboard(self):
        """Analytics dashboard page"""
        st.header("📊 Analytics Dashboard")
        
        if not st.session_state.get('monitoring_active', False):
            st.warning("⚠️ Start live monitoring to see analytics data")
            return
        
        # Get current status
        status = get_live_crowd_status()
        
        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)
        
        overall = status.get('overall_status', {})
        
        with col1:
            st.metric("Total People", overall.get('total_estimated_people', 0))
        with col2:
            st.metric("Alert Level", overall.get('overall_alert_level', 'normal').upper())
        with col3:
            st.metric("Critical Zones", overall.get('critical_zones', 0))
        with col4:
            st.metric("System Confidence", f"{overall.get('system_confidence', 0):.1%}")
        
        # Crowd history chart
        if live_predictor.live_data['crowd_history']:
            st.subheader("📈 Crowd History")
            
            history_data = []
            for entry in live_predictor.live_data['crowd_history'][-20:]:  # Last 20 entries
                history_data.append({
                    'Time': entry['timestamp'].strftime('%H:%M:%S'),
                    'People Count': entry.get('people_count', 0),
                    'Density Score': entry.get('density_score', 0),
                    'Alert Level': entry.get('alert_level', 'normal')
                })
            
            df = pd.DataFrame(history_data)
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=df['Time'], y=df['People Count'], name="People Count", line=dict(color='blue')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=df['Time'], y=df['Density Score'], name="Density Score", line=dict(color='red')),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Time")
            fig.update_yaxes(title_text="People Count", secondary_y=False)
            fig.update_yaxes(title_text="Density Score", secondary_y=True)
            
            fig.update_layout(title_text="Crowd Metrics Over Time")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Predictions chart
        if live_predictor.live_data['predictions']:
            st.subheader("🔮 Prediction Accuracy")
            
            pred_data = []
            for pred in live_predictor.live_data['predictions'][-10:]:  # Last 10 predictions
                pred_data.append({
                    'Time': pred['timestamp'].strftime('%H:%M:%S'),
                    'Predicted People': pred.get('predicted_people_count', 0),
                    'Predicted Density': pred.get('predicted_density', 0),
                    'Confidence': pred.get('confidence', 0)
                })
            
            df_pred = pd.DataFrame(pred_data)
            
            fig = px.line(df_pred, x='Time', y=['Predicted People', 'Predicted Density'], 
                         title="Prediction Trends")
            st.plotly_chart(fig, use_container_width=True)

    def zone_management_page(self):
        """Zone management page"""
        st.header("🗺️ Zone Management")
        
        st.info("Configure and monitor individual zones within your venue")
        
        # Zone configuration
        st.subheader("⚙️ Zone Configuration")
        
        # Display current zones
        zones = live_predictor.test_venue['zones']
        
        for zone_name, zone_coords in zones.items():
            with st.expander(f"📍 {zone_name.replace('_', ' ').title()}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Latitude:** {zone_coords['lat']}")
                    st.write(f"**Longitude:** {zone_coords['lng']}")
                
                with col2:
                    # Zone status
                    if st.session_state.get('monitoring_active', False):
                        status = get_live_crowd_status()
                        zone_analyses = status.get('zone_analyses', {})
                        
                        if zone_name in zone_analyses:
                            zone_data = zone_analyses[zone_name]
                            zone_status = zone_data.get('zone_status', 'normal')
                            crowd_estimate = zone_data.get('combined_crowd_estimate', 0)
                            
                            st.metric("Current Status", zone_status.upper())
                            st.metric("Estimated People", crowd_estimate)
                
                with col3:
                    # Zone controls
                    if st.button(f"📊 Analyze {zone_name}", key=f"analyze_{zone_name}"):
                        zone_analysis = live_predictor.get_zone_analysis(zone_name, zone_coords)
                        st.json(zone_analysis)

    def _analyze_uploaded_video(self, video_path: str, venue_location: Tuple[float, float], venue_info: Dict) -> Dict:
        """Uploaded video ko analyze karta hai"""
        try:
            # Initialize video capture
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Could not open video file"}
            
            # Get a frame from middle of video for analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame = frame_count // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {"error": "Could not read frame from video"}
            
            # Analyze frame with AI
            analysis = self._analyze_frame_with_gemini(frame)
            
            # Add venue context
            analysis['venue_location'] = venue_location
            analysis['venue_info'] = venue_info
            
            # Generate prediction based on current analysis
            if analysis.get('people_count', 0) > 0:
                prediction = self._generate_crowd_prediction(analysis)
                analysis['prediction_15min'] = prediction
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_frame_with_gemini(self, frame) -> Dict:
        """Frame ko Gemini AI se analyze karta hai"""
        try:
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # AI prompt for crowd analysis
            prompt = """
            You are an expert crowd analysis system. Analyze this image very carefully for accurate crowd counting and density assessment.
            
            CRITICAL INSTRUCTIONS FOR PEOPLE COUNTING:
            1. COUNT EVERY PERSON: Look at the entire image systematically
            2. INCLUDE PARTIAL BODIES: Count people even if only partially visible
            3. LOOK IN BACKGROUND: Don't miss people in the back/distance
            4. CHECK ALL AREAS: Scan left to right, top to bottom
            5. COUNT HEADS: Focus on counting heads/faces for accuracy
            6. INCLUDE CHILDREN: Count all ages, including small children
            7. LOOK FOR GROUPS: People often cluster together
            8. CHECK SHADOWS: Sometimes people are in shadows
            9. ZOOM ANALYSIS: Look carefully at crowded areas
            10. DOUBLE CHECK: Count again to verify your number
            
            DENSITY ASSESSMENT BASED ON COUNT:
            - 1-2: Almost empty (0-5 people)
            - 3-4: Light crowd (6-20 people)  
            - 5-6: Moderate crowd (21-50 people)
            - 7-8: Dense crowd (51-100 people)
            - 9-10: Very dense/packed (100+ people)
            
            Respond in JSON:
            {
                "people_count": exact_number_of_people_you_counted,
                "density_score": number_1_to_10_based_on_actual_count,
                "movement_type": "movement_description",
                "flow_direction": "direction",
                "safety_concerns": ["list of concerns"],
                "alert_level": "normal/caution/warning/critical"
            }
            
            BE EXTREMELY ACCURATE WITH COUNTING. This is for public safety.
            """
            
            # Gemini API call
            gemini_key = "AIzaSyC4_per5A9LO_9sfankoh40SxlX7OXQ-S8"
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(gemini_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    return analysis_data
                else:
                    return {"error": "Could not parse AI response"}
            else:
                return {"error": f"AI analysis failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Frame analysis failed: {str(e)}"}
    
    def _generate_crowd_prediction(self, current_analysis: Dict) -> str:
        """Current analysis ke base pe prediction generate karta hai"""
        try:
            current_count = current_analysis.get('people_count', 0)
            current_density = current_analysis.get('density_score', 0)
            movement_type = current_analysis.get('movement_type', 'stable')
            
            # Simple prediction logic
            if 'increasing' in movement_type.lower():
                predicted_count = int(current_count * 1.3)
                trend = "increasing"
            elif 'decreasing' in movement_type.lower():
                predicted_count = int(current_count * 0.7)
                trend = "decreasing"
            else:
                predicted_count = current_count
                trend = "stable"
            
            return f"Predicted crowd in 15-20 minutes: {predicted_count} people (trend: {trend})"
            
        except Exception as e:
            return f"Prediction failed: {str(e)}"
    
    def _show_crowd_flow_map(self, venue_location: Tuple[float, float], analysis: Dict, venue_info: Dict):
        """Venue map with crowd flow display karta hai"""
        try:
            import pandas as pd
            import plotly.express as px
            
            # Create map data
            map_data = {
                'lat': [venue_location[0]],
                'lng': [venue_location[1]],
                'venue': [venue_info.get('name', 'Venue')],
                'people_count': [analysis.get('people_count', 0)],
                'density': [analysis.get('density_score', 0)]
            }
            
            df = pd.DataFrame(map_data)
            
            # Create map
            fig = px.scatter_mapbox(
                df,
                lat="lat",
                lon="lng",
                hover_name="venue",
                hover_data=["people_count", "density"],
                color="density",
                size="people_count",
                color_continuous_scale="RdYlGn_r",
                size_max=20,
                zoom=15,
                mapbox_style="open-street-map",
                title="Venue Location with Crowd Analysis"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Map display failed: {str(e)}")

    def _get_venue_info(self, lat: float, lng: float, venue_name: str = "") -> Dict:
        """Maps API se venue information nikalta hai"""
        try:
            maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
            
            # Nearby places search
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 500,
                'key': maps_key
            }
            
            response = requests.get(places_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                # Find the best matching venue
                best_venue = None
                if venue_name:
                    # Search for venue by name
                    for place in places:
                        if venue_name.lower() in place.get('name', '').lower():
                            best_venue = place
                            break
                
                if not best_venue and places:
                    # Take the first place with highest rating
                    best_venue = max(places, key=lambda x: x.get('rating', 0))
                
                if best_venue:
                    # Get detailed place info
                    place_id = best_venue.get('place_id')
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'place_id': place_id,
                        'fields': 'name,formatted_address,rating,user_ratings_total,types,geometry',
                        'key': maps_key
                    }
                    
                    details_response = requests.get(details_url, params=details_params, timeout=10)
                    
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        place_details = details_data.get('result', {})
                        
                        # Estimate venue capacity based on type
                        place_types = place_details.get('types', [])
                        estimated_capacity = self._estimate_venue_capacity(place_types)
                        
                        # Calculate crowd factor
                        rating = place_details.get('rating', 0)
                        user_ratings = place_details.get('user_ratings_total', 0)
                        crowd_factor = self._calculate_crowd_factor(rating, user_ratings, place_types)
                        
                        return {
                            'name': place_details.get('name', 'Unknown Venue'),
                            'address': place_details.get('formatted_address', 'Unknown Address'),
                            'type': ', '.join(place_types[:3]) if place_types else 'Unknown',
                            'rating': rating,
                            'user_ratings_total': user_ratings,
                            'estimated_capacity': estimated_capacity,
                            'crowd_factor': crowd_factor,
                            'coordinates': {
                                'lat': place_details.get('geometry', {}).get('location', {}).get('lat', lat),
                                'lng': place_details.get('geometry', {}).get('location', {}).get('lng', lng)
                            }
                        }
            
            return {}
            
        except Exception as e:
            print(f"Error getting venue info: {e}")
            return {}

    def _estimate_venue_capacity(self, place_types: List[str]) -> str:
        """Place types ke basis par capacity estimate karta hai"""
        capacity_map = {
            'stadium': '10,000-50,000',
            'shopping_mall': '2,000-5,000',
            'convention_center': '1,000-10,000',
            'tourist_attraction': '500-2,000',
            'restaurant': '50-200',
            'movie_theater': '100-500',
            'gym': '50-300',
            'hospital': '200-1,000',
            'school': '500-2,000',
            'university': '2,000-20,000',
            'park': '100-1,000',
            'transit_station': '500-5,000'
        }
        
        for place_type in place_types:
            if place_type in capacity_map:
                return capacity_map[place_type]
        
        return '100-500'  # Default estimate

    def _calculate_crowd_factor(self, rating: float, user_ratings: int, place_types: List[str]) -> str:
        """Crowd factor calculate karta hai"""
        score = 0
        
        # Rating factor
        if rating >= 4.5:
            score += 30
        elif rating >= 4.0:
            score += 20
        elif rating >= 3.5:
            score += 10
        
        # User ratings factor
        if user_ratings >= 1000:
            score += 30
        elif user_ratings >= 500:
            score += 20
        elif user_ratings >= 100:
            score += 10
        
        # Place type factor
        high_crowd_types = ['stadium', 'shopping_mall', 'tourist_attraction', 'transit_station']
        if any(ptype in high_crowd_types for ptype in place_types):
            score += 25
        
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Medium'
        else:
            return 'Low'

    def _analyze_uploaded_video(self, video_path: str, location: Tuple[float, float], venue_info: Dict) -> Dict:
        """Uploaded video ko analyze karta hai"""
        try:
            # Import live predictor functions
            from live_crowd_predictor import LiveCrowdPredictor
            
            predictor = LiveCrowdPredictor()
            
            # Analyze video frames
            cap = cv2.VideoCapture(video_path)
            
            frame_analyses = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Analyze every 30th frame to save time
                if frame_count % 30 == 0:
                    analysis = predictor._analyze_frame_with_ai(frame)
                    frame_analyses.append(analysis)
                
                # Limit to 10 analyses for uploaded video
                if len(frame_analyses) >= 10:
                    break
            
            cap.release()
            
            if not frame_analyses:
                return {'error': 'Could not analyze video frames'}
            
            # Aggregate results
            people_counts = [a.get('people_count', 0) for a in frame_analyses]
            density_scores = [a.get('density_score', 0) for a in frame_analyses]
            flow_directions = [a.get('flow_direction', 'unknown') for a in frame_analyses]
            alert_levels = [a.get('alert_level', 'normal') for a in frame_analyses]
            
            # Calculate averages
            avg_people = sum(people_counts) / len(people_counts) if people_counts else 0
            avg_density = sum(density_scores) / len(density_scores) if density_scores else 0
            
            # Most common flow direction
            most_common_flow = max(set(flow_directions), key=flow_directions.count) if flow_directions else 'unknown'
            
            # Highest alert level
            alert_priority = {'normal': 0, 'caution': 1, 'warning': 2, 'critical': 3}
            highest_alert = max(alert_levels, key=lambda x: alert_priority.get(x, 0)) if alert_levels else 'normal'
            
            # Generate prediction based on analysis
            prediction = self._generate_video_prediction(avg_people, avg_density, venue_info)
            
            return {
                'people_count': int(avg_people),
                'density_score': round(avg_density, 1),
                'flow_direction': most_common_flow,
                'alert_level': highest_alert,
                'prediction_15min': prediction,
                'frame_count': frame_count,
                'analyses_performed': len(frame_analyses),
                'venue_context': venue_info
            }
            
        except Exception as e:
            print(f"Error analyzing uploaded video: {e}")
            return {'error': str(e)}

    def _generate_video_prediction(self, avg_people: float, avg_density: float, venue_info: Dict) -> str:
        """Video analysis ke basis par prediction generate karta hai"""
        try:
            venue_capacity = venue_info.get('estimated_capacity', '100-500')
            crowd_factor = venue_info.get('crowd_factor', 'Medium')
            
            # Extract capacity number for calculation
            capacity_parts = venue_capacity.split('-')
            if len(capacity_parts) == 2:
                max_capacity = int(capacity_parts[1].replace(',', ''))
            else:
                max_capacity = 500  # Default
            
            # Calculate utilization
            utilization = (avg_people / max_capacity) * 100 if max_capacity > 0 else 0
            
            # Generate prediction based on current state
            if avg_density >= 8 or utilization >= 80:
                return f"CRITICAL: Expect overcrowding. Current {avg_people:.0f} people may increase to {avg_people * 1.3:.0f}. Immediate crowd control needed."
            elif avg_density >= 6 or utilization >= 60:
                return f"WARNING: Crowd likely to increase. From {avg_people:.0f} to {avg_people * 1.2:.0f} people expected. Enhanced monitoring required."
            elif avg_density >= 4 or utilization >= 40:
                return f"CAUTION: Moderate increase expected. {avg_people:.0f} people may grow to {avg_people * 1.1:.0f}. Continue monitoring."
            else:
                return f"NORMAL: Stable crowd conditions. {avg_people:.0f} people expected to remain steady. Standard monitoring sufficient."
                
        except Exception as e:
            return f"Unable to generate prediction: {str(e)}"

    def _show_crowd_flow_map(self, location: Tuple[float, float], analysis: Dict, venue_info: Dict):
        """Venue map par crowd flow analysis show karta hai"""
        try:
            st.subheader("🗺️ Venue Map with Crowd Flow Analysis")
            
            # Create map data
            lat, lng = location
            
            # Base venue point
            map_data = {
                'Latitude': [lat],
                'Longitude': [lng],
                'Location': [venue_info.get('name', 'Venue')],
                'People_Count': [analysis.get('people_count', 0)],
                'Density': [analysis.get('density_score', 0)],
                'Alert_Level': [analysis.get('alert_level', 'normal')]
            }
            
            # Add flow direction points
            flow_direction = analysis.get('flow_direction', 'unknown')
            if flow_direction != 'unknown':
                # Create directional points based on flow
                flow_points = self._generate_flow_points(lat, lng, flow_direction)
                
                for i, (flow_lat, flow_lng, flow_type) in enumerate(flow_points):
                    map_data['Latitude'].append(flow_lat)
                    map_data['Longitude'].append(flow_lng)
                    map_data['Location'].append(f'Flow {flow_type}')
                    map_data['People_Count'].append(analysis.get('people_count', 0) // (i + 2))
                    map_data['Density'].append(analysis.get('density_score', 0) - i)
                    map_data['Alert_Level'].append('flow')
            
            df = pd.DataFrame(map_data)
            
            # Create color mapping for alert levels
            color_map = {
                'normal': 'green',
                'caution': 'yellow', 
                'warning': 'orange',
                'critical': 'red',
                'flow': 'blue'
            }
            
            df['Color'] = df['Alert_Level'].map(color_map)
            
            # Create map
            fig = px.scatter_mapbox(
                df,
                lat="Latitude",
                lon="Longitude",
                hover_name="Location",
                hover_data=["People_Count", "Density", "Alert_Level"],
                color="Alert_Level",
                color_discrete_map=color_map,
                size="People_Count",
                size_max=20,
                zoom=16,
                mapbox_style="open-street-map",
                title=f"Crowd Flow Analysis - {venue_info.get('name', 'Venue')}"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Flow analysis summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Flow Direction", flow_direction.title())
            with col2:
                st.metric("Venue Capacity", venue_info.get('estimated_capacity', 'Unknown'))
            with col3:
                st.metric("Crowd Factor", venue_info.get('crowd_factor', 'Unknown'))
            
            # Recommendations based on analysis
            st.subheader("💡 Location-Specific Recommendations")
            
            recommendations = self._generate_location_recommendations(analysis, venue_info)
            for rec in recommendations:
                st.write(f"• {rec}")
                
        except Exception as e:
            st.error(f"Error showing crowd flow map: {e}")

    def _generate_flow_points(self, center_lat: float, center_lng: float, flow_direction: str) -> List[Tuple[float, float, str]]:
        """Flow direction ke basis par points generate karta hai"""
        points = []
        offset = 0.001  # Small offset for visualization
        
        if flow_direction.lower() in ['north', 'up']:
            points.append((center_lat + offset, center_lng, 'North'))
            points.append((center_lat + offset*2, center_lng, 'North Exit'))
        elif flow_direction.lower() in ['south', 'down']:
            points.append((center_lat - offset, center_lng, 'South'))
            points.append((center_lat - offset*2, center_lng, 'South Exit'))
        elif flow_direction.lower() in ['east', 'right']:
            points.append((center_lat, center_lng + offset, 'East'))
            points.append((center_lat, center_lng + offset*2, 'East Exit'))
        elif flow_direction.lower() in ['west', 'left']:
            points.append((center_lat, center_lng - offset, 'West'))
            points.append((center_lat, center_lng - offset*2, 'West Exit'))
        else:  # mixed or unknown
            points.append((center_lat + offset/2, center_lng + offset/2, 'Mixed Flow 1'))
            points.append((center_lat - offset/2, center_lng - offset/2, 'Mixed Flow 2'))
        
        return points

    def _generate_location_recommendations(self, analysis: Dict, venue_info: Dict) -> List[str]:
        """Location aur analysis ke basis par recommendations generate karta hai"""
        recommendations = []
        
        people_count = analysis.get('people_count', 0)
        density_score = analysis.get('density_score', 0)
        alert_level = analysis.get('alert_level', 'normal')
        venue_type = venue_info.get('type', '')
        
        # General recommendations based on alert level
        if alert_level == 'critical':
            recommendations.extend([
                "🚨 IMMEDIATE: Deploy emergency crowd control at venue",
                "🚫 Consider restricting entry to prevent overcrowding",
                "📢 Activate emergency communication systems"
            ])
        elif alert_level == 'warning':
            recommendations.extend([
                "⚠️ Increase security presence at main entry points",
                "📊 Implement crowd counting at entrances",
                "🔄 Prepare crowd flow management measures"
            ])
        
        # Venue-specific recommendations
        if 'exhibition' in venue_type.lower() or 'convention' in venue_type.lower():
            recommendations.extend([
                "🏢 Monitor hall capacity limits closely",
                "🚪 Ensure multiple exit routes are clearly marked",
                "📋 Coordinate with event organizers for crowd management"
            ])
        elif 'shopping' in venue_type.lower():
            recommendations.extend([
                "🛍️ Monitor peak shopping hours (evenings/weekends)",
                "🚗 Ensure adequate parking management",
                "🏪 Coordinate with store management for crowd control"
            ])
        elif 'stadium' in venue_type.lower() or 'sports' in venue_type.lower():
            recommendations.extend([
                "🏟️ Implement entry time staggering",
                "🎫 Monitor ticket gate flow rates",
                "🚌 Coordinate with transportation services"
            ])
        
        # Flow-specific recommendations
        flow_direction = analysis.get('flow_direction', 'unknown')
        if flow_direction != 'unknown' and flow_direction != 'mixed':
            recommendations.append(f"🌊 Optimize {flow_direction} exit routes for crowd flow")
        
        # Density-specific recommendations
        if density_score >= 7:
            recommendations.append("📏 Consider implementing social distancing measures")
        
        return recommendations[:8]  # Limit to 8 recommendations

def main():
    """Main function"""
    ui = CrowdPredictionUI()
    ui.run()

if __name__ == "__main__":
    main()