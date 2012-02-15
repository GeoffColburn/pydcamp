#!/usr/bin/env python
import os

_PICARD_TOOLS_DIR = "~/local/share/dcamp/picard_tools/"
_ADD_OR_REPLACE_READ_GROUPS = os.path.join(_PICARD_TOOLS_DIR, "AddOrReplaceReadGroups.jar")
_MARK_DUPLICATES            = os.path.join(_PICARD_TOOLS_DIR, "MarkDuplicates.jar") 
_VALIDATE_SAM_FILE          = os.path.join(_PICARD_TOOLS_DIR, "ValidateSamFile.jar") 

def mark_duplicates(bam_path):
    output_dir = os.path.dirname(bam_path)
    output_path = os.path.join(output_dir, "MarkDuplicatesOutput")
    metric_path = os.path.join(output_dir, "MarkDuplicatesMetrics")
    
    cmd = "java -Xmx1g -jar {} \
          INPUT={} \
          OUTPUT={} \
          METRICS_FILE={}"\
          .format(_MARK_DUPLICATES, bam_path, output_path, metric_path)
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
