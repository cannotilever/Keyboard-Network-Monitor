#!/usr/bin/python3
import os
import psutil
import socket
import time
import pickle
import platform
import yaml
osType = platform.system()
confFile = 'server_config.yaml' #not final config location
config = yaml.load(open(confFile, 'r'), Loader=yaml.FullLoader)
if osType != 'Windows' and os.geteuid() != 0:
	    print("Please execute this script with root!")
	    exit()
if config['interfaceConfig'] == 'all': HOST = '0.0.0.0'
elif config['interfaceConfig'] == 'auto': HOST = socket.gethostbyaddr(socket.gethostname())[2][0]
elif config['interfaceConfig'] == 'manual': HOST = config['manualAddress']
else: raise NameError("Bad Config File")
PORT = 65432
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(8)
s.bind((HOST, PORT))
while True:
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            try:
                data = conn.recv(2048)
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
                        if osType == 'Windows': os.system('shutdown /r')
                        if osType == 'Linux': os.system("reboot")
                        if osType == 'Darwin': os.system("shutdown -r now")
                    elif data == b'poweroff':
                        conn.send(b'ok')
                        print("Got Poweroff Command")
                        time.sleep(0.2)
                        if osType == 'Windows': os.system('shutdown /s')
                        if osType == 'Linux': os.system("poweroff")
                        if osType == 'Darwin': os.system("shutdown -h now")
            except(ConnectionResetError, BrokenPipeError):
                pass