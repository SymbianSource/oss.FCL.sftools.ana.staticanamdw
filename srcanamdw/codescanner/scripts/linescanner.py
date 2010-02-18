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
# linescanner.py - the main body of CodeScanner
#
# #################################################################

import base64
import datetime
import encodings
import getopt
import os
import os.path
import psyco
import re
import sys
import xml.dom.minidom
import zlib

# Ignore flags
KIgnoreNothing = 0
KIgnoreComments = 1
KIgnoreCommentsAndQuotes = 2
KIgnoreQuotes = 3

# Severities for the scripts
KSeverityHigh = 0
KSeverityMedium = 1
KSeverityLow = 2

# The names used in the XML configuration file for severity element names.
KSeverityConfigMap = {
			KSeverityHigh		: "high",
			KSeverityMedium		: "medium",
			KSeverityLow		: "low"}

# The names used in the HTML summary file for severity element names.
KSeverityHTMLMap = {
			KSeverityHigh		: "High",
			KSeverityMedium		: "Medium",
			KSeverityLow		: "Low"}

# Categories for the scripts
KCategoryLegal = "Legal Code" 
KCategoryDefinitePanic = "Always Panic"
KCategoryCanPanic = "Can Panic"
KCategoryWrongFunctionality = "Wrong Functionality"
KCategoryLocalisation = "Localisation"
KCategoryPerformance = "Performance"
KCategoryCodingStandards = "Coding Standard"
KCategoryDocumentation = "Documentation"
KCategoryCodeReviewGuides = "Code Review Guide"
KCategoryOther = "Other"

KCategoryHtmlDisplayOrder = [KCategoryLegal,
	KCategoryDefinitePanic,
	KCategoryCanPanic,
	KCategoryWrongFunctionality,
	KCategoryLocalisation,
	KCategoryPerformance,
	KCategoryCodingStandards,
	KCategoryDocumentation,
	KCategoryCodeReviewGuides,
	KCategoryOther]

# The names used in the XML configuration file for category element names.
KCategoryConfigMap = {
			KCategoryLegal				:	"legal", 
			KCategoryDefinitePanic		:	"panic", 
			KCategoryCanPanic			:	"canpanic", 
			KCategoryWrongFunctionality	:	"functionality",
			KCategoryLocalisation		:	"localisation",
			KCategoryPerformance		:	"performance",
			KCategoryCodingStandards	:	"codingstandards",
			KCategoryDocumentation		:	"documentation",
			KCategoryCodeReviewGuides	:	"codereview",
			KCategoryOther				:	"other"}

#Custom rule keyword types
KKeywordBaseClass = "baseclass"
KKeywordCall = "call"
KKeywordClassName = "class"
KKeywordComment = "comment"
KKeywordGeneric = "generic"
KKeywordLocal = "local"
KKeywordMacro = "macro"
KKeywordMember = "member"
KKeywordMethod = "method"
KKeywordParameter = "parameter"
KKeywordUnknown = "unknown"

#The names used in the XML configuration file for custom rule keyword types.
KCustomRuleKeywordMap = {
			KKeywordBaseClass           :   "baseclass",
			KKeywordCall                :   "call",
			KKeywordClassName           :   "class",
			KKeywordComment             :   "comment",
			KKeywordGeneric             :   "generic",
			KKeywordLocal               :   "local",
			KKeywordMacro               :   "macro",
			KKeywordMember              :   "member",
			KKeywordMethod              :   "method",
			KKeywordParameter           :   "parameter",
			KKeywordUnknown             :   "unknown"}

KVersion = "Nokia CodeScanner version 2.1.4"
KCopyrightLine1 = "Copyright (c) 2007-2009. Nokia Corporation. All rights reserved."
KCopyrightLine1Html = "Copyright &copy; 2007-2009. Nokia Corporation. All rights reserved."
KCopyrightLine2 = "For product and support information, visit www.forum.nokia.com."
KWww = "www.forum.nokia.com"

stringPool = {}
#!LOCALISEHERE

def Usage(code, msg=""):
	print msg
	print
	print KVersion
	print
	print "Usage: CodeScanner [options] <source dir> [<output dir>]"	
	print "   or: CodeScanner [options] <source file> [<output dir>]"
	print 
	print "options:"
	print "    -h - display command help"
	print "    -v - display verbose messages"
	print "    -c <config file> - use specified configuration file"
	print "    -i <source dir/file> - specify additional directory/file to scan"
	print "    -l <log file> - create debug log with specified filename"
	print "    -o html|xml|std - specify output format : HTML, XML or StdOut; default is HTML"
	print "    -x url to lxr site"
	print "    -r lxr version"
	print "    -t on/off - create a time-stamped directory for results, default is on"
	print
	print "<source dir> is the directory containing the source code to scan"
	print "<source file> is the single file containing the source code to scan"
	print "<output dir> is the directory in which to produce the output"
	print
	print "Notes:"
	print "<source dir> and <output dir> cannot be identical"
	print "<output dir> cannot be the root of a drive"
	print
	print KCopyrightLine1
	print KCopyrightLine2
	if scanner.iLog <> None:
		scanner.iLog.Write("usage(): exiting with code " + str(code))
		scanner.iLog.Close()
	sys.exit(code)

def DefaultCompare(aLines, aCurrentline, aRematch, aFilename):
	if aRematch.search(aLines[aCurrentline]):
		return 1
	else:
		return 0

def DefaultFuncParamCompare(lines, currentline, rematch, filename):
	# distinguish local declaration from function parameter
    line = lines[currentline]
    m = rematch.search(line)
    if m:
        isFuncParam = (line.find(")") <> -1)
        isLocal = (line.find(";") <> -1)

        while (not isFuncParam) and (not isLocal) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]
            isFuncParam = (line.find(")") <> -1)
            isLocal = (line.find(";") <> -1)

        if isFuncParam:
            return 1
        elif isLocal:
            return 0

    return 0

def ScanDirOrFile(argument):
	if os.path.isdir(argument):
		scanner.iComponentManager.SetRoot(argument)
		scanner.TraverseDirectory(argument)
	elif os.path.isfile(argument):
		parentDir = os.path.dirname(argument)
		scanner.iComponentManager.SetRoot(parentDir)
		scanner.iComponentManager.BeginDirectory(parentDir)
		numberOfLinesScanned = 0
		numberOfLinesScanned += scanner.ScanFile(argument)
		scanner.iComponentManager.EndDirectory(parentDir, numberOfLinesScanned)
	else:
		print "Unable to open specified source file: " + argument
		sys.exit(2)


class CScript:

	# #######################################################
	# CScript - a test script

	def __init__(self, aScriptName):
		self.iScriptName = aScriptName
		self.iCompare = DefaultCompare
		self.iReString = ""
		self.iReMatch = re.compile("")
		self.iTitle = stringPool[aScriptName + "!title"]
		self.iIdeTitle = stringPool[aScriptName + "!ideTitle"]
		self.iFileExts = []
		self.iIgnore = KIgnoreNothing
		self.iDescription = stringPool[aScriptName + "!description"]
		self.iSeverity = KSeverityMedium
		self.iBaseClass = ""

	def ScriptConfig(self):
		if (scanner.iDomConfig <> None):
			for scriptsNode in scanner.iDomConfig.getElementsByTagName("scripts"):
				for scriptNode in scriptsNode.getElementsByTagName(self.iScriptName):
					return scriptNode
		return None
	
	def DefaultInheritanceCompare(self, lines, currentline, rematch, filename):
		m = rematch.search(lines[currentline])
		if m:
			inheritanceString = m.group(3)
			# check for inheritance list spanning multiple lines
			i = currentline + 1
			while (inheritanceString.find("{") == -1) and i < len(lines):
				if (inheritanceString.find(";") <> -1):
					return 0
				inheritanceString += lines[i]
				i += 1

			# construct inheritance class list
			inheritancelist = inheritanceString.split(",")
			reclass = re.compile("[\s:]*(public|protected|private)?\s*([\w:]+)")
			classlist = []
			for inheritance in inheritancelist:
				match = reclass.search(inheritance)
				if match:
					inheritclass = match.group(2)
					colonpos = inheritclass.rfind(":")
					if (colonpos <> -1):
						inheritclass = inheritclass[colonpos + 1:]
					classlist.append(inheritclass)

			# search for inheritance class
			for classname in classlist:
				if classname == self.iBaseClass:
					return 1

		return 0


class CCustomScript(CScript):

	# #######################################################
	# CScript - a test script based on a custom rule

	def __init__(self, aScriptName):
		self.iScriptName = aScriptName
		self.iCompare = DefaultCompare
		self.iReString = ""
		self.iTitle = ""
		self.iIdeTitle = ""
		self.iFileExts = []
		self.iIgnore = KIgnoreNothing
		self.iDescription = ""


class CCategorisedScripts:

	# #######################################################
	# CCategorisedScripts - a collection of scripts sorted
	# by script category (panic, can panic, etc.)

	def AddScript(self, aScript):
		# do we have a category for this already?
		category = aScript.iCategory
		if (not self.iScripts.has_key(category)):
			# no, create a linear array here
			self.iScripts[category] = []

		# append to the correct category
		self.iScripts[category].append(aScript)

		# compile the reg-ex otherwise will get continuous hits
		aScript.iReMatch = re.compile(aScript.iReString, re.VERBOSE)

	def AllScripts(self):
		result = []
		for scripts in self.iScripts.values():
			result += scripts

		return result

	def PrintListOfTestScripts(self):
		for category in self.iScripts.keys():
			print(category + "\n----------------------------------")
			for script in self.iScripts[category]:
				print("\t" + script.iScriptName)

		print("")

	# iScripts is a 2D array, 1st level is a hash of categories
	#                         2nd level is linear array
	iScripts = {}        

