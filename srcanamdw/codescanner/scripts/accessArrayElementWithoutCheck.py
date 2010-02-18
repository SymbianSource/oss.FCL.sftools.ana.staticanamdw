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
# accessArrayElementWithoutCheck.py
#
# Checks : Array element accessed by At() function without checking 
# index is within array range.
#
# Reason : Whenever an element in an array is accessed, the index 
# should be checked to ensure that it is less than array.Count(). 
# CodeScanner checks for explicit calls to a Count() function; so 
# if the array index is checked in a different way, it gives 
# false positives. Accessing an invalid index can cause a panic.
#
# #################################################################

script = CScript("accessArrayElementWithoutCheck")
script.iReString = r"""
	(->|\.)		# pointer/instance of array
	\s*			# optional whitespace
	At
	\s*			# optional whitespace
	\(			# opening bracket
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

accessArrayCountFn = re.compile("""
	(\.|->)
	\s*
	Count
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

accessArrayDeclaration = re.compile("""
	\w+			# array type
	[0-9<>*& ]*	# optional array element
	\w+			# array name
	\s*
	\[
	.*			# array size
	\]
	\s*
	;
	""", re.VERBOSE)

def isTimerObject(lines, currentline, varname):
	if (varname.lower().find("array") <> -1) or (varname.lower().find("list") <> -1):
		return False
	if (varname.lower().find("heartbeat") <> -1):
		return True
	if (varname.lower().find("periodic") <> -1):
		return True
	if (varname.lower().find("timer") <> -1):
		return True

	vartype = GetLocalVariableType(lines, currentline, varname)
	if (len(vartype) > 0):
		if (vartype.lower().find("array") <> -1) or (vartype.lower().find("list") <> -1):
			return False
		if (vartype.lower().find("heartbeat") <> -1):
			return True
		if (vartype.lower().find("periodic") <> -1):
			return True
		if (vartype.lower().find("timer") <> -1):
			return True

	return False

def arrayAccessCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (line.count("At") == 1):
			openBracketPos = line.find("At")
		else:
			openBracketPos = line.find("At(")
		cutLine = line[openBracketPos+1:]
		closeBracketPos = cutLine.find(")") + len(line) - len(cutLine)
		if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
			variable = line[openBracketPos+3:closeBracketPos]
			variable = TrimVariableName(variable)

			if (len(variable) == 0):
				return 0

			# if a constant index assume it's going to be ok!
			if (variable[0] == "E") or (variable[0] == "K"):
				return 0

			variableIsNumeric = 1
			varPos = 0
			while (varPos < len(variable)):
				if (variable[varPos] < '0') or (variable[varPos] > '9'):
					variableIsNumeric = 0
					break
				varPos = varPos + 1

			linePos = openBracketPos - 1
			while (linePos > 0) and (isNonAlpha(line[linePos])):
				linePos = linePos - 1
			arrayNameEnd = linePos + 1
			while (linePos >= 0) and (isNonAlpha(line[linePos]) == 0):
				linePos = linePos - 1
			arrayNameStart = linePos + 1
		
			arrayName = ""
			if (arrayNameStart >= 0):
				arrayName = line[arrayNameStart:arrayNameEnd]
				arrayName = TrimVariableName(arrayName)

				if (len(arrayName) > 0):
					# if a constant array assume it's going to be ok!
					if (arrayName[0] == "E") or (arrayName[0] == "K"):
						return 0

					# ignore any heartbeat/periodic/timer object that is not an array or list
					if isTimerObject(lines, currentline, arrayName):
						return 0

			if (variableIsNumeric):
				if (len(arrayName) > 2):
					if (arrayName[0] == "i") and (arrayName[1] >= 'A') and (arrayName[1] <= 'Z'):
						return 0 

			i = currentline

			while (i >= 0) and (i >= scanner.iCurrentMethodStart):
				line = lines[i]

				# check to see if index is compared to array size
				if (len(arrayName) > 0):
					arrayNamePos = line.find(arrayName)
					if (arrayNamePos >= 0):
						cutLine = line[arrayNamePos + len(arrayName):]
						if (accessArrayCountFn.search(cutLine)):
							return 0

					if (variableIsNumeric == 1):
						if (accessArrayDeclaration.search(line)):
							openBracketPos = line.find("[")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									# if a constant index assume it's going to be ok!
									if (declVariable[0] == "E") or (declVariable[0] == "K"):
										return 0

								declVariableIsNumeric = 1
								varPos = 0
								while (varPos < len(declVariable)):
									if (declVariable[varPos] < '0') or (declVariable[varPos] > '9'):
										declVariableIsNumeric = 0
										break
									varPos = varPos + 1
								if (declVariableIsNumeric == 1):
									if (int(variable) < int(declVariable)):
										return 0

				i = i - 1
			return 1

	return 0

script.iCompare	= arrayAccessCompare
scanner.AddScript(script)
