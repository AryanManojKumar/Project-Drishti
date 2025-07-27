"""Enhanced forecasting model using Gemini for bottleneck prediction."""

import os
import json
import logging
import requests
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd

class GeminiBottleneckForecaster:
    """Predicts crowd bottlenecks using Gemini AI for intelligent forecasting."""
    
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', 'project-dishti')
        self.gemini_api_key = "AIzaSyDq4jVjvz76mpWE2_8qTuMRRfEToyGryK8"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_api_key}"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def predict_bottlenecks_with_gemini(self, current_data: Dict, historical_data: List[Dict] = None) -> List[Dict]:
        """
        Use Gemini to predict bottlenecks based on current and historical data.
        
        Args:
            current_data: Current crowd and device data
            historical_data: Historical crowd patterns (optional)
            
        Returns:
            List of predictions per zone
        """
        try:
            # Prepare data for Gemini analysis
            analysis_prompt = self._create_analysis_prompt(current_data, historical_data)
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": analysis_prompt
                    }]
                }]
            }
            
            # Make API request to Gemini
            response = requests.post(
                self.gemini_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parse Gemini's prediction response
                    predictions = self._parse_gemini_predictions(text_response, current_data)
                    return predictions
                    
            else:
                self.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._fallback_predictions(current_data)
                
        except Exception as e:
            self.logger.error(f"Error calling Gemini for predictions: {e}")
            return self._fallback_predictions(current_data)
    
    def _create_analysis_prompt(self, current_data: Dict, historical_data: List[Dict] = None) -> str:
        """Create a comprehensive prompt for Gemini crowd analysis."""
        
        current_time = datetime.utcnow()
        prediction_time = current_time + timedelta(minutes=20)
        
        prompt = f"""
You are an expert crowd management AI system. Analyze the following crowd data and predict bottlenecks 20 minutes from now.

CURRENT TIME: {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
PREDICTION TARGET: {prediction_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (20 minutes ahead)

CURRENT CROWD DATA:
{json.dumps(current_data, indent=2)}

ANALYSIS FACTORS TO CONSIDER:
1. Current crowd density and person counts
2. Time of day patterns (rush hours, lunch time, etc.)
3. Day of week effects (weekday vs weekend)
4. Movement patterns and flow directions
5. Device location data trends
6. Seasonal and event-based factors

HISTORICAL CONTEXT:
{json.dumps(historical_data[:5] if historical_data else [], indent=2)}

Please provide predictions for each zone in the following JSON format:
{{
  "predictions": [
    {{
      "zone_id": "zone_name",
      "current_status": {{
        "person_count": number,
        "density_level": "low/medium/high/critical",
        "current_risk": "low/medium/high/critical"
      }},
      "prediction_20min": {{
        "predicted_person_count": number,
        "predicted_density_level": "low/medium/high/critical",
        "bottleneck_probability": 0.0-1.0,
        "risk_level": "low/medium/high/critical",
        "confidence": 0.0-1.0
      }},
      "reasoning": "explanation of prediction logic",
      "recommendations": ["action1", "action2"],
      "key_factors": ["factor1", "factor2"]
    }}
  ],
  "overall_assessment": {{
    "total_zones_at_risk": number,
    "highest_risk_zone": "zone_name",
    "recommended_actions": ["action1", "action2"],
    "confidence_level": 0.0-1.0
  }}
}}

Focus on practical, actionable insights for crowd management teams.
"""
        return prompt
    
    def _parse_gemini_predictions(self, text_response: str, current_data: Dict) -> List[Dict]:
        """Parse Gemini's prediction response into structured format."""
        try:
            # Clean the response
            clean_response = text_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON response
            gemini_analysis = json.loads(clean_response)
            
            # Convert to our standard format
            predictions = []
            
            for pred in gemini_analysis.get('predictions', []):
                formatted_pred = {
                    'zone_id': pred['zone_id'],
                    'prediction_time': datetime.utcnow().isoformat(),
                    'forecast_time': (datetime.utcnow() + timedelta(minutes=20)).isoformat(),
                    'bottleneck_probability': pred['prediction_20min']['bottleneck_probability'],
                    'predicted_density': pred['prediction_20min'].get('predicted_person_count', 0),
                    'alert_level': pred['prediction_20min']['risk_level'],
                    'requires_intervention': pred['prediction_20min']['bottleneck_probability'] > 0.7,
                    'confidence': pred['prediction_20min']['confidence'],
                    'reasoning': pred['reasoning'],
                    'recommendations': pred['recommendations'],
                    'key_factors': pred['key_factors'],
                    'analysis_method': 'gemini_ai'
                }
                predictions.append(formatted_pred)
            
            # Add overall assessment
            if predictions:
                predictions[0]['overall_assessment'] = gemini_analysis.get('overall_assessment', {})
            
            return predictions
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse Gemini prediction JSON: {e}")
            return self._parse_text_predictions(text_response, current_data)
        except Exception as e:
            self.logger.error(f"Error parsing Gemini predictions: {e}")
            return self._fallback_predictions(current_data)
    
    def _parse_text_predictions(self, text: str, current_data: Dict) -> List[Dict]:
        """Parse text response when JSON parsing fails."""
        predictions = []
        
        # Extract zones from current data
        zones = current_data.get('zones', {})
        
        for zone_id, zone_data in zones.items():
            # Simple text analysis for risk assessment
            risk_level = "medium"
            bottleneck_prob = 0.5
            
            text_lower = text.lower()
            zone_lower = zone_id.lower()
            
            # Look for zone-specific mentions
            if zone_lower in text_lower:
                if any(word in text_lower for word in ['high risk', 'critical', 'dangerous']):
                    risk_level = "critical"
                    bottleneck_prob = 0.8
                elif any(word in text_lower for word in ['low risk', 'safe', 'normal']):
                    risk_level = "low"
                    bottleneck_prob = 0.2
            
            prediction = {
                'zone_id': zone_id,
                'prediction_time': datetime.utcnow().isoformat(),
                'forecast_time': (datetime.utcnow() + timedelta(minutes=20)).isoformat(),
                'bottleneck_probability': bottleneck_prob,
                'predicted_density': zone_data.get('person_count', 0) * 1.2,
                'alert_level': risk_level,
                'requires_intervention': bottleneck_prob > 0.7,
                'confidence': 0.6,
                'reasoning': 'Parsed from Gemini text response',
                'recommendations': ['Monitor closely', 'Prepare intervention'],
                'key_factors': ['Current density', 'Time patterns'],
                'analysis_method': 'gemini_text_parsing'
            }
            predictions.append(prediction)
        
        return predictions
    
    def _fallback_predictions(self, current_data: Dict) -> List[Dict]:
        """Fallback predictions when Gemini API fails."""
        predictions = []
        
        zones = current_data.get('zones', {})
        
        for zone_id, zone_data in zones.items():
            current_density = zone_data.get('density', 0)
            current_count = zone_data.get('person_count', 0)
            
            # Simple rule-based prediction
            bottleneck_prob = min(current_density / 4.0, 1.0)  # Assuming 4.0 is critical density
            
            if bottleneck_prob > 0.8:
                alert_level = "critical"
            elif bottleneck_prob > 0.6:
                alert_level = "high"
            elif bottleneck_prob > 0.4:
                alert_level = "medium"
            else:
                alert_level = "low"
            
            prediction = {
                'zone_id': zone_id,
                'prediction_time': datetime.utcnow().isoformat(),
                'forecast_time': (datetime.utcnow() + timedelta(minutes=20)).isoformat(),
                'bottleneck_probability': bottleneck_prob,
                'predicted_density': current_count * 1.1,  # Assume 10% increase
                'alert_level': alert_level,
                'requires_intervention': bottleneck_prob > 0.7,
                'confidence': 0.5,
                'reasoning': 'Fallback rule-based prediction',
                'recommendations': ['Standard monitoring'],
                'key_factors': ['Current density only'],
                'analysis_method': 'fallback_rules'
            }
            predictions.append(prediction)
        
        return predictions
    
    def generate_crowd_insights(self, current_data: Dict, predictions: List[Dict]) -> Dict:
        """Generate comprehensive crowd management insights using Gemini."""
        try:
            insight_prompt = f"""
Based on the current crowd data and predictions, provide comprehensive crowd management insights:

CURRENT DATA:
{json.dumps(current_data, indent=2)}

PREDICTIONS:
{json.dumps(predictions, indent=2)}

Please provide insights in JSON format:
{{
  "executive_summary": "brief overview of current situation",
  "immediate_actions": ["action1", "action2"],
  "resource_allocation": {{
    "high_priority_zones": ["zone1", "zone2"],
    "staff_deployment": "recommendations",
    "equipment_needs": ["item1", "item2"]
  }},
  "risk_assessment": {{
    "overall_risk_level": "low/medium/high/critical",
    "time_to_critical": "minutes or 'none'",
    "evacuation_readiness": "assessment"
  }},
  "communication_strategy": {{
    "public_announcements": ["message1", "message2"],
    "staff_alerts": ["alert1", "alert2"]
  }}
}}
"""
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": insight_prompt
                    }]
                }]
            }
            
            response = requests.post(
                self.gemini_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parse insights
                    clean_response = text_response.strip()
                    if clean_response.startswith('```json'):
                        clean_response = clean_response.replace('```json', '').replace('```', '').strip()
                    
                    insights = json.loads(clean_response)
                    insights['generated_at'] = datetime.utcnow().isoformat()
                    insights['analysis_method'] = 'gemini_insights'
                    
                    return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
        
        # Fallback insights
        return {
            'executive_summary': 'Basic crowd monitoring active',
            'immediate_actions': ['Continue monitoring'],
            'analysis_method': 'fallback_insights',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def test_gemini_forecasting(self):
        """Test Gemini forecasting functionality."""
        print("Testing Gemini forecasting integration...")
        
        # Sample current data
        test_data = {
            'zones': {
                'entrance_main': {
                    'person_count': 25,
                    'density': 2.5,
                    'device_count': 30,
                    'flow_velocity': 1.2
                },
                'food_court': {
                    'person_count': 15,
                    'density': 1.8,
                    'device_count': 20,
                    'flow_velocity': 0.8
                }
            }
        }
        
        try:
            predictions = self.predict_bottlenecks_with_gemini(test_data)
            print("✅ Gemini forecasting successful!")
            print(f"Generated {len(predictions)} predictions")
            
            for pred in predictions:
                print(f"Zone {pred['zone_id']}: {pred['bottleneck_probability']:.2f} probability, "
                      f"method: {pred['analysis_method']}")
            
            return True
        except Exception as e:
            print(f"❌ Gemini forecasting test failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    forecaster = GeminiBottleneckForecaster()
    forecaster.test_gemini_forecasting()