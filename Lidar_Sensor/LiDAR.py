# -*- coding: utf-8 -*
import serial
import pigpio
import time
import socket
from _thread import *
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.cleanup() # cleanup all GPIO 

################ Module의 기본 설정 데이터들 ################

RX = 23 # Raspi의 GPIO 23번포트를 사용한다

pi = pigpio.pi()
pi.set_mode(RX, pigpio.INPUT)
pi.bb_serial_read_open(RX, 115200) 

MODULENAME = "LIDAR" # 모듈의 이름
HOST = '127.0.0.1' # Main server의 주소
PORT = 9999 # Main server과 연결할 포트
MODULENO = 0 ## 모듈 번호에 알맞게 바꾸기

################ Logging System ################

def logdata(text): # 데이터를 로깅할 때 사용
    try:
        t = datetime.today().isoformat(sep=' ', timespec='milliseconds')
        f.write(f'[{t}] {text}')
        f.write('\n')
    except:
        print("An error has been generated while inserting log data")
        return

f = open(f'./{MODULENAME}.txt', 'a') # 로그를 저장할 파일을 오픈
logdata("Log file generated")

################################ Main Comms ##################################
# 메인 서버와 통신을 시도한다
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.send(f'{MODULENO}'.encode()) ## 통신이 성사되면 모듈 번호를 보낸다

print (f'>> Module {MODULENO} Connected!')

def send_data(data): # data는 string type으로 보내자!!!!
    client_socket.send(f'{MODULENO}{data}'.encode())
    logdata(f'sended {MODULENO}{data} to server')

############################### Module Code #################################

def getTFminiData():
  while True:
    #print("#############")
    time.sleep(0.05)	#change the value if needed
    (count, recv) = pi.bb_serial_read(RX)
    if count > 8:
      for i in range(0, count-9):
        if recv[i] == 89 and recv[i+1] == 89: # 0x59 is 89
          checksum = 0
          for j in range(0, 8):
            checksum = checksum + recv[i+j]
          checksum = checksum % 256
          if checksum == recv[i+8]:
            distance = recv[i+2] + recv[i+3] * 256
            strength = recv[i+4] + recv[i+5] * 256
            if distance <= 1200 and strength < 2000:
              send_data(distance)
              print(distance, strength) 
            #else:
              # raise ValueError('distance error: %d' % distance)	
            #i = i + 9


if __name__ == '__main__':
  try:
    getTFminiData()
  except:  
    pi.bb_serial_read_close(RX)
    pi.stop()
    client_socket.close()
    f.close()