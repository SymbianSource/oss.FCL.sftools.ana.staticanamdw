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
* Description:  Main entry of Appdep 
*
*/


#include "appdep.hpp"

// init globals
bool _cl_use_gcc = false;
bool _cl_use_gcce = false;
bool _cl_use_rvct = false;
bool _cl_generate_clean_cache = false;
bool _cl_update_cache = false;
bool _cl_use_libs = false;
bool _cl_show_ordinals = false;
bool _cl_use_udeb = false;
bool _cl_print_debug = false;
bool _some_cache_needs_update = false;

string _cl_toolsdir = "";
string _cl_cachedir = "";
string _cl_releasedir = "";
string _cl_targets = "";
string _cl_cfiltloc = "";
string _cl_outputfile = "";
string _cl_configfile = "";
string _cl_sisfiles = "";
string _cl_usestaticdepstxt = "";
string _cl_properties = "";
string _cl_staticdeps = "";
string _cl_dependson = "";
string _cl_showfunctions = "";
string _cl_usesfunction = "";

string _gcc_nm_location = "";
string _gcce_nm_location = "";
string _gcce_readelf_location = "";
string _gcce_cfilt_location = "";
string _rvct_armar_location = "";
string _rvct_fromelf_location = "";
string _rvct_cfilt_location = "";
string _petran_location = "";
string _dumpsis_location = "";
string _tempfile_location = "";
string _target_mode = "";

vector<target> _targets;
vector<binary_info> _all_binary_infos;
vector<import_library_info> _all_import_library_infos;
vector<import_library_info> _changed_import_libraries;
vector<string> _sisfiles;

unsigned int _current_progress = 0;
unsigned int _current_progress_percentage = 0;
unsigned int _max_progress = 0;

ofstream _outputf;

int _CRT_glob = 0; // globbing not supported 

// ----------------------------------------------------------------------------------------------------------

int main(int argc, char* argv[])
{
    // parse command line arguments
    ParseCommandLineParameters(argc, argv);

    // read from StaticDependencies.txt if in use
    if (!_cl_usestaticdepstxt.empty())
    {
        GetDataFromStaticDependenciesTxt();
    }
    
    // otherwise do normal cache operations
    else
    {
        // first do some checks
        DoInitialChecksAndPreparations();
        ParseTargets();

        // checks for sis files if in use
        if (!_cl_sisfiles.empty())
            DoInitialChecksAndPreparationsForSisFiles(); 
        
        // try to read data from caches
        if (!_cl_generate_clean_cache)
        {
            for (unsigned int i=0; i<_targets.size(); i++) // loop each target
            {
                if (_targets.at(i).cache_files_valid)
                {
                    ReadDataFromSymbolTablesCache(_targets.at(i));
                    
                    if (_targets.at(i).cache_files_valid)    
                        ReadDataFromDependenciesCache(_targets.at(i));
                    else
                        _some_cache_needs_update = true;        
                }
                else
                {
                    _some_cache_needs_update = true;    
                }
            }         
        }
    }

    // check if cache needs generation or update
    if (_cl_generate_clean_cache || _cl_update_cache || _some_cache_needs_update)
    {    
        // before starting generating cache, we need more checks that user given params are correct
        DoCacheGenerationChecksAndPreparations();


        if (_cl_generate_clean_cache)
            cerr << "Generating cache files at " << _cl_cachedir << " ";
        else
            cerr << "Updating cache files at " << _cl_cachedir << " ";        


        // get lists of files from the directories
        FindImportLibrariesAndBinariesFromReleases();


        // init progress values    
        if (_max_progress == 0)
            _max_progress = 1;

        if (_cl_print_debug)
            cerr << endl;
        else
            ShowProgressInfo(_current_progress_percentage, _current_progress, _max_progress, true);


        // get import libaries of each target and then write that data to the caches
        for (unsigned int i=0; i<_targets.size(); i++) // loop each target
        {
            GetDataFromImportTables(_targets.at(i));
            
            // write data only if current file is not valid
            if (!_targets.at(i).cache_files_valid)
            {
                WriteDataToSymbolTableCacheFile(_targets.at(i));
            }

            // append all data to common vector
            for (unsigned int j=0; j<_targets.at(i).import_libraries.size(); j++)  // loop all binaries in one target
            {
               _all_import_library_infos.push_back(_targets.at(i).import_libraries.at(j));
            }

            // clear the original vector to save RAM since it is not needed anymore
            _targets.at(i).import_libraries.clear();
        }

        // get dependency data and write it to the cache files
        for (unsigned int i=0; i<_targets.size(); i++) // loop each target
        {
            GetDataFromBinaries(_targets.at(i));
            
            if (!_targets.at(i).cache_files_valid)  // only write cache if it needs updating
            {
                WriteDataToDependenciesCacheFile(_targets.at(i));    
            }
            
        }

        cerr << endl;
    }
    
    // if sis files in use and not done any previous operations, some things must be done
    else if (!_cl_sisfiles.empty()) 
    {
        // check Petran can be found
        SetAndCheckPetranPath();

        for (unsigned int i=0; i<_targets.size(); i++) // loop each target
        {
            // append all data to common vector
            for (unsigned int j=0; j<_targets.at(i).import_libraries.size(); j++)  // loop all import libraries in one target
            {
               // get a binary info data
               _all_import_library_infos.push_back(_targets.at(i).import_libraries.at(j));
            }
            
            // clear the original vector to save RAM since it is not needed anymore
            _targets.at(i).import_libraries.clear();
        }
    }    
    
    
    // include sis files to analysis if in use
    if (!_cl_sisfiles.empty())
        AnalyseSisFiles();


    // do the analysis
    if (_cl_properties.empty() && _cl_staticdeps.empty() && _cl_dependson.empty() && _cl_showfunctions.empty() && _cl_usesfunction.empty())
    {
        cerr << "Nothing to do." << endl;    
    }
	else
	{
        // copy binary_info vectors to a single one
        if (_cl_usestaticdepstxt.empty())
        {
            for (unsigned int i=0; i<_targets.size(); i++)  // loop all targets
            {
                for (unsigned int j=0; j<_targets.at(i).binaries.size(); j++)  // loop all binaries in one target
                {
                   // get a binary info data
                   _all_binary_infos.push_back(_targets.at(i).binaries.at(j));
                }
                
                // clear the original vector to save RAM
                _targets.at(i).binaries.clear();
            }            
        }

        if (!_cl_properties.empty())
        {
            // show properties of the binary file
            DisplayProperties(_cl_properties);
        } 

        if (!_cl_staticdeps.empty())
        {
            // determine all static dependencies of selected component  
            DisplayStaticDependencies(_cl_staticdeps);      
        }        

        if (!_cl_dependson.empty())
        {
            // list all components that depends on selected component
            DisplayDependents(_cl_dependson);  
        }  

        if (!_cl_showfunctions.empty())
        {
            // determine all functions that are included / supported in selected component
            DisplayFunctions(_cl_showfunctions);  
        }  
        
        if (!_cl_usesfunction.empty())
        {
            // list all components that are using selected function   
            DisplayUsesFunction(_cl_usesfunction);
        }
    }
                
     
    // close output file
    if (_outputf.is_open())
    {   
        _outputf.close();
    }

    // delete the temporary file
    if (!_tempfile_location.empty())
        RemoveFile(_tempfile_location);
 
	return EXIT_NORMAL;
}

// ----------------------------------------------------------------------------------------------------------

