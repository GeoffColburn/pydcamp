#!/usr/bin/env python
import os

def view(bam_path, sam_path):
    print "Samtools::view({}, {})".format(bam_path, sam_path)
    cmd = "samtools view -hbS -o {} {}".format(bam_path, sam_path)
    os.system(cmd) 
    return sam_path

def sort(bam_path, bam_sorted_prefix):       
    print "Samtools::sort({}, {})".format(bam_path, bam_sorted_prefix)
    cmd = "samtools sort {} {}".format(bam_path, bam_sorted_prefix)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return "{}.bam".format(bam_sorted_prefix)
    
def merge(merged_bam_path, bam_paths):
    print "Samtools::merge_bams({}, {})".format(merged_bam_path, bam_paths)
    cmd = "samtools merge -rh {} {}".format(merged_bam_path, " ".join(bam_paths))
    assert not os.system(cmd), "Command: {}".format(cmd) 
    print "\tBAM file: {} merged from {}.".format(merged_bam_path, " ".join(bam_paths))
    return merged_bam_path

def index(bam_path):
    print "Samtools::index({})".format(bam_path)
    cmd = "samtools index {}".format(bam_path)
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return bam_path

def mpileup(fasta_path, bam_sorted_path, out_vcf_path):
    print "Samtools::mpileup({}, {}, {})".format(fasta_path, bam_sorted_path, out_vcf_path)
    cmd = "samtools mpileup -uf {} {} | bcftools view -vcg - > {}".format(fasta_path, bam_sorted_path, out_vcf_path)
    assert not os.system(cmd), "Command: {}".format(cmd)
    return out_vcf_path

