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
* Description:  Handling of sis files 
*
*/


#include "appdep.hpp"

// ----------------------------------------------------------------------------------------------------------
// Note that in C/C++ code \ has been replaced with \\ and " with \".
// ----------------------------------------------------------------------------------------------------------

void DoInitialChecksAndPreparationsForSisFiles()
{
    // specify full location for dumpsis
    _dumpsis_location = _cl_releasedir + DUMPSIS_LOCATION;

    // check if dumpsis can be found
 	if (!FileExists(_dumpsis_location))
	{
		cerr << "ERROR: Unable to find " + _dumpsis_location << ", check -release param" << endl;
		cerr << "Please notice that this feature is available only in Symbian OS 9.x" << endl;
		cerr << "It is possible the user to copy dumpsis.exe from some other release under" << endl;
		cerr << "this release to support this feature." << endl;
		exit(EXIT_DUMPSIS_NOT_FOUND);
	}         

    // insert quotes to the dumpsis location to avoid any problems caused by white spaces
    InsertQuotesToFilePath(_dumpsis_location);

    // parse commandline argument "sisfiles" from sisfile;sisfile;...
    int last_found_semicolon_pos = -1;
    for (unsigned int i=0; i<_cl_sisfiles.length(); i++)
    {   
        // try to find ';' characters 
        string::size_type semicolon_pos = _cl_sisfiles.find(";", i);
        
        if (semicolon_pos == string::npos)
        {
            // could not find the ';' character, append last part of the list
            string sis_file = _cl_sisfiles.substr(last_found_semicolon_pos+1,_cl_sisfiles.length()-last_found_semicolon_pos-1);
            _sisfiles.push_back(sis_file);
            break;
        }
        else
        {
            // found a ';' character, append to the list, but needs to check if there are more
            string sis_file = _cl_sisfiles.substr(last_found_semicolon_pos+1, semicolon_pos-last_found_semicolon_pos-1);
            
            if (sis_file.length() > 0)
                _sisfiles.push_back(sis_file);
            
            last_found_semicolon_pos = semicolon_pos;
            i = last_found_semicolon_pos;
        }    
    }

    // check that all given sisfiles can be found and it is supported
    for (unsigned int i=0; i<_sisfiles.size(); i++)
    { 
        // report an error if the file does not exist
        if (!FileExists(_sisfiles.at(i)))
        {
     		cerr << "ERROR: Unable to find " + _sisfiles.at(i) << ", check -sisfiles parameter" << endl;
    		exit(EXIT_SIS_FILE_NOT_FOUND);           
        }
        
        // open the sis file for reading to check if it is supported    
        ifstream sisf(_sisfiles.at(i).c_str(), ios::binary);
		if (sisf.is_open())
		{
            int c1, c2, c3, c4;
            c1 = sisf.get();
            c2 = sisf.get();
            c3 = sisf.get();
            c4 = sisf.get();
            
            // in valid sis first four bytes of the file are 7A1A2010
            if (c1==0x7A && c2==0x1A && c3==0x20 && c4==0x10)
            {
                //cerr << _sisfiles.at(i) << " is supported" << endl;
            }
            else
            {
                // if starting from offset 8, four next bytes are 19040010, the file is
                // unsupported SIS file used in previous Symbian OS releases.    
                sisf.seekg(8, ios::beg);
                c1 = sisf.get();
                c2 = sisf.get();
                c3 = sisf.get();
                c4 = sisf.get();
                sisf.close();

                if (c1==0x19 && c2==0x04 && c3==0x00 && c4==0x10)
                {
                    cerr << "ERROR: " + _sisfiles.at(i) << " is a pre-Symbian OS 9.x" << endl;
                    cerr << "sisfile which is not supported, check -sisfiles parameter" << endl;
                    exit(EXIT_SIS_FILE_NOT_SUPPORTED); 
                }
                else
                {
                    cerr << "ERROR: " + _sisfiles.at(i) << " is not a valid sis file," << endl;
                    cerr << "check -sisfiles parameter" << endl;
                    exit(EXIT_NOT_SIS_FILE);                     
                }
            }    
            sisf.close();
        }
        else
        {
     		cerr << "ERROR: Cannot open " + _sisfiles.at(i) << " for reading, check -sisfiles parameter" << endl;
    		exit(EXIT_SIS_FILE_CANNOT_OPEN_FOR_READING); 
        }
    }    
}

// ----------------------------------------------------------------------------------------------------------

