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
# trapcleanup.py
#
# Checks : Use of LC function in TRAPs.
#
# Reason : You cannot trap something that leaves something on the 
# cleanup stack because it will panic.
#
# #################################################################

script = CScript("trapcleanup")
script.iReString = "^\s*TRAPD?"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryDefinitePanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reCMethod = re.compile("""
	\w*
	[a-z]
	\w*
	LC\(
""", re.VERBOSE)

def trapcleanupcompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)
	if m:
		bracketCount = line.count("(") - line.count(")")
		cMethod = reCMethod.search(line) 
		pop = line.find("Pop")			
						 
		while (bracketCount > 0) and (currentline + 1 < len(lines)):
			currentline += 1
			line = lines[currentline]
			bracketCount += line.count("(") - line.count(")")
			if not cMethod:
				cMethod = reCMethod.search(line) 
			if (pop == -1):
				pop = line.find("Pop")			

		if cMethod and (pop == -1):
			return 1
	
	return 0

script.iCompare = trapcleanupcompare
scanner.AddScript(script)
