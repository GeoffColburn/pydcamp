#!/usr/bin/env python
import StringIO


class DiffEntry(dict):
    
    class Type:
        UNKNOWN = "UNKNOWN"
        # mutation
        SNP = "SNP"
        SUB = "SUB"
        DEL = "DEL"
        INS = "INS"
        MOB = "MOB"
        INV = "INV"
        AMP = "AMP"
        CON = "CON"
        
        # evidence
        RA = "RA"
        MC = "MC"
        JC = "JC"
        CN = "CN"
        UN = "UN"
        
        # validation
        CURA = "CURA"
        FPOS = "FPOS"
        PHYL = "PHYL"
        TSEQ = "TSEQ"
        PFLP = "PFLP"
        RFLP = "RFLP"
        PFGE = "PFGE"
        NOTE = "NOTE"
        
    # Line specifications:
    line_specs = dict()
    #mutation
    line_specs["SNP"] = ["seq_id", "position", "new_seq"]
    line_specs["SUB"] = ["seq_id", "position", "size", "new_seq"]
    line_specs["DEL"] = ["seq_id", "position", "size"]
    line_specs["INS"] = ["seq_id", "position", "new_seq"]
    line_specs["MOB"] = ["seq_id", "position", "repeat_name", "strand", "duplication_size"]
    line_specs["INV"] = ["seq_id", "position", "size"]
    line_specs["AMP"] = ["seq_id", "position", "size", "new_copy_number"]
    line_specs["CON"] = ["seq_id", "position", "size", "region"]
    # evidence
    line_specs["RA"] = ["seq_id", "position", "insert_position", "ref_base", "new_base"]
    line_specs["MC"] = ["seq_id", "start", "end", "start_range", "end_range"]
    line_specs["JC"] = ["side_1_seq_id", "side_1_position", "side_1_strand", "side_2_seq_id", "side_2_position", "side_2_strand", "overlap"]
    line_specs["CN"] = ["seq_id", "start", "end", "copy_number"]
    line_specs["UN"] = ["seq_id", "start", "end"]
    # validation
    line_specs["CURA"] = ["expert"]
    line_specs["FPOS"] = ["expert"]
    line_specs["PHYL"] = ["gd"]
    line_specs["TSEQ"] = ["seq_id", "primer_1_start", "primer_1_end", "primer_2_start", "primer_2_end"]
    line_specs["PFLP"] = ["seq_id", "primer_1_start", "primer_1_end", "primer_2_start", "primer_2_end"]
    line_specs["RFLP"] = ["seq_id", "primer_1_start", "primer_1_end", "primer_2_start", "primer_2_end"]
    line_specs["PFGE"] = ["seq_id", "enzyme"]
    line_specs["NOTE"] = ["note"]
    
    
    
    #Private members.
    _type     = str()
    _id       = str()
    _evidence = list()
    
    #Constructors
    def __init__(self):
        self._type = ""
        sefl._id   = ""
        
    def __init__(self, line):
        tokens = line.split('\t')
        
        self._type = tokens.pop(0)
        if self._type == "NOTE":
            self["note"] = " ".join(tokens)
            return
        
        self._id = tokens.pop(0)
        evidence = tokens.pop(0)
        
        if ',' in evidence:
            self._evidence = evidence.split(',')
        else:
            self._evidence.append(evidence)
            
        for spec in self.line_specs[self.type()]:
            self[spec] = tokens.pop(0) if tokens else "?"
            
        for field in tokens:
            this_tokens = field.rstrip('\n').split('=')
            if len(this_tokens) != 2: continue
            
            key = this_tokens[0]
            value = this_tokens[1]
            self[key] = value
    
    #Getters
    def type(self):
        return self._type
    def id(self):
        return self._id
    def evidence(self):
        return self._evidence
    
    #Methods
    def is_mutation(self):
        return len(self.type()) == 3
    def is_evidence(self):
        return len(self.type()) == 2
    def is_validation(self):
        return len(self.type()) == 4

class DiffEntryList(list):
    
    #Constructors.
    def __init__(self):
        super(DiffEntryList, self).__init__()
        
    #Methods
    def __getitem__(self, type):
        ret_val = DiffEntryList()
        for de in self:
            if de.type() == type:
                ret_val.append(de)
        return ret_val
    
    def Mutations(self):
        ret_val = DiffEntryList()
        for de in self:
            if de.is_mutation():
                ret_val.append(de)
        return ret_val      
    def Evidence(self):
        ret_val = DiffEntryList()
        for de in self:
            if de.is_evidence():
                ret_val.append(de)
        return ret_val      
    def Validations(self):
        ret_val = DiffEntryList()
        for de in self:
            if de.is_validation():
                ret_val.append(de)
        return ret_val    
    
