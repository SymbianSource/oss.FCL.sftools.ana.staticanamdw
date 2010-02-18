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
#
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
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# English.loc
# localised string for Script accessArrayElementWithoutCheck

stringPool[ "accessArrayElementWithoutCheck!title" ]       = "Array element accessed by At() function without checking index is within array range"
stringPool[ "accessArrayElementWithoutCheck!description" ] = "Whenever an element in an array is accessed, the index should be checked to ensure that it is less than array.Count(). CodeScanner checks for explicit calls to a Count() function; so if the array index is checked in a different way, it gives false positives. Accessing an invalid index can cause a panic."
stringPool[ "accessArrayElementWithoutCheck!ideTitle" ]    = "array element accessed by At() function without checking index is within array range"

# localised string for Script accessArrayElementWithoutCheck2
stringPool[ "accessArrayElementWithoutCheck2!title" ]       = "Array element accessed by [] without checking range"
stringPool[ "accessArrayElementWithoutCheck2!description" ] = "Whenever an element in an array is accessed, the index should first be checked to ensure that it is within range. CodeScanner checks for explicit calls to a Count() or Length() function; so if the array index is checked in a different way, it gives false positives. Accessing an invalid index can cause a panic."
stringPool[ "accessArrayElementWithoutCheck2!ideTitle" ]    = "array element accessed by [] without checking range"

# localised string for Script activestart
stringPool[ "activestart!title" ]       = "Using CActiveScheduler::Start"
stringPool[ "activestart!description" ] = "Using CActiveScheduler::Start() can mean that something asynchronous is being made synchronous. Instead, use active objects correctly in an asynchronous way."
stringPool[ "activestart!ideTitle" ]    = "using CActiveScheduler::Start"

# localised string for Script activestop
stringPool[ "activestop!title" ]       = "Using CActiveScheduler::Stop"
stringPool[ "activestop!description" ] = "Using CActiveScheduler::Stop() can mean that something asynchronous is being made synchronous. Instead, use active objects correctly in an asynchronous way."
stringPool[ "activestop!ideTitle" ]    = "using CActiveScheduler::Stop"

# localised string for Script arraypassing
stringPool[ "arraypassing!title" ]       = "Passing arrays by value rather than reference"
stringPool[ "arraypassing!description" ] = "Passing arrays by value causes the array to be copied needlessly, which takes up time and memory. For efficiency, references should be used."
stringPool[ "arraypassing!ideTitle" ]    = "passing arrays by value rather than reference"

# localised string for Script arrayptrcleanup
stringPool[ "arrayptrcleanup!title" ]       = "Using local CArrayPtr classes without cleanup items"
stringPool[ "arrayptrcleanup!description" ] = "It is not enough to push a local CArrayPtr class onto the cleanup stack. A TCleanupItem and callback function must be used to avoid leaking the elements."
stringPool[ "arrayptrcleanup!ideTitle" ]    = "using local CArrayPtr classes without cleanup items"

# localised string for Script assertdebuginvariant
stringPool[ "assertdebuginvariant!title" ]       = "__ASSERT_DEBUG with User::Invariant"
stringPool[ "assertdebuginvariant!description" ] = "Replace __ASSERT_DEBUG(<condition>, User::Invariant()) with ASSERT(<condition>), because it is easier to read."
stringPool[ "assertdebuginvariant!ideTitle" ]    = "__ASSERT_DEBUG with User::Invariant"

# localised string for Script baddefines
stringPool[ "baddefines!title" ]       = "Lowercase definition names"
stringPool[ "baddefines!description" ] = "Badly-named definitions makes the code harder to maintain and can lead to defects."
stringPool[ "baddefines!ideTitle" ]    = "lowercase definition names"

# localised string for Script baseconstruct
stringPool[ "baseconstruct!title" ]       = "Leaving function called before BaseConstructL()"
stringPool[ "baseconstruct!description" ] = "If a leave occurs before BaseConstructL() is called, the system can panic because it is trying to clean up an application that has not been fully initialised."
stringPool[ "baseconstruct!ideTitle" ]    = "leaving method called before BaseConstructL"

# localised string for Script callActiveObjectWithoutCheckingOrStopping
stringPool[ "callActiveObjectWithoutCheckingOrStopping!title" ]       = "Active object called without checking whether it is active or canceling it first"
stringPool[ "callActiveObjectWithoutCheckingOrStopping!description" ] = "If an active object is started twice, a panic occurs. CodeScanner picks out places where there is a call to a Start(), Queue(), or After() function on a member variable, without a previous call to IsActive(), Cancel(), or Stop(). In general, if starting a timer, there should at least be a call to IsActive() to ensure that the timer is not already running."
stringPool[ "callActiveObjectWithoutCheckingOrStopping!ideTitle" ]    = "active object called without checking whether it is active or canceling it first"

# localised string for Script changenotification
stringPool[ "changenotification!title" ]       = "Using RSAVarChangeNotify to see System Agent changes"
stringPool[ "changenotification!description" ] = "When watching for System Agent changes, use RSystemAgent rather than RSAVarChangeNotify, which can fail."
stringPool[ "changenotification!ideTitle" ]    = "using RSAVarChangeNotify to see System Agent changes"

# localised string for Script cleanup
stringPool[ "cleanup!title" ]       = "CleanupStack::Pop(AndDestroy) parameters"
stringPool[ "cleanup!description" ] = "These functions should be called with explicit variable parameters to avoid misalignment."
stringPool[ "cleanup!ideTitle" ]    = "missing CleanupStack::Pop parameter"

# localised string for Script commentcode
stringPool[ "commentcode!title" ]       = "Commented-out code"
stringPool[ "commentcode!description" ] = "Instances of code that are commented out make the code hard to maintain and to interpret clearly. The commented out code should be removed. Any requirement to rediscover old code should be made through source control and not by trawling through commented-out code."
stringPool[ "commentcode!ideTitle" ]    = "commented-out code"

# localised string for Script connect
stringPool[ "connect!title" ]       = "Ignoring Connect() return value"
stringPool[ "connect!description" ] = "Ignoring the error returned from Connect() functions means that if the Connect() function fails due to OOM or other problems, the next access to the resource will panic."
stringPool[ "connect!ideTitle" ]    = "ignoring Connect() return value"

# localised string for Script ConnectAndDontCloseMemberVariable
stringPool[ "ConnectAndDontCloseMemberVariable!title" ]       = "Calling Connect() or Open() on a member variable without calling Close() in the destructor"
stringPool[ "ConnectAndDontCloseMemberVariable!description" ] = "If Connect() or Open() is called on any member variable, then Close() must be called in the destructor."
stringPool[ "ConnectAndDontCloseMemberVariable!ideTitle" ]    = "calling Connect() or Open() on a member variable without calling Close() in the destructor"

# localised string for Script constnames
stringPool[ "constnames!title" ]       = "Badly-named constants"
stringPool[ "constnames!description" ] = "Badly-named constant will make the source code harder to maintain and make defects more likely."
stringPool[ "constnames!ideTitle" ]    = "badly-named constant"

# localised string for Script consttdescptr
stringPool[ "consttdescptr!title" ]       = "Const descriptor pointer as argument"
stringPool[ "consttdescptr!description" ] = "Use \"const TDesC&\" instead of \"const TDesC*\"."
stringPool[ "consttdescptr!ideTitle" ]    = "const descriptor pointer as argument"

# localised string for Script controlornull
stringPool[ "controlornull!title" ]       = "Accessing return value of ControlOrNull()"
stringPool[ "controlornull!description" ] = "The return value might be NULL, so it should be checked before access."
stringPool[ "controlornull!ideTitle" ]    = "accessing return value of ControlOrNull()"

# localised string for Script crepository
stringPool[ "crepository!title" ]       = "Ignoring CRepository::get() return value"
stringPool[ "crepository!description" ] = "Independent application cannot assume that the Central Repository is set up fully. This means the return value of CRepository::get() cannot be ignored."
stringPool[ "crepository!ideTitle" ]    = "ignoring CRepository::get() return value"

# localised string for Script ctltargettype
stringPool[ "ctltargettype!title" ]       = "Use of targettype ctl"
stringPool[ "ctltargettype!description" ] = "The ctl target type should not be used. Instead, use DLL and explicitly refer to the Control Panel's DEF file. Note: Code that causes this issue only needs attention if it is found in code developed for Nokia Series 90 code that has extra exports for resetting the Control Panel item's data."
stringPool[ "ctltargettype!ideTitle" ]    = "use of targettype ctl"

# localised string for Script customizableicons
stringPool[ "customizableicons!title" ]       = "Use of customizable icons"
stringPool[ "customizableicons!description" ] = "Due to device customization requirements, independent application must not remove any customization done by the variant team. This means independent application cannot include customizable icons."
stringPool[ "customizableicons!ideTitle" ]    = "use of customizable icons"

# localised string for Script debugrom
stringPool[ "debugrom!title" ]       = "Debug components in ROM"
stringPool[ "debugrom!description" ] = "Debug versions of components in the ROM could mean that ROM space is being taken up with debugging information or that logging is being put out. Release versions should be in the ROM unless there is a good reason why they are not."
stringPool[ "debugrom!ideTitle" ]    = "debug components in ROM"

# localised string for Script declarename
stringPool[ "declarename!title" ]       = "Use of __DECLARE_NAME"
stringPool[ "declarename!description" ] = "The __DECLARE_NAME macro is historical and serves no purpose anymore and should be removed."
stringPool[ "declarename!ideTitle" ]    = "use of __DECLARE_NAME"

# localised string for Script deleteMemberVariable
stringPool[ "deleteMemberVariable!title" ]       = "Member variable deleted incorrectly"
stringPool[ "deleteMemberVariable!description" ] = "When a member variable is deleted, it should be assigned either to NULL or to another value. This prevents accidental access of the deleted object. If a NewL() or other leaving function is called to reassign the member variable, it should first be assigned to NULL in case that function leaves."
stringPool[ "deleteMemberVariable!ideTitle" ]    = "member variable deleted incorrectly"

# localised string for Script destructor
stringPool[ "destructor!title" ]       = "Pointer access in destructors"
stringPool[ "destructor!description" ] = "Accessing pointers to objects in destructors without checking whether they are not NULL could result in a panic because they may not have been constructed. The pointers should be checked to determine whether they are owned objects. If they are not owned, they should really be references rather than pointers."
stringPool[ "destructor!ideTitle" ]    = "destructor is accessing/dereferencing data member"

# localised string for Script doubleSemiColon
stringPool[ "doubleSemiColon!title" ]       = "Use of double semicolon"
stringPool[ "doubleSemiColon!description" ] = "Double semicolons at the end of a line are not necessary and cause a CodeWarrior compiler error."
stringPool[ "doubleSemiColon!ideTitle" ]    = "use of double semicolon"

# localised string for Script driveletters
stringPool[ "driveletters!title" ]       = "Hard-coded drive letters"
stringPool[ "driveletters!description" ] = "Drive letters should not be hard-coded."
stringPool[ "driveletters!ideTitle" ]    = "hard-coded drive letters"

# localised string for Script eikbuttons
stringPool[ "eikbuttons!title" ]       = "Checks that the R_EIK_BUTTONS_* resources are not being used"
stringPool[ "eikbuttons!description" ] = "R_EIK_BUTTONS_* resources will not be internationalised, and should not be used. Instead, create your own button resource. No button resource (or indeed, rls string) should be used in more than one location. Note: This issue is only relevant for development on Nokia platforms."
stringPool[ "eikbuttons!ideTitle" ]    = "use of R_EIK_BUTTONS_ resources"

# localised string for Script eikonenvstatic
stringPool[ "eikonenvstatic!title" ]       = "Using CEikonEnv::Static"
stringPool[ "eikonenvstatic!description" ] = "CEikonEnv::Static() calls should be kept to a minimum, because this involves TLS. All applications, controls, and dialogs already have a pointer to the singleton instance of CEikonEnv as a member variable and so do not need to find it again. If a class does not have access to a CEikonEnv and needs to use it repeatedly, then it should store one."
stringPool[ "eikonenvstatic!ideTitle" ]    = "using CEikonEnv::Static"

# localised string for Script enummembers
stringPool[ "enummembers!title" ]       = "Enums with badly-named members"
stringPool[ "enummembers!description" ] = "Enums with badly-named members make the code harder to maintain and may cause defects."
stringPool[ "enummembers!ideTitle" ]    = "enum with badly-named member"

# localised string for Script enumnames
stringPool[ "enumnames!title" ]       = "Badly-named enums"
stringPool[ "enumnames!description" ] = "Badly-named enums make the code harder to maintain and may cause defects."
stringPool[ "enumnames!ideTitle" ]    = "badly-named enum"

# localised string for Script exportinline
stringPool[ "exportinline!title" ]       = "Exporting inline functions"
stringPool[ "exportinline!description" ] = "Inline functions should not be exported because this can cause those that link to the DLL to fail to build. Exporting functions limits the changes that can be made in the future due to considerations of binary-compatibility."
stringPool[ "exportinline!ideTitle" ]    = "exporting inline functions"

# localised string for Script exportpurevirtual
stringPool[ "exportpurevirtual!title" ]       = "Exporting pure virtual functions"
stringPool[ "exportpurevirtual!description" ] = "Symbian recommends against the exportation of pure virtual functions."
stringPool[ "exportpurevirtual!ideTitle" ]    = "exporting pure virtual functions"

# localised string for Script externaldriveletters
# stringPool[ "externaldriveletters!title" ]       = "Hard-coded external drive letters"
# stringPool[ "externaldriveletters!description" ] = "External drive letters should not be hard-coded as the external drive may change between platforms and releases. This may cause confusion over ownership leading to classes being deleted erroneously and leaks occurring."
# stringPool[ "externaldriveletters!ideTitle" ]    = "hard-coded external drive letter"

# localised string for Script flags
stringPool[ "flags!title" ]       = "Use of R&D flags or feature flags"
stringPool[ "flags!description" ] = "Independent application must not use R&D flags nor feature flags via preprocessor statements in the source code. This means bld*.hrh and productvariant.hrh should not be used."
stringPool[ "flags!ideTitle" ]    = "use of R&D flags or feature flags"

# localised string for Script foff
stringPool[ "foff!title" ]       = "Use of _FOFF"
stringPool[ "foff!description" ] = "_FOFF allows access to data in classes that were not intended for public access. This may cause problems, especially when the location of the data changes."
stringPool[ "foff!ideTitle" ]    = "use of _FOFF"

# localised string for Script forbiddenwords
stringPool[ "forbiddenwords!title" ]       = "Use of forbidden words in header files"
stringPool[ "forbiddenwords!description" ] = "Some words should not be used in header files; especially those header files destined for external release. Some words may be forbidden for legal reasons or for platform consistency. Where they exist, alternative allowed words should be used. For example, \"NMP\" and \"Nokia Mobile Phones\" should be replaced by \"Nokia\"."
stringPool[ "forbiddenwords!ideTitle" ]    = "use of forbidden words in header files"

# localised string for Script forgottoputptroncleanupstack
stringPool[ "forgottoputptroncleanupstack!title" ]       = "Neglected to put variable on cleanup stack"
stringPool[ "forgottoputptroncleanupstack!description" ] = "If a variable is not put on the cleanup stack and a leaving function or ELeave is called, a memory leak occurs. CodeScanner occasionally gives false positives for this issue. Individual cases should be investigated."
stringPool[ "forgottoputptroncleanupstack!ideTitle" ]    = "neglected to put variable on cleanup stack"

# localised string for Script friend
stringPool[ "friend!title" ]       = "Use of friends"
stringPool[ "friend!description" ] = "The friend directive is often misused and can indicate problems in the OO design."
stringPool[ "friend!ideTitle" ]    = "use of friends"

# localised string for Script goto
stringPool[ "goto!title" ]       = "Use of goto"
stringPool[ "goto!description" ] = "Goto should not be used if it can be avoided because it makes the program flow more difficult to follow."
stringPool[ "goto!ideTitle" ]    = "use of goto"

# localised string for Script ifassignments
stringPool[ "ifassignments!title" ]       = "Assignment in an If statement"
stringPool[ "ifassignments!description" ] = "Assignments inside an If statement often indicate that the assignment was not intended. Even if the assignment was intended, it is clearer to separate out the assignment from the conditional. The script that detects such occurrences has a few false positives when the action statements are on the same line as the conditional check. However, this is also against the coding standards and the action should be on a separate line."
stringPool[ "ifassignments!ideTitle" ]    = "assignment in an If statement"

# localised string for Script ifpreprocessor
stringPool[ "ifpreprocessor!title" ]       = "Use of #if in .h files"
stringPool[ "ifpreprocessor!description" ] = "#if in header files should only be used before the main include guards and not around #include statements or around functional blocks in class definitions. The reason for the latter is to aid readability and to make BC breaks more difficult."
stringPool[ "ifpreprocessor!ideTitle" ]    = "use of #if in .h files (not as main include guards)"

# localised string for Script inheritanceorder
stringPool[ "inheritanceorder!title" ]       = "Incorrect inheritance order of M and C classes"
stringPool[ "inheritanceorder!description" ] = "If a C class inherits first from an M class and then a C class, a panic can occur when trying to pop a CBase pointer pointing to such a class from the cleanup stack when in fact a pointer pointing to the first predecessor, the mixin class, was popped instead."
stringPool[ "inheritanceorder!ideTitle" ]    = "incorrect inheritance order of M and C classes"

