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
# tcclasses.py
#
# Checks : T classes inheriting from C classes.
#
# Reason : T classes that are derived from C classes may have a 
# complex constructor and so need to be handled differently. 
# It is better to make the T class into a C class, which will make 
# the code easier to maintain.
#
# #################################################################

script = CScript("tcclasses")
script.iReString = r"""
	class
	\s+					# at least one whitespace char
	(\w+::)?
	(\w+)				# T class
	\s*					# optional whitespace
	:
	(.*)				# save inheritance text as group 1
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

def tcclasscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		className = m.group(2)
		if className[0] <> "T" or (len(className) == 1) or not className[1].isupper():
			return 0

		inheritanceString = m.group(3)
		i = currentline + 1
		while (inheritanceString.find("{") == -1) and i < len(lines):
			if (inheritanceString.find(";") <> -1):
				return 0
			inheritanceString += lines[i]
			i += 1	

		inheritancelist = inheritanceString.split(",")
		reclass = re.compile("[\s:]*(public|protected|private)?\s*([\w:]+)")
		classlist = []
		for inheritance in inheritancelist:
			match = reclass.search(inheritance)
			if match:
				inheritclass = match.group(2)
				colonpos = inheritclass.rfind(":")
				if (colonpos <> -1):
					inheritclass = inheritclass[colonpos + 1:]
				classlist.append(inheritclass)

		for classname in classlist:
			if (len(classname) > 2) and classname[0] == "C" and classname[1].isupper():
				return 1
	return 0

script.iCompare = tcclasscompare
scanner.AddScript(script)
