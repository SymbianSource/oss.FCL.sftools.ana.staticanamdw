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
# worryingcomments.py
#
# Checks : Worrying comments.
#
# Reason : Typically, exclamation and question marks in comments 
# indicate that something odd is in the code or that it is 
# unfinished or not understood fully.
#
# #################################################################

script = CScript("worryingcomments")
script.iFileExts = ["h", "cpp", "c"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreQuotes
script.iSeverity = KSeverityLow

reWordsStr = r"""\!|\?|[Zz]{3}|kludge|workaround|\scrap|hack"""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("worryRE"):
		reWordsStr = wordNode.firstChild.nodeValue
		print "Note: 'worrying comments' pattern configured as: " + reWordsStr
		break
script.iReString = r"""
	/(/|\*)						# "//" or "/*"
	.*("""+reWordsStr+r""")		# skip to "!", "?", "zzz", "kludge", "workaround", " crap" or "hack"
	"""

def worryingcommentcodecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		line = lines[currentline]
		i = 0
		inCommentBlock = 0

		while i < len(line):
			if not inCommentBlock:
				if (line[i] == "/"):
					if (line[i + 1] == "/"):
						# note i+3 to bypass the character after the start of the comment as can be an in-source documentation directive
						return (line[i+3:].find("!")<>-1) or (line[i+3:].find("?")<>-1)
					elif (line[i + 1] == "*"):
						inCommentBlock = 1
						i += 2
						continue
			else:
				endIndex = line[i:].find("*/")
				if (endIndex <> -1):
					inCommentBlock = 0
					# note, that first character is ignored in comments as can be direction to the in-source documentation tool
					if (line[i+1:i + endIndex + 2].find("!") <> -1) or (line[i+1:i + endIndex + 2].find("?") <> -1):
						return 1
					i += endIndex + 2
					continue
				else:
					return 1			
			i += 1		
	return 0

script.iCompare = worryingcommentcodecompare
scanner.AddScript(script)