class CLogger:

	# #######################################################
	# CLogger
	# a simple log file interface

	def __init__(self, aFilename):
		if aFilename != None and len(aFilename) > 0:
			self.iFile = file(aFilename, "w")
			self.iFile.write(KVersion + " started at " + datetime.datetime.now().ctime() + "\n")
		else:
			self.iFile = None

	def Write(self, aText):
		if self.iFile <> None:
			self.iFile.write(str(datetime.datetime.now().time())+":"+aText+"\n")
			self.iFile.flush()

	def Close(self):
		if self.iFile <> None:
			self.iFile.write(KVersion + " ended at " + datetime.datetime.now().ctime() + "\n")
			self.iFile.close()


class CRendererBase:

	# #######################################################
	# CRendererBase - base class for renderers

	def RegisterSelf(self, aName, aDescription, aRendererManager):
		self.iName = aName
		self.iDescription = aDescription
		aRendererManager.AddRenderer(self)
	def BeginComponent(self, aComponent):
		return
	def BeginFile(self, aFilename):
		return
	def ReportError(self, aLineContext, aScript):
		return
	def EndFile(self):
		return
	def EndComponent(self, aComponent):
		return


class CStdOutRenderer(CRendererBase):

	# #######################################################
	# CStdOutRenderer - renderer for Standard Console Output
	# Output goes to standard output; when run in Carbide, 
	# this shows up in the output window. Correctly formatted 
	# lines can then be selected, automatically selecting 
	# the corresponding line of the associated source file. 
	# The format is:
	#   <filename>(<line>) : <comment>

	def __init__(self, aRendererManager):
		self.RegisterSelf("stdout", "StdOut renderer", aRendererManager)
		print KVersion

	def BeginComponent(self, aComponent):
		return

	def BeginFile(self, aFilename):
		self.iErrorCount = 0
		scanner.ReportAction("Scanning file " + aFilename)

	def ReportError(self, aLineContext, aScript):
		self.iErrorCount += 1
		if (aScript.iSeverity == KSeverityLow):
			msgType = "info"
		elif (aScript.iSeverity == KSeverityMedium):
			msgType = "warning"
		elif (aScript.iSeverity == KSeverityHigh):
			msgType = "error"
		print(aLineContext.iFileName + "(" + str(aLineContext.iLineNumber) + ") : " + msgType + ": " + aScript.iScriptName + ": " + KSeverityConfigMap[aScript.iSeverity] + ": " + KCategoryConfigMap[aScript.iCategory] + ": " + aScript.iIdeTitle)
		if len(scanner.iRendererManager.iAnnotation)>0:
			print scanner.iRendererManager.iAnnotation
			scanner.iRendererManager.iAnnotation = ""

	def EndFile(self):
		scanner.ReportAction("Total problems found in file: " + str(self.iErrorCount))

	def EndComponent(self, aComponent):
		scanner.iEndTime = datetime.datetime.now().ctime()
		return


class CXmlComponentSummaryFile:
	# #########################################################
	# CXmlComponentSummaryFile
	# Encapsulates the script (problem) summary for XML output.
	# For each script, there is a listing for occurrences
	# of that script's problem and location of each occurrence.

	def CreateSummary(self, aXmlRenderer):
		try:
			outputPath = os.path.normpath(os.path.join(aXmlRenderer.iOutputDirectory, "problemIndex.xml"))
			outputFile = file(outputPath, "w")
		except IOError:
			scanner.ReportError("IOError : Unable to create output file " + outputPath)
		else:
			errors = aXmlRenderer.iErrors
			level = 0
			indent = "   "
			outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			outputFile.write(level * indent + "<problemIndex>\n")
			level += 1
			for category in KCategoryHtmlDisplayOrder:
				found = False
				if scanner.iCategoriedScripts.iScripts.has_key(category):
					for script in scanner.iCategoriedScripts.iScripts[category]:
						if errors.has_key(script.iScriptName):
							found = True
							break
					if found:
						outputFile.write(level * indent + "<category")
						outputFile.write(" name=\"" + KCategoryConfigMap[category] + "\">\n")
						level += 1
						for script in scanner.iCategoriedScripts.iScripts[category]:
							if errors.has_key(script.iScriptName):
								outputFile.write(level * indent + "<problem")
								outputFile.write(" name=\"" + script.iScriptName + "\"")
								outputFile.write(" severity=\"" + KSeverityConfigMap[script.iSeverity] + "\">\n")
								level += 1
								for fileName, lines in errors[script.iScriptName].items():
									outputFile.write(level * indent + "<file")
									outputFile.write(" path=\"" + fileName + "\">\n")
									level += 1
									for lineNo in lines:
										outputFile.write(level * indent + str(lineNo) + "\n")
									level -= 1
									outputFile.write(level * indent + "</file>\n")
								level -= 1
								outputFile.write(level * indent + "</problem>\n")
						level -= 1
						outputFile.write(level * indent + "</category>\n")
			level -= 1
			outputFile.write(level * indent + "</problemIndex>\n")
			outputFile.close()


class CXmlRenderer(CRendererBase):

	# ########################################
	# CXmlRenderer - a renderer for XML output

	def __init__(self, aRendererManager, aOutputDirectory):
		self.RegisterSelf("xml", "XML renderer", aRendererManager)
		self.iOutputDirectory = aOutputDirectory
		if os.path.isdir(self.iOutputDirectory) != True :
			os.makedirs(self.iOutputDirectory)
		self.iErrors = {} 
		print
		print KVersion
		print KCopyrightLine1
		print KCopyrightLine2

	def BeginComponent(self, aComponent):
		return

	def BeginFile(self, aFilename):
		self.iFilename = aFilename
		scanner.ReportAction("Scanning file " + aFilename)

	def ReportError(self, aLineContext, aScript):
		scriptName = aScript.iScriptName
		fileName = aLineContext.iFileName
		lineNumber = aLineContext.iLineNumber
		if (not self.iErrors.has_key(scriptName)):
			self.iErrors[scriptName] = {}
		if (not self.iErrors[scriptName].has_key(fileName)):
			self.iErrors[scriptName][fileName] = []
		self.iErrors[scriptName][fileName].append(lineNumber)

	def EndFile(self):
		#tbd
		return

	def EndComponent(self, aComponent):
		relativeComponentName = scanner.iComponentManager.RelativeComponentName(aComponent.iFullPath)
		if len(relativeComponentName) < 1:	# root component - final component
			scanner.iEndTime = datetime.datetime.now().ctime()
			componentSummaryFile = CXmlComponentSummaryFile()
			componentSummaryFile.CreateSummary(self)


class CHtmlOutputFileBase:

	# #######################################################
	# CHtmlOutputFileBase - base class for HTML output files

	def WriteHeader(self, aOutputFile):
		aOutputFile.write("<html><body>")

	def Write(self, aOutputFile, aText):
		aOutputFile.write(aText)

	def WriteLink(self, aOutputFile, aHref, aText):
		aHref = self.CleanupLink(aHref)
		aOutputFile.write("<a href=\"" + aHref + "\">" + aText + "</a>")

	def WriteElement(self, aOutputFile, aElementName, aElementValue):
		aOutputFile.write("<"+aElementName+">"+aElementValue+"</"+aElementName+">")

	def WriteBreak(self, aOutputFile):
		aOutputFile.write("<br>")

	def WriteFooter(self, aOutputFile):
		aOutputFile.write("<br><hr><center><h5>"+KCopyrightLine1Html+"</h5>")
		aOutputFile.write("<h5>")
		CHtmlOutputFileBase.WriteLink(self, aOutputFile, "http://"+KWww, KWww)
		aOutputFile.write("</h5></center></body></html>")

	def CleanupLink(self, aHref):
		# Mozilla Firefox does not handle link with the '#' character correctly, 
		# so we need to replace it with the equivalent URL encoding "%23"
		aHref = aHref.replace("#", "%23")
		# Mozilla Firefox sometimes does not handle link with '\' correctly,
		# so we need to replace it with '/'
		aHref = aHref.replace('\\', '/')
		return aHref


class CHtmlOutputFile(CHtmlOutputFileBase):

	# #######################################################
	# CHtmlOutputFile - simplified access to HTML output file

	def __init__(self, aOutputPath):
		if not os.path.isdir(os.path.dirname(aOutputPath)):
			os.makedirs(os.path.dirname(aOutputPath))
		self.iOutputFile = file(aOutputPath, "w")
		self.WriteHeader(self.iOutputFile)

	def Write(self, aText):
		CHtmlOutputFileBase.Write(self, self.iOutputFile, aText)

	def WriteLink(self, aHref, aText):
		CHtmlOutputFileBase.WriteLink(self, self.iOutputFile, aHref, aText)

	def WriteElement(self, aElementName, aElementValue):
		CHtmlOutputFileBase.WriteElement(self, self.iOutputFile, aElementName, aElementValue)

	def WriteBreak(self):
		CHtmlOutputFileBase.WriteBreak(self, self.iOutputFile)
		
	def Close(self):
		self.WriteFooter(self.iOutputFile)
		self.iOutputFile.close()


