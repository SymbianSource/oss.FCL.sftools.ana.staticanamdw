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
* Description:  Other non-categorized AppDep functionality 
*
*/


#include "appdep.hpp"

// ----------------------------------------------------------------------------------------------------------

void ParseCommandLineParameters(int argc, char* argv[])
{   
	// loop through the command line parameters and check their usage
	int i=1;
	while (i<argc)
	{
		if (StringICmp("-?", argv[i])==0 ||
		    StringICmp("-h", argv[i])==0 ||
		    StringICmp("--help", argv[i])==0)
		{
			ShowCommandLineOptionsAndExit();
		}
		
		else if (StringICmp("GCC", argv[i])==0)
		{
			_cl_use_gcc = true;
		}
		
		else if (StringICmp("GCCE", argv[i])==0)
		{
			_cl_use_gcce = true;
		}
		
		else if (StringICmp("RVCT", argv[i])==0)
		{
			_cl_use_rvct = true;
		}
	
		else if (StringICmp("--refresh", argv[i])==0)
		{
			_cl_update_cache = true;
		}

		else if (StringICmp("--clean", argv[i])==0)
		{
			_cl_generate_clean_cache = true;
		}
        		
		else if (StringICmp("--uselibs", argv[i])==0)
		{
			_cl_use_libs = true;
		}

		else if (StringICmp("--showordinals", argv[i])==0)
		{
			_cl_show_ordinals = true;
		}

		else if (StringICmp("--useudeb", argv[i])==0)
		{
			_cl_use_udeb = true;
		}

		else if (StringICmp("--debug", argv[i])==0)
		{
			_cl_print_debug = true;
		}
        		
		else if (StringICmp("-tools", argv[i])==0)
		{
			if (i+1<argc) { _cl_toolsdir = argv[i+1]; i++; }
		}

		else if (StringICmp("-cache", argv[i])==0)
		{
			if (i+1<argc) { _cl_cachedir = argv[i+1]; i++; }
		}

		else if (StringICmp("-release", argv[i])==0)
		{
			if (i+1<argc) { _cl_releasedir = argv[i+1]; i++; }
		}

		else if (StringICmp("-targets", argv[i])==0)
		{
			if (i+1<argc) { _cl_targets = argv[i+1]; i++; }
		}
		
		else if (StringICmp("-cfilt", argv[i])==0)
		{
			if (i+1<argc) { _cl_cfiltloc = argv[i+1]; i++; }
		}

		else if (StringICmp("-out", argv[i])==0)
		{
			if (i+1<argc) { _cl_outputfile = argv[i+1]; i++; }
		}		

		else if (StringICmp("-config", argv[i])==0)
		{
			if (i+1<argc) { _cl_configfile = argv[i+1]; i++; }
		}		

		else if (StringICmp("-sisfiles", argv[i])==0)
		{
			if (i+1<argc) { _cl_sisfiles = argv[i+1]; i++; }
		}
		
		else if (StringICmp("-usestaticdepstxt", argv[i])==0)
		{
			if (i+1<argc) { _cl_usestaticdepstxt = argv[i+1]; i++; }
		}
		
		else if (StringICmp("-properties", argv[i])==0)
		{
			if (i+1<argc) { _cl_properties = argv[i+1]; i++; }
		}
		
		else if (StringICmp("-staticdeps", argv[i])==0)
		{
			if (i+1<argc) { _cl_staticdeps = argv[i+1]; i++; }
		}

		else if (StringICmp("-dependson", argv[i])==0)
		{
			if (i+1<argc) { _cl_dependson = argv[i+1]; i++; }
		}        		

		else if (StringICmp("-showfunctions", argv[i])==0)
		{
			if (i+1<argc) { _cl_showfunctions = argv[i+1]; i++; }
		} 		

		else if (StringICmp("-usesfunction", argv[i])==0)
		{
			if (i+1<argc) { _cl_usesfunction = argv[i+1]; i++; }
		} 
		
		// check if the parameter is illegal
        else
        {
            string param = argv[i];
            
            if (!param.empty() && param.at(0) == '-')
            {
        		cerr << "ERROR: Illegal argument: " << param << endl;
        		cerr << "Type appdep -? for help" << endl;
                exit(EXIT_INVALID_ARGUMENT);            
            }   
        }

		i++;
	}    
}

