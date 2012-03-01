#!/usr/bin/env python
import sys, os

def index(fasta_path):
    cmd="bwa index -a bwtsw {}".format(fasta_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return fasta_path

def align(sai_path, fasta_path, fastq_path):
    cmd = "bwa aln -f {} {} {}".format(sai_path, fasta_path, fastq_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return sai_path

def samse(sam_path, fasta_path, sai_path, fastq_path):
    #bwa samse *.fasta *.sai *.fastq > *.sam
    cmd = "bwa samse -f {} {} {} {}".format(sam_path, fasta_path, sai_path, fastq_path)
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return sam_path

def sampe(sam_path, fasta_path, sai_paths, fastq_paths):
    #bwa samse *.fasta *.sai *.fastq > *.sam
    cmd = "bwa sampe -f {} {} {} {}".format(sam_path, fasta_path, " ".join(sai_paths), " ".join(fastq_paths))
    print cmd
    assert not os.system(cmd), "Command: {}".format(cmd) 
    return sam_path