# localised string for Script intleaves
stringPool[ "intleaves!title" ]       = "Methods that leave AND return a TInt error"
stringPool[ "intleaves!description" ] = "Returning an error code as well as being able to leave is problematical for the caller. It is preferable to adhere to one method of returning the error. Note: CodeScanner is likely to return false positives for this situation, because some returned TInt values will not be error codes."
stringPool[ "intleaves!ideTitle" ]    = "methods that leave AND return a TInt error"

# localised string for Script jmp
stringPool[ "jmp!title" ]       = "Use of setjmp and/or longjmp"
stringPool[ "jmp!description" ] = "Using setjmp and/or longjmp makes code less maintainable."
stringPool[ "jmp!ideTitle" ]    = "use of setjmp and/or longjmp"

# localised string for Script leave
stringPool[ "leave!title" ]       = "Leaving functions called in non-leaving functions"
stringPool[ "leave!description" ] = "Non-leaving functions should not call leaving functions. Note: Operator functions are considered to be able to leave when scanning the code inside them."
stringPool[ "leave!ideTitle" ]    = "leaving function called in non-leaving function"

# localised string for Script LeaveNoError
stringPool[ "LeaveNoError!title" ]       = "Leaving with KErrNone"
stringPool[ "LeaveNoError!description" ] = "Leaving with KErrNone usually indicates that there is a makeshift way around a design issue rather than a true and proper fix to the architecture."
stringPool[ "LeaveNoError!ideTitle" ]    = "leaving with KErrNone"

# localised string for Script leavingoperators
stringPool[ "leavingoperators!title" ]       = "Leaving functions called in operator functions"
stringPool[ "leavingoperators!description" ] = "It is not obvious that operator functions can leave. Calling leaving functions in operator functions should be considered carefully."
stringPool[ "leavingoperators!ideTitle" ]    = "leaving functions called in operator functions"

# localised string for Script LFunctionCantLeave
stringPool[ "LFunctionCantLeave!title" ]       = "L-functions that cannot leave"
stringPool[ "LFunctionCantLeave!description" ] = "A function should not be named with an 'L' if it cannot leave. The only exception is in virtual functions where the function name is defined in the base class so the L cannot be removed. For example, RunL()."
stringPool[ "LFunctionCantLeave!ideTitle" ]    = "L-functions that cannot leave"

# localised string for Script longlines
stringPool[ "longlines!title" ]       = "Overly long lines of code"
stringPool[ "longlines!description" ] = "Lines longer than about 100 characters can indicate messy or badly-structured code that is hard to maintain."
stringPool[ "longlines!ideTitle" ]    = "overly long line of code"

# localised string for Script magicnumbers
stringPool[ "magicnumbers!title" ]       = "Use of magic numbers"
stringPool[ "magicnumbers!description" ] = "Magic numbers - that is, numbers that are hard-coded into the source code and instead of being presented as constants - make code difficult to maintain and give no indication of why a calculation is the way it is. Magic numbers should be replaced with named constants."
stringPool[ "magicnumbers!ideTitle" ]    = "use of magic numbers"

# localised string for Script mclassdestructor
stringPool[ "mclassdestructor!title" ]       = "M class has destructor"
stringPool[ "mclassdestructor!description" ] = "M classes should not contain a destructor."
stringPool[ "mclassdestructor!ideTitle" ]    = "M class has destructor"

# localised string for Script memberlc
stringPool[ "memberlc!title" ]       = "Assigning LC methods to member variables"
stringPool[ "memberlc!description" ] = "Objects on the cleanup stack should not be assigned to member variables"
stringPool[ "memberlc!ideTitle" ]    = "LC method assigned to data member"

# localised string for Script membervariablecallld
stringPool[ "membervariablecallld!title" ]       = "Calling LD function on member variable"
stringPool[ "membervariablecallld!description" ] = "LD functions should not be called on a member variable because ownership can be unclear and may lead to double deletes."
stringPool[ "membervariablecallld!ideTitle" ]    = "calling LD function on member variable"

# localised string for Script missingcancel
stringPool[ "missingcancel!title" ]       = "Cancel() not called in active object's destructor"
stringPool[ "missingcancel!description" ] = "Cancel() should always be called in active object's destructor to cancel an outstanding request if there is one. If there is no request pending then Cancel() just does nothing, but if we do not call Cancel() when having an outstanding request a panic will be raised. CodeScanner occasionally gives false positives for this issue. Individual cases should be investigated."
stringPool[ "missingcancel!ideTitle" ]    = "Cancel() not called in active object's destructor"

# localised string for Script missingcclass
stringPool[ "missingcclass!title" ]       = "C class not inheriting from another C class"
stringPool[ "missingcclass!description" ] = "All C classes should inherit from another C class to ensure that all data members are zeroed."
stringPool[ "missingcclass!ideTitle" ]    = "C class not inheriting from another C class"

# localised string for Script mmpsourcepath
stringPool[ "mmpsourcepath!title" ]       = "Use of absolute path names in MMP files"
stringPool[ "mmpsourcepath!description" ] = "Use of absolute paths in MMP files makes it impossible to relocate the source. Relative paths should be used instead."
stringPool[ "mmpsourcepath!ideTitle" ]    = "use of absolute path names in MMP files"

# localised string for Script multilangrsc
stringPool[ "multilangrsc!title" ]       = "Not using BaflUtils::NearestLanguageFile() when loading a resource file"
stringPool[ "multilangrsc!description" ] = "If AddResourceFileL() is used without first using BaflUtils::NearestLanguageFile(), then not all language versions of resources will be picked up."
stringPool[ "multilangrsc!ideTitle" ]    = "not using BaflUtils::NearestLanguageFile() when loading a resource file"

# localised string for Script multipledeclarations
stringPool[ "multipledeclarations!title" ]       = "Multiple declarations on one line"
stringPool[ "multipledeclarations!description" ] = "Multiple declarations on one line can be confusing. Separate them out so that each declaration is on its own separate line."
stringPool[ "multipledeclarations!ideTitle" ]    = "multiple declarations on one line"

# localised string for Script multipleinheritance
stringPool[ "multipleinheritance!title" ]       = "Non M-class multiple inheritance"
stringPool[ "multipleinheritance!description" ] = "It is bad Symbian OS practice to derive from two classes that have implemented functions. Complex behaviour that was not intended can result."
stringPool[ "multipleinheritance!ideTitle" ]    = "multiple inheritance from non M-classes"

# localised string for Script mydocs
stringPool[ "mydocs!title" ]       = "Hard-coded mydocs directory strings"
stringPool[ "mydocs!description" ] = "The mydocs directory is subject to change so should not be referenced directly. Note: @	This issue will only occur in code developed for the Nokia Series 90 platform."
stringPool[ "mydocs!ideTitle" ]    = "hard-coded mydocs directory strings"

# localised string for Script namespace
stringPool[ "namespace!title" ]       = "Use of namespace"
stringPool[ "namespace!description" ] = "Namespaces are often used to work around a poor naming convention."
stringPool[ "namespace!ideTitle" ]    = "use of namespace"

# localised string for Script newlreferences
stringPool[ "newlreferences!title" ]       = "NewL() returning a reference"
stringPool[ "newlreferences!description" ] = "NewL() and NewLC() functions should return a pointer to an object created on the heap."
stringPool[ "newlreferences!ideTitle" ]    = "NewL() returning a reference"

# localised string for Script noleavetrap
stringPool[ "noleavetrap!title" ]       = "TRAP used with no leaving functions"
stringPool[ "noleavetrap!description" ] = "A TRAP is unnecessary if there are no leaving functions."
stringPool[ "noleavetrap!ideTitle" ]    = "TRAP contains no leaving functions"

# localised string for Script nonconsthbufc
stringPool[ "nonconsthbufc!title" ]       = "Non-const HBufC* parameter passing"
stringPool[ "nonconsthbufc!description" ] = "HBufC* parameters should almost always be passed as a const pointer."
stringPool[ "nonconsthbufc!ideTitle" ]    = "non-const HBufC* parameter passing"

# localised string for Script nonconsttdesc
stringPool[ "nonconsttdesc!title" ]       = "Non-const TDesC& parameter passing"
stringPool[ "nonconsttdesc!description" ] = "TDesC& parameters should be passed as a const. If it is not, it may indicate that the coder does not understand descriptors, for example, passing descriptors by value."
stringPool[ "nonconsttdesc!ideTitle" ]    = "non-const TDesC& parameter passing"

# localised string for Script nonleavenew
stringPool[ "nonleavenew!title" ]       = "Use of new without (ELeave)"
stringPool[ "nonleavenew!description" ] = "Using new without (ELeave) is only used in special circumstances. The leaving variant should typically be used in preference. A common exception is for application creation, where NULL is returned for failed creation."
stringPool[ "nonleavenew!ideTitle" ]    = "new used without (ELeave)"

# localised string for Script nonunicodeskins
stringPool[ "nonunicodeskins!title" ]       = "Non-Unicode skins"
stringPool[ "nonunicodeskins!description" ] = "Skin definition files (SKN, SKE) must be Unicode. Note: Code that causes this issue only needs attention if it is found in code developed for Nokia Series 90 code."
stringPool[ "nonunicodeskins!ideTitle" ]    = "non-Unicode skins"

# localised string for Script null
stringPool[ "null!title" ]       = "NULL equality check"
stringPool[ "null!description" ] = "There is no need to compare pointer variables to NULL. Use If(ptr)."
stringPool[ "null!ideTitle" ]    = "NULL equality check"

# localised string for Script open
stringPool[ "open!title" ]       = "Ignoring Open() return value"
stringPool[ "open!description" ] = "Ignoring the return value from Open() functions (due to OOM, etc.) means that when the resource is accessed next, a panic will result."
stringPool[ "open!ideTitle" ]    = "ignoring Open() return value"

# localised string for Script pointertoarrays
stringPool[ "pointertoarrays!title" ]       = "Pointer to arrays as members of a C class"
stringPool[ "pointertoarrays!description" ] = "In C classes, there is no need to use pointers to arrays as data members. Instead, use the arrays themselves. Using pointers leads to obscure notation like \"(*array)[n]\" for the more usual \"array[n]\". It also makes it necessary to explicitly delete the arrays in the destructor. Using the arrays themselves also simplifies notation, reduces indirection, and reduces heap fragmentation."
stringPool[ "pointertoarrays!ideTitle" ]    = "pointer to arrays as members of a C class"

# localised string for Script pragmadisable
stringPool[ "pragmadisable!title" ]       = "Use of #pragma warning"
stringPool[ "pragmadisable!description" ] = "Disabling warnings can lead to problems, because the warnings are probably there for a reason."
stringPool[ "pragmadisable!ideTitle" ]    = "use of #pragma warning"

# localised string for Script pragmamessage
stringPool[ "pragmamessage!title" ]       = "Use of #pragma message"
stringPool[ "pragmamessage!description" ] = "#pragma messages during the build stage can interfere with the build log parsing."
stringPool[ "pragmamessage!ideTitle" ]    = "use of #pragma message"

# localised string for Script pragmaother
stringPool[ "pragmaother!title" ]       = "Use of #pragma other than warning and message"
stringPool[ "pragmaother!description" ] = "#pragma directives should only be used in very edge cases (for example, functions consisting of inline assembler without explicit return statements) because, typically, their usage masks valid build warnings and error messages."
stringPool[ "pragmaother!ideTitle" ]    = "use of #pragma other than warning and message"

# localised string for Script privateinheritance
stringPool[ "privateinheritance!title" ]       = "Use of private inheritance"
stringPool[ "privateinheritance!description" ] = "Classes should not be inherited privately. If public or protected inheritance is not appropriate, consider using an amalgamation; that is, have an object of that type as a member variable."
stringPool[ "privateinheritance!ideTitle" ]    = "use of private inheritance"

# localised string for Script pushaddrvar
stringPool[ "pushaddrvar!title" ]       = "Pushing address of a variable onto the cleanup stack"
stringPool[ "pushaddrvar!description" ] = "If the variable is owned by the code pushing it, it should be stored as a pointer. If it is not, it should not be pushed onto the cleanup stack."
stringPool[ "pushaddrvar!ideTitle" ]    = "pushing address of a variable onto the cleanup stack"

# localised string for Script pushmember
stringPool[ "pushmember!title" ]       = "Pushing data members onto the cleanup stack"
stringPool[ "pushmember!description" ] = "Pushing member variables is likely to lead to double deletes or leakage in certain circumstances and so should be avoided. Even if no panic can result, it is bad practice and makes maintenance more difficult."
stringPool[ "pushmember!ideTitle" ]    = "data member pushed to cleanup stack"

# localised string for Script readresource
stringPool[ "readresource!title" ]       = "Using ReadResource() instead of ReadResourceL()"
stringPool[ "readresource!description" ] = "ReadResourceL() should always be used in preference to ReadResource() because in an error scenario ReadResource() effectively fails silently. If no check is performed on the resulting descriptor afterwards, unexpected states can ensue. These states are often characterized by buffer overflows."
stringPool[ "readresource!ideTitle" ]    = "Using ReadResource() instead of ReadResourceL()"

# localised string for Script resourcenotoncleanupstack
stringPool[ "resourcenotoncleanupstack!title" ]       = "Neglected to put resource objects on cleanup stack"
stringPool[ "resourcenotoncleanupstack!description" ] = "If a stack-based resource object is not put on the cleanup stack with CleanupResetAndDestroyPushL() or CleanupClosePushL(), and a leaving function or ELeave is called, a memory leak occurs. CodeScanner occasionally gives false positives for this issue. Individual cases should be investigated."
stringPool[ "resourcenotoncleanupstack!ideTitle" ]    = "neglected to put resource objects on cleanup stack"

# localised string for Script resourcesonheap
stringPool[ "resourcesonheap!title" ]       = "Resource objects on the heap"
stringPool[ "resourcesonheap!description" ] = "There is very rarely any real need to put R classes on the heap (unless they are not real R classes!).  Doing so can lead to inefficiency and cleanup stack problems."
stringPool[ "resourcesonheap!ideTitle" ]    = "resource objects on the heap"

# localised string for Script returndescriptoroutofscope
stringPool[ "returndescriptoroutofscope!title" ]       = "Return descriptor out of scope"
stringPool[ "returndescriptoroutofscope!description" ] = "Returning a TBuf descriptor that is declared locally takes it out of scope. This can cause a crash on WINSCW, although not on WINS."
stringPool[ "returndescriptoroutofscope!ideTitle" ]    = "return descriptor out of scope"

# localised string for Script rfs
stringPool[ "rfs!title" ]       = "Use of non-pointer/reference RFs"
stringPool[ "rfs!description" ] = "Connecting to an RFs is a time-consuming operation. (It can take approximately 0.1 seconds on some devices.) To minimise wasted time and resources, use the already-connected one in EikonEnv or elsewhere, if possible."
stringPool[ "rfs!ideTitle" ]    = "use of non-pointer/reference RFs"

# localised string for Script rssnames
stringPool[ "rssnames!title" ]       = "Duplicate RSS names"
stringPool[ "rssnames!description" ] = "Resource files with clashing NAME fields can cause the wrong resource file to be accessed. This can lead to incorrect functionality or panics."
stringPool[ "rssnames!ideTitle" ]    = "duplicate RSS names"

# localised string for Script stringliterals
stringPool[ "stringliterals!title" ]       = "Use of _L string literals"
stringPool[ "stringliterals!description" ] = "_L() string literals should be replaced by the _LIT() macro."
stringPool[ "stringliterals!ideTitle" ]    = "use of _L string literals"

# localised string for Script stringsinresourcefiles
stringPool[ "stringsinresourcefiles!title" ]       = "Strings in RSS or RA files"
stringPool[ "stringsinresourcefiles!description" ] = "Strings should not be defined in RSS or RA files. Instead, they should be put in RLS or other localisable files."
stringPool[ "stringsinresourcefiles!ideTitle" ]    = "strings in RSS or RA files"

# localised string for Script struct
stringPool[ "struct!title" ]       = "Use of struct"
stringPool[ "struct!description" ] = "C-style structs should not generally be used. The correct idiom is to use a class with public members. A permissible use of a C-style struct is if it is used to group non-semantically related entities together for convenience, and if a class-related hierarchy would be too heavy-weight."
stringPool[ "struct!ideTitle" ]    = "use of struct"

# localised string for Script tcclasses
stringPool[ "tcclasses!title" ]       = "T classes inheriting from C classes"
stringPool[ "tcclasses!description" ] = "T classes that are derived from C classes may have a complex constructor and so need to be handled differently. It is better to make the T class into a C class, which will make the code easier to maintain."
stringPool[ "tcclasses!ideTitle" ]    = "T class inherits from C class"

# localised string for Script tclassdestructor
stringPool[ "tclassdestructor!title" ]       = "T class has destructor"
stringPool[ "tclassdestructor!description" ] = "T classes should not have a destructor"
stringPool[ "tclassdestructor!ideTitle" ]    = "T class has destructor"

# localised string for Script todocomments
stringPool[ "todocomments!title" ]       = "\"To do\" comments"
stringPool[ "todocomments!description" ] = "\"To do\" comments in code suggest that it is not finished."
stringPool[ "todocomments!ideTitle" ]    = "\"To do\" comment"

# localised string for Script trapcleanup
stringPool[ "trapcleanup!title" ]       = "Use of LC function in TRAPs"
stringPool[ "trapcleanup!description" ] = "You cannot trap something that leaves something on the cleanup stack because it will panic."
stringPool[ "trapcleanup!ideTitle" ]    = "LC function used in TRAP"

