import network

print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Wireless')

while not wlan.isconnected():
    pass

print("WiFi connected! IP:", wlan.ifconfig()[0])

import socket
from machine import Pin, PWM

print("Starting servo controller...")

servo_pin = PWM(Pin(13), freq=50)

def set_angle(angle):
    # Map 0-180 degrees to duty cycle (approx 26-128 for ESP32 PWM 10-bit at 50Hz)
    min_duty = 26   # ~0.5ms pulse
    max_duty = 128  # ~2.5ms pulse
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo_pin.duty(duty)

set_angle(90)  # Start centered

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Servo Control</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a0a;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Courier New', monospace;
    overflow: hidden;
    gap: 40px;
  }
  h1 {
    color: #00ff88;
    font-size: 1rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    opacity: 0.8;
  }

  /* Dial */
  .dial-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  canvas {
    cursor: pointer;
  }
  .angle-display {
    color: #00ff88;
    font-size: 3rem;
    letter-spacing: 0.1em;
    text-shadow: 0 0 20px #00ff8888;
    min-width: 120px;
    text-align: center;
  }
  .angle-unit {
    font-size: 1.2rem;
    opacity: 0.5;
  }

  /* Slider */
  .slider-wrap {
    width: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  input[type=range] {
    -webkit-appearance: none;
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(to right, #00ff88 var(--pct), #1a1a1a var(--pct));
    outline: none;
    border: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00ff88, #00aa55);
    box-shadow: 0 0 12px #00ff8877;
    cursor: grab;
  }
  .tick-row {
    display: flex;
    justify-content: space-between;
    width: 100%;
    color: #00ff8855;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
  }

  /* Presets */
  .presets {
    display: flex;
    gap: 12px;
  }
  .preset-btn {
    background: #111;
    border: 1px solid #00ff8833;
    color: #00ff88;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    padding: 10px 18px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s, box-shadow 0.15s;
  }
  .preset-btn:hover {
    background: #00ff8822;
    box-shadow: 0 0 12px #00ff8833;
  }

  .status {
    color: #00ff8855;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
  }
</style>
</head>
<body>
<h1>&#9632; Servo Control</h1>

<div class="dial-wrap">
  <canvas id="dial" width="200" height="200"></canvas>
  <div class="angle-display"><span id="angleNum">90</span><span class="angle-unit">°</span></div>
</div>

<div class="slider-wrap">
  <input type="range" id="slider" min="0" max="180" value="90" style="--pct:50%">
  <div class="tick-row">
    <span>0°</span><span>45°</span><span>90°</span><span>135°</span><span>180°</span>
  </div>
</div>

<div class="presets">
  <button class="preset-btn" onclick="setAngle(0)">0°</button>
  <button class="preset-btn" onclick="setAngle(45)">45°</button>
  <button class="preset-btn" onclick="setAngle(90)">90°</button>
  <button class="preset-btn" onclick="setAngle(135)">135°</button>
  <button class="preset-btn" onclick="setAngle(180)">180°</button>
</div>

<div class="status" id="status">READY</div>

<script>
const IP = window.location.hostname;
const canvas = document.getElementById('dial');
const ctx = canvas.getContext('2d');
const slider = document.getElementById('slider');
let currentAngle = 90;
let sendTimer = null;

function send(angle) {
  clearTimeout(sendTimer);
  sendTimer = setTimeout(() => {
    fetch('http://' + IP + '/angle/' + angle).catch(() => {});
    document.getElementById('status').textContent = 'SENT ' + angle;
  }, 30); // debounce 30ms
}

function setAngle(angle) {
  currentAngle = Math.max(0, Math.min(180, Math.round(angle)));
  document.getElementById('angleNum').textContent = currentAngle;
  slider.value = currentAngle;
  slider.style.setProperty('--pct', (currentAngle / 180 * 100) + '%');
  drawDial(currentAngle);
  console.log("CURRENT ANGLE: ", currentAngle);
  send(currentAngle);
}

// --- Dial drawing ---
function drawDial(angle) {
  const cx = 100, cy = 110, r = 80;
  ctx.clearRect(0, 0, 200, 200);

  // Arc track (180° arc from left to right, bottom half up)
  const startA = Math.PI;       // 180° left
  const endA = 2 * Math.PI;     // 360° right

  // Background arc
  ctx.beginPath();
  ctx.arc(cx, cy, r, startA, endA);
  ctx.strokeStyle = '#1a1a1a';
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Filled arc up to angle
  const fillEnd = startA + (angle / 180) * Math.PI;
  ctx.beginPath();
  ctx.arc(cx, cy, r, startA, fillEnd);
  ctx.strokeStyle = '#00ff88';
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Tick marks at 0, 45, 90, 135, 180
  [0, 45, 90, 135, 180].forEach(a => {
    const rad = startA + (a / 180) * Math.PI;
    const x1 = cx + (r - 14) * Math.cos(rad);
    const y1 = cy + (r - 14) * Math.sin(rad);
    const x2 = cx + (r + 4) * Math.cos(rad);
    const y2 = cy + (r + 4) * Math.sin(rad);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = '#00ff8844';
    ctx.lineWidth = 2;
    ctx.stroke();
  });

  // Needle knob
  const needleRad = startA + (angle / 180) * Math.PI;
  const nx = cx + r * Math.cos(needleRad);
  const ny = cy + r * Math.sin(needleRad);
  ctx.beginPath();
  ctx.arc(nx, ny, 10, 0, 2 * Math.PI);
  ctx.fillStyle = '#00ff88';
  ctx.shadowColor = '#00ff88';
  ctx.shadowBlur = 15;
  ctx.fill();
  ctx.shadowBlur = 0;
}

// --- Dial drag interaction ---
let dragging = false;
function angleFromPointer(e) {
  const rect = canvas.getBoundingClientRect();
  const touch = e.touches ? e.touches[0] : e;
  const dx = touch.clientX - rect.left - 100;
  const dy = touch.clientY - rect.top - 110;
  let rad = Math.atan2(dy, dx); // -PI to PI
  // Remap: leftmost (PI) = 0°, rightmost (0/2PI) = 180°
  let a = (rad - Math.PI) / Math.PI * 180;
  // atan2 on upper half gives negative, clamp to [0,180]
  if (a < 0) a = 0;
  if (a > 180) a = 180;
  return Math.round(a);
}

canvas.addEventListener('mousedown', e => { dragging = true; setAngle(angleFromPointer(e)); });
canvas.addEventListener('touchstart', e => { dragging = true; setAngle(angleFromPointer(e)); }, {passive:true});
window.addEventListener('mousemove', e => { if (dragging) setAngle(angleFromPointer(e)); });
canvas.addEventListener('touchmove', e => { if (dragging) setAngle(angleFromPointer(e)); }, {passive:true});
window.addEventListener('mouseup', () => dragging = false);
window.addEventListener('touchend', () => dragging = false);

console.log("SLIDER VALUE: ", slider.value);
console.log("PARSE INT | SLIDER VALUE: ", parseInt(slider.value));

// --- Slider ---
slider.addEventListener('input', () => setAngle(parseInt(slider.value)));

slider.addEventListener('input', () => {
  log('SLIDER VALUE: ' + slider.value);
  log('PARSE INT | SLIDER VALUE: ' + parseInt(slider.value));
  setAngle(parseInt(slider.value));
});

// Init
drawDial(90);
</script>
</body>
</html>"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

print("Web Server | IP Address: http://172.16.9.243")

while True:
    conn, _ = s.accept()
    request = conn.recv(1024).decode()
    if 'GET /angle/' in request:
        try:
            angle = int(request.split('GET /angle/')[1].split(' ')[0])
            angle = max(0, min(180, angle))
            set_angle(angle)
            print(f"Servo -> {angle}°")
        except:
            pass
        conn.send('HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')
    elif 'GET /' in request:
        conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + HTML)
    conn.close()
