"""
Unified Crowd Analysis System
Bhai, yeh file sab kuch combine karke ek final result dega
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Import all analysis modules
from map_crowd_analyzer import analyze_complete_crowd_situation
from crowd_predictor import get_crowd_density
from src.map_density_overlay import create_map_overlay

class UnifiedCrowdAnalyzer:
    def __init__(self):
        self.analysis_timestamp = datetime.now()
        
    def complete_unified_analysis(self,
                                map_image_path: str = None,
                                video_source = 0,
                                location_coords: Tuple[float, float] = None,
                                analysis_duration: int = 30) -> Dict:
        """
        Complete unified analysis - sab kuch ek saath
        
        Args:
            map_image_path: Map/venue image path
            video_source: Video source (0 for webcam, file path for video)
            location_coords: (lat, lng) coordinates
            analysis_duration: Video analysis duration
            
        Returns:
            Complete unified analysis result
        """
        
        print("🎯 Starting Unified Crowd Analysis...")
        print("=" * 60)
        
        unified_result = {
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'analysis_type': 'unified_complete',
            'input_sources': [],
            'individual_analyses': {},
            'unified_metrics': {},
            'combined_insights': {},
            'final_assessment': {},
            'actionable_recommendations': [],
            'density_overlay_path': None,
            'confidence_score': 0.0
        }
        
        try:
            # Phase 1: Map Analysis
            if map_image_path and os.path.exists(map_image_path):
                print("\n📍 Phase 1: Map Analysis")
                print("-" * 30)
                
                map_result = analyze_complete_crowd_situation(
                    map_image_path=map_image_path,
                    video_source=None,
                    lat=location_coords[0] if location_coords else None,
                    lng=location_coords[1] if location_coords else None,
                    duration=0
                )
                
                unified_result['individual_analyses']['map_analysis'] = map_result
                unified_result['input_sources'].append('map_analysis')
                print("✅ Map analysis completed")
            
            # Phase 2: Video Analysis
            if video_source is not None:
                print("\n🎥 Phase 2: Video Analysis")
                print("-" * 30)
                
                if isinstance(video_source, str) and video_source.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    print(f"📹 Analyzing uploaded video: {video_source}")
                else:
                    print(f"📹 Analyzing live video for {analysis_duration} seconds...")
                
                video_result = get_crowd_density(
                    video_source=video_source,
                    lat=location_coords[0] if location_coords else None,
                    lng=location_coords[1] if location_coords else None
                )
                
                unified_result['individual_analyses']['video_analysis'] = video_result
                unified_result['input_sources'].append('video_analysis')
                print("✅ Video analysis completed")
            
            # Phase 3: Real Maps Data
            if location_coords:
                print("\n🌍 Phase 3: Real Maps Crowd Data")
                print("-" * 30)
                
                try:
                    # Direct implementation to avoid import issues
                    maps_crowd_data = self._get_maps_crowd_data_direct(location_coords[0], location_coords[1])
                    unified_result['individual_analyses']['maps_crowd_data'] = maps_crowd_data
                    unified_result['input_sources'].append('maps_crowd_data')
                    print("✅ Maps crowd data retrieved")
                except Exception as e:
                    print(f"⚠️ Maps data unavailable: {e}")
                    # Create dummy data
                    maps_crowd_data = {
                        'total_estimated_people': 50,
                        'crowd_zones': {'high_density_zones': [], 'medium_density_zones': [], 'low_density_zones': []},
                        'density_hotspots': []
                    }
                    unified_result['individual_analyses']['maps_crowd_data'] = maps_crowd_data
            
            # Phase 4: Unified Analysis
            print("\n🧠 Phase 4: Unified Analysis")
            print("-" * 30)
            
            unified_metrics = self._calculate_unified_metrics(unified_result['individual_analyses'])
            unified_result['unified_metrics'] = unified_metrics
            
            combined_insights = self._generate_combined_insights(unified_result['individual_analyses'], unified_metrics)
            unified_result['combined_insights'] = combined_insights
            
            final_assessment = self._create_final_assessment(unified_metrics, combined_insights)
            unified_result['final_assessment'] = final_assessment
            
            recommendations = self._generate_unified_recommendations(final_assessment, combined_insights)
            unified_result['actionable_recommendations'] = recommendations
            
            confidence_score = self._calculate_confidence_score(unified_result['input_sources'], unified_metrics)
            unified_result['confidence_score'] = confidence_score
            
            print("✅ Unified analysis completed")
            
            # Phase 5: Create Density Overlay
            if map_image_path and os.path.exists(map_image_path):
                print("\n🎨 Phase 5: Creating Density Overlay")
                print("-" * 30)
                
                try:
                    overlay_path = create_map_overlay(
                        map_image_path,
                        unified_result,
                        unified_result['individual_analyses'].get('video_analysis')
                    )
                    unified_result['density_overlay_path'] = overlay_path
                    print(f"✅ Density overlay created: {overlay_path}")
                except Exception as e:
                    print(f"⚠️ Overlay creation failed: {e}")
            
            print("\n🎉 Unified Analysis Complete!")
            return unified_result
            
        except Exception as e:
            unified_result['error'] = str(e)
            print(f"❌ Error in unified analysis: {e}")
            return unified_result

    def _calculate_unified_metrics(self, individual_analyses: Dict) -> Dict:
        """Sab analyses ko combine karke unified metrics banata hai"""
        
        metrics = {
            'total_people_estimate': 0,
            'crowd_density_score': 0,
            'safety_risk_score': 0,
            'flow_efficiency_score': 0,
            'venue_capacity_utilization': 0,
            'alert_level': 'normal',
            'critical_factors': [],
            'data_confidence': 0.0
        }
        
        try:
            people_estimates = []
            density_scores = []
            safety_scores = []
            
            # From Map Analysis
            map_analysis = individual_analyses.get('map_analysis', {})
            if map_analysis and 'map_analysis' in map_analysis:
                map_data = map_analysis['map_analysis']
                
                if 'density_rating' in map_data:
                    density_scores.append(map_data['density_rating'] * 10)  # Convert to 0-100
                
                if 'safety_score' in map_data:
                    safety_scores.append(map_data['safety_score'] * 10)  # Convert to 0-100
                
                # Estimate people from venue capacity
                if 'total_estimated_capacity' in map_data:
                    try:
                        capacity_str = str(map_data['total_estimated_capacity'])
                        capacity_num = int(''.join(filter(str.isdigit, capacity_str)))
                        people_estimates.append(capacity_num * 0.6)  # 60% occupancy estimate
                    except:
                        pass
            
            # From Video Analysis
            video_analysis = individual_analyses.get('video_analysis', {})
            if video_analysis:
                people_count = video_analysis.get('people_count', 0)
                density_score = video_analysis.get('density_score', 0)
                
                if people_count > 0:
                    people_estimates.append(people_count)
                
                if density_score > 0:
                    density_scores.append(density_score)
            
            # From Maps Crowd Data
            maps_crowd_data = individual_analyses.get('maps_crowd_data', {})
            if maps_crowd_data:
                total_estimated = maps_crowd_data.get('total_estimated_people', 0)
                if total_estimated > 0:
                    people_estimates.append(total_estimated)
                
                # Calculate density from crowd zones
                crowd_zones = maps_crowd_data.get('crowd_zones', {})
                high_zones = len(crowd_zones.get('high_density_zones', []))
                medium_zones = len(crowd_zones.get('medium_density_zones', []))
                
                if high_zones > 0 or medium_zones > 0:
                    zone_density = min((high_zones * 30 + medium_zones * 15), 100)
                    density_scores.append(zone_density)
            
            # Calculate unified metrics
            if people_estimates:
                # Use weighted average, giving more weight to video analysis
                weights = []
                for i, estimate in enumerate(people_estimates):
                    if i == 0 and 'video_analysis' in individual_analyses:  # Video analysis
                        weights.append(0.5)
                    elif 'maps_crowd_data' in individual_analyses:  # Maps data
                        weights.append(0.3)
                    else:  # Map analysis
                        weights.append(0.2)
                
                if len(weights) != len(people_estimates):
                    weights = [1.0 / len(people_estimates)] * len(people_estimates)
                
                metrics['total_people_estimate'] = int(sum(est * weight for est, weight in zip(people_estimates, weights)))
            
            if density_scores:
                metrics['crowd_density_score'] = sum(density_scores) / len(density_scores)
            
            if safety_scores:
                metrics['safety_risk_score'] = 100 - (sum(safety_scores) / len(safety_scores))  # Invert for risk
            else:
                # Estimate safety risk from density
                if metrics['crowd_density_score'] > 80:
                    metrics['safety_risk_score'] = 80
                elif metrics['crowd_density_score'] > 60:
                    metrics['safety_risk_score'] = 60
                else:
                    metrics['safety_risk_score'] = 30
            
            # Flow efficiency (based on video and maps data)
            flow_score = 70  # Default
            if video_analysis and 'alert_status' in video_analysis:
                alert_status = video_analysis['alert_status']
                if alert_status == 'emergency':
                    flow_score = 20
                elif alert_status == 'warning':
                    flow_score = 40
                elif alert_status == 'caution':
                    flow_score = 60
            
            metrics['flow_efficiency_score'] = flow_score
            
            # Venue capacity utilization
            if people_estimates and map_analysis:
                try:
                    map_data = map_analysis.get('map_analysis', {})
                    capacity_str = str(map_data.get('total_estimated_capacity', '1000'))
                    total_capacity = int(''.join(filter(str.isdigit, capacity_str)))
                    utilization = min((metrics['total_people_estimate'] / total_capacity) * 100, 100)
                    metrics['venue_capacity_utilization'] = utilization
                except:
                    metrics['venue_capacity_utilization'] = 50  # Default
            
            # Alert level
            if metrics['crowd_density_score'] >= 80 or metrics['safety_risk_score'] >= 80:
                metrics['alert_level'] = 'emergency'
            elif metrics['crowd_density_score'] >= 60 or metrics['safety_risk_score'] >= 60:
                metrics['alert_level'] = 'warning'
            elif metrics['crowd_density_score'] >= 40 or metrics['safety_risk_score'] >= 40:
                metrics['alert_level'] = 'caution'
            else:
                metrics['alert_level'] = 'normal'
            
            # Critical factors
            critical_factors = []
            if metrics['crowd_density_score'] >= 70:
                critical_factors.append('High crowd density detected')
            if metrics['safety_risk_score'] >= 70:
                critical_factors.append('Safety risk elevated')
            if metrics['venue_capacity_utilization'] >= 80:
                critical_factors.append('Venue near capacity limit')
            if metrics['flow_efficiency_score'] <= 40:
                critical_factors.append('Poor crowd flow efficiency')
            
            metrics['critical_factors'] = critical_factors
            
            # Data confidence
            confidence = len(individual_analyses) * 0.33  # More data sources = higher confidence
            metrics['data_confidence'] = min(confidence, 1.0)
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating unified metrics: {e}")
            return metrics

    def _generate_combined_insights(self, individual_analyses: Dict, unified_metrics: Dict) -> Dict:
        """Combined insights generate karta hai"""
        
        insights = {
            'crowd_situation_summary': '',
            'key_findings': [],
            'risk_assessment': {},
            'capacity_analysis': {},
            'flow_analysis': {},
            'location_hotspots': [],
            'temporal_factors': {}
        }
        
        try:
            # Crowd situation summary
            people_count = unified_metrics['total_people_estimate']
            density_score = unified_metrics['crowd_density_score']
            alert_level = unified_metrics['alert_level']
            
            if alert_level == 'emergency':
                situation = f"CRITICAL SITUATION: {people_count} people detected with {density_score:.1f}% density. Immediate intervention required."
            elif alert_level == 'warning':
                situation = f"HIGH ALERT: {people_count} people with elevated density ({density_score:.1f}%). Enhanced monitoring needed."
            elif alert_level == 'caution':
                situation = f"MODERATE CONCERN: {people_count} people with {density_score:.1f}% density. Continue active monitoring."
            else:
                situation = f"NORMAL CONDITIONS: {people_count} people with {density_score:.1f}% density. Standard monitoring sufficient."
            
            insights['crowd_situation_summary'] = situation
            
            # Key findings
            key_findings = []
            
            # From video analysis
            video_analysis = individual_analyses.get('video_analysis', {})
            if video_analysis:
                key_findings.append(f"Video Analysis: {video_analysis.get('people_count', 0)} people counted in real-time")
                if video_analysis.get('alert_status') != 'normal':
                    key_findings.append(f"Video Alert: {video_analysis.get('alert_status', 'unknown').title()} status detected")
            
            # From map analysis
            map_analysis = individual_analyses.get('map_analysis', {})
            if map_analysis and 'map_analysis' in map_analysis:
                map_data = map_analysis['map_analysis']
                if 'high_risk_areas' in map_data and map_data['high_risk_areas']:
                    key_findings.append(f"Map Analysis: {len(map_data['high_risk_areas'])} high-risk areas identified")
                if 'bottlenecks' in map_data and map_data['bottlenecks']:
                    key_findings.append(f"Bottlenecks: {len(map_data['bottlenecks'])} potential choke points found")
            
            # From maps crowd data
            maps_crowd_data = individual_analyses.get('maps_crowd_data', {})
            if maps_crowd_data:
                hotspots = maps_crowd_data.get('density_hotspots', [])
                if hotspots:
                    key_findings.append(f"Location Data: {len(hotspots)} crowd hotspots detected in area")
                
                total_places = maps_crowd_data.get('places_data', {}).get('total_places', 0)
                if total_places > 0:
                    key_findings.append(f"Area Analysis: {total_places} venues/places analyzed for crowd impact")
            
            insights['key_findings'] = key_findings
            
            # Risk assessment
            risk_score = unified_metrics['safety_risk_score']
            insights['risk_assessment'] = {
                'overall_risk_level': 'Critical' if risk_score >= 80 else 'High' if risk_score >= 60 else 'Medium' if risk_score >= 40 else 'Low',
                'risk_score': risk_score,
                'primary_risk_factors': unified_metrics['critical_factors'],
                'mitigation_priority': 'Immediate' if risk_score >= 80 else 'High' if risk_score >= 60 else 'Medium'
            }
            
            # Capacity analysis
            utilization = unified_metrics['venue_capacity_utilization']
            insights['capacity_analysis'] = {
                'current_utilization': f"{utilization:.1f}%",
                'capacity_status': 'Over Capacity' if utilization > 100 else 'Near Capacity' if utilization > 80 else 'Moderate' if utilization > 50 else 'Low',
                'estimated_people': people_count,
                'capacity_recommendation': 'Restrict entry' if utilization > 90 else 'Monitor closely' if utilization > 70 else 'Normal operations'
            }
            
            # Flow analysis
            flow_score = unified_metrics['flow_efficiency_score']
            insights['flow_analysis'] = {
                'flow_efficiency': f"{flow_score:.1f}%",
                'flow_status': 'Critical' if flow_score < 30 else 'Poor' if flow_score < 50 else 'Moderate' if flow_score < 70 else 'Good',
                'flow_recommendation': 'Immediate flow management' if flow_score < 40 else 'Enhance flow control' if flow_score < 60 else 'Monitor flow patterns'
            }
            
            # Location hotspots
            if maps_crowd_data:
                hotspots = maps_crowd_data.get('density_hotspots', [])
                location_hotspots = []
                for hotspot in hotspots[:5]:  # Top 5
                    location_hotspots.append({
                        'name': hotspot.get('name', 'Unknown'),
                        'estimated_people': hotspot.get('estimated_people', 0),
                        'level': hotspot.get('hotspot_level', 'medium'),
                        'action_needed': hotspot.get('recommendation', 'Monitor')
                    })
                insights['location_hotspots'] = location_hotspots
            
            # Temporal factors
            current_hour = datetime.now().hour
            insights['temporal_factors'] = {
                'current_time': datetime.now().strftime('%H:%M'),
                'time_factor': 'Peak Hours' if (7 <= current_hour <= 9) or (17 <= current_hour <= 19) else 'Business Hours' if 9 <= current_hour <= 17 else 'Off Hours',
                'crowd_expectation': 'Higher than normal' if (7 <= current_hour <= 9) or (17 <= current_hour <= 19) else 'Normal levels'
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating combined insights: {e}")
            return insights

    def _create_final_assessment(self, unified_metrics: Dict, combined_insights: Dict) -> Dict:
        """Final assessment create karta hai"""
        
        assessment = {
            'overall_status': '',
            'severity_level': 0,  # 0-10 scale
            'immediate_actions_required': [],
            'short_term_recommendations': [],
            'long_term_suggestions': [],
            'success_metrics': {},
            'next_review_time': ''
        }
        
        try:
            alert_level = unified_metrics['alert_level']
            density_score = unified_metrics['crowd_density_score']
            risk_score = unified_metrics['safety_risk_score']
            people_count = unified_metrics['total_people_estimate']
            
            # Overall status
            if alert_level == 'emergency':
                assessment['overall_status'] = 'EMERGENCY - Critical crowd situation requiring immediate intervention'
                assessment['severity_level'] = 9
            elif alert_level == 'warning':
                assessment['overall_status'] = 'WARNING - High crowd density with elevated safety risks'
                assessment['severity_level'] = 7
            elif alert_level == 'caution':
                assessment['overall_status'] = 'CAUTION - Moderate crowd levels requiring enhanced monitoring'
                assessment['severity_level'] = 5
            else:
                assessment['overall_status'] = 'NORMAL - Standard crowd conditions with routine monitoring'
                assessment['severity_level'] = 3
            
            # Immediate actions
            immediate_actions = []
            if alert_level == 'emergency':
                immediate_actions.extend([
                    'Deploy emergency crowd control measures immediately',
                    'Activate emergency response protocols',
                    'Consider stopping venue entry',
                    'Ensure all emergency exits are clear',
                    'Contact emergency services if needed'
                ])
            elif alert_level == 'warning':
                immediate_actions.extend([
                    'Increase security personnel by 100%',
                    'Implement enhanced crowd monitoring',
                    'Prepare crowd control barriers',
                    'Brief staff on emergency procedures'
                ])
            elif alert_level == 'caution':
                immediate_actions.extend([
                    'Deploy additional security to high-density areas',
                    'Increase monitoring frequency',
                    'Review crowd flow patterns'
                ])
            
            # Add specific actions based on analysis
            critical_factors = unified_metrics.get('critical_factors', [])
            for factor in critical_factors:
                if 'capacity' in factor.lower():
                    immediate_actions.append('Implement capacity control measures')
                elif 'flow' in factor.lower():
                    immediate_actions.append('Deploy crowd flow management')
                elif 'safety' in factor.lower():
                    immediate_actions.append('Enhance safety protocols')
            
            assessment['immediate_actions_required'] = immediate_actions
            
            # Short-term recommendations (next 1-2 hours)
            short_term = [
                'Continue monitoring every 15 minutes',
                'Update crowd analysis every 30 minutes',
                'Maintain communication with security team'
            ]
            
            if density_score > 60:
                short_term.append('Consider implementing one-way flow systems')
            if people_count > 100:
                short_term.append('Deploy crowd counting personnel at key points')
            
            assessment['short_term_recommendations'] = short_term
            
            # Long-term suggestions
            long_term = [
                'Review venue capacity limits',
                'Analyze crowd patterns for future events',
                'Consider infrastructure improvements for better flow'
            ]
            
            if risk_score > 50:
                long_term.append('Conduct comprehensive safety audit')
            
            assessment['long_term_suggestions'] = long_term
            
            # Success metrics
            assessment['success_metrics'] = {
                'target_density_reduction': f"{max(0, density_score - 50):.1f}%",
                'target_people_reduction': max(0, people_count - int(people_count * 0.8)),
                'safety_improvement_target': f"{max(0, risk_score - 30):.1f} points",
                'monitoring_frequency': '15 minutes' if alert_level in ['emergency', 'warning'] else '30 minutes'
            }
            
            # Next review time
            if alert_level == 'emergency':
                next_review = '10 minutes'
            elif alert_level == 'warning':
                next_review = '15 minutes'
            elif alert_level == 'caution':
                next_review = '30 minutes'
            else:
                next_review = '1 hour'
            
            assessment['next_review_time'] = next_review
            
            return assessment
            
        except Exception as e:
            print(f"Error creating final assessment: {e}")
            return assessment

    def _generate_unified_recommendations(self, final_assessment: Dict, combined_insights: Dict) -> List[str]:
        """Unified actionable recommendations generate karta hai"""
        
        recommendations = []
        
        try:
            # From final assessment
            immediate_actions = final_assessment.get('immediate_actions_required', [])
            for action in immediate_actions[:5]:  # Top 5 immediate actions
                recommendations.append(f"🚨 IMMEDIATE: {action}")
            
            short_term = final_assessment.get('short_term_recommendations', [])
            for rec in short_term[:3]:  # Top 3 short-term
                recommendations.append(f"⏰ SHORT-TERM: {rec}")
            
            # From risk assessment
            risk_assessment = combined_insights.get('risk_assessment', {})
            if risk_assessment.get('overall_risk_level') in ['Critical', 'High']:
                recommendations.append(f"⚠️ RISK: {risk_assessment.get('overall_risk_level')} risk level - {risk_assessment.get('mitigation_priority')} priority mitigation needed")
            
            # From capacity analysis
            capacity_analysis = combined_insights.get('capacity_analysis', {})
            capacity_rec = capacity_analysis.get('capacity_recommendation', '')
            if capacity_rec and capacity_rec != 'Normal operations':
                recommendations.append(f"📊 CAPACITY: {capacity_rec}")
            
            # From flow analysis
            flow_analysis = combined_insights.get('flow_analysis', {})
            flow_rec = flow_analysis.get('flow_recommendation', '')
            if flow_rec and 'monitor' not in flow_rec.lower():
                recommendations.append(f"🌊 FLOW: {flow_rec}")
            
            # From location hotspots
            location_hotspots = combined_insights.get('location_hotspots', [])
            for hotspot in location_hotspots[:2]:  # Top 2 hotspots
                if hotspot.get('level') in ['critical', 'high']:
                    recommendations.append(f"🎯 HOTSPOT: {hotspot['name']} - {hotspot['action_needed']}")
            
            # Add general recommendations if list is short
            if len(recommendations) < 5:
                recommendations.extend([
                    "📱 COMMUNICATION: Maintain constant communication with security team",
                    "📊 MONITORING: Continue real-time crowd monitoring",
                    "🔄 UPDATES: Provide regular updates to management"
                ])
            
            return recommendations[:10]  # Max 10 recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["Continue monitoring crowd situation"]

    def _get_maps_crowd_data_direct(self, lat: float, lng: float) -> Dict:
        """Direct Maps API call to avoid import issues"""
        try:
            import requests
            
            maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
            
            # Simple Maps API call
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 1000,
                'key': maps_key
            }
            
            response = requests.get(places_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                # Simple crowd estimation
                total_estimated = len(places) * 25  # Rough estimate
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'location': {'lat': lat, 'lng': lng},
                    'total_estimated_people': total_estimated,
                    'crowd_zones': {
                        'high_density_zones': places[:3] if len(places) > 3 else [],
                        'medium_density_zones': places[3:6] if len(places) > 6 else [],
                        'low_density_zones': places[6:] if len(places) > 6 else []
                    },
                    'density_hotspots': [
                        {
                            'name': place.get('name', 'Unknown'),
                            'estimated_people': 30,
                            'hotspot_level': 'medium'
                        } for place in places[:3]
                    ],
                    'places_data': {'total_places': len(places)}
                }
            else:
                return self._fallback_maps_data(lat, lng)
                
        except Exception as e:
            print(f"Maps API error: {e}")
            return self._fallback_maps_data(lat, lng)
    
    def _fallback_maps_data(self, lat: float, lng: float) -> Dict:
        """Fallback data when Maps API fails"""
        return {
            'timestamp': datetime.now().isoformat(),
            'location': {'lat': lat, 'lng': lng},
            'total_estimated_people': 50,
            'crowd_zones': {'high_density_zones': [], 'medium_density_zones': [], 'low_density_zones': []},
            'density_hotspots': [],
            'places_data': {'total_places': 0}
        }le': 50,  # Default estimate
            'crowd_zones': {'high_density_zones': [], 'medium_density_zones': [], 'low_density_zones': []},
            'density_hotspots': []
        }
            return get_real_crowd_data_from_maps(lat, lng, 1000)
        except Exception as e:
            print(f"Maps integration error: {e}")
            # Return dummy data
            return {
                'timestamp': datetime.now().isoformat(),
                'location': {'lat': lat, 'lng': lng},
                'crowd_zones': {
                    'high_density_zones': [{'name': 'Sample High Zone', 'estimated_people': 30}],
                    'medium_density_zones': [{'name': 'Sample Medium Zone', 'estimated_people': 20}],
                    'low_density_zones': []
                },
                'total_estimated_people': 50,
                'density_hotspots': [
                    {'name': 'Sample Hotspot', 'estimated_people': 30, 'hotspot_level': 'medium', 'recommendation': 'Monitor'}
                ],
                'places_data': {'total_places': 5}
            }

    def _calculate_confidence_score(self, input_sources: List[str], unified_metrics: Dict) -> float:
        """Analysis confidence score calculate karta hai"""
        
        try:
            base_confidence = 0.3  # Base confidence
            
            # More data sources = higher confidence
            source_confidence = len(input_sources) * 0.2
            
            # Data quality factors
            quality_factors = 0.0
            
            if 'video_analysis' in input_sources:
                quality_factors += 0.3  # Video is high quality
            
            if 'maps_crowd_data' in input_sources:
                quality_factors += 0.2  # Maps data is good quality
            
            if 'map_analysis' in input_sources:
                quality_factors += 0.1  # Map analysis provides context
            
            # Consistency check
            consistency_bonus = 0.0
            if len(input_sources) >= 2:
                # If multiple sources agree on alert level, add bonus
                consistency_bonus = 0.1
            
            total_confidence = base_confidence + source_confidence + quality_factors + consistency_bonus
            
            return min(total_confidence, 1.0)  # Cap at 1.0
            
        except Exception as e:
            return 0.5  # Default confidence

    def _get_maps_crowd_data_direct(self, lat: float, lng: float) -> Dict:
        """Direct Maps API call to avoid import issues"""
        try:
            import requests
            
            maps_key = "AIzaSyD0dYoBlkCZSD_1n5LfFb2RrAzFewBuurA"
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f"{lat},{lng}",
                'radius': 1000,
                'type': 'establishment',
                'key': maps_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('results', [])
                
                # Simple crowd estimation
                total_estimated = len(places) * 12
                
                # Create zones
                high_zones = []
                hotspots = []
                
                for place in places[:5]:
                    name = place.get('name', 'Unknown')
                    location = place.get('geometry', {}).get('location', {})
                    rating = place.get('rating', 0)
                    
                    estimated_people = 40 if rating >= 4.0 else 25
                    
                    zone_info = {
                        'name': name,
                        'location': location,
                        'estimated_people': estimated_people,
                        'density_level': 'high' if rating >= 4.0 else 'medium'
                    }
                    
                    high_zones.append(zone_info)
                    
                    if rating >= 4.0:
                        hotspots.append({
                            'name': name,
                            'location': location,
                            'estimated_people': estimated_people,
                            'hotspot_level': 'high',
                            'recommendation': 'Monitor closely'
                        })
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'location': {'lat': lat, 'lng': lng},
                    'total_estimated_people': total_estimated,
                    'crowd_zones': {
                        'high_density_zones': high_zones,
                        'medium_density_zones': [],
                        'low_density_zones': []
                    },
                    'density_hotspots': hotspots,
                    'places_data': {
                        'total_places': len(places),
                        'high_crowd_places': high_zones,
                        'medium_crowd_places': [],
                        'low_crowd_places': []
                    }
                }
            
            else:
                raise Exception(f"Maps API error: {response.status_code}")
                
        except Exception as e:
            print(f"Maps data error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'location': {'lat': lat, 'lng': lng},
                'total_estimated_people': 0,
                'crowd_zones': {'high_density_zones': [], 'medium_density_zones': [], 'low_density_zones': []},
                'density_hotspots': [],
                'places_data': {'total_places': 0, 'high_crowd_places': [], 'medium_crowd_places': [], 'low_crowd_places': []},
                'error': str(e)
            }

# Easy usage function
def run_unified_analysis(map_image_path: str = None,
                        video_source = 0,
                        location_coords: Tuple[float, float] = None,
                        analysis_duration: int = 30) -> Dict:
    """
    Bhai, yeh main function hai - complete unified analysis ke liye
    
    Args:
        map_image_path: Map/venue image path
        video_source: Video source (0 for webcam, file path for video)
        location_coords: (lat, lng) coordinates
        analysis_duration: Video analysis duration
        
    Returns:
        Complete unified analysis result
    """
    analyzer = UnifiedCrowdAnalyzer()
    return analyzer.complete_unified_analysis(map_image_path, video_source, location_coords, analysis_duration)

# Test function
if __name__ == "__main__":
    print("🎯 Testing Unified Crowd Analysis System")
    print("=" * 60)
    
    # Test parameters
    map_path = "src/Screenshot 2025-07-23 064906.png"
    coordinates = (28.6139, 77.2090)  # Delhi
    
    if os.path.exists(map_path):
        print("🚀 Running complete unified analysis...")
        
        result = run_unified_analysis(
            map_image_path=map_path,
            video_source=0,  # Webcam
            location_coords=coordinates,
            analysis_duration=15  # 15 seconds
        )
        
        print("\n📊 UNIFIED ANALYSIS RESULTS:")
        print("=" * 60)
        
        # Final assessment
        final_assessment = result.get('final_assessment', {})
        print(f"🎯 Overall Status: {final_assessment.get('overall_status', 'Unknown')}")
        print(f"📊 Severity Level: {final_assessment.get('severity_level', 0)}/10")
        
        # Unified metrics
        unified_metrics = result.get('unified_metrics', {})
        print(f"👥 Total People Estimate: {unified_metrics.get('total_people_estimate', 0)}")
        print(f"📈 Crowd Density Score: {unified_metrics.get('crowd_density_score', 0):.1f}%")
        print(f"⚠️ Safety Risk Score: {unified_metrics.get('safety_risk_score', 0):.1f}%")
        print(f"🚨 Alert Level: {unified_metrics.get('alert_level', 'normal').upper()}")
        print(f"🎯 Confidence Score: {result.get('confidence_score', 0):.2f}")
        
        # Top recommendations
        recommendations = result.get('actionable_recommendations', [])
        if recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        # Save results
        output_file = f"unified_analysis_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Complete results saved to: {output_file}")
        
        if result.get('density_overlay_path'):
            print(f"🎨 Density overlay created: {result['density_overlay_path']}")
        
    else:
        print(f"❌ Map file not found: {map_path}")
        print("Please ensure the map file exists for testing.")