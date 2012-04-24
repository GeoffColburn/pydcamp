#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse
import string
import re
import pickle as p

from collections import defaultdict


import breseq.command
from breseq.genome_diff import GenomeDiff

import pipelines.samtools as samtools
import pipelines.gatk as gatk
import pipelines.picardtools as picardtools
import pipelines.common

from libdcamp.settings import Settings
from libdcamp.html_factory import HtmlFactory
from libdcamp.file_factory import FileFactory
from libdcamp.file_wrangler import FileWrangler
import libdcamp.job as job

import urllib2
import glob


                
def do_results(args):
    settings = Settings(args)

    print "Searching for output/output.gd in paths:", ", ".join(args.input_dirs)

    job_paths = job.handle_gds(args.input_dirs, args.force_overwrite)

    html_factory = HtmlFactory()
    html_factory.write_index_page(job_paths)

    file_factory = FileFactory()
    file_factory.write_validation_table(job_paths)
    file_factory.write_mutation_rates_table(job_paths)

    return 0

def do_make_test(args):
    settings = Settings(args)
    job.handle_logs(args.test_path, args.log_path, args.force_overwrite)

    return 0

    #job_paths = job.handle_gds(args.test_path, args.force_overwrite)

    #html_factory = HtmlFactory()

    #return 0

def do_create_alignment(args):
    fasta_path = pipelines.common.prepare_reference(args, "01_reference_conversion")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "02_reference_alignment")

def do_samtools(args):
    fasta_path, sorted_bam_path = pipelines.common.ssaha2_alignment(args)

    output_dir = os.path.join(args.output_dir, "output")
    output_file = os.path.join(output_dir, "output.done")

    vcf_path = os.path.join(output_dir, "raw.vcf")
    raw_gd_path = os.path.join(output_dir, "raw.gd")
    output_gd_path = os.path.join(output_dir, "output.gd")
    if not os.path.exists(output_file):
        print "++Step 3 mutation predictions and output started."
        if not os.path.exists(output_dir): os.makedirs(output_dir)
            
        #Step: Samtools: Mutation prediction.
        if not os.path.exists(vcf_path):
            samtools.mpileup(fasta_path, sorted_bam_path, vcf_path)
        assert os.path.exists(vcf_path)
        
        #Step: Breseq: Convert VCF file to Genome Diff format.
        breseq.command.vcf2gd(vcf_path, output_gd_path)
        breseq.command.genome_diff_filter(output_gd_path, output_gd_path, ["ALL"], ['"AF1!=1"'])
        assert os.path.exists(output_gd_path)

        pipelines.common.create_data_dir(args, fasta_path, sorted_bam_path)
    
def do_breakdancer(args): 
    """Believe we need to keep all files in one directory, although it's not mentioned,
    breakdancer may look at files other than the .bam file."""
    fasta_path, sorted_bam_path = pipelines.common.ssaha2_alignment(args, "01_All", "01_All")
    sorted_bam_file = os.path.basename(sorted_bam_path)

    step_3_dir = os.path.join(args.output_dir, "01_All")
    step_3_file = os.path.join(step_3_dir, "output.done")

    cfg_path = os.path.join(step_3_dir, "output.cfg")
    ctx_path = os.path.join(step_3_dir, "output.ctx")
    cfg_file = os.path.basename(cfg_path)
    ctx_file = os.path.basename(ctx_path) 

    if not os.path.exists(step_3_file):
        print "++Step 3 mutation predictions and output started."
        if not os.path.exists(step_3_dir): os.makedirs(step_3_dir)

        """We need to change into the directory because breakdancer outputs histogram
        files into the current working directory."""
        cwd = os.getcwd()
        os.chdir(step_3_dir)
        #Breakdancer::bam2cfg.pl.
        ##if not os.path.exists(cfg_path):
        cmd = "bam2cfg.pl -h -g {} > {}".format(sorted_bam_file, cfg_file)
        print cmd           
        os.system(cmd)
        assert os.path.exists(cfg_file)

        #Breakdancer::breakdancer_max.
        ##if not os.path.exists(ctx_path):
        cmd = "breakdancer_max {} > {}".format(cfg_file, ctx_file)
        print cmd
        os.system(cmd)
        assert os.path.exists(ctx_file)
        
        os.chdir(cwd) #Change back to original cwd.
    """To be consistent with other pipelines, copy the .cfg and .ctx file to the output 
    directory."""
    output_dir = os.path.join(args.output_dir, "output")
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    new_cfg_path = os.path.join(output_dir, cfg_file)
    new_ctx_path = os.path.join(output_dir, ctx_file)

    shutil.copy2(cfg_path, new_cfg_path )
    shutil.copy2(ctx_path, new_ctx_path )

