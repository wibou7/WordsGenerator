#!/usr/bin/env python3.6

import os
import sys
import argparse

from SimpleLogger import *
from DictionnaryLoader import *
from LettersDistributionFrequency import *
from FuzzerController import *
from Writers.DebugWriter import *
from Writers.SimpleFileWriter import *
from SequenceGenerator import * 

class CommandLineUI(object):
	
	def __init__(self):
		self._loggerObj = None
		self._wordsLoaderObj = None
		self._letterFreqObj = None
		self._fuzzerLoaderObj = None
		self._writerCtrlObj = None
	
	def __createLogger(self, args):
		logger = SimpleLogger()
		if (args.verbose == True):
			logger.setDefaultLevel(SimpleLoggerLevel.INFO)
		if (not args.logging_levels is None):
			levels = args.logging_levels.split(',')
			if (len(levels) < 3):
				raise Exception("Bad --logging-levels given; format is 'N1,N2,N3' where N1 stdout level, N2 stderr level and N3 exit level.\nGot '" + str(args.logging_levels) + "'")
			
			# Assume levels are int, if not try their string
			try:
				level = SimpleLoggerLevel(int(levels[0]) )
			except ValueError as err:
				level = SimpleLoggerLevel[ str(levels[0]) ]
			logger.setDefaultLevel( level )
			
			try:
				level = SimpleLoggerLevel(int(levels[1]) )
			except ValueError as err:
				level = SimpleLoggerLevel[ str(levels[1]) ]
			logger.setPrintOnStderrLevel( level )
			
			try:
				level = SimpleLoggerLevel(int(levels[2]))
			except ValueError as err:
				level = SimpleLoggerLevel[ str(levels[2]) ]
			logger.setThrowOnLevel( level )
		
		return logger
	
	
	def _createDictionnaryLoader(self, args, logger):
		dictionnaryObj = DictionnaryLoader(loggerObj=logger, allowDuplicatePattern=args.forbid_duplicate)
		
		if ( (args.words_dictionnary_path is None) or (len(args.words_dictionnary_path) <= 0) ):
			logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Need at least ONE --words-dictionnary-path argument to load word from. See --help.")
		else:
			for dictPath in args.words_dictionnary_path:
				dictionnaryObj.loadPatternFromCsvPath(dictPath)
		
		return dictionnaryObj
	
	
	def _createLetterFrequencyLoader(self, args, logger):
		lettersFrequencyObj = LettersDistributionFrequency(loggerObj=logger, allowDuplicatePattern=args.forbid_duplicate)
		
		if ( (args.letters_by_word_frequency_path is None) or (len(args.letters_by_word_frequency_path) <= 0) ):
			logger.printMessage(self, SimpleLoggerLevel.WARNING, "Missing --letters-by-word-frequency-path argument; using default values (this is NOT want you want). See --help.")
		else:
			for freqPath in args.letters_by_word_frequency_path:
				lettersFrequencyObj.loadPatternFromCsvPath(freqPath)
		
		return lettersFrequencyObj
	
	
	def _createFuzzer(self, args, logger):
		fuzzerObj = FuzzerController(loggerObj=self._loggerObj)
		
		return fuzzerObj
		
	
	def _createWriters(self, args, logger):
		
		writerCtrlObj = WriterController(loggerObj=logger)
		
		if (args.debug):
			newWriter = DebugWriter(loggerObj=logger)
			writerCtrlObj.addWriter(newWriter)
		
		if ( (not args.write_output_to is None) and (len(args.write_output_to) > 0) ):
			for outputPath in args.write_output_to:
				newWriter = SimpleFileWriter(loggerObj=logger)
				newWriter.open(filepath=outputPath, overwrite=args.append_to_output)
				writerCtrlObj.addWriter(newWriter)
		
		if (len(writerCtrlObj.getWriters()) <= 0):
			logger.printMessage(self, SimpleLoggerLevel.WARNING, "No writer defined; you need either --write-output-to or --debug argument; generated password will NOT be written or shown. See --help.")
		
		return writerCtrlObj
	
	def _parsePasswordCount(self, args, logger):
		
		passCount = args.password_count
		if (passCount is None):
			logger.printMessage(self, SimpleLoggerLevel.WARNING, "No argument --password-count given; password generation will NOT end automatically. See --help.")
			passCount = sys.maxint
		
		return passCount
	
	def _parseSizeLimit(self, args, logger):
		maxSize = args.maximum_storage_size
		if (maxSize is None):
			maxSize = sys.maxsize
		else:
			# Assume we got byte number first
			try:
				maxSize = int(args.maximum_storage_size)
			# If not, try to parse K/M/G/T given
			except ValueError as err:
				# Remove whitespace
				maxSizeStr = args.maximum_storage_size.strip()
				# Isolate "unit" (i.e. K/M/G/T)
				unit = maxSizeStr[-1]
				# Isolate number (assuming it is a number)
				try:
					maxSize = int(maxSizeStr[:-1])
				except ValueError as err:
					logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Unrecognized --maximum-storage-size '" + str(maxSizeStr) + "'. See --help.")
				
				# Multiply number by unit
				if (unit == "K"):
					maxSize *= 1024
				elif (unit == "M"):
					maxSize *= (1024*1024)
				elif (unit == "G"):
					maxSize *= (1024*1024*1024)
				elif (unit == "T"):
					maxSize *= (1024*1024*1024*1024)
				else:
					logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Unrecognized --maximum-storage-size unit '" + str(unit) + "'. See --help.")
			
			# Some debug
			logger.printMessage(self, SimpleLoggerLevel.INFO, "Got --maximum-storage-size '" + str(maxSizeStr) + "'; generating up to " + str(maxSize) + " bytes.")
			
		return maxSize
	
	
	def __parseArguments(self):
		
		parser = argparse.ArgumentParser(
			description="Password generator", 
			epilog="\nExample:\n " + str(sys.argv[0]) + " ")
		parser.add_argument("-v", "--verbose", action="store_true", help="Turn on verbose mode; additionnal messages are going to be printed on stdout.")
		parser.add_argument("-d", "--debug", action="store_true", help="Debug mode; all messages printed on stdout, generated passwords are printed on screen as well.")
		parser.add_argument("-n", "--letter-number", type=int, help="Number of letters for the passwords to generate.", required=True)
		parser.add_argument("-m", "--password-count", type=int, help="Number of passwords that are going to be generated. Default: no limit.")
		parser.add_argument("-s", "--maximum-storage-size", type=str, help="Maximum storage size the password can use. Support K, M, G, T format (ex: 1G = 1073741824 bytes). Default: no limit.")
		parser.add_argument("-w", "--words-dictionnary-path", type=str, action="append", help="Load words from dictionnary at given path (see Format). Can be given multiple time to load multiple files.")
		parser.add_argument("-f", "--letters-by-word-frequency-path", type=str, action="append", help="Load number of letter in a word frequency from path (see Format). Can be given multiple time to load multiple files.")
		parser.add_argument("-o", "--write-output-to", type=str, action="append", help="Write output to given path. Can be given multiple time to write to multiple path at once.")
		
		parser.add_argument("--logging-levels", type=str, help="Use given logging level instead of default ones. Format is 'N1,N2,N3' where N1 stdout level, N2 stderr level and N3 exit level (Ex:'2,3,4' or 'WARNING,ERROR,CRITICAL')")
		parser.add_argument("--forbid-duplicate", action="store_false", help="Forbid duplicate words when loading dictionnaries and/or letters frequency; raise error if a word is present in more than one dictionnary at a time.")
		parser.add_argument("--append-to-output", action="store_false", help="Append to output file(s) instead of starting anew.")
		
		args = parser.parse_args()
		
		# Create logger first as everyone need it
		self._loggerObj = self.__createLogger(args)
		# Create dictionnary object
		self._wordsLoaderObj = self._createDictionnaryLoader(args, self._loggerObj)
		# Create letter frequency loader
		self._letterFreqObj = self._createLetterFrequencyLoader(args, self._loggerObj)
		# Create fuzzers loader
		self._fuzzerLoaderObj = self._createFuzzer(args, self._loggerObj)
		# Create writer controller
		self._writerCtrlObj = self._createWriters(args, self._loggerObj)
		
		# Letter number is given straight
		lettersNumber = args.letter_number
		# Number of password to generate (if any)
		passCount = self._parsePasswordCount(args, self._loggerObj)
		# Storage size limit (if any)
		storageSizeLimit = self._parseSizeLimit(args, self._loggerObj)
		
		# This (finally) create our generator
		generator = SequenceGenerator(loggerObj=self._loggerObj, 
		                        	dictionnaryLoaderObj=self._wordsLoaderObj,
		                        	fuzzerObj=self._fuzzerLoaderObj,
		                        	writerObj=self._writerCtrlObj,
		                        	numberOfLetters=lettersNumber,
		                        	lettersDistributionFrequencyObj=self._letterFreqObj,
		                        	maximumNumberOfSequences=passCount,
		                        	maximumBytesSizeForAllSequences=storageSizeLimit)
		
		return generator
	
	
	
	
	def run(self):
		generator = self.__parseArguments()
		generator.generateSequences()
	
	

if __name__ == '__main__':
	deviceTest = CommandLineUI()
	deviceTest.run()



