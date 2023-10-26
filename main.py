# Proj Gyro
# The Prototype
# Version 2.0
# With a bunch of stuff

# Author:   Kalos Robinson-Frani
# Email:    st20218@howick.school.nz
# Date:     27/10/2023 @ 09:00


import keyboard
from inputs import get_gamepad
from time import sleep
from pythonosc import udp_client
import json
from datetime import datetime
import math
import threading



def title():
	titleArt = """
█▀█ █▀█ █▀█ ░░█   █▀▀ █▄█ █▀█ █▀█
█▀▀ █▀▄ █▄█ █▄█   █▄█ ░█░ █▀▄ █▄█
	V2 - Kalos Robinson-Frani
   The Ultimate Gyro Controller\n
"""
	print(titleArt)
	
xBoundary = [0,255] # the max value the processor will go up to
yBoundary = [0,255]
currentPos = [0,0]
defaultPos = [0,0]
simPos = [0.0,0.0]

boundaryStatus = 0

destIP = ""
destPort = ""
client = ""

heads = [] #124


def initiate():

	usrInput = int(input("1. ) Manual Config\n2. ) Config from file\n"))
	if usrInput == 1:
		addressSetup()
		headsSetup()
	elif usrInput == 2:
		importHandler("load")




def addressSetup():
	global destIP, destPort, client

	usrInput = int(input("Initiate Default Address (1)\n or Manual Address (2)\n"))
	if usrInput == 1:
		print("Default Setup\n")
		destIP = "192.168.0.69"
		destPort = 8000
	
	elif usrInput == 2:
		print("Manual Setup\n")
		destIP = str(input("Input Destination IP Address - (eg. 192.168.1.3)\n: "))
		destPort = int(input("Input Destination Port - (eg. 8000) \n: "))

	else:
		print("That was not an option\n\n")
		initiate()

	print(f"Destination IP: ({destIP}), Port: ({destPort})\n")
	client = udp_client.SimpleUDPClient(destIP, destPort)
	print("Initiation Complete\n\n")
		



def headsInterface(arg):
	if arg == "add":
		newHeads = input('Input new head/s (seperate with a comma for multiple heads, eg. "123,456,789")\n: ').split(",")
		for i in newHeads:
			if i in heads:
				print(f"Duplicate detected ({i}), bypassing\n")
			heads.append(i)
	if arg == 'remove':
		rmHeads = input('Input head/s you would like to remove (seperate with a comma for multiple heads, eg. "123,456,789")\n: ').split(",")
		for i in rmHeads:
			if i not in heads:
				print(f"Head not found ({i}), bypassing\n")
				continue
			heads.remove(i)

	if arg == 'updateDefaultPos':
		global defaultPos
		defaultPos = list(map(int, (input("Enter the new default position coordinates seperated by a comma (eg. 50,100)\n: ").split(','))))
		print(f"New default position set ({defaultPos})\n")


def headsSetup():
	print("Heads Interface\n")
	if not heads:
		print("No heads setup, setting up new heads\n")
		headsInterface('add')
		
	
	print("Established Head/s:")
	for i in heads:
		print(i)
	
	print('\n 0. Continue\n 1. Add Head/s\n 2. Remove Head/s\n 3. Update default position')
	usrInput = int(input('\n: '))
	if usrInput == 0:
		print("Head Setup Finished")
		main()
		pass
	elif usrInput == 1:
		headsInterface('add')

	elif usrInput == 2:
		headsInterface('remove')
	
	elif usrInput == 3:
		headsInterface('updateDefaultPos')
	else:
		print("Invalid option")
		
	headsSetup()
	


def importHandler(arg):
	
	if arg == "save":
		dataExport = {
			'saveDate': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
			'destIP': destIP,
			'destPort': destPort,
			'heads': heads,
			'defaultPos': defaultPos
		}
	
		with open((str(input("Filename\n: ")) + "_gyro_data_file_"+ datetime.now().strftime("%d%m%Y%H%M%S") + ".json"), "w") as exportFile:
			json.dump(dataExport, exportFile)

	if arg == "load":
		with open((str(input("Input File Name \n: "))), "r") as importFile:
			dataImport = json.loads(importFile)
			destIP = dataImport['destIP']
			destPort = dataImport['destPort']
			heads = dataImport['heads']
			defaultPos = dataImport['defaultPos']



def main():
	print("Program Ready\n \
	   test 	: Test program to test communication\n \
	   control	: Free control interface for the heads\n \
	   keyframe	: Map head movements for playback \n \
	   heads	: Edit head properties \n \
	   address	: Edit destination address \n\
	   save		: Save current configuration \n \
	   load		: Load configuration	\n \
	   help		: Shows this menu \n \
	   quit		: Exit program \n \
	   ")
	usrInput = str(input("Input Command \n: "))
	if usrInput == 'test':
		headControl('test')
	elif usrInput == 'control':
		headControl('control')
	elif usrInput == 'keyframe':
		headControl('keyframe')
	elif usrInput == 'heads':
		headsSetup()
	elif usrInput == 'address':
		addressSetup()
	elif usrInput == 'save':
		importHandler('save')
	elif usrInput == 'load':
		importHandler('load')
	elif usrInput == 'help':
		main()
	elif usrInput == 'quit':
		print('\nGoodbye :)')
		exit()
	else:
		print("Unknown command\n")

