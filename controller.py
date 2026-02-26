import serial
from pynput import keyboard

print("Connecting to ESP32...")
ser = serial.Serial('COM5', 115200)
print(f"Connected on {ser.name}")

pressed = set()

KEY_MAP = {
    'w': b'f',
    's': b'b',
    'a': b'l',
    'd': b'r',
    keyboard.Key.up: b'f',
    keyboard.Key.down: b'b',
    keyboard.Key.left: b'l',
    keyboard.Key.right: b'r',
}

PRIORITY = ['w', 's', 'a', 'd',
            keyboard.Key.up, keyboard.Key.down,
            keyboard.Key.left, keyboard.Key.right]

def get_key_id(key):
    try:
        return key.char
    except AttributeError:
        return key

def send_current():
    for k in PRIORITY:
        if k in pressed:
            print(f"Sending: {KEY_MAP[k]}")
            ser.write(KEY_MAP[k])
            return
    print("Sending: stop")
    ser.write(b's')

def on_press(key):
    print(f"Key pressed: {key}")
    pressed.add(get_key_id(key))
    send_current()

def on_release(key):
    print(f"Key released: {key}")
    pressed.discard(get_key_id(key))
    send_current()
    if key == keyboard.Key.esc:
        print("Exiting...")
        ser.write(b's')
        ser.close()
        return False

print("Listening for keypresses. Press ESC to quit.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()