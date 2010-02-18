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
# uncompressedbmp.py
#
# Checks : Uncompressed bitmaps in ROM.
#
# Reason : Using uncompressed bitmaps can significantly bloat the 
# size of ROM images. All occurrences of "bitmap=" in iby/hby files 
# should be replaced with "auto-bitmap=". Also, including bitmaps 
# using "data=" or "file=" causes bloat and load-speed reductions.
#
# #################################################################

script = CScript("uncompressedbmp")
script.iReString = r"""
			(

			^
			\s*
			bitmap
			\s*
			=
			
			|

			^
			\s*
			(data|file)
			\s*
			=
			.*
			\.mbm
			)
			"""
script.iFileExts = ["iby", "hby", "oby"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)
