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
# ctltargettype.py
#
# Checks : Use of targettype ctl.
#
# Reason : The ctl target type should not be used. Instead, use DLL 
# and explicitly refer to the Control Panel's DEF file. 
# Note: Code that causes this issue only needs attention if it is 
# found in code developed for Nokia Series 90 code that has extra 
# exports for resetting the Control Panel item's data.
#
# #################################################################

script = CScript("ctltargettype")
script.iReString = r"""
	^\s*
	[Tt][Aa][Rr][Gg][Ee][Tt][Tt][Yy][Pp][Ee]
	\s+
	"""
script.iFileExts = ["mmp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

reTargetPath = re.compile("""
	^\s*
	[Tt][Aa][Rr][Gg][Ee][Tt][Pp][Aa][Tt][Hh]
	\s+
	""", re.VERBOSE)

reDefFile = re.compile("""
	^\s*
	[Dd][Ee][Ff][Ff][Ii][Ll][Ee]
	""", re.VERBOSE)
	
def ctltargettypecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if lines[currentline].upper().find("CTL") <> -1:
			return 1

		if lines[currentline].upper().find("DLL") <> -1:
			foundDefFile = 0
			foundSystemControls = 0

			for line in lines:
				if reTargetPath.search(line):
					if line.upper().find("SYSTEM\\CONTROLS") <> -1:
						foundSystemControls = 1

				if reDefFile.search(line):
					if line.upper().find("CTRL.DEF") <> -1:
						foundDefFile = 1

				if (foundSystemControls == 1) and (foundDefFile == 1):
					break
		
			if (foundSystemControls == 1) and (foundDefFile <> 1):
				return 1
			
	return 0

script.iCompare	= ctltargettypecompare
scanner.AddScript(script)
