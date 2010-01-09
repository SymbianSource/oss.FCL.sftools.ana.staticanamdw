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
* Description:  Misc utility functions 
*
*/


#include "appdep.hpp"

// ----------------------------------------------------------------------------------------------------------

void PrintOutputLn(const string& s)
{
    // check if printing to a file or directory to STDOUT
    if (!_cl_outputfile.empty())
    {
        _outputf << s << endl;    
    }
    else
    {
        cout << s << endl;
    }
}

// ----------------------------------------------------------------------------------------------------------

void MakeSureTrailingDirectoryMarkerExists(string& path)
{
	if (!path.empty() && path.at(path.length()-1) != DIR_SEPARATOR2)
        {
		path.insert(path.length(), DIR_SEPARATOR);
        }
}

// ----------------------------------------------------------------------------------------------------------

bool FileExists(const string& path)
{
    if (!path.empty())
    {
        struct stat stat_p;
        if (stat(path.c_str(), &stat_p) == 0)
            return !S_ISDIR(stat_p.st_mode);  // return true if not a directory
        else
            return false;  // cannot find entry
    }
    else
        return false;
}

// ----------------------------------------------------------------------------------------------------------

bool DirectoryExists(const string& path)
{
    if (!path.empty())
    {
        string temp_path = path;
        
        // remove trailing directory marker if exists
        if (path.at(path.length()-1) == DIR_SEPARATOR2)
            temp_path = path.substr(0, path.length()-1);
            
        struct stat stat_p;
        if (stat(temp_path.c_str(), &stat_p) == 0)
            return S_ISDIR(stat_p.st_mode);  // return true if a directory
        else
            return false;  // cannot find entry
    }
    else
        return false;
}

// ----------------------------------------------------------------------------------------------------------

bool RemoveFile(const string& path)
{
    return _unlink(path.c_str()) == 0;
}

// ----------------------------------------------------------------------------------------------------------

bool RemoveDirectoryWithAllFiles(const string& path)
{
    string temp_path = path;
    MakeSureTrailingDirectoryMarkerExists(temp_path);
    
    // remove all files in the directory via OS call
    string del_command = DEL_ALL_COMMAND;
    string cmd = del_command + " " + temp_path + "* " + CERR_TO_NULL;
        
    vector<string> tempVector;
    ExecuteCommand(cmd, tempVector);
    
    // finally tries to remove the directory, fails if not empty
    return _rmdir(path.c_str()) == 0;
}

// ----------------------------------------------------------------------------------------------------------

string LowerCase(const string& s)
{
	char* buf = new char[s.length()];
	s.copy(buf, s.length());
	
	for(unsigned int i = 0; i < s.length(); i++)
		buf[i] = tolower(buf[i]);
	
	string r(buf, s.length());
	delete buf;
	return r;
}

// ----------------------------------------------------------------------------------------------------------

void MkDirAll(const string& path)
{
    if (!path.empty() && !DirectoryExists(path))
    {
        string target_path = path;
        
        // make sure that the directory has a trailing directory marker
        MakeSureTrailingDirectoryMarkerExists(target_path);
        
        // loop through each character in the string and try to find directory delimeters
        for (unsigned int i=0; i<target_path.length(); i++)
        {
            string::size_type pos = target_path.find(DIR_SEPARATOR, i);

            if (pos != string::npos)
            {
                // construct the base directory name
                string base_directory = target_path.substr(0, pos+1);
                
                if (!DirectoryExists(base_directory))
                {
                    _mkdir(base_directory.c_str());    
                }
                
                i=pos;
            }    
        }
    }
}

// ----------------------------------------------------------------------------------------------------------

bool ExecuteCommand(const string& command, vector<string>& resultset)
{
    // note, cannot use compiler parameters "-std=c++98" because of popen/pclose
    // also cannot compile this code is MSVC because usage of popen/pclose

    FILE* fp;
    char buffer[1024];
    string tempstr;

    resultset.clear();

    if ((fp = _popen(command.c_str(), "r")) == NULL)
    {    
        return false;
    }

    while (fgets(buffer, sizeof(buffer), fp))
    {
        tempstr = buffer;
        resultset.push_back(tempstr.substr(0, tempstr.size()-1));  
    }   

    _pclose(fp);

    return true;
}

// ----------------------------------------------------------------------------------------------------------

string& TrimRight(string& s)
{
	int pos(s.size());
	for (; pos && (s[pos-1]==' ' || s[pos-1]=='\t'); --pos);
	s.erase(pos, s.size()-pos);
	return s;
}

