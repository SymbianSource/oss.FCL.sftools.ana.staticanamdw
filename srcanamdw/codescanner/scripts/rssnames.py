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
# rssnames.py
#
# Checks : Duplicate RSS names.
#
# Reason : Resource files with clashing NAME fields can cause the 
# wrong resource file to be accessed. This can lead to incorrect 
# functionality or panics.
#
# #################################################################

script = CScript("rssnames")
script.iReString = "^\s*NAME\s+(\w+)"
script.iFileExts = ["rss"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

rssnames = []

def rsscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		text = m.group(1).lower()
		shortfilename = filename[filename.rfind("/") + 1:].lower()
		for pair in rssnames:
			if (pair[0] == text):
			 	if (pair[1] == shortfilename):
					return 0
				else:
					scanner.iRendererManager.ReportAnnotation(pair[2])
					return 1

		rssnames.append([text, shortfilename, filename])
		return 0
	else:
		return 0

script.iCompare = rsscompare
scanner.AddScript(script)
