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

CodeScanner is primarily made up of 2 parts :

-- The main body, found in /scripts/linescanner.py, handles the scanning of 
source file, importing rules from individual python scripts, creating and 
formatting output HTML files, and other misc functions.

-- Individual Python scripts, found in other files in /scripts. Each of these 
scripts correspond to a unique problem checked by CodeScanner. To extend 
CodeScanner, simply add new scripts for problems to be checked.


Some other files/directories found in the CodeScanner tree:

-- The script Buildparser.py is used to collect and combine all the Python scripts 
found in /script with the main body and any localized strings. The result is a 
single script that can be executed by the Python interpreter. Documentation for
BuildParser can be found in /BuildParserdoc.

-- The batch file buildtools.bat uses Buildparser.py to generate a single Python
script, which is then converted into a stand alone executable. 

-- /script/resource contains the string resource files that are used for storing 
localized strings for CodeScanner.

====================
Building CodeScanner
====================

Because CodeScanner is written as Python scripts, one needs the Python interpretor 
to compile these scripts. Besides from the standard Python installation, one also 
needs the pywin32 package and the Psyco extension module. 
Go to <http://python.org/> for the latest version of Python and pywin32 package.
Go to <http://psyco.sourceforge.net/> for the latest version of Psyco.

To build CodeScanner do the following :

1) open a console window and set current directory to :

..../codescanner

2) type the following command in the console window :

python pyinstaller/configure.py

This will configure pyinstaller, a 3rd party utility responsible for making CodeScanner
a stand-alone command line tool.

3) execute the batch file "buildtools.bat".

4) at this point you should have the file CodeScanner.exe and other runtime modules in
the directory /discodescanner.
