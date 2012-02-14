#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse

import breseq.command
import extern.samtools as samtools
import pipelines.common

from libdcamp.settings import Settings
from libdcamp.html_factory import HtmlFactory
from libdcamp.job import Job


                
def do_results(args):
    settings = Settings(args.data, args.downloads, args.output, args.logs, args.results)
    settings.create_results_dir()
    job = Job(settings)
    job.setup_paths_database()

    if args.action == "convert" or args.action == "process":
        job.handle_breseq_orig_test_gds()
        job.handle_test_vcfs()
        job.handle_orig_ctrl_gds()
        job.handle_convert_vcfs_to_gds(Job.VcfOption.NONE)          
        job.handle_convert_vcfs_to_gds(Job.VcfOption.AF_099)    
        job.handle_convert_vcfs_to_gds(Job.VcfOption.AF_100)            
        job.handle_logs()

    if args.action == "normalize" or args.action == "process":
        job.handle_norm_ctrl_gds()
        job.handle_norm_test_gds()

    if args.action == "compare" or args.action == "process":
        job.handle_comp_orig_gds()
        job.handle_comp_norm_gds()
    
    job.commit_db()

def do_create_alignment(args):
    fasta_path = pipelines.common.prepare_reference(args, "01_reference_conversion")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "02_reference_alignment")

def do_samtools(args):
    fasta_path = pipelines.common.prepare_reference(args, "01_reference_conversion")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "02_reference_alignment")

    step_3_dir = os.path.join(args.output_dir, "output")
    step_3_file = os.path.join(step_3_dir, "output.done")

    vcf_path = os.path.join(step_3_dir, "output.vcf")
    gd_path = os.path.join(step_3_dir, "output.gd")
    if not os.path.exists(step_3_file):
        print "++Step 3 mutation predictions and output started."
        if not os.path.exists(step_3_dir):
            os.makedirs(step_3_dir)
            
        #Step: Samtools: Mutation prediction.
        if not os.path.exists(vcf_path):
            samtools.mpileup(fasta_path, sorted_bam_path, vcf_path)
        assert os.path.exists(vcf_path)
        
        #Step: Breseq: Convert VCF file to Genome Diff format.
        if not os.path.exists(gd_path):
            breseq.command.vcf2gd(vcf_path, gd_path)
        assert os.path.exists(gd_path)

def do_breakdancer(args): 
    fasta_path = pipelines.common.prepare_reference(args, "01_All")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "01_All")

    step_3_dir = os.path.join(args.output_dir, "01_All")
    step_3_file = os.path.join(step_3_dir, "output.done")

    if not os.path.exists(step_3_file):
        print "++Step 3 mutation predictions and output started."
        if not os.path.exists(step_3_dir):
            os.makedirs(step_3_dir)

        #shutil.copy2(sorted_bam_path, os.path.join(step_3_dir, os.path.basename(sorted_bam_path)))
        #sorted_bam_path = os.path.join(step_3_dir, os.path.basename(sorted_bam_path))
            
        #Breakdancer::bam2cfg.pl
        cfg_path = os.path.join(step_3_dir, "output.cfg")
        ##if not os.path.exists(cfg_path):
        #cwd = os.getcwd()
        #os.chdir(step_3_dir)
        cmd = "bam2cfg.pl -h -g {} > {}".format(sorted_bam_path, cfg_path)
        #cmd = "bam2cfg.pl -h -g {} > {}".format(os.path.basename(sorted_bam_path), os.path.basename(cfg_path))
        print cmd
        os.system(cmd)
        #os.chdir(cwd)
        #assert os.path.exists(cfg_path)

        ctx_path = os.path.join(step_3_dir, "output.ctx")
        ##if not os.path.exists(ctx_path):
        #cwd = os.getcwd()
        #os.chdir(step_3_dir)
        cmd = "breakdancer_max {} > {}".format(cfg_path, ctx_path)
        #cmd = "breakdancer_max {} > {}".format(os.path.basename(cfg_path), os.path.basename(ctx_path))
        print cmd
        os.system(cmd)
        #os.chdir(cwd)
        #assert os.path.exists(ctx_path)

def main():
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers()

    #Handle results.
    results_parser = subparser.add_parser("results")
    results_parser.add_argument("--data",      dest = "data",      default = "01_Data")
    results_parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    results_parser.add_argument("--output",    dest = "output",    default = "03_Output")
    results_parser.add_argument("--logs",      dest = "logs",      default = "04_Logs")
    results_parser.add_argument("--results",   dest = "results",   default = "05_Results")
    results_parser.add_argument("--action",    dest = "action",    default = "process", choices = ["convert", "normalize", "compare", "process"])
    results_parser.set_defaults(func = do_results)

    #Create alignment.
    create_alignment_parser = subparser.add_parser("create-alignment")
    create_alignment_parser.add_argument("-o", dest = "output_dir")
    create_alignment_parser.add_argument("-r", action = "append", dest = "ref_paths")
    create_alignment_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    create_alignment_parser.add_argument("read_paths", nargs = '+')
    create_alignment_parser.set_defaults(func = do_create_alignment)

    #Samtools pipeline.
    samtools_parser = subparser.add_parser("samtools")
    samtools_parser.add_argument("-o", dest = "output_dir")
    samtools_parser.add_argument("-r", action = "append", dest = "ref_paths")
    samtools_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    samtools_parser.add_argument("read_paths", nargs = '+')
    samtools_parser.set_defaults(func = do_samtools)

    #Breakdancer pipeline.
    breakdancer_parser = subparser.add_parser("breakdancer")
    breakdancer_parser.add_argument("-o", dest = "output_dir")
    breakdancer_parser.add_argument("-r", action = "append", dest = "ref_paths")
    breakdancer_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = True)
    breakdancer_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = False)
    breakdancer_parser.add_argument("read_paths", nargs = '+')
    breakdancer_parser.set_defaults(func = do_breakdancer)

    args = main_parser.parse_args()
    args.func(args)

    


    
    #html_factory = HtmlFactory(settings)
    ##html_factory.CreateIndexPage("index.html")
    #html_factory.CreateValidationPage("index.html")






if __name__ == "__main__":
    main()
