#!/usr/bin/env 
import os

def configure(bam_path, out_cfg_path):
    cmd = "bam2cfg.pl -g -h {} > {}".format(bam_path, out_cfg_path)
    print cmd
    os.system(cmd)
    