class CHtmlComponentSummaryFiles:

	# #######################################################
	# CHtmlComponentSummaryFiles
	# Encapsulates the component summary files for HTML output.
	# For each component, there is a component report file listing the number 
	# of occurrences of each problem type. There is also a single index or 
	# summary file with links to each of the component report files.

	def CreateSummaries(self, aHtmlRenderer, aOutputDirectory):
		totalErrorCount = 0
		outputPath = os.path.normpath(os.path.join(aOutputDirectory, "componentIndex.html"))
		componentSummaryFile = CHtmlOutputFile(outputPath)
		componentSummaryFile.Write("<font face=verdana>")
		componentSummaryFile.WriteElement("h2", "Component Summary")
		componentSummaryFile.Write("Source: "+scanner.iSource)
		componentSummaryFile.WriteBreak()
		componentSummaryFile.Write("Scan started at:   " + scanner.iStartTime)
		componentSummaryFile.WriteBreak()
		componentSummaryFile.Write("Scan completed at: " + scanner.iEndTime)
		componentSummaryFile.WriteBreak()
		componentSummaryFile.WriteBreak()
		componentSummaryFile.WriteLink("problemIndex.html", "View problems by type")
		componentSummaryFile.WriteBreak()
		componentSummaryFile.Write("<hr>")
		componentSummaryFile.WriteBreak()
		componentSummaryFile.Write("<table border=\"1\" width=\"100%\">")
		componentSummaryFile.Write("<tr bgcolor=\"#0099ff\">")
		componentSummaryFile.WriteElement("th width=\"75%\"", "Component")
		componentSummaryFile.WriteElement("th", "Items Found")
		componentSummaryFile.WriteElement("th", "Lines of Code")
		componentSummaryFile.WriteElement("th", "Possible Defects/KLOC")
		componentSummaryFile.Write("</tr>")
		for component in scanner.iComponentManager.iCompletedComponents:
			componentName = scanner.iComponentManager.ComponentName(component.iFullPath)
			outputPath = os.path.normpath(os.path.join(aOutputDirectory, "byComponent"))
			outputPath = os.path.normpath(os.path.join(outputPath, componentName))
			outputPath = os.path.normpath(os.path.join(outputPath, "componentSummary.html"))
			errorCount = self.WriteComponentReport(aHtmlRenderer, outputPath, component.iFullPath, componentName)
			if (errorCount > 0):
				totalErrorCount = totalErrorCount + errorCount
				numberOfLinesScanned = component.iNumberOfLinesScanned
				if (numberOfLinesScanned > 0):
					defectsPerKLOC = int((1000.0 / numberOfLinesScanned) * errorCount)
				else:
					defectsPerKLOC = 0
				componentSummaryFile.Write("<tr>")
				componentSummaryFile.Write("<td>")
				relOutputPath = os.path.normpath(os.path.join("byComponent", componentName))
				relOutputPath = os.path.normpath(os.path.join(relOutputPath, "componentSummary.html"))
				componentSummaryFile.WriteLink(relOutputPath, component.iFullPath)
				componentSummaryFile.Write("</td>")
				componentSummaryFile.Write("<td>")
				componentSummaryFile.WriteElement("center",str(errorCount))
				componentSummaryFile.Write("</td>")
				componentSummaryFile.Write("<td>")
				componentSummaryFile.WriteElement("center",str(numberOfLinesScanned))
				componentSummaryFile.Write("</td>")
				componentSummaryFile.Write("<td>")
				componentSummaryFile.WriteElement("center",str(defectsPerKLOC))
				componentSummaryFile.Write("</td>")
				componentSummaryFile.Write("</tr>")

		componentSummaryFile.Write("<tr>")
		componentSummaryFile.Write("<td>")
		componentSummaryFile.WriteElement("b", "Total")
		componentSummaryFile.Write("</td>")
		componentSummaryFile.Write("<td><center>")
		componentSummaryFile.WriteElement("b", str(totalErrorCount))
		componentSummaryFile.Write("</center></td>")
		componentSummaryFile.Write("</tr>")

		componentSummaryFile.Write("</table>")
		componentSummaryFile.Close()

	def WriteComponentReport(self, aHtmlRenderer, aOutputPath, aComponentFullPath, aComponentName):
		totalErrorCount = 0
		componentReportFile = CHtmlOutputFile(aOutputPath)
		componentReportFile.Write("<font face=verdana>")
		componentReportFile.WriteElement("h2", "Component Report")
		componentReportFile.WriteElement("h3", "Component: "+aComponentFullPath)
		componentReportFile.Write("<font face=verdana color=black>")
		found = False
		for category in KCategoryHtmlDisplayOrder:
			if scanner.iCategoriedScripts.iScripts.has_key(category):
				for script in scanner.iCategoriedScripts.iScripts[category]:
					errorCount = scanner.iComponentManager.ScriptComponentErrorCount(aComponentFullPath, script.iScriptName)
					if errorCount > 0:
						found = True
						break

		if found:
			componentReportFile.Write("<table border=\"1\" width=\"100%\">")
			componentReportFile.Write("<tr bgcolor=\"#0099ff\">")
			componentReportFile.WriteElement("th width=\"75%\"", "Problem")
			componentReportFile.WriteElement("th", "Items Found")
			componentReportFile.WriteElement("th", "Severity")
			componentReportFile.Write("</tr>")
			for category in KCategoryHtmlDisplayOrder:
				if scanner.iCategoriedScripts.iScripts.has_key(category):
					for script in scanner.iCategoriedScripts.iScripts[category]:
						errorCount = scanner.iComponentManager.ScriptComponentErrorCount(aComponentFullPath, script.iScriptName)
						if errorCount > 0:
							componentReportFile.Write("<tr>")
							componentReportFile.Write("<td>")
							#scriptComponentPath = aHtmlRenderer.ScriptComponentPath(aComponentFullPath, script.iScriptName)
							#componentReportFile.WriteLink(scriptComponentPath, script.iTitle)
							componentReportFile.WriteLink(script.iScriptName+".html", script.iTitle)
							componentReportFile.Write("</td>")
							componentReportFile.Write("<td>")
							componentReportFile.WriteElement("center", str(errorCount))
							componentReportFile.Write("</td>")
							componentReportFile.Write("<td>")
							componentReportFile.WriteElement("center", KSeverityHTMLMap[script.iSeverity])
							componentReportFile.Write("</td>")
							componentReportFile.Write("</tr>")
							totalErrorCount = totalErrorCount + errorCount
			componentReportFile.Write("<tr>")
			componentReportFile.Write("<td>")
			componentReportFile.WriteElement("b", "Total")
			componentReportFile.Write("</td>")
			componentReportFile.Write("<td><center>")
			componentReportFile.WriteElement("b", str(totalErrorCount))
			componentReportFile.Write("</center></td>")
			componentReportFile.Write("</tr>")
			componentReportFile.Write("</table>")
		else:
			componentReportFile.WriteBreak()
			componentReportFile.WriteElement("i", "There are no items to report for this component.")
			componentReportFile.WriteBreak()
		componentReportFile.Close()
		return totalErrorCount


