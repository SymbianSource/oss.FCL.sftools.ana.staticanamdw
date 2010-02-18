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
# arrayptrcleanup.py
#
# Checks : Using local CArrayPtr classes without cleanup items.
#
# Reason : It is not enough to push a local CArrayPtr class onto 
# the cleanup stack. A TCleanupItem and callback function must be 
# used to avoid leaking the elements.
#
# #################################################################

script = CScript("arrayptrcleanup")
script.iReString = r"""
	\s+
	(
	\w+
	)
	\s*
	=
	\s*
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	\s*
	CArrayPtr
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def arrayptrcleanupcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		varName = m.group(1)
		if (len(varName) == 1) or (varName[0] not in "ai") or varName[1].islower():
			for i in range(currentline, currentline + 10):
				if i >= len(lines):
					break
				elif (lines[i].find("TCleanupItem") <> -1) and (lines[i].find(varName) <> -1):
					return 0
			return 1
	return 0

script.iCompare = arrayptrcleanupcompare
scanner.AddScript(script)