// ----------------------------------------------------------------------------------------------------------

void ShowCommandLineOptionsAndExit()
{
    cout << "AppDep v" << APPDEP_VERSION << " - " << APPDEP_DATE << "\n"
            "Copyright (c) " << APPDEP_COPYRIGHT_YEARS << " Nokia Corporation and/or its subsidiary(-ies). All rights reserved.\n"            
            "\n"
            "Usage: appdep GCC|GCCE|RVCT [parameters] [options] [commands]\n"
            "\n"
            "Where:\n"
            "  GCC                      Use Symbian GCC tool chain\n"
            "  GCCE                     Use CSL ARM tool chain\n"
            "  RVCT                     Use RVCT tool chain\n"
            "\n"
            "Parameters:\n"
            "  -targets A+B+C+...       Target types from release, one or more separated with + without spaces\n"
            "\n"
            "Required parameters when RVCT tool chain is used:\n"
            "  -cfilt FILE              Location FILE of cfilt/c++filt\n"
            "\n"
            "Options:\n"
            "  -tools DIRECTORY         DIRECTORY where the used compiler tool chain is installed\n"
            "  -release DIRECTORY       DIRECTORY where release has been installed\n"
            "  -cache DIRECTORY         DIRECTORY to store cache files\n"
            "  -out FILE                Prints results to FILE\n"
            "  --refresh                Updates the cache, use always after making changes to the release\n"
            "  --clean                  Always creates a clean cache\n"
            "  --uselibs                Always use LIBs instead of DSOs (not valid with GCC)\n"
            "  --showordinals           Show ordinals numbers in output when appropriate\n"
            "  --useudeb                Scan udeb folder for binaries instead of urel\n"
            "  -sisfiles FILE;FILE;...  Includes binaries from sis FILE under analysis\n"
            //"  -usestaticdepstxt FILE   Use platform generated StaticDependencies.txt instead of cache\n"
            //"  --debug                  Print debug messages where available\n"
            "\n"
            "Commands:\n"
            "  -properties FILE         Show properties of binary FILE\n"
            "  -staticdeps FILE         Print all static dependencies of component FILE\n"
            "  -dependson FILE          Print all components that depends on component FILE\n"
            "  -showfunctions FILE      Print all functions used by compoment FILE\n"
            "  -usesfunction NAME       Print all components that are using function NAME (NAME can be full\n"
            "                             function name or in format DLLNAME@ORDINALNUMBER)\n"
            "\n";

	exit(EXIT_NORMAL);
}

// ----------------------------------------------------------------------------------------------------------

void DoInitialChecksAndPreparations()
{
    // make sure the directory names have trailing directory markers
    MakeSureTrailingDirectoryMarkerExists(_cl_toolsdir);
    MakeSureTrailingDirectoryMarkerExists(_cl_cachedir);
    MakeSureTrailingDirectoryMarkerExists(_cl_releasedir);    

    // check that both --refresh and --clean are not defined
    if (_cl_update_cache && _cl_generate_clean_cache)
        {
    	cerr << "Do not specify both --refresh and --clean at the same time!" << endl;
    	cerr << "Type appdep -? for help" << endl;
    	exit(EXIT_WRONG_USAGE);
        }            

    // check if targets parameter has been given
    if (_cl_targets.empty())
    {
    	cerr << "-targets parameter not specified!" << endl;
    	cerr << "Type appdep -? for help" << endl;
    	exit(EXIT_NO_TARGETS);
    }
        
    // if releasedir param is not specified, assign it be the root of current drive
    if (_cl_releasedir.empty())
    {
        _cl_releasedir = DIR_SEPARATOR;
    }
   
    // append default cache location if otherwise the cache parameter is empty
    if (_cl_cachedir.empty())
    {
        _cl_cachedir = _cl_releasedir + DEFAULT_CACHE_DIR;
    }

	// check output file can be created
    if (!_cl_outputfile.empty())
    {
        _outputf.open(_cl_outputfile.c_str(), ios::trunc);
        if (!_outputf.is_open())
        {
            _outputf.close();
    		cerr << "ERROR: Cannot open " << _cl_outputfile << " for writing!" << endl;
    		cerr << "Please check that the directory exists and there are no write permission problems" << endl;
    		exit(EXIT_CANNOT_CREATE_OUTPUT_FILE);
        }            
    }    

    // set target mode
    if (_cl_use_udeb)
        _target_mode = "udeb";
    else
        _target_mode = "urel";

}

