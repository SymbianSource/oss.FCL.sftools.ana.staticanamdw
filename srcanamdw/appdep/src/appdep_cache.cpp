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
* Description:  Cache handling routines 
*
*/


#include "appdep.hpp"


// ----------------------------------------------------------------------------------------------------------

void ReadDataFromSymbolTablesCache(target& a_target)
{
	string line;
	
	ifstream symtabcachef(a_target.st_cache_path.c_str());
    if (!symtabcachef.is_open())
    {
        cerr << "Warning: Regenerating corrupted cache of target " << a_target.name << endl;
        a_target.cache_files_valid = false;
        _some_cache_needs_update = true;
        return;    
    }	
	
	getline(symtabcachef, line);
	if (line != CACHE_ST_HEADER)
    {
        cerr << "Warning: Regenerating corrupted cache of target " << a_target.name  << endl;
        a_target.cache_files_valid = false;  
        _some_cache_needs_update = true;
    }
    else
    {     
        // loop through all lines in the file
        while(!symtabcachef.eof())
        {
            getline(symtabcachef, line);
            
            if (line.length() > 0 && line[0] != CACHE_COMMENT_CHAR)
            {
                // first entry is the directory|filename|modification_time|symbol_table_size , eg
                // x:\epoc32\release\armv5\urel\|avkon.dll|1160666488|178
                string::size_type delim1 = line.find(CACHE_SEP, 0);
                string::size_type delim2 = line.find(CACHE_SEP, delim1+1);
                string::size_type delim3 = line.find(CACHE_SEP, delim2+1);

                import_library_info lib_info;
                lib_info.directory = line.substr(0, delim1);
                lib_info.filename = line.substr(delim1+1, delim2-delim1-1);
                lib_info.mod_time = Str2Int( line.substr(delim2+1, delim3-delim2-1) );
                unsigned int symbol_table_size = Str2Int( line.substr(delim3+1, line.length()-delim3-1) );
                
                // get symbol table
                vector<string> symbol_table; 
                for (unsigned int j=0; j<symbol_table_size; j++)
                {
                    getline(symtabcachef, line);
                    symbol_table.push_back( line );
                }
                
                lib_info.symbol_table = symbol_table;
                
                // append binary info to the vectory
                a_target.import_libraries.push_back( lib_info );
            }            
        }
        
        // check that the last line of the file contains the footer of the cache
        if (line != CACHE_FOOTER)
        {
            cerr << "Warning: Regenerating corrupted cache of target " << a_target.name  << endl;
            a_target.import_libraries.clear();
            a_target.cache_files_valid = false;  
            _some_cache_needs_update = true;
        }
    }
    
    symtabcachef.close();  
}

// ----------------------------------------------------------------------------------------------------------

