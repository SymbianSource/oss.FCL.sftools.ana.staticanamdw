/*
* Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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
* Description:  Header file of Appdep
*
*/


#ifndef __APPDEP_HPP__
#define __APPDEP_HPP__


#if (defined(_MSC_VER) && (_MSC_VER < 1400))
  #error "ERROR: Minimum supported version of Visual C++ is 8.0 (2005)."
#endif

#ifdef _MSC_VER
  #pragma message("IMPORTANT: You can use Visual C++ to aid development, but please compile the releasable executable with MinGW/MSYS !!!")
  #pragma warning(disable:4267) // 'var' : conversion from 'size_t' to 'type', possible loss of data
  #pragma warning(disable:4996) // 'function': was declared deprecated
  #define _CRT_SECURE_NO_DEPRECATE
  #ifndef WIN32
    #error "ERROR: Only Win32 target supported!"
  #endif
#endif


#include <algorithm>
#include <string>
#include <cctype>
#include <fstream>
#include <iostream>
#include <vector>
#include <sstream>
#include <time.h>
#include <sys/stat.h>
#include <stdio.h>
#include <boost/regex.hpp>

#ifdef _MSC_VER
  #include <direct.h>
  #define S_ISDIR(m)  ((m) & S_IFDIR)
#else
  #include <dirent.h>
#endif

using namespace std;

#define APPDEP_VERSION "2.2"
#define APPDEP_DATE "27th Nov 2009"
#define APPDEP_COPYRIGHT_YEARS "2001-2009"
#define CACHE_ST_FILENAME "appdep-cache_symbol_tables.txt"
#define CACHE_DEP_FILENAME "appdep-cache_dependencies.txt"
#define CACHE_ST_HEADER "appdep symbol tables cache version: 101"
#define CACHE_DEP_HEADER "appdep dependencies cache version: 101"
#define CACHE_FOOTER "#end"
#define CACHE_COMMENT_CHAR '#'
#define CACHE_SEP "|"
#define TEMP_FILENAME "appdep-temp.txt"
#define SIS_TEMP_DIR "sistemp"
#define UNKNOWN "unknown"
#define NOT_VALID "not valid"

#ifdef WIN32
  #define DIR_SEPARATOR "\\"
  #define DIR_SEPARATOR2 '\\'
  #define DEFAULT_CACHE_DIR "epoc32\\tools\\s60rndtools\\appdep\\cache\\"
  #define DUMPSIS_LOCATION "epoc32\\tools\\dumpsis.exe"
  #define PETRAN_LOCATION "epoc32\\tools\\petran.exe" // used for GCC toolchain
  #define ELFTRAN_LOCATION "epoc32\\tools\\elftran.exe" // used for other toolchains
  #define EPOC32_RELEASE "epoc32\\release\\"
  #define GCC_NM_EXE "nm.exe"
  #define GCCE_NM_EXE "arm-none-symbianelf-nm.exe"
  #define GCCE_READELF_EXE "arm-none-symbianelf-readelf.exe"
  #define GCCE_CFILT_EXE "arm-none-symbianelf-c++filt.exe"
  #define RVCT_ARMAR_EXE "armar.exe"
  #define RVCT_FROMELF_EXE "fromelf.exe"
  #define CERR_TO_NULL "2>NUL"
  #define DIR_COMMAND "dir /b"
  #define DEL_ALL_COMMAND "del /F /S /Q"
#else
  #define DIR_SEPARATOR "/"
  #define DIR_SEPARATOR2 '/'
  #define DEFAULT_CACHE_DIR "epoc32/tools/s60rndtools/appdep/cache/"
  #define DUMPSIS_LOCATION "epoc32/tools/dumpsis"
  #define PETRAN_LOCATION "epoc32/tools/petran"   // used for GCC toolchain
  #define ELFTRAN_LOCATION "epoc32/tools/elftran" // used for other toolchains
  #define EPOC32_RELEASE "epoc32/release/"
  #define GCC_NM_EXE "nm"
  #define GCCE_NM_EXE "arm-none-symbianelf-nm"
  #define GCCE_READELF_EXE "arm-none-symbianelf-readelf"
  #define GCCE_CFILT_EXE "arm-none-symbianelf-c++filt"
  #define RVCT_ARMAR_EXE "armar"
  #define RVCT_FROMELF_EXE "fromelf"
  #define CERR_TO_NULL "2>/dev/null"
  #define DIR_COMMAND "ls --format=single-column"
  #define DEL_ALL_COMMAND "rm -f -R"
  #define _mkdir(X) mkdir(X, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH)
  #define _rmdir rmdir
  #define _unlink unlink
  #define _popen popen
  #define _pclose pclose
