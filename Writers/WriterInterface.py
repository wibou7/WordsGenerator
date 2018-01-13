#!/usr/bin/env python3.6

from SimpleLogger import *

class WriterInterface(object):
	
	def __init__(self, loggerObj):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
	
	def open(self, filepath, overwrite=True):
		raise Exception("Method must be implemented by child class")
	
	def write(self, wordsList):
		raise Exception("Method must be implemented by child class")
	
	def close(self):
		raise Exception("Method must be implemented by child class")