class CHtmlScriptSummaryFiles:

	# #######################################################
	# CHtmlScriptSummaryFiles
	# Encapsulates the script (problem) summary files for HTML output.
	# For each script, there is a file listing the number of occurrences
	# of that script's problem for each component. There is also a single
	# index or summary file with links to each of the problem report file.

	def CreateSummaries(self, aHtmlRenderer, aOutputDirectory):

		totalErrorCount = 0

		outputPath = os.path.normpath(os.path.join(aOutputDirectory, "problemIndex.html"))
		scriptSummaryFile = CHtmlOutputFile(outputPath)
		scriptSummaryFile.Write("<font face=verdana>")
		scriptSummaryFile.WriteElement("h2", "Problem Summary")
		scriptSummaryFile.Write("Source: "+scanner.iSource)
		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.Write("Scan started at:   " + scanner.iStartTime)
		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.Write("Scan completed at: " + scanner.iEndTime)
		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.WriteLink("componentIndex.html", "View problems by component")
		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.Write("<hr>")
		scriptSummaryFile.WriteBreak()
		for category in KCategoryHtmlDisplayOrder:
			if scanner.iCategoriedScripts.iScripts.has_key(category):
				scriptSummaryFile.WriteElement("h3", "Category: "+category)
				scriptSummaryFile.Write("<table border=\"1\" width=\"100%\">")
				scriptSummaryFile.Write("<tr bgcolor=\"#0099ff\">")
				scriptSummaryFile.WriteElement("th width=\"75%\"", "Problem")
				scriptSummaryFile.WriteElement("th", "Items Found")
				scriptSummaryFile.WriteElement("th", "Severity")
				scriptSummaryFile.Write("</tr>")
				categoryErrorCount = 0
				for script in scanner.iCategoriedScripts.iScripts[category]:
					outputPath = os.path.normpath(os.path.join(aOutputDirectory, "byProblem"))
					outputPath = os.path.normpath(os.path.join(outputPath, script.iScriptName+"Summary.html"))
					errorCount = self.WriteScriptReport(aHtmlRenderer, outputPath, script)
					categoryErrorCount = categoryErrorCount + errorCount
					scriptSummaryFile.Write("<tr>")
					scriptSummaryFile.Write("<td>")
					relOutputPath = os.path.normpath(os.path.join("byProblem", script.iScriptName+"Summary.html"))
					scriptSummaryFile.WriteLink(relOutputPath, script.iTitle)
					scriptSummaryFile.Write("</td>")
					scriptSummaryFile.Write("<td>")
					scriptSummaryFile.WriteElement("center", str(errorCount))
					scriptSummaryFile.Write("</td>")
					scriptSummaryFile.Write("<td>")
					scriptSummaryFile.WriteElement("center", KSeverityHTMLMap[script.iSeverity])
					scriptSummaryFile.Write("</td>")
					scriptSummaryFile.Write("</tr>")
				totalErrorCount = totalErrorCount + categoryErrorCount
				scriptSummaryFile.Write("<tr>")
				scriptSummaryFile.Write("<td>")
				scriptSummaryFile.WriteElement("b", "Category Total")
				scriptSummaryFile.Write("</td>")
				scriptSummaryFile.Write("<td>")
				scriptSummaryFile.WriteElement("center", "<b>"+str(categoryErrorCount)+"</b>")
				scriptSummaryFile.Write("</td>")
				scriptSummaryFile.Write("</tr>")
				scriptSummaryFile.Write("</table>")

		scriptSummaryFile.WriteBreak()
		scriptSummaryFile.WriteElement("b", "Total: " + str(totalErrorCount))
		scriptSummaryFile.WriteBreak()

		scriptSummaryFile.Close()

	def WriteScriptReport(self, aHtmlRenderer, aOutputPath, aScript):
		totalErrorCount = 0
		scriptReportFile = CHtmlOutputFile(aOutputPath)
		scriptReportFile.Write("<font face=verdana>")
		scriptReportFile.WriteElement("h2", "Problem Report")
		scriptReportFile.WriteElement("h3", "Problem: " + aScript.iTitle)
		scriptReportFile.Write(aScript.iDescription)
		scriptReportFile.WriteBreak()
		scriptReportFile.WriteBreak()

		found = False
		for component in scanner.iComponentManager.iCompletedComponents:
			errorCount = scanner.iComponentManager.ScriptComponentErrorCount(component.iFullPath, aScript.iScriptName)
			if errorCount > 0:
				found = True
				break

		if found:
			scriptReportFile.Write("<table border=\"1\" width=\"100%\">")
			scriptReportFile.Write("<tr bgcolor=\"#0099ff\">")
			scriptReportFile.WriteElement("th width=\"80%\"", "Component")
			scriptReportFile.WriteElement("th", "Items Found")
			scriptReportFile.Write("</tr>")
			for component in scanner.iComponentManager.iCompletedComponents:
				errorCount = scanner.iComponentManager.ScriptComponentErrorCount(component.iFullPath, aScript.iScriptName)
				if errorCount > 0:
					scriptReportFile.Write("<tr>")
					scriptReportFile.Write("<td>")
					scriptComponentPath = aHtmlRenderer.ScriptComponentPath(component.iFullPath, aScript.iScriptName, "..")
					scriptReportFile.WriteLink(scriptComponentPath, component.iFullPath)
					scriptReportFile.Write("</td>")
					scriptReportFile.Write("<td>")
					scriptReportFile.WriteElement("center", str(errorCount))
					scriptReportFile.Write("</td>")
					scriptReportFile.Write("</tr>")
					totalErrorCount = totalErrorCount + errorCount
			scriptReportFile.Write("<tr>")
			scriptReportFile.Write("<td>")
			scriptReportFile.WriteElement("b", "Total")
			scriptReportFile.Write("</td>")
			scriptReportFile.Write("<td><center>")
			scriptReportFile.WriteElement("b", str(totalErrorCount))
			scriptReportFile.Write("</center></td>")
			scriptReportFile.Write("</tr>")
			scriptReportFile.Write("</table>")
		else:
			scriptReportFile.WriteBreak()
			scriptReportFile.WriteElement("i", "There are no items of this problem type to report.")
			scriptReportFile.WriteBreak()

		scriptReportFile.Close()
		return totalErrorCount


class CHtmlScriptComponentFile:

	# #######################################################
	# CHtmlScriptComponentFile
	# Encapsulates access to the HTML output files with the greatest amount of detail.
	# Each of these files is for a specific problem (script) and for a specific component.

	# The file handle is closed between each call to avoid exhausting the system
	# limit for open file handles. Many of these files may be open at one time,
	# and the number of open files is dependent on both the directory structure
	# being traversed and the number of types of problems found.

	def __init__(self, aLxrUrl, aLxrVersion):
		self.iLxrUrl = aLxrUrl
		self.iLxrVersion = aLxrVersion
		
	def BeginOutputFile(self, aOutputPath, aScript, aComponentName):
		if not os.path.isdir(os.path.dirname(aOutputPath)):
			os.makedirs(os.path.dirname(aOutputPath))
		outputFile = file(aOutputPath, "w")
		self.iScriptComponentFile = CHtmlOutputFileBase()
		self.iScriptComponentFile.Write(outputFile, "<font face=verdana>")
		self.iScriptComponentFile.WriteHeader(outputFile)
		self.iScriptComponentFile.WriteElement(outputFile, "h2", "Detailed Problem Report")
		self.iScriptComponentFile.WriteElement(outputFile, "h3", "Component: "+aComponentName)
		self.iScriptComponentFile.WriteElement(outputFile, "h3", "Problem: "+aScript.iTitle)
		self.iScriptComponentFile.Write(outputFile, aScript.iDescription)
		self.iScriptComponentFile.WriteBreak(outputFile)
		self.iScriptComponentFile.Write(outputFile, "<hr>")
		self.iScriptComponentFile.WriteBreak(outputFile)
		outputFile.close()

	def ReportError(self, aOutputPath, aLineContext):
		outputFile = file(aOutputPath, "a")
		if self.iLxrUrl == None:
			# Mozilla Firefox cannot open links to local files, 
			# so it is necessary to convert local file path
			filePath = "file:///" + aLineContext.iFileName
		else:
			# generate link to LXR server instead of local file system
			filePath = self.iLxrUrl + aLineContext.iFileName[len(scanner.iComponentManager.iRootPath):]
			if self.iLxrVersion <> None:
				filePath = filePath + "?v="+self.iLxrVersion
			filePath = filePath + '#%03d'%aLineContext.iLineNumber
		self.iScriptComponentFile.WriteLink(outputFile, filePath, self.TrimFileName(aLineContext))
		self.iScriptComponentFile.Write(outputFile, "(" + str(aLineContext.iLineNumber) + ") ")
		self.iScriptComponentFile.Write(outputFile, aLineContext.iClassName+"::"+aLineContext.iMethodName+" ")
		self.iScriptComponentFile.Write(outputFile, "<code><font color=red>"+self.CleanUpText(aLineContext.iLineText))
		self.iScriptComponentFile.Write(outputFile, "</font></code>")
		self.iScriptComponentFile.WriteBreak(outputFile)
		if len(scanner.iRendererManager.iAnnotation)>0:
			self.iScriptComponentFile.Write(outputFile, scanner.iRendererManager.iAnnotation)
			self.iScriptComponentFile.WriteBreak(outputFile)
			scanner.iRendererManager.iAnnotation = ""
		outputFile.close()

	def EndOutputFile(self, aOutputPath):
		outputFile = file(aOutputPath, "a")
		self.iScriptComponentFile.WriteFooter(outputFile)
		outputFile.close()

	def TrimFileName(self, aLineContext):
		filename = aLineContext.iFileName
		componentNameLen = len(aLineContext.iComponentName)
		if len(filename) > componentNameLen:
			if filename[0:componentNameLen] == aLineContext.iComponentName:
				filename = filename[componentNameLen:]
				if filename[0] == os.path.sep:
					filename = filename[1:]
		return filename

	def CleanUpText(self, aLineText):
		# check for sub-strings that look like HTML tags and preform clean up if needed
		reTag = re.compile(r"""(<.+>)""", re.VERBOSE)
		foundTag = reTag.search(aLineText)
		if foundTag:
			aNewLineText = aLineText.replace("<", "&lt;")
			aNewLineText = aNewLineText.replace(">", "&gt;")
			return aNewLineText
		else:
			return aLineText		

			
def ComponentCompare(a, b):
	return cmp(os.path.normcase(a.iFullPath), os.path.normcase(b.iFullPath))


