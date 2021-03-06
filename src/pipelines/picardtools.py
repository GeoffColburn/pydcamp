#!/usr/bin/env python
import libdcamp.common as common
import os

_PICARD_TOOLS_DIR = "~/local/share/dcamp/picard_tools/"
_ADD_OR_REPLACE_READ_GROUPS = os.path.join(_PICARD_TOOLS_DIR, "AddOrReplaceReadGroups.jar")
_MARK_DUPLICATES            = os.path.join(_PICARD_TOOLS_DIR, "MarkDuplicates.jar") 
_VALIDATE_SAM_FILE          = os.path.join(_PICARD_TOOLS_DIR, "ValidateSamFile.jar") 
_CREATE_SEQUENCE_DICTIONARY = os.path.join(_PICARD_TOOLS_DIR, "CreateSequenceDictionary.jar") 
_SORT_SAM                   = os.path.join(_PICARD_TOOLS_DIR, "SortSam.jar")
_MERGE_SAMS                 = os.path.join(_PICARD_TOOLS_DIR, "MergeSamFiles.jar")

def mark_duplicates(bam_path, output_bam_path, output_metrics_path):
    cmd = "java -Xmx1g -jar {} \
          INPUT={} \
          OUTPUT={} \
          METRICS_FILE={}"\
          .format(_MARK_DUPLICATES, bam_path, output_bam_path, output_metrics_path)
    common.system(cmd)
    common.assert_file(output_bam_path, cmd)
    common.assert_file(output_metrics_path, cmd)

    return output_bam_path

def validate_alignment(aln_path):
    cmd = "java -jar {} I={}".format(_VALIDATE_SAM_FILE, aln_path)
    common.system(cmd)
    return aln_path
    
def add_or_replace_read_groups(input_path, output_path):
    cmd = "java -jar {} I={} O={} LB=FOO PL=ILLUMINA PU=BAR SM=NEE".format(_ADD_OR_REPLACE_READ_GROUPS, input_path, output_path)
    common.system(cmd) 
    common.assert_file(output_path, cmd)
    return output_path

def create_sequence_dictionary(ref_path, output_path):
    cmd = "java -jar {} R={} O={}".format(_CREATE_SEQUENCE_DICTIONARY, ref_path, output_path)
    common.system(cmd)
    common.assert_file(output_path, cmd)
    return output_path

def sort_sam(aln_path, output_aln_path, sort_option = "coordinate"):
    cmd = "java -jar {} INPUT={} OUTPUT={} SORT_ORDER={}".format(_SORT_SAM, aln_path, output_aln_path, sort_option)
    common.system(cmd)
    common.assert_file(output_aln_path, cmd)
    return output_aln_path

def merge_sams(sam_paths, output, merge_seq_dicts = True):
    cmd = "java -jar {} INPUT={} OUTPUT={} MERGE_SEQUENCE_DICTIONARIES={}".format(_MERGE_SAMS," INPUT=".join(sam_paths), output, "true" if merge_seq_dicts else "false")
    common.system(cmd)
    common.assert_file(output, cmd)
    return output


