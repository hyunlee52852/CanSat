#!/usr/bin/env python3

# 2023 KAIST CANSAT Competition | Team RPG
# CommsCore.py | Developed by Hyeon Lee
# Credits : https://github.com/martinohanlon/BlueDot for Bluetooth COMMS

from bluedot.btcomm import BluetoothClient
from datetime import datetime
from time import sleep
from signal import pause

def data_received(data):
    print("recv - {}".format(data))

print("Connecting")
c = BluetoothClient("pi4", data_received)

print("Sending")
try:
    while True:
        c.send("hi {} \n".format(str(datetime.now())))
        sleep(1)
finally:
    c.disconnect()