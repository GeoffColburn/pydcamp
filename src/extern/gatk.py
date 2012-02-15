#!/usr/bin/env python
import sys, os

"""  
NOTE(1/18/2012): On lonestar you need to get a newer version of apache-ant http://ant.apache.org/manual/index.html
than is available in modules to build GATK.
"""

_GATK_DIR = "~/local/share/dcamp/gatk"
_GENOME_ANALYSIS_TK = os.path.join(_GATK_DIR, "GenomeAnalysisTK.jar")

def realigner_target_creator(ref_path, bam_path, output_intervals_path):
    cmd = "java -Xmx1g -jar {} \
          -T RealignerTargetCreator \
          -R {} \
          -I {} \
          -o {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, output_intervals_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_intervals_path

def indel_realigner(ref_path, bam_path, intervals_path, output_bam_path):
    cmd = "java -Xmx1g -jar {} \
          -T IndelRealigner \
          -R {} \
          -I {} \
          -targetIntervals {} \
          -o {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, intervals_path, output_bam_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_bam_path

def count_covariates(ref_path, bam_path):
    cmd = "java -Xmx1g -jar {} \
          -T CountCovariates \
          -R {} \
          -I {} \
          -l INFO \
          -cov ReadGroupCovariate \
          -cov QualityScoreCovariate \
          -cov CycleCovariate \
          -cov DinucCovariate \
          -recalFile recal_data.csv \
          --default_read_group 1 \
          --default_platform illumina"\
          .format(_GENOME_ANALYSIS_TK, ref_path, bam_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)

def unified_genotyper(ref_path, bam_path, output_vcf_path):
    cmd = "java -jar {} \
          -T UnifiedGenotyper \
          -R {} \
          -I {} \
          -o {} \
          -l INFO \
          -glm BOTH".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, output_vcf_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_vcf_path

    
