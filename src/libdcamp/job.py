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
    def __init__(self, dir_paths, key):
        self.file_wrangle_fmt = os.path.join("{}/{}", key)
        self.data_list = list()
        self.data_dict = defaultdict(dict)
        self.job_ids = list()
        self.run_ids = list()
        seen_job_ids = set()
        seen_run_ids = set()
        for dir_path in dir_paths:
            dir_path = dir_path.strip('/')
            for path in glob.glob(self.file_wrangle_fmt.format(dir_path, '*')):
                m = re.search(self.file_wrangle_fmt.format("(?P<job_id>\w+)", "(?P<run_id>\w+)"), path)
                if m:
                    job_id = m.group("job_id")
                    run_id = m.group("run_id")
                    self.data_dict[job_id][run_id] = path
                    self.data_list.append((job_id, run_id, path))

                    #Unique values only.
                    if job_id not in seen_job_ids and not seen_job_ids.add(job_id):
                        self.job_ids.append(job_id)
                    if run_id not in seen_run_ids and not seen_run_ids.add(run_id):
                        self.run_ids.append(run_id)

        #Sort by run_ids numerically/alphabetically.
        self.data_list.sort(key = lambda x: x[1])
        self.run_ids.sort()

    def __iter__(self):
        return self.data_list.__iter__()

    def file_exists(self, job_id, run_id):
        return job_id in self.data_dict and run_id in self.data_dict[job_id]

    def get_file(self, job_id, run_id):
        if self.file_exists(job_id, run_id):
            return self.data_dict[job_id][run_id]
        else:
            return None

def handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite):
    try:
        if force_overwrite or not os.path.exists(results[0]):
            breseq.command.normalize_gd(ctrl_gd, ref_seqs, results[0])
        
        if force_overwrite or not os.path.exists(results[1]):
            breseq.command.normalize_gd(test_gd, ref_seqs, results[1])
        
        if force_overwrite or not os.path.exists(results[2]):
            breseq.command.compare_gd(results[0], results[1], results[2])

        return results[2]
    except:
        return None

class Job:
    class Status:
        FAILED = "FAILED"
        COMPLETED = "COMPLETED"
        NO_CONTROL = "NO_CONTROL"
        NO_REFERENCE_FILE = "NO_REFERENCE_FILE"

    
    def __init__(self): 
        self.settings = Settings.instance()


    def handle_gds(self, paths, force_overwrite):
        wrangler = FileWrangler(paths, "output/output.gd")
        
        if not os.path.exists(self.settings.job_dir):
            os.makedirs(self.settings.job_dir)

        ppservers = ()
        job_server = pp.Server(ppservers=ppservers)
        support_funcs = (breseq.command.normalize_gd,)
        support_mods = ("os", "breseq.command",)
        jobs = list()
        print "Starting pp with", job_server.get_ncpus(), "Workers"

        for job_id, run_id, test_gd in wrangler:
            ctrl_gd = self.settings.ctrl_gd_fmt.format(run_id)
            ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(self.settings.downloads)
            results = Settings.JobPaths(job_id, run_id)
            args = (ctrl_gd, test_gd, ref_seqs, results, force_overwrite,)
            jobs.append(job_server.submit(handle_gd, args, support_funcs, support_mods))

        for job in jobs:
            print job()

        job_server.print_stats()

        #for job_id, run_id, test_gd in wrangler:

        #ctrl_gd = self.settings.ctrl_gd_fmt.format(run_id)
        #ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(self.settings.downloads)

        #results = Settings.JobPaths(job_id, run_id)
        #args = (ctrl_gd, test_gd, ref_seqs, results, force_overwrite,)
        #support_funcs = (breseq.command.normalize_gd,)
        #job = job_server.submit(handle_gd, args, support_funcs, ("os","breseq.command",))

        #for job_id, run_id, test_gd in wrangler:

        #    ctrl_gd = self.settings.ctrl_gd_fmt.format(run_id)
        #    ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(self.settings.downloads)

        #    results = Settings.JobPaths(job_id, run_id)
        #    args = (ctrl_gd, test_gd, ref_seqs, results, force_overwrite,)
        #    support_funcs = (breseq.command.normalize_gd,)
        #    job = job_server.submit(handle_gd, args, support_funcs, ("os","breseq.command",))
        #    jobs.append(job)
        #    handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite)

        return [path.replace(self.settings.output, self.settings.job_dir) for path in paths]



                #self.cur.execute("update {} set test_gd = ?, ctrl_gd = ?, comp_gd = ?, status = ? where run_name = ?"\
                #        .format(m.group("pipeline")), [results_test_gd_path, results_ctrl_gd_path, results_comp_gd_path, Job.Status.COMPLETED, m.group("run_name")])


            





