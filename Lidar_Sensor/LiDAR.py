# -*- coding: utf-8 -*
import serial
import time

ser = serial.Serial("/dev/serial0", 115200)


def getTFminiData():
    while True:
        #time.sleep(0.1)
        count = ser.in_waiting
        if count > 8:
            recv = ser.read(9)
            ser.reset_input_buffer()
            # type(recv), 'str' in python2(recv[0] = 'Y'), 'bytes' in python3(recv[0] = 89)
            # type(recv[0]), 'str' in python2, 'int' in python3

            if recv[0] == 0x59 and recv[1] == 0x59:     #python3
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                print('(', distance, ',', strength, ')')
                ser.reset_input_buffer()

            # you can also distinguish python2 and python3:
            #import sys
            #sys.version[0] == '2'    #True, python2
            #sys.version[0] == '3'    #True, python3


if __name__ == '__main__':
    try:
        if ser.is_open == False:
            ser.open()
            #print(syncdata())
        getTFminiData()
    except KeyboardInterrupt:   # Ctrl+C
        print('exit')
        if ser != None:
            ser.close()
