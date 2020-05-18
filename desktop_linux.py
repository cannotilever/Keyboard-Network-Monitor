#!/usr/bin/python3
import os
import time
import keyboard
import socket
import pickle
import psutil
import yaml
from requests import get
config = yaml.load(open('desktop_config.yaml', 'r'), Loader=yaml.FullLoader)
yes = config['colors']['yes']
no = config['colors']['no']
black = config['colors']['black']
default = config['colors']['default']
CPUcolor = config['colors']['CPUcolor']
RAMcolor = config['colors']['RAMcolor']
DSKcolor = config['colors']['DSKcolor']
shutdownColor = config['colors']['shutdownColor']
rebootColor = config['colors']['rebootColor']
armKcolor = config['colors']['armKcolor']
pointNames = list(config['hosts'].keys())
focus = 0 #default focus, no host selected
loops = 0
running = True
doUpdate = False
doClear = False
armLights = True
armed = False
armedCD = 0
points = []
linux = 1
windows = 1
local = 2
other = 0
WAN = get('https://api.ipify.org').text
cpuKeys = {10.0:'q', 20.0:'w', 30.0:'e', 40.0:'r', 50.0:'t', 60.0:'y', 70.0:'u', 80.0:'i', 90.0:'o', 100.0:'p'}
ramKeys = {10.0:'a', 20.0:'s', 30.0:'d', 40.0:'f', 50.0:'g', 60.0:'h', 70.0:'j', 80.0:'k', 90.0:'l', 100.0:'semicolon'}
dskKeys = {10.0:'z', 20.0:'x', 30.0:'c', 40.0:'v', 50.0:'b', 60.0:'n', 70.0:'m', 80.0:'comma', 90.0:'period', 100.0:'slash'}
armKeys = [1,3,7,9]
pingTimer = statTimer = time.time()
PMerrors = 0
class point:
	def __init__(self):
		self.name = GetAttribute('name')
		if self.name is not None:
			self.address = GetAttribute('address', self.name)
			if self.address == 'WAN': self.address = WAN
			self.key = GetAttribute('key', self.name)
			self.statType = GetAttribute('type', self.name)
			self.online = no
			self.doConnect = False
			points.append(self)
			keyboard.add_hotkey('shift+{0}'.format(self.key), setFocus, args=[self])
	def check(self):
		a = 1
		a = os.system("ping -c 1 -W 1 {0} > /dev/null".format(self.address))
		if a == 0: self.online = yes
		else: self.online = no
		os.system("g810-led -k {0} {1}".format(self.key, self.online))
	def connect(self):
		global s
		self.doConnect = False
		HOST = self.address
		PORT = 65432
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		try: s.connect((HOST, PORT))
		except(ConnectionRefusedError, OSError):
			errFlash()
			print("Cannot Connect to remote host!")
			return 1
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
			if i <= Wcpu:
				os.system('g810-led -k {0} {1}'.format(cpuKeys[i], CPUcolor))
			elif i > Wcpu:
				os.system('g810-led -k {0} {1}'.format(cpuKeys[i], black))
		Wram = w[1] #get usage from list
		Wram = round(Wram, -1) #find the ram usage to nearest 10
		for i in ramKeys:
			if i <= Wram:
				os.system('g810-led -k {0} {1}'.format(ramKeys[i], RAMcolor))
			elif i > Wram:
				os.system('g810-led -k {0} {1}'.format(ramKeys[i], black))
		Wdsk = w[2] #get usage from list
		Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
		for i in dskKeys:
			if i <= Wdsk:
				os.system('g810-led -k {0} {1}'.format(dskKeys[i], DSKcolor))
			elif i > Wdsk:
				os.system('g810-led -k {0} {1}'.format(dskKeys[i], black))
def errFlash():
	for i in range (0, 4):
		os.system("g810-led -g keys {0}".format(no))
		time.sleep(0.25)
		os.system("g810-led -g keys {0}".format(black))
		time.sleep(0.25)
	os.system("g810-led -g keys {0}".format(default))
