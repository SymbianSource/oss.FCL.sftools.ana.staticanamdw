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
# leave.py
#
# Checks : Leaving functions called in non-leaving functions.
#
# Reason : Non-leaving functions should not call leaving functions. 
# Note: Operator functions are considered to be able to leave when 
# scanning the code inside them.
#
# #################################################################

script = CScript("leave")
script.iReString = KReStringLeavingLine
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reLeavingMethod = re.compile("""
	(
	\s*operator
	|
	\w*
	[a-z]
	\w*
	L
	(C(C*|[2-9])|D|P|X)?
	$
	)
""", re.VERBOSE)

def leavecompare(lines, currentline, rematch, filename):
	currentMethod = scanner.iCurrentMethodName
	if (currentMethod <> "") and (currentMethod[:5] <> "Leave"):
		m = rematch.search(lines[currentline])
		if m and not reLeavingMethod.search(currentMethod):
			line = lines[currentline]
			startline = currentline
			if (lines[currentline].find("TRAP") != -1):
				return 0

			bracketCount = line.count("(") - line.count(")")
			startBracketCount = bracketCount

			while (currentline > startline - 40) and (currentline >= 0):
				currentline -= 1
				line = lines[currentline]
				bracketCount += line.count("(") - line.count(")")
				if (lines[currentline].find("TRAP") != -1) and (bracketCount == startBracketCount + 1):
					return 0
			return 1

	return 0

script.iCompare = leavecompare
scanner.AddScript(script)
