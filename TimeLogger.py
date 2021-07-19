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

setWindowTitle("a")

def convertTimeToReadable(sec): 
	# from https://www.journaldev.com/44690/python-convert-time-hours-minutes-seconds
	hour = sec // 3600
	sec %= 3600
	min = sec // 60
	sec %= 60
	return "%02d:%02d:%02d" % (hour, min, sec) 
	
def isInt(string):
	
	try:
		int(string)
		return True
	except ValueError:
		return False

class InputOutput:
	# Class for dealing with all the input from the settings file and
	# output to log files and commandline interface.
	
	def __init__(self):
		
		self.settingsDefaults = {"hotkey":"ctrl+t", "display_timer":"true", "log_delay":"1"}
		if not exists("settings.txt"):
			self.createConfig()
		self.validateConfig()
	
	def validateConfig(self):
		# Checks if values for all settings can be found in the settings file. 
		# If not rewrite it to the default.
		
		rewriteNeeded = False
		for setting in self.settingsDefaults:
			value = self.getFromConfig(setting)
			if value == None:
				rewriteNeeded = True
				print("Settings file corrupt. Could not find " + setting + ".")
		if rewriteNeeded:
			print("Rewriting settings file to defaults.")
			self.createConfig()
		
	def createConfig(self):
		
		lines = ["# Hotkey can be set to a single key such as <t> or <shift>, or it\n",
				"# can be set to a combination such as <ctrl+shift+t>.\n",
				"hotkey="+self.settingsDefaults["hotkey"]+"\n\n",
				"# Program is prevented from logging two times within log_delay seconds\n",
				"# of eachother. This prevents log spam caused by holding down the hotkey.\n",
				"# Recommended value greater than 0.\n",
				"log_delay="+self.settingsDefaults["log_delay"]+"\n\n",
				"# Displays current time elapsed. Not tested accross platforms. Any value other\n",
				"display_timer="+self.settingsDefaults["display_timer"]
				]
				
		f = open("settings.txt", "w")
		f.writelines(lines)
		f.close()
			
	def setInConfig(self, setting, value):
		#Sets <setting> to <value> in the settings file.
		
		config = open("settings.txt", "r")
		lines = config.readlines()
		config.close()
		config = open("settings.txt", "w")
		for lineIndex in range(len(lines)):
			line = lines[lineIndex]
			if line.split("=")[0]==setting:
				lines[lineIndex] = setting+"="+value
		config.writelines(lines)
		config.close()
	
	def notifyInvalidHotkey(self):
		
		default = self.settingsDefaults["hotkey"]
		print("The hotkey setting is not set to a valid hotkey. Using default value "+default+".")
		
	def getDefaultSetting(self, setting):
		return self.settingsDefaults[setting]
	
	def getSetting(self, setting):
		# Returns the value of <setting> after retrieving it from the settings file.
		# Checks for blank values and invalid log_delay values.
		
		value = self.getFromConfig(setting)
		default = self.settingsDefaults[setting]
		if value == "":
			value = default
			print("Value for "+setting+" is blank. Using default value "+default+".")
		if setting == "log_delay" and not isInt(value):
			value = default
			print("The log_delay setting is not set to an integer. Using default value "+default+".")
		return value
	
	def getFromConfig(self, setting):
		# Used by getSetting to read from the settings file.
		
		config = open("settings.txt", "r")
		value = None
		for line in config:
			if not line[0] == "#":
				splitLine = line.rstrip().split("=")
				if splitLine[0] == setting:
					value = splitLine[1]
		config.close()
		return value

	def createLogFile(self):
		# Creates a new log file with name generated from the date and time.
		
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
		# Outputs timer start message to command line and creates a new log file.
		
		sys.stdout.write("\r")
		sys.stdout.write("Timer began at " + startNow.strftime("%H:%M:%S") + " on " + startNow.strftime("%d/%m/%Y") + "\n\n")
		self.logFileName = self.createLogFile()
		
	def notifyHotkeyPressed(self, readableTime):
		# Outputs time logged message to command line and logs time in log file.
		
		logFile = open(self.logFileName, "a")
		logFile.write(readableTime+"\n")
		logFile.close()
		sys.stdout.write("\r")
		sys.stdout.write("Logged:       " + readableTime + "\n")
		sys.stdout.flush()

class Timer:
	# Class for holding time elapsed and displaying timer
	
	def __init__(self, display):
		
		self.timerBegan = False
		self.startTime = None
		self.display = display
	
	def displayTimer(self):
		
		while True:
			self.displayTimeElapsed()
			time.sleep(.2)
			
	def begin(self):
		
		self.startTime = time.time()
		self.timerBegan = True
		
		if self.display:
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
		self.getSettings()
		self.timer = Timer(self.displayTimer)
		
		self.addHotkey() 
		
		sys.stdout.write("Press your hotkey to begin the timer")
		sys.stdout.flush()
		
		self.lastTimeElapsed = -self.logDelay
	
	def getSettings(self):
		
		self.hotkey = self.io.getSetting("hotkey")
		self.displayTimer = self.io.getSetting("display_timer") == "true"
		self.logDelay = int(self.io.getSetting("log_delay"))
		
	def addHotkey(self):
		
		try:
			keyboard.add_hotkey(self.hotkey, self.callback)
			print("")
			print("Your hotkey is " + self.hotkey)
		except ValueError:
			self.io.notifyInvalidHotkey()
			self.hotkey = self.io.getDefaultSetting("hotkey")
			keyboard.add_hotkey(self.hotkey, self.callback)
			print("")
			print("Your hotkey is " + self.hotkey)
		
	def callback(self):
		# If the timer has already started check if gap between logged times is greater than logDelay
		# and pass to io class that hotkey has been pressed.
		# Otherwise start the timer.
		
		if self.timer.getTimerBegan():
			timeElapsedSeconds = self.timer.getTimeElapsed()
			if timeElapsedSeconds - self.lastTimeElapsed >= self.logDelay: #if it isn't rapid fire
				self.lastTimeElapsed = timeElapsedSeconds
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
