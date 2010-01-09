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
* Description:  Functionality of analysis 
*
*/


#include "appdep.hpp"


// ----------------------------------------------------------------------------------------------------------

void DisplayProperties(const string& binary_name)
{
    bool match_found = false;

    for (unsigned int i=0; i<_all_binary_infos.size(); i++)
    {
        if (StringICmp(_all_binary_infos.at(i).filename.c_str(), binary_name.c_str()) == 0)
        {
            binary_info b_info = _all_binary_infos.at(i);

            PrintOutputLn("Directory:           " + b_info.directory);
            PrintOutputLn("Filename:            " + b_info.filename);
            PrintOutputLn("Binary format:       " + b_info.binary_format);
            PrintOutputLn("UID1:                " + b_info.uid1);
            PrintOutputLn("UID2:                " + b_info.uid2);
            PrintOutputLn("UID3:                " + b_info.uid3);
            
            if (b_info.secureid.length() > 2 && b_info.secureid.at(0)=='0' && b_info.secureid.at(1)=='x')
            {
                PrintOutputLn("Secure ID:           " + b_info.secureid);
                PrintOutputLn("Vendor ID:           " + b_info.vendorid);
                
                vector<string> symbian_caps;
                symbian_caps.push_back("TCB");
                symbian_caps.push_back("CommDD");
                symbian_caps.push_back("PowerMgmt");
                symbian_caps.push_back("MultimediaDD");
                symbian_caps.push_back("ReadDeviceData");
                symbian_caps.push_back("WriteDeviceData");
                symbian_caps.push_back("DRM");
                symbian_caps.push_back("TrustedUI");
                symbian_caps.push_back("ProtServ");
                symbian_caps.push_back("DiskAdmin");
                symbian_caps.push_back("NetworkControl");
                symbian_caps.push_back("AllFiles");
                symbian_caps.push_back("SwEvent");
                symbian_caps.push_back("NetworkServices");
                symbian_caps.push_back("LocalServices");
                symbian_caps.push_back("ReadUserData");
                symbian_caps.push_back("WriteUserData");
                symbian_caps.push_back("Location");
                symbian_caps.push_back("SurroundingsDD");
                symbian_caps.push_back("UserEnvironment");
                
                PrintOutputLn("Capabilities:");
                for (unsigned int x=0; x<symbian_caps.size(); x++)
                {
                    if (b_info.capabilities&(1<<(x&31)))
                        PrintOutputLn("   " + symbian_caps.at(x));
                }
            }
            PrintOutputLn("Min Heap Size:       " + Int2Str(b_info.min_heap_size));
            PrintOutputLn("Max Heap Size:       " + Int2Str(b_info.max_heap_size));
            PrintOutputLn("Stack Size:          " + Int2Str(b_info.stack_size));
            PrintOutputLn("Dll ref table count: " + Int2Str(b_info.dependencies.size()));
            
            match_found = true;
            break;    
        }  
    }
    
    if (!match_found)
    {
        cerr << "Properties: " << binary_name << " not found from the release" << endl;
        exit(EXIT_COMPONENT_NOT_FOUND);
    }         
}

// ----------------------------------------------------------------------------------------------------------

void DisplayStaticDependencies(const string& binary_name)
{
    bool match_found = false;

    for (unsigned int i=0; i<_all_binary_infos.size(); i++)
    {
        if (StringICmp(_all_binary_infos.at(i).filename.c_str(), binary_name.c_str()) == 0)
        {
            PrintOutputLn(binary_name + " - static dependencies:");
            
            vector<dependency> deps = _all_binary_infos.at(i).dependencies;
            
            for (unsigned int j=0; j<deps.size(); j++)
            {
                PrintOutputLn(deps.at(j).filename);    
            } 
        
            match_found = true;
            break;    
        }  
    }
    
    if (!match_found)
    {
        cerr << "Static deps: " << binary_name << " not found from the release" << endl;
        exit(EXIT_COMPONENT_NOT_FOUND);
    }        
}

// ----------------------------------------------------------------------------------------------------------

void DisplayDependents(const string& binary_name)
{
    PrintOutputLn(binary_name + " - components that depends on:");
    
    for (unsigned int i=0; i<_all_binary_infos.size(); i++)
    {
        string component_name = _all_binary_infos.at(i).filename;
        
        vector<dependency> deps = _all_binary_infos.at(i).dependencies;
        
        for (unsigned int j=0; j<deps.size(); j++)
        {
            if (StringICmp(deps.at(j).filename.c_str(), binary_name.c_str()) == 0)
            {
                PrintOutputLn(component_name);                        
                break;    
            }    
        } 
    }      
}

