#!/usr/bin/env python
import os

_PICARD_TOOLS_DIR = "~/local/share/dcamp/picard_tools/"
_ADD_OR_REPLACE_READ_GROUPS = os.path.join(_PICARD_TOOLS_DIR, "AddOrReplaceReadGroups.jar")
_MARK_DUPLICATES            = os.path.join(_PICARD_TOOLS_DIR, "MarkDuplicates.jar") 
_VALIDATE_SAM_FILE          = os.path.join(_PICARD_TOOLS_DIR, "ValidateSamFile.jar") 
_CREATE_SEQUENCE_DICTIONARY = os.path.join(_PICARD_TOOLS_DIR, "CreateSequenceDictionary.jar") 
_SORT_SAM                   = os.path.join(_PICARD_TOOLS_DIR, "SortSam.jar")

def mark_duplicates(bam_path, output_bam_path, output_metrics_path):
    cmd = "java -Xmx1g -jar {} \
          INPUT={} \
          OUTPUT={} \
          METRICS_FILE={}"\
          .format(_MARK_DUPLICATES, bam_path, output_bam_path, output_metrics_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return bam_path

def validate_alignment(aln_path):
    cmd = "java -jar {} I={}".format(_VALIDATE_SAM_FILE, aln_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return aln_path
    
def add_or_replace_read_groups(input_path, output_path):
    cmd = "java -jar {} I={} O={} LB=FOO PL=ILLUMINA PU=BAR SM=NEE".format(_ADD_OR_REPLACE_READ_GROUPS, input_path, output_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return output_path

def create_sequence_dictionary(ref_path, output_path):
    cmd = "java -jar {} R={} O={}".format(_CREATE_SEQUENCE_DICTIONARY, ref_path, output_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return output_path

def sort_sam(aln_path, output_aln_path, sort_option = "coordinate"):
    cmd = "java -jar {} INPUT={} OUTPUT={} SORT_ORDER={}".format(_SORT_SAM, aln_path, output_aln_path, sort_option)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return output_aln_path

