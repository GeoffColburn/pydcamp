#!/usr/bin/env python
import sys, os
import string

from diff_entry import DiffEntry
from diff_entry import DiffEntryList
    
    
class HeaderInfo:
    def __init__(self):
        self.file_path = ""
        self.file_name = ""
        self.run_name  = ""
        self.ref_seqs  = list()
        self.read_seqs = list()
        self.other     = dict()
        
class GenomeDiff:
    
    #Constructors:
    def __init__(self): pass
    
    def __init__(self, file_path):
        self._header_info = HeaderInfo()
        self._entry_list = DiffEntryList()
        self.from_genome_diff_file(file_path)
        
    #Getters.
    def entry_list(self):
        return self._entry_list
    def header_info(self):
        return self._header_info
    def ref_sequence_file_names(self):
        ret_val = list()
        for ref_seq in self._header_info.ref_seqs:
            ret_val.append(os.path.basename(ref_seq))
        return ret_val
    
    def ref_sequence_file_paths(self, downloads_dir = "02_Downloads"):
        tokens = self._header_info.ref_seqs
        ref_seq_paths = list()
        for token in tokens:
            kvp = token.split(":")
            file_name = os.path.basename(kvp[1])
            if not file_name.endswith(".gbk"):
                file_name = "{}.gbk".format(file_name)
            file_path = os.path.join(downloads_dir, file_name)
            ref_seq_paths.append(file_path)
        assert ref_seq_paths
        return ref_seq_paths
    
    def from_genome_diff_file(self, file_path):
        self._header_info.file_path = file_path
        self._header_info.file_name = os.path.basename(file_path)
        self._header_info.run_name  = os.path.basename(file_path).split('.')[0] 
        
        fp = open(file_path, 'r')
        
        #Hander header info.
        lines = fp.readlines()
        assert string.find(lines.pop(0), "#=GENOME_DIFF") == 0
        for line in lines:
            if string.find(line, "#=") != 0:
                lines.append(line)
                break
            if (line.startswith("#=REFSEQ")): 
                self._header_info.ref_seqs.append(line.split()[1])
            elif (line.startswith("#=READSEQ")):
                self._header_info.read_seqs.append(line.split()[1])
            elif (line.startswith("#=TITLE")):
                self._header_info.run_name = line.split()[1]
            else:
                tokens = line.lstrip("#=").split()
                if tokens:
                    key = tokens.pop(0)
                    value = " ".join(tokens) if len(tokens) > 0 else "?"
                    self._header_info.other[key] = value
            line = fp.readline()
                
        #Handle diff entries.
        for line in lines:
            if line.startswith("#"): continue
            line = line.rstrip('\n')
            if not line: continue
            de = DiffEntry(line)
            self._entry_list.append(de)

        
        
        
            
                
        
        
                
            
            
                
            
                
                
            
        


