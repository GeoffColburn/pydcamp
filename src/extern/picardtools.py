#!/usr/bin/env python
import os

def MarkDuplicates(bam_path):
    output_dir = os.path.dirname(bam_path)
    output_path = os.path.join(output_dir, "MarkDuplicatesOutput")
    metric_path = os.path.join(output_dir, "MarkDuplicatesMetrics")
    
    print "PicardTools::mark_duplicates({})".format(bam_path)
    cmd = "java -Xmx1g -jar {} \
          INPUT={} \
          OUTPUT={} \
          METRICS_FILE={}"\
          .format("MarkDuplicates.jar", bam_path, output_path, metric_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return bam_path

def ValidateSamFile(aln_path):
    print "PicardTools::validate_alignment({})".format(aln_path)
    cmd = "java -jar {} I={}".format("ValidateSamFile.jar", aln_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return aln_path
    
def AddOrReplaceReadGroups(input_path, output_path):
    print "PicardTools::add_read_groups({}, {})".format(input_path, output_path)
    cmd = "java -jar {} I={} O={} LB=FOO PL=ILLUMINA PU=BAR SM=NEE".format("AddOrReplaceReadGroups.jar", input_path, output_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return output_path
