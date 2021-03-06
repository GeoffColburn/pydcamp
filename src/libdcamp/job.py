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
    #*** Attempt at parallelization.
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

    print "***Begin normalizing and comparing genome diffs."
    settings = Settings.instance()

    print "Searching output/output.gd in paths:"
    for path in test_paths:
        print "\t", path

    wrangler = FileWrangler(test_paths, "output/output.gd")

    assert len(wrangler.data_list), "No GDs found from, check REGEX expression in FileWrangler."

    print "Found files:"
    for job_id, run_id, test_gd in wrangler:
        print "[job_id]: {} [run_id]: {} [file]: {}".format(job_id, run_id, test_gd)
    
    if not os.path.exists(settings.job_dir):
        os.makedirs(settings.job_dir)


    job_paths = list()
    for job_id, run_id, test_gd in wrangler:
        ctrl_gd = settings.ctrl_gd_fmt.format(run_id)
        ref_seqs = GenomeDiff(ctrl_gd).ref_sequence_file_paths(settings.downloads)

        results = settings.job_paths(job_id, run_id)
        handle_gd(ctrl_gd, test_gd, ref_seqs, results, force_overwrite)
        job_paths.append(results[3])

    print "***End normalizing and comparing genome diffs."
    return job_paths

def handle_logs(test_paths, force_overwrite):
    print "***Handling stdout/sterr logs and determining failed tests."
    settings = Settings.instance()

    wrangler = FileWrangler(test_paths, "output/output.gd")

    for job_id, run_id, test_gd in wrangler:
        #Create log path string, depending on if the run completed or not.
        log_path = "log.txt" if os.path.exists(test_gd) else "error_log.txt"
        log_path = os.path.join(settings.job_paths(job_id, run_id)[3], log_path)
        #Copy log to above path
        shutil.copy2(settings.log_fmt.format(job_id, run_id), log_path)


