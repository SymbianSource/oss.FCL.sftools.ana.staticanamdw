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
# commentcode.py
#
# Checks : Commented-out code.
#
# Reason : Instances of code that are commented out make the code 
# hard to maintain and to interpret clearly. The commented out code 
# should be removed. Any requirement to rediscover old code 
# should be made through source control and not by trawling through 
# commented-out code.
#
# #################################################################

script = CScript("commentcode")
script.iReString = r"""
	/(/|\*)			# "//" or "/*"
	(.*);			# skip to semicolon
	\s*				# optional whitespace
	(//.*)?			# optional comment
	$				# end of line
	"""
script.iFileExts = ["h","cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreQuotes
script.iSeverity = KSeverityLow

reDeclaration = re.compile("""
	\s*
	[A-Z][\w<>*&]+
	\s+
	\w+
	\s*
	""", re.VERBOSE)

def commentcodecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if ((m.group(2)[-1:] == ")") or (m.group(2).find("=") <> -1)) or (reDeclaration.match(m.group(2))):
			line = lines[currentline]
			i = 0
			inCommentBlock = 0

			while i < len(line):
				if not inCommentBlock:
					if (line[i] == "/"):
						if (line[i + 1] == "/"):
							return 1
						elif (line[i + 1] == "*"):
							inCommentBlock = 1
							i += 2
							continue
				else:
					endIndex = line[i:].find("*/")
					if (endIndex <> -1):
						inCommentBlock = 0
						if line[i:i + endIndex + 2].find(";") <> -1:
							return 1
						i += endIndex + 2
						continue
					else:
						return 1
				
				i += 1
		
	return 0

script.iCompare = commentcodecompare
scanner.AddScript(script)