def headHandler(arg):
	global currentPos

	if arg == 'select':
		for i in heads:
			client.send_message("/rpc ", "\<01>,{}H".format(i))
	
	if arg == 'intensityMax':
		print('intensity 100')
		client.send_message("/rpc ", "\<05>,100,1H")

	if arg == 'intensityMin':
		print('intensity 0')
		client.send_message("/rpc ", "\<05>,0,1H")

	if arg == 'intensityHalf':
		print('intensity 50')
		client.send_message("/rpc ", "\<05>,50,1H")

	if arg == 'resetPos':
		client.send_message("/rpc ", "\<06>,4,{}H".format(defaultPos[0]))
		client.send_message("/rpc ", "\<06>,5,{}H".format(defaultPos[1]))
		currentPos = defaultPos
	if arg == 'updatePos':
		client.send_message("/rpc ", "\<06>,4,{}H".format(currentPos[0]))
		client.send_message("/rpc ", "\<06>,5,{}H".format(currentPos[1]))

	if arg =='colRed':
		client.send_message("/rpc ", "\<06>,4,{}H".format(currentPos[0]))
	
	if arg =='colBlue':
		client.send_message("/rpc ", "\<06>,4,{}H".format(currentPos[0]))
	
	if arg =='colGreen':
		client.send_message("/rpc ", "\<06>,4,{}H".format(currentPos[0]))

	if arg =='colWhite':
		client.send_message("/rpc ", "\<06>,4,{}H".format(currentPos[0]))
	
	if isinstance(arg, int):
		client.send_message("/rpc ", "\<05>,{},1H".format((arg*10)))
	
		

def posInterpreter(arg, mp=1):
	global xBoundary, yBoundary, currentPos, defaultPos, simPos, boundaryStatus
	simPos = currentPos

	if mp <= 0:
		if arg == "left":
			simPos[0] = simPos[0]+(mp*5)
		if arg == "right":
			simPos[0] = simPos[0]+(mp*5)
		if arg == "up":
			simPos[1] = simPos[1]+(mp*5)
		if arg == "down":
			simPos[1] = simPos[1]+(mp*5)
	if mp > 0:
		if arg == "left":
			simPos[0] += -5
		if arg == "right":
			simPos[0] += 5
		if arg == "up":
			simPos[1] += 5
		if arg == "down":
			simPos[1] += -5

	#print(simPos)
	currentPos = [round(num) for num in simPos]

	if currentPos[0] > xBoundary[1]:
		print("BOUNDARY REACHED")
		if boundaryStatus == 0:
			currentPos[0] = xBoundary[1]
		elif boundaryStatus == 1:
			currentPos[0] = xBoundary[0]

		
	if currentPos[0] < xBoundary[0]:
		print("DEBUG: BOUNDARY REACHED")
		if boundaryStatus == 0:
			currentPos[0] = xBoundary[0]
		elif boundaryStatus == 1:
			currentPos[0] = xBoundary[1]

	
	if currentPos[1] > yBoundary[1]:
		currentPos[1] = yBoundary[1]
	if currentPos[1] < yBoundary[0]:
		currentPos[1] = yBoundary[0]
	
	
	print(currentPos)


