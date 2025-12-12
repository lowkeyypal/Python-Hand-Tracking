from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("🚀 Hand Gesture Tic-Tac-Toe Started!")
    print("👉 Open http://localhost:5000 in your browser")
    print("✋ Use your hand to play against AI!")
    print("💡 Press Ctrl+C to stop")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
