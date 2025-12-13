# Hand Gesture Tic-Tac-Toe

A real-time hand tracking Tic-Tac-Toe game where you play against an AI using hand gestures captured through your webcam.

## Features

- ☝️ **Finger Gesture Control**: Move cursor with index finger, click by pinching
- 🤖 **AI Opponent**: Play against AI with 3 difficulty levels (Easy, Medium, Hard)
- ⭕❌ **Symbol Choice**: Choose to play as X or O
- 📊 **Score Tracking**: Keep track of wins, losses, and draws
- ↩️ **Undo Move**: Take back your last move
- 📱 **Responsive Design**: Works on various screen sizes

## Directory Structure

```
tic-tac-toe-hand-tracking/
├── app.py                      # Flask server
├── requirements.txt            # Python dependencies
├── static/
│   ├── css/
│   │   └── styles.css         # All styling
│   └── js/
│       ├── game.js            # Game logic & AI
│       ├── handTracking.js    # Hand detection
│       └── ui.js              # UI updates
```

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser**:
   Navigate to `http://localhost:5000`

## How to Play

### Hand Gestures
- **Move**: Point your index finger to control the cursor
- **Click**: Pinch your thumb and index finger together

### Game Controls
- **Difficulty**: Choose Easy, Medium, or Hard AI difficulty
- **Symbol**: Select X or O as your playing symbol
- **New Game**: Start a fresh game
- **Undo**: Take back your last move

### Rules
- Get 3 symbols in a row (horizontal, vertical, or diagonal) to win
- AI automatically plays after your move
- Game auto-restarts after 2 seconds when finished

## Technical Details

### Technologies Used
- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Hand Tracking**: MediaPipe Hands
- **AI**: Minimax algorithm with alpha-beta pruning

### File Descriptions

- **app.py**: Flask server setup and routing
- **index.html**: Main HTML structure and layout
- **styles.css**: All styling including responsive design
- **game.js**: Game logic, AI implementation (minimax), win detection
- **handTracking.js**: MediaPipe integration, gesture recognition
- **ui.js**: DOM manipulation, event handlers, display updates

## Browser Compatibility

Works best in:
- Chrome (Recommended)
- Edge
- Firefox
- Safari (may require camera permissions)

## Troubleshooting

**Camera not working?**
- Grant camera permissions in your browser
- Ensure no other application is using the camera
- Try refreshing the page

**Hand not detected?**
- Ensure good lighting
- Keep hand within camera frame
- Try different hand positions

## License

Open source - feel free to modify and use!
