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
# crepository.py
#
# Checks : Ignoring CRepository::get() return value.
#
# Reason : Independent application cannot assume that the 
# Central Repository is set up fully. This means the return value 
# of CRepository::get() cannot be ignored.
#
# #################################################################

script = CScript("crepository")
script.iReString = r"""
    ^\s*
    (\w+)
    (\.|->)
    (G|g)et\s*\(
    """
script.iFileExts = ["cpp"]
script.iCategory = KCategoryOther
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reCRepositoryAssignStr = "=\s+$"
reCRepositoryAssign = re.compile(reCRepositoryAssignStr, re.IGNORECASE)

reCRepositoryConditionalStr = "(if|while)\s+\($"
reCRepositoryConditional = re.compile(reCRepositoryConditionalStr, re.IGNORECASE)

def crepositorycompare(lines, currentline, rematch, filename):
    m = rematch.search(lines[currentline])
    if m:
        objectName = m.group(1)
        objectType = GetLocalVariableType(lines, currentline, objectName)
        if (objectType.find("CRepository") == -1):
            return 0

        # look for handler of CRepository::get() return value on a different line
        i = currentline - 1
        if (i > 0) and (i >= scanner.iCurrentMethodStart):
            line = lines[i]
            bracketCount = line.count("(") - line.count(")")
            if (bracketCount > 0):
                return 0
            r1 = reCRepositoryAssign.search(line)
            if r1:
                return 0
            r2 = reCRepositoryConditional.search(line)
            if r2:
                return 0
        return 1
    else:
        return 0

script.iCompare = crepositorycompare
scanner.AddScript(script)
