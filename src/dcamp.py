#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse

import breseq.command
import extern.samtools as samtools
import extern.gatk as gatk
import extern.picardtools as picardtools
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
        if not os.path.exists(step_3_dir): os.makedirs(step_3_dir)
            
        #Step: Samtools: Mutation prediction.
        if not os.path.exists(vcf_path):
            samtools.mpileup(fasta_path, sorted_bam_path, vcf_path)
        assert os.path.exists(vcf_path)
        
        #Step: Breseq: Convert VCF file to Genome Diff format.
        if not os.path.exists(gd_path):
            breseq.command.vcf2gd(vcf_path, gd_path)
        assert os.path.exists(gd_path)

def do_breakdancer(args): 
    """Believe we need to keep all files in one directory, although it's not mentioned,
    breakdancer may look at files other than the .bam file."""
    fasta_path = pipelines.common.prepare_reference(args, "01_All")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "01_All")
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

        """We need to change into the directory because breakdancer output's histogram
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



def do_gatk(args):
    fasta_path = pipelines.common.prepare_reference(args, "01_reference_conversion")
    sorted_bam_path = pipelines.common.create_alignment(args, fasta_path, "02_reference_alignment")
#Gatk
#Step 3
    step_3_dir = os.path.join(args.output_dir, "03_gatk")
    step_3_file = os.path.join(step_3_dir, "gatk.done")
    if not os.path.exists(step_3_file):
        print "++Step 3 mutation predictions and output started."
        if not os.path.exists(step_3_dir):
            os.makedirs(step_3_dir)
            
        #Step: Samtools: Index BAM.
        sorted_bam_path = samtools.index(sorted_bam_path)
        
        #Step: Gatk: Intervals.
        intervals_path = gatk.realigner_target_creator(fasta_path, sorted_bam_path)
        
        #Step: Gatk: Indel Realigner.
        realigned_bam_path = gatk.indel_realigner(fasta_path, sorted_bam_path, intervals_path)
        
        #Step: Picardtools: Validate alignment.
        picardtools.validate_alignment(realigned_bam_path)
        
#Gatk Output
#Step 4
    output_dir = os.path.join(args.output_dir, "output")
    vcf_path = os.path.join(output_dir, "output.vcf")
    gd_path = os.path.join(output_dir, "output.gd")

    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    gatk.unified_genotyper(fasta_path, realigned_bam_path, vcf_path)
    breseq.command.vcf2gd(vcf_path, gd_path)


def main():
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers()

    #results.
    results_parser = subparser.add_parser("results")
    results_parser.add_argument("--data",      dest = "data",      default = "01_Data")
    results_parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    results_parser.add_argument("--output",    dest = "output",    default = "03_Output")
    results_parser.add_argument("--logs",      dest = "logs",      default = "04_Logs")
    results_parser.add_argument("--results",   dest = "results",   default = "05_Results")
    results_parser.add_argument("--action",    dest = "action",    default = "process", choices = ["convert", "normalize", "compare", "process"])
    results_parser.set_defaults(func = do_results)

    #create-alignment.
    create_alignment_parser = subparser.add_parser("create-alignment")
    create_alignment_parser.add_argument("-o", dest = "output_dir")
    create_alignment_parser.add_argument("-r", action = "append", dest = "ref_paths")
    create_alignment_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    create_alignment_parser.add_argument("read_paths", nargs = '+')
    create_alignment_parser.set_defaults(func = do_create_alignment)

    #samtools.
    samtools_parser = subparser.add_parser("samtools")
    samtools_parser.add_argument("-o", dest = "output_dir")
    samtools_parser.add_argument("-r", action = "append", dest = "ref_paths")
    samtools_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    samtools_parser.add_argument("read_paths", nargs = '+')
    samtools_parser.set_defaults(func = do_samtools)

    #breakdancer.
    breakdancer_parser = subparser.add_parser("breakdancer")
    breakdancer_parser.add_argument("-o", dest = "output_dir")
    breakdancer_parser.add_argument("-r", action = "append", dest = "ref_paths")
    breakdancer_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = True)
    breakdancer_parser.add_argument("--sort_bam", action = "store_true", dest = "sort_bam", default = True)
    breakdancer_parser.add_argument("read_paths", nargs = '+')
    breakdancer_parser.set_defaults(func = do_breakdancer)

    #gatk.
    gatk_parser = subparser.add_parser("gatk")
    gatk_parser.add_argument("-o", dest = "output_dir")
    gatk_parser.add_argument("-r", action = "append", dest = "ref_paths")
    gatk_parser.add_argument("--pair-ended", action = "store_true", dest = "pair_ended", default = False)
    gatk_parser.add_argument("read_paths", nargs = '+')
    gatk_parser.set_defaults(func = do_gatk)

    args = main_parser.parse_args()
    args.func(args)

    


    
    #html_factory = HtmlFactory(settings)
    ##html_factory.CreateIndexPage("index.html")
    #html_factory.CreateValidationPage("index.html")






if __name__ == "__main__":
    main()
