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
# privateinheritance.py
#
# Checks : Use of private inheritance.
#
# Reason : Classes should not be inherited privately. If public or 
# protected inheritance is not appropriate, consider using an 
# amalgamation; that is, have an object of that type as a 
# member variable.
#
# #################################################################

script = CScript("privateinheritance")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	class
	\s+					# whitespace
	\w+					# class name
	\s*					# optional whitespace
	:
	(.*)
	"""
script.iFileExts = ["cpp", "h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def privatecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		searchtext = m.group(1)
		if (searchtext.find("private") == -1):
			return 0
		else:
			return 1
	else:
		return 0

script.iCompare = privatecompare
scanner.AddScript(script)
