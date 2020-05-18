print("--Welcome to the Keyboard Network Monitor--")
print("This window will automatically minimize, but you can refer to it for troubleshooting")
import os
import time
import keyboard
import socket
import pickle
import psutil
import pygetwindow as gw
from logipy import logi_led as logi
logi.logi_led_init()
time.sleep(0.5)
selfWindow = gw.getActiveWindow()
selfWindow.minimize()
#---Begin Color Definitions---
yes = 0,100,0
no = 100,0,0
black = 0,0,0
default = 0,12,100
CPUcolor = 99,53,1
RAMcolor = 91,99,1
DSKcolor = 90,0,100
shutdownColor = 100,0,0
rebootColor = 100,42,0
armKcolor = 100,0,0
#---End Color Definitions---
focus = 0 #default focus, no host selected
loops = 0
doUpdate = False
armLights = True
armed = False
doClear = False
armedCD = 0
points = []
linux = 1
windows = 1
local = 2
other = 3
cpuKeys = {10.0:16, 20.0:17, 30.0:18, 40.0:19, 50.0:20, 60.0:21, 70.0:22, 80.0:23, 90.0:24, 100.0:25}
ramKeys = {10.0:30, 20.0:31, 30.0:32, 40.0:33, 50.0:34, 60.0:35, 70.0:36, 80.0:37, 90.0:38, 100.0:39}
dskKeys = {10.0:44, 20.0:45, 30.0:46, 40.0:47, 50.0:48, 60.0:49, 70.0:50, 80.0:51, 90.0:52, 100.0:53}
pingTimer = statTimer = time.time()
armKeys = [79,81,71,73]
PMerrors = 0
class point:
	def __init__(self, name, address, key, statType):
		self.name = name
		self.address = address
		self.key = key
		self.statType = statType
		self.online = no
		self.doConnect = False
		points.append(self)
		keyboard.add_hotkey('shift+{0}'.format(self.key), setFocus, args=[self])
	def check(self):
		a = 1
		a = os.system('ping -n 1 -w 1000 {0} > NUL'.format(self.address))
		if a == 0: self.online = yes
		else:
			self.online = no
			print("Detected that {0} is offline!".format(self.name))
		logi.logi_led_set_lighting_for_key_with_key_name(keytoInt(self.key), self.online[0],self.online[1],self.online[2])
	def connect(self):
		global s
		self.doConnect = False
		HOST = self.address
		PORT = 65432
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try: s.connect((HOST, PORT))
		except(ConnectionRefusedError, OSError):
			errFlash()
			print("Cannot Connect to remote host!")
	def details(self):
		global s, doUpdate
		try:
			s.sendall(b'status')
			data = s.recv(2048)
		except(OSError):
			doUpdate = False
			return None
		try:
			w = pickle.loads(data)
		except(pickle.UnpicklingError, EOFError):
			print("can't Read Data!")
			errFlash()
			return None
		Wcpu = w[0] #get usage from list
		Wcpu = round(Wcpu, -1) #find the cpu usage to nearest 10
		for i in cpuKeys:
			if i <= Wcpu: logi.logi_led_set_lighting_for_key_with_key_name(cpuKeys[i],CPUcolor[0],CPUcolor[1],CPUcolor[2])
			elif i > Wcpu: logi.logi_led_set_lighting_for_key_with_key_name(cpuKeys[i],black[0],black[1],black[2])
		Wram = w[1] #get usage from list
		Wram = round(Wram, -1) #find the ram usage to nearest 10
		for i in ramKeys:
			if i <= Wram: logi.logi_led_set_lighting_for_key_with_key_name(ramKeys[i],RAMcolor[0],RAMcolor[1],RAMcolor[2])
			elif i > Wram: logi.logi_led_set_lighting_for_key_with_key_name(ramKeys[i],black[0],black[1],black[2])
		Wdsk = w[2] #get usage from list
		Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
		for i in dskKeys:
			if i <= Wdsk: logi.logi_led_set_lighting_for_key_with_key_name(dskKeys[i],DSKcolor[0],DSKcolor[1],DSKcolor[2])
			elif i > Wdsk: logi.logi_led_set_lighting_for_key_with_key_name(dskKeys[i],black[0],black[1],black[2])
def errFlash():
	logi.logi_led_flash_lighting(no[0],no[1],no[2],2000,250)
	ClearBoard()
def setFocus(what):
	global focus, doUpdate
	if what == 0:
		ClearBoard()
		doUpdate = False
		try:
			s.close()
		except(NameError):
			print("Kill Socket failed!")
			pass
	else:
		if what.statType == other or what.online == no:
			print('This host is either offline or is set to "other" in the config file')
			errFlash()
			focus = 0
			doUpdate = False
		else:
			focus = what
			focus.doConnect = True
			doUpdate = True
def ClearBoard():
	global loops, doClear
	logi.logi_led_set_lighting(default[0],default[1],default[2])
	loops += 1
	if loops == 5:
		logi.logi_led_set_lighting(default[0],default[1],default[2])
	if loops == 10:
		logi.logi_led_set_lighting(default[0],default[1],default[2])
		doClear = False
		loops = 0
