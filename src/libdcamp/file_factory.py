#!/usr/bin/env python
import os, sys
import glob
import re

from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff
from libdcamp.job import Job
from collections import defaultdict

class FileFactory:
    def __init__(self, settings):
        self.settings = settings

    def collect_gd_data(self, key):
        ret_val = defaultdict(dict)
        for gd_path in glob.glob(os.path.join(self.settings.results, "*/*/{}".format(key))):
            #m = re.match("^.*\/(?P<pipeline>\w+)\/(?P<run_name>\w+)\/comp\.gd$", gd_path)
            m = re.match(r"^.*/(?P<pipeline>\w+)/(?P<run_name>\w+)/{}$".format(key), gd_path)
            if m:
                ret_val[m.group("run_name")][m.group("pipeline")] = gd_path

        return ret_val


    def write_validation_table(self, path, key = "comp.gd"): 
        table = open(path, 'w')
        #Header.
        table.write("run_name\tpipeline\tTP\tFN\tFP\n")

        #Lines
        gd_data = self.collect_gd_data(key)
        for run_name, gd_paths_dict in gd_data.iteritems():
            for pipeline, gd_path in gd_paths_dict.iteritems():
                gd = GenomeDiff(gd_path)
                assert "TP|FN|FP" in gd.header_info().other

                val = gd.header_info().other["TP|FN|FP"].split('|')
                table.write("{}\t{}\t{}\t{}\t{}\n".format(run_name, pipeline, val[0], val[1], val[2]))

        table.close()



