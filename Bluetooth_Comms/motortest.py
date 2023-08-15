import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
pin2 = 17
pin1 = 27

GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)

try:
    print("on")
    GPIO.output(pin1, GPIO.HIGH)
    GPIO.output(pin2, GPIO.LOW)
    time.sleep(0.3)
    GPIO.output(pin2, GPIO.LOW)
    GPIO.output(pin1, GPIO.LOW)
    print("off")
    time.sleep(2)
    GPIO.output(pin2, GPIO.HIGH)
    GPIO.output(pin1, GPIO.LOW)
    #print("re on")
    time.sleep(1)
finally:
    GPIO.output(pin1, GPIO.LOW)
    GPIO.output(pin2, GPIO.LOW)
GPIO.cleanup()
