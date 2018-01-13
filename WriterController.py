#!/usr/bin/env python3.6

from SimpleLogger import *
from Writers.WriterInterface import *

class WriterController(object):
	
	def __init__(self, loggerObj):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		self._writerList = set()
		
	
	def addWriter(self, writerObj):
		if (not isinstance(writerObj, WriterInterface)):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "writerObj not of a WriterInterface instance!")
		
		if (writerObj in self._writerList):
			self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "writer object '" + str(writerObj) + "' already added in writer list")
		
		self._writerList.add(writerObj)
	
	
	def removeWriter(self, writerObj):
		if (writerObj not in self._writerList):
			self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "writer object '" + str(writerObj) + "' not in writer list")
		
		self._writerList.remove(writerObj)
	
	
	def getWriters(self):
		return self._writerList
	
	
	def write(self, wordsList):
		for writer in self._writerList:
			writer.write(wordsList)
	
	
	def close(self):
		for writer in self._writerList:
			writer.close()