#!/usr/bin/env python3.6

import os

from Writers.WriterInterface import *

class SimpleFileWriter(WriterInterface):
	
	def __init__(self, loggerObj):
		super().__init__(loggerObj)
		self._fileHandler = None
	
	def open(self, filepath, overwrite=True):
		
		parentDir = os.path.dirname(filepath)
		# Check if we have a parent subdirectory
		# If not, use "." (current work dir)
		if (parentDir == ""):
			parentDir = "."
		# Check existence and write on parent
		if ( (not os.path.exists(parentDir)) or (not os.access(parentDir, os.W_OK)) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Writer destination path '" + str(filepath) + "' does not exist or is not writable!" )
		
		# If target already exist, check that it is a file and that it is writable
		if ( (os.path.exists(filepath)) and 
			( (not os.access(filepath, os.W_OK)) or (not os.path.isfile(filepath)) ) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Writer destination path '" + str(filepath) + "' is not a file or file is not writable!" )
		
		if (overwrite):
			self._fileHandler = open(filepath, "w")
		else:
			self._fileHandler = open(filepath, "a")
	
	
	def write(self, wordsList):
		for word in wordsList:
			self._fileHandler.write(word + "\n")
	
	
	def close(self):
		self._fileHandler.close()
		self._fileHandler = None