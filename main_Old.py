import sys
from machine import Pin

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

COMMANDS = {
    'f': forward,
    'b': backward,
    'l': turn_left,
    'r': turn_right,
    's': stop,
}

while True:
    cmd = sys.stdin.read(1)
    action = COMMANDS.get(cmd)
    if action:
        action()
        