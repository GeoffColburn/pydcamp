#!/usr/bin/env python
import os
import libdcamp.common as common

samtools_exe = "samtools"

def view(bam_path, sam_path):
    cmd = samtools_exe + " view -hbS -o {} {}".format(bam_path, sam_path)
    common.system(cmd) 
    common.assert_file(bam_path, cmd)
    return bam_path

def sort(bam_path, bam_sorted_prefix):       
    cmd = samtools_exe + " sort {} {}".format(bam_path, bam_sorted_prefix)
    sorted_bam_path = bam_sorted_prefix + ".bam" 
    common.system(cmd)
    common.assert_file(sorted_bam_path, cmd)
    return sorted_bam_path
    
def merge(sam_paths, merged_bam_path, bam_paths):
    cmd = samtools_exe + " merge -r -n -h {} {} {}".format(" -h ".join(sam_paths), merged_bam_path, " ".join(bam_paths))
    common.system(cmd)
    common.assert_file(merged_bam_path, cmd)
    return merged_bam_path

def index(bam_path):
    cmd = samtools_exe + " index {}".format(bam_path)
    common.system(cmd)
    common.assert_file(bam_path, cmd)
    return bam_path

def mpileup(fasta_path, bam_sorted_path, out_vcf_path):
    cmd = samtools_exe + " mpileup -uf {} {} | bcftools view -vcg - > {}".format(fasta_path, bam_sorted_path, out_vcf_path)
    common.system(cmd)
    common.assert_file(out_vcf_path, cmd)
    return out_vcf_path


def faidx(fasta_path):
    cmd = samtools_exe + " faidx {}".format(fasta_path)
    common.system(cmd)
    return fasta_path

