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
# customizableicons.py
#
# Checks : Use of customizable icons.
#
# Reason : Due to device customization requirements, independent 
# application must not remove any customization done by the 
# variant team. This means independent application cannot include 
# customizable icons.
#
# #################################################################

script = CScript("customizableicons")
script.iReString = ""
script.iFileExts = ["mk", "mmp"]
script.iCategory = KCategoryOther
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reCustomizableIconsStr = ""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
    for wordNode in scriptNode.getElementsByTagName("iconsRE"):
        reCustomizableIconsStr = wordNode.firstChild.nodeValue
        print "Note: 'customizable icons' pattern configured as:  " + reCustomizableIconsStr
        break
if len(reCustomizableIconsStr) > 0:
    reCustomizableIcons = re.compile(reCustomizableIconsStr, re.IGNORECASE)
else:
    reCustomizableIcons = None

def customizableIconsCompare(lines, currentline, rematch, filename):
    if reCustomizableIcons:
        return reCustomizableIcons.search(lines[currentline])

script.iCompare = customizableIconsCompare
scanner.AddScript(script)
