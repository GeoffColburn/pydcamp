#!/usr/bin/env python
import sys, os
    
def convert_genbank(gbk_path, fasta_path):
    cmd="breseq CONVERT_GENBANK -i {} -f {}".format(gbk_path, fasta_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return fasta_path

def vcf2gd(vcf_path, output_gd_path, option = ""):
    cmd = "breseq VCF2GD {} --input {} --output {}".format(option, vcf_path, output_gd_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_gd_path

def normalize_gd(in_gd_path, ref_paths, output_gd_path):
    cmd = "breseq normalize-gd -g {} -r {} -o {}".format(in_gd_path, " -r ".join(ref_paths), output_gd_path)
    print cmd
    os.system(cmd)
    return output_gd_path

def compare_gd(control_path, test_path, output_path):
    cmd = "breseq compare-gd -c {} -t {} -o {}".format(control_path, test_path, output_path)
    print cmd
    os.system(cmd)
    return output_path

def genome_diff_compare(output_path, ref_paths, gd_paths):
    cmd = "genomediff compare -o {} -r {} {}".format(output_path, " -r ".join(ref_paths), " ".join(gd_paths))
    print cmd
    os.system(cmd)
    return output_path

def genome_diff_merge(gd_paths, output_gd_path):
    cmd = "breseq merge -u -g {} -o {}".format(" -g ".join(gd_paths), output_gd_path)
    print cmd
    os.system(cmd)
    return output_gd_path
    
def genome_diff_filter(gd_path, output_gd_path, filter_option):
    filter_values = list()
    mut_types = list()
    if filter_option == "SNP":
        filter_values = ['"QD < 2.0"', '"MQ < 40.0"', '"FS > 60.0"',\
                         '"HaplotypeScore > 13.0"', '"MQRankSum < -12.5"', '"ReadPosRankSum < -8.0"']
        mut_types = ["SNP"]
    elif filter_option == "INDEL":
        filter_values = ['"QD < 2.0"', '"ReadPosRankSum < -20.0"', '"InbreedingCoeff < -0.8"', '"FS > 200.0"']
        mut_types = ["INS", "DEL"]
    else:
        assert 0
    cmd = "breseq filter-gd -g {} -o {} -m {} {}".format(gd_path, output_gd_path, " -m ".join(mut_types), " ".join(filter_values))
    print cmd
    os.system(cmd)
    return output_gd_path
