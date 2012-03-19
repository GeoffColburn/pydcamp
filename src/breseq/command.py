#!/usr/bin/env python
import sys, os
    
def convert_genbank(gbk_path, fasta_path):
    cmd="breseq convert-genbank -i {} -f {}".format(gbk_path, fasta_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return fasta_path

def vcf2gd(vcf_path, output_gd_path, option = ""):
    cmd = "breseq VCF2GD {} --input {} --output {}".format(option, vcf_path, output_gd_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return output_gd_path

def normalize_gd(in_gd_path, ref_paths, output_gd_path):
    cmd = "breseq gd-normalize -g {} -r {} -o {}".format(in_gd_path, " -r ".join(ref_paths), output_gd_path)
    print cmd
    os.system(cmd)
    return output_gd_path

def compare_gd(control_path, test_path, output_path):
    cmd = "breseq gd-compare -c {} -t {} -o {}".format(control_path, test_path, output_path)
    print cmd
    os.system(cmd)
    return output_path

def genome_diff_compare(output_path, ref_paths, gd_paths):
    cmd = "genomediff compare -o {} -r {} {}".format(output_path, " -r ".join(ref_paths), " ".join(gd_paths))
    print cmd
    os.system(cmd)
    return output_path

def genome_diff_merge(gd_paths, output_gd_path):
    cmd = "breseq gd-merge -u -g {} -o {}".format(" -g ".join(gd_paths), output_gd_path)
    print cmd
    os.system(cmd)
    return output_gd_path
    
def genome_diff_filter(gd_path, output_gd_path, mut_types, filters):
    if mut_types.count("ALL"):
        cmd = "breseq gd-filter -g {} -o {} {}".format(gd_path,\
                                                       output_gd_path,\
                                                       " ".join(filters))
    else:
        cmd = "breseq gd-filter -g {} -o {} -m {} {}".format(gd_path,\
                                                             output_gd_path,\
                                                             " -m ".join(mut_types),\
                                                             " ".join(filters))

    print cmd
    os.system(cmd)
    return output_gd_path
