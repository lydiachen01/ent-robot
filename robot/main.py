import socket
from machine import Pin

print("Starting motor controller...")

left_in1 = Pin(32, Pin.OUT)
left_in2 = Pin(33, Pin.OUT)
right_in3 = Pin(25, Pin.OUT)
right_in4 = Pin(26, Pin.OUT)

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
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Robot Control</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; touch-action: none; }
  body {
    background: #0a0a0a;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Courier New', monospace;
    overflow: hidden;
  }
  h1 {
    color: #00ff88;
    font-size: 1rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 40px;
    opacity: 0.8;
  }
  .hud {
    display: flex;
    gap: 80px;
    align-items: center;
    justify-content: center;
  }
  .joystick-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  .label {
    color: #00ff88;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    opacity: 0.6;
  }
  .joystick-zone {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle, #1a1a1a, #0d0d0d);
    border: 2px solid #00ff8833;
    position: relative;
    box-shadow: 0 0 30px #00ff8822, inset 0 0 20px #00000066;
  }
  .joystick-knob {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00ff88, #00aa55);
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 20px #00ff8866;
    transition: box-shadow 0.1s;
    cursor: grab;
  }
  .joystick-knob.active {
    box-shadow: 0 0 40px #00ff88aa;
  }
  .status {
    margin-top: 40px;
    color: #00ff8866;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
  }
</style>
</head>
<body>
<h1>&#9632; Robot Control</h1>
<div class="hud">
  <div class="joystick-wrap">
    <div class="label">LEFT</div>
    <div class="joystick-zone" id="leftZone">
      <div class="joystick-knob" id="leftKnob"></div>
    </div>
  </div>
  <div class="joystick-wrap">
    <div class="label">RIGHT</div>
    <div class="joystick-zone" id="rightZone">
      <div class="joystick-knob" id="rightKnob"></div>
    </div>
  </div>
</div>
<div class="status" id="status">STANDBY</div>
<script>
const IP = window.location.hostname;

function send(cmd) {
  fetch('http://' + IP + '/cmd/' + cmd).catch(() => {});
}

function makeJoystick(zoneEl, knobEl, side) {
  let active = false;
  let lastCmd = 's';

  function getCmd(dy) {
    if (dy < -20) return side === 'l' ? 'lf' : 'rf';
    if (dy > 20)  return side === 'l' ? 'lb' : 'rb';
    return 's';
  }

  function onStart(e) {
    active = true;
    knobEl.classList.add('active');
    onMove(e);
  }

  function onMove(e) {
    if (!active) return;
    const touch = e.touches ? e.touches[0] : e;
    const rect = zoneEl.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = Math.max(-50, Math.min(50, touch.clientX - cx));
    const dy = Math.max(-50, Math.min(50, touch.clientY - cy));
    knobEl.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
    const cmd = getCmd(dy);
    if (cmd !== lastCmd) {
      lastCmd = cmd;
      send(cmd);
      document.getElementById('status').textContent = cmd.toUpperCase();
    }
  }

  function onEnd() {
    active = false;
    knobEl.classList.remove('active');
    knobEl.style.transform = 'translate(-50%, -50%)';
    lastCmd = 's';
    send('s');
    document.getElementById('status').textContent = 'STANDBY';
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

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

print("Web Server | IP Address: http://10.243.87.230")

while True:
    conn, _ = s.accept()
    request = conn.recv(1024).decode()
    print("Request:", request)
    if 'GET /cmd/' in request:
        cmd = request.split('GET /cmd/')[1].split(' ')[0]
        print(f"Executing: {cmd}")
        action = COMMANDS.get(cmd)
        if action:
            action()
        conn.send('HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')
    elif 'GET /' in request:
        conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + HTML)
    conn.close()