class CHtmlRenderer(CRendererBase):

	# #######################################################
	# CHtmlRenderer - a renderer for HTML output

	# I have nothing to offer but blood, toil, tears and sweat. 
	#  - Winston Churchill, 1940 

	def __init__(self, aRendererManager, aOutputDirectory, aLxrUrl, aLxrVersion):
		self.RegisterSelf("html", "HTML renderer", aRendererManager)
		self.iOutputDirectory = aOutputDirectory
		if os.path.isdir(self.iOutputDirectory) != True :
			os.makedirs(self.iOutputDirectory)
		self.iScriptComponentFile = CHtmlScriptComponentFile(aLxrUrl, aLxrVersion)
		self.iScriptComponentFilePaths = {}
		print
		print KVersion
		print KCopyrightLine1
		print KCopyrightLine2

	def BeginFile(self, aFilename):
		self.iFilename = aFilename
		scanner.ReportAction("Scanning file " + aFilename)

	def ReportError(self, aLineContext, aScript):
		outputPath = self.ScriptComponentPath(aLineContext.iComponentName, aScript.iScriptName)
		if not os.path.isfile(outputPath):
			self.iScriptComponentFilePaths[aLineContext.iComponentName].append(outputPath)
			self.iScriptComponentFile.BeginOutputFile(outputPath, aScript, aLineContext.iComponentName)
		self.iScriptComponentFile.ReportError(outputPath, aLineContext)

	def EndFile(self):
		return

	def BeginComponent(self, aComponent):
		self.iScriptComponentFilePaths[aComponent.iFullPath] = []

	def EndComponent(self, aComponent):
		if self.iScriptComponentFilePaths.has_key(aComponent.iFullPath):
			for outputPath in self.iScriptComponentFilePaths[aComponent.iFullPath]:
				self.iScriptComponentFile.EndOutputFile(outputPath)
			del self.iScriptComponentFilePaths[aComponent.iFullPath]
		relativeComponentName = scanner.iComponentManager.RelativeComponentName(aComponent.iFullPath)
		if len(relativeComponentName) < 1:	# root component - final component
			scanner.iEndTime = datetime.datetime.now().ctime()
			scanner.iComponentManager.iCompletedComponents.sort(ComponentCompare)
			scriptSummaryFiles = CHtmlScriptSummaryFiles()
			scriptSummaryFiles.CreateSummaries(self, self.iOutputDirectory)
			componentSummaryFiles = CHtmlComponentSummaryFiles()
			componentSummaryFiles.CreateSummaries(self, self.iOutputDirectory)

	def ScriptComponentPath(self, aComponentName, aScriptName, aRel=None):
		componentName = scanner.iComponentManager.ComponentName(aComponentName)
		if aRel==None:
			aRel = self.iOutputDirectory
		outputPath = os.path.normpath(os.path.join(aRel, "byComponent"))
		outputPath = os.path.normpath(os.path.join(outputPath, componentName))
		outputPath = os.path.normpath(os.path.join(outputPath, aScriptName+".html"))
		return outputPath


class CRendererManager:

	# #######################################################
	# CRendererManager
	# this class handles all the renderers 

	def __init__(self):
		# declare associative list of renderers: iRendererList[name]=renderer
		self.iRendererList = {}
		self.iAnnotation = ""

	def AddRenderer(self, aRenderer):
		self.iRendererList[aRenderer.iName.lower()] = aRenderer

	def PrintListOfRenderers(self):
		print("Renderers:")        
		for name, renderer in self.iRendererList.items():
			print("\t" + name + "\t" + renderer.iDescription)

		print("")

	def BeginFile(self, aFilename):
		for name, renderer in self.iRendererList.items():
			renderer.BeginFile(aFilename)

	def ReportError(self, aLineContext, aScript):
		for name, renderer in self.iRendererList.items():
			renderer.ReportError(aLineContext, aScript)

	def ReportAnnotation(self, aAnnotation):
		self.iAnnotation = aAnnotation

	def EndFile(self):
		for name, renderer in self.iRendererList.items():
			renderer.EndFile()

	def BeginComponent(self, aComponent):
		for name, renderer in self.iRendererList.items():
			renderer.BeginComponent(aComponent)

	def EndComponent(self, aComponent):
		for name, renderer in self.iRendererList.items():
			renderer.EndComponent(aComponent)


class CComponent:

	# #######################################################
	# CComponent - a single component, identified by the
	# directory path to its source code

	def __init__(self, aPath):
		self.iFullPath = aPath
		self.iScriptErrorCounts = {}
		self.iHasGroupDir = False
		self.iNumberOfLinesScanned = 0

	def appendComponent(self, aComponent):
		for scriptName in aComponent.iScriptErrorCounts.keys():
			if self.iScriptErrorCounts.has_key(scriptName):
				self.iScriptErrorCounts[scriptName] += aComponent.iScriptErrorCounts[scriptName]
			else:
				self.iScriptErrorCounts[scriptName] = aComponent.iScriptErrorCounts[scriptName]
		self.iNumberOfLinesScanned += aComponent.iNumberOfLinesScanned
		return


class CComponentManager:

	# #######################################################
	# CComponentManager - controls access to components

	def __init__(self):
		self.iComponentStack = []
		self.iCompletedComponents = []
		self.iRootComponent = CComponent("")
		self.iUseFullComponentPath = False

	def SetRoot(self, aRootPath):
		# set the list of root directories - used to left-trim component names
		self.iRootPath = self.SanitizePath(aRootPath)

	def BeginDirectory(self, aPath):
		aPath = self.SanitizePath(aPath)
		if os.path.isdir(aPath):
			newComponent = CComponent(aPath)
			contents = os.listdir(aPath)
			for entry in contents:
				if (entry.upper() == "GROUP"):
					entryPath = os.path.normpath(os.path.join(aPath, entry))
					if os.path.isdir(entryPath):
						newComponent.iHasGroupDir = True
						break
			if len(self.iComponentStack) > 0:
				topComponent = self.iComponentStack[len(self.iComponentStack)-1]
				if (newComponent.iHasGroupDir or (not topComponent.iHasGroupDir)):
					self.BeginComponent(newComponent)
				else:
					scanner.iLog.Write(aPath + " taken as part of " + topComponent.iFullPath)
			else:
				self.BeginComponent(newComponent)
		else:
			scanner.iLog.Write("ERROR: CComponentManager::BeginDirectory: bad path "+aPath)
		return aPath

	def EndDirectory(self, aPath, numberOfLinesScanned):
		aPath = self.SanitizePath(aPath)
		if len(self.iComponentStack) > 0:
			topComponent = self.iComponentStack[len(self.iComponentStack)-1]
			topComponent.iNumberOfLinesScanned += numberOfLinesScanned
			if (topComponent.iFullPath == aPath):
				self.EndComponent()

	def ReportError(self, aLineContext, aScript):
		scanner.iRendererManager.ReportError(aLineContext, aScript)
		for component in self.iComponentStack:
			if component.iFullPath == aLineContext.iComponentName:
				if component.iScriptErrorCounts.has_key(aScript.iScriptName):
					component.iScriptErrorCounts[aScript.iScriptName] = component.iScriptErrorCounts[aScript.iScriptName] + 1
				else:
					component.iScriptErrorCounts[aScript.iScriptName] = 1

	def ScriptComponentErrorCount(self, aComponentName, aScriptName):
		for component in self.iCompletedComponents:
			if component.iFullPath == aComponentName:
				if component.iScriptErrorCounts.has_key(aScriptName):
					return component.iScriptErrorCounts[aScriptName]
				else:
					return 0
		return 0

	def BeginComponent(self, aComponent):
		scanner.iRendererManager.BeginComponent(aComponent)
		scanner.ReportAction("Begin component: " + aComponent.iFullPath)
		self.iComponentStack.append(aComponent)

	def EndComponent(self):
		previousComponent = self.iComponentStack.pop()
		matchingComponent = self.MatchingComponent(previousComponent)
		if (matchingComponent <> None):
			matchingComponent.appendComponent(previousComponent)
		else:
			self.iCompletedComponents.append(previousComponent)
		scanner.ReportAction("End component: " + previousComponent.iFullPath)
		scanner.iRendererManager.EndComponent(previousComponent)

	def MatchingComponent(self, aComponent):
		for component in self.iCompletedComponents:
			if (ComponentCompare(component, aComponent) == 0):
				return component
		return None

	def CurrentComponentName(self):
		if len(self.iComponentStack) < 1:
			return None
		return self.iComponentStack[len(self.iComponentStack)-1].iFullPath

	def SanitizePath(self, aPath):
		# Translate an unspecified or relative pathname into an absolute pathname
		if len(aPath) < 1:
			aPath = "."
		aPath = os.path.normpath(aPath)
		# translate "." and ".." into absolute paths
		aPath = os.path.abspath(aPath)
		return aPath

	def ComponentName(self, aFullComponentName):
		if (self.iUseFullComponentPath):
			(unused, componentName) = os.path.splitdrive(aFullComponentName)
			if len(componentName) > 0:
				if componentName[0] == os.path.sep and len(componentName) > 1:
					componentName = componentName[1:]
			return componentName
		else:
			return self.RelativeComponentName(aFullComponentName)

	def RelativeComponentName(self, aFullComponentName):
		# Remove the root path from the specified component name
		rootLen = len(self.iRootPath)
		if aFullComponentName[0:rootLen] == self.iRootPath:
			relativeComponentName = aFullComponentName[rootLen:]
		else:
			# this case is unexpected...but we'll try to make the best of it
			(unused, relativeComponentName) = os.path.splitdrive(aFullComponentName)
		# trim leading path separator, if present
		if len(relativeComponentName) > 0:
			if relativeComponentName[0] == os.path.sep and len(relativeComponentName) > 1:
				relativeComponentName = relativeComponentName[1:]
		return relativeComponentName


class CLineContext:

	# #######################################################
	# CLineContext
	# A description of the line of source code currently being scanned

	iComponentName = ""
	iFileName = ""
	iLineNumber = 0
	iClassName = ""
	iMethodName = ""
	iLineText = ""


