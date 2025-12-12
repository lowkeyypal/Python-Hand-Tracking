// DOM Elements
const cells = document.querySelectorAll('.cell');
const statusEl = document.getElementById('status');
const playerScoreEl = document.getElementById('playerScore');
const aiScoreEl = document.getElementById('aiScore');
const drawScoreEl = document.getElementById('drawScore');
const playerLabelEl = document.getElementById('playerLabel');
const aiLabelEl = document.getElementById('aiLabel');

// UI Update Functions
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

function updateStatus(message) {
    statusEl.textContent = message;
}

function updateScores() {
    playerScoreEl.textContent = scores.player;
    aiScoreEl.textContent = scores.ai;
    drawScoreEl.textContent = scores.draw;
    playerLabelEl.textContent = `You (${playerSymbol})`;
    aiLabelEl.textContent = `AI (${aiSymbol})`;
}

// Event Listeners
function initializeEventListeners() {
    // Cell clicks
    cells.forEach((cell, i) => {
        cell.addEventListener('click', () => makeMove(i));
    });

    // Control buttons
    document.getElementById('newGame').addEventListener('click', resetGame);
    document.getElementById('undo').addEventListener('click', undoMove);

    // Difficulty buttons
    document.querySelectorAll('[data-difficulty]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-difficulty]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            changeDifficulty(btn.dataset.difficulty);
        });
    });

    // Symbol buttons
    document.querySelectorAll('[data-symbol]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-symbol]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            changeSymbol(btn.dataset.symbol);
        });
    });
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
});