// ----------------------------------------------------------------------------------------------------------

void DisplayFunctions(const string& binary_name)
{
    bool match_found = false;

    for (unsigned int i=0; i<_all_binary_infos.size(); i++)
    {
        if (StringICmp(_all_binary_infos.at(i).filename.c_str(), binary_name.c_str()) == 0)
        {
            PrintOutputLn(binary_name + " - included functions:");
            
            vector<dependency> deps = _all_binary_infos.at(i).dependencies;
            
            for (unsigned int j=0; j<deps.size(); j++)
            {
                vector<import> imps = deps.at(j).imports;
                
                for (unsigned int k=0; k<imps.size(); k++)
                {
                    if (_cl_show_ordinals)
                    {
                        if (imps.at(k).is_vtable)
                            PrintOutputLn(imps.at(k).funcname + "  [virtual table offset by " + Int2Str(imps.at(k).vtable_offset) + "]" + "  [" + deps.at(j).filename + "@" + Int2Str(imps.at(k).funcpos) + "]");    
                        else    
                            PrintOutputLn(imps.at(k).funcname + "  [" + deps.at(j).filename + "@" + Int2Str(imps.at(k).funcpos) + "]");
                    }
                    else
                    {
                        if (imps.at(k).is_vtable)
                            PrintOutputLn(imps.at(k).funcname + "  [virtual table offset by " + Int2Str(imps.at(k).vtable_offset) + "]");    
                        else    
                            PrintOutputLn(imps.at(k).funcname);
                    }
                }    
            } 
        
            match_found = true;
            break;    
        }  
    }
    
    if (!match_found)
    {
        cerr << "Show functions: " << binary_name << " not found from the release" << endl;
        exit(EXIT_COMPONENT_NOT_FOUND);
    }
}
   
// ----------------------------------------------------------------------------------------------------------

void DisplayUsesFunction(const string& function_name)
{
    // check if it's full function name or dll name with ordinal
    string::size_type marker_pos = function_name.find_last_of('@');

    if (marker_pos == string::npos)
    {
        // it is a normal function name
    
        PrintOutputLn(function_name + " - is used by:");
        
        for (unsigned int i=0; i<_all_binary_infos.size(); i++)
        {
            string component_name = _all_binary_infos.at(i).filename;
            
            vector<dependency> deps = _all_binary_infos.at(i).dependencies;
            
            for (unsigned int j=0; j<deps.size(); j++)
            {
                vector<import> imps = deps.at(j).imports;
                    
                for (unsigned int k=0; k<imps.size(); k++)
                {                    
                    if (StringICmp(imps.at(k).funcname.c_str(), function_name.c_str()) == 0)
                    {
                        if (_cl_show_ordinals)
                            PrintOutputLn(component_name + "  [" + deps.at(j).filename + "@" + Int2Str(imps.at(k).funcpos) + "]");                        
                        else
                            PrintOutputLn(component_name);                        

                        break;    
                    }      
                }
            } 
        }            
    }
    
    else
    {
        // get dll name and ordinal number
        string dll_name = function_name.substr(0, marker_pos);
        unsigned int ordinal_number = Str2Int( function_name.substr(marker_pos+1, function_name.length()-marker_pos-1) );

        if (ordinal_number == 0 || ordinal_number > 27500)
        {
            cerr << "Uses function: Given ordinal number is invalid: " << ordinal_number << endl;
            exit(EXIT_INVALID_ORDINAL);
        }                         
    
        PrintOutputLn(function_name + " - is used by:");
        
        for (unsigned int i=0; i<_all_binary_infos.size(); i++)
        {
            string component_name = _all_binary_infos.at(i).filename;
            
            vector<dependency> deps = _all_binary_infos.at(i).dependencies;
            
            for (unsigned int j=0; j<deps.size(); j++)
            {
                string dependency_name = deps.at(j).filename;
                
                if (StringICmp(deps.at(j).filename.c_str(), dll_name.c_str()) == 0)
                {
                    vector<import> imps = deps.at(j).imports;
                        
                    for (unsigned int k=0; k<imps.size(); k++)
                    {                    
                        if (imps.at(k).funcpos == ordinal_number)
                        {
                            PrintOutputLn(component_name);                        
                            break;    
                        }      
                    }
                }
            } 
        }                            
    }    
}

// ----------------------------------------------------------------------------------------------------------