class CCodeScanner:

	# #######################################################
	# CCodeScanner - main application class

	def __init__(self):
		self.iCategoriedScripts = CCategorisedScripts()
		self.iRendererManager   = CRendererManager()
		self.iComponentManager = CComponentManager()
		self.iLineContext = CLineContext()
		self.iDomConfig = None
		self.iVerbose = False
		self.iLog = None
		self.iSource = None
		self.iEncodedFileList = None
		self.iOutputDirectory = None
		self.iStartTimeObj = None
		self.iStartTime = None
		self.iEndTime = None
		self.iLxrUrl = None
		self.iLxrVersion = None
		self.iConfigFilename = ""
		self.iInputFilenames = ""
		self.iLogFilename = ""
		self.iOutputFormat = ""
		self.iTimeStampedOutput = ""
		self.iReMethod = re.compile(r"""
			((?P<class>\w+)::~?)?
			(?P<method>[A-Za-z0-9<>=!*\-+/]+)
			[\s\n]*
			\(
			[^;]*
			$
			""", re.VERBOSE)

	def ReportError(self, aErrorMsg):
		self.iLog.Write(aErrorMsg)
		print aErrorMsg

	def ReportAction(self, aAction):
		self.iLog.Write(aAction)
		if self.iVerbose:
			print aAction

	def ReportInfo(self, aInfoMsg):
		self.iLog.Write(aInfoMsg)
		print aInfoMsg

	def CleanOutputDirectory(self):
		self.iLog.Write("Deleting existing contents of output directory " + self.iOutputDirectory)
		for root, dirs, files in os.walk(self.iOutputDirectory, topdown = False):
			for name in files:
				os.remove(os.path.join(root, name))
			for name in dirs:
				os.rmdir(os.path.join(root, name))

	def CheckSourceIncluded(self, aSourceFileName):
		if (self.iDomConfig <> None):
			for sourceNode in self.iDomConfig.getElementsByTagName("sources"):
				for excludeSourceNode in sourceNode.getElementsByTagName("exclude"):
					reExcludeSourceStr = excludeSourceNode.firstChild.nodeValue
					reExcludeSource = re.compile(reExcludeSourceStr, re.IGNORECASE)
					if reExcludeSource.search(aSourceFileName):
						self.ReportInfo("Note: excluding " + aSourceFileName + " : " + reExcludeSourceStr)
						return False
		return True

	def CheckScriptEnabled(self, aScript):
		if (self.iDomConfig <> None):
			for scriptsNode in self.iDomConfig.getElementsByTagName("scripts"):
				for scriptNode in scriptsNode.getElementsByTagName(aScript.iScriptName):
					enabledAttr = scriptNode.getAttribute("enable")
					if (enabledAttr.lower() == "false"):
						return False
			for severitiesNode in self.iDomConfig.getElementsByTagName("severities"):
				for severityNode in severitiesNode.getElementsByTagName(KSeverityConfigMap[aScript.iSeverity]):
					enabledAttr = severityNode.getAttribute("enable")
					if (enabledAttr.lower() == "false"):
						return False
			for categoriesNode in self.iDomConfig.getElementsByTagName("categories"):
				for categoryNode in categoriesNode.getElementsByTagName(KCategoryConfigMap[aScript.iCategory]):
					enabledAttr = categoryNode.getAttribute("enable")
					if (enabledAttr.lower() == "false"):
						return False
		return True

	def UpdateScriptCategory(self, aScript):
		if (self.iDomConfig <> None):
			for scriptsNode in self.iDomConfig.getElementsByTagName("scripts"):
				for scriptNode in scriptsNode.getElementsByTagName(aScript.iScriptName):
					if scriptNode.hasAttribute("category"):
						newCategory = scriptNode.getAttribute("category").lower()
						if (newCategory <> KCategoryConfigMap[aScript.iCategory]):
							for name, value in KCategoryConfigMap.items():
								if (newCategory == value):
									return name
		# no update needed, return original category
		return aScript.iCategory

	def UpdateScriptSeverity(self, aScript):
		if (self.iDomConfig <> None):
			for scriptsNode in self.iDomConfig.getElementsByTagName("scripts"):
				for scriptNode in scriptsNode.getElementsByTagName(aScript.iScriptName):
					if scriptNode.hasAttribute("severity"):
						newSeverity = scriptNode.getAttribute("severity").lower()
						if (newSeverity <> KSeverityConfigMap[aScript.iSeverity]):
							for name, value in KSeverityConfigMap.items():
								if (newSeverity == value):
									return name
		# no update needed, return original severity
		return aScript.iSeverity

	def ScanFile(self, aSourceFile):
		self.iLineContext.iFileName = aSourceFile
		self.iLineContext.iLineNumber = 0
		self.iLineContext.iClassName = ""
		self.iLineContext.iMethodName = ""
		self.iLineContext.iComponentName = self.iComponentManager.CurrentComponentName()

		self.iRendererManager.BeginFile(aSourceFile)

		# note source file extension - used for filtering later on
		(unused, sourceFileExt) = os.path.splitext(aSourceFile)
		if len(sourceFileExt) > 0 and sourceFileExt[0] == '.':
			sourceFileExt = sourceFileExt[1:]

		# open, read, and preparse source file
		inputFileHandle = file(aSourceFile, "r")
		inputFileLines = inputFileHandle.readlines()
		inputFileHandle.close()
		
		(noQuoteFileLines, noCommentFileLines, noCommentOrQuoteFileLines, csCommands) = self.PreParseSourceFile(inputFileLines)

		# bundle all the filtered versions of the file contents into
		# a hash to re-factor code
		fileContentsToTest = { KIgnoreNothing           : inputFileLines,
							   KIgnoreComments          : noCommentFileLines,
							   KIgnoreQuotes            : noQuoteFileLines,
							   KIgnoreCommentsAndQuotes : noCommentOrQuoteFileLines
							   }

		# now apply test scripts to source file
		iBraceCount = 0
		iBraceCountList = []
		newCurrentClassName = ""
		newCurrentMethodName = ""
		self.iCurrentClassName = ""
		self.iCurrentMethodName = ""
		self.iCurrentMethodStart = -1

		totalNumberOfLines = len(inputFileLines)
		reConstant = re.compile(r"""
			^\s*
			(static\s+)?
			const
			\s+
			\w+		# type
			\s*
			[\*&]?	# reference or pointer
			\s*
			\w+		# name
			\s*
			(=|\()
			""", re.VERBOSE)
		reInheritance = re.compile("[\s:]*(public|protected|private)\s*([\w:]+)")
		rePreprocessorIf = re.compile("^\s*\#(el)*if(.*)")
		rePreprocessorElse = re.compile("^\s*\#else")
		rePreprocessorEnd = re.compile("^\s*\#endif")
		reTypedef = re.compile("^\s*typedef")
		i = 0
		while (i < totalNumberOfLines):
			# for extra open braces in #if blocks
			if (rePreprocessorIf.search(noCommentOrQuoteFileLines[i])):
				iBraceCountList.append(iBraceCount)
			if (rePreprocessorElse.search(noCommentOrQuoteFileLines[i])):
				if (len(iBraceCountList) > 0):
					iBraceCount = iBraceCountList.pop()
			if (rePreprocessorEnd.search(noCommentOrQuoteFileLines[i])):
				if (len(iBraceCountList) > 0):
					iBraceCountList.pop()

			if (newCurrentMethodName == ""):
				methodString = noCommentOrQuoteFileLines[i]
				currentLine = i
				m = self.iReMethod.search(methodString)
				if not m and (i + 1 < totalNumberOfLines):
					currentLine = i + 1
					methodString += noCommentOrQuoteFileLines[currentLine]
					m = self.iReMethod.search(methodString)

				if m and (iBraceCount == 0) and (methodString.find("#") == -1) and (methodString.find("_LIT") == -1):	# must be at root level and not a preprocessor directive or a _LIT
					if not reTypedef.match(methodString) and not reConstant.match(methodString):  # must not be typedef or constant declaration 
						# check for cases where macros are used to declare a class
						# by searching for the inheritance part
						# eg. NONSHARABLE_CLASS(CMyClass) : public CBase
						isClass = reInheritance.search(methodString)
						if not isClass and (currentLine + 1 < totalNumberOfLines):
							methodString += noCommentOrQuoteFileLines[currentLine + 1]
							isClass = reInheritance.search(methodString)
						if not isClass:
							newCurrentMethodName = m.group('method')
							if m.group('class'):
								newCurrentClassName = m.group('class')
							else:
								newCurrentClassName = ""

			iBraceCount += noCommentOrQuoteFileLines[i].count("{")
			if (iBraceCount > 0) and (newCurrentMethodName <> ""):
				self.iCurrentClassName = newCurrentClassName
				self.iCurrentMethodName = newCurrentMethodName
				self.iCurrentMethodStart = i
				newCurrentClassName = ""
				newCurrentMethodName = ""

			self.iLineContext.iLineNumber = i+1
			self.iLineContext.iClassName = self.iCurrentClassName
			self.iLineContext.iMethodName = self.iCurrentMethodName

			# perform all test scripts onto source file									   
			for script in self.iCategoriedScripts.AllScripts():
				if (script.iFileExts.count(sourceFileExt) > 0
				    and fileContentsToTest[script.iIgnore][i] != "\n"
					and	script.iCompare(fileContentsToTest[script.iIgnore], i, script.iReMatch, aSourceFile)):
					# skip any script that has been disabled via CodeScanner command(s) in sources
					if script.iScriptName.lower() in csCommands[i].lower():
						continue
					self.iLineContext.iLineText = fileContentsToTest[script.iIgnore][i]
					self.iComponentManager.ReportError(self.iLineContext, script)

			iBraceCount -= noCommentOrQuoteFileLines[i].count("}")
			if (iBraceCount < 0):	# for extra close braces in #if blocks
				iBraceCount = 0

			if (iBraceCount == 0):
				self.iCurrentClassName = ""
				self.iCurrentMethodName = ""
				self.iCurrentMethodStart = -1

			i = i + 1

		self.iRendererManager.EndFile()
		return totalNumberOfLines

	def TraverseDirectory(self, aDirectory):
		# skip folders marked to be excluded in configuration file
		aPath = self.iComponentManager.SanitizePath(aDirectory)
		if (not self.CheckSourceIncluded(aPath)) or (not self.CheckSourceIncluded(aPath + os.path.sep)):
			return
		aDirectory = self.iComponentManager.BeginDirectory(aDirectory)
		contents = os.listdir(aDirectory)
		numberOfLinesScanned = 0
		for entry in contents:
			entryPath = os.path.normpath(os.path.join(aDirectory, entry))
			if os.path.isdir(entryPath):
				self.TraverseDirectory(entryPath)
			else:
				if self.CheckSourceIncluded(entryPath):
					numberOfLinesScanned += self.ScanFile(entryPath)
		self.iComponentManager.EndDirectory(aDirectory, numberOfLinesScanned)

	def AddScript(self, aScript):
		enabled = self.CheckScriptEnabled(script)
		if enabled:
			aScript.iCategory = self.UpdateScriptCategory(aScript)
			aScript.iSeverity = self.UpdateScriptSeverity(aScript)
			self.iCategoriedScripts.AddScript(aScript)
		else:
			self.ReportInfo("Note: script '" + aScript.iScriptName + "' DISABLED")

	def AddCustomScript(self, aScript):
		self.ReportInfo("Note: custom rule '" + aScript.iScriptName + "' ADDED")
		self.iCategoriedScripts.AddScript(aScript)

	def PreParseSourceFile(self, aLines):
		# it provides 3 versions of input:
		# 	1. without quotes
		# 	2. without comments
		# 	3. without quotes and without comments
		
		inCommentBlock = 0
		noQuoteLines = []
		noCommentLines = []
		noCommentOrQuoteLines = []
		csCommands = []
		reCSCommand = re.compile("codescanner((::\w+)+)") # CodeScanner command(s) in comments

		for line in aLines:
			noQuoteLine = ""
			noCommentLine = ""
			noCommentOrQuoteLine = ""
			csCommand = "\n"

			i = 0
			startQuote = 0
			b = 0
			escCount = 0

			while i < len(line):
				# skip quotes
				if not inCommentBlock and ((line[i] == "\"") or (line[i] == "\'")):
					startQuote = i
					i += 1
					while (i < len(line)):
						endIndex = line[i:].find(line[startQuote])
						if (endIndex <> -1):
							b = i + endIndex - 1
							escCount = 0
							while (line[b] == "\\"):
								escCount += 1
								b -= 1

							i += endIndex + 1
							if (escCount % 2 == 0):
								noQuoteLine += "\"\""
								noCommentOrQuoteLine += "\"\""
								noCommentLine += line[startQuote:i]
								break
						else:
							#	print "Unterminated quote : " + line
							break
					continue	
				
				# parse comments
				if not inCommentBlock:
					if (line[i] == "/"):
						if (i < (len(line)-1)):
							if (line[i + 1] == "/"):
								noCommentLine += "\n"
								noCommentOrQuoteLine += "\n"
								noQuoteLine += line[i:]
								# look for CodeScanner command(s) in comments
								m = reCSCommand.search(line[i:])
								if m:
									csCommand = m.group(1)
								break
							elif (line[i + 1] == "*"):
								inCommentBlock = 1
								i += 2
								noQuoteLine += "/*"
								continue

					noCommentLine += line[i]
					noCommentOrQuoteLine += line[i]
					noQuoteLine += line[i]
				else:
					# look for CodeScanner command(s) in comments
					m = reCSCommand.search(line[i:])
					if m:
						csCommand = m.group(1)
					endIndex = line[i:].find("*/")
					if (endIndex <> -1):
						inCommentBlock = 0
						noQuoteLine += line[i:i + endIndex + 2]
						i += endIndex + 2
						continue
					else:
						noCommentLine += "\n"
						noCommentOrQuoteLine += "\n"
						noQuoteLine = line[i:]
						break
				
				i += 1

			noCommentLines.append(noCommentLine)
			noCommentOrQuoteLines.append(noCommentOrQuoteLine)
			noQuoteLines.append(noQuoteLine)
			csCommands.append(csCommand)

		return [noQuoteLines, noCommentLines, noCommentOrQuoteLines, csCommands]

	def ReadConfigFile(self):
		if self.iConfigFilename <> "":
			if (os.path.isfile(self.iConfigFilename)):
				self.iDomConfig = xml.dom.minidom.parse(self.iConfigFilename)
				if self.iVerbose:
					print "Note: using configuration file " + self.iConfigFilename
			else:
				self.ReportInfo("Unable to open specified configuration file: " + self.iConfigFilename)
				self.iLog.Close()
				sys.exit(2)

	def ReadArgumentsFromConfigFile(self):
		if (self.iDomConfig <> None):
			for argumentsNode in self.iDomConfig.getElementsByTagName("arguments"):
				# read input file names
				for inputFileNode in argumentsNode.getElementsByTagName("input"):
					self.iInputFilenames += inputFileNode.firstChild.nodeValue + "::"
				# read output format
				for outputFormatNode in argumentsNode.getElementsByTagName("outputformat"):
					self.iOutputFormat += outputFormatNode.firstChild.nodeValue
				# read lxr URL
				for lxrURLNode in argumentsNode.getElementsByTagName("lxr"):
					self.iLxrUrl = lxrURLNode.firstChild.nodeValue
				# read lxr version
				for lxrVersionNode in argumentsNode.getElementsByTagName("lxrversion"):
					self.iLxrVersion = lxrVersionNode.firstChild.nodeValue
				# read time stamped output option
				for timeStampedOutputNode in argumentsNode.getElementsByTagName("timestampedoutput"):
					self.iTimeStampedOutput = timeStampedOutputNode.firstChild.nodeValue

	def ReadCustomRulesFromConfigFile(self):
		if (self.iDomConfig <> None):
			for customRulesNode in self.iDomConfig.getElementsByTagName("customrules"):
				for customRuleNode in customRulesNode.getElementsByTagName("customrule"):
					ignoreComments = True

					# read the name of the rule
					ruleName = ""
					for ruleNameNode in customRuleNode.getElementsByTagName("name"):
						if (ruleNameNode == None) or (ruleNameNode.firstChild == None) or (ruleNameNode.firstChild.nodeValue == None):
							continue
						else:
							ruleName = ruleNameNode.firstChild.nodeValue
					if len(ruleName) == 0:
						self.ReportError("Missing custom rule name in configuration file: " + self.iConfigFilename)
						continue

					# read the keywords associated with the rule
					keywordList = []
					badKeywordElement = False
					for keywordNode in customRuleNode.getElementsByTagName("keyword"):
						# read keyword content
						if (keywordNode == None) or (keywordNode.firstChild == None) or (keywordNode.firstChild.nodeValue == None):
							badKeywordElement = True
							continue
						newKeyword = CCustomRuleKeyword()
						newKeyword.iContent = keywordNode.firstChild.nodeValue

						# read keyword type
						if not keywordNode.hasAttribute("type"):
							badKeywordElement = True
							continue
						type = keywordNode.getAttribute("type").lower()
						if type in KCustomRuleKeywordMap.values():
							if type == KKeywordComment:
								ignoreComments = False
						else:
							type = KCustomRuleKeywordMap[KKeywordUnknown]
						newKeyword.iType = type
						keywordList.append(newKeyword)
					if (len(keywordList) == 0) or (badKeywordElement == True):
						self.ReportBadCustomRuleElement(ruleName, "keyword")
						continue

					# read the file types associated with the rule
					fileTypeList = []
					badFileTypeElement = False
					for fileTypeNode in customRuleNode.getElementsByTagName("filetype"):
						if (fileTypeNode == None) or (fileTypeNode.firstChild == None) or (fileTypeNode.firstChild.nodeValue == None):
							badFileTypeElement = True
							continue
						newFileType = fileTypeNode.firstChild.nodeValue
						fileTypeList.append(newFileType.lower())
					if (len(fileTypeList) == 0) or (badFileTypeElement == True):
						self.ReportBadCustomRuleElement(ruleName, "file type")
						continue

					# read the severity level of the rule
					severity = KSeverityLow
					for severityNode in customRuleNode.getElementsByTagName("severity"):
						if (severityNode == None) or (severityNode.firstChild == None) or (severityNode.firstChild.nodeValue == None):
							self.ReportBadCustomRuleElement(ruleName, "severity")
							continue
						severityValue = severityNode.firstChild.nodeValue
						for severityKey in KSeverityConfigMap.keys():
							if severityValue == KSeverityConfigMap[severityKey]:
								severity = severityKey

					# read the tile of the rule
					title = ""
					for titleNode in customRuleNode.getElementsByTagName("title"):
						if (titleNode == None) or (titleNode.firstChild == None) or (titleNode.firstChild.nodeValue == None):
							continue
						title = titleNode.firstChild.nodeValue
					if len(title) == 0:
						self.ReportBadCustomRuleElement(ruleName, "title")
						continue

					# read the description of the rule
					description = ""
					for descriptionNode in customRuleNode.getElementsByTagName("description"):
						if (descriptionNode == None) or (descriptionNode.firstChild == None) or (descriptionNode.firstChild.nodeValue == None):
							continue
						description = descriptionNode.firstChild.nodeValue
					if len(description) == 0:
						self.ReportBadCustomRuleElement(ruleName, "description")
						continue

					# read the optional link of the rule
					link = None
					for linkNode in customRuleNode.getElementsByTagName("link"):
						if (linkNode == None) or (linkNode.firstChild == None) or (linkNode.firstChild.nodeValue == None):
							self.ReportBadCustomRuleElement(ruleName, "link")
							continue
						link = linkNode.firstChild.nodeValue

					# create the RE string for the custom rule
					keywordMap = self.ConstructCustomRuleKeywordMap(keywordList)
					reString = self.ConstructCustomRuleREString(keywordMap)
					if len(reString) == 0:
						continue
					
					# create a script based on the custom rule
					aScript = CCustomScript(ruleName)
					aScript.iReString = reString
					aScript.iReMatch = re.compile(reString)
					aScript.iFileExts = fileTypeList
					aScript.iCategory = KCategoryOther
					if keywordMap.has_key(KKeywordBaseClass):
						aScript.iBaseClass = keywordMap[KKeywordBaseClass]
						aScript.iCompare = aScript.DefaultInheritanceCompare
					if ignoreComments:
						aScript.iIgnore = KIgnoreComments
					else:
						aScript.iIgnore = KIgnoreQuotes
					aScript.iSeverity = severity
					aScript.iTitle = title
					aScript.iIdeTitle = title
					aScript.iDescription = description
					if link <> None:
						aScript.iLink = link
					self.AddCustomScript(aScript)
		return

	def ReportBadCustomRuleElement(self, name, element):
		self.ReportError("<customrule> element '" + name + "' has bad <" + element + "> child element in configuration file: " + self.iConfigFilename)

	def ConstructCustomRuleKeywordMap(self, keywordList):
		reString = ""
		keywordMap = {}
		for keyword in keywordList:
			if keywordMap.has_key(keyword.iType):
				keywordMap[keyword.iType] = keywordMap[keyword.iType] + "|" + keyword.iContent
			else:
				keywordMap[keyword.iType] = keyword.iContent
		return keywordMap

	def ConstructCustomRuleREString(self, keywordMap):
		# generate RE string based on the keyword types
		if keywordMap.has_key(KKeywordBaseClass):
			reString = "^\s*class\s+(\w+::)?(\w+)\s*:(.*)"
		elif keywordMap.has_key(KKeywordCall):
			reString = "(" + keywordMap[KKeywordCall] + ")\s*\(.*\)\s*;"
		elif keywordMap.has_key(KKeywordClassName):
			if keywordMap.has_key(KKeywordMethod):
				reString = "([A-Za-z0-9]+\s+" + keywordMap[KKeywordClassName] + "::)?(" + keywordMap[KKeywordMethod] + ")\s*\(.*\)\s*[^;]"
			else:
				reString = "^\s*class\s+(\w+::)?(" + keywordMap[KKeywordClassName] + ")"
		elif keywordMap.has_key(KKeywordComment):
			reString = "/(/|\*).*(" + keywordMap[KKeywordComment] + ")"
		elif keywordMap.has_key(KKeywordGeneric):
			reString = "(" + keywordMap[KKeywordGeneric] + ")"
		elif keywordMap.has_key(KKeywordLocal):
			reString = "^\s*[A-Z]\w*\s*[\*&\s]\s*(" + keywordMap[KKeywordLocal] + ")\w*\s*[;\(=]"
		elif keywordMap.has_key(KKeywordMacro):
			reString = "^\s*\#define\s+(" + keywordMap[KKeywordMacro] + ")"
		elif keywordMap.has_key(KKeywordMember):
			reString = "^\s*[A-Z]\w*\s*[\*&\s]\s*(" + keywordMap[KKeywordMember] + ")\w*\s*[;\(=]"
		elif keywordMap.has_key(KKeywordMethod):
			reString = "[A-Za-z0-9]+\s+[C|T|R][A-Za-z0-9]+::(" + keywordMap[KKeywordMethod] + ")\s*\(.*\)\s*[^;]"
		elif keywordMap.has_key(KKeywordParameter):
			reString = "({)*\s*(" + keywordMap[KKeywordParameter] + ")\s*=\s*(.*);"
		return reString


