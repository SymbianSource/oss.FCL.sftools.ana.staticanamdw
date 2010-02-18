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
# arraypassing.py
#
# Checks : Passing arrays by value rather than reference.
#
# Reason : Passing arrays by value causes the array to be copied 
# needlessly, which takes up time and memory. For efficiency, 
# references should be used.
#
# #################################################################

script = CScript("arraypassing")
script.iReString = r"""
    (\(|,)?         # open bracket or preceeding comma
    \s*             # whitespace
	(R|C)\w*Array	# skip to a parameter type containing "R...Array..." or "C...Array..."
    \s*				# whitespace
	(<.*>)?			# optional class in angle brackets
	\s+				# whitespace
	(\w+)			# parameter name
    (=|\w|\s)*      # optional parameter initialization or whitespace
    (\)|,)			# close bracket or trailing comma
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium
script.iCompare = DefaultFuncParamCompare

scanner.AddScript(script)
