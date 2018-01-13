#!/usr/bin/env python3.6

import os
import sys
import enum

# Enum is Python >= 3.4!
class SimpleLoggerLevel(enum.IntEnum):
	DEBUG    = 0
	INFO     = 1
	WARNING  = 2
	ERROR    = 3
	CRITICAL = 4

class SimpleLogger(object):
	
	def __init__(self, 
	             defaultLevel=SimpleLoggerLevel.ERROR, 
	             printOnStderrLevel=SimpleLoggerLevel.ERROR, 
	             throwOnLevel=SimpleLoggerLevel.CRITICAL):
		
		# Sanity checks
		if (not isinstance(defaultLevel, SimpleLoggerLevel)):
			raise Exception("defaultLevel is not of type SimpleLoggerLevel")
		if (not isinstance(printOnStderrLevel, SimpleLoggerLevel)):
			raise Exception("printOnStderrLevel is not of type SimpleLoggerLevel")
		if (not isinstance(throwOnLevel, SimpleLoggerLevel)):
			raise Exception("throwOnLevel is not of type SimpleLoggerLevel")
		
		self._defaultLevel = defaultLevel
		self._stderrLevel  = printOnStderrLevel
		self._throwLevel   = throwOnLevel
	
	def getDefaultLevel(self):
		return self._defaultLevel
	
	def setDefaultLevel(self, newLevel):
		if (not isinstance(newLevel, SimpleLoggerLevel)):
			raise Exception("newLevel is not of type SimpleLoggerLevel")
		self._defaultLevel = newLevel
	
	def getPrintOnStderrLevel(self):
		return self._stderrLevel
	
	def setPrintOnStderrLevel(self, newLevel):
		if (not isinstance(newLevel, SimpleLoggerLevel)):
			raise Exception("newLevel is not of type SimpleLoggerLevel")
		self._stderrLevel = newLevel
	
	def getThrowOnLevel(self):
		return self._throwLevel
	
	def setThrowOnLevel(self, newLevel):
		if (not isinstance(newLevel, SimpleLoggerLevel)):
			raise Exception("newLevel is not of type SimpleLoggerLevel")
		self._throwLevel = newLevel
	
	def printMessage(self, caller, level, message):
		if (not isinstance(level, SimpleLoggerLevel)):
			raise Exception("level is not of type SimpleLoggerLevel")
		
		if (level < self._defaultLevel):
			return
		
		if (level >= self._stderrLevel):
			target=sys.stderr
		else:
			target=sys.stdout
		
		if (level >= self._throwLevel):
			raise Exception(message)
		else:
			# This should be backward compatible with python 2.X
			# Didn't test, though
			print(str(caller.__class__.__name__) + ":\t", message, file=target)


if __name__ == '__main__':
	myObject = SimpleLogger(defaultLevel=SimpleLoggerLevel.INFO, 
	                        printOnStderrLevel=SimpleLoggerLevel.ERROR,
	                        throwOnLevel=SimpleLoggerLevel.CRITICAL)
	myObject.printMessage(myObject, SimpleLoggerLevel.DEBUG,   "Test1: will NOT show")
	myObject.printMessage(myObject, SimpleLoggerLevel.WARNING, "Test2: will show")
	myObject.printMessage(myObject, SimpleLoggerLevel.ERROR,   "Test3: will show on stderr")
	myObject.printMessage(myObject, SimpleLoggerLevel.CRITICAL,"Test4: will throw")
	