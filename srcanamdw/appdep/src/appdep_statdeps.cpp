/*
* Copyright (c) 2007 Nokia Corporation and/or its subsidiary(-ies). 
* All rights reserved.
* This component and the accompanying materials are made available
* under the terms of "Eclipse Public License v1.0"
* which accompanies this distribution, and is available
* at the URL "http://www.eclipse.org/legal/epl-v10.html".
*
* Initial Contributors:
* Nokia Corporation - initial contribution.
*
* Contributors:
*
* Description:  Handling of StaticDependencies.txt 
*
*/


#include "appdep.hpp"


// ----------------------------------------------------------------------------------------------------------
// Note that in C/C++ code \ has been replaced with \\ and " with \".
// ----------------------------------------------------------------------------------------------------------

void GetDataFromStaticDependenciesTxt()
{
    // read cache data from given StaticDependencies.txt
 	if (!FileExists(_cl_usestaticdepstxt))
	{
		cerr << "ERROR: Unable to find " + _cl_usestaticdepstxt << ", check -usestaticdepstxt param" << endl;
		cerr << "Please note that this parameter is required only if you use StaticDependencies.txt." << endl;
		exit(EXIT_CANNOT_OPEN_STATIC_DEPENDENCIES_TXT);
	} 

	ifstream staticdepsf(_cl_usestaticdepstxt.c_str());
	string line;
	
	getline(staticdepsf, line);
	if (line != "# Full direct component mapping:")
    {
		cerr << "ERROR: " << _cl_usestaticdepstxt << " is not a supported StaticDependencies.txt file!" << endl;
		staticdepsf.close(); 
		exit(EXIT_OPENED_STATIC_DEPENDENCIES_TXT_NOT_SUPPORTED);   
    }
    else
    { 
        cerr << "Warning: Use of StaticDependencies.txt may provide incomplete results..." << endl;    

        bool line_was_consumed = true;

        // loop through all lines in the file
        while(!staticdepsf.eof())
        {
            // get a line
            if (line_was_consumed)
                getline(staticdepsf, line);

            if (line == "# Full inverse component mapping:")
            {
                // no interesting lines in this file anymore, break the loop
                break;    
            }
            
            // first line is the executable type, eg
            // armv5::screengrabber (exe)
            boost::regex re1("^(\\S+)::(\\S+)\\s\\((\\S+)\\).*");
            boost::cmatch matches1;                
            if (boost::regex_match(line.c_str(), matches1, re1))
            {
                // match found
                string ms1(matches1[1].first, matches1[1].second); // binary type
                string ms2(matches1[2].first, matches1[2].second); // filename
                string ms3(matches1[3].first, matches1[3].second); // extension
                                
                line_was_consumed = true;

                binary_info b_info;
                b_info.directory = UNKNOWN;
                b_info.filename = ms2 + "." + ms3;
                b_info.binary_format = ms1 + " " +ms3;
                b_info.uid1 = UNKNOWN;
                b_info.uid2 = UNKNOWN;
                b_info.uid3 = UNKNOWN;
                b_info.secureid = UNKNOWN;
                b_info.vendorid = UNKNOWN;
                b_info.capabilities = 0;
                b_info.min_heap_size = 0;
                b_info.max_heap_size = 0;
                b_info.stack_size = 0;
                b_info.mod_time = 0;
                
                vector<dependency> deps;
                for (;;)
                {
                    // get a line
                    if (line_was_consumed)
                        getline(staticdepsf, line);
            
                    // check for dependency line, eg
                    //    screengrabber -> euser
                    boost::regex re2("^\\s\\s\\s(\\S+)\\s->\\s(\\S+).*");
                    boost::cmatch matches2;                
                    if (boost::regex_match(line.c_str(), matches2, re2))
                    {
                        // match found
                        string ms1(matches2[1].first, matches2[1].second); // filename
                        string ms2(matches2[2].first, matches2[2].second); // dependency
                        
                        line_was_consumed = true;
                                            
                        dependency dep;
                        dep.filename = ms2 + ".dll"; // assumming that the file extension is always .dll 
                        
                        vector<import> imps;
                        for (;;)
                        {
                            if (line_was_consumed)
                                getline(staticdepsf, line);
                    
                            // check for function names, eg
                            //       fref::screengrabber->euser.CActive::Cancel (1)
                            boost::regex re3("^\\s\\s\\s\\s\\s\\sfref::(\\S+)->(\\S+)\\.(\\S+)\\s\\((\\S+)\\).*");
                            boost::cmatch matches3;   
                            if (boost::regex_match(line.c_str(), matches3, re3))
                            {
                                // match found
                                string ms1(matches3[1].first, matches3[1].second); // filename
                                string ms2(matches3[2].first, matches3[2].second); // dependency
                                string ms3(matches3[3].first, matches3[3].second); // functionname
                                string ms4(matches3[4].first, matches3[4].second); // ???
                                
                                line_was_consumed = true;
                                
                                import imp;
                                imp.funcpos = 0;
                                imp.funcname = ms3;
                                imp.is_vtable = false;
                                imp.vtable_offset = 0;
                
                                // append to the import info vector
                                imps.push_back( imp );
                            }
                            else
                            {
                                // the line does not match, break the loop
                                line_was_consumed = false;
                                break;
                            }
                                
                        } // for (;;)
                            
                        // now we have import info too
                        dep.imports = imps;
                        
                        // append to the deps info vector
                        deps.push_back( dep );
                            
                    } 
                    else
                    {
                        // the line does not match, break the loop
                        line_was_consumed = false;
                        break;
                    }
                } // for (;;)
                
                // now we have the dep info too
                b_info.dependencies = deps;
                
                // apppend binary info to the vectory
                _all_binary_infos.push_back( b_info );
                
            }
            else
            {
                // no match found, line was consumed anyway
                line_was_consumed = true;    
            } // else of if (boost::regex_match(tempVector.at(j).c_str(), matches1, re1))
            
        } // while(!staticdepsf.eof())
    } // else of if (line != "# Full direct component mapping:")   

    // close handle to the cache file
    staticdepsf.close();  
}

// ----------------------------------------------------------------------------------------------------------

