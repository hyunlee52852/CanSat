import RPi.GPIO as GPIO
import time
#!/usr/bin/env python3
from bluedot.btcomm import BluetoothServer
from signal import pause
import datetime

# 2023 KAIST CANSAT Competition | Team RPG
# MotorRun.py | Developed by Hyeon Lee
# Credits : https://github.com/martinohanlon/BlueDot for Bluetooth COMMS

MODULENAME = "MOTOR" # 모듈의 이름

################ Logging System ################

def logdata(text): # 데이터를 로깅할 때 사용
    try:
        t = datetime.datetime.today().isoformat(sep=' ', timespec='milliseconds')
        f.write(f'[{t}] {text}')
        f.write('\n')
    except Exception as e:
        print("An error has been generated while inserting log data")
        print(f"Error : {e}")
        return

f = open(f'./{MODULENAME}.txt', 'a') # 로그를 저장할 파일을 오픈
logdata("Log file generated")

GPIO.setmode(GPIO.BCM)
pin1 = 17 # In1 port on Relay
pin2 = 27 # In2 port on Relay
####### Motor Settings ##########

# Pin1 | Pin2 | SKYCRANE
#____________________________________
# HIGH | LOW  | RELEASE // 줄이 풀린다
# LOW  | HIGH | PULL // 줄이 당겨진다

GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)
GPIO.output(pin2, GPIO.LOW)
GPIO.output(pin1, GPIO.LOW)

def PullMotor():
    logdata("MOTOR PULLED")
    GPIO.output(pin2, GPIO.HIGH)
    GPIO.output(pin1, GPIO.LOW)
    time.sleep(0.5) # 당기는 시간
    GPIO.output(pin2, GPIO.LOW)
    GPIO.output(pin1, GPIO.LOW)

def ReleaseMotor():
    logdata("MOTOR RELEASED")
    GPIO.output(pin1, GPIO.HIGH)
    GPIO.output(pin2, GPIO.LOW)
    time.sleep(0.5) # 줄을 푸는 시간
    GPIO.output(pin2, GPIO.LOW)
    GPIO.output(pin1, GPIO.LOW)

def data_received(data):
    logdata("recv - {}".format(data))
    logdata(f"Received {data}")
    if data == '0': # 아래쪽 모듈에서 0 을 받았을 때, 줄을 푼다
        ReleaseMotor()
    if data == '1': # 아래쪽 모듈에서 1을 받았을 때, 줄을 당긴다
        PullMotor()

def client_connected():
    logdata("client connected")

def client_disconnected():
    logdata("client disconnected")

print("init")
server = BluetoothServer(
    data_received,
    auto_start = False,
    when_client_connects = client_connected,
    when_client_disconnects = client_disconnected)

print("starting")
server.start()
print(server.server_address)
print("waiting for connection")

try:
    pause()
except KeyboardInterrupt as e:
    print("cancelled by user")
finally:
    print("stopping")
    server.stop()
    GPIO.cleanup()
print("stopped")


