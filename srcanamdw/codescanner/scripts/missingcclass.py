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
# missingcclass.py
#
# Checks : C class not inheriting from another C class.
#
# Reason : All C classes should inherit from another C class to 
# ensure that all data members are zeroed.
#
# #################################################################

script = CScript("missingcclass")
script.iReString = r"""
	^\s*
	class
	\s+
	(\w+::)?
	(\w+)
	\s*
	(.*)"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reCClassIgnoreStr = ""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("cclassIgnoreRE"):
		reCClassIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following classes when checking for C class not inheriting from another C class: " + reCClassIgnoreStr
		break
if len(reCClassIgnoreStr) > 0:
	reCClassIgnores = re.compile(reCClassIgnoreStr, re.IGNORECASE)
else :
	reCClassIgnores = None

def missingcclasscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		className = m.group(2)
		if className[0] <> "C" or (len(className) == 1) or not className[1].isupper():
			return 0

		#ignore classes on the ignored list
		if reCClassIgnores:
			if reCClassIgnores.search(className):
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

		ccount = 0
		for classname in classlist:
			if (len(classname) > 2) and classname[0] == "C" and classname[1].isupper():
				ccount += 1
				
		if ccount == 0:
			return 1
		else:
			return 0
	else:
		return 0

script.iCompare = missingcclasscompare
scanner.AddScript(script)
