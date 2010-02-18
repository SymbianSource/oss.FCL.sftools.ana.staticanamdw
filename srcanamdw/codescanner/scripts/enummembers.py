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
# enummembers.py
#
# Checks : Badly-named enum members.
#
# Reason : Badly-named enum members make the code harder to 
# maintain and may cause defects.
#
# #################################################################

script = CScript("enummembers")
script.iReString = r"""
			^
			\s*
			enum
			((\s+\w+)|(\s+\w+\s*::\s*\w+))?
			\s*
			({|$)
			"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reMember = re.compile("^\s*(\w+)")

def enummemberscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		startline = currentline
		openbraceindex = lines[startline].find("{")
		while (openbraceindex == -1) and (startline < len(lines)) and (lines[startline].find(";") == -1):
			startline += 1
			openbraceindex = lines[startline].find("{")

		if openbraceindex == -1:
			return 0

		endline = currentline
		closebraceindex = lines[endline].find("}")
		while (closebraceindex == -1) and (endline < len(lines)):
			endline += 1
			closebraceindex = lines[endline].find("}")

		enumcontents = ""
		if (startline == endline):
			enumcontents = lines[startline][openbraceindex + 1:closebraceindex - 1]
		else:
			enumcontents = lines[startline][openbraceindex + 1:]
			line = startline + 1
			while (line < len(lines)) and (line < endline):
				enumcontents = enumcontents + lines[line]
				line += 1

			enumcontents = enumcontents + lines[endline][:closebraceindex - 1]

		# check contents
		members = enumcontents.split("\n\r,")
		for member in members:
			m2 = reMember.search(member)
			if m2 and (m2.group(1)[:1] <> "E"):
				return 1
									
	return 0

script.iCompare = enummemberscompare
scanner.AddScript(script)