# localised string for Script trapeleave
stringPool[ "trapeleave!title" ]       = "Trapping new(ELeave)"
stringPool[ "trapeleave!description" ] = "The trapping of a \"new(ELeave) CXxx\" call is redundant and wasteful as the code to support TRAP is surprisingly large. If the instantiation process really needs not to leave, use \"new CXxx\" and check for NULL."
stringPool[ "trapeleave!ideTitle" ]    = "trapping new(ELeave)"

# localised string for Script traprunl
stringPool[ "traprunl!title" ]       = "Trapping of (Do)RunL() rather than using RunError()"
stringPool[ "traprunl!description" ] = "The RunError() function should be used rather than the CActive derivative using its own TRAPD solution within a RunL()."
stringPool[ "traprunl!ideTitle" ]    = "trapping of (Do)RunL() rather than using RunError()"

# localised string for Script trspassing
stringPool[ "trspassing!title" ]       = "Passing TRequestStatus parameters by value"
stringPool[ "trspassing!description" ] = "TRequestStatus parameters should be passed by reference. If TRequestStatus is just being used as an error code, then convert it to a TInt."
stringPool[ "trspassing!ideTitle" ]    = "passing TRequestStatus parameters by value"

# localised string for Script uids
stringPool[ "uids!title" ]       = "Duplicate UIDs"
stringPool[ "uids!description" ] = "UIDs must be unique."
stringPool[ "uids!ideTitle" ]    = "duplicate UIDs"

# localised string for Script uncompressedaif
stringPool[ "uncompressedaif!title" ]       = "Uncompressed AIFs in ROM"
stringPool[ "uncompressedaif!description" ] = "AIF files should be referenced as \"AIF=\" rather than \"data=\" or \"file=\" otherwise they can bloat the ROM size and slow down application loading."
stringPool[ "uncompressedaif!ideTitle" ]    = "uncompressed AIFs in ROM"

# localised string for Script uncompressedbmp
stringPool[ "uncompressedbmp!title" ]       = "Uncompressed bitmaps in ROM"
stringPool[ "uncompressedbmp!description" ] = "Using uncompressed bitmaps can significantly bloat the size of ROM images. All occurrences of \"bitmap=\" in iby/hby files should be replaced with \"auto-bitmap=\". Also, including bitmaps using \"data=\" or \"file=\" causes bloat and load-speed reductions."
stringPool[ "uncompressedbmp!ideTitle" ]    = "uncompressed bitmaps in ROM"

# localised string for Script unicodesource
stringPool[ "unicodesource!title" ]       = "Unicode source files"
stringPool[ "unicodesource!description" ] = "Having Unicode source files (CPP, H, RLS, LOC, RSS, and RA) will break most build systems."
stringPool[ "unicodesource!ideTitle" ]    = "Unicode source files"

# localised string for Script userafter
stringPool[ "userafter!title" ]       = "Use of User::After"
stringPool[ "userafter!description" ] = "Generally, User::After() functions are used to skirt around timing problems. Typically, they should be removed and the defects fixed properly: that is, by waiting for the correct event to continue execution."
stringPool[ "userafter!ideTitle" ]    = "use of User::After"

# localised string for Script userfree
stringPool[ "userfree!title" ]       = "Using User::Free directly"
stringPool[ "userfree!description" ] = "User::Free() should never be called, because all objects free their memory on deletion; their destructors are not called and further resources cannot be freed or closed. This function should be removed and replaced by explicit deletes."
stringPool[ "userfree!ideTitle" ]    = "using User::Free directly"

# localised string for Script userWaitForRequest
stringPool[ "userWaitForRequest!title" ]       = "Use of User::WaitForRequest"
stringPool[ "userWaitForRequest!description" ] = "User::WaitForRequest() should not generally be used in UI code because the UI will not respond to redraw events while its thread is stopped."
stringPool[ "userWaitForRequest!ideTitle" ]    = "use of User::WaitForRequest"

# localised string for Script variablenames
stringPool[ "variablenames!title" ]       = "Local variables with member/argument names"
stringPool[ "variablenames!description" ] = "Local variable names should be of the form localVariable and not aLocalVar or iLocalVar. Badly-named variables can be misleading and cause maintenance and coding errors."
stringPool[ "variablenames!ideTitle" ]    = "local variables with member/argument names"

# localised string for Script voidparameter
stringPool[ "voidparameter!title" ]       = "Void parameter explicitly declared"
stringPool[ "voidparameter!description" ] = "Declaring a void parameter is unnecessary. A function declared as DoSomething(void) may as well be declared as DoSomething(). Void casts are also unnecessary."
stringPool[ "voidparameter!ideTitle" ]    = "void parameter explicitly declared"

# localised string for Script worryingcomments
stringPool[ "worryingcomments!title" ]       = "Worrying comments"
stringPool[ "worryingcomments!description" ] = "Typically, exclamation and question marks in comments indicate that something odd is in the code or that it is unfinished or not understood fully."
stringPool[ "worryingcomments!ideTitle" ]    = "worrying comments"

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
# accessArrayElementWithoutCheck.py
#
# Checks : Array element accessed by At() function without checking 
# index is within array range.
#
# Reason : Whenever an element in an array is accessed, the index 
# should be checked to ensure that it is less than array.Count(). 
# CodeScanner checks for explicit calls to a Count() function; so 
# if the array index is checked in a different way, it gives 
# false positives. Accessing an invalid index can cause a panic.
#
# #################################################################

script = CScript("accessArrayElementWithoutCheck")
script.iReString = r"""
	(->|\.)		# pointer/instance of array
	\s*			# optional whitespace
	At
	\s*			# optional whitespace
	\(			# opening bracket
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

accessArrayCountFn = re.compile("""
	(\.|->)
	\s*
	Count
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

accessArrayDeclaration = re.compile("""
	\w+			# array type
	[0-9<>*& ]*	# optional array element
	\w+			# array name
	\s*
	\[
	.*			# array size
	\]
	\s*
	;
	""", re.VERBOSE)

def isTimerObject(lines, currentline, varname):
	if (varname.lower().find("array") <> -1) or (varname.lower().find("list") <> -1):
		return False
	if (varname.lower().find("heartbeat") <> -1):
		return True
	if (varname.lower().find("periodic") <> -1):
		return True
	if (varname.lower().find("timer") <> -1):
		return True

	vartype = GetLocalVariableType(lines, currentline, varname)
	if (len(vartype) > 0):
		if (vartype.lower().find("array") <> -1) or (vartype.lower().find("list") <> -1):
			return False
		if (vartype.lower().find("heartbeat") <> -1):
			return True
		if (vartype.lower().find("periodic") <> -1):
			return True
		if (vartype.lower().find("timer") <> -1):
			return True

	return False

def arrayAccessCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (line.count("At") == 1):
			openBracketPos = line.find("At")
		else:
			openBracketPos = line.find("At(")
		cutLine = line[openBracketPos+1:]
		closeBracketPos = cutLine.find(")") + len(line) - len(cutLine)
		if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
			variable = line[openBracketPos+3:closeBracketPos]
			variable = TrimVariableName(variable)

			if (len(variable) == 0):
				return 0

			# if a constant index assume it's going to be ok!
			if (variable[0] == "E") or (variable[0] == "K"):
				return 0

			variableIsNumeric = 1
			varPos = 0
			while (varPos < len(variable)):
				if (variable[varPos] < '0') or (variable[varPos] > '9'):
					variableIsNumeric = 0
					break
				varPos = varPos + 1

			linePos = openBracketPos - 1
			while (linePos > 0) and (isNonAlpha(line[linePos])):
				linePos = linePos - 1
			arrayNameEnd = linePos + 1
			while (linePos >= 0) and (isNonAlpha(line[linePos]) == 0):
				linePos = linePos - 1
			arrayNameStart = linePos + 1
		
			arrayName = ""
			if (arrayNameStart >= 0):
				arrayName = line[arrayNameStart:arrayNameEnd]
				arrayName = TrimVariableName(arrayName)

				if (len(arrayName) > 0):
					# if a constant array assume it's going to be ok!
					if (arrayName[0] == "E") or (arrayName[0] == "K"):
						return 0

					# ignore any heartbeat/periodic/timer object that is not an array or list
					if isTimerObject(lines, currentline, arrayName):
						return 0

			if (variableIsNumeric):
				if (len(arrayName) > 2):
					if (arrayName[0] == "i") and (arrayName[1] >= 'A') and (arrayName[1] <= 'Z'):
						return 0 

			i = currentline

			while (i >= 0) and (i >= scanner.iCurrentMethodStart):
				line = lines[i]

				# check to see if index is compared to array size
				if (len(arrayName) > 0):
					arrayNamePos = line.find(arrayName)
					if (arrayNamePos >= 0):
						cutLine = line[arrayNamePos + len(arrayName):]
						if (accessArrayCountFn.search(cutLine)):
							return 0

					if (variableIsNumeric == 1):
						if (accessArrayDeclaration.search(line)):
							openBracketPos = line.find("[")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									# if a constant index assume it's going to be ok!
									if (declVariable[0] == "E") or (declVariable[0] == "K"):
										return 0

								declVariableIsNumeric = 1
								varPos = 0
								while (varPos < len(declVariable)):
									if (declVariable[varPos] < '0') or (declVariable[varPos] > '9'):
										declVariableIsNumeric = 0
										break
									varPos = varPos + 1
								if (declVariableIsNumeric == 1):
									if (int(variable) < int(declVariable)):
										return 0

				i = i - 1
			return 1

	return 0

script.iCompare	= arrayAccessCompare
scanner.AddScript(script)

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
# accessArrayElementWithoutCheck2.py
#
# Checks : Array element accessed by [] without checking range.
#
# Reason : Whenever an element in an array is accessed, the index 
# should first be checked to ensure that it is within range. 
# CodeScanner checks for explicit calls to a Count() or Length() 
# function; so if the array index is checked in a different way, 
# it gives false positives. Accessing an invalid index can cause 
# a panic.
#
# #################################################################

script = CScript("accessArrayElementWithoutCheck2")
script.iReString = r"""
	\w+
	\s*		# optional whitespace
	\)*		# optional closing bracket
	\s*		# optional whitespace
	\[
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

accessArrayCountFn = re.compile("""
	(\.|->)
	\s*
	Count
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

