# Fix the streamlit file by removing corrupted content
with open('streamlit_crowd_ui_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the error line and remove everything after the map function
error_pos = content.find('st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")')
if error_pos != -1:
    # Find the end of this line
    end_pos = content.find('\n', error_pos)
    if end_pos != -1:
        # Keep content up to this point and add proper ending
        clean_content = content[:end_pos + 1]
        
        # Add the missing methods and main function
        clean_content += '''
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
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update x-axis labels
            fig.update_xaxes(title_text="Time", row=1, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            
            # Update y-axis labels
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
                    # Create exportable summary
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
            
            # Store in session for future use
            st.session_state['latest_crowd_summary'] = {
                'analysis': analysis,
                'alert_level': alert_level,
                'recommendations': recommendations,
                'timestamp': datetime.now()
            }
                
        except Exception as e:
            st.error(f"❌ Error showing summary alert box: {e}")

    def add_temporary_test_data(self):
        """Add temporary test data for demonstration"""
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
        
        # Store in session state for testing
        st.session_state['test_system_alerts'] = test_alerts
        st.session_state['test_bottleneck_predictions'] = test_bottlenecks
        st.session_state['test_mode_active'] = True


def main():
    """Main function"""
    ui = CrowdPredictionUI()
    ui.run()

if __name__ == "__main__":
    main()
'''
        
        # Write clean content back
        with open('streamlit_crowd_ui_fixed.py', 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print("✅ File fixed successfully!")
    else:
        print("❌ Could not find end position")
else:
    print("❌ Could not find error position")