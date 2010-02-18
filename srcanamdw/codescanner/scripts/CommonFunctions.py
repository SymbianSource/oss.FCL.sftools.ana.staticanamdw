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
# CommonFunctions.py
#
# Some commonly used functions.
#
# #################################################################

KReStringLeavingLine = "(\w*[a-z]\w*L(C*|D|P))\s*\(|ELeave|User::Leave|tream\s+<<|tream\s+>>"

KReLeavingLine = re.compile(KReStringLeavingLine, re.VERBOSE)

def isNonAlpha(char):
	if (char >= 'A'):
		if (char <= 'Z'):
			return 0
	if (char >= 'a'):
		if (char <= 'z'):
			return 0
	if (char >= '0'):
		if (char <= '9'):
			return 0
	return 1

def TrimVariableName(var):
	while (len(var) > 0) and (isNonAlpha(var[0])):
		var = var[1:len(var)]
	while (len(var) > 0) and (isNonAlpha(var[len(var)-1])):
		var = var[0:len(var)-1]

	if (len(var) > 0):
		spaceIndex = var.find(" ")
		if (spaceIndex <> -1):
			cutVar = var[spaceIndex:]
			return TrimVariableName(cutVar)
	return var

def GetBracketDepth(lines, currentline):
	i = scanner.iCurrentMethodStart
	bracketdepth = 0
	while (i < currentline):
		thisline = lines[i]
		commentBegin = thisline.find("//")
		if (commentBegin != -1):
			thisline = thisline[:commentBegin]
		bracketdepth += thisline.count("{")
		bracketdepth -= thisline.count("}")
		i = i + 1

	return bracketdepth	

varDeclaration = re.compile("""
	\s*					# whitespace
	([A-Z]\w*)			# variable type
	\s*             	# whitespace
	(<.*>)?				# optional class in angle brackets
	\s*[\*&\s]\s*		# optional "*" or "&" plus at least one whitespace char
	(\w+)				# variable name
	\s*             	# whitespace
	[;\(=]				# ";" or "(" or "="
	""", re.VERBOSE)

def GetLocalVariableType(lines, currentline, varname):
	# skip non-local object
	if (len(varname) > 2):
		if (varname[0] == 'i'):
			return ""

	# lookup type of local variable or function parameter
	if (scanner.iCurrentMethodStart <> -1):
		i = scanner.iCurrentMethodStart
		while (i < currentline):
			line = lines[i]
			if (line.find(varname) <> -1):
				# look up variable declaration
				m = varDeclaration.search(line)
				if m:
					# return variable type
					return m.group(1)
			i = i + 1
	return ""
