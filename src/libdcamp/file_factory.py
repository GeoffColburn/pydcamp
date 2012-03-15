#!/usr/bin/env python
import os, sys
import glob
import re
from collections import defaultdict

from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff
from breseq.diff_entry import DiffEntry
from libdcamp.file_wrangler import FileWrangler

class FileFactory:
    def __init__(self):
        self.settings = Settings.instance()

    def write_validation_table(self, job_paths): 
        print "*** Writing {}".format(self.settings.job_validation_table_path)
        table = open(self.settings.job_validation_table_path, 'w')
        table.write("run_name\tpipeline\tTP\tFN\tFP\n")

        wrangler = FileWrangler(job_paths, "comp.gd")

        for job_id, run_id, path in wrangler:
            if wrangler.file_exists(job_id, run_id):
                gd = GenomeDiff(path, header_only = True)
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

    def write_mutation_rates_table(self, job_paths):
        print "*** Writing {}".format(self.settings.job_mutation_rates_table_path)
        table = open(self.settings.job_mutation_rates_table_path, 'w')

        mut_types = [type for type in DiffEntry.line_specs if len(type) == 3]
        table.write("run_name\tpipeline\t{}\n".format("\t".join(mut_types)))

        wrangler = FileWrangler(job_paths, "comp.gd")
        for run_id in wrangler.run_ids:
            for job_id in wrangler.job_ids:
                table.write("{}\t{}".format(run_id, job_id))

                if wrangler.file_exists(job_id, run_id):
                    path = wrangler.get_file(job_id, run_id)
                    gd = GenomeDiff(path)
                    header_info = gd.header_info()
                    assert "TP|FN|FP" in header_info.other
                    validation = header_info.other["TP|FN|FP"].split('|')
                    tp = validation[0]
                    fn = validation[1]
                    fp = validation[2]

                    for mut_type in mut_types:
                        n_tp = float(len([mut for mut in gd[mut_type] if "validation" in mut and mut["validation"] == "TP"]))
                        n_fn = float(len([mut for mut in gd[mut_type] if "validation" in mut and mut["validation"] == "FN"]))
                        n_fp = float(len([mut for mut in gd[mut_type] if "validation" in mut and mut["validation"] == "FP"]))
                        total = float(n_tp + n_fn + n_fp)
                        if total:
                            tdr = float(n_tp / total) * 100.0
                            tdr = round(tdr, 1)
                            table.write("\t{}".format(tdr))
                        else:
                            table.write("\t-")
                        
                else:
                    for i in mut_types:
                        table.write("\t-")

                table.write("\n")
        table.close()