#endif

enum ExitStates
{
    EXIT_NORMAL = 0,
    EXIT_INVALID_ARGUMENT,
    EXIT_NO_TARGETS,
    EXIT_WRONG_USAGE,
    EXIT_CANNOT_CREATE_OUTPUT_FILE,
    EXIT_TOOLCHAIN_NOT_FOUND,
    EXIT_TARGETDIR_NOT_FOUND,
    EXIT_CFILT_NOT_FOUND,
    EXIT_PETRAN_NOT_FOUND,
    EXIT_TOOLCHAIN_NOT_FOUND_FROM_PATH,
    EXIT_PATH_VARIABLE_NOT_FOUND,
    EXIT_ONLY_SUPPORTED_IN_WIN32,
    EXIT_CANNOT_WRITE_TO_TEMP_FILE,
    EXIT_ORDINAL_LIST_CORRUPTED,
    EXIT_COMPONENT_NOT_FOUND,
    EXIT_INVALID_ORDINAL,
    EXIT_CANNOT_WRITE_TO_CACHE_FILE,
    EXIT_CANNOT_OPEN_STATIC_DEPENDENCIES_TXT,
    EXIT_OPENED_STATIC_DEPENDENCIES_TXT_NOT_SUPPORTED,
    EXIT_DUMPSIS_NOT_FOUND,
    EXIT_SIS_FILE_NOT_FOUND,
    EXIT_SIS_FILE_NOT_SUPPORTED,
    EXIT_NOT_SIS_FILE,
    EXIT_SIS_FILE_CANNOT_OPEN_FOR_READING,
    EXIT_TEMP_SIS_FILE_CANNOT_OPEN_FOR_WRITING,
    EXIT_NO_PKG_FILE_FOUND,
    EXIT_PKG_FILE_CANNOT_OPEN_FOR_READING,
    EXIT_PKG_FORMAT_NOT_SUPPORTED
};

struct ordinal
{
    unsigned int funcpos;
    string funcname;

    ordinal(unsigned int fp, string fn)
    {
       funcpos = fp;
       funcname = fn;
    }
};

struct import
{
    unsigned int funcpos;
    string funcname;
    bool is_vtable;
    unsigned int vtable_offset;
};

struct dependency
{
    string filename;
    vector<import> imports;
};

struct binary_info
{
    string directory;
    string filename;
    string binary_format;
    unsigned long file_size;
    string uid1;
    string uid2;
    string uid3;
    string secureid;
    string vendorid;
    unsigned long capabilities;
    unsigned long min_heap_size;
    unsigned long max_heap_size;
    unsigned long stack_size;
    time_t mod_time;
    vector<dependency> dependencies;
};

struct import_library_info
{
    string directory;
    string filename;
    time_t mod_time;
    vector<string> symbol_table;
};

struct target
{
    string name;
    string release_dir;
    string release_lib_dir;
    string release_bin_dir;
    string cache_dir;
    string st_cache_path;
    string dep_cache_path;
    bool cache_files_valid;
    vector<string> lib_files;
    vector<string> bin_files;
    vector<import_library_info> import_libraries;
    vector<binary_info> binaries;
};


// global variables
extern bool _cl_use_gcc;
extern bool _cl_use_gcce;
extern bool _cl_use_rvct;
extern bool _cl_generate_clean_cache;
extern bool _cl_update_cache;
extern bool _cl_use_libs;
extern bool _cl_show_ordinals;
extern bool _cl_use_udeb;
extern bool _cl_print_debug;
extern bool _some_cache_needs_update;

extern string _cl_toolsdir;
extern string _cl_cachedir;
extern string _cl_releasedir;
extern string _cl_targets;
extern string _cl_cfiltloc;
extern string _cl_outputfile;
extern string _cl_configfile;
extern string _cl_sisfiles;
extern string _cl_usestaticdepstxt;
extern string _cl_properties;
extern string _cl_staticdeps;
extern string _cl_dependson;
extern string _cl_showfunctions;
extern string _cl_usesfunction;

