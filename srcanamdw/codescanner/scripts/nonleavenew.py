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
# nonleavenew.py
#
# Checks : Use of new without (ELeave).
#
# Reason : Using new without (ELeave) is only used in special 
# circumstances. The leaving variant should typically be used in 
# preference. A common exception is for application creation, 
# where NULL is returned for failed creation.
#
# #################################################################

script = CScript("nonleavenew")
script.iReString = r"""
	(=|\(|,)		# equals, open bracket or comma
	\s*				# optional whitespace
	new\s+			# "new" plus at least one whitespace char
	([^\(\s]		# a character other than a bracket
	.*)
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

currentfilename = ""
iswindowsfile = 0
rewindows = re.compile("^\s*#include\s+<(windows|wchar).h>", re.IGNORECASE)

def checkforwindowsinclude(lines, filename):
	global currentfilename
	global iswindowsfile
	global rewindows

	if (currentfilename <> filename):
		currentfilename = filename
		iswindowsfile = 0
		for line in lines:
			m = rewindows.search(line)
			if m:
				iswindowsfile = 1
				break

	return iswindowsfile

def nonleavenewcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if (m.group(2).find("Application") <> -1):
			return 0
		else:				
			return not checkforwindowsinclude(lines, filename)

	return 0

script.iCompare = nonleavenewcompare
scanner.AddScript(script)
