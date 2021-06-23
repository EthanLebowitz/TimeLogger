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

def createConfig():
	text = "# if the hotkey variable is left empty the program will prompt you for a hotkey when\n# opened next and will store it.\nhotkey="
	if not exists("config.txt"):
		f = open("config.txt", "w")
		f.write(text)
		f.close()

createConfig()

def setHotkeyInConfig(hotkey):
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

def getHotkey():
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
	
def createLogFile():
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
				
def convertTimeToReadable(sec): # from https://www.journaldev.com/44690/python-convert-time-hours-minutes-seconds
   #sec = sec % (24 * 3600)
   hour = sec // 3600
   sec %= 3600
   min = sec // 60
   sec %= 60
   return "%02d:%02d:%02d" % (hour, min, sec) 

def callback(logFileName):
	timeElapsedSeconds = time.time() - startTime
	readableTime = convertTimeToReadable(timeElapsedSeconds)
	logFile = open(logFileName, "a")
	logFile.write(readableTime+"\n")
	logFile.close()
	print(readableTime)

startTime = time.time()
hotkey = getHotkey()
logFileName = createLogFile()
keyboard.add_hotkey(hotkey, callback, args=[logFileName])

keyboard.wait()
