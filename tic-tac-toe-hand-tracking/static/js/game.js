// Game State
let board = ['', '', '', '', '', '', '', '', ''];
let currentPlayer = 'X';
let playerSymbol = 'X';
let aiSymbol = 'O';
let gameActive = true;
let difficulty = 'easy';
let scores = { player: 0, ai: 0, draw: 0 };
let moveHistory = [];

const winPatterns = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
];

// Game Logic Functions
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
    gameActive = false; // Lock during AI's turn
    updateStatus(`AI's Turn (${aiSymbol})`);

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
            gameActive = true; // Unlock for player's turn
            updateStatus(`Your Turn (${playerSymbol})`);
        }
    }
    else {
        gameActive = true; // Unlock if no move is possible
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
        updateStatus('🎉 You Win!');
    } else if (result.winner === aiSymbol) {
        scores.ai++;
        updateStatus('🤖 AI Wins!');
    } else {
        scores.draw++;
        updateStatus('🤝 Draw!');
    }

    updateScores();

    if (result.line.length > 0) {
        const cells = document.querySelectorAll('.cell');
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
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => cell.classList.remove('winner'));

    if (playerSymbol === 'O') {
        updateStatus(`AI's Turn (${aiSymbol})`);
        gameActive = false;  // Lock during AI's turn
        setTimeout(() => aiMove(), 500);
    } else {
        updateStatus(`Your Turn (${playerSymbol})`);
    }
}

function undoMove() {
    if (moveHistory.length < 1) return;
    board = moveHistory.pop();
    currentPlayer = playerSymbol;
    gameActive = true;
    updateDisplay();
    updateStatus(`Your Turn (${playerSymbol})`);
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => cell.classList.remove('winner'));
}

function changeDifficulty(newDifficulty) {
    difficulty = newDifficulty;
    resetGame();
}

function changeSymbol(newSymbol) {
    playerSymbol = newSymbol;
    aiSymbol = playerSymbol === 'X' ? 'O' : 'X';
    scores = { player: 0, ai: 0, draw: 0 };
    updateScores();
    resetGame();
}