void ReadDataFromDependenciesCache(target& a_target)
{
    string line;
        	
    // read data from the dependencies cache file
	ifstream depcachef(a_target.dep_cache_path.c_str());
    if (!depcachef.is_open())
    {
        cerr << "Warning: Regenerating corrupted cache of target " << a_target.name << endl;
        a_target.cache_files_valid = false;
        _some_cache_needs_update = true;
        return;    
    }	
	
	getline(depcachef, line);
	if (line != CACHE_DEP_HEADER)
    {
        cerr << "Warning: Regenerating corrupted cache of target " << a_target.name  << endl;
        a_target.cache_files_valid = false;  
        _some_cache_needs_update = true;
    }
    else
    {     
        // loop through all lines in the file
        while(!depcachef.eof())
        {
            getline(depcachef, line);
            
            if (line.length() > 0 && line[0] != CACHE_COMMENT_CHAR)
            {
                // first entry is the directory|filename|binary_format|uid1|uid2|uid3|secureid|vendorid|capabilities|min_heap_size|max_heap_size|stack_size|modification_time|number_of_dependencies , eg
                // x:\epoc32\release\armv5\urel\|about.exe|EPOC Exe for ARMV4 CPU|0x1000007a|0x100039ce|0x10005a22|0x10005a22|0x101fb657|782384|4096|1048576|8192|1160666488|11
                string::size_type delim1 = line.find(CACHE_SEP, 0);
                string::size_type delim2 = line.find(CACHE_SEP, delim1+1);
                string::size_type delim3 = line.find(CACHE_SEP, delim2+1);
                string::size_type delim4 = line.find(CACHE_SEP, delim3+1);
                string::size_type delim5 = line.find(CACHE_SEP, delim4+1);
                string::size_type delim6 = line.find(CACHE_SEP, delim5+1);
                string::size_type delim7 = line.find(CACHE_SEP, delim6+1);
                string::size_type delim8 = line.find(CACHE_SEP, delim7+1);
                string::size_type delim9 = line.find(CACHE_SEP, delim8+1);
                string::size_type delim10 = line.find(CACHE_SEP, delim9+1);
                string::size_type delim11 = line.find(CACHE_SEP, delim10+1);
                string::size_type delim12 = line.find(CACHE_SEP, delim11+1);
                string::size_type delim13 = line.find(CACHE_SEP, delim12+1);

                binary_info b_info;
                b_info.directory = line.substr(0, delim1);
                b_info.filename = line.substr(delim1+1, delim2-delim1-1);
                b_info.binary_format = line.substr(delim2+1, delim3-delim2-1);
                b_info.uid1 = line.substr(delim3+1, delim4-delim3-1);
                b_info.uid2 = line.substr(delim4+1, delim5-delim4-1);
                b_info.uid3 = line.substr(delim5+1, delim6-delim5-1);
                b_info.secureid = line.substr(delim6+1, delim7-delim6-1);
                b_info.vendorid = line.substr(delim7+1, delim8-delim7-1);
                b_info.capabilities = Str2Int( line.substr(delim8+1, delim9-delim8-1) );
                b_info.min_heap_size = Str2Int( line.substr(delim9+1, delim10-delim9-1) );
                b_info.max_heap_size = Str2Int( line.substr(delim10+1, delim11-delim10-1) );
                b_info.stack_size = Str2Int( line.substr(delim11+1, delim12-delim11-1) );
                b_info.mod_time = Str2Int( line.substr(delim12+1, delim13-delim12-1) );
                unsigned int number_of_deps = Str2Int( line.substr(delim13+1, line.length()-delim13-1) );
                
                vector<dependency> deps; 
                for (unsigned int j=0; j<number_of_deps; j++)
                {
                    getline(depcachef, line);
                    
                    // second type entry is filename|number_of_imports , eg
                    // APPARC.DLL|6
                    string::size_type delim1 = line.find(CACHE_SEP, 0);
                    
                    dependency dep;
                    dep.filename = line.substr(0, delim1);
                    unsigned int number_of_imports = Str2Int( line.substr(delim1+1, line.length()-delim1-1) );
                    
                    vector<import> imps;
                    for (unsigned int k=0; k<number_of_imports; k++)
                    {
                        getline(depcachef, line);
                        
                        // third type on entry is funcpos|funcname|is_vtable|vtable_offset, eg
                        // 121|CApaDocument::Capability() const|0|0
                        string::size_type delim1 = line.find(CACHE_SEP, 0);
                        string::size_type delim2 = line.find(CACHE_SEP, delim1+1);
                        string::size_type delim3 = line.find(CACHE_SEP, delim2+1);
                        
                        import imp;
                        imp.funcpos = Str2Int( line.substr(0, delim1) );
                        imp.funcname = line.substr(delim1+1, delim2-delim1-1);
                        imp.is_vtable = Str2Int( line.substr(delim2+1, delim3-delim2-1) );
                        imp.vtable_offset = Str2Int( line.substr(delim3+1, line.length()-delim3-1) );
                        
                        // append to the import info vector
                        imps.push_back( imp );
                    }                     
                    
                    // now we have import info too
                    dep.imports = imps;
                    
                    // append to the deps info vector
                    deps.push_back( dep );
                                    
                }
                // now we have the dep info too
                b_info.dependencies = deps;
                
                // apppend binary info to the vector
                a_target.binaries.push_back( b_info );
            }            
        }

        // check that the last line of the file contains the footer of the cache
        if (line != CACHE_FOOTER)
        {
            cerr << "Warning: Regenerating corrupted cache of target " << a_target.name  << endl;
            a_target.binaries.clear();
            a_target.cache_files_valid = false;  
            _some_cache_needs_update = true;
        }
    }
    depcachef.close();         
}

