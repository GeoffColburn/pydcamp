#!/usr/bin/env python
import sys, os

"""  
NOTE(1/18/2012): On lonestar you need to get a newer version of apache-ant http://ant.apache.org/manual/index.html
than is available in modules to build GATK.
"""


def realigner_target_creator(ref_path, bam_path, output_intervals_path):
    print "Gatk::realigner_target_creator({}, {}, {})".format(ref_path, bam_path, output_intervals_path)
    cmd = "java -Xmx1g -jar {} \
          -T RealignerTargetCreator \
          -R {} \
          -I {} \
          -o {}".format("GenomeAnalysisTK.jar", ref_path, bam_path, output_intervals_path)
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_intervals_path

def indel_realigner(self, ref_path, bam_path, intervals_path, output_bam_path):
    print "Gatk::indel_realigner({}, {}, {}, {})".format(ref_path, bam_path, intervals_path, output_bam_path)
    cmd = "java -Xmx1g -jar {} \
          -T IndelRealigner \
          -R {} \
          -I {} \
          -targetIntervals {} \
          -o {}".format("GenomeAnalysisTK.jar", ref_path, bam_path, intervals_path, output_bam_path)
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_bam_path

def count_covariates(self, ref_path, bam_path):
    print "Gatk::count_covariates({}, {})".format(ref_path, bam_path)
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
          .format("GenomeAnalysisTK.jar", ref_path, bam_path)
    assert not os.system(cmd), "Command: {}".format(cmd)

def unified_genotyper(self, ref_path, bam_path, output_vcf_path):
    print "Gatk::unified_geno_typer({}, {}, {})".format(ref_path, bam_path, output_vcf_path)
    cmd = "java -jar {} \
          -T UnifiedGenotyper \
          -R {} \
          -I {} \
          -o {} \
          -l INFO \
          -glm BOTH".format("GenomeAnalysisTK.jar", ref_path, bam_path, output_vcf_path)
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_vcf_path

    
