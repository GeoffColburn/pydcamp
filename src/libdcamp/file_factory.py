#!/usr/bin/env python
import os, sys
import glob
import re
from collections import defaultdict

from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff
from libdcamp.file_wrangler import FileWrangler

class FileFactory:
    def __init__(self):
        self.settings = Settings.instance()

    def write_validation_table(self, job_paths): 
        table = open(self.settings.job_validation_table_path, 'w')
        table.write("run_name\tpipeline\tTP\tFN\tFP\n")

        wrangler = FileWrangler(job_paths, "comp.gd")

        for job_id, run_id, path in wrangler:
            if wrangler.file_exists(job_id, run_id):
                gd = GenomeDiff(path)
                header_info = gd.header_info()
                assert "TP|FN|FP" in header_info.other
                validation = header_info.other["TP|FN|FP"].split('|')
                tp = validation[0]
                fn = validation[1]
                fp = validation[2]
                table.write("{}\t{}\t{}\t{}\t{}\n".format(run_id, job_id, tp, fn, fp))
            else:
                table.write("{}\t{}\t'-'\t'-'\t'-'\n".format(run_id, job_id))
        table.close()




