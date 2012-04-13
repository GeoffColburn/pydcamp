#!/usr/bin/env python

import sys, os
import argparse
import pickle as p
import shutil

import breseq.command
import pipelines.bwa as bwa
import pipelines.samtools as samtools
import pipelines.picardtools as picardtools
import libdcamp.common 

    
def convert_genbanks(ref_paths, output_dir):
    fasta_paths = list()
    for ref_path in ref_paths:
        gbk_path = ref_path
        print gbk_path
        
        fasta_file = os.path.basename(gbk_path).replace(".gbk", ".fasta")
        fasta_path = os.path.join(output_dir, fasta_file)
        
        fasta_paths.append(fasta_path)
        if os.path.exists(fasta_path): continue
        
        breseq.command.convert_genbank(gbk_path, fasta_path)
        assert os.path.exists(fasta_path)
            
    assert len(fasta_paths)
    return fasta_paths

def merge_fastas(fasta_paths, output_dir):
    fasta_path = ""
    if len(fasta_paths) > 1:
        fasta_path = os.path.join(output_dir, "merged.fasta")
        if not os.path.exists(fasta_path):
            for path in fasta_paths:
                libdcamp.common.merge_files(fasta_path, path)
    else :
        fasta_path = fasta_paths[0]
    assert os.path.exists(fasta_path)
    return fasta_path

def bwa_index(fasta_path, output_dir):
    index_done_file_name = "index_{}.done".format(libdcamp.common.get_base_name(fasta_path))
    index_done_file_path = os.path.join(output_dir, index_done_file_name)
    if not os.path.exists(index_done_file_path):
        bwa.index(fasta_path)
        p.dump(fasta_path, open(index_done_file_path, 'w'))
    assert os.path.exists(index_done_file_path)
    return fasta_path
        
def bwa_aln(fasta_path, read_paths, output_dir):
    sam_args = list()
    for fastq_path in read_paths:
        sai_name= "{}_{}.sai".format(libdcamp.common.get_base_name(fasta_path), libdcamp.common.get_base_name(fastq_path))
        sai_path=os.path.join(output_dir, sai_name)
        
        sam_args.append((fasta_path, fastq_path, sai_path))
        if os.path.exists(sai_path): continue
        
        bwa.align(sai_path, fasta_path, fastq_path)
        
    assert len(sam_args)
    return sam_args

def bwa_samse(sam_args, output_dir):
    sam_paths=list()
    for args in sam_args:
        fasta_path, fastq_path, sai_path = args
        sam_path = str(sai_path).replace(".sai", ".sam")
        
        sam_paths.append(sam_path)
        if os.path.exists(sam_path): continue
        
        bwa.samse(sam_path, fasta_path, sai_path, fastq_path)
    assert len(sam_paths)
    return sam_paths

def bwa_sampe(sam_args, output_dir):
    sai_paths = list()
    fastq_paths = list()
    sam_path = os.path.join(output_dir, "sampe.sam")
    for args in sam_args:
        fasta_path, fastq_path, sai_path = args
        sai_paths.append(sai_path)
        fastq_paths.append(fastq_path)
    assert sai_paths
    assert fastq_paths
        
    bwa.sampe(sam_path, fasta_path, sai_paths, fastq_paths)
    return [sam_path]


def add_read_groups(aln_paths, output_dir):
    rg_aln_paths = list()
    for aln_path in aln_paths:
        rg_aln_name = "RG_{}.sam".format(get_base_name(aln_path))
        rg_aln_path = os.path.join(output_dir, rg_aln_name)
        
        rg_aln_paths.append(rg_aln_path)
        if os.path.exists(rg_aln_path): continue
        
        picard_tools.add_read_groups(aln_path, rg_aln_path)
    assert len(rg_aln_paths)
    return rg_aln_paths