def do_freebayes(args):
    fasta_path, sorted_bam_path = pipelines.common.bowtie_alignment(args)

    output_dir = os.path.join(args.output_dir, "output")
    vcf_path = os.path.join(args.output_dir, "output.vcf")
    gd_path = os.path.join(args.output_dir, "output.gd")

    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(vcf_path):
        cmd = "freebayes --vcf {} --fasta-reference {} --bam {}"\
                .format(vcf_path, fasta_path, sorted_bam_path)
        os.system(cmd)

    breseq.command.vcf2gd(vcf_path, gd_path)


def do_gatk(args):
    fasta_path, sorted_bam_path = pipelines.common.ssaha2_alignment(args)


    #Gatk
    #Step 3
    step_3_dir = os.path.join(args.output_dir, "03_gatk")
    step_3_file = os.path.join(step_3_dir, "gatk.done")
    realigned_bam_path = ""
    if not os.path.exists(step_3_file):
        print "++Gatk recalibration and realignment of reference alignment file."
        if not os.path.exists(step_3_dir):
            os.makedirs(step_3_dir)
            
        #Step: Picard: Mark Duplicates.
        dedup_bam_path = os.path.join(step_3_dir, "dedup.bam")
        dedup_metrics_path = os.path.join(step_3_dir, "dedup.metrics")
        picardtools.mark_duplicates(sorted_bam_path, dedup_bam_path, dedup_metrics_path)

        #Step: Samtools: Index BAM. ***Do after mark duplicates.
        index_done_file = os.path.join(step_3_dir, "index.done")
        if not os.path.exists(index_done_file):
            samtools.index(dedup_bam_path)
            open(index_done_file, 'w').close()

        #Step: Gatk Realign.
        #Gatk: Intervals.
        intervals_path = gatk.realigner_target_creator(fasta_path, dedup_bam_path)
        #Gatk: Indel Realign.
        realigned_bam_path = gatk.indel_realigner(fasta_path, dedup_bam_path, intervals_path)

        #Step: Gatk Recal. ***May not be able to do due to need for dbSNP file.
        #CountCovariates.
        #recal_csv_path = os.path.join(step_3_dir, "recal_data.csv")
        #gatk.count_covariates(fasta_path, realigned_bam_path, recal_csv_path)
        ##TableRecalibration.
        #recal_bam_path = os.path.join(step_3_dir, "recal.bam")
        #gatk.table_recalibration(fasta_path, realigned_bam_path, recal_csv_path, recal_bam_path)
        
        p.dump(realigned_bam_path, open(step_3_file, 'w'))
    else:
        realigned_bam_path = p.load(open(step_3_file, 'r'))
        
    #Gatk Output
    #Step 4
    output_dir = os.path.join(args.output_dir, "output")
    raw_vcf_path = os.path.join(output_dir, "output.vcf")
    gd_path = os.path.join(output_dir, "output.gd")
    print "++Filtering poor values for SNPs and INDELs in output and converting vcf files to gd."

    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    if not os.path.exists(raw_vcf_path):
        gatk.unified_genotyper(fasta_path, realigned_bam_path, raw_vcf_path, args.glm_option)

    breseq.command.vcf2gd(raw_vcf_path, gd_path)
    
    #Gatk recommended filter values for SNPs and INDELs.
    snp_filters = ['"QD < 2.0"',\
                   '"MQ < 40.0"',\
                   '"FS > 60.0"',\
                   '"HaplotypeScore > 13.0"',\
                   '"MQRankSum < -12.5"',\
                   '"ReadPosRankSum < -8.0"']

    indel_filters = ['"QD < 2.0"',\
                     '"ReadPosRankSum < -20.0"',\
                     '"InbreedingCoeff < -0.8"',\
                     '"FS > 200.0"']

    snp_gd = os.path.join(output_dir, "SNP.gd")
    indels_gd = os.path.join(output_dir, "INDELS.gd")

    breseq.command.genome_diff_filter(snp_gd, gd_path, ["SNP"], snp_filters)
    breseq.command.genome_diff_filter(indels_gd, gd_path, ["INS", "DEL"], indel_filters)

    breseq.command.genome_diff_merge([snp_gd, indels_gd] , gd_path)
    breseq.command.genome_diff_filter(gd_path, gd_path, ["ALL"], ['"AF!=1.00"'])


    pipelines.common.create_data_dir(args, fasta_path, realigned_bam_path)