// ----------------------------------------------------------------------------------------------------------

string& TrimLeft(string& s)
{
	int pos(0);
	for (; s[pos]==' ' || s[pos]=='\t'; ++pos);
	s.erase(0, pos);
	return s;
}

// ----------------------------------------------------------------------------------------------------------

string& TrimAll(string& s)
{
	return TrimLeft(TrimRight(s));
}

// ----------------------------------------------------------------------------------------------------------

int StringICmp(const string& s1, const string& s2)
{
    string ss1 = LowerCase(s1);
    string ss2 = LowerCase(s2);
    
    return ss1.compare(ss2);
}

// ----------------------------------------------------------------------------------------------------------

int StringICmpFileNamesWithoutExtension(const string& s1, const string& s2)
{
    // remove extension and then compare
    string ss1;
    string ss2;
    
    string::size_type dot_pos1 = s1.find_last_of('.');
    if (dot_pos1 == string::npos)
        ss1 = s1;
    else
        ss1 = s1.substr(0, dot_pos1);    

    string::size_type dot_pos2 = s2.find_last_of('.');
    if (dot_pos2 == string::npos)
        ss2 = s2;
    else
        ss2 = s2.substr(0, dot_pos2);
    
    return StringICmp(ss1, ss2);
}

// ----------------------------------------------------------------------------------------------------------

bool TimestampsMatches(const time_t& orginal_time, const time_t& new_time)
{
	// allow two second difference to both directions
    if (new_time-2 <= orginal_time && orginal_time <= new_time+2)
        return true;
    else
        return false;
}

// ----------------------------------------------------------------------------------------------------------

string Int2Str(int value)
{
    ostringstream os;
    if (os << value)
        return os.str();
    else    
        return ""; 
}

// ----------------------------------------------------------------------------------------------------------

int Str2Int(const string& s)
{
    int res(0);

    // return 0 for empty string
    if (s.empty())
    {
    }
    
    // hex conversion if the string begings with 0x...
    else if (s.length() >= 3 && s.at(0) == '0' && s.at(1) == 'x')
    {        
        istringstream is(s);
        is >> hex >> res;
        if(!is || !is.eof())
            res = 0;
    }
    
    // normal integer
    else  
    {        
        istringstream is(s);
        is >> res;
        if(!is || !is.eof())
            res = 0;
    }    

    return res;
}

// ----------------------------------------------------------------------------------------------------------

void InsertQuotesToFilePath(string& s)
{
    // example C:\Program Files\do something.exe -> C:\"Program Files"\"do something.exe"
    
    bool firstBacklashFound = false;
    bool anyQuoteInserted = false;

    if (!s.empty())
    {
        int s_length = s.length();

        for (int i=0; i<s_length; i++)
        {
            string::size_type pos = s.find(DIR_SEPARATOR, i);
            
            if (pos != string::npos)
            {
                if (!firstBacklashFound)
                {
                    // replace \ -> \"
                    s.insert(pos+1, "\"");
                    
                    anyQuoteInserted = true;
                    firstBacklashFound = true;
                    s_length++;
                    i = pos+1;
                }
                else
                {
                    // replace \ -> "\"
                    s.insert(pos, "\"");
                    s.insert(pos+2, "\"");

                    anyQuoteInserted = true;                        
                    s_length += 2;
                    i = pos+2;
                }
            }          
           
            if (i>255)
                return;  // something went wrong..
        }

        // append extra quote to the end if needed        
        if (anyQuoteInserted)
            s.insert(s.length(), "\"");
    }
}

// ----------------------------------------------------------------------------------------------------------

void ShowProgressInfo(unsigned int& current_progress_percentage, unsigned int& current_progress, unsigned int& max_progress, bool print_initial_value)
{
    if (print_initial_value)
    {
        cerr << "(  0% complete)";
    }
    else
    {    
        current_progress++;

        unsigned int temp_percentage = int( (double) current_progress / (double) max_progress * 100 );
        
        if (temp_percentage > current_progress_percentage)
        {
            current_progress_percentage = temp_percentage;
            cerr << "\b\b\b\b\b\b\b\b\b\b\b\b\b\b";
            
            if (current_progress_percentage < 10)
                cerr << "  ";
            else if (current_progress_percentage < 100)
                cerr << " ";                
            cerr << current_progress_percentage << "% complete)";  
        }            
    }    
}


// ----------------------------------------------------------------------------------------------------------