def convert_sam_to_bam(sam_paths, output_dir):
    bam_paths=list()
    for sam_path in sam_paths:
        bam_path = str(sam_path).replace(".sam", ".bam")
        
        bam_paths.append(bam_path)
        if os.path.exists(bam_path): continue
        
        samtools.view(bam_path, sam_path)
    assert len(bam_paths)
    return bam_paths

def sort_alignments(bam_paths, output_dir):
    sorted_bam_paths = list()
    for bam_path in bam_paths:
        bam_sorted_prefix = os.path.join(output_dir, "sorted_{}".format(libdcamp.common.get_base_name(bam_path)))
        bam_sorted_path = "{}.bam".format(bam_sorted_prefix)
        
        sorted_bam_paths.append(bam_sorted_path)
        if os.path.exists(bam_sorted_path): continue
        
        samtools.sort(bam_path, bam_sorted_prefix)
    assert len(sorted_bam_paths)
    return sorted_bam_paths

def handle_multiple_bams(sam_paths, bam_paths, output_dir):
    bam_path = ""
    if len(bam_paths) > 1:
        bam_path=os.path.join(output_dir, "merged.bam")
        
        if not os.path.exists(bam_path):
            samtools.merge(sam_paths, bam_path, bam_paths)
    else:
        bam_path = bam_paths[0]
    
    assert os.path.exists(bam_path)
    return bam_path

def add_read_groups(aln_paths, output_dir):
    rg_aln_paths = list()
    for aln_path in aln_paths:
        rg_aln_name = "RG_{}".format(os.path.basename(aln_path))
        rg_aln_path = os.path.join(output_dir, rg_aln_name)
        
        rg_aln_paths.append(rg_aln_path)
        if os.path.exists(rg_aln_path): continue
        
        picardtools.add_or_replace_read_groups(aln_path, rg_aln_path)
    assert len(rg_aln_paths)
    return rg_aln_paths

def convert_sam_to_bam(sam_paths, output_dir = "02_reference_alignment"):
    bam_paths=list()
    for sam_path in sam_paths:
        bam_path = str(sam_path).replace(".sam", ".bam")
        
        bam_paths.append(bam_path)
        if os.path.exists(bam_path): continue
        
        samtools.view(bam_path, sam_path)
    assert len(bam_paths)
    return bam_paths

def sort_alignments(bam_paths, output_dir):
    sorted_bam_paths = list()
    for bam_path in bam_paths:
        bam_sorted_prefix = os.path.join(output_dir, "sorted_{}".format(libdcamp.common.get_base_name(bam_path)))
        bam_sorted_path = "{}.bam".format(bam_sorted_prefix)
        
        sorted_bam_paths.append(bam_sorted_path)
        if os.path.exists(bam_sorted_path): continue
        
        picardtools.sort_sam(bam_path, bam_sorted_path, "coordinate")
    assert len(sorted_bam_paths)
    return sorted_bam_paths

def add_sequence_dict(ref_path, sam_paths, output_dir):
    sd_sam_paths = map(lambda sam_path:os.path.join(output_dir, "SD_{}".format(os.path.basename(sam_path))), sam_paths)

    #Place header info at start of files.
    map(lambda sd_sam_path: picardtools.create_sequence_dictionary(ref_path, sd_sam_path), sd_sam_paths)

    #Append the alignments.
    for sd_sam_path, sam_path in zip(sd_sam_paths, sam_paths):
        sd_sam_file = open(sd_sam_path, 'a')
        for line in open(sam_path, 'r').readlines():
            sd_sam_file.write(line)

    return sd_sam_paths

