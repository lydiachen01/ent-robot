import network

print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Wireless')

while not wlan.isconnected():
    pass

print("WiFi connected! IP:", wlan.ifconfig()[0])