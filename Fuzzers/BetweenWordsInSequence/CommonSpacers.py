#!/usr/bin/env python3.6

import random

from SimpleLogger import *

class CommonSpacers(object):
	
	# This fuzzer applies "typical" spacing:
	#	<space>   : 75%
	#	-         : 20%
	#	_         : 5%
	#
	# It adds one char to the sequence
	def __init__(self, loggerObj):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		self._fuzzingList = {
			' ':0.75,
			'-':0.2,
			'_':0.05,
		}
		self._nbCharsAdded = 1
	
	
	def getNumberCharactersAdded(self):
		return self._nbCharsAdded
	
	
	def getNumberOfFuzzingChoices(self):
		return len(self._fuzzingList)
	
	
	# *** TODO ***
	# Implement something to "pick" nb of fuzzing to apply
	# Not quite sure how that would work, but..?
	def applyFuzzing(self, wordBefore, wordCurrent, nbFuzzingChoiceToApply=9999):
		
		fuzzedWords = []
		
		maxChoices = len(self._fuzzingList)
		if (nbFuzzingChoiceToApply >= maxChoices):
			nbFuzzingChoiceToApply = maxChoices
		
		# Copy the dict to avoid destroying the master copy as we go
		fuzzingChoices = self._fuzzingList.copy()
		while (nbFuzzingChoiceToApply > 0):
			newFuzzing = random.choices(population=list(fuzzingChoices.keys()), weights=list(fuzzingChoices.values()), k=1)[0]
			fuzzedWords.append(wordBefore + newFuzzing + wordCurrent)
			
			# Remove picked choice, decrement choice left
			del fuzzingChoices[newFuzzing]
			nbFuzzingChoiceToApply = nbFuzzingChoiceToApply - 1
		
		return fuzzedWords
		
		
