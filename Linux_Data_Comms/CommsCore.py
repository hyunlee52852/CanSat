import socket
from _thread import *
import time
import serial
from datetime import datetime
from bluedot.btcomm import BluetoothClient

# 2023 KAIST CANSAT Competition | Team RPG
# CommsCore.py | Developed by Hyeon Lee
# Credits : https://stickode.tistory.com/225 for Socket Communication

############# SCHEMATICS ############
# MODULES
# No | NAME       | DESC                   | Data format
# _______________________________________________________
# 0  | CORE       | 위성 중앙 시스템       | None
# 1  | ACCEL_GYRO | 가속도계, 자이로스코프 | {xms},{yms},{zms},{gyrooutX},{gyrooutY},{gyrooutZ}
# 2  | BARO       | 기압고도계             | {temperature},{pressure},{altitude}
# 3  | GPS        | GPS 모듈               | {lat},{lon},{alt},{time},{epv},{ept},{speed},{climb}
# 4  | LiDAR      | LiDAR 센서             | {distance}

############## 모듈 기본 데이터 ###############

MODULENAME = "CORE"
HOST = '127.0.0.1'
PORT = 9999

module_active = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


############## MISSION CRITICAL DATA ##############
PACKET_SEND_PERIOD = 1 # 패킷이 전송되는 주기 // 단위 : 초

SkycraneReleased = 0 # Skycrane이 풀렸는지 체크 // 0 = False, 1 = True
SkycraneActivated = 0 # Skycrane이 다시 감겼는지 체크 // 0 = False, 1 = True

DeployFlagCNT = 0
SkycraneCNT = 0

CurAccel = 0 # 현재 가속도 값 // 단위 : m/s^2
CurLiDARDistance = 1300 # 현재 LiDAR 거리 값

DEPLOYED_ACCEL = 9.2  # 위성이 Deploy 상태라고 가정하는 낙하 가속도
SKYCRANE_ACTIVATE_HEIGHT = 120 # Skycrane이 작동하는 LiDAR 센서 상의 거리 / 단위 : cm

################ Logging System ################
def logdata(text): # 데이터를 로깅할 때 사용
    try:
        t = datetime.now().isoformat(sep=' ', timespec='milliseconds')
        f.write(f'[{t}] {text}')
        f.write('\n')
        print(f'[{t}] {text}')
    except Exception as e:
        print("An error has been generated while inserting log data")
        print(f"Error : {e}")
        return

f = open(f'./{MODULENAME}.txt', 'a') # 로그를 저장할 파일을 오픈
logdata("Log file generated")

############ Bluetooth Comms ###########

print("Connecting to Bluetooth")
def data_received(data):
    logdata(f"recv - {data} from bluetooth")

try:
    c = BluetoothClient("raspberrypi", data_received)
    logdata("Bluetooth Connected")
except:
    logdata("An Error happened while connecting to bluetooth")

def sendbluetoothdata(data):
    try:
        c.send(data)
        logdata(f"{data} sent to bluetooth")
    except:
        logdata(f"error happened while sending {data} to bluetooth")

############# Mission Code #############

def CheckDeployStatus(): # 위성이 분리되어있는지 판단하는 부분
    global DeployFlagCNT
    global SkycraneReleased
    print(f"DeployFlagCNT : {DeployFlagCNT}")
    if CurAccel >= DEPLOYED_ACCEL and SkycraneReleased == 0:
        if SkycraneReleased == 0:
            DeployFlagCNT += 1

    elif DeployFlagCNT > 1:
        DeployFlagCNT -= 2
    elif DeployFlagCNT == 1:
        DeployFlagCNT -= 1

    if DeployFlagCNT >= 5: # 0.1 초마다 한번 /// 1초 연속으로 아래로 가속될경우 // Deploy 된 상태라고 가정
        SkycraneReleased = 1
        logdata("Cansat Deployed, Releasing Skycrane")
        sendbluetoothdata("0") # 위쪽 모듈에 0이라는 데이터 전송

