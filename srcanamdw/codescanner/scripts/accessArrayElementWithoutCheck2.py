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
# accessArrayElementWithoutCheck2.py
#
# Checks : Array element accessed by [] without checking range.
#
# Reason : Whenever an element in an array is accessed, the index 
# should first be checked to ensure that it is within range. 
# CodeScanner checks for explicit calls to a Count() or Length() 
# function; so if the array index is checked in a different way, 
# it gives false positives. Accessing an invalid index can cause 
# a panic.
#
# #################################################################

script = CScript("accessArrayElementWithoutCheck2")
script.iReString = r"""
	\w+
	\s*		# optional whitespace
	\)*		# optional closing bracket
	\s*		# optional whitespace
	\[
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

accessArrayLengthFn = re.compile("""
	(\.|->)
	\s*
	Length
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

accessArrayDeclareNew = re.compile("""
	\s*
	=
	\s*
	new
	\s*
	""", re.VERBOSE)

bufferArrayDeclaration = re.compile("""
	\w+		# array type
	\s*
	<
	\s*
	[0-9]+
	\s*
	>
	\s*
	\w+		# array name
	\s*
	;
	""", re.VERBOSE)

accessArrayDeclaration = re.compile("""
	\w+		# array type
	\s*
	(\*|&)*
	\s*
	\[
	.*		# array size
	\]
	\s*
	;
	""", re.VERBOSE)

constArrayDeclaration = re.compile("""
	\w+		# array type
	[0-9<>*& ]*	# optional array element
	\s+
	\w+		# array name
	\s*
	\[
	.*		# array size
	\]
	\s*
	=
	[^=]
	""", re.VERBOSE)

def arrayAccessCompare2(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (accessArrayDeclareNew.search(line)):
			return 0

		if (accessArrayDeclaration.search(line)):
			return 0

		if (constArrayDeclaration.search(line)):
			return 0

		openBracketPos = line.find("[")
		cutLine = line[openBracketPos:]
		closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
		if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
			variable = line[openBracketPos:closeBracketPos]
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

			linePos = openBracketPos
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
						if (accessArrayLengthFn.search(cutLine)):
							return 0

					if (variableIsNumeric == 1):
						doCheck = 0
						if (accessArrayDeclaration.search(line)):
							openBracketPos = line.find("[")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									doCheck = 1

						if (bufferArrayDeclaration.search(line)):
							openBracketPos = line.find("<")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find(">") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									doCheck = 1

						if (doCheck == 1):
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

script.iCompare	= arrayAccessCompare2
scanner.AddScript(script)
