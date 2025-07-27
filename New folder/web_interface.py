from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
from video_anomaly_detector import VideoAnomalyDetector
from config import Config
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
socketio = SocketIO(app, cors_allowed_origins="*")

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global detector instance
detector = None
monitoring_thread = None

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    global detector, monitoring_thread
    
    try:
        if detector is None:
            detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
        
        if monitoring_thread is None or not monitoring_thread.is_alive():
            monitoring_thread = threading.Thread(
                target=run_monitoring,
                daemon=True
            )
            monitoring_thread.start()
            
        return jsonify({"status": "success", "message": "Monitoring started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring():
    global detector
    
    if detector:
        detector.is_monitoring = False
        
    return jsonify({"status": "success", "message": "Monitoring stopped"})

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    if os.path.exists('anomaly_alerts.json'):
        with open('anomaly_alerts.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"all_reports": []})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    global detector
    
    if detector:
        stats = detector.get_statistics()
        return jsonify(stats)
    return jsonify({"total_anomalies": 0})

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    global detector, monitoring_thread
    
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            if detector is None:
                detector = VideoAnomalyDetector(Config.GEMINI_API_KEY)
            
            # Stop current monitoring if running
            if detector:
                detector.is_monitoring = False
            
            # Start monitoring with uploaded video
            if monitoring_thread is None or not monitoring_thread.is_alive():
                monitoring_thread = threading.Thread(
                    target=run_video_monitoring,
                    args=(filepath,),
                    daemon=True
                )
                monitoring_thread.start()
                
            return jsonify({
                "status": "success", 
                "message": f"Video uploaded and monitoring started: {filename}",
                "filename": filename
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "Invalid file type"}), 400

# Global logs storage
analysis_logs = []

@app.route('/api/logs', methods=['GET'])
def get_logs():
    global analysis_logs
    # Also try to read from file if available
    try:
        if os.path.exists('analysis_logs.json'):
            with open('analysis_logs.json', 'r') as f:
                latest_log = json.load(f)
                # Add to logs if not already present
                if latest_log not in analysis_logs:
                    analysis_logs.append(latest_log)
    except Exception as e:
        print(f"Error reading logs file: {e}")
    
    return jsonify({"logs": analysis_logs[-50:]})  # Return last 50 logs

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    global analysis_logs
    analysis_logs = []
    # Also clear the logs file
    try:
        if os.path.exists('analysis_logs.json'):
            os.remove('analysis_logs.json')
    except Exception as e:
        print(f"Error clearing logs file: {e}")
    return jsonify({"status": "success", "message": "Logs cleared"})

def run_monitoring():
    global detector
    if detector:
        try:
            detector.start_live_monitoring(0)
        except Exception as e:
            print(f"Monitoring error: {e}")

def run_video_monitoring(video_path):
    global detector
    if detector:
        try:
            print(f"🎬 Starting video analysis: {video_path}")
            detector.start_live_monitoring(video_path)
        except Exception as e:
            print(f"Video monitoring error: {e}")

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'message': 'Connected to anomaly detection system'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# WebSocket event for real-time anomaly alerts
def send_anomaly_alert(alert_data):
    socketio.emit('anomaly_alert', alert_data)

# WebSocket event for real-time analysis logs
def send_analysis_log(log_data):
    global analysis_logs
    analysis_logs.append(log_data)
    # Keep only last 100 logs in memory
    if len(analysis_logs) > 100:
        analysis_logs = analysis_logs[-100:]
    socketio.emit('analysis_log', log_data)

@app.route('/api/send-log', methods=['POST'])
def receive_log():
    """Receive log data from video detector and broadcast via WebSocket"""
    try:
        log_data = request.get_json()
        if log_data:
            send_analysis_log(log_data)
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No log data provided"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)