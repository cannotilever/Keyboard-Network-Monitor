#!/usr/bin/python3
import os
import psutil
import socket
import time
import pickle
time.sleep(8) #wait for operating system to initialize networking before registering socket
HOST = socket.gethostbyaddr(socket.gethostname())[2][0]
PORT = 65432
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
while True:
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            else:
                if data == b'status':
                    toSend = [psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent]
                    sendData = pickle.dumps(toSend)
                    conn.send(sendData)
                elif data == b'reboot':
                    conn.send(b'ok')
                    print("Got Reboot Command")
                    time.sleep(0.2)
                    os.system("reboot")
                elif data == b'poweroff':
                    conn.send(b'ok')
                    print("Got Poweroff Command")
                    time.sleep(0.2)
                    os.system("poweroff")