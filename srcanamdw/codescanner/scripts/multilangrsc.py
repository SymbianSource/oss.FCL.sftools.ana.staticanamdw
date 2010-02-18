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
# multilangrsc.py
#
# Checks : Not using BaflUtils::NearestLanguageFile() when loading 
# a resource file.
#
# Reason : If AddResourceFileL() is used without first using 
# BaflUtils::NearestLanguageFile(), then not all language versions 
# of resources will be picked up.
#
# #################################################################

script = CScript("multilangrsc")
script.iReString = """
	AddResourceFileL
	\s*
	\(
	\s*\w+.*
	\)
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reBaflNearestLanguage = re.compile("""
	\s*
	BaflUtils::NearestLanguageFile
	\s*
	\(
	\s*\w+.*
	\)
	""", re.VERBOSE)

def multilangrsccompare(lines, currentline, rematch, filename):
	if (scanner.iCurrentMethodName <> ""):
		m = rematch.search(lines[currentline])
		if m:
			scanLineNum = currentline
			while (scanLineNum>scanner.iCurrentMethodStart):
				addResMatch = reBaflNearestLanguage.search(lines[scanLineNum])
				if addResMatch:
					return 0
				scanLineNum = scanLineNum - 1
			return 1
	return 0

script.iCompare = multilangrsccompare
scanner.AddScript(script)