// ----------------------------------------------------------------------------------------------------------

void ParseTargets()
{
    // parse A+B+C+... to a vector
    int last_found_plus_pos = -1;
    for (unsigned int i=0; i<_cl_targets.length(); i++)
    {   
        // try to find '+' characters 
        string::size_type plus_pos = _cl_targets.find("+", i);
        
        target new_target;
        
        if (plus_pos == string::npos)
        {
            // could not find the plus character, append last part of the list
            string tmp = _cl_targets.substr(last_found_plus_pos+1, _cl_targets.length()-last_found_plus_pos-1);
            new_target.name = LowerCase(tmp);   
            _targets.push_back(new_target);
            break;
        }
        else
        {
            // found a plus character, append to the list, but needs to check if there are more
            string tmp = _cl_targets.substr(last_found_plus_pos+1, plus_pos-last_found_plus_pos-1);
            new_target.name = LowerCase(tmp);
            
            if (new_target.name.length() > 0)
                _targets.push_back(new_target);
            
            last_found_plus_pos = plus_pos;
            i = last_found_plus_pos;
        }    
    }        
    
    // set more values of targets vector
    for (unsigned int i=0; i<_targets.size(); i++)
    {  
        // set path where release the release can be found, eg z:\epoc32\release\armv5\ .
        _targets.at(i).release_dir = _cl_releasedir + EPOC32_RELEASE + _targets.at(i).name + DIR_SEPARATOR;

        // set path where the import libraries of the release can be found, eg z:\epoc32\release\armv5\lib\ .
        string lib_dir;
        if (_cl_use_gcce || _cl_use_rvct)
            lib_dir = "lib"; // lib dir used in Symbian OS 9.x    
        else
            lib_dir = _target_mode;
        
        _targets.at(i).release_lib_dir = _targets.at(i).release_dir + lib_dir + DIR_SEPARATOR;

        // set path where the binaries of the release can be found, eg z:\epoc32\release\armv5\urel\ .
        _targets.at(i).release_bin_dir = _targets.at(i).release_dir + _target_mode + DIR_SEPARATOR;
        
        // set location of the cache files of this target, eg z:\caches\armv5\urel\xxx.txt 
        _targets.at(i).cache_dir =  _cl_cachedir + _targets.at(i).name + DIR_SEPARATOR + _target_mode + DIR_SEPARATOR;      
        _targets.at(i).st_cache_path = _targets.at(i).cache_dir + CACHE_ST_FILENAME;
        _targets.at(i).dep_cache_path = _targets.at(i).cache_dir + CACHE_DEP_FILENAME;
     
        // check if those cache files exists
        _targets.at(i).cache_files_valid = FileExists(_targets.at(i).st_cache_path) && FileExists(_targets.at(i).dep_cache_path);
    }            
}

// ----------------------------------------------------------------------------------------------------------