// ----------------------------------------------------------------------------------------------------------

void GetDataFromImportTables(target& a_target)
{
    // read data from import libraries if needed
    for (unsigned int i=0; i<a_target.lib_files.size(); i++)
    {
        bool is_new_file = true;

        vector<string> symbol_table;

        if (_cl_print_debug)
            cerr << "Processing " << a_target.release_lib_dir << a_target.lib_files.at(i) << "...";

        // if not generating a clean cache, check if this file was already in the cache 
        if (!_cl_generate_clean_cache)
        {
            // first try to find existing file
            bool update_file = false;
            int position = 0;
            
            for (unsigned int j=0; j<a_target.import_libraries.size(); j++)
            {
                // check if names match
                if (StringICmpFileNamesWithoutExtension(a_target.lib_files.at(i), a_target.import_libraries.at(j).filename) == 0)
                {
                    // the file was already found from the cache
                    is_new_file = false;
                    
                    // compare modification times
                    struct stat stat_p;
                    stat((a_target.release_lib_dir + a_target.lib_files.at(i)).c_str(), &stat_p); // get new stats
                    
                    if (!TimestampsMatches(a_target.import_libraries.at(j).mod_time, stat_p.st_mtime))
                    {
                        // time stamps are different so needs to update the file
                        update_file = true;
                        position = j;                         
                    }
                    
                    // there can't be anymore same names, so break the loop anyway
                    break;
                }
            }

            // get the new data
            if (update_file)
            {
                a_target.cache_files_valid = false;  // cache files on disk must be rewritten
                
                import_library_info& lib_info = a_target.import_libraries.at(position);
                lib_info.directory = a_target.release_lib_dir;
                                 
                if (_cl_use_gcc)
                {
                    GetSymbolTableWithNM(_gcc_nm_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                }
                else if (_cl_use_gcce)
                {
                    if (_cl_use_libs)
                    {
                        GetSymbolTableWithNM(_gcce_nm_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                    }
                    else
                    {
                        GetSymbolTableWithReadelf(_gcce_readelf_location, _gcce_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                    }
                }
                else if (_cl_use_rvct)
                {
                    if (_cl_use_libs)
                    {
                        GetSymbolTableWithArmar(_rvct_armar_location, _rvct_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                    }
                    else
                    {
                        GetSymbolTableWithFromelf(_rvct_fromelf_location, _rvct_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                    }
                }
                
                lib_info.symbol_table = symbol_table;
                
                // get statistics of the file and set the modification time
                struct stat stat_p;
                stat((a_target.release_lib_dir + a_target.lib_files.at(i)).c_str(), &stat_p);
                lib_info.mod_time = stat_p.st_mtime;
                
                // record changed import libraries
                _changed_import_libraries.push_back( lib_info );
            }
        }
        
        // this is a new file, get info and append it to the vector
        if (is_new_file)
        {
            a_target.cache_files_valid = false;  // cache files on disk must be rewritten

            // get the symbol tables of the library
            if (_cl_use_gcc)
            {
                GetSymbolTableWithNM(_gcc_nm_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
            }
            else if (_cl_use_gcce)
            {
                if (_cl_use_libs)
                {
                    GetSymbolTableWithNM(_gcce_nm_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                }
                else
                {
                    GetSymbolTableWithReadelf(_gcce_readelf_location, _gcce_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                }
            }
            else if (_cl_use_rvct)
            {
                if (_cl_use_libs)
                {
                    GetSymbolTableWithArmar(_rvct_armar_location, _rvct_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                }
                else
                {
                    GetSymbolTableWithFromelf(_rvct_fromelf_location, _rvct_cfilt_location, a_target.release_lib_dir, a_target.lib_files.at(i), symbol_table);
                }
            }
            
            // get statistics of the file
            struct stat stat_p;
            stat((a_target.release_lib_dir + a_target.lib_files.at(i)).c_str(), &stat_p);
            
            // create a new entry to list of all import libraries
            import_library_info lib_info;
            lib_info.directory = a_target.release_lib_dir;
            lib_info.filename = a_target.lib_files.at(i);
            lib_info.mod_time = stat_p.st_mtime;
            lib_info.symbol_table = symbol_table;
            
            a_target.import_libraries.push_back( lib_info );
        }         
        if (_cl_print_debug)
            cerr << "OK" << endl;
        else
            ShowProgressInfo(_current_progress_percentage, _current_progress, _max_progress, false);
    }
}

// ----------------------------------------------------------------------------------------------------------

void GetDataFromBinaries(target& a_target)
{
    // read data from binaries
    for (unsigned int i=0; i<a_target.bin_files.size(); i++)
    {
        bool is_new_file = true;

        if (_cl_print_debug)
            cerr << "Processing " << a_target.release_bin_dir << a_target.bin_files.at(i) << "...";

        // if not generating a clean cache, check if this file was already in the cache 
        if (!_cl_generate_clean_cache)
        {
            // first try to find existing file
            bool update_file = false;
            int position = 0;
            
            for (unsigned int j=0; j<a_target.binaries.size(); j++)
            {
                // check if names match
                if (StringICmp(a_target.bin_files.at(i).c_str(), a_target.binaries.at(j).filename.c_str()) == 0)
                {
                    is_new_file = false;

                    // compare modification times
                    struct stat stat_p;
                    stat((a_target.release_bin_dir + a_target.bin_files.at(i)).c_str(), &stat_p); // get new stats
                    
                    if (!TimestampsMatches(a_target.binaries.at(j).mod_time, stat_p.st_mtime))
                    {
                        // time stamps are different so needs to update the file
                        update_file = true;
                        position = j;   
                        break; 
                    }
                    
                    // the entry also needs to be updated if any import library which this binary has dependency on has changed
                    for (unsigned int k=0; k<_changed_import_libraries.size(); k++)
                    {
                        for (unsigned int p=0; p<a_target.binaries.at(j).dependencies.size(); p++)
                        {
                            // check for file name match
                            if (StringICmpFileNamesWithoutExtension(a_target.binaries.at(j).dependencies.at(p).filename, _changed_import_libraries.at(k).filename) == 0)
                            {
                                update_file = true;
                                position = j;   
                                break;
                            }
                        }

                        // no need to loop anymore if the file needs update
                        if (update_file)
                            break;
                    }
                    
                    // there can't be anymore same names, so break the loop anyway
                    break;
                }
            }

            // get the new data
            if (update_file)
            {
                a_target.cache_files_valid = false;  // cache files on disk must be rewritten
                
                binary_info& b_info = a_target.binaries.at(position);
                b_info.directory = a_target.release_bin_dir;
                                 
                GetImportTableWithPetran(_petran_location, b_info);
                
                // get statistics of the file and set the modification time
                struct stat stat_p;
                stat((a_target.release_bin_dir + a_target.bin_files.at(i)).c_str(), &stat_p);
                b_info.mod_time = stat_p.st_mtime;
            }
        }

        // this is a new file, get info and append it to the vector
        if (is_new_file)
        {            
            a_target.cache_files_valid = false;  // cache files on disk must be rewritten

            binary_info b_info;
            b_info.directory = a_target.release_bin_dir;
            b_info.filename = a_target.bin_files.at(i);
                             
            GetImportTableWithPetran(_petran_location, b_info);
            
            // get statistics of the file and set the modification time
            struct stat stat_p;
            stat((a_target.release_bin_dir + a_target.bin_files.at(i)).c_str(), &stat_p);
            b_info.mod_time = stat_p.st_mtime;
            
            // create a new entry to list of all binary files
            a_target.binaries.push_back( b_info );
        }
        
        if (_cl_print_debug)
            cerr << "OK" << endl;
        else
            ShowProgressInfo(_current_progress_percentage, _current_progress, _max_progress, false);
    }

}

// ----------------------------------------------------------------------------------------------------------

void WriteDataToSymbolTableCacheFile(const target& a_target)
{
    // open the cache file for writing
    ofstream symtabcachef(a_target.st_cache_path.c_str(), ios::trunc);
    if (!symtabcachef.is_open())
    {
        symtabcachef.close();
		cerr << endl << "ERROR: Cannot open " << a_target.st_cache_path << " for writing!" << endl;
		cerr << "Please check that the directory exists and there are no write permission problems" << endl;
		exit(EXIT_CANNOT_WRITE_TO_CACHE_FILE);
    }
            
    // write data to the cache file
    symtabcachef << CACHE_ST_HEADER << endl;
    
    for (unsigned int i=0; i<a_target.import_libraries.size(); i++)
    {
        vector<string> symbol_table = a_target.import_libraries.at(i).symbol_table;

        symtabcachef << a_target.import_libraries.at(i).directory << CACHE_SEP << a_target.import_libraries.at(i).filename << CACHE_SEP
                     << a_target.import_libraries.at(i).mod_time << CACHE_SEP << symbol_table.size() << endl;
        
        for (unsigned int j=0; j<symbol_table.size(); j++)
        {
            symtabcachef << symbol_table.at(j) << endl;
        }
    }

    // write footer, note that there is no eol char
    symtabcachef << CACHE_FOOTER;

    symtabcachef.close(); 
}

// ----------------------------------------------------------------------------------------------------------

void WriteDataToDependenciesCacheFile(const target& a_target)
{
    // open the cache file for writing
    ofstream depcachef(a_target.dep_cache_path.c_str(), ios::trunc);
    if (!depcachef.is_open())
    {
        depcachef.close();
		cerr << endl << "ERROR: Cannot open " << a_target.dep_cache_path << " for writing!" << endl;
		cerr << "Please check that the directory exists and there are no write permission problems" << endl;
		exit(EXIT_CANNOT_WRITE_TO_CACHE_FILE);
    }

    // write data to the cache file
    depcachef << CACHE_DEP_HEADER << endl;
    
    for (unsigned int i=0; i<a_target.binaries.size(); i++)
    {
        vector<dependency> deps = a_target.binaries.at(i).dependencies;

        depcachef << a_target.binaries.at(i).directory << CACHE_SEP << a_target.binaries.at(i).filename << CACHE_SEP
                  << a_target.binaries.at(i).binary_format << CACHE_SEP << a_target.binaries.at(i).uid1 << CACHE_SEP
                  << a_target.binaries.at(i).uid2 << CACHE_SEP << a_target.binaries.at(i).uid3 << CACHE_SEP
                  << a_target.binaries.at(i).secureid << CACHE_SEP << a_target.binaries.at(i).vendorid << CACHE_SEP
                  << a_target.binaries.at(i).capabilities << CACHE_SEP << a_target.binaries.at(i).min_heap_size << CACHE_SEP
                  << a_target.binaries.at(i).max_heap_size << CACHE_SEP << a_target.binaries.at(i).stack_size << CACHE_SEP
                  << a_target.binaries.at(i).mod_time << CACHE_SEP << deps.size() << endl;
        
        for (unsigned int j=0; j<deps.size(); j++)
        {
            vector<import> imps = deps.at(j).imports;

            depcachef << deps.at(j).filename << CACHE_SEP << imps.size() << endl;
            
            for (unsigned int k=0; k<imps.size(); k++)
            {
                depcachef << imps.at(k).funcpos << CACHE_SEP << imps.at(k).funcname << CACHE_SEP << imps.at(k).is_vtable
                          << CACHE_SEP << imps.at(k).vtable_offset << endl;   
            }
        }
    }

    // write footer, note that there is no eol char
    depcachef << CACHE_FOOTER;

    depcachef.close();  
}

// ----------------------------------------------------------------------------------------------------------


