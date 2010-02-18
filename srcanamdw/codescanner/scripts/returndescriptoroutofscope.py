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
# returndescriptoroutofscope.py
#
# Checks : Return descriptor out of scope.
#
# Reason : Returning a TBuf descriptor that is declared locally 
# takes it out of scope. This can cause a crash on WINSCW, although 
# not on WINS.
#
# #################################################################

script = CScript("returndescriptoroutofscope")
script.iReString = r"""
	TBuf
	\s*
	<
	[A-Za-z0-9]+
	>
	\s*
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reReturnValue = re.compile("""
	return
	\s*
	""", re.VERBOSE)

reOpenCurlyBracket = re.compile("""
	{
	""", re.VERBOSE)

reCloseCurlyBracket = re.compile("""
	}
	""", re.VERBOSE)

def finddescriptor(line, descriptor):
	startindex = line.find(descriptor)
	if (startindex <> -1):
		if (line[startindex] == " "):
			if (line[startindex + len(descriptor)] == ";"):
				return 1
	return 0

def returnvaluecompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		startindex = line.find(">");
		endindex = line.find(";");

		if (startindex <> -1):
			descriptor = line[startindex+1:endindex]

			i = currentline
			bracketdepth = 1
			while (i+1 < len(lines)):
				i = i + 1
				line2 = lines[i]

				if reReturnValue.search(line2):
					if (finddescriptor(line2, descriptor)):
						return 1

				if reOpenCurlyBracket.search(line2):
					bracketdepth = bracketdepth + 1

				if reCloseCurlyBracket.search(line2):
					bracketdepth = bracketdepth - 1
					if (bracketdepth == 0):
						return 0

	return 0

script.iCompare	= returnvaluecompare
scanner.AddScript(script)