def bowtie_alignment(args):
    fasta_path = prepare_reference(args, "01_reference_conversion")

    output_dir = "02_reference_alignment"
    step_2_dir = os.path.join(args.output_dir, output_dir)
    step_2_done_file = os.path.join(step_2_dir, "create_alignment.done")
    sorted_bam_path = ""
    if not os.path.exists(step_2_done_file):
        print "++Processing and creating reference alignment file."
        if not os.path.exists(step_2_dir): os.makedirs(step_2_dir)

        print "Indexing reference file: ",  fasta_path
        basename = fasta_path.replace(".fasta", "")
        cmd = "bowtie-build {} {}".format(fasta_path, basename)
        print cmd
        os.system(cmd)

        print "Begin alignment."
        sam_path = fasta_path.replace(".fasta", ".sam")
        cmd = "bowtie -S {} {} {}".format(basename, ",".join(args.read_paths), sam_path) 
        print cmd
        if not os.path.exists(sam_path):
            os.system(cmd)

        #Step: Picardtools: Add read groups.
        read_group_sam_path = add_read_groups([sam_path], step_2_dir)[0]

        #Step: Samtools: BAM(s)
        bam_path = convert_sam_to_bam([read_group_sam_path], step_2_dir)[0]

        sorted_bam_path = sort_alignments([bam_path], step_2_dir)
    else:
        print "++Reference alignment file has already been completed."
        sorted_bam_path = p.load(open(step_2_done_file, 'r'))
    assert os.path.exists(sorted_bam_path) and sorted_bam_path.endswith(".bam")

    return fasta_path, sorted_bam_path

def prepare_alignment(fasta_path, sam_paths, output_dir, add_sequence_dicts = False):
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    #Step: Add sequence dicts.
    if add_sequence_dict:
        print "+++ Adding sequence dictionaries to: {}".format(", ".join(sam_paths))
        sam_paths = add_sequence_dict(fasta_path, sam_paths, output_dir)

    #Step: Picardtools: Add read groups.
    print "+++ Adding read groups to: {}".format(", ".join(sam_paths))
    sam_paths = add_read_groups(sam_paths, output_dir)

    #Step: Samtools: BAM(s)
    print "+++ Converting to BAM format: {}".format(", ".join(sam_paths))
    bam_paths = convert_sam_to_bam(sam_paths, output_dir)

    #Step: Sort BAM(s)
    print "+++ Sorting: {}".format(", ".join(bam_paths))
    bam_paths = sort_alignments(bam_paths, output_dir)

    #Step: Samtools: Merge sorted BAMs, return bam file if there is only one.
    bam_path = handle_multiple_bams(sam_paths, bam_paths, output_dir)

    #Step:Sort Merged BAM(s)
    if len(bam_paths) > 1:
        bam_path = sort_alignments([bam_path], output_dir)

    return bam_path

def ssaha2_alignment(args):
    fasta_path = prepare_reference(args, "01_reference_conversion")

    step_2_dir = os.path.join(args.output_dir, "02_reference_alignment")
    step_2_done_file = os.path.join(step_2_dir, "create_alignment.done")

    bam_path = ""
    if not os.path.exists(step_2_done_file):
        if not os.path.exists(step_2_dir): os.makedirs(step_2_dir)

        samtools.faidx(fasta_path)

        built_reference_path = fasta_path.replace(".fasta", "")
        cmd = "ssaha2Build -rtype solexa -skip 1 -save {} {}".format(built_reference_path, fasta_path)
        print cmd
        os.system(cmd)

        cmd_fmt = "ssaha2 -disk 2 -save {} -kmer 13 -skip 1 -seeds 1 -score 12 -cmatch 9 -ckmer 1 -output sam_soft -outfile {} {}"

        sam_paths = map(lambda read_path: os.path.join(step_2_dir, os.path.basename(read_path.replace(".fastq",".sam"))), args.read_paths)
        for sam_path, read_path in zip(sam_paths, args.read_paths):
            cmd = cmd_fmt.format(built_reference_path, sam_path, read_path)
            print cmd
            if not os.path.exists(sam_path): os.system(cmd)

        bam_path = prepare_alignment(fasta_path, sam_paths, step_2_dir, True)

        #Step: Mark step as completed.
        p.dump(bam_path, open(step_2_done_file, 'w'))

    else:
        print "++Reference alignment file has already been completed."
        bam_path = p.load(open(step_2_done_file, 'r'))
    assert os.path.exists(bam_path) and bam_path.endswith(".bam")

    print fasta_path, bam_path
    return fasta_path, bam_path



