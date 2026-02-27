import network
import socket
from machine import Pin, PWM

print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Wireless')

while not wlan.isconnected():
    pass

print("WiFi connected! IP:", wlan.ifconfig()[0])
print("Starting robot1 controller...")

# --- Motor Pins ---
left_in1 = Pin(32, Pin.OUT)
left_in2 = Pin(33, Pin.OUT)
right_in3 = Pin(25, Pin.OUT)
right_in4 = Pin(26, Pin.OUT)

# --- Servo ---
servo_pin = PWM(Pin(13), freq=50)

def notify_robot2(angle):
    try:
        r2 = socket.socket()
        r2.settimeout(0.5)
        r2.connect(('172.16.9.243', 80))
        r2.send(b'GET /angle/' + str(angle).encode() + b' HTTP/1.0\r\nHost: 172.16.9.243\r\n\r\n')
        r2.close()
    except:
        pass  # don't crash robot1 if robot2 is unreachable

def set_angle(angle):
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo_pin.duty(duty)
    # Mirror to robot2: robot1 @ 90 -> robot2 @ 0, and vice versa
    if angle == 90:
        notify_robot2(0)
    elif angle == 0:
        notify_robot2(90)

set_angle(90)  # Start centered

# --- Motor Functions ---
def stop():
    left_in1.off(); left_in2.off()
    right_in3.off(); right_in4.off()

def forward():
    left_in1.off(); left_in2.on()
    right_in3.on(); right_in4.off()

def backward():
    left_in1.on(); left_in2.off()
    right_in3.off(); right_in4.on()

def turn_left():
    left_in1.off(); left_in2.off()
    right_in3.on(); right_in4.off()

def turn_right():
    left_in1.off(); left_in2.on()
    right_in3.off(); right_in4.off()

def left_forward():
    left_in1.off(); left_in2.on()
    right_in3.off(); right_in4.off()

def left_backward():
    left_in1.on(); left_in2.off()
    right_in3.off(); right_in4.off()

def right_forward():
    left_in1.off(); left_in2.off()
    right_in3.on(); right_in4.off()

def right_backward():
    left_in1.off(); left_in2.off()
    right_in3.off(); right_in4.on()

