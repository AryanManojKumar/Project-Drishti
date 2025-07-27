#!/usr/bin/env python3
"""
Admin Panel for Video Anomaly Detection System
Receives analysis summaries and provides volunteer management interface
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin_panel_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
incidents = []
volunteers = []
recent_anomalies = {}  # Track recent anomalies to prevent duplicates
system_status = {
    "monitoring_active": False,
    "total_incidents": 0,
    "active_incidents": 0,
    "resolved_incidents": 0,
    "volunteers_available": 0,
    "volunteers_assigned": 0,
    "last_update": datetime.now().isoformat()
}

# Mock volunteer data for UI demonstration
mock_volunteers = [
    {"id": 1, "name": "John Smith", "role": "Security", "status": "available", "location": "Main Gate", "skills": ["crowd_control", "security"]},
    {"id": 2, "name": "Sarah Johnson", "role": "Medical", "status": "assigned", "location": "Stage Area", "skills": ["medical_emergency", "first_aid"]},
    {"id": 3, "name": "Mike Wilson", "role": "Technical", "status": "available", "location": "Control Room", "skills": ["equipment_failure", "technical"]},
    {"id": 4, "name": "Emma Davis", "role": "Coordinator", "status": "busy", "location": "VIP Section", "skills": ["crowd_control", "coordination"]},
    {"id": 5, "name": "Alex Brown", "role": "Security", "status": "available", "location": "Parking", "skills": ["security_threat", "vehicle_incident"]},
    {"id": 6, "name": "Lisa Garcia", "role": "Medical", "status": "available", "location": "First Aid Station", "skills": ["medical_emergency", "evacuation"]},
    {"id": 7, "name": "David Lee", "role": "Fire Safety", "status": "assigned", "location": "Backstage", "skills": ["fire_hazard", "evacuation"]},
    {"id": 8, "name": "Rachel White", "role": "Coordinator", "status": "available", "location": "Information Desk", "skills": ["crowd_control", "coordination"]}
]

volunteers = mock_volunteers.copy()

@app.route('/')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/receive-incident', methods=['POST'])
def receive_incident():
    """Receive incident data from video analysis system with duplicate detection"""
    try:
        incident_data = request.get_json()
        if incident_data:
            # Check for duplicate anomalies (5-minute window)
            if is_duplicate_anomaly(incident_data):
                return jsonify({"status": "duplicate", "message": "Duplicate anomaly ignored"})
            
            # Process and enhance incident data for admin view
            enhanced_incident = process_incident_for_admin(incident_data)
            incidents.append(enhanced_incident)
            
            # Track this anomaly to prevent duplicates
            track_anomaly(incident_data)
            
            # Update system status
            update_system_status()
            
            # Broadcast to admin dashboard
            socketio.emit('new_incident', enhanced_incident)
            socketio.emit('status_update', system_status)
            
            return jsonify({"status": "success", "message": "Incident received"})
        return jsonify({"status": "error", "message": "No incident data provided"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents"""
    return jsonify({"incidents": incidents[-50:]})  # Return last 50 incidents

@app.route('/api/volunteers', methods=['GET'])
def get_volunteers():
    """Get all volunteers"""
    return jsonify({"volunteers": volunteers})

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    """Get system status"""
    return jsonify(system_status)