accessArrayLengthFn = re.compile("""
	(\.|->)
	\s*
	Length
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

accessArrayDeclareNew = re.compile("""
	\s*
	=
	\s*
	new
	\s*
	""", re.VERBOSE)

bufferArrayDeclaration = re.compile("""
	\w+		# array type
	\s*
	<
	\s*
	[0-9]+
	\s*
	>
	\s*
	\w+		# array name
	\s*
	;
	""", re.VERBOSE)

accessArrayDeclaration = re.compile("""
	\w+		# array type
	\s*
	(\*|&)*
	\s*
	\[
	.*		# array size
	\]
	\s*
	;
	""", re.VERBOSE)

constArrayDeclaration = re.compile("""
	\w+		# array type
	[0-9<>*& ]*	# optional array element
	\s+
	\w+		# array name
	\s*
	\[
	.*		# array size
	\]
	\s*
	=
	[^=]
	""", re.VERBOSE)

def arrayAccessCompare2(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (accessArrayDeclareNew.search(line)):
			return 0

		if (accessArrayDeclaration.search(line)):
			return 0

		if (constArrayDeclaration.search(line)):
			return 0

		openBracketPos = line.find("[")
		cutLine = line[openBracketPos:]
		closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
		if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
			variable = line[openBracketPos:closeBracketPos]
			variable = TrimVariableName(variable)

			if (len(variable) == 0):
				return 0

			# if a constant index assume it's going to be ok!
			if (variable[0] == "E") or (variable[0] == "K"):
				return 0

			variableIsNumeric = 1
			varPos = 0
			while (varPos < len(variable)):
				if (variable[varPos] < '0') or (variable[varPos] > '9'):
					variableIsNumeric = 0
					break
				varPos = varPos + 1

			linePos = openBracketPos
			while (linePos > 0) and (isNonAlpha(line[linePos])):
				linePos = linePos - 1
			arrayNameEnd = linePos + 1
			while (linePos >= 0) and (isNonAlpha(line[linePos]) == 0):
				linePos = linePos - 1
			arrayNameStart = linePos + 1
		
			arrayName = ""
			if (arrayNameStart >= 0):
				arrayName = line[arrayNameStart:arrayNameEnd]
				arrayName = TrimVariableName(arrayName)

				if (len(arrayName) > 0):
					# if a constant array assume it's going to be ok!
					if (arrayName[0] == "E") or (arrayName[0] == "K"):
						return 0

			if (variableIsNumeric):
				if (len(arrayName) > 2):
					if (arrayName[0] == "i") and (arrayName[1] >= 'A') and (arrayName[1] <= 'Z'):
						return 0 

			i = currentline

			while (i >= 0) and (i >= scanner.iCurrentMethodStart):
				line = lines[i]
				
				# check to see if index is compared to array size
				if (len(arrayName) > 0):
					arrayNamePos = line.find(arrayName)
					if (arrayNamePos >= 0):
						cutLine = line[arrayNamePos + len(arrayName):]
						if (accessArrayCountFn.search(cutLine)):
							return 0
						if (accessArrayLengthFn.search(cutLine)):
							return 0

					if (variableIsNumeric == 1):
						doCheck = 0
						if (accessArrayDeclaration.search(line)):
							openBracketPos = line.find("[")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find("]") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									doCheck = 1

						if (bufferArrayDeclaration.search(line)):
							openBracketPos = line.find("<")
							cutLine = line[openBracketPos:]
							closeBracketPos = cutLine.find(">") + len(line) - len(cutLine)
							if (closeBracketPos > openBracketPos) and (openBracketPos >= 0):
								declVariable = line[openBracketPos:closeBracketPos]
								declVariable = TrimVariableName(declVariable)
								if (len(declVariable) > 0):
									doCheck = 1

						if (doCheck == 1):
							# if a constant index assume it's going to be ok!
							if (declVariable[0] == "E") or (declVariable[0] == "K"):
								return 0

							declVariableIsNumeric = 1
							varPos = 0
							while (varPos < len(declVariable)):
								if (declVariable[varPos] < '0') or (declVariable[varPos] > '9'):
									declVariableIsNumeric = 0
									break
								varPos = varPos + 1
							if (declVariableIsNumeric == 1):
								if (int(variable) < int(declVariable)):
									return 0

				i = i - 1
			return 1

	return 0

script.iCompare	= arrayAccessCompare2
scanner.AddScript(script)

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
# activestart.py
#
# Checks : Using CActiveScheduler::Start.
#
# Reason : Using CActiveScheduler::Start() can mean that something 
# asynchronous is being made synchronous. Instead, use active 
# objects correctly in an asynchronous way.
#
# #################################################################

script = CScript("activestart")
script.iReString = "CActiveScheduler::Start"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# activestop.py
#
# Checks : Using CActiveScheduler::Stop.
#
# Reason : Using CActiveScheduler::Stop() can mean that something 
# asynchronous is being made synchronous. Instead, use active 
# objects correctly in an asynchronous way.
#
# #################################################################

script = CScript("activestop")
script.iReString = "CActiveScheduler::Stop"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# arraypassing.py
#
# Checks : Passing arrays by value rather than reference.
#
# Reason : Passing arrays by value causes the array to be copied 
# needlessly, which takes up time and memory. For efficiency, 
# references should be used.
#
# #################################################################

script = CScript("arraypassing")
script.iReString = r"""
    (\(|,)?         # open bracket or preceeding comma
    \s*             # whitespace
	(R|C)\w*Array	# skip to a parameter type containing "R...Array..." or "C...Array..."
    \s*				# whitespace
	(<.*>)?			# optional class in angle brackets
	\s+				# whitespace
	(\w+)			# parameter name
    (=|\w|\s)*      # optional parameter initialization or whitespace
    (\)|,)			# close bracket or trailing comma
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium
script.iCompare = DefaultFuncParamCompare

scanner.AddScript(script)

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
# arrayptrcleanup.py
#
# Checks : Using local CArrayPtr classes without cleanup items.
#
# Reason : It is not enough to push a local CArrayPtr class onto 
# the cleanup stack. A TCleanupItem and callback function must be 
# used to avoid leaking the elements.
#
# #################################################################

script = CScript("arrayptrcleanup")
script.iReString = r"""
	\s+
	(
	\w+
	)
	\s*
	=
	\s*
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	\s*
	CArrayPtr
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def arrayptrcleanupcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		varName = m.group(1)
		if (len(varName) == 1) or (varName[0] not in "ai") or varName[1].islower():
			for i in range(currentline, currentline + 10):
				if i >= len(lines):
					break
				elif (lines[i].find("TCleanupItem") <> -1) and (lines[i].find(varName) <> -1):
					return 0
			return 1
	return 0

script.iCompare = arrayptrcleanupcompare
scanner.AddScript(script)

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
# assertdebuginvariant.py
#
# Checks : __ASSERT_DEBUG with User::Invariant.
#
# Reason : Replace __ASSERT_DEBUG(<condition>, User::Invariant()) 
# with ASSERT(<condition>), because it is easier to read.
#
# #################################################################

script = CScript("assertdebuginvariant")
	
script.iReString = "__ASSERT_DEBUG\s*\(\w*\s*,\s*User::Invariant\s*\(\s*\)\s*\)\s*;"
script.iFileExts = ["h", "cpp", ".inl", "c"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# baddefines.py
#
# Checks : Lowercase definition names.
#
# Reason : Badly-named definitions makes the code harder to 
# maintain and can lead to defects.
#
# #################################################################

script = CScript("baddefines")
script.iReString = r"""
	\#define
	\s+					# at least one whitespace char
	[A-Z0-9_]*[a-z]+	# find a lower case character
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# baseconstruct.py
#
# Checks : Leaving function called before BaseConstructL().
#
# Reason : If a leave occurs before BaseConstructL() is called, 
# the system can panic because it is trying to clean up an 
# application that has not been fully initialised.
#
# #################################################################

script = CScript("baseconstruct")
script.iReString = r"""
	^
	\s*
	BaseConstructL
	\s*
	\(
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def baseconstructcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if scanner.iCurrentMethodStart >= 0:
			for i in range(scanner.iCurrentMethodStart, currentline):
				line = lines[i]
				n = KReLeavingLine.search(line)
				if n:
					return 1
	return 0

script.iCompare = baseconstructcompare
scanner.AddScript(script)

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
# callActiveObjectWithoutCheckingOrStopping.py
#
# Checks : Active object called without checking whether it is 
# active or canceling it first.
#
# Reason : If an active object is started twice, a panic occurs. 
# CodeScanner picks out places where there is a call to a Start(), 
# Queue(), or After() function on a member variable, without a 
# previous call to IsActive(), Cancel(), or Stop(). In general, 
# if starting a timer, there should at least be a call to IsActive() 
# to ensure that the timer is not already running.
#
# #################################################################

script = CScript("callActiveObjectWithoutCheckingOrStopping")
script.iReString = r"""\("""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

activeObjectIsActive = re.compile("""
	(\.|->)
	\s*
	IsActive
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectCancel = re.compile("""
	(\.|->)
	\s*
	Cancel
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectStop = re.compile("""
	(\.|->)
	\s*
	Stop
	\s*
	\(
	\s*
	\)
	""", re.VERBOSE)

activeObjectCreate = re.compile("""
	=
	\s*
	\w+
	::
	New
	\w*
	\s*
	\(
	""", re.VERBOSE)

activeObjectCreate2 = re.compile("""
	=
	\s*
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	""", re.VERBOSE)

activeObjectStart = re.compile("""
	(\.|->)
	\s*
	Start
	\s*
	\(
	""", re.VERBOSE)

activeObjectQueue = re.compile("""
	(\.|->)
	\s*
	Queue
	\s*
	\(
	""", re.VERBOSE)

activeObjectAfter = re.compile("""
	(\.|->)
	\s*
	After
	\s*
	\(
	""", re.VERBOSE)

# RTimer::After() takes 2 arguments
rtimerObjectAfter = re.compile("""
	(\.|->)
	\s*
	After
	\s*
	\(
	\s*
	\w+			# first argument
	\s*
	,
	""", re.VERBOSE)

# Non-active types with After(), Queue() or Start() function
KNonActiveTypes = {
	"KAnimation"					: "Animation",
	"KAnimator"						: "Animator",
	"KClockSourcePeriodicUtility"	: "ClockSourcePeriodicUtility",
	"KCodecWrapper"					: "CodecWrapper",
	"KCommTimer"					: "CommTimer",
	"KEmbeddedStore"				: "EmbeddedStore",
	"KFormulaTextLexer"				: "FormulaTextLexer",
	"KObexServer"					: "ObexServer",
	"KSpriteAnimation"				: "SpriteAnimation",
	"KRConnection"					: "RConnection",
	"KRSubConnection"				: "RSubConnection",
	"KRTest"						: "RTest",
	"KRTimer"						: "RTimer",
	"KValidityPeriod"				: "ValidityPeriod",
	"KVideoPlayHwDevice"			: "VideoPlayHwDevice",
	"KVideoRecordHwDevice"			: "VideoRecordHwDevice",
}

def isNonActiveObject(variable):
	for name, value in KNonActiveTypes.items():
		if (variable.lower().find(value.lower()) <> -1):
			return True
	return False

def activeObjectCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (scanner.iCurrentMethodName == "Start"):
			return 0
		if (scanner.iCurrentMethodName == "Queue"):
			return 0
		if (scanner.iCurrentMethodName == "After"):
			return 0

		checkForIsActive = 0	
		if (activeObjectStart.search(line)):
			checkForIsActive = 1
		if (activeObjectQueue.search(line)):
			checkForIsActive = 1
		if (activeObjectAfter.search(line)):
			# make sure we are not dealing with RTimer::After()
			if (not rtimerObjectAfter.search(line)):
				checkForIsActive = 1
		if (checkForIsActive == 1):
			varEnd = line.find("->")
			if (varEnd < 0):
				varEnd = line.find(".")
			if (varEnd < 0):
				return 0
			
			variable = TrimVariableName(line[:varEnd])
			if (len(variable) == 0):
				return 0

			# if a local variable then unlikely to have been started already
			if (len(variable) > 2):
				if (variable[0] != 'i'):
					return 0
				else:
					if (variable[1] < 'A') or (variable[1] > 'Z'):
						return 0

			# ignore non-active object
			if isNonActiveObject(variable):
				return 0

			i = currentline
			while (i > scanner.iCurrentMethodStart):
				line = lines[i]
				varPos = line.find(variable)
				if (varPos >= 0):
					cutLine = line[varPos:]
					if (activeObjectIsActive.search(cutLine)):
						return 0
					if (activeObjectCancel.search(cutLine)):
						return 0
					if (activeObjectStop.search(cutLine)):
						return 0
					if (activeObjectCreate.search(cutLine)):
						return 0
					if (activeObjectCreate2.search(cutLine)):
						return 0
				i = i - 1
			return 1

	return 0

script.iCompare	= activeObjectCompare
scanner.AddScript(script)

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
# changenotification.py
#
# Checks : Using RSAVarChangeNotify to see System Agent changes.
#
# Reason : When watching for System Agent changes, use RSystemAgent 
# rather than RSAVarChangeNotify, which can fail.
#
# #################################################################

script = CScript("changenotification")
script.iReString = "RSAVarChangeNotify"
script.iFileExts = ["cpp", "h", "inl", "hpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# cleanup.py
#
# Checks : CleanupStack::Pop(AndDestroy) parameters.
#
# Reason : These functions should be called with explicit variable 
# parameters to avoid misalignment.
#
# #################################################################

script = CScript("cleanup")
script.iReString = r"""
	CleanupStack::Pop(AndDestroy)?
	\s*
	\(
	\s*
	([0-9]+\s*\)|\))
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# commentcode.py
#
# Checks : Commented-out code.
#
# Reason : Instances of code that are commented out make the code 
# hard to maintain and to interpret clearly. The commented out code 
# should be removed. Any requirement to rediscover old code 
# should be made through source control and not by trawling through 
# commented-out code.
#
# #################################################################

script = CScript("commentcode")
script.iReString = r"""
	/(/|\*)			# "//" or "/*"
	(.*);			# skip to semicolon
	\s*				# optional whitespace
	(//.*)?			# optional comment
	$				# end of line
	"""
script.iFileExts = ["h","cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreQuotes
script.iSeverity = KSeverityLow

reDeclaration = re.compile("""
	\s*
	[A-Z][\w<>*&]+
	\s+
	\w+
	\s*
	""", re.VERBOSE)

def commentcodecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if ((m.group(2)[-1:] == ")") or (m.group(2).find("=") <> -1)) or (reDeclaration.match(m.group(2))):
			line = lines[currentline]
			i = 0
			inCommentBlock = 0

			while i < len(line):
				if not inCommentBlock:
					if (line[i] == "/"):
						if (line[i + 1] == "/"):
							return 1
						elif (line[i + 1] == "*"):
							inCommentBlock = 1
							i += 2
							continue
				else:
					endIndex = line[i:].find("*/")
					if (endIndex <> -1):
						inCommentBlock = 0
						if line[i:i + endIndex + 2].find(";") <> -1:
							return 1
						i += endIndex + 2
						continue
					else:
						return 1
				
				i += 1
		
	return 0

script.iCompare = commentcodecompare
scanner.AddScript(script)


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
# CommonFunctions.py
#
# Some commonly used functions.
#
# #################################################################

KReStringLeavingLine = "(\w*[a-z]\w*L(C*|D|P))\s*\(|ELeave|User::Leave|tream\s+<<|tream\s+>>"

KReLeavingLine = re.compile(KReStringLeavingLine, re.VERBOSE)

def isNonAlpha(char):
	if (char >= 'A'):
		if (char <= 'Z'):
			return 0
	if (char >= 'a'):
		if (char <= 'z'):
			return 0
	if (char >= '0'):
		if (char <= '9'):
			return 0
	return 1

def TrimVariableName(var):
	while (len(var) > 0) and (isNonAlpha(var[0])):
		var = var[1:len(var)]
	while (len(var) > 0) and (isNonAlpha(var[len(var)-1])):
		var = var[0:len(var)-1]

	if (len(var) > 0):
		spaceIndex = var.find(" ")
		if (spaceIndex <> -1):
			cutVar = var[spaceIndex:]
			return TrimVariableName(cutVar)
	return var

def GetBracketDepth(lines, currentline):
	i = scanner.iCurrentMethodStart
	bracketdepth = 0
	while (i < currentline):
		thisline = lines[i]
		commentBegin = thisline.find("//")
		if (commentBegin != -1):
			thisline = thisline[:commentBegin]
		bracketdepth += thisline.count("{")
		bracketdepth -= thisline.count("}")
		i = i + 1

	return bracketdepth	

varDeclaration = re.compile("""
	\s*					# whitespace
	([A-Z]\w*)			# variable type
	\s*             	# whitespace
	(<.*>)?				# optional class in angle brackets
	\s*[\*&\s]\s*		# optional "*" or "&" plus at least one whitespace char
	(\w+)				# variable name
	\s*             	# whitespace
	[;\(=]				# ";" or "(" or "="
	""", re.VERBOSE)

def GetLocalVariableType(lines, currentline, varname):
	# skip non-local object
	if (len(varname) > 2):
		if (varname[0] == 'i'):
			return ""

	# lookup type of local variable or function parameter
	if (scanner.iCurrentMethodStart <> -1):
		i = scanner.iCurrentMethodStart
		while (i < currentline):
			line = lines[i]
			if (line.find(varname) <> -1):
				# look up variable declaration
				m = varDeclaration.search(line)
				if m:
					# return variable type
					return m.group(1)
			i = i + 1
	return ""

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
# connect.py
#
# Checks : Ignoring Connect() return value.
#
# Reason : Ignoring the error returned from Connect() functions 
# means that if the Connect() function fails due to OOM or 
# other problems, the next access to the resource will panic.
#
# #################################################################

script = CScript("connect")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	\w+					# variable name
	(\.|->)				# "." or "->"
	Connect\s*\(\s*\)
	\s*;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

scanner.AddScript(script)




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
# ConnectAndDontCloseMemberVariable.py
#
# Checks : Calling Connect() or Open() on a member variable without 
# calling Close() in the destructor.
#
# Reason : If Connect() or Open() is called on any member variable, 
# then Close() must be called in the destructor.
#
# #################################################################

script = CScript("ConnectAndDontCloseMemberVariable")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	i[A-Z]\w+			# member variable name
	(\.|->)				# "." or "->"
	(Connect|Open)
	\s*\(\s*\)
	\s*;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

ConnectAndDontCloseLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D|P)*
	\s*
	\(
	""", re.VERBOSE)

def ConnectNotCloseCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		# get the variable name, between the '*' and the '='
		startindex = line.find("i")
		if (startindex == -1):
			startindex = 0
		endindex = line.find("Connect")
		if (endindex == -1):
			endindex = line.find("Open")
		variable = line[startindex:endindex]
		if (len(variable) < 1):
			return 0
		variable = TrimVariableName(variable)

		# see if variable is closed within this function before a Leave
		i = currentline
		bracketdepth = GetBracketDepth(lines, i)
		while (i < len(lines)) and (bracketdepth  > 0):
			line = lines[i]
			if (line.find(variable) >= 0):
				if (line.find("Close") >= 0):
					return 0

			bracketdepth += line.count("{")
			bracketdepth -= line.count("}")

			if (line.find("User::Leave") >= 0):
				bracketdepth = 0
			if (line.find("ELeave") >= 0):
				bracketdepth = 0
			if (ConnectAndDontCloseLeavingFunction.search(line)):
				bracketdepth = 0
				
			i = i + 1
		
		# look for destructor and see if variable is closed there
		stringToFind = "~" + scanner.iCurrentClassName
		i = 1
		foundDestructor = 0
		bracketdepth = 0
		while (i < len(lines)):
			thisLine = lines[i]
			if (thisLine.find(stringToFind) >= 0) and (foundDestructor == 0):
				while (i < len(lines)) and (foundDestructor == 0):
					thisLine = lines[i]
					if (thisLine.find('{') >= 0):
						foundDestructor = 1
					else:
						i = i + 1

			if (foundDestructor):
				bracketdepth += thisLine.count("{")
				bracketdepth -= thisLine.count("}")
				if (bracketdepth == 0):
					return 1
				
				if (thisLine.find(variable) >= 0):
					if (thisLine.find("Close") >= 0):
						return 0
			i = i + 1

		if (foundDestructor):
			return 1
	return 0

script.iCompare	= ConnectNotCloseCompare
scanner.AddScript(script)

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
# constnames.py
#
# Checks : Badly-named constants.
#
# Reason : Badly-named constant will make the source code harder to 
# maintain and make defects more likely.
#
# #################################################################

script = CScript("constnames")
script.iReString = r"""
	^
	\s*
	const
	\s+
	\w+		# type
	\s*
	[\*&]?	# reference or pointer
	\s*
	[^K\s]	# name initial letter
	\w+		# name
	\s*
	=
	[^()]*
	;
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def constnamescompare(lines, currentline, rematch, filename):
	if (scanner.iCurrentMethodName == ""):
		if rematch.search(lines[currentline]):
			return 1

	return 0

script.iCompare = constnamescompare
scanner.AddScript(script)

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
# consttdescptr.py
#
# Checks : Const descriptor pointer as argument.
#
# Reason : Use "const TDesC&" instead of "const TDesC*".
#
# #################################################################

script = CScript("consttdescptr")
script.iReString = r"""
    (\(|,)?        # open bracket or preceeding comma
    \s*            # whitespace
	const
    \s+            # whitespace
	TDesC
    \s*            # whitespace
	\*
    \s*            # whitespace
    (=|\w|\s)*     # optional parameter name, parameter initialization or whitespace
    (\)|,)         # close bracket or trailing comma
	"""
script.iFileExts = ["h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# controlornull.py
#
# Checks : Accessing return value of ControlOrNull().
#
# Reason : The return value might be NULL, so it should be checked 
# before access.
#
# #################################################################

script = CScript("controlornull")
script.iReString = "(\.|->)ControlOrNull\(.*\)->"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

scanner.AddScript(script)

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
# ctltargettype.py
#
# Checks : Use of targettype ctl.
#
# Reason : The ctl target type should not be used. Instead, use DLL 
# and explicitly refer to the Control Panel's DEF file. 
# Note: Code that causes this issue only needs attention if it is 
# found in code developed for Nokia Series 90 code that has extra 
# exports for resetting the Control Panel item's data.
#
# #################################################################

script = CScript("ctltargettype")
script.iReString = r"""
	^\s*
	[Tt][Aa][Rr][Gg][Ee][Tt][Tt][Yy][Pp][Ee]
	\s+
	"""
script.iFileExts = ["mmp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

reTargetPath = re.compile("""
	^\s*
	[Tt][Aa][Rr][Gg][Ee][Tt][Pp][Aa][Tt][Hh]
	\s+
	""", re.VERBOSE)

reDefFile = re.compile("""
	^\s*
	[Dd][Ee][Ff][Ff][Ii][Ll][Ee]
	""", re.VERBOSE)
	
def ctltargettypecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if lines[currentline].upper().find("CTL") <> -1:
			return 1

		if lines[currentline].upper().find("DLL") <> -1:
			foundDefFile = 0
			foundSystemControls = 0

			for line in lines:
				if reTargetPath.search(line):
					if line.upper().find("SYSTEM\\CONTROLS") <> -1:
						foundSystemControls = 1

				if reDefFile.search(line):
					if line.upper().find("CTRL.DEF") <> -1:
						foundDefFile = 1

				if (foundSystemControls == 1) and (foundDefFile == 1):
					break
		
			if (foundSystemControls == 1) and (foundDefFile <> 1):
				return 1
			
	return 0

script.iCompare	= ctltargettypecompare
scanner.AddScript(script)

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
# debugrom.py
#
# Checks : Debug components in ROM.
#
# Reason : Debug versions of components in the ROM could mean that 
# ROM space is being taken up with debugging information or that 
# logging is being put out. Release versions should be in the ROM 
# unless there is a good reason why they are not.
#
# #################################################################

script = CScript("debugrom")
script.iReString = "DEBUG_DIR|\\udeb\\\\"
script.iFileExts = ["iby", "hby"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# declarename.py
#
# Checks : Use of __DECLARE_NAME.
#
# Reason : The __DECLARE_NAME macro is historical and serves 
# no purpose anymore and should be removed.
#
# #################################################################

script = CScript("declarename")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	__DECLARE_NAME
	\s*					# optional whitespace
	\(					# open bracket
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# deleteMemberVariable.py
#
# Checks : Member variable deleted incorrectly.
#
# Reason : When a member variable is deleted, it should be assigned 
# either to NULL or to another value. This prevents accidental 
# access of the deleted object. If a NewL() or other leaving 
# function is called to reassign the member variable, it should 
# first be assigned to NULL in case that function leaves.
#
# #################################################################

script = CScript("deleteMemberVariable")
script.iReString = r"""
	delete		# delete command
	\s*			# optional space
	\(*			# optional open bracket
	\s*			# optional space
	i[A-Z]		# member variable name
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

deleteMemberVariableLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D)*
	\s*
	\(
	""", re.VERBOSE)

deleteMemberVariableNewELeave = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
	""", re.VERBOSE)

deleteMemberVariableLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

deleteMemberVariableArrayDeletion = re.compile("""
	(\.|->)
	\s*
	Delete
	\s*
	\(
	""", re.VERBOSE)

deleteMemberVariableArrayDeletion2 = re.compile("""
	(\.|->)
	\s*
	Remove
	\s*
	\(
	""", re.VERBOSE)

def deleteMemberVariableCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		if (scanner.iCurrentMethodName.find(scanner.iCurrentClassName) > -1):
			return 0

		deletingArrayMember = 0
		if (line.find("[")):
			deletingArrayMember = 1

		# get the variable name, between the 'delete' and the ';'
		endindex = line.find(";")
		if (endindex == -1):
			endindex = len(line)
		startindex = line.find("delete")
		variable = line[startindex+6:endindex]
		variable2 = TrimVariableName(variable)

		bracketdepth = GetBracketDepth(lines, currentline)

		i = currentline
		while (i < len(lines)):
			nextLine = lines[i]

			if deleteMemberVariableLeavingFunction.search(nextLine):
				return 1
			if deleteMemberVariableLeave.search(nextLine):
				return 1
			if deleteMemberVariableNewELeave.search(nextLine):
				return 1
			
			if (deletingArrayMember == 1):
				if (nextLine.find(variable2)):
					if deleteMemberVariableArrayDeletion.search(nextLine):
						return 0
					if deleteMemberVariableArrayDeletion2.search(nextLine):
						return 0

			foundAssignment = nextLine.find("=")
			if (foundAssignment > -1 and nextLine[foundAssignment+1] != "="):
				assigned = nextLine[:foundAssignment]
				if (assigned.find(variable2)):
					return 0

			if (nextLine.find('{') >= 0):
				bracketdepth = bracketdepth + 1
			if (nextLine.find('}') >= 0):
				bracketdepth = bracketdepth - 1
				if (bracketdepth == 0):
					return 1

			i = i + 1
	return 0

script.iCompare	= deleteMemberVariableCompare
scanner.AddScript(script)

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
# destructor.py
#
# Checks : Pointer access in destructors.
# 
# Reason : Accessing pointers to objects in destructors without 
# checking whether they are not NULL could result in a panic, since
# they may not have been constructed. The pointers should be
# checked to determine whether they are owned objects. If they are
# not owned, they should really be references rather than pointers.
#
# #################################################################

script = CScript("destructor")
script.iReString = r"""
	^\s*
	\w+
	\s*
	::~
	\s*
	\w+
	\(
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

remember = re.compile("(i[A-Z]\w*)(.+)")
reguard = re.compile("^\s*(if|while)(.*)({|$)")

def findguard(lines, currentline, destructorstartline, membername):
	i = currentline
	line = lines[i]

	while (i > destructorstartline):
		line = lines[i]
		m = reguard.search(line)
		if m:
			index = m.group(2).find(membername)
			if (index <> -1):
				if (line[index - 1:index] <> "*") and (line[index + len(membername):index + len(membername) + 2] <> "->"):
					return 1
		i = i - 1

	return 0

def destructorcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		openbracecount = 0
		closebracecount = 0
		checkline = currentline

		while (checkline < len(lines)):
			line = lines[checkline]
			openbracecount += line.count("{")
			closebracecount += line.count("}")
			member = remember.search(line)
			if member and ((member.group(2)[:2] == "->") or (line[member.start()-1:member.start()] == "*" and member.group(2)[:1] <> ".")):
				membername = member.group(1)
				if (membername.upper()[-3:] == "ENV") or findguard(lines, checkline, currentline, membername) <> 0:
					return 0
				else:
					return 1

			if (openbracecount and (openbracecount - closebracecount == 0)):
				break
			checkline += 1

	return 0

script.iCompare	= destructorcompare
scanner.AddScript(script)

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
# doubleSemiColon.py
#
# Checks : Use of double semicolon.
#
# Reason : Double semicolons at the end of a line are not necessary 
# and cause a CodeWarrior compiler error.
#
# #################################################################

script = CScript("doubleSemiColon")
script.iReString = r"""
	;
	\s*
	;
	\s*
	$
	"""
script.iFileExts = ["cpp", "h", "inl"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# driveletters.py
#
# Checks : Hard-coded drive letters.
#
# Reason : Drive letters should not be hard-coded.
#
# #################################################################

script = CScript("driveletters")
script.iReString = r"""[a-zA-Z]:\\\\"""
script.iFileExts = ["cpp", "h", "rss", "rls", "loc", "ra"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreComments
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# eikbuttons.py
#
# Checks : Checks that the R_EIK_BUTTONS_* resources are not being 
# used.
#
# Reason : R_EIK_BUTTONS_* resources will not be internationalised, 
# and should not be used. Instead, create your own button resource. 
# No button resource (or indeed, rls string) should be used in 
# more than one location. Note: This issue is only relevant for 
# development on Nokia platforms.
#
# #################################################################

script = CScript("eikbuttons")
script.iReString = "R_EIK_BUTTONS_.*?"
script.iFileExts = ["rss", "cpp"]
script.iCategory = KCategoryLocalisation
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# eikonenvstatic.py
#
# Checks : Using CEikonEnv::Static.
#
# Reason : CEikonEnv::Static() calls should be kept to a minimum, 
# because this involves TLS. All applications, controls, and 
# dialogs already have a pointer to the singleton instance of 
# CEikonEnv as a member variable and so don't need to find it again. 
# If a class does not have access to a CEikonEnv and needs to use 
# it repeatedly, then it should store one.
#
# #################################################################

script = CScript("eikonenvstatic")
script.iReString = "CEikonEnv::Static"

script.iFileExts = ["cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# enummembers.py
#
# Checks : Badly-named enum members.
#
# Reason : Badly-named enum members make the code harder to 
# maintain and may cause defects.
#
# #################################################################

script = CScript("enummembers")
script.iReString = r"""
			^
			\s*
			enum
			((\s+\w+)|(\s+\w+\s*::\s*\w+))?
			\s*
			({|$)
			"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reMember = re.compile("^\s*(\w+)")

def enummemberscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		startline = currentline
		openbraceindex = lines[startline].find("{")
		while (openbraceindex == -1) and (startline < len(lines)) and (lines[startline].find(";") == -1):
			startline += 1
			openbraceindex = lines[startline].find("{")

		if openbraceindex == -1:
			return 0

		endline = currentline
		closebraceindex = lines[endline].find("}")
		while (closebraceindex == -1) and (endline < len(lines)):
			endline += 1
			closebraceindex = lines[endline].find("}")

		enumcontents = ""
		if (startline == endline):
			enumcontents = lines[startline][openbraceindex + 1:closebraceindex - 1]
		else:
			enumcontents = lines[startline][openbraceindex + 1:]
			line = startline + 1
			while (line < len(lines)) and (line < endline):
				enumcontents = enumcontents + lines[line]
				line += 1

			enumcontents = enumcontents + lines[endline][:closebraceindex - 1]

		# check contents
		members = enumcontents.split("\n\r,")
		for member in members:
			m2 = reMember.search(member)
			if m2 and (m2.group(1)[:1] <> "E"):
				return 1
									
	return 0

script.iCompare = enummemberscompare
scanner.AddScript(script)

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
# enumnames.py
#
# Checks : Badly-named enums.
#
# Reason : Badly-named enums make the code harder to maintain and 
# may cause defects.
#
# #################################################################

script = CScript("enumnames")
script.iReString = r"""
			^
			\s*
			enum
			\s+
			(\w+\s*::\s*)?
			(\w+)
			\s*
			({|$)
			"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def enumnamescompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if m.group(2)[:1] <> "T":
				return 1

	return 0

script.iCompare = enumnamescompare
scanner.AddScript(script)

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
# exportinline.py
#
# Checks : Exporting inline functions.
#
# Reason : Inline functions should not be exported because this can 
# cause those that link to the DLL to fail to build. Exporting 
# functions limits the changes that can be made in the future 
# due to considerations of binary-compatibility.
#
# #################################################################

script = CScript("exportinline")
script.iReString = "IMPORT_C\s+.*inline\s+.+\("
script.iFileExts = ["cpp", "h", "hpp", "inl", "c"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# exportpurevirtual.py
#
# Checks : Exporting pure virtual functions.
#
# Reason : Symbian recommends against the exportation of 
# pure virtual functions.
#
# #################################################################

script = CScript("exportpurevirtual")
script.iReString = "IMPORT_C\s+.*\)\s*=\s*0\s*;$"
script.iFileExts = ["cpp", "h", "hpp", "inl", "c"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)



# This script is duplicate of driveletters.py

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
# externaldriveletters.py
#
# Checks : Hard-coded external drive letters.
#
# Reason : External drive letters should not be hard-coded as the 
# external drive may change between platforms and releases. 
# This may cause confusion over ownership leading to classes being 
# deleted erroneously and leaks occurring.
#
# #################################################################

#script = CScript("externaldriveletters")
#script.iReString = """"[abd-yABD-Y]:\\\\"""
#script.iFileExts = ["cpp", "h", "rss", "rls", "loc", "ra"]
#script.iCategory = KCategoryCanPanic
#script.iIgnore = KIgnoreComments
#script.iSeverity = KSeverityHigh

#scanner.AddScript(script)

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
# flags.py
#
# Checks : Use of R&D flags or feature flags.
#
# Reason : Independent application must not use R&D flags nor 
# feature flags via preprocessor statements in the source code.
# This means bld*.hrh and productvariant.hrh should not be used.
#
# #################################################################

script = CScript("flags")
script.iReString = r"""
    ^\s*
    \#include
    \s+
    ("|<)
    ((bld\w+|productvariant)\.hrh)
    ("|>)
    """
script.iFileExts = ["cpp", "h", "hrh", "mmp"]
script.iCategory = KCategoryOther
script.iIgnore = KIgnoreComments
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# foff.py
#
# Checks : Use of _FOFF.
#
# Reason : _FOFF allows access to data in classes that were not 
# intended for public access. This may cause problems, especially 
# when the location of the data changes.
#
# #################################################################

script = CScript("foff")
script.iReString = "_FOFF"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# forbiddenwords.py
#
# Checks : Use of forbidden words in header files.
#
# Reason : Some words should not be used in header files; 
# especially those header files destined for external release. 
# Some words may be forbidden for legal reasons or for platform 
# consistency. Where they exist, alternative allowed words should 
# be used. For example, \"NMP\" and \"Nokia Mobile Phones\" should 
# be replaced by \"Nokia\".
#
# #################################################################

script = CScript("forbiddenwords")
script.iReString = ""
script.iFileExts = ["h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreNothing
script.iSeverity = KSeverityLow

reForbiddenWordsStr = "(Typhoon|Hurricane|Calypso|Rubik|Epoc\\|Nokia Mobile Phones|NMP|Mobile Innovation|(^|\s)S90|(^|\s)S80)"

scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("wordsRE"):
		reForbiddenWordsStr = wordNode.firstChild.nodeValue
		print "Note: 'forbidden words' pattern configured as: " + reForbiddenWordsStr
		break
reForbiddenWords = re.compile(reForbiddenWordsStr, re.IGNORECASE)

def forbiddenwordcompare(lines, currentline, rematch, filename):
	return reForbiddenWords.search(lines[currentline])

script.iCompare = forbiddenwordcompare
scanner.AddScript(script)

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
# forgottoputptroncleanupstack.py
#
# Checks : Neglected to put variable on cleanup stack.
#
# Reason : If a variable is not put on the cleanup stack and a 
# leaving function or ELeave is called, a memory leak occurs. 
# CodeScanner occasionally gives false positives for this issue. 
# Individual cases should be investigated.
#
# #################################################################

script = CScript("forgottoputptroncleanupstack")
script.iReString = r"""
	\s+				# optional whitespace
	[b-hj-z]+		# must not be a member or parameter
	[A-Za-z0-9]+	# variable name
	\s*				# optional whitespace
	=				# assignment operator
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

forgottoputptroncleanupstackCleanup = re.compile("""Cleanup""", re.VERBOSE)

forgottoputptroncleanupstackDeleteOp = re.compile("""
	\s+
	delete
	\s+
	""", re.VERBOSE)

forgottoputptroncleanupstackReturnCmd = re.compile("""
	(\s*|\()
	return
	(\s*|\()
	""", re.VERBOSE)

forgottoputptroncleanupstackSetFn = re.compile("""
	Set
	[A-Za-z0-9]+
	[A-KM-Za-z0-9]
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackBreak = re.compile("""
	\s+
	break
	\s*
	;
	""", re.VERBOSE)

forgottoputptroncleanupstackIf = re.compile("""
	\s+
	if
	\s*
	\(
	""", re.VERBOSE)
	
forgottoputptroncleanupstackElse = re.compile("""
	\}*
	\s*
	else
	\s*
	\{*
	""", re.VERBOSE)

forgottoputptroncleanupstackAssignToMember = re.compile("""
	i
	[A-Za-z0-9\[\]]+
	\s*
	=
	\s*
	.*
	\s*
	;
	""", re.VERBOSE)

forgottoputptroncleanupstackTrapMacro = re.compile("""
	TRAP
	[D]*
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackLeavingFunction = re.compile("""
	[A-Za-z0-9]+
	L
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

forgottoputptroncleanupstackLeaveAndDelete = re.compile("""
	L
	[D]+
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackNewOperator = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	""", re.VERBOSE)

forgottoputptroncleanupstackNewFunction = re.compile("""
	::NewL
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackCreateFunction = re.compile("""
	Create
	[A-Za-z0-9]+
	L
	\s*
	\(
	""", re.VERBOSE)

forgottoputptroncleanupstackAllocFunction = re.compile("""
	Alloc
	L*
	\s*
	\(
	""", re.VERBOSE)

def findForgetCompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		foundNew = 0
		equalPos = line.find("=")
		assignedSection = line[equalPos:]
	
		if forgottoputptroncleanupstackNewFunction.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackNewOperator.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackAllocFunction.search(assignedSection):
			foundNew = 1
		if forgottoputptroncleanupstackCreateFunction.search(assignedSection):
			foundNew = 1

		# if this line contains a 'new', a 'NewL(', or an 'AllocL('
		if (foundNew == 1):	
			i = currentline

		# move to next line ending if this line doesn't contain one
			while (lines[i].find(';') == -1):
				i = i + 1

		# go to next line
			i = i + 1
			bracketdepth = GetBracketDepth(lines, i)
			
		# get the variable name, between the '*' and the '='
			startindex = line.find("*")
			if (startindex == -1):
				startindex = 0
			endindex = line.find("=")
			variable = line[startindex+1:endindex]
			if (len(variable) < 1):
				return 0
			variable = TrimVariableName(variable)

			inAnIfOrSelectStatement = 1 # possibly
			
			while (i < len(lines)):
				line2 = lines[i]

				if (line2.find('{') >= 0):
					bracketdepth = bracketdepth + 1
				if (line2.find('}') >= 0):
					bracketdepth = bracketdepth - 1
					inAnIfOrSelectStatement = 0
					if (bracketdepth == 0):
						return 0

				varIndex = line2.find(variable)
		# if a later line contains the variable...
				while (varIndex <> -1):
					if (isNonAlpha(line2[varIndex-1])):
						if (isNonAlpha(line2[varIndex+len(variable)])):
		# ...and delete, exit
							if forgottoputptroncleanupstackDeleteOp.search(line2):
								return 0
	
		# ...and an xxxLD() function, exit
							if forgottoputptroncleanupstackLeaveAndDelete.search(line2):
								return 0
							
		# ...and the variable is assigned to a member variable, exit
							if forgottoputptroncleanupstackAssignToMember.search(line2):
								return 0
		
		# ...and it is a Set...() call, exit (e.g. SetArray, SetAppUi)
							if forgottoputptroncleanupstackSetFn.search(line2):
								return 0

		# ...and a return command, exit 
							if forgottoputptroncleanupstackReturnCmd.search(line2):
								return 0

		# search this line again incase there are similarly named variables
					line2 = line2[varIndex+1:]
					varIndex = line2.find(variable)

				line2 = lines[i]
		# if a leaving function is called...
				if forgottoputptroncleanupstackLeavingFunction.search(line2):
		# ...if the leaving function is trapped, exit
					if forgottoputptroncleanupstackTrapMacro.search(line2):
						return 0
		# ...if a Cleanup function is called, exit
					if forgottoputptroncleanupstackCleanup.search(line2):
						return 0
		# ...otherwise this is a problem!
					return 1

		# if a User::Leave is called, this is a problem
				if forgottoputptroncleanupstackLeave.search(line2):
					return 1
	
		# if the variable is initialised in a branch of an 'if' or 'switch' statement, ignore other branches
				if (inAnIfOrSelectStatement == 1):
					if forgottoputptroncleanupstackBreak.search(line2):
						atLine = i
						inAnIfOrSelectStatement = 0
						findSwitch = i
						line3 = lines[findSwitch]
						while (line3.find("switch") == -1):
							findSwitch = findSwitch - 1
							if (findSwitch <= 0):
								return 0
							line3 = lines[findSwitch]
						switchBracketDepth = GetBracketDepth(lines, findSwitch)
						i = atLine
						while (bracketdepth > switchBracketDepth):
							if (i >= len(lines)):
								return 0
							line2 = lines[i]
							if (line2.find('{') >= 0):
								bracketdepth = bracketdepth + 1
							if (line2.find('}') >= 0):
								bracketdepth = bracketdepth - 1
							i = i + 1
							
					if forgottoputptroncleanupstackElse.search(line2):
						inAnIfOrSelectStatement = 0
						elseBracketDepth = bracketdepth
						if (line2.find('{') >= 0):
							elseBracketDepth = elseBracketDepth - 1
						if (elseBracketDepth == GetBracketDepth(lines, currentline)):
							while (line2.find(';') == -1):
								i = i + 1
								if (i >= len(lines)):
									return 0
								line2 = lines[i]
						else:
							while (bracketdepth > elseBracketDepth):
								i = i + 1
								if (i >= len(lines)):
									return 0
								line2 = lines[i]
								if (line2.find('{') >= 0):
									bracketdepth = bracketdepth + 1
								if (line2.find('}') >= 0):
									bracketdepth = bracketdepth - 1

					if forgottoputptroncleanupstackIf.search(line2):
						inAnIfOrSelectStatement = 0
				i = i + 1
			return 0

	return 0

script.iCompare	= findForgetCompare
scanner.AddScript(script)

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
# friend.py
#
# Checks : Use of friends.
#
# Reason : The friend directive is often misused and can indicate 
# problems in the OO design.
#
# #################################################################

script = CScript("friend")
script.iReString = "^\s*friend\s"
script.iFileExts = ["cpp", "h", "hpp", "inl", "c"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# goto.py
#
# Checks : Use of goto.
#
# Reason : Goto should not be used if it can be avoided because 
# it makes the program flow more difficult to follow.
#
# #################################################################

script = CScript("goto")
script.iReString = "(^|[^\w])goto\s+"	# a goto at the beginning of a line or after a non-alphanumeric char
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# ifassignments.py
#
# Checks : Assignment in an If statement.
#
# Reason : Assignments inside an If statement often indicate that 
# the assignment was not intended. Even if the assignment was 
# intended, it is clearer to separate out the assignment from the 
# conditional. The script that detects such occurrences has a few 
# false positives when the action statements are on the same line 
# as the conditional check. However, this is also against the 
# coding standards and the action should be on a separate line.
#
# #################################################################

script = CScript("ifassignments")
script.iReString = "^\s*if\s*\(\s*.*[A-Za-z0-9_]\s*=\s*[A-Za-z0-9_].*\)"
script.iFileExts = ["h", "cpp", "c"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# ifpreprocessor.py
#
# Checks : Use of #if in .h files.
#
# Reason : #if in header files should only be used before the 
# main include guards and not around #include statements or around 
# functional blocks in class definitions. The reason for the latter 
# is to aid readability and to make BC breaks more difficult.
#
# #################################################################

script = CScript("ifpreprocessor")
script.iReString = "^\s*\#if(.*)"
script.iFileExts = ["h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def ifpreprocessorcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		text = m.group(1)
		slashindex = filename.rfind("/")
		if slashindex == -1 :
			slashindex = filename.rfind("\\")			
		if (slashindex <> -1) and (text.upper().find(filename[slashindex+1:-2].upper()) == -1):
			return 1
		else:
			return 0

script.iCompare = ifpreprocessorcompare
scanner.AddScript(script)

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
# inheritaenceorder.py
#
# Checks : Incorrect inheritance order of M and C classes.
#
# Reason : If a C class inherits first from an M class and then a 
# C class, a panic can occur when trying to pop a CBase pointer 
# pointing to such a class from the cleanup stack when in fact a 
# pointer pointing to the first predecessor, the mixin class, was 
# popped instead.
#
# #################################################################

script = CScript("inheritanceorder")
script.iReString = r"""
    ^\s*         # optional whitespace
    class
    \s+          # whitespace
    (\w+::)?
    (\w+)        # class name
    \s*          # optional whitespace
    :
    (.*)         # inheritance list
    """
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

def inheritancecompare(lines, currentline, rematch, filename):
    m = rematch.search(lines[currentline])
    if m:
        className = m.group(2)
        if className[0] <> "C" or (len(className) == 1) or not className[1].isupper():
            return 0

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

        # check the order of M and C classes in inheritance class list 
        mclassIndex = -1
        cclassIndex = -1
        for classname in classlist:
            if (len(classname) > 2):
                if classname[0] == "M" and classname[1].isupper() and mclassIndex == -1:
                    mclassIndex = classlist.index(classname)
                if classname[0] == "C" and classname[1].isupper() and cclassIndex == -1:
                    cclassIndex = classlist.index(classname)
        if mclassIndex != -1 and cclassIndex != -1 and mclassIndex < cclassIndex:
            return 1
        else:
            return 0

    return 0

script.iCompare = inheritancecompare
scanner.AddScript(script)

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
# intleaves.py
#
# Checks : Methods that leave AND return a TInt error.
#
# Reason : Returning an error code as well as being able to leave 
# is problematical for the caller. It is preferable to adhere to 
# one method of returning the error. Note: CodeScanner is likely to 
# return false positives for this situation, because some returned 
# TInt values will not be error codes.
#
# #################################################################

script = CScript("intleaves")
script.iReString = "TInt\s+\w+::\w+LC?\s*\("
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# jmp.py
#
# Checks : Use of setjmp and/or longjmp.
#
# Reason : Using setjmp and/or longjmp makes code less maintainable.
#
# #################################################################

script = CScript("jmp")
script.iReString = r"""
	(set|long)jmp
	"""
script.iFileExts = ["cpp", "h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# leave.py
#
# Checks : Leaving functions called in non-leaving functions.
#
# Reason : Non-leaving functions should not call leaving functions. 
# Note: Operator functions are considered to be able to leave when 
# scanning the code inside them.
#
# #################################################################

script = CScript("leave")
script.iReString = KReStringLeavingLine
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reLeavingMethod = re.compile("""
	(
	\s*operator
	|
	\w*
	[a-z]
	\w*
	L
	(C(C*|[2-9])|D|P|X)?
	$
	)
""", re.VERBOSE)

def leavecompare(lines, currentline, rematch, filename):
	currentMethod = scanner.iCurrentMethodName
	if (currentMethod <> "") and (currentMethod[:5] <> "Leave"):
		m = rematch.search(lines[currentline])
		if m and not reLeavingMethod.search(currentMethod):
			line = lines[currentline]
			startline = currentline
			if (lines[currentline].find("TRAP") != -1):
				return 0

			bracketCount = line.count("(") - line.count(")")
			startBracketCount = bracketCount

			while (currentline > startline - 40) and (currentline >= 0):
				currentline -= 1
				line = lines[currentline]
				bracketCount += line.count("(") - line.count(")")
				if (lines[currentline].find("TRAP") != -1) and (bracketCount == startBracketCount + 1):
					return 0
			return 1

	return 0

script.iCompare = leavecompare
scanner.AddScript(script)

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
# LeaveNoError.py
#
# Checks : Leaving with KErrNone.
#
# Reason : Leaving with KErrNone usually indicates that there is a 
# makeshift way around a design issue rather than a true and proper 
# fix to the architecture.
#
# #################################################################

script = CScript("LeaveNoError")
script.iReString = "User\s*::\s*Leave\(\s*KErrNone\s*\)"
script.iFileExts = ["cpp", "h", "c", "inl"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreComments
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# leavingoperators.py
#
# Checks : Leaving functions called in operator functions.
#
# Reason : It is not obvious that operator functions can leave. 
# Calling leaving functions in operator functions should be 
# considered carefully.
#
# #################################################################

script = CScript("leavingoperators")
script.iReString = "(\w*[a-z]\w*L(C*|D|P))\s*\(|ELeave|User::Leave|tream\s+<<|tream\s+>>"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reOperatorMethod = re.compile("""
	operator
	""", re.VERBOSE)

def leavecompare(lines, currentline, rematch, filename):
	currentMethod = scanner.iCurrentMethodName
	if (currentMethod <> "") and (currentMethod[:5] <> "Leave"):
		m = rematch.search(lines[currentline])
		if m and reOperatorMethod.search(currentMethod):
			line = lines[currentline]
			startline = currentline
			if (lines[currentline].find("TRAP") != -1):
				return 0

			bracketCount = line.count("(") - line.count(")")
			startBracketCount = bracketCount

			while (currentline > startline - 20) and (currentline >= 0):
				currentline -= 1
				line = lines[currentline]
				bracketCount += line.count("(") - line.count(")")
				if (lines[currentline].find("TRAP") != -1) and (bracketCount == startBracketCount + 1):
					return 0
			return 1

	return 0

script.iCompare = leavecompare
scanner.AddScript(script)

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
# LFunctionCantLeave.py
#
# Checks : L-functions that cannot leave.
#
# Reason : A function should not be named with an 'L' if it cannot 
# leave. The only exception is in virtual functions where the 
# function name is defined in the base class so the L cannot be 
# emoved. For example, RunL().
#
# #################################################################

script = CScript("LFunctionCantLeave")
script.iReString = r"""
	[A-Za-z0-9]+			# return type
	\s+
	[C|T|R][A-Za-z0-9]+		# class name
	::
	([A-Za-z0-9]+L(C|D)*)	# leaving function name (possible LC or LD function)
	\s*						# optional whitespace
	\(						# open bracket
	.*						# parameters
	\)						# close bracket
	\s*
	[^;]					# no semicolon after function definition
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

lfunctioncantleaveLeavingMethod = re.compile("""
	[A-Za-z0-9]+
	L
	(C|D)*
	\(
""", re.VERBOSE)

lfunctioncantleaveUserLeave = re.compile("""
	User::Leave
	""", re.VERBOSE)

lfunctioncantleaveNewELeave = re.compile("""
	new
	\s*
	\(
	\s*
	ELeave
	\s*
	\)
""", re.VERBOSE)

reLFunctionIgnoreStr = "RunL"
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("LFunctionIgnoreRE"):
		reLFunctionIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following functions when checking for L-functions that cannot leave: " + reLFunctionIgnoreStr
		break
if len(reLFunctionIgnoreStr) > 0:
	reLFunctionIgnores = re.compile(reLFunctionIgnoreStr, re.IGNORECASE)
else :
	reLFunctionIgnores = None

def lfunctioncantleavecompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		#ignore functions on the ignored list
		functionName = m.group(1)
		if reLFunctionIgnores:
			if reLFunctionIgnores.match(functionName):
				return 0

		i = currentline

		# find opening { in function
		while (line.count("{") == 0):
			i = i + 1
			if (i >= len(lines)):
				return 1
			line = lines[i]

		# if empty function (or one-line function?)
		if (line.count("}") > 0):
			return 1

		i = i + 1
		bracketDepth = 1

		while (i < len(lines)):
			line = lines[i]
			if lfunctioncantleaveLeavingMethod.search(line):
				return 0
			if lfunctioncantleaveUserLeave.search(line):
				return 0
			if lfunctioncantleaveNewELeave.search(line):
				return 0 

			bracketDepth += line.count("{") - line.count("}")
			if (bracketDepth == 0):
				return 1
			i = i + 1
	return 0

script.iCompare = lfunctioncantleavecompare
scanner.AddScript(script)

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
# longlines.py
#
# Checks : Overly long lines of code.
#
# Reason : Lines longer than about 100 characters can indicate 
# messy or badly-structured code that is hard to maintain.
#
# #################################################################

script = CScript("longlines")
# use configured line length, if available
scriptNode = script.ScriptConfig()
attrInt = 100
if (scriptNode <> None):
	attr = scriptNode.getAttribute("length")
	attrStr = str(attr)
	attrInt = 0
	if (attrStr.isdigit()):
		attrInt = int(attrStr)
	if (attrInt < 10):
		attrInt = 100
		print "Warning: Invalid line length configured; using default of 100: " + attr
	else:
		print "Note: 'long' line length configured as: " + str(attrInt)
script.iReString = r""".{"""+str(attrInt)+r"""}"""

script.iFileExts = ["cpp", "h", "rss", "rls", "loc", "ra","mmp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# magicnumbers.py
#
# Checks : Use of magic numbers.
#
# Reason : Magic numbers - that is, numbers that are hard-coded 
# into the source code and instead of being presented as constants 
# - make code difficult to maintain and give no indication of why 
# a calculation is the way it is. Magic numbers should be replaced 
# with named constants.
#
# #################################################################

script = CScript("magicnumbers")
script.iReString = "(.*[^a-zA-Z0-9_])([0-9]+)"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reEnum = re.compile("^\s*E\w+\s*=\s*");

def magiccompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		pretext = m.group(1)
		number = m.group(2)
		if (number == "0") or (number == "1") or (number == '2'):
			return 0
		elif (pretext.find("const") <> -1):
			return 0
		else:
			m2 = reEnum.search(pretext)
			if m2:
				return 0
			else:
				return 1

script.iCompare = magiccompare
scanner.AddScript(script)

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
# mclassdestructor.py
#
# Checks : M class has destructor.
#
# Reason : M classes should not contain a destructor.
#
# #################################################################

script = CScript("mclassdestructor")
script.iReString = r"""
	::
	\s*				# optional whitespace
	~M[A-Z]			# destructor
	"""
script.iFileExts = ["cpp", "h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)
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
# memberlc.py
#
# Checks : Assigning LC methods to member variables.
#
# Reason : Objects on the cleanup stack should not be assigned to 
# member variables.
#
# #################################################################

script = CScript("memberlc")
script.iReString = r"""
	^\s*
	i[A-Z]\w*
	\s*
	=
	\s*
	[\w:]+
	LC
	\s*
	\(
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reMemberLCPop = re.compile("\s*CleanupStack::Pop\s*\(")

def memberlccompare(lines, currentline, rematch, filename):
	if rematch.search(lines[currentline]):
		if (currentline + 1) < len(lines):
			if reMemberLCPop.search(lines[currentline + 1]):
				return 0	# next line is a Pop
			else:
				return 1
		else:					
			return 1
	else:
		return 0

script.iCompare = memberlccompare
scanner.AddScript(script)

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
# membervariablecallld.py
#
# Checks : Calling LD function on member variable.
#
# Reason : LD functions should not be called on a member variable 
# because ownership can be unclear and may lead to double deletes.
#
# #################################################################

script = CScript("membervariablecallld")
script.iReString = r"""
	i[A-Z]			# instance variable
	\w+				# rest of the instance variable name
	\s*				# optional whitespace
	(.|->)			# operator
	\s*				# optional whitespace
	[A-Z]			# classname
	\w+				# rest of the instance variable name
	LD\(			# LD function
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# missingcclass.py
#
# Checks : C class not inheriting from another C class.
#
# Reason : All C classes should inherit from another C class to 
# ensure that all data members are zeroed.
#
# #################################################################

script = CScript("missingcclass")
script.iReString = r"""
	^\s*
	class
	\s+
	(\w+::)?
	(\w+)
	\s*
	(.*)"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reCClassIgnoreStr = ""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("cclassIgnoreRE"):
		reCClassIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following classes when checking for C class not inheriting from another C class: " + reCClassIgnoreStr
		break
if len(reCClassIgnoreStr) > 0:
	reCClassIgnores = re.compile(reCClassIgnoreStr, re.IGNORECASE)
else :
	reCClassIgnores = None

def missingcclasscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		className = m.group(2)
		if className[0] <> "C" or (len(className) == 1) or not className[1].isupper():
			return 0

		#ignore classes on the ignored list
		if reCClassIgnores:
			if reCClassIgnores.search(className):
				return 0

		inheritanceString = m.group(3)
		i = currentline + 1
		while (inheritanceString.find("{") == -1) and i < len(lines):
			if (inheritanceString.find(";") <> -1):
				return 0
			inheritanceString += lines[i]
			i += 1
		
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

		ccount = 0
		for classname in classlist:
			if (len(classname) > 2) and classname[0] == "C" and classname[1].isupper():
				ccount += 1
				
		if ccount == 0:
			return 1
		else:
			return 0
	else:
		return 0

script.iCompare = missingcclasscompare
scanner.AddScript(script)

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
# mmpsourcepath.py
#
# Checks : Use of absolute path names in MMP files.
#
# Reason : Use of absolute paths in MMP files makes it impossible 
# to relocate the source. Relative paths should be used instead.
#
# #################################################################

script = CScript("mmpsourcepath")
script.iReString = "^\s*[Ss][Oo][Uu][Rr][Cc][Ee][Pp][Aa][Tt][Hh]\s*\\\\"
script.iFileExts = ["mmp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# multilangrsc.py
#
# Checks : Not using BaflUtils::NearestLanguageFile() when loading 
# a resource file.
#
# Reason : If AddResourceFileL() is used without first using 
# BaflUtils::NearestLanguageFile(), then not all language versions 
# of resources will be picked up.
#
# #################################################################

script = CScript("multilangrsc")
script.iReString = """
	AddResourceFileL
	\s*
	\(
	\s*\w+.*
	\)
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reBaflNearestLanguage = re.compile("""
	\s*
	BaflUtils::NearestLanguageFile
	\s*
	\(
	\s*\w+.*
	\)
	""", re.VERBOSE)

def multilangrsccompare(lines, currentline, rematch, filename):
	if (scanner.iCurrentMethodName <> ""):
		m = rematch.search(lines[currentline])
		if m:
			scanLineNum = currentline
			while (scanLineNum>scanner.iCurrentMethodStart):
				addResMatch = reBaflNearestLanguage.search(lines[scanLineNum])
				if addResMatch:
					return 0
				scanLineNum = scanLineNum - 1
			return 1
	return 0

script.iCompare = multilangrsccompare
scanner.AddScript(script)

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
# multipledeclarations.py
#
# Checks : Multiple declarations on one line.
#
# Reason : Multiple declarations on one line can be confusing. 
# Separate them out so that each declaration is on its own separate 
# line.
#
# #################################################################

script = CScript("multipledeclarations")
script.iReString = r"""
	\w+		# variable name
	\s*		# optional whitespace
	=
	\s*		# optional whitespace
	\w+		# variable value
	\s*		# optional whitespace
	,
	\s*		# optional whitespace
	\w+		# variable name
	\s*		# optional whitespace
	=
	\s*		# optional whitespace
	\w+		# variable value
	\s*		# optional whitespace
	;
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# multipleinheritance.py
#
# Checks : Non M-class multiple inheritance.
#
# Reason : It is bad Symbian OS practice to derive from two classes 
# that have implemented functions. Complex behaviour that was not 
# intended can result.
#
# #################################################################

script = CScript("multipleinheritance")
script.iReString = r"""
	^\s*
	class
	\s+
	(\w+::)?
	(\w+)
	\s*
	:
	(.*)"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

def classcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		className = m.group(2)
		if className[0] <> "C" or (len(className) == 1) or not className[1].isupper():
			return 0

		inheritanceString = m.group(3)
		i = currentline + 1
		while (inheritanceString.find("{") == -1) and i < len(lines):
			if (inheritanceString.find(";") <> -1):
				return 0
			inheritanceString += lines[i]
			i += 1
		
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

		ccount = 0
		for classname in classlist:
			if (len(classname) > 2) and classname[0] == "C" and classname[1].isupper():
				ccount += 1
				
		if ccount > 1:
			return 1
		else:
			return 0
	else:
		return 0

script.iCompare = classcompare
scanner.AddScript(script)

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
# mydocs.py
#
# Checks : Hard-coded mydocs directory strings.
# 
# Reason : The mydocs directory is subject to change so should not 
# be referenced directly. Note: @    This issue will only occur in 
# code developed for the Nokia Series 90 platform.
#
# #################################################################

script = CScript("mydocs")
script.iReString = """".*[Mm][Yy][Dd][Oo][Cc][Ss]"""
script.iFileExts = ["cpp", "h", "rss", "rls", "loc", "ra"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreComments
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# namespace.py
#
# Checks : Use of namespace.
#
# Reason : Namespaces are often used to work around a poor naming 
# convention.
#
# #################################################################

script = CScript("namespace")
script.iReString = "^\s*namespace\s*"
script.iFileExts = ["cpp", "h", "hpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# newlreferences.py
#
# Checks : NewL() returning a reference.
#
# Reason : NewL() and NewLC() functions should return a pointer to 
# an object created on the heap.
#
# #################################################################

script = CScript("newlreferences")
script.iReString = "&\s*NewL"
script.iFileExts = ["cpp", "h", "hpp", "inl", "c"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# nonconsthbufc.py
#
# Checks : Non-const HBufC* parameter passing.
#
# Reason : HBufC* parameters should almost always be passed as a 
# const pointer.
#
# #################################################################

script = CScript("nonconsthbufc")
script.iReString = """
    (\(|,)?        # open bracket or preceeding comma
    \s*            # whitespace
    (\w+)?
    \s*            # whitespace
    HBufC
    \s*            # whitespace
    \*
    \s*            # whitespace
    (\w+)          # parameter name
    (=|\w|\s)*     # optional parameter initialization or whitespace
    (\)|,)         # close bracket or trailing comma
    """
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def consthbufccompare(lines, currentline, rematch, filename):
    # make sure const HBufC* parameters are skipped
    line = lines[currentline]
    m = rematch.search(line)
    if m:
        isConst = (m.group(0).find("const") <> -1)
        while m and isConst:
            line = line[m.end():]
            m = rematch.search(line)
            if m:
                isConst = (m.group(0).find("const") <> -1)
        if isConst:
            return 0
        else:
            return DefaultFuncParamCompare(lines, currentline, rematch, filename)
    return 0

script.iCompare = consthbufccompare
scanner.AddScript(script)

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
# nonconsttdesc.py
#
# Checks : Non-const TDesC& parameter passing.
#
# Reason : TDesC& parameters should be passed as a const. If it is 
# not, it may indicate that the coder does not understand 
# descriptors, for example, passing descriptors by value.
#
# #################################################################

script = CScript("nonconsttdesc")
script.iReString = """
    (\(|,)?        # open bracket or preceeding comma
    \s*            # whitespace
    (\w+)?
    \s*            # whitespace
    (TDesC)
    \s*            # whitespace
    &
    \s*            # whitespace
    (\w+)          # parameter name
    (=|\w|\s)*     # optional parameter initialization or whitespace
    (\)|,)         # close bracket or trailing comma
    """
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def consttdesccompare(lines, currentline, rematch, filename):
    # make sure const TDesC& parameters are skipped
    line = lines[currentline]
    m = rematch.search(line)
    if m:
        isConst = (m.group(0).find("const") <> -1)
        while m and isConst:
            line = line[m.end():]
            m = rematch.search(line)
            if m:
                isConst = (m.group(0).find("const") <> -1)
        if isConst:
            return 0
        else:
            return DefaultFuncParamCompare(lines, currentline, rematch, filename)
    return 0

script.iCompare = consttdesccompare
scanner.AddScript(script)

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
# nonleavenew.py
#
# Checks : Use of new without (ELeave).
#
# Reason : Using new without (ELeave) is only used in special 
# circumstances. The leaving variant should typically be used in 
# preference. A common exception is for application creation, 
# where NULL is returned for failed creation.
#
# #################################################################

script = CScript("nonleavenew")
script.iReString = r"""
	(=|\(|,)		# equals, open bracket or comma
	\s*				# optional whitespace
	new\s+			# "new" plus at least one whitespace char
	([^\(\s]		# a character other than a bracket
	.*)
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

currentfilename = ""
iswindowsfile = 0
rewindows = re.compile("^\s*#include\s+<(windows|wchar).h>", re.IGNORECASE)

def checkforwindowsinclude(lines, filename):
	global currentfilename
	global iswindowsfile
	global rewindows

	if (currentfilename <> filename):
		currentfilename = filename
		iswindowsfile = 0
		for line in lines:
			m = rewindows.search(line)
			if m:
				iswindowsfile = 1
				break

	return iswindowsfile

def nonleavenewcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if (m.group(2).find("Application") <> -1):
			return 0
		else:				
			return not checkforwindowsinclude(lines, filename)

	return 0

script.iCompare = nonleavenewcompare
scanner.AddScript(script)

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
# nonunicodeskins.py
#
# Checks : Non-Unicode skins.
#
# Reason : Skin definition files (SKN, SKE) must be Unicode. 
# Note: Code that causes this issue only needs attention if it is 
# found in code developed for Nokia Series 90 code.
#
# #################################################################

script = CScript("nonunicodeskins")
script.iReString = r"""
	^\s*
	(//|/\*|A-Z|a-z|\#|\[)
"""
script.iFileExts = ["skn", "ske"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreNothing
script.iSeverity = KSeverityLow

def nonunicodecompare(lines, currentline, rematch, filename):
	return (currentline == 0) and rematch.search(lines[currentline])

script.iCompare = nonunicodecompare
scanner.AddScript(script)

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
# null.py
#
# Checks : NULL equality check.
#
# Reason : There is no need to compare pointer variables to NULL. 
# Use If(ptr).
#
# #################################################################

script = CScript("null")
script.iReString = r"""
	[!=]=\s*NULL
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def nullcompare(lines, currentline, rematch, filename):
    # It's OK to compare against NULL in return statement
    line = lines[currentline]
    m = rematch.search(line)
    if m:
    	if (line.find("return") > -1):
    		return 0
    	if (line.find("ASSERT") > -1):
    		return 0
    	return 1

    return 0

script.iCompare = nullcompare
scanner.AddScript(script)

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
# open.py
#
# Checks : Ignoring Open() return value.
#
# Reason : Ignoring the return value from Open() functions 
# (due to OOM, etc.) means that when the resource is accessed next, 
# a panic will result.
#
# #################################################################

script = CScript("open")
script.iReString = "^\s*(\w+)(\.|->)Open\s*\("
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reOpenIgnoreStr = ""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("openIgnoreRE"):
		reOpenIgnoreStr = wordNode.firstChild.nodeValue
		print "Note: ignoring the following objects and classes when checking for open() return value: " + reOpenIgnoreStr
		break
if len(reOpenIgnoreStr) > 0:
	reOpenIgnores = re.compile(reOpenIgnoreStr, re.IGNORECASE)
else :
	reOpenIgnores = None

reOpenAssignStr = "=\s+$"
reOpenAssign = re.compile(reOpenAssignStr, re.IGNORECASE)

def streamcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		# ignore objects with the word "tream" in object name or object type
		objectName = m.group(1)
		if (objectName.find("tream") <> -1):
			return 0
		objectType = GetLocalVariableType(lines, currentline, objectName)
		if (objectType.find("tream") <> -1):
			return 0

		#ignore objects with either object name or object type on the ignored list
		if reOpenIgnores:
			if reOpenIgnores.search(objectName):
				return 0
			if reOpenIgnores.search(objectType):
				return 0

		# look for handler of Open() return value on a different line
		i = currentline - 1
		if (i > 0) and (i >= scanner.iCurrentMethodStart):
			line = lines[i]
			bracketCount = line.count("(") - line.count(")")
			if (bracketCount > 0):
				return 0
			r = reOpenAssign.search(line)
			if r:
				return 0
		return 1
	else:
		return 0

script.iCompare = streamcompare
scanner.AddScript(script)

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
# pointertoarrays.py
#
# Checks : Pointer to arrays as members of a C class.
#
# Reason : In C classes, there is no need to use pointers to arrays 
# as data members. Instead, use the arrays themselves. Using 
# pointers leads to obscure notation like \"(*array)[n]\" for the 
# more usual \"array[n]\". It also makes it necessary to explicitly 
# delete the arrays in the destructor. Using the arrays themselves 
# also simplifies notation, reduces indirection, and reduces heap 
# fragmentation.
#
# #################################################################

script = CScript("pointertoarrays")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	[CR]\w*Array\w*		# class name e.g. RPointerArray
    (|<\w*>)			# optional "<Xxxx>" part
	\s*\*				# "*" (with optional whitespace)
	\s*i[A-Z]			# optional whitespace followed by the starting i of the member variable and then a capital letter
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

def pointerToArraysCompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		if (len(scanner.iCurrentClassName) > 1)  and (scanner.iCurrentClassName[0]=="C"):
			return 1    # only a problem with C classes
		else:
			return 0    
	else:
		return 0

script.iCompare = pointerToArraysCompare
script.iDisplayMethodName = 0
script.iDisplayClassName = 1

scanner.AddScript(script)

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
# pragmadisable.py
#
# Checks : Use of #pragma warning.
#
# Reason : Disabling warnings can lead to problems, because the 
# warnings are probably there for a reason.
#
# #################################################################

script = CScript("pragmadisable")
script.iReString = "\#pragma\s+warning"
script.iFileExts = ["h","cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# pragmamessage.py
#
# Checks : Use of #pragma message.
#
# Reason : #pragma messages during the build stage can interfere 
# with the build log parsing.
#
# #################################################################

script = CScript("pragmamessage")
script.iReString = "\#pragma\s+message"
script.iFileExts = ["h","cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# pragmaother.py
#
# Checks : Use of #pragma other than warning and message.
#
# Reason : #pragma directives should only be used in very edge 
# cases (for example, functions consisting of inline assembler 
# without explicit return statements) because, typically, their 
# usage masks valid build warnings and error messages.
#
# #################################################################

script = CScript("pragmaother")
script.iReString = "\#pragma\s+[^warning|message]"
script.iFileExts = ["h","cpp", "c", "inl"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# privateinheritance.py
#
# Checks : Use of private inheritance.
#
# Reason : Classes should not be inherited privately. If public or 
# protected inheritance is not appropriate, consider using an 
# amalgamation; that is, have an object of that type as a 
# member variable.
#
# #################################################################

script = CScript("privateinheritance")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	class
	\s+					# whitespace
	\w+					# class name
	\s*					# optional whitespace
	:
	(.*)
	"""
script.iFileExts = ["cpp", "h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def privatecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		searchtext = m.group(1)
		if (searchtext.find("private") == -1):
			return 0
		else:
			return 1
	else:
		return 0

script.iCompare = privatecompare
scanner.AddScript(script)

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
# pushaddrvar.py
#
# Checks : Pushing address of a variable onto the cleanup stack.
#
# Reason : If the variable is owned by the code pushing it, it 
# should be stored as a pointer. If it is not, it should not be 
# pushed onto the cleanup stack.
#
# #################################################################

script = CScript("pushaddrvar")
script.iReString = r"""
	::
	PushL\s*		# "PushL" plus optional whitespace
	\(				# open bracket
	\s*				# optional whitespace
	&				# taking the address?
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

scanner.AddScript(script)

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
# pushmember.py
#
# Checks : Pushing data members onto the cleanup stack.
#
# Reason : Pushing member variables is likely to lead to double 
# deletes or leakage in certain circumstances and so should be 
# avoided. Even if no panic can result, it is bad practice and 
# makes maintenance more difficult.
#
# #################################################################

script = CScript("pushmember")
script.iReString = r"""
	::
	PushL\s*		# "PushL" plus optional whitespace
	\(				# open bracket
	\s*				# optional whitespace
	i[A-Z]			# i variable
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

scanner.AddScript(script)

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
# readresource.py
#
# Checks : Using ReadResource() instead of ReadResourceL().
#
# Reason : ReadResourceL() should always be used in preference to 
# ReadResource() because in an error scenario ReadResource() 
# effectively fails silently. If no check is performed on the 
# resulting descriptor afterwards, unexpected states can ensue. 
# These states are often characterized by buffer overflows.
#
# #################################################################

script = CScript("readresource")
# matching against a line like this: iCoeEnv->ReadResource( buffer, R_RESOURCE_ID );
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	\w+					# variable name
	(\.|->)				# "." or "->"
	ReadResource\s*\(.*\)
	\s*;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

scanner.AddScript(script)

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
# resourcenotoncleanupstack.py
#
# Checks : Neglected to put resource objects on cleanup stack.
#
# Reason : If a stack-based resource object is not put on the 
# cleanup stack with CleanupResetAndDestroyPushL() or 
# CleanupClosePushL(), and a leaving function or ELeave is called, 
# a memory leak occurs. CodeScanner occasionally gives false 
# positives for this issue. Individual cases should be investigated.
#
# #################################################################

script = CScript("resourcenotoncleanupstack")
script.iReString = r"""
	^\s*					# start of line plus optional whitespace
	R\w+					# resource type
	\s*						# optional whitespace
	(<.*>)?					# optional class in angle brackets
	\s+						# whitespace
	(\w+)					# object name
	\s*						# optional whitespace
	;
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

cleanupFunction = re.compile("""
	\s*						# optional whitespace
	(CleanupClosePushL|CleanupResetAndDestroyPushL)
	\s*						# optional whitespace
	\(
	\s*						# optional whitespace
	(\w+)					# object name
	\s*						# optional whitespace
	\)
	\s*						# optional whitespace
	;
	""", re.VERBOSE)

def resourcecompare(lines, currentline, rematch, filename):
    m = rematch.search(lines[currentline])
    if m:
    	objectName = m.group(2)
    	bracketdepth = GetBracketDepth(lines, currentline)
    	i = currentline

    	# search for CleanupClosePushL() or CleanupResetAndDestroyPushL() 
    	# with the resource object at parameter
    	while (i < len(lines)):
    		nextLine = lines[i]
    		
    		match = cleanupFunction.search(nextLine)
    		if (match):
    			if objectName == match.group(2):
    				return 0

    		if (nextLine.find('{') >= 0):
    			bracketdepth = bracketdepth + 1
    		if (nextLine.find('}') >= 0):
    			bracketdepth = bracketdepth - 1
    			if (bracketdepth == 0):
    				return 1

    		i += 1

	return 0

script.iCompare = resourcecompare
scanner.AddScript(script)

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
# resourcesonheap.py
#
# Checks : Resource objects on the heap.
#
# Reason : There is very rarely any real need to put R classes on 
# the heap (unless they are not real R classes!).  Doing so can 
# lead to inefficiency and cleanup stack problems.
#
# #################################################################

script = CScript("resourcesonheap")
script.iReString = "new\s*(|\(ELeave\))\s+R[A-Z]"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# returndescriptoroutofscope.py
#
# Checks : Return descriptor out of scope.
#
# Reason : Returning a TBuf descriptor that is declared locally 
# takes it out of scope. This can cause a crash on WINSCW, although 
# not on WINS.
#
# #################################################################

script = CScript("returndescriptoroutofscope")
script.iReString = r"""
	TBuf
	\s*
	<
	[A-Za-z0-9]+
	>
	\s*
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCanPanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reReturnValue = re.compile("""
	return
	\s*
	""", re.VERBOSE)

reOpenCurlyBracket = re.compile("""
	{
	""", re.VERBOSE)

reCloseCurlyBracket = re.compile("""
	}
	""", re.VERBOSE)

def finddescriptor(line, descriptor):
	startindex = line.find(descriptor)
	if (startindex <> -1):
		if (line[startindex] == " "):
			if (line[startindex + len(descriptor)] == ";"):
				return 1
	return 0

def returnvaluecompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)

	if m:
		startindex = line.find(">");
		endindex = line.find(";");

		if (startindex <> -1):
			descriptor = line[startindex+1:endindex]

			i = currentline
			bracketdepth = 1
			while (i+1 < len(lines)):
				i = i + 1
				line2 = lines[i]

				if reReturnValue.search(line2):
					if (finddescriptor(line2, descriptor)):
						return 1

				if reOpenCurlyBracket.search(line2):
					bracketdepth = bracketdepth + 1

				if reCloseCurlyBracket.search(line2):
					bracketdepth = bracketdepth - 1
					if (bracketdepth == 0):
						return 0

	return 0

script.iCompare	= returnvaluecompare
scanner.AddScript(script)

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
# rfs.py
#
# Checks : Use of non-pointer/reference RFs.
#
# Reason : Connecting to an RFs is a time-consuming operation. 
# (It can take approximately 0.1 seconds on some devices.) 
# To minimise wasted time and resources, use the already-connected 
# one in EikonEnv or elsewhere, if possible.
#
# #################################################################

script = CScript("rfs")
script.iReString = r"""
	RFs
	\s+					# at least one whitespace char
	\w+					# variable name
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# rssnames.py
#
# Checks : Duplicate RSS names.
#
# Reason : Resource files with clashing NAME fields can cause the 
# wrong resource file to be accessed. This can lead to incorrect 
# functionality or panics.
#
# #################################################################

script = CScript("rssnames")
script.iReString = "^\s*NAME\s+(\w+)"
script.iFileExts = ["rss"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

rssnames = []

def rsscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		text = m.group(1).lower()
		shortfilename = filename[filename.rfind("/") + 1:].lower()
		for pair in rssnames:
			if (pair[0] == text):
			 	if (pair[1] == shortfilename):
					return 0
				else:
					scanner.iRendererManager.ReportAnnotation(pair[2])
					return 1

		rssnames.append([text, shortfilename, filename])
		return 0
	else:
		return 0

script.iCompare = rsscompare
scanner.AddScript(script)

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
# stringliterals.py
#
# Checks : Use of _L string literals.
#
# Reason : _L() string literals should be replaced by the _LIT() 
# macro.
#
# #################################################################

script = CScript("stringliterals")
script.iReString = r"""
	_L
	(16|8)?			# optional "16" or "8"
	\(
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def stringliteralscompare(lines, currentline, rematch, filename):
	if (lines[currentline].find("RDebug::Print(") != -1):
		return 0
	else:
		m = rematch.search(lines[currentline])
		if m:
			return 1
		else:
			return 0

script.iCompare = stringliteralscompare
scanner.AddScript(script)

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
# stringsinresourcefiles.py
#
# Checks : Strings in RSS or RA files.
#
# Reason : Strings should not be defined in RSS or RA files. 
# Instead, they should be put in RLS or other localisable files.
#
# #################################################################

script = CScript("stringsinresourcefiles")
script.iReString = "=\s*\"[^\"]+\""
script.iFileExts = ["rss", "ra"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreComments
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# struct.py
#
# Checks : Use of struct.
#
# Reason : C-style structs should not generally be used. 
# The correct idiom is to use a class with public members. 
# A permissible use of a C-style struct is if it is used to group 
# non-semantically related entities together for convenience, and 
# if a class-related hierarchy would be too heavy-weight.
#
# #################################################################

script = CScript("struct")
script.iReString = "^\s*struct\s*"
script.iFileExts = ["cpp", "h", "hpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# tcclasses.py
#
# Checks : T classes inheriting from C classes.
#
# Reason : T classes that are derived from C classes may have a 
# complex constructor and so need to be handled differently. 
# It is better to make the T class into a C class, which will make 
# the code easier to maintain.
#
# #################################################################

script = CScript("tcclasses")
script.iReString = r"""
	class
	\s+					# at least one whitespace char
	(\w+::)?
	(\w+)				# T class
	\s*					# optional whitespace
	:
	(.*)				# save inheritance text as group 1
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

def tcclasscompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		className = m.group(2)
		if className[0] <> "T" or (len(className) == 1) or not className[1].isupper():
			return 0

		inheritanceString = m.group(3)
		i = currentline + 1
		while (inheritanceString.find("{") == -1) and i < len(lines):
			if (inheritanceString.find(";") <> -1):
				return 0
			inheritanceString += lines[i]
			i += 1	

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

		for classname in classlist:
			if (len(classname) > 2) and classname[0] == "C" and classname[1].isupper():
				return 1
	return 0

script.iCompare = tcclasscompare
scanner.AddScript(script)

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
# tclassdestructor.py
#
# Checks : T class has destructor.
#
# Reason : T classes should not have a destructor.
#
# #################################################################

script = CScript("tclassdestructor")
script.iReString = r"""
	::
	\s*				# optional whitespace
	~T[A-Z]			# destructor
	"""
script.iFileExts = ["cpp", "h"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# todocomments.py
#
# Checks : "To do" comments.
#
# Reason : "To do" comments in code suggest that it is not finished.
#
# #################################################################

script = CScript("todocomments")
script.iReString = r"""
	/(/|\*)						# "//" or "/*"
	.*(t|T)(o|O)(d|D)(o|O)		# skip to Todo
	"""
script.iFileExts = ["h", "cpp", "c"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreQuotes
script.iSeverity = KSeverityLow

def todocommentcodecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		line = lines[currentline]
		i = 0
		inCommentBlock = 0

		while i < len(line):
			if not inCommentBlock:
				if (line[i] == "/"):
					if (line[i + 1] == "/"):
						return 1
					elif (line[i + 1] == "*"):
						inCommentBlock = 1
						i += 2
						continue
			else:
				endIndex = line[i:].find("*/")
				if (endIndex <> -1):
					inCommentBlock = 0
					# note, that first character is ignored in comments as can be direction to the in-source documentation tool
					if (line[i+1:i + endIndex + 2].lower().find("todo") <> -1):
						return 1
					i += endIndex + 2
					continue
				else:
					return 1			
			i += 1		
	return 0

script.iCompare = todocommentcodecompare
scanner.AddScript(script)

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
# trapcleanup.py
#
# Checks : Use of LC function in TRAPs.
#
# Reason : You cannot trap something that leaves something on the 
# cleanup stack because it will panic.
#
# #################################################################

script = CScript("trapcleanup")
script.iReString = "^\s*TRAPD?"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryDefinitePanic
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityHigh

reCMethod = re.compile("""
	\w*
	[a-z]
	\w*
	LC\(
""", re.VERBOSE)

def trapcleanupcompare(lines, currentline, rematch, filename):
	line = lines[currentline]
	m = rematch.search(line)
	if m:
		bracketCount = line.count("(") - line.count(")")
		cMethod = reCMethod.search(line) 
		pop = line.find("Pop")			
						 
		while (bracketCount > 0) and (currentline + 1 < len(lines)):
			currentline += 1
			line = lines[currentline]
			bracketCount += line.count("(") - line.count(")")
			if not cMethod:
				cMethod = reCMethod.search(line) 
			if (pop == -1):
				pop = line.find("Pop")			

		if cMethod and (pop == -1):
			return 1
	
	return 0

script.iCompare = trapcleanupcompare
scanner.AddScript(script)

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
# trapeleave.py
#
# Checks : Trapping new(ELeave).
#
# Reason : The trapping of a "new(ELeave) CXxx" call is redundant 
# and wasteful as the code to support TRAP is surprisingly large. 
# If the instantiation process really needs not to leave, use 
# "new CXxx" and check for NULL.
#
# #################################################################

script = CScript("trapeleave")
script.iReString = "^\s*TRAPD?"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

reELeave = re.compile("""
    new
    \s*        # whitespace
    \(         # open bracket
    \s*        # whitespace
    ELeave
    \s*        # whitespace
    \)         # close bracket
""", re.VERBOSE)

def trapeleavecompare(lines, currentline, rematch, filename):
    line = lines[currentline]
    m = rematch.search(line)
    if m:
        if (line.find("(") == -1) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]

        bracketCount = line.count("(") - line.count(")")
        found = reELeave.search(line) 

        while (bracketCount > 0) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]
            bracketCount += line.count("(") - line.count(")")
            if not found:
                found = reELeave.search(line) 

        if found:
            return 1

    return 0

script.iCompare = trapeleavecompare
scanner.AddScript(script)

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
# traprunl.py
#
# Checks : Trapping of (Do)RunL() rather than using RunError().
#
# Reason : The RunError() function should be used rather than the 
# CActive derivative using its own TRAPD solution within a RunL().
#
# #################################################################

script = CScript("traprunl")
script.iReString = "^\s*TRAPD?"
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

reRunL = re.compile("""
    RunL
    \s*        # whitespace
    \(         # open bracket
""", re.VERBOSE)

def traprunlcompare(lines, currentline, rematch, filename):
    line = lines[currentline]
    m = rematch.search(line)
    if m:
        if (line.find("(") == -1) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]

        bracketCount = line.count("(") - line.count(")")
        found = reRunL.search(line) 

        while (bracketCount > 0) and (currentline + 1 < len(lines)):
            currentline += 1
            line = lines[currentline]
            bracketCount += line.count("(") - line.count(")")
            if not found:
                found = reRunL.search(line) 

        if found:
            return 1

    return 0

script.iCompare = traprunlcompare
scanner.AddScript(script)

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
# trspassing.py
#
# Checks : Passing TRequestStatus parameters by value.
#
# Reason : TRequestStatus parameters should be passed by reference. 
# If TRequestStatus is just being used as an error code, then 
# convert it to a TInt.
#
# #################################################################

script = CScript("trspassing")
script.iReString = r"""
    (\(|,)?				# open bracket or preceeding comma
    \s*					# whitespace
	TRequestStatus
    \s*					# whitespace
	[^&*]				# matches any character except '&' and '*'
    \s*					# whitespace
	(\w+)				# parameter name
    (=|\w|\s)*          # optional parameter initialization or whitespace
    (\)|,)				# close bracket or trailing comma
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryWrongFunctionality
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium
script.iCompare = DefaultFuncParamCompare

scanner.AddScript(script)

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
# uids.py
#
# Checks : Duplicate UIDs.
#
# Reason : UIDs must be unique.
#
# #################################################################

script = CScript("uids")
script.iReString = r"""
	^\s*			# whitespace
	[Uu][Ii][Dd]	# uid			
	\s+				# at least one whitespace char
	\w+
	\s+				# at least one whitespace char
	(\w+)
	"""
script.iFileExts = ["mmp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

uids = []

def uidcompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		text = m.group(1).lower()
		shortfilename = filename[filename.rfind("/") + 1:].lower()
		for pair in uids:
			if (pair[0] == text):
			 	if (pair[1] == shortfilename):
					return 0
				else:
					scanner.iRendererManager.ReportAnnotation(pair[2])
					return 1

		uids.append([text, shortfilename, filename])
		return 0
	else:
		return 0

script.iCompare = uidcompare
scanner.AddScript(script)

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
# uncompressedaif.py
#
# Checks : Uncompressed AIFs in ROM.
#
# Reason : AIF files should be referenced as "AIF=" rather than 
# "data=" or "file=" otherwise they can bloat the ROM size and 
# slow down application loading.
#
# #################################################################

script = CScript("uncompressedaif")
script.iReString = r"""
			(
			^
			\s*
			(data|file)
			\s*
			=
			.*
			\.aif
			)
			"""
script.iFileExts = ["iby", "hby", "oby"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# unicodesource.py
#
# Checks : Unicode source files.
#
# Reason : Having Unicode source files (CPP, H, RLS, LOC, RSS, and 
# RA) will break most build systems.
#
# #################################################################

script = CScript("unicodesource")
script.iReString = r"""
	^
	\xFF\xFE	
	"""
script.iFileExts = ["cpp", "h", "rls", "loc", "rss", "ra"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def unicodesourcecompare(lines, currentline, rematch, filename):
	return (currentline == 0) and rematch.search(lines[currentline])

script.iCompare = unicodesourcecompare
scanner.AddScript(script)

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
# userafter.py
#
# Checks : Use of User::After.
#
# Reason : Generally, User::After() functions are used to skirt 
# around timing problems. Typically, they should be removed and the 
# defects fixed properly: that is, by waiting for the correct event 
# to continue execution.
#
# #################################################################

script = CScript("userafter")
script.iReString = "User::After\s*\("
script.iFileExts = ["cpp"]
script.iCategory = KCategoryPerformance
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityMedium

scanner.AddScript(script)

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
# userfree.py
#
# Checks : Using User::Free directly.
#
# Reason : User::Free() should never be called, because all objects 
# free their memory on deletion; their destructors are not called 
# and further resources cannot be freed or closed. This function 
# should be removed and replaced by explicit deletes.
#
# #################################################################

script = CScript("userfree")
script.iReString = "User::Free\s*\("
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# userWaitForRequest.py
#
# Checks : Use of User::WaitForRequest.
#
# Reason : User::WaitForRequest() should not generally be used in 
# UI code because the UI will not respond to redraw events while 
# its thread is stopped.
#
# #################################################################

script = CScript("userWaitForRequest")
script.iReString = "User::WaitForRequest\s*\(\s*"
script.iFileExts = ["cpp","inl"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# variablenames.py
#
# Checks : Local variables with member/argument names.
#
# Reason : Local variable names should be of the form localVariable 
# and not aLocalVar or iLocalVar. Badly-named variables can be 
# misleading and cause maintenance and coding errors.
#
# #################################################################

script = CScript("variablenames")
script.iReString = r"""
	^\s*				# start of line plus optional whitespace
	[A-Z]\w*			# class name e.g. TInt, CActive
	\s*[\*&\s]\s*		# optional "*" or "&" plus at least one whitespace char
	[ai][A-Z]\w*\s*		# a or i variable name plus optional whitespace
	[;\(=]				# ";" or "(" or "="
	"""
script.iFileExts = ["cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

def bracecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		checkline = currentline - 1
		bracecount = 1
		while (bracecount > 0) and (checkline >= 0):
			bracecount -= lines[checkline].count("{")
			bracecount += lines[checkline].count("}")
			checkline -= 1

		while (bracecount == 0) and (checkline >= 0):
			if (lines[checkline].upper().find("CLASS") <> -1) or (lines[checkline].upper().find("STRUCT") <> -1):
				return 0
			
			bracecount -= lines[checkline].count("{")
			bracecount += lines[checkline].count("}")
			checkline -= 1

		return 1
	else:
		return 0

script.iCompare = bracecompare
scanner.AddScript(script)

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
# voidparameter.py
#
# Checks : Void parameter explicitly declared.
#
# Reason : Declaring a void parameter is unnecessary. A function 
# declared as DoSomething(void) may as well be declared as 
# DoSomething(). Void casts are also unnecessary.
#
# #################################################################

script = CScript("voidparameter")
script.iReString = r"""
	\(				# opening bracket
	\s*				# optional whitespace
	void			# void paramater declaration
	\s*				# optional whitespace
	\)				# closing bracket
	.*;				# skip to semicolon
	"""
script.iFileExts = ["h", "cpp"]
script.iCategory = KCategoryCodingStandards
script.iIgnore = KIgnoreCommentsAndQuotes
script.iSeverity = KSeverityLow

scanner.AddScript(script)

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
# worryingcomments.py
#
# Checks : Worrying comments.
#
# Reason : Typically, exclamation and question marks in comments 
# indicate that something odd is in the code or that it is 
# unfinished or not understood fully.
#
# #################################################################

script = CScript("worryingcomments")
script.iFileExts = ["h", "cpp", "c"]
script.iCategory = KCategoryCodeReviewGuides
script.iIgnore = KIgnoreQuotes
script.iSeverity = KSeverityLow

reWordsStr = r"""\!|\?|[Zz]{3}|kludge|workaround|\scrap|hack"""
scriptNode = script.ScriptConfig()
if (scriptNode <> None):
	for wordNode in scriptNode.getElementsByTagName("worryRE"):
		reWordsStr = wordNode.firstChild.nodeValue
		print "Note: 'worrying comments' pattern configured as: " + reWordsStr
		break
script.iReString = r"""
	/(/|\*)						# "//" or "/*"
	.*("""+reWordsStr+r""")		# skip to "!", "?", "zzz", "kludge", "workaround", " crap" or "hack"
	"""

def worryingcommentcodecompare(lines, currentline, rematch, filename):
	m = rematch.search(lines[currentline])
	if m:
		line = lines[currentline]
		i = 0
		inCommentBlock = 0

		while i < len(line):
			if not inCommentBlock:
				if (line[i] == "/"):
					if (line[i + 1] == "/"):
						# note i+3 to bypass the character after the start of the comment as can be an in-source documentation directive
						return (line[i+3:].find("!")<>-1) or (line[i+3:].find("?")<>-1)
					elif (line[i + 1] == "*"):
						inCommentBlock = 1
						i += 2
						continue
			else:
				endIndex = line[i:].find("*/")
				if (endIndex <> -1):
					inCommentBlock = 0
					# note, that first character is ignored in comments as can be direction to the in-source documentation tool
					if (line[i+1:i + endIndex + 2].find("!") <> -1) or (line[i+1:i + endIndex + 2].find("?") <> -1):
						return 1
					i += endIndex + 2
					continue
				else:
					return 1			
			i += 1		
	return 0

script.iCompare = worryingcommentcodecompare
scanner.AddScript(script)

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
