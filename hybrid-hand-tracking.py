from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Simple in-memory storage (use database in production)
sessions = []
gestures_log = []
stats = {
    'total_sessions': 0,
    'total_gestures_detected': 0,
    'total_tracking_time': 0
}

# HTML Template for the frontend
FRONTEND_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>Hand Tracking Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }

        @media (max-width: 968px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .video-section {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }

        .video-container {
            position: relative;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        #videoElement {
            width: 100%;
            height: auto;
            display: block;
            transform: scaleX(-1);
        }

        #canvasElement {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            transform: scaleX(-1);
        }

        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }

        button {
            padding: 12px 25px;
            font-size: 15px;
            border: none;
            border-radius: 50px;
            background: white;
            color: #667eea;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .stats-panel {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }

        .stats-panel h2 {
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .stat-item {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
        }

        .status {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            margin-top: 15px;
        }

        .gesture-log {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
            margin-top: 20px;
        }

        .gesture-log h2 {
            margin-bottom: 15px;
        }

        .gesture-item {
            background: rgba(255,255,255,0.15);
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .gesture-time {
            font-size: 0.85em;
            opacity: 0.7;
        }

        #sessionTimer {
            font-size: 1.2em;
            font-weight: bold;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👋 Hand Tracking Pro</h1>
        
        <div class="main-grid">
            <div class="video-section">
                <div class="video-container">
                    <video id="videoElement" autoplay playsinline></video>
                    <canvas id="canvasElement"></canvas>
                </div>

                <div class="controls">
                    <button id="startBtn">Start Tracking</button>
                    <button id="stopBtn" disabled>Stop</button>
                    <button id="recordGestureBtn" disabled>Record Gesture</button>
                </div>

                <div class="status" id="status">Click "Start Tracking" to begin</div>
                <div id="sessionTimer"></div>
            </div>

            <div class="stats-panel">
                <h2>📊 Live Stats</h2>
                <div class="stat-item">
                    <div class="stat-label">Hands Detected</div>
                    <div class="stat-value" id="handsCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Gestures Recorded</div>
                    <div class="stat-value" id="gesturesCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Sessions</div>
                    <div class="stat-value" id="totalSessions">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Tracking Time</div>
                    <div class="stat-value" id="trackingTime">0s</div>
                </div>
            </div>
        </div>

        <div class="gesture-log">
            <h2>🖐️ Recent Gestures</h2>
            <div id="gestureList">
                <p style="opacity: 0.6; text-align: center;">No gestures recorded yet</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>

    <script>
        const API_URL = window.location.origin;
        
        const videoElement = document.getElementById('videoElement');
        const canvasElement = document.getElementById('canvasElement');
        const canvasCtx = canvasElement.getContext('2d');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const recordGestureBtn = document.getElementById('recordGestureBtn');
        const statusDiv = document.getElementById('status');

        let camera = null;
        let hands = null;
        let currentSession = null;
        let sessionStartTime = null;
        let timerInterval = null;
        let currentHandLandmarks = null;
        let gesturesRecorded = 0;

        function updateStatus(message) {
            statusDiv.textContent = message;
        }

        function updateTimer() {
            if (sessionStartTime) {
                const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
                document.getElementById('sessionTimer').textContent = `Session Time: ${elapsed}s`;
            }
        }

        async function loadStats() {
            try {
                const response = await fetch(`${API_URL}/api/stats`);
                const data = await response.json();
                document.getElementById('totalSessions').textContent = data.total_sessions;
                document.getElementById('trackingTime').textContent = data.total_tracking_time + 's';
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadGestures() {
            try {
                const response = await fetch(`${API_URL}/api/gestures`);
                const data = await response.json();
                const gestureList = document.getElementById('gestureList');
                
                if (data.gestures.length === 0) {
                    gestureList.innerHTML = '<p style="opacity: 0.6; text-align: center;">No gestures recorded yet</p>';
                } else {
                    gestureList.innerHTML = data.gestures.slice(-10).reverse().map(g => `
                        <div class="gesture-item">
                            <div>
                                <strong>${g.hands_count} hand(s)</strong><br>
                                <span style="font-size: 0.9em; opacity: 0.8;">${g.fingers_up || 'N/A'} fingers</span>
                            </div>
                            <div class="gesture-time">${new Date(g.timestamp).toLocaleTimeString()}</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading gestures:', error);
            }
        }

        function countFingers(landmarks) {
            const tips = [8, 12, 16, 20]; // Index, Middle, Ring, Pinky tips
            const pipJoints = [6, 10, 14, 18];
            let count = 0;

            // Check thumb (different logic)
            if (landmarks[4].x < landmarks[3].x) count++;

            // Check other fingers
            for (let i = 0; i < tips.length; i++) {
                if (landmarks[tips[i]].y < landmarks[pipJoints[i]].y) {
                    count++;
                }
            }
            return count;
        }

        function onResults(results) {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;

            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

            if (results.multiHandLandmarks) {
                currentHandLandmarks = results.multiHandLandmarks;
                
                for (const landmarks of results.multiHandLandmarks) {
                    drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
                        color: '#00FF00',
                        lineWidth: 5
                    });
                    drawLandmarks(canvasCtx, landmarks, {
                        color: '#FF0000',
                        lineWidth: 2,
                        radius: 5
                    });
                }
                
                document.getElementById('handsCount').textContent = results.multiHandLandmarks.length;
                updateStatus(`✅ Tracking ${results.multiHandLandmarks.length} hand(s)`);
            } else {
                currentHandLandmarks = null;
                document.getElementById('handsCount').textContent = 0;
                updateStatus('🔍 No hands detected');
            }

            canvasCtx.restore();
        }

        async function startSession() {
            try {
                const response = await fetch(`${API_URL}/api/session/start`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_agent: navigator.userAgent })
                });
                const data = await response.json();
                currentSession = data.session_id;
                sessionStartTime = Date.now();
                timerInterval = setInterval(updateTimer, 1000);
                return data;
            } catch (error) {
                console.error('Error starting session:', error);
            }
        }

        async function endSession() {
            if (!currentSession) return;
            
            const duration = Math.floor((Date.now() - sessionStartTime) / 1000);
            
            try {
                await fetch(`${API_URL}/api/session/end`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSession,
                        duration: duration
                    })
                });
                
                clearInterval(timerInterval);
                currentSession = null;
                sessionStartTime = null;
                document.getElementById('sessionTimer').textContent = '';
                await loadStats();
            } catch (error) {
                console.error('Error ending session:', error);
            }
        }

        async function recordGesture() {
            if (!currentHandLandmarks || !currentSession) return;

            const fingersUp = currentHandLandmarks.map(h => countFingers(h)).join(', ');
            
            try {
                const response = await fetch(`${API_URL}/api/gesture/record`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSession,
                        hands_count: currentHandLandmarks.length,
                        fingers_up: fingersUp,
                        landmarks: currentHandLandmarks
                    })
                });
                
                gesturesRecorded++;
                document.getElementById('gesturesCount').textContent = gesturesRecorded;
                await loadGestures();
                
                updateStatus('✅ Gesture recorded!');
                setTimeout(() => {
                    if (currentHandLandmarks) {
                        updateStatus(`✅ Tracking ${currentHandLandmarks.length} hand(s)`);
                    }
                }, 1500);
            } catch (error) {
                console.error('Error recording gesture:', error);
            }
        }

        async function startCamera() {
            try {
                updateStatus('📷 Loading camera...');
                startBtn.disabled = true;

                await startSession();

                hands = new Hands({
                    locateFile: (file) => {
                        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                    }
                });

                hands.setOptions({
                    maxNumHands: 2,
                    modelComplexity: 0,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.5
                });

                hands.onResults(onResults);

                camera = new Camera(videoElement, {
                    onFrame: async () => {
                        await hands.send({image: videoElement});
                    },
                    width: 640,
                    height: 480
                });

                await camera.start();
                
                stopBtn.disabled = false;
                recordGestureBtn.disabled = false;
                updateStatus('✅ Camera active - show your hands!');
            } catch (error) {
                console.error('Error starting camera:', error);
                updateStatus('❌ Error: ' + error.message);
                startBtn.disabled = false;
            }
        }

        async function stopCamera() {
            if (camera) {
                camera.stop();
                camera = null;
            }
            if (hands) {
                hands.close();
                hands = null;
            }
            
            await endSession();
            
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            
            startBtn.disabled = false;
            stopBtn.disabled = true;
            recordGestureBtn.disabled = true;
            updateStatus('⏸️ Camera stopped');
            document.getElementById('handsCount').textContent = 0;
        }

        startBtn.addEventListener('click', startCamera);
        stopBtn.addEventListener('click', stopCamera);
        recordGestureBtn.addEventListener('click', recordGesture);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' || e.key === 'Escape') {
                stopCamera();
            }
            if (e.key === 'r' || e.key === 'R') {
                if (!recordGestureBtn.disabled) {
                    recordGesture();
                }
            }
        });

        window.addEventListener('beforeunload', () => {
            stopCamera();
        });

        loadStats();
        loadGestures();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(FRONTEND_TEMPLATE)

@app.route('/api/session/start', methods=['POST'])
def start_session():
    data = request.json
    session_id = f"session_{len(sessions) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    session = {
        'session_id': session_id,
        'start_time': datetime.now().isoformat(),
        'user_agent': data.get('user_agent', 'Unknown'),
        'gestures': []
    }
    
    sessions.append(session)
    stats['total_sessions'] += 1
    
    return jsonify({
        'session_id': session_id,
        'message': 'Session started successfully'
    })

@app.route('/api/session/end', methods=['POST'])
def end_session():
    data = request.json
    session_id = data.get('session_id')
    duration = data.get('duration', 0)
    
    for session in sessions:
        if session['session_id'] == session_id:
            session['end_time'] = datetime.now().isoformat()
            session['duration'] = duration
            stats['total_tracking_time'] += duration
            break
    
    return jsonify({'message': 'Session ended successfully'})

@app.route('/api/gesture/record', methods=['POST'])
def record_gesture():
    data = request.json
    session_id = data.get('session_id')
    
    gesture = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'hands_count': data.get('hands_count', 0),
        'fingers_up': data.get('fingers_up', ''),
        'landmarks': data.get('landmarks', [])
    }
    
    gestures_log.append(gesture)
    stats['total_gestures_detected'] += 1
    
    for session in sessions:
        if session['session_id'] == session_id:
            session['gestures'].append(gesture)
            break
    
    return jsonify({
        'message': 'Gesture recorded successfully',
        'gesture_id': len(gestures_log)
    })

@app.route('/api/gestures', methods=['GET'])
def get_gestures():
    return jsonify({'gestures': gestures_log})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(stats)

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    return jsonify({'sessions': sessions})

if __name__ == '__main__':
    print("🚀 Hand Tracking Pro Server Starting...")
    print("📱 Open http://localhost:5000 in your browser")
    print("💡 Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