def localDetails():
	w = [psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent]
	Wcpu = w[0] #get usage from list
	Wcpu = round(Wcpu, -1) #find the cpu usage to nearest 10
	for i in cpuKeys:
		if i <= Wcpu: logi.logi_led_set_lighting_for_key_with_key_name(cpuKeys[i],CPUcolor[0],CPUcolor[1],CPUcolor[2])
		elif i > Wcpu: logi.logi_led_set_lighting_for_key_with_key_name(cpuKeys[i],black[0],black[1],black[2])
	Wram = w[1] #get usage from list
	Wram = round(Wram, -1) #find the ram usage to nearest 10
	for i in ramKeys:
		if i <= Wram: logi.logi_led_set_lighting_for_key_with_key_name(ramKeys[i],RAMcolor[0],RAMcolor[1],RAMcolor[2])
		elif i > Wram: logi.logi_led_set_lighting_for_key_with_key_name(ramKeys[i],black[0],black[1],black[2])
	Wdsk = w[2] #get usage from list
	Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
	for i in dskKeys:
		if i <= Wdsk: logi.logi_led_set_lighting_for_key_with_key_name(dskKeys[i],DSKcolor[0],DSKcolor[1],DSKcolor[2])
		elif i > Wdsk: logi.logi_led_set_lighting_for_key_with_key_name(dskKeys[i],black[0],black[1],black[2])
def powerKeys():
	global armLights
	if armed:
		armLights = not armLights
		logi.logi_led_set_lighting_for_key_with_key_name(327,rebootColor[0],rebootColor[1],rebootColor[2])
		logi.logi_led_set_lighting_for_key_with_key_name(335,shutdownColor[0],shutdownColor[1],shutdownColor[2])
		if armLights:
			for i in armKeys:
				logi.logi_led_set_lighting_for_key_with_key_name(i,armKcolor[0],armKcolor[1],armKcolor[2])
		else:
			for i in armKeys:
				logi.logi_led_set_lighting_for_key_with_key_name(i,black[0],black[1],black[2])
	else:
		logi.logi_led_set_lighting_for_key_with_key_name(327,black[0],black[1],black[2])
		logi.logi_led_set_lighting_for_key_with_key_name(335,black[0],black[1],black[2])
		logi.logi_led_set_lighting_for_key_with_key_name(76,armKcolor[0],armKcolor[1],armKcolor[2])
		for i in armKeys:
			logi.logi_led_set_lighting_for_key_with_key_name(i,black[0],black[1],black[2])
def keytoInt(key):
    #I know this is ugly but whatever
    if key.lower() == 'esc': return 1
    if key.lower() == 'f1': return 59
    if key.lower() == 'f2': return 60
    if key.lower() == 'f3': return 61
    if key.lower() == 'f4': return 62
    if key.lower() == 'f5': return 63
    if key.lower() == 'f6': return 64
    if key.lower() == 'f7': return 65
    if key.lower() == 'f8': return 66
    if key.lower() == 'f9': return 67
    if key.lower() == 'f10': return 68
    if key.lower() == 'f11': return 87
    if key.lower() == 'f12': return 88
def arm():
	global armed, armedCD
	armed = True
	armedCD = 100
def PowerMan(kind):
	global PMerrors
	if focus == 0 or focus.statType == other or not armed:
		print("invalid.")
	elif focus.statType == 1: #assumes socket is establised
		try:
			s.sendall(kind)
			s.close()
			setFocus(0)
		except(NameError): #if socket fails, establish it again and try again
			PMerrors += 1
			if PMerrors >= 5:
				errFlash()
				print("Socket keeps failing, bad connection?")
				PMerrors = 0
			else:
				focus.connect()
				time.sleep(0.1)
				PowerMan(kind)
	if focus.statType == local:
		if kind == b'reboot': os.system('shutdown /r')
		if kind == b'poweroff': os.system('shutdown /s')
def PingCheck(): #only pings every 2 seconds
	global pingTimer
	if time.time() - pingTimer >= 2:
		for i in points:
			viewStats()
			i.check()
			pingTimer = time.time()
def viewStats(): #updates stats every quarter second
	global statTimer
	if doUpdate and (time.time() - statTimer >= 0.25):
		powerKeys()
		if focus.doConnect and focus.statType == 1: focus.connect()
		if focus.statType == 1: focus.details()
		else: localDetails()
		statTimer = time.time()
#----------Start Point Definitions----------
localhost = point('localhost', socket.gethostbyaddr(socket.gethostname())[2][0], 'esc', local)  
SamplePoint0 = point('Sample linux server', '192.168.1.10', 'f1', linux)
SamplePoint1 = point('Sample linux server 2', '192.168.1.11', 'f2', linux)
SampleOtherPoint = point('Sample other server', '192.168.1.12', 'f3', other) 							
cloudflare = point("cloudflare", 'www.cloudflare.com', 'f10', other) #other means that the host cannot be monitored							
aws = point("Amazon Web Service", 'aws.amazon.com', 'f11', other)								
google = point("Google", 'google.com', 'f12', other)											
#----------End Point Definitions----------
keyboard.add_hotkey('esc', setFocus, args=[0])
logi.logi_led_set_lighting(default[0],default[1],default[2])
keyboard.add_hotkey('ctrl+home', PowerMan, args=[b'reboot'])
keyboard.add_hotkey('ctrl+end', PowerMan, args=[b'poweroff'])
keyboard.add_hotkey('ctrl+num 5', arm)
while True:
	time.sleep(0.05)
	PingCheck()
	viewStats()
	if armed: armedCD -=1
	if armedCD <= 0: armed = False
	if doClear: ClearBoard()