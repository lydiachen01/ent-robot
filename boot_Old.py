# boot.py == main.py
# aka. runs the code every time we reboot (can call the functions later)

# """
# ESP32 + L298N 2-Wheel Robot - Simple Spin Test
# No ENA/ENB needed (make sure jumpers are ON the L298N board)
# """
#

# Complete project details at https://RandomNerdTutorials.com

try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'Lydiaaaaa'
password = 'KungFuPanda'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

# --- Web Server---
# AF_INET = setup comm over IPv4 networks
# SOCK_STREAM = create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 8080))
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html><html><body></body></html>'
    conn.send(response)
    conn.close()

# from machine import Pin
# import time
# 
# # Motor A (Left motor) - connected to IN1 and IN2
# IN1 = Pin(27, Pin.OUT)
# IN2 = Pin(26, Pin.OUT)
# 
# # Motor B (Right motor) - connected to IN3 and IN4
# IN3 = Pin(25, Pin.OUT)
# IN4 = Pin(33, Pin.OUT)
# 
# def stop():
#     """Stop both motors"""
#     IN1.value(0)
#     IN2.value(0)
#     IN3.value(0)
#     IN4.value(0)
# 
# def spin_right():
#     """Spin right - left motor forward, right motor backward"""
#     IN1.value(1)  # Left motor forward
#     IN2.value(0)
#     IN3.value(0)  # Right motor backward
#     IN4.value(1)
# 
# def spin_left():
#     """Spin left - right motor forward, left motor backward"""
#     IN1.value(0)  # Left motor backward
#     IN2.value(1)
#     IN3.value(1)  # Right motor forward
#     IN4.value(0)
# 
# # Main program
# print("Starting spin test...")
# 
# # Make sure motors are stopped
# stop()
# time.sleep(1)
# 
# # Spin right for 3 seconds
# print("Spinning right...")
# spin_right()
# time.sleep(3)
# 
# # Stop for 1 second
# print("Stopping...")
# stop()
# time.sleep(1)
# 
# # Spin left for 3 seconds
# print("Spinning left...")
# spin_left()
# time.sleep(3)
# 
# # Stop
# print("Done! Stopping motors.")
# stop()


# left_in1.off() # left backwards 
# left_in2.off() # left forwards
# right_in3.off() # right forwards
# right_in4.off() # right backwards
    
# forward = left forwards + right forwards
# right = left forwards
# left = right forwards

# later todo:
# two joysticks -> one for each wheel (for mannuevering