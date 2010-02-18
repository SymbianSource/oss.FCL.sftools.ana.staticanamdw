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
# open.py
#
# Checks : Ignoring Open() return value.
#
# Reason : Ignoring the return value from Open() functions 
# (due to OOM, etc.) means that when the resource is accessed next, 
# a panic will result.
#
# #################################################################

script = CScript("open")
script.iReString = "^\s*(\w+)(\.|->)Open\s*\("
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reOpenIgnoreStr = ""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("openIgnoreRE"):
		reOpenIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following objects and classes when checking for open() return value: " + reOpenIgnoreStr
		break
if len(reOpenIgnoreStr) > 0:
	reOpenIgnores = re.compile(reOpenIgnoreStr, re.IGNORECASE)
else :
	reOpenIgnores = None

reOpenAssignStr = "=\s+$"
reOpenAssign = re.compile(reOpenAssignStr, re.IGNORECASE)

def streamcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		# ignore objects with the word "tream" in object name or object type
		objectName = m.group(1)
		if (objectName.find("tream") <> -1):
			return 0
		objectType = GetLocalVariableType(lines, currentline, objectName)
		if (objectType.find("tream") <> -1):
			return 0

		#ignore objects with either object name or object type on the ignored list
		if reOpenIgnores:
			if reOpenIgnores.search(objectName):
				return 0
			if reOpenIgnores.search(objectType):
				return 0

		# look for handler of Open() return value on a different line
		i = currentline - 1
		if (i > 0) and (i >= scanner.iCurrentMethodStart):
			line = lines[i]
			bracketCount = line.count("(") - line.count(")")
			if (bracketCount > 0):
				return 0
			r = reOpenAssign.search(line)
			if r:
				return 0
		return 1
	else:
		return 0

script.iCompare = streamcompare
scanner.AddScript(script)
