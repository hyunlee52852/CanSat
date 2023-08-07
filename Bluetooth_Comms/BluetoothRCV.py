irom bluetooth import *

port = 3
socket = BluetoothSocket(RFCOMM)
socket.connect(("98:D3:51:FD:E4:0C", port))
print("bluetooth connected!")

try:
    while True:
        data = socket.recv(1024)
        print(f"Received : {data}")
except KeyboardInterrupt:
    print("finished")
    socket.close()