def headControl(arg):
	global boundaryStatus
	if arg == 'test':
		print("Initiating osc test\n WARNING: SETUP WILL FLASH\n")
		try:
			for i in range(4):
				print(f"Iteration {i+1}/4")
		
				client.send_message("/dbo", 0)
				sleep(0.5)
				client.send_message("/dbo", 1)
				sleep(0.5)
			client.send_message("/dbo", 1)

			print("Test finished, make adjustments as needed\n")

		except KeyboardInterrupt:
			print("Exiting test...\n")
		
	if arg == 'control':
		print("Initiating manual controls\nInput Control Commands\n")
		try:
			while True:
				usrInput = str(input(": "))
				if usrInput == '?' or usrInput == 'help':
					print('Command Help: \n\
		   sel		: Select head/s \n \
		   on		: Heads intensity to 100 \n \
		   off		: Heads intensity to 0 \n \
		   half		: Heads intensity to 50 \n \
		   reset	: Reset heads position \n \
		   update	: Update default heads position \n \
		   kb		: Initiate the keyboard listener \n \
		   gp		: Initiate the gamepad listener \n \
		   quit		: Quits \n \
		   					')
				elif usrInput == 'sel':
					headHandler('select')
					print(f"Heads ({heads}) Selected")
				elif usrInput == 'on':
					headHandler('intensityMax')
				elif usrInput == 'off':
					headHandler('intensityMin')
				elif usrInput == 'half':
					headHandler('intensityHalf')
				elif usrInput == 'reset':
					headHandler('resetPos')
				elif usrInput == 'update':
					headsInterface('updateDefaultPos')
				elif usrInput == 'quit':
					continue
				elif usrInput == 'kb':
					try:
						while True:
							keyboard.on_press_key("a", lambda _: posInterpreter("left"))
							keyboard.on_press_key("d", lambda _: posInterpreter("right"))
							keyboard.on_press_key("w", lambda _: posInterpreter("up"))
							keyboard.on_press_key("s", lambda _: posInterpreter("down"))
							
							keyboard.on_press_key("1", lambda _: headHandler(1))
							keyboard.on_press_key("2", lambda _: headHandler(2))
							keyboard.on_press_key("3", lambda _: headHandler(3))
							keyboard.on_press_key("4", lambda _: headHandler(4))
							keyboard.on_press_key("5", lambda _: headHandler(5))
							keyboard.on_press_key("6", lambda _: headHandler(6))
							keyboard.on_press_key("7", lambda _: headHandler(7))
							keyboard.on_press_key("8", lambda _: headHandler(8))
							keyboard.on_press_key("9", lambda _: headHandler(9))
							keyboard.on_press_key("0", lambda _: headHandler(0))

							keyboard.on_press_key("`", lambda _: headHandler(10))

							keyboard.on_press_key("/", lambda _: headHandler("resetPos"))

							while True:
								sleep(0.1)
								continue

					except KeyboardInterrupt:
						print("Exited to control menu:")
						pass
				elif usrInput == "gp":
					joy = XboxController()
					try:
						while True:
							joy.read()
							sleep(0.1)
					except KeyboardInterrupt:
						print("Exited to control menu:")
						pass

				elif usrInput == "bdy":
					if boundaryStatus == 0:
						boundaryStatus = 1
						print("Toggled boundary status - will reset")
					elif boundaryStatus == 1:
						boundaryStatus = 0
						print("Toggled boundary status - will NOT reset")


				
		except KeyboardInterrupt:
			print('Going back to main menu\n')
		



	main()

class XboxController(object):
	MAX_TRIG_VAL = math.pow(2, 8)
	MAX_JOY_VAL = math.pow(2, 15)

	def __init__(self):

		self.LeftJoystickY = 0
		self.LeftJoystickX = 0
		self.RightJoystickY = 0
		self.RightJoystickX = 0
		self.LeftTrigger = 0
		self.RightTrigger = 0
		self.LeftBumper = 0
		self.RightBumper = 0
		self.A = 0
		self.X = 0
		self.Y = 0
		self.B = 0
		self.LeftThumb = 0
		self.RightThumb = 0
		self.Back = 0
		self.Start = 0
		self.LeftDPad = 0
		self.RightDPad = 0
		self.UpDPad = 0
		self.DownDPad = 0

		self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
		self._monitor_thread.daemon = True
		self._monitor_thread.start()


	def read(self): # return the buttons/triggers that you care about in this methode
		x = self.LeftJoystickX
		y = self.LeftJoystickY

		if self.A:
			headHandler('intensityMax')
		if self.X:
			headHandler('intensityMin')

		

		if x > 0.2:
			posInterpreter("right", round(x, 1))
		if x < -0.2:
			posInterpreter("left", round(x, 1))
		if y > 0.2:
			posInterpreter("up", round(y, 1))
		if y < -0.2:
			posInterpreter("down", round(y, 1))

		


			


	def _monitor_controller(self):
		while True:
			events = get_gamepad()
			for event in events:
				if event.code == 'ABS_Y':
					self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_X':
					self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_RY':
					self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_RX':
					self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
				elif event.code == 'ABS_Z':
					self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
				elif event.code == 'ABS_RZ':
					self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
				elif event.code == 'BTN_TL':
					self.LeftBumper = event.state
				elif event.code == 'BTN_TR':
					self.RightBumper = event.state
				elif event.code == 'BTN_SOUTH':
					self.A = event.state
				elif event.code == 'BTN_NORTH':
					self.Y = event.state #previously switched with X
				elif event.code == 'BTN_WEST':
					self.X = event.state #previously switched with Y
				elif event.code == 'BTN_EAST':
					self.B = event.state
				elif event.code == 'BTN_THUMBL':
					self.LeftThumb = event.state
				elif event.code == 'BTN_THUMBR':
					self.RightThumb = event.state
				elif event.code == 'BTN_SELECT':
					self.Back = event.state
				elif event.code == 'BTN_START':
					self.Start = event.state
				elif event.code == 'BTN_TRIGGER_HAPPY1':
					self.LeftDPad = event.state
				elif event.code == 'BTN_TRIGGER_HAPPY2':
					self.RightDPad = event.state
				elif event.code == 'BTN_TRIGGER_HAPPY3':
					self.UpDPad = event.state
				elif event.code == 'BTN_TRIGGER_HAPPY4':
					self.DownDPad = event.state





if __name__ == "__main__":
	title()
	initiate()
