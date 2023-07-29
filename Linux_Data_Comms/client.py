import socket
from _thread import *

HOST = '127.0.0.1'
PORT = 9999
MODULENO = 0 ## 모듈 번호에 알맞게 바꾸기

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.send(f'{MODULENO}'.encode()) ## 통신이 성사되면 모듈 번호를 보낸다


# 서버로부터 메세지를 받는 메소드
# 스레드로 구동 시켜, 메세지를 보내는 코드와 별개로 작동하도록 처리

"""
def recv_data(client_socket) :
    while True :
        data = client_socket.recv(1024)

        print("recive : ",repr(data.decode()))


start_new_thread(recv_data, (client_socket,))
"""
# Client가 Main server에서 데이터를 받을 일이 있으면 사용

print (f'>> Module {MODULENO} Connected!')

# 보낼 메세지를 여기에 쓰면 된다.
while True:
    message = input('')
    if message == 'quit':
        close_data = message
        break

    client_socket.send(message.encode())


client_socket.close()