class CCustomRuleKeyword:
	# #######################################################
	# CCustomRuleKeyword - keyword associated with custom rules

	def __init__(self):
		iContent = ""
		iType = "unknown"


# #######################################################

class CEncodedFile:
    def Extract(self, aBaseDirectory):
        outputFileHandle = open(os.path.join(aBaseDirectory, self.iFilename), 'wb')
        outputFileBinary = zlib.decompress(base64.decodestring(self.iFileBody))
        outputFileHandle.write(outputFileBinary)
        outputFileHandle.close()

	iFilename = ""
	iFileBody = ""

# #######################################################


class CEncodedFileList:
	def AddEncodedFile(self, aEncodedFile):
		self.iEncodedFileList[aEncodedFile.iFilename.lower()] = aEncodedFile

	def ExtractEncodedFile(self, aFilename, aBaseDirectory):
		# look for the filename in our list of files
		filename = aFilename.lower()
		if (self.iEncodedFileList.has_key(filename)):
			self.iEncodedFileList[filename].Extract(aBaseDirectory)
		else:
			scanner.iLog.Write("Missing "+filename)

	def ExtractAllEncodedFiles(self, aBaseDirectory):
		# run through associative array and extract everything
		for filename in self.iEncodedFileList.keys():
			self.ExtractEncodedFile(filename, aBaseDirectory)

	# declare iEncodedFileList is an associative array
	iEncodedFileList = {}