def setFocus(what):
	global focus, doUpdate, doClear
	if what == 0:
		doClear = True
		doUpdate = False
		try:
			s.close()
		except(NameError):
			print("Kill Socket failed!")
			pass
	else:
		if what.statType == other or what.online == no:
			errFlash()
			focus = 0
			doUpdate = False
		else:
			focus = what
			focus.doConnect = True
			doUpdate = True
def GetAttribute(request, name = None):
	if request == 'name':
		if pointNames == []: return None
		else:
			temp = pointNames[0]
			pointNames.remove(temp)
	else: temp = config['hosts'][name][request]
	return temp
def ClearBoard():
	global loops
	global doClear
	os.system('g810-led -g keys {0}'.format(default))
	for i in ['num5', 'home', 'end']:
		os.system('g810-led -k {0} {1}'.format(i, default))
	for i in armKeys:
		os.system('g810-led -k num{0} {1}'.format(i, default))
	loops += 1
	if loops >= 2:
		loops = 0
		doClear = False
		os.system("g810-led -g keys {0}".format(default))
def localDetails():
	w = [psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent]
	Wcpu = w[0] #get usage from list
	Wcpu = round(Wcpu, -1) #find the cpu usage to nearest 10
	for i in cpuKeys:
		if i <= Wcpu:
			os.system('g810-led -k {0} {1}'.format(cpuKeys[i], CPUcolor))
		elif i > Wcpu:
			os.system('g810-led -k {0} {1}'.format(cpuKeys[i], black))
	Wram = w[1] #get usage from list
	Wram = round(Wram, -1) #find the ram usage to nearest 10
	for i in ramKeys:
		if i <= Wram:
			os.system('g810-led -k {0} {1}'.format(ramKeys[i], RAMcolor))
		elif i > Wram:
			os.system('g810-led -k {0} {1}'.format(ramKeys[i], black))
	Wdsk = w[2] #get usage from list
	Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
	for i in dskKeys:
		if i <= Wdsk:
			os.system('g810-led -k {0} {1}'.format(dskKeys[i], DSKcolor))
		elif i > Wdsk:
			os.system('g810-led -k {0} {1}'.format(dskKeys[i], black))
def powerKeys():
	global loops, armLights
	if armed:
		armLights = not armLights
		os.system('g810-led -k home {0}'.format(rebootColor))
		os.system('g810-led -k end {0}'.format(shutdownColor))
		if armLights:
			for i in armKeys:
				os.system('g810-led -k num{0} {1}'.format(i, armKcolor))
		else:
			for i in armKeys:
				os.system('g810-led -k num{0} {1}'.format(i, black))
			loops = 0
	else:
		os.system('g810-led -k home {0}'.format(black))
		os.system('g810-led -k end {0}'.format(black))
		os.system('g810-led -k num5 {0}'.format(armKcolor))
		for i in armKeys:
			os.system('g810-led -k num{0} {1}'.format(i, black))
def arm():
	global armed, armedCD
	armed = True
	armedCD = 200
def leave():
	global focus, running
	ClearBoard()
	focus = 0
	running = False
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
				PMerrors = 0
			else:
				focus.connect()
				time.sleep(0.1)
				PowerMan(kind)
	if focus.statType == local:
		if kind == b'reboot': os.system('reboot')
		if kind == b'poweroff': os.system('poweroff')
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
s0 = point()
s1 = point()
s2 = point()
s3 = point()
s4 = point()
s5 = point()
s6 = point()
s7 = point()
s8 = point()
s9 = point()
s10 = point()
s11 = point()
s12 = point()
s13 = point()
s14 = point()
s15 = point()
keyboard.add_hotkey('esc', setFocus, args=[0])
os.system("g810-led -a {0}".format(default))
keyboard.add_hotkey('ctrl+home', PowerMan, args=[b'reboot'])
keyboard.add_hotkey('ctrl+end', PowerMan, args=[b'poweroff'])
keyboard.add_hotkey('ctrl+esc+q', leave)
keyboard.add_hotkey('ctrl+num 5', arm)
if not points:
	print("Error: No servers have been configured. Abort.")
	exit()
while running:
	time.sleep(0.01)
	PingCheck()
	viewStats()
	if armed: armedCD -=1
	if armedCD <= 0: armed = False
	if doClear: ClearBoard()
