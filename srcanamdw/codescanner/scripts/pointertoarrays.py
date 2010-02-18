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
# pointertoarrays.py
#
# Checks : Pointer to arrays as members of a C class.
#
# Reason : In C classes, there is no need to use pointers to arrays 
# as data members. Instead, use the arrays themselves. Using 
# pointers leads to obscure notation like \"(*array)[n]\" for the 
# more usual \"array[n]\". It also makes it necessary to explicitly 
# delete the arrays in the destructor. Using the arrays themselves 
# also simplifies notation, reduces indirection, and reduces heap 
# fragmentation.
#
# #################################################################

script = CScript("pointertoarrays")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	[CR]\w*Array\w*		# class name e.g. RPointerArray
    (|<\w*>)			# optional "<Xxxx>" part
	\s*\*				# "*" (with optional whitespace)
	\s*i[A-Z]			# optional whitespace followed by the starting i of the member variable and then a capital letter
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

def pointerToArraysCompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if (len(scanner.iCurrentClassName) > 1)  and (scanner.iCurrentClassName[0]=="C"):
			return 1    # only a problem with C classes
		else:
			return 0    
	else:
		return 0

script.iCompare = pointerToArraysCompare
script.iDisplayMethodName = 0
script.iDisplayClassName = 1

scanner.AddScript(script)