# #######################################################
# main()
scanner = CCodeScanner()

# process command line arguments
opts, args = getopt.getopt(sys.argv[1:], "hvc:i:l:o:x:r:t:", ["help", "verbose", "config=", "input=", "logfile=", "outputformat=", "lxr=", "lxrversion=", "timestampedoutput="])
for o, a in opts:
	if o in ("-h", "--help"):
		Usage(0)
	if o in ("-v", "--verbose"):
		scanner.iVerbose = True
	if o in ("-c", "--config"):
		scanner.iConfigFilename = a
	if o in ("-i", "--input"):
		scanner.iInputFilenames += a + "::"
	if o in ("-l", "--logfile"):
		scanner.iLogFilename = a
	if o in ("-o", "--outputformat"):
		scanner.iOutputFormat += a			
	if o in ("-x", "--lxr"):
		scanner.iLxrUrl = a
	if o in ("-r", "--lxrversion"):
		scanner.iLxrVersion = a
	if o in ("-t", "--timestampedoutput"):
		scanner.iTimeStampedOutput = a

if len(args) < 1:
	Usage(1)

scanner.iLog = CLogger(scanner.iLogFilename)
scanner.iLog.Write("Command line: " + str(sys.argv[1:]))
scanner.iLog.Write("Current working directory: " + os.getcwd())

scanner.ReadConfigFile()
scanner.ReadArgumentsFromConfigFile()
scanner.ReadCustomRulesFromConfigFile()

scanner.iSource = args[0]
scanner.iEncodedFileList = CEncodedFileList()
scanner.iStartTimeObj = datetime.datetime.now()
scanner.iStartTime = scanner.iStartTimeObj.ctime()
scanner.iOutputDirectory = scanner.iStartTimeObj.strftime("%a-%b-%d-%H-%M-%S-%Y")

# invoke the pysco module to improve performance
psyco.full()

# choose renderer based on command line arguments
if len(args) > 1:
	if ("off" in scanner.iTimeStampedOutput.lower()):
		scanner.iOutputDirectory = args[1]
	else:
		scanner.iOutputDirectory = os.path.normpath(os.path.join(args[1], scanner.iOutputDirectory))
	scanner.CleanOutputDirectory()
	if scanner.iOutputFormat <> "":
	#user specified output format
		if ("xml" in scanner.iOutputFormat.lower()):
			CXmlRenderer(scanner.iRendererManager, scanner.iOutputDirectory)
		if ("html" in scanner.iOutputFormat.lower()):
			CHtmlRenderer(scanner.iRendererManager, scanner.iOutputDirectory, scanner.iLxrUrl, scanner.iLxrVersion)
		if ("std" in scanner.iOutputFormat.lower()):
			CStdOutRenderer(scanner.iRendererManager)
	else:
	#default output format
		CHtmlRenderer(scanner.iRendererManager, scanner.iOutputDirectory, scanner.iLxrUrl, scanner.iLxrVersion)
else:
	CStdOutRenderer(scanner.iRendererManager)

#!PARSE

if (scanner.iVerbose):
	scanner.iCategoriedScripts.PrintListOfTestScripts()
	scanner.iRendererManager.PrintListOfRenderers()

print
print "Scanning inititated : " + scanner.iStartTime

if scanner.iInputFilenames <> "":
	scanner.iComponentManager.iUseFullComponentPath = True
	#additional input files
	inputFiles = scanner.iInputFilenames.split("::")
	for inputFile in inputFiles:
		if inputFile <> "":
			ScanDirOrFile(inputFile)

argument = args[0]
ScanDirOrFile(argument)

print "Scanning finished   : " + scanner.iEndTime
scanner.iLog.Close()

if (scanner.iDomConfig <> None):
	scanner.iDomConfig.unlink()

sys.exit(0)