def do_create_simulated_gds(args):
    quality_scores = list()
    if args.quality_score == "all" or args.quality_score == "05": quality_scores.append("05")
    if args.quality_score == "all" or args.quality_score == "10": quality_scores.append("10")
    if args.quality_score == "all" or args.quality_score == "20": quality_scores.append("20")
    if args.quality_score == "all" or args.quality_score == "40": quality_scores.append("40")
    if args.quality_score == "all" or args.quality_score == "80": quality_scores.append("80")

    base_name = os.path.basename(args.genome_diff).split(".gd")[0]
    ref_file = os.path.basename(args.ref_seq)
    values = list()
    for quality_score in quality_scores:
        this_base_name = "{}_{}".format(base_name, quality_score) 
        gd_file = "{}.gd".format(this_base_name)
        read_file = "{}.fastq.gz".format(this_base_name)

        ref_header = "#=REFSEQ\t{}:{}\n".format(args.ref_key, os.path.join(args.ref_prefix, ref_file))
        read_header = "#=READSEQ\t{}:{}\n".format(args.read_key, os.path.join(args.read_prefix, read_file))
        values.append((gd_file, ref_header, read_header))

    for gd_file, ref_header, read_header in values:
        lines = open(args.genome_diff, 'r').readlines()
        fout = open(gd_file, 'w')
        while lines:
            if string.find(lines[0], "#=") == 0:
                fout.write(lines.pop(0))
            else:
                break
        fout.write(ref_header)
        fout.write(read_header)
        for line in lines:
            fout.write(line)

def do_prepare_alignment(args):
    pipelines.common.prepare_alignment(args.fasta_path, args.sam_paths, args.output_dir, True)

def do_test(args): pass

def do_prepare_alignment(args): 
    pipelines.common.prepare_alignment(args.fasta_path, args.sam_paths, args.output_dir)

def do_mut_table(args):
    import libdcamp.html_factory as html
    union_table = defaultdict(dict)#Test/Pipeline/union.gd
    for path in args.inputs:
        test = path.strip('/').split('/').pop()
        for dir in glob.glob(os.path.join(path, '*')):
            name = dir.split('/').pop()
            comp_gds = glob.glob(os.path.join(dir, "*/comp.gd"))
            if comp_gds:
                dcamp_dir = os.path.join(path, "dcamp/{}".format(name)) 
                if not os.path.exists(dcamp_dir):
                    os.makedirs(dcamp_dir)

                union_gd = os.path.join(dcamp_dir, "union.gd")
                if not os.path.exists(union_gd):
                    breseq.command.gdtools_union(union_gd, comp_gds)

                union_table[test][name] = union_gd

    html.mutation_rate_table(args.output, union_table)

def do_ins_graph(args):
    from libdcamp.file_wrangler import Wrangler
    wrangler = Wrangler.comp_gds(args.inputs)
    for i in wrangler:
        print i



    