void DoCacheGenerationChecksAndPreparations()
{
	if (!_cl_use_gcc && !_cl_use_gcce && !_cl_use_rvct)     
	{	
		cerr << "ERROR: No tool chain defined!" << endl;
		cerr << "Type appdep -? for help" << endl;
        exit(EXIT_WRONG_USAGE);
	}        

	if (_cl_use_rvct && _cl_cfiltloc.empty())     
	{	
		cerr << "ERROR: Specify -cfilt when RVCT is defined!" << endl;
		cerr << "Type appdep -? for help" << endl;
        exit(EXIT_WRONG_USAGE);
	}  

	if ( (_cl_use_gcc && (_cl_use_gcce || _cl_use_rvct)) || (_cl_use_gcce && (_cl_use_gcc || _cl_use_rvct)) ||
         (_cl_use_rvct && (_cl_use_gcc || _cl_use_gcce)) )   
	{	
		cerr << "ERROR: Specify only one tool chain!" << endl;
		cerr << "Type appdep -? for help" << endl;
        exit(EXIT_WRONG_USAGE);
	}     	    

	// make sure the vectors are empty when generating clean cache
	if (_cl_generate_clean_cache)
    {
        for (unsigned int i=0; i<_targets.size(); i++) // loop each target
        {
            _targets.at(i).import_libraries.clear();
            _targets.at(i).binaries.clear();    
        }
    }

    // if tools parameter is empty, try get it from path, otherwise check given parameter
    if (_cl_toolsdir.empty())
    {
        GetToolsPathFromEnvironmentVariable();
    }
    else
    {
        // check the given tools directory parameter is valid
        if (_cl_use_gcc)
        {
            _gcc_nm_location = _cl_toolsdir + GCC_NM_EXE;
    
        	if (!FileExists(_gcc_nm_location))
        	{
        		cerr << "ERROR: Unable to find " + _gcc_nm_location << ", check -tools parameter" << endl;
        		cerr << "Tip: GCC is typically installed to \\epoc32\\gcc\\bin directory" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	}        
    
            // extra quotes needed to prevent white space problems while executing the tool
            InsertQuotesToFilePath(_gcc_nm_location);
        }
    
        else if (_cl_use_gcce)
        {
            _gcce_nm_location = _cl_toolsdir + GCCE_NM_EXE;
            _gcce_readelf_location = _cl_toolsdir + GCCE_READELF_EXE;
            _gcce_cfilt_location = _cl_toolsdir + GCCE_CFILT_EXE;
    
        	if (!FileExists(_gcce_nm_location))
        	{
        		cerr << "ERROR: Unable to find " + _gcce_nm_location << ", check -tools param" << endl;
        		cerr << "Tip: GCCE is typically installed to C:\\Program Files\\CSL Arm Toolchain\\bin" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	} 
    
        	if (!FileExists(_gcce_readelf_location))
        	{
        		cerr << "ERROR: Unable to find " + _gcce_readelf_location << ", check -tools param" << endl;
        		cerr << "Tip: GCCE is typically installed to C:\\Program Files\\CSL Arm Toolchain\\bin" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	} 
    
        	if (!FileExists(_gcce_cfilt_location))
        	{
        		cerr << "ERROR: Unable to find " + _gcce_cfilt_location << ", check -tools param" << endl;
        		cerr << "Tip: GCCE is typically installed to C:\\Program Files\\CSL Arm Toolchain\\bin" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	} 
    
            // extra quotes needed to prevent white space problems while executing the tool
            InsertQuotesToFilePath(_gcce_nm_location);
            InsertQuotesToFilePath(_gcce_readelf_location);
            InsertQuotesToFilePath(_gcce_cfilt_location);
            
        }
    
        else if (_cl_use_rvct)
        {
            _rvct_armar_location = _cl_toolsdir + RVCT_ARMAR_EXE;
            _rvct_fromelf_location = _cl_toolsdir + RVCT_FROMELF_EXE;
    
        	if (!FileExists(_rvct_armar_location))
        	{
        		cerr << "ERROR: Unable to find " + _rvct_armar_location << ", check -tools param" << endl;
        		cerr << "Tip: Check your environment variables to see the directory where RVCT has been installed" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	} 
    
        	if (!FileExists(_rvct_fromelf_location))
        	{
        		cerr << "ERROR: Unable to find " + _rvct_fromelf_location << ", check -tools param" << endl;
        		cerr << "Tip: Check your environment variables to see the directory where RVCT has been installed" << endl;
        		exit(EXIT_TOOLCHAIN_NOT_FOUND);
        	} 
                    
            // extra quotes needed to prevent white space problems while executing the tool
            InsertQuotesToFilePath(_rvct_armar_location);
            InsertQuotesToFilePath(_rvct_fromelf_location);
        }            
    } // else of if (!cl_toolsdir)

        
    // check path of RVCT's cfilt is correct
    if (_cl_use_rvct)
    {
        _rvct_cfilt_location = _cl_cfiltloc;
        
    	if (!FileExists(_rvct_cfilt_location))
    	{
    		cerr << "ERROR: Unable to find " + _rvct_cfilt_location << ", check -cfilt param" << endl;
    		cerr << "Tip: Working cfilt.exe can be found from the same directory where appdep has been installed" << endl;
    		exit(EXIT_CFILT_NOT_FOUND);
    	}    
        
        // extra quotes needed to prevent white space problems while executing the tool
        InsertQuotesToFilePath(_rvct_cfilt_location);
    }


    // check Petran can be found
    SetAndCheckPetranPath();

    // loop all targets
    for (unsigned int i=0; i<_targets.size(); i++)
    {
        // check directories for given targets are valid
        if (!DirectoryExists(_targets.at(i).release_dir))
        {
    		cerr << "ERROR: Directory " << _targets.at(i).release_dir << " not found!" << endl;
    		cerr << "Please check that -targets parameter is valid and you have a full release environment" << endl;
    		exit(EXIT_TARGETDIR_NOT_FOUND);            
        }
        else
        {
            //cerr <<  "NOTE: " << targets.at(i) << " is a valid target in your release" << endl;  
        }

        // make sure that the cache directory exists
        MkDirAll(_targets.at(i).cache_dir);    
    }

	// check that it is possible to create the temporary file under the cache directory
    _tempfile_location = _cl_cachedir + TEMP_FILENAME;
    ofstream tempf(_tempfile_location.c_str(), ios::trunc);
    if (!tempf.is_open())
    {
        tempf.close();
		cerr << "ERROR: Cannot open " << _tempfile_location << " for writing!" << endl;
		cerr << "Please check that the directory exists and there are no write permission problems" << endl;
		exit(EXIT_CANNOT_WRITE_TO_TEMP_FILE);
    }
    else
        tempf.close(); 
        
}

