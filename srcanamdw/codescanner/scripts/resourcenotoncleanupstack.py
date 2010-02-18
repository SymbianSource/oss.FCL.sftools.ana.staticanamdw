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
# resourcenotoncleanupstack.py
#
# Checks : Neglected to put resource objects on cleanup stack.
#
# Reason : If a stack-based resource object is not put on the 
# cleanup stack with CleanupResetAndDestroyPushL() or 
# CleanupClosePushL(), and a leaving function or ELeave is called, 
# a memory leak occurs. CodeScanner occasionally gives false 
# positives for this issue. Individual cases should be investigated.
#
# #################################################################

script = CScript("resourcenotoncleanupstack")
script.iReString = r"""
	^\s*					# start of line plus optional whitespace
	R\w+					# resource type
	\s*						# optional whitespace
	(<.*>)?					# optional class in angle brackets
	\s+						# whitespace
	(\w+)					# object name
	\s*						# optional whitespace
	;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

cleanupFunction = re.compile("""
	\s*						# optional whitespace
	(CleanupClosePushL|CleanupResetAndDestroyPushL)
	\s*						# optional whitespace
	\(
	\s*						# optional whitespace
	(\w+)					# object name
	\s*						# optional whitespace
	\)
	\s*						# optional whitespace
	;
	""", re.VERBOSE)

def resourcecompare(lines, currentline, rematch, filename):
    m = rematch.search(lines[currentline])
    if m:
    	objectName = m.group(2)
    	bracketdepth = GetBracketDepth(lines, currentline)
    	i = currentline

    	# search for CleanupClosePushL() or CleanupResetAndDestroyPushL() 
    	# with the resource object at parameter
    	while (i < len(lines)):
    		nextLine = lines[i]
    		
    		match = cleanupFunction.search(nextLine)
    		if (match):
    			if objectName == match.group(2):
    				return 0

    		if (nextLine.find('{') >= 0):
    			bracketdepth = bracketdepth + 1
    		if (nextLine.find('}') >= 0):
    			bracketdepth = bracketdepth - 1
    			if (bracketdepth == 0):
    				return 1

    		i += 1

	return 0

script.iCompare = resourcecompare
scanner.AddScript(script)
