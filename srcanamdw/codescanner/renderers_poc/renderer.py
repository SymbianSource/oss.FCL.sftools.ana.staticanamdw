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


# experimentation

# #############################################################
class CRendererBase:
    def RegisterSelf( self, aName, aDescription, aRendererManager ):
        self.iName = aName
        self.iDescription = aDescription
        aRendererManager.AddRenderer( self )
        
    def DoBeginTest( self, aTestName ):
        return

    def DoEndTest( self, aTestName ):
        return

    def DoReportError( self, aFile, aLine, aResult ):
        return

    iName = "CRendererBase!"
    iDescription = ""


class CRendererManager:
    def __init__( self ):
        # declare associative list of renderers
        self.iRendererList = {}

    def AddRenderer( self, aRenderer ):
        self.iRendererList[ aRenderer.iName ] = aRenderer
        print( "Added " + aRenderer.iName )

    def ListRenderers( self ):
        print( "Renderers:" )        
        for name, renderer in self.iRendererList.items():
            print( "\t" + name + "\t" + renderer.iDescription  )

        print( "" )


    def BeginTest( self, aTestName ):
        for name, renderer in self.iRendererList.items():
            renderer.DoBeginTest( aTestName )

    def EndTest( self, aTestName ):
        for name, renderer in self.iRendererList.items():
            renderer.DoEndTest( aTestName )

    def ReportError( self, aFile, aLine, aResult ):
        for name, renderer in self.iRendererList.items():
            renderer.DoReportError( aFile, aLine, aResult )


# #############################################################


# renderers are to be dropped in arbitarily, much like test scripts, images and embedded files
# rest of linescanners uses them via the RendererManager instance.

# #############################################################
class CHtmlRenderer( CRendererBase ):
    def __init__( self, aRendererManager ):
        self.RegisterSelf( "html", "Classic CodeScanner browsable HTML tree", aRendererManager )
        
    def DoBeginTest( self, aTestName ):
        self.iFileHandle = open( aTestName + ".html", "w" )
        self.iFileHandle.write( "<html>\n<body>\n<h1>" + aTestName + "</h1>\n" )

    def DoEndTest( self, aTestName ):
        self.iFileHandle.write( "</body>\n</html>\n" )
        self.iFileHandle.close()

    def DoReportError( self, aFile, aLine, aResult ):
        self.iFileHandle.write( "<i>" + aResult + "</i> at " + str( aLine ) + "<br/>\n" )

# #############################################################



# #############################################################
class CMsdevRenderer( CRendererBase ):
    def __init__( self, aRendererManager ):
        self.RegisterSelf( "msdev", "Classic MIScan plugin for MSDEV", aRendererManager )

    def DoBeginTest( self, aTestName ):
        self.iErrorCount = 0
        return
    
    def DoEndTest( self, aTestName ):
        print( "\n\n" + str( self.iErrorCount ) + " total errors" )
        return
    
    def DoReportError( self, aFile, aLine, aResult ):
        self.iErrorCount += 1
        # :\Series60Ex\menu\src\aknexmenusubcontainer.cpp(126) : warning: to do comment
        print( aFile + "(" + str( aLine ) + ") : " + aResult )
    

# #############################################################

# objects register themselves with rendererManager
rendererManager = CRendererManager()

CHtmlRenderer( rendererManager )
CMsdevRenderer( rendererManager )

rendererManager.ListRenderers()


errorCasesFiles = [ "moose.cpp",
                    "lama.cpp",
                    "underflow.cpp",
                    "wankers.cpp" ]

errorCasesLines = [ 56,
                    23,
                    67,
                    42 ]

errorCasesMessages = [ "moose farmer in field",
                       "lama shags sheep",
                       "out of budget",
                       "DELL are bad people" ]



rendererManager.BeginTest( "arbitarytest case" )
for file, line, error in zip( errorCasesFiles, errorCasesLines, errorCasesMessages ):
    rendererManager.ReportError( file, line, error )

rendererManager.EndTest( "test harness" )
    




