#!/usr/bin/env python
import os

def view(bam_path, sam_path):
    cmd = "samtools-0.1.18 view -hbS -o {} {}".format(bam_path, sam_path)
    print cmd
    assert not os.system(cmd) 
    return sam_path

def sort(bam_path, bam_sorted_prefix):       
    cmd = "samtools-0.1.18 sort {} {}".format(bam_path, bam_sorted_prefix)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return "{}.bam".format(bam_sorted_prefix)
    
def merge(sam_paths, merged_bam_path, bam_paths):
    cmd = "samtools-0.1.18 merge -r -n -h {} {} {}"\
            .format(" -h ".join(sam_paths), merged_bam_path, " ".join(bam_paths))
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    print "\tBAM file: {} merged from {}.".format(merged_bam_path, " ".join(bam_paths))
    return merged_bam_path

def index(bam_path):
    cmd = "samtools-0.1.18 index {}".format(bam_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return bam_path

def mpileup(fasta_path, bam_sorted_path, out_vcf_path):
    cmd = "samtools-0.1.18 mpileup -uf {} {} | bcftools view -vcg - > {}".format(fasta_path, bam_sorted_path, out_vcf_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return out_vcf_path


def faidx(fasta_path):
    cmd = "samtools-0.1.18 faidx {}".format(fasta_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd)
    return fasta_path

