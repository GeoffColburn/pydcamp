#!/usr/bin/env python
import os, fnmatch

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


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.relpath(os.path.join(path, filename))
