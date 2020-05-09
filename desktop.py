#!/usr/bin/python3
import os
import time
import platform
import keyboard
import socket
import pickle
import psutil
yes = "03fc0b"
no = "fc0303"
black = '000000'
default = "001eff"
focus = 0 #default focus, no host selected
loops = 0
doUpdate = False
doClear = False
armLights = True
armed = False
armedCD = 0
points = []
linux = 1
bsd = 1
local = 2
other = 3
cpuKeys = {10.0:'q', 20.0:'w', 30.0:'e', 40.0:'r', 50.0:'t', 60.0:'y', 70.0:'u', 80.0:'i', 90.0:'o', 100.0:'p'}
ramKeys = {10.0:'a', 20.0:'s', 30.0:'d', 40.0:'f', 50.0:'g', 60.0:'h', 70.0:'j', 80.0:'k', 90.0:'l', 100.0:'semicolon'}
dskKeys = {10.0:'z', 20.0:'x', 30.0:'c', 40.0:'v', 50.0:'b', 60.0:'n', 70.0:'m', 80.0:'comma', 90.0:'period', 100.0:'slash'}
armKeys = [1,3,7,9]
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
			if i <= Wcpu:
				os.system('g810-led -k {0} c20000'.format(cpuKeys[i]))
			elif i > Wcpu:
				os.system('g810-led -k {0} {1}'.format(cpuKeys[i], black))
		Wram = w[1] #get usage from list
		Wram = round(Wram, -1) #find the ram usage to nearest 10
		for i in ramKeys:
			if i <= Wram:
				os.system('g810-led -k {0} fce303'.format(ramKeys[i]))
			elif i > Wram:
				os.system('g810-led -k {0} {1}'.format(ramKeys[i], black))
		Wdsk = w[2] #get usage from list
		Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
		for i in dskKeys:
			if i <= Wdsk:
				os.system('g810-led -k {0} e600ff'.format(dskKeys[i]))
			elif i > Wdsk:
				os.system('g810-led -k {0} {1}'.format(dskKeys[i], black))
def errFlash():
	for i in range (0, 4):
		os.system("g810-led -g keys {0}".format(no))
		time.sleep(0.25)
		os.system("g810-led -g keys {0}".format(black))
		time.sleep(0.25)
	os.system("g810-led -g keys 001eff")
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
def ClearBoard():
	global loops
	global doClear
	os.system("g810-led -g keys 001eff")
	os.system('g810-led -k num5 001eff')
	os.system('g810-led -k home 001eff')
	os.system('g810-led -k end 001eff')
	for i in armKeys:
			os.system('g810-led -k num{0} 001eff'.format(i))
	loops += 1
	if loops >= 10:
		loops = 0
		doClear = False
		os.system("g810-led -g keys 001eff")
def localDetails():
	w = [psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent]
	Wcpu = w[0] #get usage from list
	Wcpu = round(Wcpu, -1) #find the cpu usage to nearest 10
	for i in cpuKeys:
		if i <= Wcpu:
			os.system('g810-led -k {0} c20000'.format(cpuKeys[i]))
		elif i > Wcpu:
			os.system('g810-led -k {0} {1}'.format(cpuKeys[i], black))
	Wram = w[1] #get usage from list
	Wram = round(Wram, -1) #find the ram usage to nearest 10
	for i in ramKeys:
		if i <= Wram:
			os.system('g810-led -k {0} fce303'.format(ramKeys[i]))
		elif i > Wram:
			os.system('g810-led -k {0} {1}'.format(ramKeys[i], black))
	Wdsk = w[2] #get usage from list
	Wdsk = round(Wdsk, -1) #find the disk usage to nearest 10
	for i in dskKeys:
		if i <= Wdsk:
			os.system('g810-led -k {0} e600ff'.format(dskKeys[i]))
		elif i > Wdsk:
			os.system('g810-led -k {0} {1}'.format(dskKeys[i], black))
def powerKeys():
	global loops, armLights
	if armed:
		armLights = not armLights
		os.system('g810-led -k home fc9d03')
		os.system('g810-led -k end fc0303')
		if armLights:
			for i in armKeys:
				os.system('g810-led -k num{0} ff0000'.format(i))
		else:
			for i in armKeys:
				os.system('g810-led -k num{0} 000000'.format(i))
			loops = 0
	else:
		os.system('g810-led -k home 000000')
		os.system('g810-led -k end 000000')
		os.system('g810-led -k num5 ff0000')
		for i in armKeys:
			os.system('g810-led -k num{0} 000000'.format(i))
def arm():
	global armed, armedCD
	armed = True
	armedCD = 20
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
#----------Start Point Definitions----------
localhost = point('localhost', socket.gethostbyaddr(socket.gethostname())[2][0], 'esc', local)  
SamplePoint0 = point('Sample linux server', '192.168.1.10', 'f1', linux)
SamplePoint1 = point('Sample bsd server', '192.168.1.11', 'f2', bsd)
SampleOtherPoint = point('Sample bsd server', '192.168.1.12', 'f3', other) #other means that the host cannot be monitored							
cloudflare = point("cloudflare", 'www.cloudflare.com', 'f10', other)							
aws = point("Amazon Web Service", 'aws.amazon.com', 'f11', other)								
google = point("Google", 'google.com', 'f12', other)											
#----------End Point Definitions----------
keyboard.add_hotkey('esc', setFocus, args=[0])
os.system("g810-led -a {0}".format(default))
keyboard.add_hotkey('ctrl+home', PowerMan, args=[b'reboot'])
keyboard.add_hotkey('ctrl+end', PowerMan, args=[b'poweroff'])
keyboard.add_hotkey('ctrl+num 5', arm)
while True:
	for i in points:
		i.check()
		time.sleep(0.01)
		if doUpdate:
			powerKeys()
			if focus.doConnect and focus.statType == 1: focus.connect()
			if focus.statType == 1: focus.details()
			else: localDetails()
		else: time.sleep(0.08)
		if doClear: ClearBoard()
		if armed: armedCD -=1
		if armedCD <= 0: armed = False