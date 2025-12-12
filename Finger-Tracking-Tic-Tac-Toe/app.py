from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            display: grid;
            grid-template-columns: 340px 480px 340px;
            gap: 25px;
            max-width: 1250px;
            width: 100%;
        }

        /* Common Card Styling */
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        /* Left Column */
        .left-column {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .video-card {
            position: relative;
        }

        .video-container {
            background: #000;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        video {
            display: none;
        }

        canvas {
            width: 100%;
            height: auto;
            display: block;
            transform: scaleX(-1);
        }

        .hud {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 11px;
        }

        .hud-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            gap: 20px;
        }

        .hud-row:last-child {
            margin-bottom: 0;
        }

        .hud-label {
            opacity: 0.7;
        }

        .hud-value {
            font-weight: bold;
            color: #00ff00;
        }

        .state-hover {
            color: #ffd700 !important;
        }

        .state-click {
            color: #00ff00 !important;
        }

        .instructions {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 15px;
        }

        .instructions h3 {
            font-size: 1em;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .instructions ul {
            list-style: none;
            font-size: 0.9em;
            line-height: 1.8;
        }

        .instructions li {
            opacity: 0.95;
        }

        /* Center Column - Game */
        .game-card {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .status-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }

        .status-text {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .scores {
            display: flex;
            justify-content: space-around;
        }

        .score-item {
            text-align: center;
        }

        .score-label {
            font-size: 0.85em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .score-value {
            font-size: 2em;
            font-weight: bold;
        }

        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            width: 100%;
            aspect-ratio: 1;
        }

        .cell {
            background: rgba(255, 255, 255, 0.2);
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4em;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }

        .cell:hover:not(.taken) {
            background: rgba(255, 255, 255, 0.25);
        }

        .cell.taken {
            cursor: not-allowed;
        }

        .cell.x {
            color: #00ff00;
            text-shadow: 0 0 20px #00ff00;
        }

        .cell.o {
            color: #ff6b6b;
            text-shadow: 0 0 20px #ff6b6b;
        }

        .cell.winner {
            background: rgba(255, 215, 0, 0.3);
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% {
                background: rgba(255, 215, 0, 0.3);
            }
            50% {
                background: rgba(255, 215, 0, 0.5);
            }
        }

        /* Right Column */
        .right-column {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .title-card {
            padding: 35px 20px;
            text-align: center;
        }

        .title-emoji {
            font-size: 3.5em;
            display: block;
            margin-bottom: 10px;
        }

        .title-text {
            font-size: 2.5em;
            font-weight: bold;
            line-height: 1.1;
        }

        .control-card h3 {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 12px;
            text-align: center;
        }

        .difficulty-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        .symbol-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .action-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .btn {
            padding: 14px 12px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 0.95em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .btn.active {
            background: rgba(255, 255, 255, 0.3);
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }

        .btn-x.active {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }

        .btn-o.active {
            color: #ff6b6b;
            text-shadow: 0 0 10px #ff6b6b;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            border: none;
        }

        /* Cursor Indicator */
        .cursor {
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

        .cursor.clicking {
            width: 30px;
            height: 30px;
            background: rgba(0, 255, 0, 0.3);
        }

        /* Responsive */
        @media (max-width: 1300px) {
            .container {
                grid-template-columns: 1fr;
                max-width: 500px;
            }

            .right-column {
                order: -1;
            }

            .title-text {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="cursor" id="cursor"></div>

    <div class="container">
        <!-- Left Column -->
        <div class="left-column">
            <div class="card video-card">
                <div class="video-container">
                    <video id="video"></video>
                    <canvas id="canvas" width="640" height="480"></canvas>
                    <div class="hud">
                        <div class="hud-row">
                            <span class="hud-label">State:</span>
                            <span class="hud-value state-hover" id="state">Hover</span>
                        </div>
                        <div class="hud-row">
                            <span class="hud-label">FPS:</span>
                            <span class="hud-value" id="fps">0</span>
                        </div>
                        <div class="hud-row">
                            <span class="hud-label">Hands:</span>
                            <span class="hud-value" id="hands">0</span>
                        </div>
                    </div>
                </div>
                <div class="instructions">
                    <h3>ℹ️ How to Play</h3>
                    <ul>
                        <li>☝️ <strong>Move:</strong> Use index finger to point mouse</li>
                        <li>👌 <strong>Click:</strong> Pinch thumb and index finger to perform mouse click</li>
                        <li>🤖 <strong>AI:</strong> Computer plays opposite</li>
                        <li>😊 <strong>Difficulty:</strong> Easy, Medium, or Hard</li>
                        <li>❌/⭕ <strong>Symbol:</strong> Choose X or O to play</li>
                        <li>🔄 <strong>New Game:</strong> Restart anytime</li>
                        <li>↩️ <strong>Undo:</strong> Take back your last move</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Center Column -->
        <div class="game-card card">
            <div class="status-card">
                <div class="status-text" id="status">Your Turn (X)</div>
                <div class="scores">
                    <div class="score-item">
                        <div class="score-label" id="playerLabel">You (X)</div>
                        <div class="score-value" style="color: #00ff00;" id="playerScore">0</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Draws</div>
                        <div class="score-value" style="color: #ffd700;" id="drawScore">0</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label" id="aiLabel">AI (O)</div>
                        <div class="score-value" style="color: #ff6b6b;" id="aiScore">0</div>
                    </div>
                </div>
            </div>
            <div class="board" id="board">
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
        </div>

        <!-- Right Column -->
        <div class="right-column">
            <div class="card title-card">
                <span class="title-emoji">⭕❌</span>
                <div class="title-text">
                    Tic<br>Tac<br>Toe
                </div>
            </div>

            <div class="card control-card">
                <h3>Choose Difficulty</h3>
                <div class="difficulty-grid">
                    <button class="btn active" data-difficulty="easy">😊 Easy</button>
                    <button class="btn" data-difficulty="medium">🤔 Medium</button>
                    <button class="btn" data-difficulty="hard">😈 Hard</button>
                </div>
            </div>

            <div class="card control-card">
                <h3>Choose Symbol</h3>
                <div class="symbol-grid">
                    <button class="btn btn-x active" data-symbol="X">Play as X</button>
                    <button class="btn btn-o" data-symbol="O">Play as O</button>
                </div>
            </div>

            <div class="card control-card">
                <div class="action-grid">
                    <button class="btn btn-primary" id="newGame">🔄 New Game</button>
                    <button class="btn btn-secondary" id="undo">↩️ Undo</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Game State
        let board = ['', '', '', '', '', '', '', '', ''];
        let currentPlayer = 'X';
        let playerSymbol = 'X';
        let aiSymbol = 'O';
        let gameActive = true;
        let difficulty = 'easy';
        let scores = { player: 0, ai: 0, draw: 0 };
        let moveHistory = [];

        // Elements
        const cells = document.querySelectorAll('.cell');
        const statusEl = document.getElementById('status');
        const playerScoreEl = document.getElementById('playerScore');
        const aiScoreEl = document.getElementById('aiScore');
        const drawScoreEl = document.getElementById('drawScore');
        const playerLabelEl = document.getElementById('playerLabel');
        const aiLabelEl = document.getElementById('aiLabel');

        const winPatterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ];

        // Game Logic
        function checkWinner() {
            for (let pattern of winPatterns) {
                const [a, b, c] = pattern;
                if (board[a] && board[a] === board[b] && board[a] === board[c]) {
                    return { winner: board[a], line: pattern };
                }
            }
            if (!board.includes('')) return { winner: 'draw', line: [] };
            return null;
        }

        function updateDisplay() {
            cells.forEach((cell, i) => {
                cell.textContent = board[i];
                cell.classList.remove('x', 'o', 'taken');
                if (board[i] === 'X') {
                    cell.classList.add('x', 'taken');
                } else if (board[i] === 'O') {
                    cell.classList.add('o', 'taken');
                }
            });
        }

        function updateScores() {
            playerScoreEl.textContent = scores.player;
            aiScoreEl.textContent = scores.ai;
            drawScoreEl.textContent = scores.draw;
            playerLabelEl.textContent = `You (${playerSymbol})`;
            aiLabelEl.textContent = `AI (${aiSymbol})`;
        }

        function makeMove(index) {
            if (!gameActive || board[index] || currentPlayer !== playerSymbol) return;

            moveHistory.push([...board]);
            board[index] = playerSymbol;
            updateDisplay();

            const result = checkWinner();
            if (result) {
                endGame(result);
                return;
            }

            currentPlayer = aiSymbol;
            statusEl.textContent = `AI's Turn (${aiSymbol})`;

            setTimeout(() => {
                aiMove();
            }, 500);
        }

        function aiMove() {
            let move;
            if (difficulty === 'easy') {
                move = randomMove();
            } else if (difficulty === 'medium') {
                move = Math.random() < 0.5 ? bestMove() : randomMove();
            } else {
                move = bestMove();
            }

            if (move !== null) {
                board[move] = aiSymbol;
                updateDisplay();

                const result = checkWinner();
                if (result) {
                    endGame(result);
                } else {
                    currentPlayer = playerSymbol;
                    statusEl.textContent = `Your Turn (${playerSymbol})`;
                }
            }
        }

        function randomMove() {
            const available = board.map((cell, i) => cell === '' ? i : null).filter(i => i !== null);
            return available.length > 0 ? available[Math.floor(Math.random() * available.length)] : null;
        }

        function bestMove() {
            let bestScore = -Infinity;
            let move = null;
            for (let i = 0; i < 9; i++) {
                if (board[i] === '') {
                    board[i] = aiSymbol;
                    let score = minimax(0, false);
                    board[i] = '';
                    if (score > bestScore) {
                        bestScore = score;
                        move = i;
                    }
                }
            }
            return move;
        }

        function minimax(depth, isMaximizing) {
            const result = checkWinner();
            if (result) {
                if (result.winner === aiSymbol) return 10 - depth;
                if (result.winner === playerSymbol) return depth - 10;
                return 0;
            }

            if (isMaximizing) {
                let bestScore = -Infinity;
                for (let i = 0; i < 9; i++) {
                    if (board[i] === '') {
                        board[i] = aiSymbol;
                        let score = minimax(depth + 1, false);
                        board[i] = '';
                        bestScore = Math.max(score, bestScore);
                    }
                }
                return bestScore;
            } else {
                let bestScore = Infinity;
                for (let i = 0; i < 9; i++) {
                    if (board[i] === '') {
                        board[i] = playerSymbol;
                        let score = minimax(depth + 1, true);
                        board[i] = '';
                        bestScore = Math.min(score, bestScore);
                    }
                }
                return bestScore;
            }
        }

        function endGame(result) {
            gameActive = false;

            if (result.winner === playerSymbol) {
                scores.player++;
                statusEl.textContent = '🎉 You Win!';
            } else if (result.winner === aiSymbol) {
                scores.ai++;
                statusEl.textContent = '🤖 AI Wins!';
            } else {
                scores.draw++;
                statusEl.textContent = '🤝 Draw!';
            }

            updateScores();

            if (result.line.length > 0) {
                result.line.forEach(i => cells[i].classList.add('winner'));
            }

            setTimeout(() => resetGame(), 2000);
        }

        function resetGame() {
            board = ['', '', '', '', '', '', '', '', ''];
            currentPlayer = 'X';
            gameActive = true;
            moveHistory = [];
            updateDisplay();
            cells.forEach(cell => cell.classList.remove('winner'));

            if (playerSymbol === 'O') {
                statusEl.textContent = `AI's Turn (${aiSymbol})`;
                setTimeout(() => aiMove(), 500);
            } else {
                statusEl.textContent = `Your Turn (${playerSymbol})`;
            }
        }

        function undoMove() {
            if (moveHistory.length < 1) return;
            board = moveHistory.pop();
            currentPlayer = playerSymbol;
            gameActive = true;
            updateDisplay();
            statusEl.textContent = `Your Turn (${playerSymbol})`;
            cells.forEach(cell => cell.classList.remove('winner'));
        }

        // Event Listeners
        cells.forEach((cell, i) => {
            cell.addEventListener('click', () => makeMove(i));
        });

        document.getElementById('newGame').addEventListener('click', resetGame);
        document.getElementById('undo').addEventListener('click', undoMove);

        document.querySelectorAll('[data-difficulty]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('[data-difficulty]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                difficulty = btn.dataset.difficulty;
                resetGame();
            });
        });

        document.querySelectorAll('[data-symbol]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('[data-symbol]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                playerSymbol = btn.dataset.symbol;
                aiSymbol = playerSymbol === 'X' ? 'O' : 'X';
                scores = { player: 0, ai: 0, draw: 0 };
                updateScores();
                resetGame();
            });
        });

        // Hand Tracking
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const cursorEl = document.getElementById('cursor');
        const stateEl = document.getElementById('state');
        const fpsEl = document.getElementById('fps');
        const handsEl = document.getElementById('hands');

        let prevX = 0.5, prevY = 0.5;
        let isClicking = false;
        let lastTime = Date.now();
        let hoveredElement = null;

        function distance(p1, p2) {
            return Math.hypot(p1.x - p2.x, p1.y - p2.y);
        }

        function lerp(start, end, amt) {
            return (1 - amt) * start + amt * end;
        }

        function mapRange(value, inMin, inMax, outMin, outMax) {
            return Math.max(outMin, Math.min(outMax,
                (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
            ));
        }

        function updateCursor(x, y) {
            const cursorX = x * window.innerWidth;
            const cursorY = y * window.innerHeight;

            cursorEl.style.display = 'block';
            cursorEl.style.left = (cursorX - 20) + 'px';
            cursorEl.style.top = (cursorY - 20) + 'px';

            const elements = document.querySelectorAll('.cell, .btn');
            let found = false;

            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (cursorX >= rect.left && cursorX <= rect.right &&
                    cursorY >= rect.top && cursorY <= rect.bottom) {
                    if (hoveredElement !== el) {
                        if (hoveredElement) {
                            hoveredElement.style.boxShadow = '';
                        }
                        el.style.boxShadow = '0 5px 25px rgba(0,255,0,0.6)';
                        hoveredElement = el;
                    }
                    found = true;
                } else if (el === hoveredElement) {
                    el.style.boxShadow = '';
                }
            });

            if (!found && hoveredElement) {
                hoveredElement.style.boxShadow = '';
                hoveredElement = null;
            }
        }

        function onResults(results) {
            const now = Date.now();
            fpsEl.textContent = Math.round(1000 / (now - lastTime));
            lastTime = now;

            ctx.save();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                handsEl.textContent = results.multiHandLandmarks.length;
                const landmarks = results.multiHandLandmarks[0];

                const indexMCP = landmarks[5];
                const indexTip = landmarks[8];
                const thumbTip = landmarks[4];
                const wrist = landmarks[0];

                // Draw tracking
                ctx.beginPath();
                ctx.arc(indexMCP.x * 640, indexMCP.y * 480, 12, 0, 2 * Math.PI);
                ctx.fillStyle = '#00ffff';
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(thumbTip.x * 640, thumbTip.y * 480);
                ctx.lineTo(indexTip.x * 640, indexTip.y * 480);
                ctx.strokeStyle = isClicking ? '#00ff00' : '#ffff00';
                ctx.lineWidth = 3;
                ctx.stroke();

                // Cursor position
                let rawX = mapRange(indexMCP.x, 0.2, 0.8, 0, 1);
                let rawY = mapRange(indexMCP.y, 0.2, 0.8, 0, 1);
                const currX = lerp(prevX, rawX, 0.2);
                const currY = lerp(prevY, rawY, 0.2);
                prevX = currX;
                prevY = currY;

                updateCursor(currX, currY);

                // Click detection
                const pinchDist = distance(thumbTip, indexTip);
                const handScale = distance(wrist, indexMCP);
                const ratio = pinchDist / handScale;

                if (ratio < 0.25) {
                    if (!isClicking) {
                        isClicking = true;
                        stateEl.textContent = 'CLICK';
                        stateEl.className = 'hud-value state-click';
                        cursorEl.classList.add('clicking');
                        if (hoveredElement) {
                            hoveredElement.click();
                        }
                    }
                } else {
                    if (isClicking) {
                        isClicking = false;
                        stateEl.textContent = 'Hover';
                        stateEl.className = 'hud-value state-hover';
                        cursorEl.classList.remove('clicking');
                    }
                }
            } else {
                handsEl.textContent = '0';
            }

            ctx.restore();
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

        const camera = new Camera(video, {
            onFrame: async () => {
                await hands.send({ image: video });
            },
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
    print("⭕❌ Pointing Tic-Tac-Toe Started!")
    print("🌐 Visit http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)