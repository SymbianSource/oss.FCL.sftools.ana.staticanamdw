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

import os
import getopt
import string
import sys
import re

def usage(code, msg=""):
    print msg
    print "Usage: Buildparser.py -h -s <script dir> -m <main file> -o <output dir/file> -v <version text>"
    print 
    print "options:"
    print "     -h  command help"
    print "     -s  script dir is the directory containing python subscripts"
    print "     -m  main file is the file which contains main() function"
    print "     -o  output dir/file is the directory (and file) for output result"
    print "     -v  version text indicates within scripts which fractions to copy"
    print "         into resultant script"
    print "     -l  localised filename"
    print
    sys.exit(code)

class CFileScanner:

    # Main scan file
    def startscan(self):
        # Default output file name is Resultant.py
        if os.path.isdir(output):
            resultantfile = open(output+"\Resultant.py", "w")
        else:
            resultantfile = open(output, "w")

        # Parse main file from begin to '#!PARSE' tag (copy appropriate lines to resultant file)
        # and store/parse remaining lines (lines after '#!Parse') into an array
        # scanfile is in use to scan script files. Here is in use to scan main file! (exception)
        storelines=self.scanfile(mainfile,resultantfile)
        # Parse other script files(copy appropriate lines to resultant file)
        self.traverse(scriptdir,resultantfile)
        # Flush remaining lines from main file (array) to resultant file
        self.FlushMainFile(resultantfile,storelines)

        resultantfile.close()
    # Flush
    def FlushMainFile(self,resultantfile,storelines):
        for line in storelines:
            resultantfile.write(line)

    def InsertFile( self, aResultantfile, aFilename ):
        # inserts a file without preparsing - for example localised text
        fileToInsert = open( aFilename, "r" )
        fileToInsertContent = fileToInsert.readlines()

        for fileToInsertLine in fileToInsertContent:
            aResultantfile.write( fileToInsertLine )
        
        fileToInsert.close()


    def scanfile(self,fullfilename,resultantfile):
        storelines=""
        ParseDelimiter=False
        # Copy by default (All lines will be copied which are not within tags)
        CopyIndicator=True
        sourcefile = open(fullfilename,"r")
        filelines = sourcefile.readlines()
        for line in filelines:
            delimiter=line.find("#!PARSE")
            # Parse to delimiter (#!PARSE)
            if (delimiter<>-1):
                ParseDelimiter=True

            if( -1 <> line.find( "#!LOCALISEHERE" ) ):
                self.InsertFile( resultantfile, localiseFilename )
                
            
                
            # Find begining tag
            delimiter=line.find("#<<")
            if (delimiter<>-1):
                # Version (tag) text not found. Don't copy additional lines
                if (line.find(version,delimiter+3,delimiter+3+len(version))==-1):
                    CopyIndicator=False
                else:
                    # Found given version, copy lines
                    CopyIndicator=True

            # Find ending tag
            reMethod = re.compile("#.*>>")
            delimiter = reMethod.search(line)
            if (delimiter):
                # End of previous version block declaration
                if (not CopyIndicator):
                    # If previous version block was not copied, skip '# >>' (don't write this tag to resultant file)
                    CopyIndicator=True
                    continue
                else:
                    CopyIndicator=True

            # Haven't reached '#!Parse' delimiter so copy current line to resultant file
            if (not ParseDelimiter):
                # Copy indicator is still working
                if (CopyIndicator):
                    resultantfile.write(line)
            else:
                if (CopyIndicator):
                    # Store lines after '#!PARSE'
                    storelines=storelines+line

        resultantfile.write("\n")                
        sourcefile.close()
        return storelines

    # Searching subdirectories and files
    def traverse(self, currentdir,resultantfile):
        contents = os.listdir(currentdir)
        for entry in contents:
            fullfilename = os.path.normpath(os.path.join(currentdir, entry))
            if os.path.isdir(fullfilename):
                self.traverse(fullfilename,resultantfile)
            else:
                # Scan file if it is not the main file and it is python file
                if (fullfilename.upper().find((mainfile[mainfile.rfind("\\")+1:]).upper())==-1 and fullfilename.upper()[-3:]==".PY"):
                    self.scanfile(fullfilename,resultantfile)

#
# main
#
opts, args = getopt.getopt(sys.argv[1:], "hs:m:o:v:l:", ["help", "scriptdir=", "mainfile=", "output=","version=","localisefile="])

storelines=""
scriptdir=""
mainfile=""
output=""
version=0
localiseFilename=""

for o, a in opts:
    if o in ("-h", "--help"):
        usage(0)
    if o in ("-s", "--scriptdir"):
        scriptdir = a
    if o in ("-m", "--mainfile"):
        mainfile = a
    if o in ("-o", "--output"):
        output = a
    if o in ("-v", "--version"):
        version = a
    if o in ("-l", "--localisefile"):
        localiseFilename = a

if (scriptdir=="" or mainfile=="" or output=="" or version==0 or localiseFilename=="" ):
    usage(1)

scanner = CFileScanner()
scanner.startscan()