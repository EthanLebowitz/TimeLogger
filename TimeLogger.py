import pip

try:
	__import__("keyboard")
except ImportError:
	pip.main(["install", "keyboard"])
	
import keyboard
import time
from datetime import datetime
import os
from os.path import exists
import sys
import threading


def convertTimeToReadable(sec): # from https://www.journaldev.com/44690/python-convert-time-hours-minutes-seconds
   #sec = sec % (24 * 3600)
   hour = sec // 3600
   sec %= 3600
   min = sec // 60
   sec %= 60
   return "%02d:%02d:%02d" % (hour, min, sec) 

class InputOutput:
	
	def __init__(self):
		self.createConfig()
		self.logFileName = ""
	
	def createConfig(self):
		text = "# if the hotkey variable is left empty the program will prompt you for a hotkey when\n# opened next and will store it.\nhotkey="
		if not exists("config.txt"):
			f = open("config.txt", "w")
			f.write(text)
			f.close()
			
	def setHotkeyInConfig(self, hotkey):
		config = open("config.txt", "r")
		lines = config.readlines()
		config.close()
		config = open("config.txt", "w")
		for lineIndex in range(len(lines)):
			line = lines[lineIndex]
			if line.split("=")[0]=="hotkey":
				lines[lineIndex] = "hotkey="+hotkey
		config.writelines(lines)
		config.close()

	def getHotkey(self):
		config = open("config.txt", "r")
		hotkey = ""
		for line in config:
			if not line[0] == "#":
				splitLine = line.rstrip().split("=")
				if splitLine[0] == "hotkey":
					if splitLine[1] != "":
						hotkey = splitLine[1]
						print("hotkey = " + hotkey)
					else:
						print("Press the key you would like to use for your hotkey")
						hotkey = keyboard.read_key(suppress=False)
						print("'" + hotkey + "' selected")
						setHotkeyInConfig(hotkey)
		config.close()
		return hotkey

	def createLogFile(self):
		try:
			os.mkdir("logs")
		except:
			pass
		now = datetime.now()
		dateString = now.strftime("%Y-%m-%d-%H-%M-%S")
		fileName = "logs/"+dateString+".txt"
		logFile = open(fileName, "a")
		logFile.write("Timer began at " + now.strftime("%H:%M:%S") + " on " + now.strftime("%d/%m/%Y") + "\n")
		logFile.close()
		return fileName
		
	def notifyTimerBegin(self, startNow):
		print("Timer began at " + startNow.strftime("%H:%M:%S") + " on " + startNow.strftime("%d/%m/%Y") + "\n")
		self.logFileName = self.createLogFile()
		
	def notifyHotkeyPressed(self, readableTime):
		logFile = open(self.logFileName, "a")
		logFile.write(readableTime+"\n")
		logFile.close()
		sys.stdout.write("\r")
		sys.stdout.write("Logged:       " + readableTime + "\n")
		sys.stdout.flush()

class Timer:
	
	def __init__(self):
		self.timerBegan = False
		self.startNow = None
		self.startTime = None
	
	def displayTimer(self):
		while True:
			self.displayTimeElapsed()
			time.sleep(.2)
			
	def begin(self):
		self.startNow = datetime.now()
		self.startTime = time.time()
		self.timerBegan = True
		timerDisplayThread = threading.Thread(target=self.displayTimer)
		timerDisplayThread.start()
		
	def getTimerBegan(self):
		return self.timerBegan
		
	def getTimeElapsed(self):
		return time.time() - self.startTime
		
	def displayTimeElapsed(self):
		timeElapsedSeconds = time.time() - self.startTime
		readableTime = convertTimeToReadable(timeElapsedSeconds)
		sys.stdout.write("\r")
		sys.stdout.write("Time elapsed: " + readableTime)
		sys.stdout.flush()

class Main:
	
	def __init__(self):
		self.io = InputOutput()
		self.timer = Timer()
		
		self.hotkey = self.io.getHotkey()
		self.timerBegan = False
		keyboard.add_hotkey(self.hotkey, self.callback)
		print("Press your hotkey to begin the timer")
		

	def callback(self):
		if self.timer.getTimerBegan():
			timeElapsedSeconds = self.timer.getTimeElapsed()
			readableTime = convertTimeToReadable(timeElapsedSeconds)
			self.io.notifyHotkeyPressed(readableTime)
		else:
			self.beginTimer()

	def beginTimer(self):
		now = datetime.now()
		self.io.notifyTimerBegin(now)
		self.timer.begin()


Main()
keyboard.wait()