def CheckSkycraneActivate(): # SkyCrane이 작동하는지 판단하는 부분
    global SkycraneCNT
    global SkycraneReleased
    global SkycraneActivated
    if CurLiDARDistance < SKYCRANE_ACTIVATE_HEIGHT and SkycraneReleased == 1 and SkycraneActivated == 0 and CurLiDARDistance >= 20: # 라이더 고도 제한 추가
        SkycraneCNT += 1
    elif SkycraneCNT > 1:
        SkycraneCNT -= 2
    elif SkycraneCNT == 1:
        SkycraneCNT -= 1

    if SkycraneCNT >= 5: # 0.25초동안 LiDAR 센서 거리가 임계값보다 작아질경우
        SkycraneActivated = 1
        logdata("Skycrane Activated")
        sendbluetoothdata("1") # 위쪽 모듈에 1이라는 데이터 전송

############ Serial Communication #############

ser = serial.Serial("/dev/serial0", 9600) # 지상국과의 통신을 위해 Serial port 지정

packet = {"MSG_ID":None,
          "SEQ":None,
          "Length":None,
          "Timestamp":None,
          "Module_Stat":None,

          "BerryIMU_Accel":(0, 0, 0), # (x,y,z) .. m/s^2
          "BerryIMU_Gyro":(0, 0, 0), # (x,y,z) .. degrees

          "Temperature" : None,
          "Pressure" : None, # atm
          "Altitiude": None,

          "GpsPos" : (0, 0, 0), # (lat, lon, alt) ... degrees
          "GpsEtc" : (None, None, None, None, None), # {time},{epv},{ept},{speed},{climb}

          "LiDAR_Dist":None, # (dist) .. cm

          "Packet_Count":1,
          }

def addpacketdata(moduleno, data):
    global CurAccel
    global CurLiDARDistance

    if moduleno == 1: # BerryGPS_IMU Accel, Gyro 의 경우
        # BerryGPS 데이터는 ,(콤마) 를 기준으로 6개의 데이터가 들어옴
        # 데이터 형식 >>> 가속도X,가속도Y,가속도Z,자이로X,자이로Y,자이로Z
        splitdata = data.split(',')
        packet['BerryIMU_Accel'] = (float(splitdata[0]), float(splitdata[1]), float(splitdata[2]))
        packet['BerryIMU_Gyro'] = (float(splitdata[3]), float(splitdata[4]), float(splitdata[5]))
        CurAccel = float(splitdata[2])
        CheckDeployStatus()

    if moduleno == 2: # BerryGPS_IMU Barometer의 경우
        splitdata = data.split(',')
        packet["Temperature"] = float(splitdata[0])
        packet["Pressure"] = float(splitdata[1])
        packet["Altitiude"] = float(splitdata[2])

    if moduleno == 3: # BerryGPS_IMU GPS의 경우
        splitdata = data.split(',')
        packet["GpsPos"] = (float(splitdata[0]), float(splitdata[1]), float(splitdata[2]))
        packet["GpsEtc"] = (splitdata[3], splitdata[4], splitdata[5], splitdata[6], splitdata[7])
        MAXHeight = max(MAXHeight, splitdata[2]) # 현재까지의 최대 고도를 측정, 만약 GPS 고도 데이터가 정확하지 않다면 기압고도계를 사용할 것

    if moduleno == 4: # LiDAR 센서의 경우
        packet['LiDAR_Dist'] = int(data)
        CurLiDARDistance = int(data) # 현재 라이다 센서에 잡히는 거리
        CheckSkycraneActivate()

