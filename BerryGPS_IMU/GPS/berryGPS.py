from gps import *
import time
import datetime
import serial
import socket
from _thread import *

# 2023 KAIST CANSAT Competition | Team RPG
# BerryIMU_BARO.py | Developed by Hyeon Lee
# Credits : https://github.com/ozzmaker/BerryIMU/tree/master for BerryGPS CODE

MODULENAME = "BARO" # 모듈의 이름
HOST = '127.0.0.1' # Main server의 주소
PORT = 9999 # Main server과 연결할 포트
MODULENO = 3 ## 모듈 번호에 알맞게 바꾸기

################ Logging System ################

def logdata(text): # 데이터를 로깅할 때 사용
    try:
        t = datetime.today().isoformat(sep=' ', timespec='milliseconds')
        f.write(f'[{t}] {text}')
        f.write('\n')
    except Exception as e:
        print("An error has been generated while inserting log data")
        print(f"Error : {e}")
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
    logdata(f'send {MODULENO}{data} to server')

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

print('gps connected!')
try:
    while True:
        report = gpsd.next()
        #print(report)
        if report['class'] == 'TPV':
            #print('report is TPV')
            GPSlat = round(getattr(report, 'lat', 0.0), 2)
            GPSlon = round(getattr(report, 'lon', 0.0), 2)
            GPStime = round(getattr(report, 'time',''), 2)
            GPSalt = round(getattr(report, 'alt','nan'), 2)
            GPSepv = round(getattr(report, 'epv','nan'), 2)
            GPSept = round(getattr(report, 'ept','nan'), 2)
            GPSspeed = round(getattr(report, 'speed','nan'), 2)
            GPSclimb = round(getattr(report, 'climb','nan'), 2)

            print(f'''
            lat : {GPSlat}
            lon : {GPSlon}
            time : {GPStime}
            alt : {GPSalt}
            epv : {GPSepv}
            ept : {GPSept}
            speed : {GPSspeed}
            climb : {GPSclimb}
            ''')
            send_data(f"{GPSlat},{GPSlon},{GPSalt},{GPStime},{GPSepv},{GPSept},{GPSspeed},{GPSclimb}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Keyboardinterrupt!!")
finally:
    print("exit")
