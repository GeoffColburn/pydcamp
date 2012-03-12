#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse
import re, fnmatch
from collections import defaultdict

import extern.libpp.pp as pp

import breseq.command

import libdcamp.common
from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff


class FileWrangler:
    def __init__(self, key):
        self.file_wrangle_fmt = os.path.join("{}/{}", key)
        self.data = list()
        self.status_data = defaultdict(dict)
        settings = Settings.instance()
        for job_path in settings.job_paths:
            job_path = job_path.strip('/')
            assert not job_path in self.status_data
            for path in glob.glob(self.file_wrangle_fmt.format(job_path, '*')):
                m = re.search(self.file_wrangle_fmt.format("(?P<job_id>\w+)", "(?P<run_id>\w+)"), path)
                if m:
                    self.data.append((m.group("job_id"), m.group("run_id"), path))
                    self.status_data[m.group("job_id")][m.group("run_id")] = Job.Status.COMPLETED

    def __iter__(self):
        return self.data.__iter__()


def handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite):
    if force_overwrite or not os.path.exists(results[0]):
        breseq.command.normalize_gd(ctrl_gd, ref_seqs, results[0])
    
    if force_overwrite or not os.path.exists(results[1]):
        breseq.command.normalize_gd(test_gd, ref_seqs, results[1])
    
    if force_overwrite or not os.path.exists(results[2]):
        breseq.command.compare_gd(results[0], results[1], results[2])

class Job:
    class Status:
        FAILED = "FAILED"
        COMPLETED = "COMPLETED"
        NO_CONTROL = "NO_CONTROL"
        NO_REFERENCE_FILE = "NO_REFERENCE_FILE"

    
    def __init__(self): 
        self.settings = Settings.instance()


    def handle_gds(self, job_paths, force_overwrite):
        test_wrangler = FileWrangler("output/output.gd")
        ppservers = ()
        job_server = pp.Server(ppservers=ppservers)
        jobs = list()

        print "Starting pp with", job_server.get_ncpus(), "Workers"

        for job_id, run_id, test_gd in test_wrangler:
            dir = os.path.join(self.settings.job_dir, "{}/{}".format(job_id, run_id))
            if not os.path.exists(dir):
                os.makedirs(dir)

            ctrl_gd = self.settings.ctrl_gd_fmt.format(run_id)
            ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(self.settings.downloads)

            results = Settings.JobPaths(job_id, run_id)
            #args = (ctrl_gd, test_gd, ref_seqs, results, force_overwrite,)
            #support_funcs = (breseq.command.normalize_gd,)
            #job = job_server.submit(handle_gd, args, support_funcs, ("os","breseq.command",))
            #jobs.append(job)
            handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite)




                #self.cur.execute("update {} set test_gd = ?, ctrl_gd = ?, comp_gd = ?, status = ? where run_name = ?"\
                #        .format(m.group("pipeline")), [results_test_gd_path, results_ctrl_gd_path, results_comp_gd_path, Job.Status.COMPLETED, m.group("run_name")])


            





