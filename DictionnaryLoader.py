#!/usr/bin/env python3.6

import os
import sys
import csv

from SimpleLogger import *

class DictionnaryLoader(object):
	
	def __init__(self, loggerObj, allowDuplicatePattern=False):
		
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		self._duplicateOk = allowDuplicatePattern
		
		# Dict of dicts
		# 	key  : string len
		#	value: patterns dict for this len
		# Pattern dict is:
		#	key  : pattern
		#	value: probability
		self._patternLenDict = {}
		
	
	def getPatternDictForLength(self, length):
		if (length not in self._patternLenDict):
			return {}
		else:
			return self._patternLenDict[length]
	
	
	def loadPatternFromCsvPath(self, csvPath):
		if ( (not os.path.exists(csvPath)) or
		     (not os.access(csvPath, os.R_OK) ) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "File '" + str(csvPath) + "' does not exists or is not readable")
		
		csvfile = open(csvPath, "r")
		if (csvfile is None):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Error while opening path '" + str(csvPath) + "'")
		
		reader = csv.reader(csvfile, delimiter=',')
		# A row is expected to be a list [percent, char]
		for row in reader:
			
			# Make sure we are dealing with string
			if (not isinstance(row[1], str)):
				self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Read value '" + str(row[1]) + "' is not a recognized string!")
				# Skip that pattern, move to next one
				continue
			pattern = row[1]
			
			# Make sure we are dealing with percentage
			try:
				probability = float(row[0])
				if ( (probability < 0.0) or (probability > 1.0) ):
					raise ValueError("Not a recognized percentage (0.0 to 1.0) !")
			except ValueError as err:
				self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Probability '" + str(probability) + "' for pattern '" + pattern + "' is not a recognized float OR is not between 0.0 and 1.0!")
				# Bad value / bad type, move on
				continue
			
			patternLen = len(pattern)
			if (patternLen not in self._patternLenDict):
				self._patternLenDict[patternLen] = {}
			
			patternDict = self._patternLenDict[patternLen]
			
			# Key duplicate not accepted unless "allowDuplicate" flag is on
			if (pattern in patternDict):
				if (self._duplicateOk is False):
					self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Pattern '" + pattern + "' already defined in pattern list!")
					# Duplicate: moving on
					continue
				else:
					self._logger.printMessage(self, SimpleLoggerLevel.WARNING, "Found duplicate pattern '" + pattern + "', replacing existing")
			patternDict[pattern] = probability
		
			
	


if __name__ == '__main__':
	
	import random
	
	myLogger = SimpleLogger(defaultLevel=SimpleLoggerLevel.INFO, 
	                        printOnStderrLevel=SimpleLoggerLevel.WARNING,
	                        throwOnLevel=SimpleLoggerLevel.CRITICAL)
	
	myObject = DictionnaryLoader(loggerObj=myLogger, allowDuplicatePattern=True)
	myObject.loadPatternFromCsvPath("/mnt/data/Software/Fun/Dictionnaries/Unigramme-formatted.csv")
	myObject.loadPatternFromCsvPath("/mnt/data/Software/Fun/Dictionnaries/dict-english-filtered-formatted-all-equal.csv")
	myObject.loadPatternFromCsvPath("/mnt/data/Software/Fun/Dictionnaries/dict-french-filtered-formatted-all-equal.csv")

	for i in range(100):
		
		nb_char = 8
		my_string = ""
		while (nb_char > 1):
			getNbLetters = 999
			while (getNbLetters > nb_char):
				getNbLetters = random.randint(2,8)
			myPatterns = myObject.getPatternDictForLength(getNbLetters)
		
			my_population = list(myPatterns.keys())
			my_weight = list(myPatterns.values())
		
			draw = random.choices(population=my_population, weights=my_weight, k=1)
			my_string += draw[0]
			nb_char = nb_char - getNbLetters
			
		print(my_string)
