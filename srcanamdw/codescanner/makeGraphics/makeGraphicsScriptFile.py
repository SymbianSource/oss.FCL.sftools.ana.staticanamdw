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
# #################################################################
#!/usr/bin/python

import sys
import base64
import zlib

# sort out args
inputFilename = sys.argv[1]
outputFilename = sys.argv[2]

# read in file
inputFileHandle = open( inputFilename, 'rb' )
inputFileBinary = inputFileHandle.read()
inputFileHandle.close()


# apply ZLib compression and then convert to base64
outputFileBase64 = base64.encodestring( zlib.compress( inputFileBinary ) )

# output to file
outputFileHandle = open( outputFilename, 'w' )
outputFileHandle.write( "# ##############################################################\n# " + inputFilename + "\n\n" )
outputFileHandle.write( "encodedFile = CEncodedFile()\n" );
outputFileHandle.write( "encodedFile.iFilename = \"" + inputFilename + "\"\n" )
outputFileHandle.write( "encodedFile.iFileBody = \"\"\"\n" )
outputFileHandle.write( outputFileBase64 )
outputFileHandle.write( "\"\"\"\n\n" )
outputFileHandle.write( "encodedFileList.AddEncodedFile( encodedFile )\n\n" )
outputFileHandle.write( "# ##############################################################\n\n\n" )


outputFileHandle.close()