def main():
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers()


    #results.
    results_parser = subparser.add_parser("results")
    results_parser.add_argument("--data",      dest = "data",       default = "01_Data")
    results_parser.add_argument("--downloads", dest = "downloads",  default = "02_Downloads")
    results_parser.add_argument("-o",          dest = "output_dir", required = True)
    results_parser.add_argument("input_dirs", nargs = '+')
    results_parser.add_argument("-f", action = "store_true", dest = "force_overwrite", default = False)
    results_parser.set_defaults(func = do_results)

    #Make test.
    make_test_parser = subparser.add_parser("make-test")
    make_test_parser.add_argument("--data",      dest = "data",      default = "01_Data")
    make_test_parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    make_test_parser.add_argument("--output",    dest = "test_path", default = "03_Output")
    make_test_parser.add_argument("--logs",      dest = "log_path",  default = "04_Logs")
    make_test_parser.add_argument("--results",   dest = "results",   default = "05_Results")
    make_test_parser.add_argument("--name",      dest = "job_name",  default = "make_test")
    make_test_parser.add_argument("-f", action = "store_true", dest = "force_overwrite", default = False)
    make_test_parser.set_defaults(func = do_make_test)

    #create-alignment.
    create_alignment_parser = subparser.add_parser("create-alignment")
    create_alignment_parser.add_argument("-o", dest = "output_dir")
    create_alignment_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    create_alignment_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    create_alignment_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    create_alignment_parser.add_argument("read_paths", nargs = '+')
    create_alignment_parser.set_defaults(func = do_create_alignment)

    #bowtie.
    bowtie_parser = subparser.add_parser("bowtie")
    bowtie_parser.add_argument("-o", dest = "output_dir", required = True)
    bowtie_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    bowtie_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    bowtie_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    bowtie_parser.add_argument("read_paths", nargs = '+')
    bowtie_parser.set_defaults(func = pipelines.common.bowtie_alignment)

    #ssaha2.
    ssaha2_parser = subparser.add_parser("ssaha2")
    ssaha2_parser.add_argument("-o", dest = "output_dir", required = True)
    ssaha2_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    ssaha2_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    ssaha2_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    ssaha2_parser.add_argument("read_paths", nargs = '+')
    ssaha2_parser.set_defaults(func = pipelines.common.ssaha2_alignment)

    #samtools.
    samtools_parser = subparser.add_parser("samtools")
    samtools_parser.add_argument("-o", dest = "output_dir")
    samtools_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    samtools_parser.add_argument("-a", action = "append", dest = "aln_paths", required = False)
    samtools_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    samtools_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    samtools_parser.add_argument("read_paths", nargs = '+', default = None)
    samtools_parser.set_defaults(func = do_samtools)

    #breakdancer.
    breakdancer_parser = subparser.add_parser("breakdancer")
    breakdancer_parser.add_argument("-o", dest = "output_dir")
    breakdancer_parser.add_argument("-r", action = "append", dest = "ref_paths")
    breakdancer_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = True)
    breakdancer_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    breakdancer_parser.add_argument("read_paths", nargs = '+')
    breakdancer_parser.set_defaults(func = do_breakdancer)

    #breakdancer.
    freebayes_parser = subparser.add_parser("freebayes")
    freebayes_parser.add_argument("-o", dest = "output_dir")
    freebayes_parser.add_argument("-r", action = "append", dest = "ref_paths")
    freebayes_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    freebayes_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    freebayes_parser.add_argument("read_paths", nargs = '+')
    freebayes_parser.set_defaults(func = do_freebayes)

    #gatk.
    gatk_parser = subparser.add_parser("gatk")
    gatk_parser.add_argument("-o", dest = "output_dir")
    gatk_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    gatk_parser.add_argument("-a", action = "append", dest = "aln_paths", required = False)
    gatk_parser.add_argument("--glm", dest = "glm_option", default = "BOTH", choices = ["BOTH", "SNP", "INDEL"])
    gatk_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    gatk_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    gatk_parser.add_argument("read_paths", nargs = '+', default = None)
    gatk_parser.set_defaults(func = do_gatk)

    #create-simulated-gds
    sim_gd_parser = subparser.add_parser("sim-gds")
    sim_gd_parser.add_argument("-g", dest = "genome_diff", required = True)
    sim_gd_parser.add_argument("-r", dest = "ref_seq", default = "REL606.5.gbk")
    sim_gd_parser.add_argument("--quality-score", dest = "quality_score",\
            default = "all", choices = ["05", "10", "20", "40", "80"])
    sim_gd_parser.add_argument("--ref-key", dest = "ref_key", default = "BarrickLab-Private")
    sim_gd_parser.add_argument("--ref-prefix", dest = "ref_prefix", default = "genomes/simulated")
    sim_gd_parser.add_argument("--read-key", dest = "read_key", default = "BarrickLab-Private")
    sim_gd_parser.add_argument("--read-prefix", dest = "read_prefix", default = "genomes/simulated")
    sim_gd_parser.set_defaults(func = do_create_simulated_gds)

    #prepare alignment
    prepare_alignment_parser = subparser.add_parser("prep-alignment")
    prepare_alignment_parser.add_argument("-r", dest = "fasta_path")
    prepare_alignment_parser.add_argument("-o", dest = "output_dir", default = ".")
    prepare_alignment_parser.add_argument("sam_paths", nargs = '+', default = None)
    prepare_alignment_parser.set_defaults(func = do_prepare_alignment)

    #weights_table
    mut_table_parser = subparser.add_parser("mut-table")
    mut_table_parser.add_argument("-o", dest = "output", required = True)
    mut_table_parser.add_argument("inputs", nargs = '+', default = None)#ie: meyer_2012, woods_2011
    mut_table_parser.set_defaults(func = do_mut_table)

    #ins-graph
    mut_table_parser = subparser.add_parser("ins-graph")
    mut_table_parser.add_argument("-o", dest = "output", required = True)
    mut_table_parser.add_argument("inputs", nargs = '+', default = None)
    mut_table_parser.set_defaults(func = do_ins_graph)


    #testing
    testing_parser = subparser.add_parser("test")
    testing_parser.set_defaults(func = do_test)



    #Process args.
    args = main_parser.parse_args()
    args.func(args)


    




if __name__ == "__main__":
    main()
