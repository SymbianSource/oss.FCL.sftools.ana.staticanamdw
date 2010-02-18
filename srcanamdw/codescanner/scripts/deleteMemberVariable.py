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
# deleteMemberVariable.py
#
# Checks : Member variable deleted incorrectly.
#
# Reason : When a member variable is deleted, it should be assigned 
# either to NULL or to another value. This prevents accidental 
# access of the deleted object. If a NewL() or other leaving 
# function is called to reassign the member variable, it should 
# first be assigned to NULL in case that function leaves.
#
# #################################################################

script = CScript("deleteMemberVariable")
script.iReString = r"""
	delete		# delete command
	\s*			# optional space
	\(*			# optional open bracket
	\s*			# optional space
	i[A-Z]		# member variable name
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

deleteMemberVariableLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D)*
	\s*
	\(
	""", re.VERBOSE)

deleteMemberVariableNewELeave = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	""", re.VERBOSE)

deleteMemberVariableLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

deleteMemberVariableArrayDeletion = re.compile("""
	(\.|->)
	\s*
	Delete
	\s*
	\(
	""", re.VERBOSE)

deleteMemberVariableArrayDeletion2 = re.compile("""
	(\.|->)
	\s*
	Remove
	\s*
	\(
	""", re.VERBOSE)

def deleteMemberVariableCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (scanner.iCurrentMethodName.find(scanner.iCurrentClassName) > -1):
			return 0

		deletingArrayMember = 0
		if (line.find("[")):
			deletingArrayMember = 1

		# get the variable name, between the 'delete' and the ';'
		endindex = line.find(";")
		if (endindex == -1):
			endindex = len(line)
		startindex = line.find("delete")
		variable = line[startindex+6:endindex]
		variable2 = TrimVariableName(variable)

		bracketdepth = GetBracketDepth(lines, currentline)

		i = currentline
		while (i < len(lines)):
			nextLine = lines[i]

			if deleteMemberVariableLeavingFunction.search(nextLine):
				return 1
			if deleteMemberVariableLeave.search(nextLine):
				return 1
			if deleteMemberVariableNewELeave.search(nextLine):
				return 1
			
			if (deletingArrayMember == 1):
				if (nextLine.find(variable2)):
					if deleteMemberVariableArrayDeletion.search(nextLine):
						return 0
					if deleteMemberVariableArrayDeletion2.search(nextLine):
						return 0

			foundAssignment = nextLine.find("=")
			if (foundAssignment > -1 and nextLine[foundAssignment+1] != "="):
				assigned = nextLine[:foundAssignment]
				if (assigned.find(variable2)):
					return 0

			if (nextLine.find('{') >= 0):
				bracketdepth = bracketdepth + 1
			if (nextLine.find('}') >= 0):
				bracketdepth = bracketdepth - 1
				if (bracketdepth == 0):
					return 1

			i = i + 1
	return 0

script.iCompare	= deleteMemberVariableCompare
scanner.AddScript(script)