COMMANDS = {
    'f': forward,
    'b': backward,
    'l': turn_left,
    'r': turn_right,
    's': stop,
    'lf': left_forward,
    'lb': left_backward,
    'rf': right_forward,
    'rb': right_backward,
}

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Robot1 Control</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; touch-action: none; }
  body {
    background: #0a0a0a;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Courier New', monospace;
    overflow: hidden;
    gap: 24px;
    padding: 20px 0;
  }
  h1 { color: #00ff88; font-size: 1rem; letter-spacing: 0.3em; text-transform: uppercase; opacity: 0.8; }
  .servo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 20px 30px;
    border: 1px solid #00ff8822;
    border-radius: 12px;
    background: #0d0d0d;
  }
  .section-label { color: #00ff88; font-size: 0.65rem; letter-spacing: 0.3em; opacity: 0.5; text-transform: uppercase; }
  .dial-row { display: flex; align-items: center; gap: 24px; }
  canvas { cursor: pointer; }
  .angle-display { color: #00ff88; font-size: 2.4rem; letter-spacing: 0.1em; text-shadow: 0 0 20px #00ff8888; min-width: 90px; text-align: center; }
  .angle-unit { font-size: 1rem; opacity: 0.5; }
  .slider-wrap { width: 280px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
  input[type=range] {
    -webkit-appearance: none; width: 100%; height: 6px; border-radius: 3px;
    background: linear-gradient(to right, #00ff88 var(--pct), #1a1a1a var(--pct));
    outline: none; border: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 24px; height: 24px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00ff88, #00aa55);
    box-shadow: 0 0 12px #00ff8877; cursor: grab;
  }
  .tick-row { display: flex; justify-content: space-between; width: 100%; color: #00ff8855; font-size: 0.6rem; letter-spacing: 0.1em; }
  .presets { display: flex; gap: 10px; }
  .preset-btn {
    background: #111; border: 1px solid #00ff8833; color: #00ff88;
    font-family: 'Courier New', monospace; font-size: 0.75rem; letter-spacing: 0.15em;
    padding: 8px 16px; border-radius: 4px; cursor: pointer;
    transition: background 0.15s, box-shadow 0.15s; touch-action: manipulation;
  }
  .preset-btn:hover, .preset-btn:active { background: #00ff8822; box-shadow: 0 0 12px #00ff8833; }
  .joystick-section { display: flex; flex-direction: column; align-items: center; gap: 14px; }
  .hud { display: flex; gap: 80px; align-items: center; justify-content: center; }
  .joystick-wrap { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .joy-label { color: #00ff88; font-size: 0.65rem; letter-spacing: 0.2em; opacity: 0.5; }
  .joystick-zone {
    width: 140px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle, #1a1a1a, #0d0d0d);
    border: 2px solid #00ff8833; position: relative;
    box-shadow: 0 0 30px #00ff8822, inset 0 0 20px #00000066;
  }
  .joystick-knob {
    width: 56px; height: 56px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00ff88, #00aa55);
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 20px #00ff8866; transition: box-shadow 0.1s; cursor: grab;
  }
  .joystick-knob.active { box-shadow: 0 0 40px #00ff88aa; }
  .status { color: #00ff8855; font-size: 0.65rem; letter-spacing: 0.2em; }
</style>
</head>
<body>

<h1>&#9632; Robot1 Control</h1>

<div class="servo-section">
  <div class="section-label">Servo</div>
  <div class="dial-row">
    <canvas id="dial" width="160" height="160"></canvas>
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
  </div>
</div>

<div class="joystick-section">
  <div class="section-label">Drive</div>
  <div class="hud">
    <div class="joystick-wrap">
      <div class="joy-label">LEFT</div>
      <div class="joystick-zone" id="leftZone">
        <div class="joystick-knob" id="leftKnob"></div>
      </div>
    </div>
    <div class="joystick-wrap">
      <div class="joy-label">RIGHT</div>
      <div class="joystick-zone" id="rightZone">
        <div class="joystick-knob" id="rightKnob"></div>
      </div>
    </div>
  </div>
</div>

<div class="status" id="status">STANDBY</div>

<script>
const IP = window.location.hostname;

function sendCmd(cmd) { fetch('http://' + IP + '/cmd/' + cmd).catch(() => {}); }
function sendAngle(angle) { fetch('http://' + IP + '/angle/' + angle).catch(() => {}); }

// Servo
const canvas = document.getElementById('dial');
const ctx = canvas.getContext('2d');
const slider = document.getElementById('slider');
let currentAngle = 90;
let angleTimer = null;

function setAngle(angle) {
  currentAngle = Math.max(0, Math.min(180, Math.round(angle)));
  document.getElementById('angleNum').textContent = currentAngle;
  slider.value = currentAngle;
  slider.style.setProperty('--pct', (currentAngle / 180 * 100) + '%');
  drawDial(currentAngle);
  clearTimeout(angleTimer);
  angleTimer = setTimeout(() => {
    sendAngle(currentAngle);
    document.getElementById('status').textContent = 'SERVO ' + currentAngle + '\u00b0';
  }, 30);
}

function drawDial(angle) {
  const cx = 80, cy = 88, r = 64;
  ctx.clearRect(0, 0, 160, 160);
  const startA = Math.PI;
  ctx.beginPath(); ctx.arc(cx, cy, r, startA, 2 * Math.PI);
  ctx.strokeStyle = '#1a1a1a'; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.stroke();
  const fillEnd = startA + (angle / 180) * Math.PI;
  ctx.beginPath(); ctx.arc(cx, cy, r, startA, fillEnd);
  ctx.strokeStyle = '#00ff88'; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.stroke();
  [0, 45, 90, 135, 180].forEach(a => {
    const rad = startA + (a / 180) * Math.PI;
    const x1 = cx + (r - 11) * Math.cos(rad), y1 = cy + (r - 11) * Math.sin(rad);
    const x2 = cx + (r + 3) * Math.cos(rad),  y2 = cy + (r + 3) * Math.sin(rad);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
    ctx.strokeStyle = '#00ff8844'; ctx.lineWidth = 2; ctx.stroke();
  });
  const nr = startA + (angle / 180) * Math.PI;
  const nx = cx + r * Math.cos(nr), ny = cy + r * Math.sin(nr);
  ctx.beginPath(); ctx.arc(nx, ny, 8, 0, 2 * Math.PI);
  ctx.fillStyle = '#00ff88'; ctx.shadowColor = '#00ff88'; ctx.shadowBlur = 14;
  ctx.fill(); ctx.shadowBlur = 0;
}

function angleFromPointer(e) {
  const rect = canvas.getBoundingClientRect();
  const touch = e.touches ? e.touches[0] : e;
  const dx = touch.clientX - rect.left - 80, dy = touch.clientY - rect.top - 88;
  let a = (Math.atan2(dy, dx) - Math.PI) / Math.PI * 180;
  return Math.round(Math.max(0, Math.min(180, a < 0 ? 0 : a)));
}

let dialDragging = false;
canvas.addEventListener('mousedown', e => { dialDragging = true; setAngle(angleFromPointer(e)); });
canvas.addEventListener('touchstart', e => { dialDragging = true; setAngle(angleFromPointer(e)); }, {passive:true});
window.addEventListener('mousemove', e => { if (dialDragging) setAngle(angleFromPointer(e)); });
canvas.addEventListener('touchmove', e => { if (dialDragging) setAngle(angleFromPointer(e)); }, {passive:true});
window.addEventListener('mouseup', () => dialDragging = false);
window.addEventListener('touchend', () => dialDragging = false);
slider.addEventListener('input', () => setAngle(parseInt(slider.value)));
drawDial(90);

// Joysticks
const state = { l: 0, r: 0 };
let lastDriveCmd = 's';

function resolveDrive() {
  const l = state.l, r = state.r;
  let cmd;
  if      (l === 1  && r === 1)  cmd = 'f';
  else if (l === -1 && r === -1) cmd = 'b';
  else if (l === 1  && r === 0)  cmd = 'lf';
  else if (l === -1 && r === 0)  cmd = 'lb';
  else if (l === 0  && r === 1)  cmd = 'rf';
  else if (l === 0  && r === -1) cmd = 'rb';
  else if (l === 1  && r === -1) cmd = 'r';
  else if (l === -1 && r === 1)  cmd = 'l';
  else                           cmd = 's';
  if (cmd !== lastDriveCmd) {
    lastDriveCmd = cmd;
    sendCmd(cmd);
    document.getElementById('status').textContent = 'DRIVE ' + cmd.toUpperCase();
  }
}

function makeJoystick(zoneEl, knobEl, side) {
  let active = false;
  function getVal(dy) { return dy < -20 ? 1 : dy > 20 ? -1 : 0; }
  function onStart(e) { active = true; knobEl.classList.add('active'); onMove(e); }
  function onMove(e) {
    if (!active) return;
    const touch = e.touches ? e.touches[0] : e;
    const rect = zoneEl.getBoundingClientRect();
    const dx = Math.max(-50, Math.min(50, touch.clientX - rect.left - rect.width / 2));
    const dy = Math.max(-50, Math.min(50, touch.clientY - rect.top - rect.height / 2));
    knobEl.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
    state[side] = getVal(dy);
    resolveDrive();
  }
  function onEnd() {
    active = false; knobEl.classList.remove('active');
    knobEl.style.transform = 'translate(-50%, -50%)';
    state[side] = 0; resolveDrive();
  }
  zoneEl.addEventListener('touchstart', onStart, {passive: true});
  zoneEl.addEventListener('touchmove', onMove, {passive: true});
  zoneEl.addEventListener('touchend', onEnd);
  zoneEl.addEventListener('mousedown', onStart);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onEnd);
}

makeJoystick(document.getElementById('leftZone'), document.getElementById('leftKnob'), 'l');
makeJoystick(document.getElementById('rightZone'), document.getElementById('rightKnob'), 'r');
</script>
</body>
</html>"""

# --- Web Server ---
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

stop()
print("Robot1 web server running...")

while True:
    conn, _ = s.accept()
    request = conn.recv(1024).decode()

    if 'GET /cmd/' in request:
        cmd = request.split('GET /cmd/')[1].split(' ')[0]
        print(f"Drive: {cmd}")
        action = COMMANDS.get(cmd)
        if action:
            action()
        conn.send('HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')

    elif 'GET /angle/' in request:
        try:
            angle = int(request.split('GET /angle/')[1].split(' ')[0])
            angle = max(0, min(180, angle))
            set_angle(angle)
            print(f"Servo: {angle}deg")
        except:
            pass
        conn.send('HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')

    elif 'GET /' in request:
        conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + HTML)

    conn.close()