extern string _gcc_nm_location;
extern string _gcce_nm_location;
extern string _gcce_readelf_location;
extern string _gcce_cfilt_location;
extern string _rvct_armar_location;
extern string _rvct_fromelf_location;
extern string _rvct_cfilt_location;
extern string _petran_location;
extern string _dumpsis_location;
extern string _tempfile_location;
extern string _target_mode;

extern vector<target> _targets;
extern vector<binary_info> _all_binary_infos;
extern vector<import_library_info> _all_import_library_infos;
extern vector<import_library_info> _changed_import_libraries;
extern vector<string> _sisfiles;

extern unsigned int _current_progress;
extern unsigned int _current_progress_percentage;
extern unsigned int _max_progress;

extern ofstream _outputf;


// from appdep_otherfunc.cpp
void ParseCommandLineParameters(int argc, char* argv[]);
void ShowCommandLineOptionsAndExit();
void DoInitialChecksAndPreparations();
void ParseTargets();
void DoCacheGenerationChecksAndPreparations();
void GetToolsPathFromEnvironmentVariable();
void FindImportLibrariesAndBinariesFromReleases();
void GetFileNamesFromDirectory(const string& directory, const string& filter, vector<string>& resultset);
void SetAndCheckPetranPath();

// from appdep_utils.cpp
void PrintOutputLn(const string& s);
void MakeSureTrailingDirectoryMarkerExists(string& path);
bool FileExists(const string& path);
bool DirectoryExists(const string& path);
bool RemoveFile(const string& path);
bool RemoveDirectoryWithAllFiles(const string& path);
string LowerCase(const string& s);
string Int2Str(int value);
int Str2Int(const string& s);
void MkDirAll(const string& path);
string& TrimRight(string& s);
string& TrimLeft(string& s);
string& TrimAll(string& s);
int StringICmp(const string& s1, const string& s2);
int StringICmpFileNamesWithoutExtension(const string& s1, const string& s2);
void InsertQuotesToFilePath(string& s);
bool ExecuteCommand(const string& command, vector<string>& resultset);
bool TimestampsMatches(const time_t& orginal_time, const time_t& new_time);
void ShowProgressInfo(unsigned int& current_progress_percentage, unsigned int& current_progress, unsigned int& max_progress, bool print_initial_value);

// from appdep_getters.cpp
void GetImportTableWithPetran(const string& petran_location, binary_info& b_info);
bool ImportFunctionsHasSameOrdinal(import imp1, import imp2);
void GetSymbolTableWithNM(const string& nm_location, const string& lib_directory, const string& lib_name, vector<string>& symbol_table);
void GetSymbolTableWithReadelf(const string& readelf_location, const string& cfilt_location, const string& lib_directory, const string& lib_name, vector<string>& symbol_table);
void GetSymbolTableWithArmar(const string& armar_location, const string& cfilt_location, const string& lib_directory, const string& lib_name, vector<string>& symbol_table);
void GetSymbolTableWithFromelf(const string& fromelf_location, const string& cfilt_location, const string& lib_directory, const string& lib_name, vector<string>& symbol_table);
void ConvertOrdinalListIntoSymbolTable(const vector<ordinal>& ordinals, vector<string>& symbol_table, const string& lib_path);
void DemangleOrdinalsInSymbolTable(const string& cfilt_location, vector<string>& symbol_table);
bool OrdinalCompare(const ordinal& left, const ordinal& right);

// from appdep_cache.cpp
void ReadDataFromSymbolTablesCache(target& a_target);
void ReadDataFromDependenciesCache(target& a_target);
void GetDataFromImportTables(target& a_target);
void GetDataFromBinaries(target& a_target);
void WriteDataToSymbolTableCacheFile(const target& a_target);
void WriteDataToDependenciesCacheFile(const target& a_target);

// from appdep_statdeps.cpp
void GetDataFromStaticDependenciesTxt();

// from appdep_sisfiles.cpp
void DoInitialChecksAndPreparationsForSisFiles();
void AnalyseSisFiles();

// from appdep_analysis.cpp
void DisplayProperties(const string& binary_name);
void DisplayStaticDependencies(const string& binary_name);
void DisplayDependents(const string& binary_name);
void DisplayFunctions(const string& binary_name);
void DisplayUsesFunction(const string& function_name);


#endif // __APPDEP_HPP__
