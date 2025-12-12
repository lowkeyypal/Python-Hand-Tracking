// Hand Tracking Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const cursorEl = document.getElementById('cursor');
const stateEl = document.getElementById('state');
const fpsEl = document.getElementById('fps');
const handsEl = document.getElementById('hands');

// Hand Tracking State
let prevX = 0.5, prevY = 0.5;
let isClicking = false;
let lastTime = Date.now();
let hoveredElement = null;

// Utility Functions
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

// Cursor Update Function
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

// MediaPipe Results Handler
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

        // Draw tracking visualizations
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

        // Calculate cursor position (with horizontal flip fix)
        let rawX = mapRange(1 - indexMCP.x, 0.2, 0.8, 0, 1);
        let rawY = mapRange(indexMCP.y, 0.2, 0.8, 0, 1);
        const currX = lerp(prevX, rawX, 0.2);
        const currY = lerp(prevY, rawY, 0.2);
        prevX = currX;
        prevY = currY;

        updateCursor(currX, currY);

        // Pinch gesture detection
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

// Initialize MediaPipe Hands
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

// Initialize Camera
const camera = new Camera(video, {
    onFrame: async () => {
        await hands.send({ image: video });
    },
    width: 640,
    height: 480
});

camera.start();
