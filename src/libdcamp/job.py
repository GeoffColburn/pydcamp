#!/usr/bin/env python
import sys, os
import multiprocessing
from multiprocessing import Pool

import breseq.command
from breseq.genome_diff import GenomeDiff

from libdcamp.settings import Settings
from libdcamp.file_wrangler import FileWrangler


def handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite):
    if force_overwrite or not os.path.exists(results[0]):
        breseq.command.normalize_gd(ctrl_gd, ref_seqs, results[0])
    
    if force_overwrite or not os.path.exists(results[1]):
        breseq.command.normalize_gd(test_gd, ref_seqs, results[1])
    
    if force_overwrite or not os.path.exists(results[2]):
        breseq.command.compare_gd(results[0], results[1], results[2])

    return results[2]


def handle_gds(test_paths, force_overwrite):
    settings = Settings.instance()
    wrangler = FileWrangler(test_paths, "output/output.gd")
    
    if not os.path.exists(settings.job_dir):
        os.makedirs(settings.job_dir)

    #pool = Pool(multiprocessing.cpu_count())
    #job_paths = list()
    #args = list()
    #for job_id, run_id, test_gd in wrangler:
    #    ctrl_gd = settings.ctrl_gd_fmt.format(run_id)
    #    ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(settings.downloads)

    #    results = settings.job_paths(job_id, run_id)
    #    args.append((ctrl_gd, test_gd, ref_seqs, results, force_overwrite))
    #    job_paths.append(results[3])
    #
    #pool.map(handle_gd, args)

    job_paths = list()
    for job_id, run_id, test_gd in wrangler:
        ctrl_gd = settings.ctrl_gd_fmt.format(run_id)
        ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(settings.downloads)

        results = settings.job_paths(job_id, run_id)
        handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite)
        job_paths.append(results[3])

    return job_paths
