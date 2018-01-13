#!/usr/bin/env python3.6

import os
import importlib
import operator

from SimpleLogger import *

class FuzzerController(object):
	
	# Following path are used to load fuzzers
	# We assume this file is ALWAYS at the root of "fuzzer" directory
	# Ex: Fuzzer/
	#     Fuzzer/FuzzerController.py
	#
	#     Fuzzer/NewSequence/
	#     Fuzzer/NewSequence/SomeFuzzer.py
	#
	#     Fuzzer/CompleteSequence/
	#
	#     Fuzzer/NewWord/
	#
	#     Fuzzer/InBetweenWord/
	#     Fuzzer/InBetweenWord/MoreFuzzer.py
	FUZZER_SUBDIR_NAME = "Fuzzers"
	NEW_SEQUENCE_PATH = "NewSequence"
	COMPLETE_SEQUENCE_PATH = "CompleteSequence"
	NEW_WORD_IN_SEQUENCE_PATH = "NewWordInSequence"
	BETWEEN_WORDS_IN_SEQUENCE_PATH = "BetweenWordsInSequence"
	
	def __init__(self, loggerObj):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		# Fuzzers are kept in dict like:
		# 	fuzzerObj : nb chars it add / remove
		self._newSequenceFuzzers = {}
		self._completeSequenceFuzzers = {}
		self._newWordInSequenceFuzzers = {}
		self._betweenWordsInSequenceFuzzers = {}
		
		# Dynamically import all Fuzzers
		self.__importAllFuzzerModules()
		
	
	
	def __importAndCreateFuzzer(self, directoryName, moduleName):
		
		newFuzzerObj = None
		
		# Only proceed if the file's not starting with __ and end with .py
		# That avoid .pyc and functional stuff like __init__.py
		if ( (os.path.splitext(moduleName)[1] == ".py") and (moduleName[:2] != "__") ):
			# Turn "stuff/morestuff/module.py" to "stuff.morestuff.module"
			moduleShortname = os.path.splitext(moduleName)[0]
			moduleRealName = os.path.join(directoryName, moduleShortname).replace("/", ".")
			
			try:
				newMod = importlib.import_module(moduleRealName)
				newClass = getattr(newMod, moduleShortname)
				newFuzzerObj = newClass(loggerObj=self._logger)
			except Exception as err:
				self._logger.printMessage(self, SimpleLoggerLevel.ERROR, "Dynamic import of Fuzzer failed, got error: '" + str(err) + "'")
		
		return newFuzzerObj
	
	
	def __importAllFuzzerModules(self):
		# Make sure cache is clear prior to the import
		importlib.invalidate_caches()
		
		fuzzerObj = None
		modulePath = os.path.join(self.FUZZER_SUBDIR_NAME, self.NEW_SEQUENCE_PATH)
		for moduleName in os.listdir(modulePath):
			fuzzerObj = self.__importAndCreateFuzzer(modulePath, moduleName)
			if (fuzzerObj is not None):
				self._newSequenceFuzzers[fuzzerObj] = fuzzerObj.getNumberCharactersAdded()
		self._logger.printMessage(self, SimpleLoggerLevel.INFO, "Loaded " + str(len(self._newSequenceFuzzers)) + " fuzzer(s) from '" + str(self.NEW_SEQUENCE_PATH) + "'")
		
		modulePath = os.path.join(self.FUZZER_SUBDIR_NAME, self.COMPLETE_SEQUENCE_PATH)
		for moduleName in os.listdir(modulePath):
			fuzzerObj = self.__importAndCreateFuzzer(self.COMPLETE_SEQUENCE_PATH, moduleName)
			if (fuzzerObj is not None):
				self._completeSequenceFuzzers[fuzzerObj] = fuzzerObj.getNumberCharactersAdded()
		self._logger.printMessage(self, SimpleLoggerLevel.INFO, "Loaded " + str(len(self._completeSequenceFuzzers)) + " fuzzer(s) from '" + str(self.COMPLETE_SEQUENCE_PATH) + "'")
		
		modulePath = os.path.join(self.FUZZER_SUBDIR_NAME, self.NEW_WORD_IN_SEQUENCE_PATH)
		for moduleName in os.listdir(modulePath):
			fuzzerObj = self.__importAndCreateFuzzer(self.NEW_WORD_IN_SEQUENCE_PATH, moduleName)
			if (fuzzerObj is not None):
				self._newWordInSequenceFuzzers[fuzzerObj] = fuzzerObj.getNumberCharactersAdded()
		self._logger.printMessage(self, SimpleLoggerLevel.INFO, "Loaded " + str(len(self._newWordInSequenceFuzzers)) + " fuzzer(s) from '" + str(self.NEW_WORD_IN_SEQUENCE_PATH) + "'")
		
		modulePath = os.path.join(self.FUZZER_SUBDIR_NAME, self.BETWEEN_WORDS_IN_SEQUENCE_PATH)
		for moduleName in os.listdir(modulePath):
			fuzzerObj = self.__importAndCreateFuzzer(modulePath, moduleName)
			if (fuzzerObj is not None):
				self._betweenWordsInSequenceFuzzers[fuzzerObj] = fuzzerObj.getNumberCharactersAdded()
		self._logger.printMessage(self, SimpleLoggerLevel.INFO, "Loaded " + str(len(self._betweenWordsInSequenceFuzzers)) + " fuzzer(s) from '" + str(self.BETWEEN_WORDS_IN_SEQUENCE_PATH) + "'")

	def _getFuzzersFromCharactersAdded(self, fuzzerDict, maxCharsFuzzerAdd):
		fuzzersList = []
		fuzzerTuples = sorted(fuzzerDict.items(), key=operator.itemgetter(1))
		for fuzzer, nbCharsAdded in fuzzerTuples:
			if (nbCharsAdded <= maxCharsFuzzerAdd):
				fuzzersList.append(fuzzer)
		return fuzzersList

	def getNewSequenceFuzzers(self, maxCharsFuzzerAdd):
		return self._getFuzzersFromCharactersAdded(self._newSequenceFuzzers, maxCharsFuzzerAdd)
	
	def getCompleteSequenceFuzzers(self, maxCharsFuzzerAdd):
		return self._getFuzzersFromCharactersAdded(self._completeSequenceFuzzers, maxCharsFuzzerAdd)
	
	def getNewWordInSequenceFuzzers(self, maxCharsFuzzerAdd):
		return self._getFuzzersFromCharactersAdded(self._newWordInSequenceFuzzers, maxCharsFuzzerAdd)
	
	def getBetweenWordInSequenceFuzzers(self, maxCharsFuzzerAdd):
		return self._getFuzzersFromCharactersAdded(self._betweenWordsInSequenceFuzzers, maxCharsFuzzerAdd)


if __name__ == '__main__':
	myLogger = SimpleLogger(defaultLevel=SimpleLoggerLevel.INFO, 
	                        printOnStderrLevel=SimpleLoggerLevel.WARNING,
	                        throwOnLevel=SimpleLoggerLevel.CRITICAL)
	
	myObject = FuzzerController(loggerObj=myLogger)
	print("getNewSequenceFuzzerList: " + str(myObject.getNewSequenceFuzzerList()))
	print("getCompleteSequenceFuzzerList: " + str(myObject.getCompleteSequenceFuzzerList()))
	print("getNewWordInSequenceFuzzerList: " + str(myObject.getNewWordInSequenceFuzzerList()))
	print("getBetweenWordInSequenceFuzzerList: " + str(myObject.getBetweenWordInSequenceFuzzerList()))
	