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
# noleavetrap.py
#
# Checks : TRAP used with no leaving functions.
#
# Reason : A TRAP is unnecessary if there are no leaving functions.
#
# #################################################################

script = CScript("noleavetrap")
script.iReString = "^\s*TRAPD?"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reLeave = re.compile("(L[CDP]?\s*\(|ELeave|\)\s*\(|<<|>>)")

def noleavetrapcompare(lines, currentline, rematch, filename):
    line = lines[currentline]
    m = rematch.search(line)
    if m:
    	if (line.find("(") == -1) and (currentline + 1 < len(lines)):
    		currentline += 1
    		line = lines[currentline]

        bracketCount = line.count("(") - line.count(")")
        found = reLeave.search(line) 

        while (bracketCount > 0) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]
            bracketCount += line.count("(") - line.count(")")
            if not found:
                found = reLeave.search(line) 

        if found:
            return 0
        else:
        	return 1

    return 0

script.iCompare = noleavetrapcompare
scanner.AddScript(script)