// ----------------------------------------------------------------------------------------------------------

void GetToolsPathFromEnvironmentVariable()
{
   #ifdef WIN32
    // get path environment variable
    const char* env_path = getenv("PATH");
    
    if (env_path != NULL)
    {
        string env_path_str = env_path;
        
        string::size_type previous_delimpos = 0;
        bool match_found(false);
        string test_path;

        for (unsigned int i=0; i<env_path_str.length(); i++)
        {
            // directories in %PATH% are separated with ';'-char
            string::size_type delimpos = env_path_str.find(";", i);
            
            if (delimpos != string::npos)
            {
                // get path
                test_path = env_path_str.substr(previous_delimpos, delimpos-previous_delimpos);
               
                MakeSureTrailingDirectoryMarkerExists(test_path);
                
                // remember found position
                previous_delimpos = delimpos + 1;
                i = delimpos;

                // do check if path is correct
                if (_cl_use_gcc)
                {
                    _gcc_nm_location = test_path + GCC_NM_EXE;
           
                	if (FileExists(_gcc_nm_location))
                	{
                		match_found = true;

                        // extra quotes needed to prevent white space problems while executing the tool
                        InsertQuotesToFilePath(_gcc_nm_location);
                	}        
                }
            
                else if (_cl_use_gcce)
                {
                    _gcce_nm_location = test_path + GCCE_NM_EXE;
                    _gcce_readelf_location = test_path + GCCE_READELF_EXE;
                    _gcce_cfilt_location = test_path + GCCE_CFILT_EXE;
            
                	if (FileExists(_gcce_nm_location) && FileExists(_gcce_readelf_location) && FileExists(_gcce_cfilt_location))
                	{
                		match_found = true;

                        // extra quotes needed to prevent white space problems while executing the tool
                        InsertQuotesToFilePath(_gcce_nm_location);
                        InsertQuotesToFilePath(_gcce_readelf_location);
                        InsertQuotesToFilePath(_gcce_cfilt_location);
                	} 
                }
            
                else if (_cl_use_rvct)
                {
                    _rvct_armar_location = test_path + RVCT_ARMAR_EXE;
                    _rvct_fromelf_location = test_path + RVCT_FROMELF_EXE;
            
                	if (FileExists(_rvct_armar_location) && FileExists(_rvct_fromelf_location))
                	{
                		match_found = true;

                        // extra quotes needed to prevent white space problems while executing the tool
                        InsertQuotesToFilePath(_rvct_armar_location);
                        InsertQuotesToFilePath(_rvct_fromelf_location);
                	} 
                }   

            }          

            // first matching directory found, no need to loop anymore
            if (match_found)
            {
                _cl_toolsdir = test_path;
                cerr << "Tool chain found from %PATH% at " << test_path << endl;
                break;
            }                           
            
            if (i>5000)
                break;  // something went wrong..
        }

        if (!match_found)
        {
            cerr << "ERROR: Cannot find specified compiler toolset from PATH environment" << endl;
            cerr << "Fix PATH environment variable or specify -tools parameter" << endl;
        	exit(EXIT_TOOLCHAIN_NOT_FOUND_FROM_PATH);                      
        }

    }
    else
    {
        cerr << "ERROR: PATH environment variable not available, please specify -tools parameter" << endl;
    	exit(EXIT_PATH_VARIABLE_NOT_FOUND);                
    }
  
   #else

    cerr << "ERROR: Optional -tools parameter is only supported in Windows environment " << endl;
	exit(EXIT_ONLY_SUPPORTED_IN_WIN32);                

   #endif

}