@app.route('/api/assign-volunteer', methods=['POST'])
def assign_volunteer():
    """Assign volunteer to incident (placeholder for future implementation)"""
    try:
        data = request.get_json()
        volunteer_id = data.get('volunteer_id')
        incident_id = data.get('incident_id')
        
        # Find volunteer and update status
        for volunteer in volunteers:
            if volunteer['id'] == volunteer_id:
                volunteer['status'] = 'assigned'
                volunteer['assigned_incident'] = incident_id
                break
        
        # Find incident and update status
        for incident in incidents:
            if incident['id'] == incident_id:
                incident['status'] = 'assigned'
                incident['assigned_volunteer'] = volunteer_id
                break
        
        update_system_status()
        socketio.emit('volunteer_assigned', {"volunteer_id": volunteer_id, "incident_id": incident_id})
        socketio.emit('status_update', system_status)
        
        return jsonify({"status": "success", "message": "Volunteer assigned"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/resolve-incident', methods=['POST'])
def resolve_incident():
    """Mark incident as resolved and free up assigned volunteers"""
    try:
        data = request.get_json()
        incident_id = data.get('incident_id')
        
        # Find and resolve incident
        for incident in incidents:
            if incident['id'] == incident_id:
                incident['status'] = 'resolved'
                incident['resolved_at'] = datetime.now().isoformat()
                
                # Free up assigned volunteers
                if 'assigned_volunteers' in incident and incident['assigned_volunteers']:
                    for vol_id in incident['assigned_volunteers']:
                        for volunteer in volunteers:
                            if volunteer['id'] == vol_id:
                                volunteer['status'] = 'available'
                                volunteer['assigned_incident'] = None
                                break
                break
        
        update_system_status()
        socketio.emit('incident_resolved', {"incident_id": incident_id})
        socketio.emit('volunteer_status_updated', {"message": "Volunteers freed from resolved incident"})
        socketio.emit('status_update', system_status)
        
        return jsonify({"status": "success", "message": "Incident resolved and volunteers freed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def process_incident_for_admin(incident_data: Dict) -> Dict:
    """Process incident data for admin dashboard with comprehensive analysis integration"""
    enhanced_incident = {
        "id": f"INC_{int(time.time())}",
        "timestamp": incident_data.get('timestamp', datetime.now().isoformat()),
        "category": incident_data.get('category', 'Unknown'),
        "severity": incident_data.get('severity', {}),
        "location": incident_data.get('location', 'Unknown location'),
        "confidence": incident_data.get('confidence', '0%'),
        "status": "new",
        "priority": get_priority_level(incident_data.get('severity', {}).get('level', 1)),
        
        # Complete analysis summary for admin
        "analysis_summary": {
            "situation_overview": incident_data.get('summary', {}).get('situation_overview', 'No description available'),
            "severity_assessment": incident_data.get('summary', {}).get('severity_assessment', 'Assessment pending'),
            "hazard_analysis": incident_data.get('summary', {}).get('hazard_analysis', 'Analysis pending'),
            "immediate_actions": incident_data.get('summary', {}).get('immediate_actions', []),
            "equipment_required": incident_data.get('summary', {}).get('equipment_required', []),
            "de_escalation_strategy": incident_data.get('summary', {}).get('de_escalation_strategy', 'No strategy provided'),
            "resolution_method": incident_data.get('summary', {}).get('resolution_method', 'No method provided')
        },
        
        # Admin-focused summary with key insights
        "admin_insights": {
            "critical_points": extract_critical_points(incident_data),
            "risk_assessment": create_risk_assessment(incident_data),
            "resource_allocation": create_resource_plan(incident_data),
            "response_priorities": determine_response_priorities(incident_data),
            "escalation_triggers": identify_escalation_triggers(incident_data)
        },
        
        # Volunteer assignment info
        "volunteer_requirements": determine_volunteer_requirements(incident_data),
        "estimated_response_time": calculate_response_time(incident_data.get('severity', {}).get('level', 1)),
        "assigned_volunteers": [],
        "created_at": datetime.now().isoformat(),
        
        # Raw data for reference
        "raw_analysis": incident_data
    }
    
    return enhanced_incident

def extract_key_concerns(incident_data: Dict) -> List[str]:
    """Extract key concerns for admin attention"""
    concerns = []
    
    severity_level = incident_data.get('severity', {}).get('level', 1)
    category = incident_data.get('category', '').lower()
    
    if severity_level >= 4:
        concerns.append("🚨 CRITICAL: Immediate response required")
    
    if severity_level >= 3:
        concerns.append("⚠️ HIGH PRIORITY: Urgent attention needed")
    
    if 'crowd' in category:
        concerns.append("👥 Crowd management issue - potential for escalation")
    
    if 'medical' in category:
        concerns.append("🏥 Medical response required - dispatch first aid")
    
    if 'security' in category:
        concerns.append("🔒 Security threat - alert security team")
    
    if 'fire' in category:
        concerns.append("🔥 Fire hazard - contact fire safety team")
    
    if 'evacuation' in category:
        concerns.append("🚪 Evacuation may be required - prepare emergency protocols")
    
    return concerns if concerns else ["ℹ️ Standard monitoring - assess situation"]

def determine_volunteer_requirements(incident_data: Dict) -> Dict:
    """Determine volunteer requirements based on incident"""
    category = incident_data.get('category', '').lower()
    severity = incident_data.get('severity', {}).get('level', 1)
    
    requirements = {
        "count": 1,
        "skills": [],
        "roles": [],
        "urgency": "normal"
    }
    
    if severity >= 4:
        requirements["count"] = 3
        requirements["urgency"] = "critical"
    elif severity >= 3:
        requirements["count"] = 2
        requirements["urgency"] = "high"
    
    if 'crowd' in category:
        requirements["skills"].extend(["crowd_control", "coordination"])
        requirements["roles"].extend(["Security", "Coordinator"])
    elif 'medical' in category:
        requirements["skills"].extend(["medical_emergency", "first_aid"])
        requirements["roles"].extend(["Medical"])
    elif 'security' in category:
        requirements["skills"].extend(["security_threat", "security"])
        requirements["roles"].extend(["Security"])
    elif 'fire' in category:
        requirements["skills"].extend(["fire_hazard", "evacuation"])
        requirements["roles"].extend(["Fire Safety"])
    elif 'technical' in category or 'equipment' in category:
        requirements["skills"].extend(["equipment_failure", "technical"])
        requirements["roles"].extend(["Technical"])
    
    return requirements

def calculate_response_time(severity_level: int) -> str:
    """Calculate estimated response time based on severity"""
    if severity_level >= 5:
        return "Immediate (0-2 minutes)"
    elif severity_level >= 4:
        return "Critical (2-5 minutes)"
    elif severity_level >= 3:
        return "High (5-10 minutes)"
    elif severity_level >= 2:
        return "Medium (10-15 minutes)"
    else:
        return "Low (15-30 minutes)"

def get_priority_level(severity_level: int) -> str:
    """Get priority level for incident"""
    if severity_level >= 5:
        return "EMERGENCY"
    elif severity_level >= 4:
        return "CRITICAL"
    elif severity_level >= 3:
        return "HIGH"
    elif severity_level >= 2:
        return "MEDIUM"
    else:
        return "LOW"

def extract_critical_points(incident_data: Dict) -> List[str]:
    """Extract critical points for admin decision making"""
    critical_points = []
    
    # Add situation overview as first critical point
    situation = incident_data.get('summary', {}).get('situation_overview', '')
    if situation:
        critical_points.append(f"📋 Situation: {situation}")
    
    # Add severity assessment
    severity_assessment = incident_data.get('summary', {}).get('severity_assessment', '')
    if severity_assessment:
        critical_points.append(f"⚠️ Risk Level: {severity_assessment}")
    
    # Add hazard analysis
    hazard_analysis = incident_data.get('summary', {}).get('hazard_analysis', '')
    if hazard_analysis:
        critical_points.append(f"🔍 Hazards: {hazard_analysis}")
    
    # Add location and confidence
    location = incident_data.get('location', '')
    confidence = incident_data.get('confidence', '')
    if location and confidence:
        critical_points.append(f"📍 Location: {location} (Confidence: {confidence})")
    
    return critical_points

def create_risk_assessment(incident_data: Dict) -> Dict:
    """Create comprehensive risk assessment"""
    severity_level = incident_data.get('severity', {}).get('level', 1)
    category = incident_data.get('category', '').lower()
    
    risk_factors = []
    mitigation_steps = []
    
    # Assess risk factors based on category and severity
    if severity_level >= 4:
        risk_factors.append("High severity incident requiring immediate response")
        mitigation_steps.append("Deploy emergency response team immediately")
    
    if 'crowd' in category:
        risk_factors.append("Crowd dynamics - potential for rapid escalation")
        mitigation_steps.append("Implement crowd control measures")
    
    if 'medical' in category:
        risk_factors.append("Medical emergency - time-critical response needed")
        mitigation_steps.append("Dispatch medical personnel and equipment")
    
    if 'security' in category:
        risk_factors.append("Security threat - potential danger to attendees")
        mitigation_steps.append("Alert security team and law enforcement if needed")
    
    return {
        "risk_level": get_priority_level(severity_level),
        "risk_factors": risk_factors,
        "mitigation_steps": mitigation_steps,
        "escalation_potential": "High" if severity_level >= 3 else "Medium" if severity_level >= 2 else "Low"
    }

def create_resource_plan(incident_data: Dict) -> Dict:
    """Create resource allocation plan"""
    equipment_required = incident_data.get('summary', {}).get('equipment_required', [])
    immediate_actions = incident_data.get('summary', {}).get('immediate_actions', [])
    severity_level = incident_data.get('severity', {}).get('level', 1)
    
    return {
        "equipment_needed": equipment_required[:5],  # Top 5 equipment items
        "personnel_count": 3 if severity_level >= 4 else 2 if severity_level >= 3 else 1,
        "estimated_cost": "High" if severity_level >= 4 else "Medium" if severity_level >= 3 else "Low",
        "deployment_time": calculate_response_time(severity_level),
        "priority_actions": immediate_actions[:3]  # Top 3 priority actions
    }

def determine_response_priorities(incident_data: Dict) -> List[Dict]:
    """Determine response priorities with specific assignments"""
    immediate_actions = incident_data.get('summary', {}).get('immediate_actions', [])
    severity_level = incident_data.get('severity', {}).get('level', 1)
    category = incident_data.get('category', '').lower()
    
    priorities = []
    
    # Priority 1: Immediate safety
    if immediate_actions:
        priorities.append({
            "priority": 1,
            "action": immediate_actions[0] if immediate_actions else "Assess situation",
            "urgency": "IMMEDIATE" if severity_level >= 4 else "HIGH",
            "assigned_to": "First responder team"
        })
    
    # Priority 2: Crowd management (if applicable)
    if 'crowd' in category:
        priorities.append({
            "priority": 2,
            "action": "Implement crowd control measures",
            "urgency": "HIGH",
            "assigned_to": "Security team"
        })
    
    # Priority 3: Medical response (if applicable)
    if 'medical' in category:
        priorities.append({
            "priority": 2,  # Same priority as crowd for medical
            "action": "Provide medical assistance",
            "urgency": "CRITICAL",
            "assigned_to": "Medical team"
        })
    
    # Priority 3: Communication
    priorities.append({
        "priority": 3,
        "action": "Notify relevant stakeholders and update status",
        "urgency": "MEDIUM",
        "assigned_to": "Coordination team"
    })
    
    return priorities

def identify_escalation_triggers(incident_data: Dict) -> List[str]:
    """Identify conditions that would trigger escalation"""
    triggers = []
    severity_level = incident_data.get('severity', {}).get('level', 1)
    category = incident_data.get('category', '').lower()
    
    # General escalation triggers
    if severity_level >= 3:
        triggers.append("If situation worsens or spreads to other areas")
        triggers.append("If initial response is ineffective within 10 minutes")
    
    # Category-specific triggers
    if 'crowd' in category:
        triggers.append("If crowd size increases beyond manageable levels")
        triggers.append("If panic behavior is observed")
    
    if 'medical' in category:
        triggers.append("If additional casualties are reported")
        triggers.append("If advanced medical intervention is required")
    
    if 'security' in category:
        triggers.append("If threat level increases or spreads")
        triggers.append("If law enforcement assistance is required")
    
    # Always include these general triggers
    triggers.extend([
        "If media attention increases significantly",
        "If incident affects VIP areas or critical infrastructure",
        "If evacuation becomes necessary"
    ])
    
    return triggers

def is_duplicate_anomaly(incident_data: Dict) -> bool:
    """Check if this anomaly is a duplicate within 5 minutes"""
    global recent_anomalies
    
    # Create a unique key for this anomaly type and location
    category = incident_data.get('category', 'unknown')
    location = incident_data.get('location', 'unknown')
    anomaly_key = f"{category}_{location}".lower().replace(' ', '_')
    
    current_time = datetime.now()
    
    # Clean up old entries (older than 5 minutes)
    cutoff_time = current_time - timedelta(minutes=5)
    recent_anomalies = {k: v for k, v in recent_anomalies.items() if v > cutoff_time}
    
    # Check if this anomaly type/location was seen recently
    if anomaly_key in recent_anomalies:
        return True
    
    return False

def track_anomaly(incident_data: Dict):
    """Track this anomaly to prevent duplicates"""
    global recent_anomalies
    
    category = incident_data.get('category', 'unknown')
    location = incident_data.get('location', 'unknown')
    anomaly_key = f"{category}_{location}".lower().replace(' ', '_')
    
    recent_anomalies[anomaly_key] = datetime.now()

@app.route('/api/assign-multiple-volunteers', methods=['POST'])
def assign_multiple_volunteers():
    """Assign multiple volunteers to an incident"""
    try:
        data = request.get_json()
        volunteer_ids = data.get('volunteer_ids', [])
        incident_id = data.get('incident_id')
        
        if not volunteer_ids or not incident_id:
            return jsonify({"status": "error", "message": "Missing volunteer IDs or incident ID"}), 400
        
        assigned_volunteers = []
        
        # Update volunteer statuses
        for vol_id in volunteer_ids:
            for volunteer in volunteers:
                if volunteer['id'] == vol_id and volunteer['status'] == 'available':
                    volunteer['status'] = 'assigned'
                    volunteer['assigned_incident'] = incident_id
                    assigned_volunteers.append(vol_id)
                    break
        
        # Update incident with assigned volunteers
        for incident in incidents:
            if incident['id'] == incident_id:
                if 'assigned_volunteers' not in incident:
                    incident['assigned_volunteers'] = []
                incident['assigned_volunteers'].extend(assigned_volunteers)
                incident['status'] = 'assigned'
                break
        
        update_system_status()
        socketio.emit('volunteers_assigned', {
            "volunteer_ids": assigned_volunteers, 
            "incident_id": incident_id,
            "count": len(assigned_volunteers)
        })
        socketio.emit('status_update', system_status)
        
        return jsonify({
            "status": "success", 
            "message": f"{len(assigned_volunteers)} volunteers assigned",
            "assigned_count": len(assigned_volunteers)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-risk-categories', methods=['GET'])
def get_risk_categories():
    """Get incidents organized by risk categories"""
    try:
        risk_categories = {
            "EMERGENCY": [],
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        active_incidents = [i for i in incidents if i['status'] in ['new', 'assigned']]
        
        for incident in active_incidents:
            priority = incident.get('priority', 'LOW')
            if priority in risk_categories:
                risk_categories[priority].append(incident)
        
        return jsonify({"risk_categories": risk_categories})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def update_system_status():
    """Update system status"""
    global system_status
    
    active_incidents = len([i for i in incidents if i['status'] in ['new', 'assigned']])
    resolved_incidents = len([i for i in incidents if i['status'] == 'resolved'])
    available_volunteers = len([v for v in volunteers if v['status'] == 'available'])
    assigned_volunteers = len([v for v in volunteers if v['status'] == 'assigned'])
    
    system_status.update({
        "total_incidents": len(incidents),
        "active_incidents": active_incidents,
        "resolved_incidents": resolved_incidents,
        "volunteers_available": available_volunteers,
        "volunteers_assigned": assigned_volunteers,
        "last_update": datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    print('Admin connected to dashboard')
    emit('status', {'message': 'Connected to admin dashboard'})
    emit('status_update', system_status)

@socketio.on('disconnect')
def handle_disconnect():
    print('Admin disconnected from dashboard')

if __name__ == '__main__':
    print("🔧 Starting Admin Panel...")
    print("   Dashboard: http://localhost:5001")
    print("   Features:")
    print("   • Real-time incident monitoring")
    print("   • Volunteer management")
    print("   • Situation analysis")
    print("   • Resource allocation")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)