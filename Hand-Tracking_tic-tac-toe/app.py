from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML Template with Tic-Tac-Toe Game
FRONTEND_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hand Gesture Tic-Tac-Toe</title>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            overflow: hidden;
            height: 100vh;
        }

        .main-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            height: 100vh;
            position: relative;
        }

        .game-panel {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }

        # .left-panel {
        #     position: fixed;
        #     bottom: 20px;
        #     right: 20px;
        #     width: 320px;
        #     z-index: 1000;
        # }

        .video-container {
            position: relative;
            background: rgba(0,0,0,0.5);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            border: 2px solid rgba(255,255,255,0.2);
        }

        video { display: none; }
        
        canvas { 
            transform: scaleX(-1); 
            width: 100%; 
            height: auto;
            display: block;
            max-height: 240px;
        }

        .hud { 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            background: rgba(0,0,0,0.8); 
            padding: 10px 15px; 
            border-radius: 10px;
            backdrop-filter: blur(10px);
            font-size: 12px;
        }

        .hud-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 11px;
        }

        .hud-item:last-child { margin-bottom: 0; }

        .hud-label { opacity: 0.7; margin-right: 15px; }

        .hud-value { 
            font-weight: bold; 
            color: #00ff00;
        }

        .state-hover { color: #ffd700 !important; }
        .state-click { color: #00ff00 !important; }

        .cursor-indicator {
            position: fixed;
            width: 40px;
            height: 40px;
            border: 3px solid #00ff00;
            border-radius: 50%;
            pointer-events: none;
            transition: all 0.05s;
            box-shadow: 0 0 20px #00ff00;
            z-index: 10000;
            display: none;
        }

        .cursor-indicator.clicking {
            width: 30px;
            height: 30px;
            background: rgba(0,255,0,0.3);
        }

        .game-panel {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .game-status {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }

        .status-text {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .score-board {
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
        }

        .score-item {
            text-align: center;
        }

        .score-label {
            font-size: 0.9em;
            opacity: 0.7;
            margin-bottom: 5px;
        }

        .score-value {
            font-size: 2em;
            font-weight: bold;
        }

        .game-board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
            aspect-ratio: 1;
        }

        .cell {
            background: rgba(255,255,255,0.2);
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }

        .cell:hover:not(.taken) {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(255,255,255,0.3);
        }

        .cell.taken {
            cursor: not-allowed;
        }

        .cell.player-x {
            color: #00ff00;
            text-shadow: 0 0 20px #00ff00;
        }

        .cell.player-o {
            color: #ff6b6b;
            text-shadow: 0 0 20px #ff6b6b;
        }

        .cell.winner {
            background: rgba(255,215,0,0.3);
            animation: winner-pulse 1s infinite;
        }

        @keyframes winner-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .btn {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .btn-secondary {
            background: rgba(255,255,255,0.2);
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        .difficulty-selector {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .difficulty-btn {
            flex: 1;
            padding: 10px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            cursor: pointer;
            transition: all 0.3s;
        }

        .difficulty-btn.active {
            background: rgba(255,255,255,0.3);
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0,255,0,0.5);
        }

        .instructions {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
            font-size: 11px;
        }

        .instructions h3 {
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .instructions ul {
            list-style: none;
            padding: 0;
        }

        .instructions li {
            padding: 4px 0;
            font-size: 0.85em;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .instructions li:last-child {
            border-bottom: none;
        }

        @media (max-width: 1200px) {
            .game-panel {
                max-width: 90%;
            }
            
            .left-panel {
                width: 280px;
                bottom: 10px;
                right: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="game-panel">
            <h1>🎮 Tic-Tac-Toe vs AI</h1>

            <div class="game-board" id="gameBoard">
                <div class="cell" data-index="0"></div>
                <div class="cell" data-index="1"></div>
                <div class="cell" data-index="2"></div>
                <div class="cell" data-index="3"></div>
                <div class="cell" data-index="4"></div>
                <div class="cell" data-index="5"></div>
                <div class="cell" data-index="6"></div>
                <div class="cell" data-index="7"></div>
                <div class="cell" data-index="8"></div>
            </div>

            <div class="difficulty-selector">
                <button class="difficulty-btn active" data-difficulty="easy">😊 Easy</button>
                <button class="difficulty-btn" data-difficulty="medium">🤔 Medium</button>
                <button class="difficulty-btn" data-difficulty="hard">😈 Hard</button>
            </div>

            <div class="controls">
                <button class="btn btn-primary" id="newGameBtn">🔄 New Game</button>
                <button class="btn btn-secondary" id="undoBtn">↩️ Undo</button>
            </div>
        </div>
    </div>

    <div class="left-panel">
                <video id="input_video"></video>
                <canvas id="output_canvas" width="640" height="480"></canvas>
                <div class="cursor-indicator" id="cursorIndicator"></div>
                
                <div class="hud">
                    <div class="hud-item">
                        <span class="hud-label">State:</span>
                        <span class="hud-value state-hover" id="state">Hover</span>
                    </div>
                    <div class="hud-item">
                        <span class="hud-label">FPS:</span>
                        <span class="hud-value" id="fps">0</span>
                    </div>
                    <div class="hud-item">
                        <span class="hud-label">Hands:</span>
                        <span class="hud-value" id="handsCount">0</span>
                    </div>
                </div>
            </div>

            <div class="instructions">
                <h3>✋ How to Play</h3>
                <ul>
                    <li>🖐️ <strong>Move:</strong> Use your index finger knuckle to control cursor</li>
                    <li>👌 <strong>Select:</strong> Pinch thumb and index finger to place X</li>
                    <li>🤖 <strong>AI:</strong> Computer plays as O automatically</li>
                    <li>🎯 <strong>Win:</strong> Get 3 in a row (horizontal, vertical, or diagonal)</li>
                    <li>🔄 <strong>Reset:</strong> Click "New Game" or press 'R' key</li>
                </ul>
            </div>
        </div>

        # <div class="left-panel">
        #     <div class="video-container">
        #         <video id="input_video"></video>
        #         <canvas id="output_canvas" width="640" height="480"></canvas>
        #         <div class="cursor-indicator" id="cursorIndicator"></div>
            
            <div class="game-status">
                <div class="status-text" id="statusText">Your Turn (X)</div>
                
                <div class="score-board">
                    <div class="score-item">
                        <div class="score-label">You (X)</div>
                        <div class="score-value" style="color: #00ff00;" id="playerScore">0</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Draws</div>
                        <div class="score-value" style="color: #ffd700;" id="drawScore">0</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">AI (O)</div>
                        <div class="score-value" style="color: #ff6b6b;" id="aiScore">0</div>
                    </div>
                </div>
            </div>

            <div class="game-board" id="gameBoard">
                <div class="cell" data-index="0"></div>
                <div class="cell" data-index="1"></div>
                <div class="cell" data-index="2"></div>
                <div class="cell" data-index="3"></div>
                <div class="cell" data-index="4"></div>
                <div class="cell" data-index="5"></div>
                <div class="cell" data-index="6"></div>
                <div class="cell" data-index="7"></div>
                <div class="cell" data-index="8"></div>
            </div>

            <div class="difficulty-selector">
                <button class="difficulty-btn active" data-difficulty="easy">😊 Easy</button>
                <button class="difficulty-btn" data-difficulty="medium">🤔 Medium</button>
                <button class="difficulty-btn" data-difficulty="hard">😈 Hard</button>
            </div>

            <div class="controls">
                <button class="btn btn-primary" id="newGameBtn">🔄 New Game</button>
                <button class="btn btn-secondary" id="undoBtn">↩️ Undo</button>
            </div>
        </div>
    </div>

    <script>
        // Tic-Tac-Toe Game Logic
        let board = ['', '', '', '', '', '', '', '', ''];
        let currentPlayer = 'X';
        let gameActive = true;
        let difficulty = 'easy';
        let scores = { player: 0, ai: 0, draw: 0 };
        let moveHistory = [];

        const statusText = document.getElementById('statusText');
        const cells = document.querySelectorAll('.cell');
        const newGameBtn = document.getElementById('newGameBtn');
        const undoBtn = document.getElementById('undoBtn');
        const playerScoreEl = document.getElementById('playerScore');
        const aiScoreEl = document.getElementById('aiScore');
        const drawScoreEl = document.getElementById('drawScore');

        const winConditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
            [0, 4, 8], [2, 4, 6]              // Diagonals
        ];

        function checkWinner() {
            for (let condition of winConditions) {
                const [a, b, c] = condition;
                if (board[a] && board[a] === board[b] && board[a] === board[c]) {
                    return { winner: board[a], line: condition };
                }
            }
            if (!board.includes('')) return { winner: 'draw', line: [] };
            return null;
        }

        function updateDisplay() {
            cells.forEach((cell, index) => {
                cell.textContent = board[index];
                cell.className = 'cell';
                if (board[index]) {
                    cell.classList.add('taken');
                    cell.classList.add(board[index] === 'X' ? 'player-x' : 'player-o');
                }
            });
        }

        function updateStatus(message) {
            statusText.textContent = message;
        }

        function makeMove(index) {
            if (!gameActive || board[index] !== '') return false;
            
            moveHistory.push([...board]);
            board[index] = currentPlayer;
            updateDisplay();

            const result = checkWinner();
            if (result) {
                gameActive = false;
                if (result.winner === 'draw') {
                    updateStatus("It's a Draw! 🤝 Restarting in 2s...");
                    scores.draw++;
                    drawScoreEl.textContent = scores.draw;
                } else {
                    updateStatus(result.winner === 'X' ? "You Win! 🎉 Restarting in 2s..." : "AI Wins! 🤖 Restarting in 2s...");
                    if (result.winner === 'X') {
                        scores.player++;
                        playerScoreEl.textContent = scores.player;
                    } else {
                        scores.ai++;
                        aiScoreEl.textContent = scores.ai;
                    }
                    result.line.forEach(i => cells[i].classList.add('winner'));
                }
                
                // Auto-restart after 2 seconds
                setTimeout(() => {
                    resetGame();
                }, 2000);
                
                return true;
            }

            currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
            updateStatus(currentPlayer === 'X' ? "Your Turn (X)" : "AI Thinking... 🤖");
            return true;
        }

        function getAIMove() {
            if (difficulty === 'hard') {
                return getBestMove();
            } else if (difficulty === 'medium') {
                return Math.random() < 0.5 ? getBestMove() : getRandomMove();
            } else {
                return Math.random() < 0.7 ? getRandomMove() : getBestMove();
            }
        }

        function getRandomMove() {
            const available = board.map((cell, i) => cell === '' ? i : null).filter(i => i !== null);
            return available[Math.floor(Math.random() * available.length)];
        }

        function getBestMove() {
            // Check for winning move
            for (let i = 0; i < 9; i++) {
                if (board[i] === '') {
                    board[i] = 'O';
                    if (checkWinner()?.winner === 'O') {
                        board[i] = '';
                        return i;
                    }
                    board[i] = '';
                }
            }

            // Block player's winning move
            for (let i = 0; i < 9; i++) {
                if (board[i] === '') {
                    board[i] = 'X';
                    if (checkWinner()?.winner === 'X') {
                        board[i] = '';
                        return i;
                    }
                    board[i] = '';
                }
            }

            // Take center if available
            if (board[4] === '') return 4;

            // Take corners
            const corners = [0, 2, 6, 8].filter(i => board[i] === '');
            if (corners.length > 0) return corners[Math.floor(Math.random() * corners.length)];

            // Take any available
            return getRandomMove();
        }

        function aiMove() {
            if (!gameActive || currentPlayer !== 'O') return;
            
            setTimeout(() => {
                const move = getAIMove();
                makeMove(move);
                if (gameActive) {
                    currentPlayer = 'X';
                    updateStatus("Your Turn (X)");
                }
            }, 500);
        }

        function handleCellClick(index) {
            if (currentPlayer === 'X' && makeMove(index)) {
                if (gameActive) {
                    currentPlayer = 'O';
                    aiMove();
                }
            }
        }

        function resetGame() {
            board = ['', '', '', '', '', '', '', '', ''];
            currentPlayer = 'X';
            gameActive = true;
            moveHistory = [];
            updateDisplay();
            updateStatus("Your Turn (X)");
            cells.forEach(cell => cell.classList.remove('winner'));
        }

        function undoMove() {
            if (moveHistory.length < 2) return;
            moveHistory.pop(); // Remove AI move
            board = moveHistory.pop(); // Remove player move
            currentPlayer = 'X';
            gameActive = true;
            updateDisplay();
            updateStatus("Your Turn (X)");
            cells.forEach(cell => cell.classList.remove('winner'));
        }

        // Event Listeners
        cells.forEach((cell, index) => {
            cell.addEventListener('click', () => handleCellClick(index));
        });

        newGameBtn.addEventListener('click', resetGame);
        undoBtn.addEventListener('click', undoMove);

        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                difficulty = btn.dataset.difficulty;
                resetGame();
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') resetGame();
            if (e.key === 'Escape') resetGame();
        });

        // Hand Tracking
        const videoElement = document.getElementById('input_video');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d');
        const stateSpan = document.getElementById('state');
        const fpsSpan = document.getElementById('fps');
        const handsCountSpan = document.getElementById('handsCount');
        const cursorIndicator = document.getElementById('cursorIndicator');

        const CLICK_THRESHOLD = 0.25;
        const SMOOTHING = 0.2;
        
        let prevX = 0.5, prevY = 0.5;
        let isClicking = false;
        let lastTime = Date.now();
        let hoveredCell = null;

        function mapRange(value, inMin, inMax, outMin, outMax) {
            return Math.max(outMin, Math.min(outMax, 
                (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
            ));
        }

        function distance(p1, p2) {
            return Math.hypot(p1.x - p2.x, p1.y - p2.y);
        }

        function lerp(start, end, amt) {
            return (1 - amt) * start + amt * end;
        }

        function updateCursor(x, y) {
            const cursorX = x * window.innerWidth;
            const cursorY = y * window.innerHeight;
            
            // Make sure cursor is visible
            cursorIndicator.style.display = 'block';
            cursorIndicator.style.left = (cursorX - 20) + 'px';
            cursorIndicator.style.top = (cursorY - 20) + 'px';

            let found = false;
            
            // Check cells
            cells.forEach(cell => {
                const rect = cell.getBoundingClientRect();
                if (cursorX >= rect.left && cursorX <= rect.right &&
                    cursorY >= rect.top && cursorY <= rect.bottom) {
                    if (hoveredCell !== cell && !cell.classList.contains('taken')) {
                        if (hoveredCell && hoveredCell.classList.contains('cell')) {
                            hoveredCell.style.transform = 'scale(1)';
                            hoveredCell.style.boxShadow = '';
                        }
                        cell.style.transform = 'scale(1.1)';
                        cell.style.boxShadow = '0 5px 25px rgba(0,255,0,0.5)';
                        hoveredCell = cell;
                    }
                    found = true;
                } else if (cell === hoveredCell) {
                    cell.style.transform = 'scale(1)';
                    cell.style.boxShadow = '';
                }
            });

            // Check all buttons (difficulty, new game, undo)
            const allButtons = document.querySelectorAll('.difficulty-btn, .btn');
            allButtons.forEach(button => {
                const rect = button.getBoundingClientRect();
                if (cursorX >= rect.left && cursorX <= rect.right &&
                    cursorY >= rect.top && cursorY <= rect.bottom) {
                    if (hoveredCell !== button) {
                        if (hoveredCell && !hoveredCell.classList.contains('cell')) {
                            hoveredCell.style.transform = 'scale(1)';
                            hoveredCell.style.boxShadow = '';
                        }
                        button.style.transform = 'scale(1.05)';
                        button.style.boxShadow = '0 5px 20px rgba(0,255,0,0.5)';
                        hoveredCell = button;
                    }
                    found = true;
                } else if (button === hoveredCell) {
                    button.style.transform = 'scale(1)';
                    button.style.boxShadow = '';
                }
            });

            if (!found && hoveredCell) {
                hoveredCell.style.transform = 'scale(1)';
                hoveredCell.style.boxShadow = '';
                hoveredCell = null;
            }
        }

        function onResults(results) {
            const now = Date.now();
            fpsSpan.textContent = Math.round(1000 / (now - lastTime));
            lastTime = now;

            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                handsCountSpan.textContent = results.multiHandLandmarks.length;
                const landmarks = results.multiHandLandmarks[0];
                
                const indexMCP = landmarks[5];
                const indexTip = landmarks[8];
                const thumbTip = landmarks[4];
                const wrist = landmarks[0];

                canvasCtx.beginPath();
                canvasCtx.arc(indexMCP.x * 640, indexMCP.y * 480, 12, 0, 2 * Math.PI);
                canvasCtx.fillStyle = '#00ffff';
                canvasCtx.fill();
                canvasCtx.strokeStyle = '#fff';
                canvasCtx.lineWidth = 2;
                canvasCtx.stroke();

                canvasCtx.beginPath();
                canvasCtx.moveTo(thumbTip.x * 640, thumbTip.y * 480);
                canvasCtx.lineTo(indexTip.x * 640, indexTip.y * 480);
                canvasCtx.strokeStyle = isClicking ? '#00ff00' : '#ffff00';
                canvasCtx.lineWidth = 3;
                canvasCtx.stroke();

                // Movement calculation with proper mirroring for camera flip
                let rawX = indexMCP.x; // Use raw x value
                let rawY = mapRange(indexMCP.y, 0.2, 0.8, 0, 1);

                // Map X from 0-1 range (already flipped by scaleX on canvas)
                rawX = mapRange(rawX, 0.2, 0.8, 0, 1);

                const currX = lerp(prevX, rawX, SMOOTHING);
                const currY = lerp(prevY, rawY, SMOOTHING);
                
                prevX = currX;
                prevY = currY;

                updateCursor(currX, currY);

                const pinchDist = distance(thumbTip, indexTip);
                const handScale = distance(wrist, indexMCP);
                const ratio = pinchDist / handScale;

                if (ratio < CLICK_THRESHOLD) {
                    if (!isClicking) {
                        isClicking = true;
                        stateSpan.textContent = 'CLICK';
                        stateSpan.className = 'hud-value state-click';
                        cursorIndicator.classList.add('clicking');
                        
                        if (hoveredCell) {
                            hoveredCell.click();
                        }
                    }
                } else {
                    if (isClicking) {
                        isClicking = false;
                        stateSpan.textContent = 'Hover';
                        stateSpan.className = 'hud-value state-hover';
                        cursorIndicator.classList.remove('clicking');
                    }
                }
            } else {
                handsCountSpan.textContent = '0';
            }

            canvasCtx.restore();
        }

        const hands = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });
        
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.7,
            minTrackingConfidence: 0.7
        });
        
        hands.onResults(onResults);

        const camera = new Camera(videoElement, {
            onFrame: async () => { await hands.send({image: videoElement}); },
            width: 640,
            height: 480
        });
        
        camera.start();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(FRONTEND_TEMPLATE)

if __name__ == '__main__':
    print("🚀 Hand Gesture Tic-Tac-Toe Started!")
    print("👉 Open http://localhost:5000 in your browser")
    print("✋ Use your hand to play against AI!")
    print("💡 Press Ctrl+C to stop")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)