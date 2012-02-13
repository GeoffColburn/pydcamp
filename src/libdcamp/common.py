#!/usr/bin/env python
import os

def merge_files(append_file_name, read_file_name):
    file1 = open(append_file_name, 'a')
    file2 = open(read_file_name, 'r')
    
    for line in file2.readlines():
        file1.write(line)
    
    file1.close()
    file2.close()
    
def get_base_name(value):
    value=os.path.basename(value)
    value=os.path.splitext(value)[0]
    return value

def GetRunName(value):
    value = get_base_name(value)
    return value.split('.')[0]