void AnalyseSisFiles()
{
    // create a new target and set some defaults
    target sis_target;
    sis_target.name = "sis";
    sis_target.cache_dir = _cl_cachedir + sis_target.name + DIR_SEPARATOR;
    sis_target.dep_cache_path = sis_target.cache_dir + CACHE_DEP_FILENAME;

    cerr << "Analysing sis files..." << endl;

    // define path to a temp directory where dumpsis will extract the files    
    const string tempdir = _cl_cachedir + SIS_TEMP_DIR + DIR_SEPARATOR;
    const string tempdir2 = _cl_cachedir + SIS_TEMP_DIR;

    // do analysis for each file
    for (unsigned int i=0; i<_sisfiles.size(); i++)
    { 
        // create the temporary directory
        MkDirAll(tempdir);

        cerr << "Binaries in " << _sisfiles.at(i) << " are:" << endl;
        
        // due to bugginess of a specific version of dumpsis, we need to copy the source file under the temporary directory
        const string new_sis_loc = tempdir + "tempsis.sis";
        
        ifstream src_sis_f(_sisfiles.at(i).c_str(), ios::binary);
        if (src_sis_f.is_open())
		{
            ofstream trgt_sis_f(new_sis_loc.c_str(), ios::binary);
            if (trgt_sis_f.is_open())
    		{
                // read all bytes from source and write to the target
                int c1;

                while(!src_sis_f.eof())
                {
                    c1 = src_sis_f.get();
                    trgt_sis_f.put(c1);
                }
                
                trgt_sis_f.close();            
            
            }
            else
            {
         		cerr << "ERROR: Cannot open " + new_sis_loc << " for writing, check write permissions" << endl;
        		exit(EXIT_TEMP_SIS_FILE_CANNOT_OPEN_FOR_WRITING); 
            }             

            src_sis_f.close();
                        
        }
        else
        {
     		cerr << "ERROR: Cannot open " + _sisfiles.at(i) << " for reading, check -sisfiles parameter" << endl;
    		exit(EXIT_SIS_FILE_CANNOT_OPEN_FOR_READING); 
        }        
        
        

        // execute dumpsis        
        string cmd = _dumpsis_location + " -x -d \"" + tempdir2 + "\" \"" + new_sis_loc + "\" " + CERR_TO_NULL;
        
        vector<string> tempVector;
        ExecuteCommand(cmd, tempVector);
        
       
        // check if pkg file found
        string pkgfile_location = tempdir + "tempsis.pkg";
        
        if (!FileExists(pkgfile_location))
        {
            // try again with an alternative
            pkgfile_location = tempdir + "tempsis.sis.pkg";

            if (!FileExists(pkgfile_location))
            {
         		RemoveDirectoryWithAllFiles(tempdir);
                cerr << "ERROR: Dumpsis failed for " << _sisfiles.at(i) << " since it does not contain a pkg file, check -sisfiles parameter" << endl;
        		exit(EXIT_NO_PKG_FILE_FOUND); 
            }            
        }

        // open the pkg file for reading
        ifstream pkgf(pkgfile_location.c_str(), ios::binary);
		if (pkgf.is_open())
		{
            int c1, c2;
            c1 = pkgf.get();
            c2 = pkgf.get();
            
            // we only support unicode format
            if (c1 == 0xFF && c2 == 0xFE)
            {
                string line;

                 // read more chars
                 while(!pkgf.eof())
                 {
                    c1 = pkgf.get();
                    c2 = pkgf.get();
                    
                 //   if (c1 == 0x0D && c2 == 0x00)  // new line marker #1
                  //  {
                      //  c1 = pkgf.get();
                      //  c2 = pkgf.get();                        

                        if (c1 == 0x0A && c2 == 0x00)  // new line marker #2
                        {
                            // full line is now available, parse it
                                                        
                            boost::regex re1("^\\\"(.+)\\\"-\\\".*\\\\(\\S+)\\\",.*$");
                            boost::cmatch matches1;                
                            if (boost::regex_match(line.c_str(), matches1, re1))
                            {
                                // match found
                                string ms1(matches1[1].first, matches1[1].second); // source name
                                string ms2(matches1[2].first, matches1[2].second); // target name
                                
                                binary_info b_info;
                                b_info.directory = tempdir;
                                b_info.filename = ms1;

                                GetImportTableWithPetran(_petran_location, b_info);
                                
                                // make sure that Petran succeeded for this file since we don't do any file
                                // extension checks when parsering the file
                                if (b_info.binary_format != UNKNOWN)
                                {
                                    // print name of the destination binary
                                    cerr << ms2 << endl;
                                
                                    b_info.directory = "";
                                    b_info.filename = ms2;
    
                                    // get statistics of the file and set the modification time
                                    struct stat stat_p;
                                    stat((tempdir + ms1).c_str(), &stat_p);
                                    b_info.mod_time = stat_p.st_mtime;
                                    
                                    // create a new entry to list of binary files
                                    sis_target.binaries.push_back( b_info );                                      
                                }
                                              
                            }
                            
                            // clear the buffer since we start scanning another line
                            line = "";
                        }                        
                    //}
                    else
                    {
                        char c(c1);  // simple unicode to ascii conversion, just ignore c2
                        line += c;  // append the char to end of the line      
                    }    
                 }       
            }
            else
            {
                pkgf.close();
                RemoveDirectoryWithAllFiles(tempdir);
                cerr << "ERROR: Pkg file " + pkgfile_location << " is not supported, check -sisfiles parameter" << endl;
                exit(EXIT_PKG_FILE_CANNOT_OPEN_FOR_READING); 
            } 
        
        }
        else
        {
      		RemoveDirectoryWithAllFiles(tempdir);
     		cerr << "ERROR: Cannot open " + pkgfile_location << " for reading, check -sisfiles parameter" << endl;
    		exit(EXIT_PKG_FILE_CANNOT_OPEN_FOR_READING); 
        }                

        // close handles and clear any temp files        
        pkgf.close();
        RemoveDirectoryWithAllFiles(tempdir);
    }    

    // make sure that the cache directory exists
    MkDirAll(sis_target.cache_dir); 
        
    // write the dependencies cache of the sis files
    WriteDataToDependenciesCacheFile(sis_target);
    
    // append to targets
    _targets.push_back(sis_target);
    
    cerr << endl;

}

// ----------------------------------------------------------------------------------------------------------
    
    
