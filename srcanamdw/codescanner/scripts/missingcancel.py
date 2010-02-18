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
# missingcancel.py
#
# Checks : Cancel() not called in active object's destructor.
# 
# Reason : Cancel() should always be called in active object's 
# destructor to cancel an outstanding request if there is one. 
# If there is no request pending then Cancel() just does nothing, 
# but if we do not call Cancel() when having an outstanding request 
# a panic will be raised. CodeScanner occasionally gives false 
# positives for this issue. Individual cases should be 
# investigated.
#
# #################################################################

script = CScript("missingcancel")
script.iReString = r"""
    ::
    \s*        # optional whitespace
    ~C(\w+)
    """
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

# possible active and timer object types
activeObjectType = re.compile("\w+Active$")
timerObjectType = re.compile("\w+Timer$")

cancelFunction = re.compile("""
    Cancel
    \s*
    \(
    """, re.VERBOSE)

def isActiveDestructor(destructorType):
    if (activeObjectType.match(destructorType)) or (timerObjectType.match(destructorType)):
        return True
    return False

def cancelcompare(lines, currentline, rematch, filename):
    line = lines[currentline]
    m = rematch.search(line)

    if m:
        destructorType = m.group(1)
        # skip non-active types
        if (not isActiveDestructor(destructorType)):
            return 0

        i = currentline

        # find opening { in function
        while (line.count("{") == 0):
            i = i + 1
            if (i >= len(lines)):
                return 1
            line = lines[i]

        # if one-line or empty function
        if (line.count("}") > 0):
            if (cancelFunction.search(line)):
                return 0
            else:
                return 1

        i = i + 1
        bracketDepth = 1
        while (i < len(lines)):
            line = lines[i]
            if (cancelFunction.search(line)):
                return 0

            bracketDepth += line.count("{") - line.count("}")
            if (bracketDepth == 0):
                return 1
            i = i + 1
    return 0

script.iCompare = cancelcompare
scanner.AddScript(script)
