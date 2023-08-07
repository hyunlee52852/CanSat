irom bluetooth import *

port = 3
socket = BluetoothSocket(RFCOMM)
socket.connect(("B8:27:EB:C1:D4:9C", port))
print("bluetooth connected!")

try:
    while True:
        data = socket.recv(1024)
        print(f"Received : {data}")
except KeyboardInterrupt:
    print("finished")
    socket.close()