def create_alignment(args, fasta_path, output_dir):
    step_2_dir = os.path.join(args.output_dir, output_dir)
    step_2_done_file = os.path.join(step_2_dir, "create_alignment.done")
    sorted_bam_path = ""
    if not os.path.exists(step_2_done_file):
        print "++Processing and creating reference alignment file."
        if not os.path.exists(step_2_dir): os.makedirs(step_2_dir)

        bam_paths = list()
        #Read file input.
        if args.read_paths:
            #Step: BWA: SAI(s)
            sam_args = bwa_aln(fasta_path, args.read_paths, step_2_dir)
                    
            #Step: BWA: SAM(s)
            sam_paths = list()
            if args.pair_ended == True:
                sam_paths = bwa_sampe(sam_args, step_2_dir)
            else:
                sam_paths = bwa_samse(sam_args, step_2_dir)
        
            #Step: Picardtools: Add read groups.
            read_group_sam_paths = add_read_groups(sam_paths, step_2_dir)

            #Step: Samtools: BAM(s)
            bam_paths = convert_sam_to_bam(read_group_sam_paths, step_2_dir)

        
        #Step: Samtools: Sort BAM(s)
        sorted_bam_paths = list()
        if args.sort_bam and args.sort_bam == True:
            sorted_bam_paths = sort_alignments(bam_paths, step_2_dir)
        else:
            sorted_bam_paths = bam_paths

        assert sorted_bam_paths
        
        #Step: Samtools: Merge sorted BAMs, return bam file if there is only one.
        sorted_bam_path = handle_multiple_bams(read_group_sam_paths, sorted_bam_paths, step_2_dir)
        
        #Step: Mark step as completed.
        p.dump(sorted_bam_path, open(step_2_done_file, 'w'))
        
    else:
        print "++Reference alignment file has already been completed."
        sorted_bam_path = p.load(open(step_2_done_file, 'r'))
    assert os.path.exists(sorted_bam_path) and sorted_bam_path.endswith(".bam")
    
    return sorted_bam_path



def prepare_reference(args, output_dir):
    step_1_dir  = os.path.join(args.output_dir, output_dir)
    step_1_done_file = os.path.join(step_1_dir, "prepare_reference.done")
    fasta_path = ""
    if not os.path.exists(step_1_done_file):
        print "++Preparing reference file."
        if not os.path.exists(step_1_dir): os.makedirs(step_1_dir)
        
        #Step: Convert Genbank files to Fasta files.
        fasta_paths = convert_genbanks(args.ref_paths, step_1_dir)
        
        #Step: Merge fasta files if there is more than one return single fasta path if not.
        fasta_path = merge_fastas(fasta_paths, step_1_dir)
        
        #Step: Mark step as completed.
        p.dump(fasta_path, open(step_1_done_file, 'w'))

    else:
        print "++Reference file has already been prepared."
        fasta_path = p.load(open(step_1_done_file, 'r'))
                
    assert os.path.exists(fasta_path) and fasta_path.endswith(".fasta")
    
    return fasta_path



def create_data_dir(args, fasta_path, bam_path):
    print "++Creating data directory for bam2aln processing."
    data_dir = os.path.join(args.output_dir, "data")
    if not os.path.exists(data_dir): os.makedirs(data_dir)

    reference_fasta_path = os.path.join(data_dir, "reference.fasta")
    if not os.path.exists(reference_fasta_path):
        shutil.copy2(fasta_path, reference_fasta_path)
        samtools.faidx(reference_fasta_path)

    reference_bam_path = os.path.join(data_dir, "reference.bam")
    if not os.path.exists(reference_bam_path):
        shutil.copy2(bam_path, reference_bam_path)
        samtools.index(reference_bam_path)

