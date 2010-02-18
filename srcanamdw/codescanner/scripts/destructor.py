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
# destructor.py
#
# Checks : Pointer access in destructors.
# 
# Reason : Accessing pointers to objects in destructors without 
# checking whether they are not NULL could result in a panic, since
# they may not have been constructed. The pointers should be
# checked to determine whether they are owned objects. If they are
# not owned, they should really be references rather than pointers.
#
# #################################################################

script = CScript("destructor")
script.iReString = r"""
	^\s*
	\w+
	\s*
	::~
	\s*
	\w+
	\(
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

remember = re.compile("(i[A-Z]\w*)(.+)")
reguard = re.compile("^\s*(if|while)(.*)({|$)")

def findguard(lines, currentline, destructorstartline, membername):
	i = currentline
	line = lines[i]

	while (i > destructorstartline):
		line = lines[i]
		m = reguard.search(line)
		if m:
			index = m.group(2).find(membername)
			if (index <> -1):
				if (line[index - 1:index] <> "*") and (line[index + len(membername):index + len(membername) + 2] <> "->"):
					return 1
		i = i - 1

	return 0

def destructorcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		openbracecount = 0
		closebracecount = 0
		checkline = currentline

		while (checkline < len(lines)):
			line = lines[checkline]
			openbracecount += line.count("{")
			closebracecount += line.count("}")
			member = remember.search(line)
			if member and ((member.group(2)[:2] == "->") or (line[member.start()-1:member.start()] == "*" and member.group(2)[:1] <> ".")):
				membername = member.group(1)
				if (membername.upper()[-3:] == "ENV") or findguard(lines, checkline, currentline, membername) <> 0:
					return 0
				else:
					return 1

			if (openbracecount and (openbracecount - closebracecount == 0)):
				break
			checkline += 1

	return 0

script.iCompare	= destructorcompare
scanner.AddScript(script)