def sendpacket(): # 패킷을 보내는 코드
    while True:
        packet['Module_Stat'] = ''
        for i in module_active:
            packet['Module_Stat'] += str(i)
        curtime = datetime.now().isoformat(sep=' ', timespec='milliseconds')
        #sendstr = f"/*{packet['Packet_Count']},{curtime},{packet['Module_Stat']},{packet['LiDAR_Dist']}*/" # 지상국에 보낼 메세지
        sendstr = "/*" # 지상국 데이터 시작 표시
        sendstr += f"{packet['Packet_Count']},{curtime},{packet['Module_Stat']}," # 지상국 기본 데이터 추가
        sendstr += f"{packet['BerryIMU_Accel'][0]},{packet['BerryIMU_Accel'][1]},{packet['BerryIMU_Accel'][2]}," # BerryGPS Accel 값 추가
        sendstr += f"{packet['BerryIMU_Gyro'][0]},{packet['BerryIMU_Gyro'][1]},{packet['BerryIMU_Gyro'][2]}," # BerryGPS Gyro 값 추가
        sendstr += f"{packet['Temperature']},{packet['Pressure']},{packet['Altitiude']}," # BerryGPS Baro 값 추가
        sendstr += f"{packet['GpsPos'][0]},{packet['GpsPos'][1]},{packet['GpsPos'][2]},"
        sendstr += f"{packet['GpsEtc'][0]},{packet['GpsEtc'][1]},{packet['GpsEtc'][2]},{packet['GpsEtc'][3]},{packet['GpsEtc'][4]},"
        sendstr += f"{packet['LiDAR_Dist']}," # 라이다 센서 데이터 추가
        sendstr += f"{SkycraneReleased},{SkycraneActivated}" # 스카이크래인이 작동했는지 확인
        sendstr += "*/" # 지상국 데이터 끝 표시
        logdata(sendstr)
        packet['Packet_Count'] += 1

        ser.write(sendstr.encode()) # 지상국에 serial 보내기

        time.sleep(PACKET_SEND_PERIOD) # 패킷을 보내는 주기

##################################################

def threaded(client_socket, addr):
    logdata(f'>> Connected by : {addr[0]} : {addr[1]}')
    moduleno=int(client_socket.recv(1024).decode()) # 모듈과 연결된 후 첫 데이터는 1자리 숫자이고, 그 숫자는 각 모듈의 고유 번호임
    module_active[moduleno] = 1 # 그 모듈이 연결되었음을 표시
    logdata(f'module number {moduleno} is active!')

    # 클라이언트가 접속을 끊을 때 까지 반복합니다.
    while True:
        try:
            # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
            data = client_socket.recv(1024)

            if not data:
                logdata(f'>> Disconnected by {addr[0]} : {addr[1]}')
                module_active[moduleno] = 0 # 그 모듈의 연결이 끊겼음을 표시
                break

            #logdata(f'>> Received from  + {addr[0]} : {addr[1]}, {data.decode()}')
            addpacketdata(int(data.decode()[0]), data.decode()[1:])


            ############# Cansat Mission Status check #############
            # Climb 값이 계속 음수면 낙하 상태라고 판단, LiDAR 줄 내리기, Flag 키기
            # 그 후 LiDAR 데이터가 일정 거리 이내로 들어오면 SkyCrane 작동
            # Uppermodule과는 Bluetooth로 통신



            ##########################################
            # 서버에 접속한 클라이언트들에게 채팅 보내기
            # 메세지를 보낸 본인을 제외한 서버에 접속한 클라이언트에게 메세지 보내기
            for client in client_sockets :
                if client != client_socket :
                    client.send(data)

        except ConnectionResetError as e:
            logdata(f'>> Disconnected by {addr[0]} : {addr[1]}')
            module_active[moduleno] = 0 # 그 모듈의 연결이 끊겼음을 표시
            break

    if client_socket in client_sockets :
        client_sockets.remove(client_socket)
        logdata(f'remove client list : {len(client_sockets)}')

    client_socket.close()

client_sockets = [] # 서버에 접속한 클라이언트 목록

# 서버 IP 및 열어줄 포트


# 서버 소켓 생성
logdata('>> Server Start')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

try:
    start_new_thread(sendpacket, ())
    while True:
        logdata('>> Wait')

        client_socket, addr = server_socket.accept()
        client_sockets.append(client_socket)
        start_new_thread(threaded, (client_socket, addr))
        logdata(f"참가자 수 : {len(client_sockets)}")

except Exception as e :
    logdata (f'에러는? : {e}')

finally:
    server_socket.close()
    c.disconnect()

# 쓰레드에서 실행되는 코드입니다.
# 접속한 클라이언트마다 새로운 쓰레드가 생성되어 통신을 하게 됩니다.
