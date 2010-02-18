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
# forgottoputptroncleanupstack.py
#
# Checks : Neglected to put variable on cleanup stack.
#
# Reason : If a variable is not put on the cleanup stack and a 
# leaving function or ELeave is called, a memory leak occurs. 
# CodeScanner occasionally gives false positives for this issue. 
# Individual cases should be investigated.
#
# #################################################################

script = CScript("forgottoputptroncleanupstack")
script.iReString = r"""
	\s+				# optional whitespace
	[b-hj-z]+		# must not be a member or parameter
	[A-Za-z0-9]+	# variable name
	\s*				# optional whitespace
	=				# assignment operator
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

forgottoputptroncleanupstackCleanup = re.compile("""Cleanup""", re.VERBOSE)

forgottoputptroncleanupstackDeleteOp = re.compile("""
	\s+
	delete
	\s+
	""", re.VERBOSE)

forgottoputptroncleanupstackReturnCmd = re.compile("""
	(\s*|\()
	return
	(\s*|\()
	""", re.VERBOSE)

forgottoputptroncleanupstackSetFn = re.compile("""
	Set
	[A-Za-z0-9]+
	[A-KM-Za-z0-9]
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackBreak = re.compile("""
	\s+
	break
	\s*
	;
	""", re.VERBOSE)

forgottoputptroncleanupstackIf = re.compile("""
	\s+
	if
	\s*
	\(
	""", re.VERBOSE)
	
forgottoputptroncleanupstackElse = re.compile("""
	\}*
	\s*
	else
	\s*
	\{*
	""", re.VERBOSE)

forgottoputptroncleanupstackAssignToMember = re.compile("""
	i
	[A-Za-z0-9\[\]]+
	\s*
	=
	\s*
	.*
	\s*
	;
	""", re.VERBOSE)

forgottoputptroncleanupstackTrapMacro = re.compile("""
	TRAP
	[D]*
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

forgottoputptroncleanupstackLeaveAndDelete = re.compile("""
	L
	[D]+
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackNewOperator = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	""", re.VERBOSE)

forgottoputptroncleanupstackNewFunction = re.compile("""
	::NewL
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackCreateFunction = re.compile("""
	Create
	[A-Za-z0-9]+
	L
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackAllocFunction = re.compile("""
	Alloc
	L*
	\s*
	\(
	""", re.VERBOSE)

def findForgetCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		foundNew = 0
		equalPos = line.find("=")
		assignedSection = line[equalPos:]
	
		if forgottoputptroncleanupstackNewFunction.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackNewOperator.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackAllocFunction.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackCreateFunction.search(assignedSection):
			foundNew = 1

		# if this line contains a 'new', a 'NewL(', or an 'AllocL('
		if (foundNew == 1):	
			i = currentline

		# move to next line ending if this line doesn't contain one
			while (lines[i].find(';') == -1):
				i = i + 1

		# go to next line
			i = i + 1
			bracketdepth = GetBracketDepth(lines, i)
			
		# get the variable name, between the '*' and the '='
			startindex = line.find("*")
			if (startindex == -1):
				startindex = 0
			endindex = line.find("=")
			variable = line[startindex+1:endindex]
			if (len(variable) < 1):
				return 0
			variable = TrimVariableName(variable)

			inAnIfOrSelectStatement = 1 # possibly
			
			while (i < len(lines)):
				line2 = lines[i]

				if (line2.find('{') >= 0):
					bracketdepth = bracketdepth + 1
				if (line2.find('}') >= 0):
					bracketdepth = bracketdepth - 1
					inAnIfOrSelectStatement = 0
					if (bracketdepth == 0):
						return 0

				varIndex = line2.find(variable)
		# if a later line contains the variable...
				while (varIndex <> -1):
					if (isNonAlpha(line2[varIndex-1])):
						if (isNonAlpha(line2[varIndex+len(variable)])):
		# ...and delete, exit
							if forgottoputptroncleanupstackDeleteOp.search(line2):
								return 0
	
		# ...and an xxxLD() function, exit
							if forgottoputptroncleanupstackLeaveAndDelete.search(line2):
								return 0
							
		# ...and the variable is assigned to a member variable, exit
							if forgottoputptroncleanupstackAssignToMember.search(line2):
								return 0
		
		# ...and it is a Set...() call, exit (e.g. SetArray, SetAppUi)
							if forgottoputptroncleanupstackSetFn.search(line2):
								return 0

		# ...and a return command, exit 
							if forgottoputptroncleanupstackReturnCmd.search(line2):
								return 0

		# search this line again incase there are similarly named variables
					line2 = line2[varIndex+1:]
					varIndex = line2.find(variable)

				line2 = lines[i]
		# if a leaving function is called...
				if forgottoputptroncleanupstackLeavingFunction.search(line2):
		# ...if the leaving function is trapped, exit
					if forgottoputptroncleanupstackTrapMacro.search(line2):
						return 0
		# ...if a Cleanup function is called, exit
					if forgottoputptroncleanupstackCleanup.search(line2):
						return 0
		# ...otherwise this is a problem!
					return 1

		# if a User::Leave is called, this is a problem
				if forgottoputptroncleanupstackLeave.search(line2):
					return 1
	
		# if the variable is initialised in a branch of an 'if' or 'switch' statement, ignore other branches
				if (inAnIfOrSelectStatement == 1):
					if forgottoputptroncleanupstackBreak.search(line2):
						atLine = i
						inAnIfOrSelectStatement = 0
						findSwitch = i
						line3 = lines[findSwitch]
						while (line3.find("switch") == -1):
							findSwitch = findSwitch - 1
							if (findSwitch <= 0):
								return 0
							line3 = lines[findSwitch]
						switchBracketDepth = GetBracketDepth(lines, findSwitch)
						i = atLine
						while (bracketdepth > switchBracketDepth):
							if (i >= len(lines)):
								return 0
							line2 = lines[i]
							if (line2.find('{') >= 0):
								bracketdepth = bracketdepth + 1
							if (line2.find('}') >= 0):
								bracketdepth = bracketdepth - 1
							i = i + 1
							
					if forgottoputptroncleanupstackElse.search(line2):
						inAnIfOrSelectStatement = 0
						elseBracketDepth = bracketdepth
						if (line2.find('{') >= 0):
							elseBracketDepth = elseBracketDepth - 1
						if (elseBracketDepth == GetBracketDepth(lines, currentline)):
							while (line2.find(';') == -1):
								i = i + 1
								if (i >= len(lines)):
									return 0
								line2 = lines[i]
						else:
							while (bracketdepth > elseBracketDepth):
								i = i + 1
								if (i >= len(lines)):
									return 0
								line2 = lines[i]
								if (line2.find('{') >= 0):
									bracketdepth = bracketdepth + 1
								if (line2.find('}') >= 0):
									bracketdepth = bracketdepth - 1

					if forgottoputptroncleanupstackIf.search(line2):
						inAnIfOrSelectStatement = 0
				i = i + 1
			return 0

	return 0

script.iCompare	= findForgetCompare
scanner.AddScript(script)
