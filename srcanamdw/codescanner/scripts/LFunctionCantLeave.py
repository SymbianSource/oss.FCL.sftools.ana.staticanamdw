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
# LFunctionCantLeave.py
#
# Checks : L-functions that cannot leave.
#
# Reason : A function should not be named with an 'L' if it cannot 
# leave. The only exception is in virtual functions where the 
# function name is defined in the base class so the L cannot be 
# emoved. For example, RunL().
#
# #################################################################

script = CScript("LFunctionCantLeave")
script.iReString = r"""
	[A-Za-z0-9]+			# return type
	\s+
	[C|T|R][A-Za-z0-9]+		# class name
	::
	([A-Za-z0-9]+L(C|D)*)	# leaving function name (possible LC or LD function)
	\s*						# optional whitespace
	\(						# open bracket
	.*						# parameters
	\)						# close bracket
	\s*
	[^;]					# no semicolon after function definition
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

lfunctioncantleaveLeavingMethod = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D)*
	\(
""", re.VERBOSE)

lfunctioncantleaveUserLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

lfunctioncantleaveNewELeave = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
""", re.VERBOSE)

reLFunctionIgnoreStr = "RunL"
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("LFunctionIgnoreRE"):
		reLFunctionIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following functions when checking for L-functions that cannot leave: " + reLFunctionIgnoreStr
		break
if len(reLFunctionIgnoreStr) > 0:
	reLFunctionIgnores = re.compile(reLFunctionIgnoreStr, re.IGNORECASE)
else :
	reLFunctionIgnores = None

def lfunctioncantleavecompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		#ignore functions on the ignored list
		functionName = m.group(1)
		if reLFunctionIgnores:
			if reLFunctionIgnores.match(functionName):
				return 0

		i = currentline

		# find opening { in function
		while (line.count("{") == 0):
			i = i + 1
			if (i >= len(lines)):
				return 1
			line = lines[i]

		# if empty function (or one-line function?)
		if (line.count("}") > 0):
			return 1

		i = i + 1
		bracketDepth = 1

		while (i < len(lines)):
			line = lines[i]
			if lfunctioncantleaveLeavingMethod.search(line):
				return 0
			if lfunctioncantleaveUserLeave.search(line):
				return 0
			if lfunctioncantleaveNewELeave.search(line):
				return 0 

			bracketDepth += line.count("{") - line.count("}")
			if (bracketDepth == 0):
				return 1
			i = i + 1
	return 0

script.iCompare = lfunctioncantleavecompare
scanner.AddScript(script)
