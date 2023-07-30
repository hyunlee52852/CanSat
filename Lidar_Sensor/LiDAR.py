# -*- coding: utf-8 -*
import serial
import time
import socket
from _thread import *
from datetime import datetime


################ Module의 기본 설정 데이터들 ################

ser = serial.Serial("/dev/serial0", 115200) # Module의 통신 포트

MODULENAME = "LIDAR" # 모듈의 이름
HOST = '127.0.0.1' # Main server의 주소
PORT = 9999 # Main server과 연결할 포트
MODULENO = 0 ## 모듈 번호에 알맞게 바꾸기

################ Logging System ################

def logdata(text): # 데이터를 로깅할 때 사용
    try:
        t = datetime.today().isoformat(sep=' ', timespec='milliseconds')
        f.write(f'[{t}] {text}')
    except:
        print("An error has been generated while inserting log data")
        return

f = open(f'./Logs/{MODULENAME}.txt', 'a') # 로그를 저장할 파일을 오픈
logdata("Log file generated")

################################ Main Comms ##################################
# 메인 서버와 통신을 시도한다
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.send(f'{MODULENO}'.encode()) ## 통신이 성사되면 모듈 번호를 보낸다

print (f'>> Module {MODULENO} Connected!')

def send_data(data): # data는 string type으로 보내자!!!!
    client_socket.send(f'{MODULENO}{data}'.encode())

############################### Module Code #################################

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
                send_data(distance) # 데이터 보내기
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
        getTFminiData()
    except KeyboardInterrupt:   # Ctrl+C
        print('exit')
        if ser != None:
            ser.close()
        client_socket.close()
        f.close()
