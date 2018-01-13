#!/usr/bin/env python3.6

import os
import sys
import csv

from SimpleLogger import *

class LettersDistributionFrequency(object):
	
	def __init__(self, loggerObj, allowDuplicatePattern=False):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		self._duplicateOk = allowDuplicatePattern
		
		# Create default (linear) values
		# This is for simplicity, it is expected to get overwritten
		# It WON'T give best result
		self._probabilityLetterList = {
						1 : 0.1,
						2 : 0.1,
						3 : 0.1,
						4 : 0.1,
						5 : 0.1,
						6 : 0.1,
						7 : 0.1,
						8 : 0.1,
						9 : 0.1,
						10: 0.1,
		}
		
	
	def loadPatternFromCsvPath(self, csvPath):
		
		letterProbabilityDistribution = {}
		
		if ( (not os.path.exists(csvPath)) or
		     (not os.access(csvPath, os.R_OK) ) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "File '" + str(csvPath) + "' does not exists or is not readable")
		
		csvfile = open(csvPath, "r")
		if (csvfile is None):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Error while opening path '" + str(csvPath) + "'")
		
		reader = csv.reader(csvfile, delimiter=',')
		# A row is expected to be a list [percent, number]
		for row in reader:
			
			# Make sure we are dealing with int
			try:
				number = int(row[1])
			except ValueError as err:
				self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Read value '" + str(row[1]) + "' is not a recognized integer!")
				# If we didn't raise, skip that and continue forward
				continue
			
			# Make sure we are dealing with percentage
			try:
				probability = float(row[0])
				if ( (probability < 0.0) or (probability > 1.0) ):
					raise ValueError("Not a recognized percentage (0.0 to 1.0) !")
			except ValueError as err:
				self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Probability '" + str(probability) + "' for pattern '" + pattern + "' is not a recognized float OR is not between 0.0 and 1.0!")
				# Bad value / bad type, move on
				continue
			
			# Duplicate not accepted unless "allowDuplicate" flag is on
			if (number in letterProbabilityDistribution):
				if (self._duplicateOk is False):
					self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Pattern '" + pattern + "' already defined in pattern list!")
					# Duplicated : skip
					continue
				else:
					self._logger.printMessage(self, SimpleLoggerLevel.WARNING, "Found duplicate pattern '" + pattern + "', replacing existing")
			
			# Assign number:prob to the dict
			letterProbabilityDistribution[number] = probability
		
		# Reading completed: overwrite class dict
		self._probabilityLetterList = letterProbabilityDistribution
		
		
	def getDistributionDict(self):
		return self._probabilityLetterList
	
	def getLettersList(self):
		return list(self._probabilityLetterList.keys())
	
	def getLettersProbability(self):
		return list(self._probabilityLetterList.values())
	
	
	
if __name__ == '__main__':
	
	myLogger = SimpleLogger(defaultLevel=SimpleLoggerLevel.INFO, 
	                        printOnStderrLevel=SimpleLoggerLevel.WARNING,
	                        throwOnLevel=SimpleLoggerLevel.CRITICAL)
	
	myObject = LettersDistributionFrequency(loggerObj=myLogger, allowDuplicatePattern=True)
	# Load twice to test duplicate
	myObject.loadPatternFromCsvPath("/mnt/data/Software/Fun/Dictionnaries/DistributionByLettersEnglish.csv")
	myObject.loadPatternFromCsvPath("/mnt/data/Software/Fun/Dictionnaries/DistributionByLettersEnglish.csv")
	print(str(myObject.getDistributionDict() ) )
	