#!/usr/bin/env python
import sys, os
    
def convert_genbank(gbk_path, fasta_path):
    print "Breseq::convert_genbank({}, {})".format(gbk_path, fasta_path)
    cmd="breseq CONVERT_GENBANK -i {} -f {}".format(gbk_path, fasta_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return fasta_path

def vcf2gd(vcf_path, output_gd_path, option = ""):
    print "Breseq::vcf2gd({}, {})".format(vcf_path, output_gd_path)
    cmd = "breseq VCF2GD {} --input {} --output {}".format(option, vcf_path, output_gd_path)
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_gd_path

def normalize_gd(in_gd_path, ref_paths, output_gd_path):
    cmd = "breseq normalize-gd -g {} -r {} -o {}".format(in_gd_path, " -r ".join(ref_paths), output_gd_path)
    print cmd
    os.system(cmd)
    return output_gd_path

def compare_gd(control_path, test_path, output_path):
    cmd = "breseq compare-gd -c {} -t {} -o {}".format(control_path, test_path, output_path)
    os.system(cmd)
    return output_path