// ----------------------------------------------------------------------------------------------------------

void FindImportLibrariesAndBinariesFromReleases()
{
    // check if analysing .dso or .lib files
    string lib_filter;
    if (_cl_use_gcc || _cl_use_libs)  // for GCC use always .lib files
        lib_filter = "*.lib";
    else
        lib_filter = "*.dso";
            
    for (unsigned int i=0; i<_targets.size(); i++) // loop each target
    {
        // get import libraries
        GetFileNamesFromDirectory(_targets.at(i).release_lib_dir, lib_filter, _targets.at(i).lib_files);
        _max_progress += _targets.at(i).lib_files.size();

        // get binaries
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.app", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.exe", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.dll", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.prt", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.?sy", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.fep", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.agt", _targets.at(i).bin_files);
        GetFileNamesFromDirectory(_targets.at(i).release_bin_dir, "*.fxt", _targets.at(i).bin_files);

        // increase the value of total number of files
        _max_progress += _targets.at(i).bin_files.size();
    }
}

// ----------------------------------------------------------------------------------------------------------

void GetFileNamesFromDirectory(const string& directory, const string& filter, vector<string>& resultset)
{  
    // get list of files from the directory by executing OS specific dir/ls command
    string dir_command = DIR_COMMAND;
    string cmd = dir_command + " \"" + directory + "\"" + filter + " " + CERR_TO_NULL;
        
    vector<string> tempVector;
    ExecuteCommand(cmd, tempVector);
    
    // loop through all returned files
    for (unsigned int i=0; i<tempVector.size(); i++)
    {
        // remove any leading and trailing white spaces
        string file_entry = tempVector.at(i);
        TrimAll(file_entry);
        
        // filter out any unwanted files and append the file to the vector
        if (!file_entry.empty() && file_entry.find("{000a0000}")==string::npos && file_entry.find(".dll55l")==string::npos)
        {
            // strip out any possible directory paths
            string::size_type sep_pos = file_entry.find_last_of(DIR_SEPARATOR);
            if (sep_pos != string::npos)
                file_entry = file_entry.substr(sep_pos+1, file_entry.length()-sep_pos-1); 
                        
            // append entry
            resultset.push_back(file_entry);
        }
    }
}

// ----------------------------------------------------------------------------------------------------------

void SetAndCheckPetranPath()
{
	if(_cl_use_gcc)
	{
    	_petran_location = _cl_releasedir + PETRAN_LOCATION;
	}
	else
	{
    	_petran_location = _cl_releasedir + ELFTRAN_LOCATION;
	}

 	if (!FileExists(_petran_location))
	{
		cerr << "ERROR: Unable to find " + _petran_location << ", check -release param" << endl;
		cerr << "Make sure you have a working development environment" << endl;
		exit(EXIT_PETRAN_NOT_FOUND);
	}
}

// ----------------------------------------------------------------------------------------------------------
