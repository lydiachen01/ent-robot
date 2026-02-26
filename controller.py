import requests
from pynput import keyboard

ESP32_IP = 'http://10.243.87.230'

pressed = set()

KEY_MAP = {
    'w': 'f',
    's': 'b',
    'a': 'l',
    'd': 'r',
    keyboard.Key.up: 'f',
    keyboard.Key.down: 'b',
    keyboard.Key.left: 'l',
    keyboard.Key.right: 'r',
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
            requests.get(f"{ESP32_IP}/cmd/{KEY_MAP[k]}")
            return
    print("Sending: stop")
    requests.get(f"{ESP32_IP}/cmd/s")

def on_press(key):
    print(f"Key pressed: {key}")
    pressed.add(get_key_id(key))
    send_current()

def on_release(key):
    print(f"Key released: {key}")
    pressed.discard(get_key_id(key))
    send_current()
    if key == keyboard.Key.esc:
        return False

print("Listening for keypresses. Press ESC to quit.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()