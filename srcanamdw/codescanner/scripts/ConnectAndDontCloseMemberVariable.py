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
# ConnectAndDontCloseMemberVariable.py
#
# Checks : Calling Connect() or Open() on a member variable without 
# calling Close() in the destructor.
#
# Reason : If Connect() or Open() is called on any member variable, 
# then Close() must be called in the destructor.
#
# #################################################################

script = CScript("ConnectAndDontCloseMemberVariable")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	i[A-Z]\w+			# member variable name
	(\.|->)				# "." or "->"
	(Connect|Open)
	\s*\(\s*\)
	\s*;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

ConnectAndDontCloseLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D|P)*
	\s*
	\(
	""", re.VERBOSE)

def ConnectNotCloseCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		# get the variable name, between the '*' and the '='
		startindex = line.find("i")
		if (startindex == -1):
			startindex = 0
		endindex = line.find("Connect")
		if (endindex == -1):
			endindex = line.find("Open")
		variable = line[startindex:endindex]
		if (len(variable) < 1):
			return 0
		variable = TrimVariableName(variable)

		# see if variable is closed within this function before a Leave
		i = currentline
		bracketdepth = GetBracketDepth(lines, i)
		while (i < len(lines)) and (bracketdepth  > 0):
			line = lines[i]
			if (line.find(variable) >= 0):
				if (line.find("Close") >= 0):
					return 0

			bracketdepth += line.count("{")
			bracketdepth -= line.count("}")

			if (line.find("User::Leave") >= 0):
				bracketdepth = 0
			if (line.find("ELeave") >= 0):
				bracketdepth = 0
			if (ConnectAndDontCloseLeavingFunction.search(line)):
				bracketdepth = 0
				
			i = i + 1
		
		# look for destructor and see if variable is closed there
		stringToFind = "~" + scanner.iCurrentClassName
		i = 1
		foundDestructor = 0
		bracketdepth = 0
		while (i < len(lines)):
			thisLine = lines[i]
			if (thisLine.find(stringToFind) >= 0) and (foundDestructor == 0):
				while (i < len(lines)) and (foundDestructor == 0):
					thisLine = lines[i]
					if (thisLine.find('{') >= 0):
						foundDestructor = 1
					else:
						i = i + 1

			if (foundDestructor):
				bracketdepth += thisLine.count("{")
				bracketdepth -= thisLine.count("}")
				if (bracketdepth == 0):
					return 1
				
				if (thisLine.find(variable) >= 0):
					if (thisLine.find("Close") >= 0):
						return 0
			i = i + 1

		if (foundDestructor):
			return 1
	return 0

script.iCompare	= ConnectNotCloseCompare
scanner.AddScript(script)
