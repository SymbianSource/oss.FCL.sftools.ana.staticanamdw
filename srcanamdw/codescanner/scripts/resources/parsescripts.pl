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
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.#
#
#!/usr/bin/perl -w


use strict;


open( STRINGPOOL, ">>stringPool.py" ) || die "Unable to open String Pool";

my $fileName;
for $fileName ( @ARGV )
{
    open( INPUT, $fileName ) || die "Unable to open $fileName";
    my @file = <INPUT>;
    close( INPUT );


    open( OUTPUT, ">$fileName" ) || die "Unable to open $fileName";
    my $scriptName = "!!!";
    my $title = "!!!no title found";
    my $description = "!!!no description found";
    my $ideTitle = "!!!no IDE title found";

    my $i;
    for( $i = 0; $i <= $#file; $i++ )
    {
	if( $file[ $i ] =~ m/CScript\(\"(\w+)\"\)/ )
	{
	    $scriptName = $1;
	}

	if( $file[ $i ] =~ m/script.iTitleString\ +=\ +\"(.+)\"/ )
	{
	    $title = $1;
	    $file[ $i ] = "# " . $file[ $i ];
	}

	if( $file[ $i ] =~ m/script.iDescription\ +=\ +\"(.+)\"/ )
	{
	    $description = $1;
	    $file[ $i ] = "# " . $file[ $i ];
	}

    
	if( $file[ $i ] =~ m/script.iErrorMessage\ +=\ +\"(.+)\"/ )
	{
	    $ideTitle = $1;
	    $file[ $i ] = "# " . $file[ $i ];
	}

	print OUTPUT $file[ $i ];

    }
    
    close( OUTPUT );

    print STRINGPOOL <<EOS;
# localised string for Script $scriptName
stringPool[ "$scriptName!title" ]       = "$title"
stringPool[ "$scriptName!description" ] = "$description"
stringPool[ "$scriptName!ideTitle" ]    = "$ideTitle"

EOS
    ;
}

close( STRINGPOOL );

