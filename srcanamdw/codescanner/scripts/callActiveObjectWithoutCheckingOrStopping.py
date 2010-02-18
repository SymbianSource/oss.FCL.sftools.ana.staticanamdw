# #################################################################
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of Nokia Corporation nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS 
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.#
#
# callActiveObjectWithoutCheckingOrStopping.py
#
# Checks : Active object called without checking whether it is 
# active or canceling it first.
#
# Reason : If an active object is started twice, a panic occurs. 
# CodeScanner picks out places where there is a call to a Start(), 
# Queue(), or After() function on a member variable, without a 
# previous call to IsActive(), Cancel(), or Stop(). In general, 
# if starting a timer, there should at least be a call to IsActive() 
# to ensure that the timer is not already running.
#
# #################################################################

script = CScript("callActiveObjectWithoutCheckingOrStopping")
script.iReString = r"""\("""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

activeObjectIsActive = re.compile("""
	(\.|->)
	\s*
	IsActive
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectCancel = re.compile("""
	(\.|->)
	\s*
	Cancel
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectStop = re.compile("""
	(\.|->)
	\s*
	Stop
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectCreate = re.compile("""
	=
	\s*
	\w+
	::
	New
	\w*
	\s*
	\(
	""", re.VERBOSE)

activeObjectCreate2 = re.compile("""
	=
	\s*
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	""", re.VERBOSE)

activeObjectStart = re.compile("""
	(\.|->)
	\s*
	Start
	\s*
	\(
	""", re.VERBOSE)

activeObjectQueue = re.compile("""
	(\.|->)
	\s*
	Queue
	\s*
	\(
	""", re.VERBOSE)

activeObjectAfter = re.compile("""
	(\.|->)
	\s*
	After
	\s*
	\(
	""", re.VERBOSE)

# RTimer::After() takes 2 arguments
rtimerObjectAfter = re.compile("""
	(\.|->)
	\s*
	After
	\s*
	\(
	\s*
	\w+			# first argument
	\s*
	,
	""", re.VERBOSE)

# Non-active types with After(), Queue() or Start() function
KNonActiveTypes = {
	"KAnimation"					: "Animation",
	"KAnimator"						: "Animator",
	"KClockSourcePeriodicUtility"	: "ClockSourcePeriodicUtility",
	"KCodecWrapper"					: "CodecWrapper",
	"KCommTimer"					: "CommTimer",
	"KEmbeddedStore"				: "EmbeddedStore",
	"KFormulaTextLexer"				: "FormulaTextLexer",
	"KObexServer"					: "ObexServer",
	"KSpriteAnimation"				: "SpriteAnimation",
	"KRConnection"					: "RConnection",
	"KRSubConnection"				: "RSubConnection",
	"KRTest"						: "RTest",
	"KRTimer"						: "RTimer",
	"KValidityPeriod"				: "ValidityPeriod",
	"KVideoPlayHwDevice"			: "VideoPlayHwDevice",
	"KVideoRecordHwDevice"			: "VideoRecordHwDevice",
}

def isNonActiveObject(variable):
	for name, value in KNonActiveTypes.items():
		if (variable.lower().find(value.lower()) <> -1):
			return True
	return False

def activeObjectCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (scanner.iCurrentMethodName == "Start"):
			return 0
		if (scanner.iCurrentMethodName == "Queue"):
			return 0
		if (scanner.iCurrentMethodName == "After"):
			return 0

		checkForIsActive = 0	
		if (activeObjectStart.search(line)):
			checkForIsActive = 1
		if (activeObjectQueue.search(line)):
			checkForIsActive = 1
		if (activeObjectAfter.search(line)):
			# make sure we are not dealing with RTimer::After()
			if (not rtimerObjectAfter.search(line)):
				checkForIsActive = 1
		if (checkForIsActive == 1):
			varEnd = line.find("->")
			if (varEnd < 0):
				varEnd = line.find(".")
			if (varEnd < 0):
				return 0
			
			variable = TrimVariableName(line[:varEnd])
			if (len(variable) == 0):
				return 0

			# if a local variable then unlikely to have been started already
			if (len(variable) > 2):
				if (variable[0] != 'i'):
					return 0
				else:
					if (variable[1] < 'A') or (variable[1] > 'Z'):
						return 0

			# ignore non-active object
			if isNonActiveObject(variable):
				return 0

			i = currentline
			while (i > scanner.iCurrentMethodStart):
				line = lines[i]
				varPos = line.find(variable)
				if (varPos >= 0):
					cutLine = line[varPos:]
					if (activeObjectIsActive.search(cutLine)):
						return 0
					if (activeObjectCancel.search(cutLine)):
						return 0
					if (activeObjectStop.search(cutLine)):
						return 0
					if (activeObjectCreate.search(cutLine)):
						return 0
					if (activeObjectCreate2.search(cutLine)):
						return 0
				i = i - 1
			return 1

	return 0

script.iCompare	= activeObjectCompare
scanner.AddScript(script)
