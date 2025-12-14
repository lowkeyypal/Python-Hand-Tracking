from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # For local development
    # print("⭕❌ Pointing Tic-Tac-Toe Started!")
    # print("🌐 Visit http://localhost:5000")
    # print("💡 Press Ctrl+C to stop")
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
