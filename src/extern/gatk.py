#!/usr/bin/env python
import sys, os

"""  
NOTE(1/18/2012): On lonestar you need to get a newer version of apache-ant http://ant.apache.org/manual/index.html
than is available in modules to build GATK.
"""

_GATK_DIR = "~/local/share/dcamp/gatk"
_GENOME_ANALYSIS_TK = os.path.join(_GATK_DIR, "GenomeAnalysisTK.jar")

def realigner_target_creator(ref_path, bam_path):
    intervals_path = os.path.join(os.path.dirname(bam_path), "output.intervals")
    cmd = "java -Xmx1g -jar {} \
          -T RealignerTargetCreator \
          -R {} \
          -I {} \
          -o {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, intervals_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return intervals_path

def indel_realigner(ref_path, bam_path, intervals_path):
    realigned_bam_path = os.path.join(os.path.dirname(bam_path), "realigned.bam")
    cmd = "java -Xmx1g -jar {} \
          -T IndelRealigner \
          -R {} \
          -I {} \
          -targetIntervals {} \
          -o {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, intervals_path, realigned_bam_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return realigned_bam_path

def count_covariates(ref_path, bam_path, out_recal_csv):
    cmd = "java -Xmx1g -jar {} \
          -T CountCovariates \
          -R {} \
          -I {} \
          -l INFO \
          -cov ReadGroupCovariate \
          -cov QualityScoreCovariate \
          -cov CycleCovariate \
          -cov DinucCovariate \
          -recalFile {} \
          --default_read_group 1 \
          --default_platform illumina\
          -run_without_dbsnp_potentially_ruining_quality"\
          .format(_GENOME_ANALYSIS_TK, ref_path, bam_path, out_recal_csv)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)

def table_recalibration(ref_path, bam_path, recal_csv_path, output_bam_path):
    cmd = "java -jar {} \
           -R {} \
           -I {} \
           -T TableRecalibration \
           -o {} \
           -recalFile {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, output_bam_path, recal_csv_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)

def unified_genotyper(ref_path, bam_path, output_vcf_path, glm_option):
    cmd = "java -jar {} \
          -T UnifiedGenotyper \
          -R {} \
          -I {} \
          -o {} \
          -l INFO \
          -glm {}".format(_GENOME_ANALYSIS_TK, ref_path, bam_path, output_vcf_path, glm_option)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_vcf_path

def variant_filtration_walker(ref_path, vcf_path, output_vcf_path, filter_option):
    filter_values = list()
    if filter_option == "SNP":
        #filter_values = ['"QD < 2.0"', '"MQ < 40.0"', '"FS > 60.0"', '"HaplotypeScore > 13.0"', '"MQRankSum < -12.5"', '"ReadPosRankSum < -8.0"']
        #filter_values = ["QD < 2.0", "MQ < 40.0", "FS > 60.0", "HaplotypeScore > 13.0", "MQRankSum < -12.5", "ReadPosRankSum < -8.0"]
        filter_values = ["QD < 2.0", "MQ < 40.0", "FS > 60.0", "HaplotypeScore > 13.0"]

    elif filter_option == "INDEL":
        filter_values = ["QD < 2.0", "FS > 200.0"]

    else:
        assert 0

    cmd = 'java -Xmx2g -jar {} \
          -T VariantFiltration \
          -R {} \
          -o {} \
          --variant {} \
          --filterExpression "{}" \
          --filterName {}Filter'.format(_GENOME_ANALYSIS_TK, ref_path, output_vcf_path, vcf_path, " || ".join(filter_values), filter_option)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)



    
