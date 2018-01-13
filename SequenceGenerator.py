#!/usr/bin/env python3.6

import sys
import random

from collections import deque

from SimpleLogger import *
from DictionnaryLoader import *
from WriterController import *
from FuzzerController import *
from LettersDistributionFrequency import *

class SequenceGenerator(object):
	def __init__(self, 
		     loggerObj, 
		     dictionnaryLoaderObj,
		     fuzzerObj,
		     writerObj,
		     numberOfLetters,
		     lettersDistributionFrequencyObj=None,
		     maximumNumberOfSequences=0,
		     maximumBytesSizeForAllSequences=0):
		if (not isinstance(loggerObj, SimpleLogger)):
			raise Exception("loggerObj not of a SimpleLogger instance!")
		self._logger = loggerObj
		
		if (not isinstance(dictionnaryLoaderObj, DictionnaryLoader)):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "dictionnaryLoaderObj not of a DictionnaryLoader instance!")
		self._wordsObj = dictionnaryLoaderObj
		
		if (not isinstance(fuzzerObj, FuzzerController)):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "fuzzerObj not of a FuzzerController instance!")
		self._fuzzerCtrl = fuzzerObj
		
		if (not isinstance(writerObj, WriterController)):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "writerObj not of a WriterController instance!")
		self._writer = writerObj
		
		if ( (not isinstance(numberOfLetters, int)) or (numberOfLetters < 1) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "numberOfLetters must be an integer greater or equal to 1")
		self._nbLetters = numberOfLetters
		
		
		# If the distribution wasn't given, use the default (linear) one
		# Note: this WON'T give the best result!
		if (lettersDistributionFrequencyObj is None):
			lettersDistributionFrequencyObj = LettersDistributionFrequency(loggerObj=myLogger)
		if (not isinstance(lettersDistributionFrequencyObj, LettersDistributionFrequency)):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "lettersDistributionSample not of a LettersDistributionFrequency instance!")
		self._lettersFrequencyObj = lettersDistributionFrequencyObj
		
		if ( (not isinstance(maximumNumberOfSequences, int)) or (maximumNumberOfSequences < 1) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "maximumNumberOfSequences must be an integer greater or equal to 1")
		self._maxNbSequence = maximumNumberOfSequences
		
		if ( (not isinstance(maximumBytesSizeForAllSequences, int)) or (maximumBytesSizeForAllSequences < 1) ):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "maximumBytesSizeForAllSequences must be an integer greater or equal to 1")
		# Calculate max size for the sequences (based on nbLetters)
		self._maxSizeBytes = (maximumBytesSizeForAllSequences * self._nbLetters)
	
	
	def _checkIterationsLeft(self, sequencesLeft, spaceLeft, newlyGeneratedSequences):
		# compute size left with the newly generated sequences
		for sequence in newlyGeneratedSequences:
			# Decrement storage space left
			spaceLeft = spaceLeft - len(sequence)
			# Decrement number of sequence left
			sequencesLeft = sequencesLeft - 1
		return sequencesLeft, spaceLeft
	
	
	
	def _pickWord(self, maxNbLetters):
		
		pickedNbLetters = 0
		while ( (pickedNbLetters <= 0) or (pickedNbLetters > maxNbLetters) ):
			# Get starting sequence
			randomPick = random.choices(population=self._lettersFrequencyObj.getLettersList(), weights=self._lettersFrequencyObj.getLettersProbability(), k=1)
			# TODO
			# Do we want to re-loop if sequence size not available?
			# To investigate...
			if (not randomPick):
				# Make sure there is actually a distribution for that size!
				self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "No distribution value found!")
				return None
			else:
				pickedNbLetters = randomPick[0]
				letterLeftAfterPick = maxNbLetters - pickedNbLetters
		
		wordsForLetter = self._wordsObj.getPatternDictForLength(pickedNbLetters)
		# *** FIXME ***
		# Might not have pattern for that size...
		# Need to better handle case where myPatterns is empty!
		if (not wordsForLetter):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "No word of " + str(pickedNbLetters) + " returned!")
			return None
		
		wordsList = list(wordsForLetter.keys())
		wordProbabilityList = list(wordsForLetter.values())
		# Pick a word
		chosenWord = random.choices(population=wordsList, weights=wordProbabilityList, k=1)[0]
		
		return chosenWord
	
	def _sortCompletedSequence(self, sequencesToSort, completedSet, incompletedDeque, nbSequencesLeft, sequenceSizeLeft):
		
		sequenceAdded = 0
		
		# *** FIXME ***
		# Lost of performance!
		# We do not need to loop, applyFuzzing() could simply return a tuple (size, word)
		for sequence in sequencesToSort:
			# If we reached limit on number of sequences, 
			#   don't bother checking and skip loop
			if ( (nbSequencesLeft > 0) and (sequenceSizeLeft > 0) ):
				charLeft = self._nbLetters - len(sequence)
				
				if (charLeft > 0):
					incompletedDeque.append( (sequence, charLeft) )
				else:
					# Only insert non-duplicated
					if (sequence not in completedSet):
						completedSet.add(sequence)
						sequenceAdded = sequenceAdded + 1
						nbSequencesLeft = nbSequencesLeft - 1
						# FIXME
						# Is this bytes calculation always valid?
						sequenceSizeLeft = sequenceSizeLeft - self._nbLetters
		
		# Everything is sorted, empty the list
		sequencesToSort.clear()
		
		return (sequenceAdded, nbSequencesLeft, sequenceSizeLeft)
	
	
	
	def generateSequences(self):
		
		completeSequences = set()
		incompleteSequences = deque()
		newSequences = list()
		
		# Sanity test
		if (self._nbLetters <= 0):
			self._logger.printMessage(self, SimpleLoggerLevel.CRITICAL, "Invalid numbers of letters : must be a positive integer (got " + str(self._nbLetters) + ")")
			return []
		
		# Setup limits conditions (number of sequences and total sequence storage size)
		sequencesLeft = self._maxNbSequence
		sequenceSizeLeft = self._maxSizeBytes
		
		while ((sequencesLeft > 0) and (sequenceSizeLeft > 0) ):
			
			# ***    HOOK     ***
			# *** NEW SEQUENCE  ***
			for fuzzer in self._fuzzerCtrl.getNewSequenceFuzzers(self._nbLetters):
				newSequences.extend(fuzzer.applyFuzzing() )
			
			# Seed word to build on from
			newWord = self._pickWord(self._nbLetters)
			newSequences.append(newWord)
			
			# ***  HOOK      ***
			# *** NEW WORD   ***
			for fuzzer in self._fuzzerCtrl.getNewWordInSequenceFuzzers(self._nbLetters - len(newWord) ):
				newSequences.extend(fuzzer.applyFuzzing(newWord))
			
			# Sort completed / uncompleted
			(completedWordAdded, sequencesLeft, sequenceSizeLeft) = self._sortCompletedSequence(newSequences, completeSequences, incompleteSequences, sequencesLeft, sequenceSizeLeft)
			
			completedWordAdded = 0
			# Loop while incomplete sequence exists in the list
			while ( len(incompleteSequences) > 0):
				
				(previousWord, nbCharLeft) = incompleteSequences.pop()
				
				newWord = self._pickWord(nbCharLeft)
				newWordSequence = previousWord + newWord
				newSequences.append(newWordSequence)
				
				# ***        HOOK           ***
				# *** BETWEEN WORD SEQUENCE ***
				spaceLeftFuzzer = self._nbLetters - len(newWordSequence)
				for fuzzer in self._fuzzerCtrl.getBetweenWordInSequenceFuzzers( spaceLeftFuzzer ):
					newSequences.extend(fuzzer.applyFuzzing(previousWord, newWord) )
				
				# Sort completed / uncompleted
				(completedWordAdded, sequencesLeft, sequenceSizeLeft) = self._sortCompletedSequence(newSequences, completeSequences, incompleteSequences, sequencesLeft, sequenceSizeLeft)
				
				# If we completed at least ONE word, 
				# Then add back our starting word to incomplete sequence
				if (completedWordAdded > 0):
					incompleteSequences.append( (previousWord, nbCharLeft)  )
				
			# No more incomplete sequence, apply final fuzzing on complete sequences
			nonFuzzedCompleteSequences = set(completeSequences)
			# ***        HOOK       ***
			# *** COMPLETE SEQUENCE ***
			for sequence in nonFuzzedCompleteSequences:
				for fuzzer in self._fuzzerCtrl.getCompleteSequenceFuzzers(0):
					completeSequences.union(fuzzer.applyFuzzing(sequence) )
		
			# Let writer save/print the result
			self._writer.write(completeSequences)
		
		# We are done, close the writers
		self._writer.close()
		