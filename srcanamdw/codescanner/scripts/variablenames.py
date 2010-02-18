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
# variablenames.py
#
# Checks : Local variables with member/argument names.
#
# Reason : Local variable names should be of the form localVariable 
# and not aLocalVar or iLocalVar. Badly-named variables can be 
# misleading and cause maintenance and coding errors.
#
# #################################################################

script = CScript("variablenames")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	[A-Z]\w*			# class name e.g. TInt, CActive
	\s*[\*&\s]\s*		# optional "*" or "&" plus at least one whitespace char
	[ai][A-Z]\w*\s*		# a or i variable name plus optional whitespace
	[;\(=]				# ";" or "(" or "="
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def bracecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		checkline = currentline - 1
		bracecount = 1
		while (bracecount > 0) and (checkline >= 0):
			bracecount -= lines[checkline].count("{")
			bracecount += lines[checkline].count("}")
			checkline -= 1

		while (bracecount == 0) and (checkline >= 0):
			if (lines[checkline].upper().find("CLASS") <> -1) or (lines[checkline].upper().find("STRUCT") <> -1):
				return 0
			
			bracecount -= lines[checkline].count("{")
			bracecount += lines[checkline].count("}")
			checkline -= 1

		return 1
	else:
		return 0

script.iCompare = bracecompare
scanner.AddScript(script)
