#!/usr/bin/env python3.6

import sys

from Writers.WriterInterface import *

class DebugWriter(WriterInterface):
	
	def __init__(self, loggerObj):
		super().__init__(loggerObj)
	
	def open(self, filepath, overwrite=True):
		# No open required for debug writer
		pass
	
	def write(self, wordsList):
		for word in wordsList:
			sys.stdout.write(word + "\n")
		sys.stdout.flush()
	
	def close(self):
		# No close required for debug writer
		pass