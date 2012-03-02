#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse
import re, fnmatch

import breseq.command

import libdcamp.common
from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff


class Job:
    class Status:
        FAILED = "FAILED"
        COMPLETED = "COMPLETED"
        NO_CONTROL = "NO_CONTROL"
        NO_REFERENCE_FILE = "NO_REFERENCE_FILE"
    
    class VcfOption:
        NONE   = ""
        AF_100 = "--AF-100"
        AF_099 = "--AF-099"

    def __init__(self, settings = Settings()): 
        self.settings = settings
        self.pipelines = list()

        self.con = sqlite3.connect(self.settings.results_dcamp_paths_db_pth)
        self.cur = self.con.cursor()
        for path in glob.glob(os.path.join(self.settings.output, '*')):
            m = re.match("^.*\/(?P<pipeline>\w+)", path)
            if m:
                self.cur.execute("""create table if not exists {} 
                    (run_name text primary key,
                     status text,
                     test_gd text,
                     ctrl_gd text,
                     comp_gd text,
                     log text)""".format(m.group("pipeline")))

    def run_has_completed(self, pipeline, run_name):
        if pipeline.lower() == "breseq":
            return os.path.exists(self.settings.output_gd_fmt.format(pipeline, run_name, "output"))
        else:
            return os.path.exists(self.settings.output_gd_fmt.format(pipeline, run_name, run_name)) or\
                   os.path.exists(self.settings.output_vcf_fmt.format(pipeline, run_name, run_name))

#Paths database methods.
    def setup_paths_database(self):
        for path in glob.glob(os.path.join(self.settings.output, "*/*")):
            m = re.match("^.*\/(?P<pipeline>\w+)\/(?P<run_name>\w+)", path)
            if m:
                self.cur.execute("insert or replace into {} (run_name) values(?)".format(m.group("pipeline")), [m.group("run_name")])

    def tables_in_db(self):
        ret_val = list()
        for table in self.cur.execute("select name from sqlite_master where type='table'"):
            ret_val.append(table[0])
        return ret_val

    def run_names_in_db_table(self, table):
        ret_val = list()
        for run_name in self.cur.execute("select run_name from {}".format(table)):
            ret_val.append(run_name[0])
        return ret_val
    
    def commit_db(self):
        self.con.commit()
        self.cur.close()

    def completed_run_names_in_db(self):
        ret_val = list()
        for pipeline in self.tables_in_db():
            self.cur.execute("select run_name from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, in self.cur.fetchall():
                if run_name not in ret_val:
                    ret_val.append(run_name)
        ret_val.sort()
        return ret_val




    def handle_logs(self):
        for pipeline in self.tables_in_db():
            self.cur.execute("select run_name, status from {}".format(pipeline))
            for run_name, status in self.cur.fetchall():
                old_path = self.settings.logs_log_fmt.format(pipeline, run_name)
                new_path = ""
                if status == Job.Status.COMPLETED:
                    new_path = self.settings.results_log_fmt.format(pipeline, run_name)
                else:
                    new_path = self.settings.results_error_log_fmt.format(pipeline, run_name)
                assert new_path
                #Copy file to results dir.
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    shutil.copy2(old_path, new_path)
                self.cur.execute("update {} set log = ? where run_name = ?".format(pipeline), (new_path, run_name))

    def compare_gds(self):
        for run_name in self.completed_run_names_in_db():
            gd_paths = list()
            for pipeline in self.tables_in_db():
                self.cur.execute("select comp_gd from {} where run_name = ?"\
                        .format(pipeline), [run_name])
                gd_path, = self.cur.fetchone()
                gd_paths.append(gd_path)

            ctrl_gd_path = self.settings.data_ctrl_gd_fmt.format(run_name)
            ref_seqs = GenomeDiff(ctrl_gd_path).ref_sequence_file_names()

            for i, ref_seq in enumerate(ref_seqs):
                ref_seqs[i] = os.path.join(self.settings.downloads, ref_seq)
                if not os.path.exists(ref_seqs[i]):
                    print ref_seqs[i], ctrl_gd_path
                    sys.exit(1)
            
            output_path = self.settings.results_dcamp_genome_diff_compare_fmt.format(run_name)
            if not os.path.exists(output_path):
                breseq.command.genome_diff_compare(output_path, ref_seqs, gd_paths) 

            for pipeline in self.tables_in_db():
                self.cur.execute("update {} set genome_diff_comp_html = ? where run_name = ?"\
                        .format(pipeline), [output_path, run_name])

    def test_db(self): 
       for table in self.tables_in_db():
            for row in self.cur.execute("select * from {}".format(table)):
                print row


    def handle_gds(self):
        for test_gd_path in libdcamp.common.locate("output.gd", self.settings.output):
            m = re.match(".*\/(?P<pipeline>\w+)\/(?P<run_name>\w+)\/output\/output\.gd\Z(?ms)", test_gd_path)
            if m:
                ctrl_gd_path = os.path.join(self.settings.data, "{}.gd".format(m.group("run_name")))
                ref_seq_paths = GenomeDiff(ctrl_gd_path).ref_sequence_file_paths(self.settings.downloads)
                
                #Normalize ctrl.
                results_ctrl_gd_path = self.settings.results_ctrl_gd_fmt.format(m.group("pipeline"), m.group("run_name"))
                breseq.command.normalize_gd(ctrl_gd_path, ref_seq_paths, results_ctrl_gd_path)
                
                #Normalize test.
                results_test_gd_path = self.settings.results_test_gd_fmt.format(m.group("pipeline"), m.group("run_name"))
                breseq.command.normalize_gd(test_gd_path, ref_seq_paths, results_test_gd_path)

                #Compare test versus ctrl.
                results_comp_gd_path = self.settings.results_comp_gd_fmt.format(m.group("pipeline"), m.group("run_name"))
                breseq.command.compare_gd(results_ctrl_gd_path, results_test_gd_path, results_comp_gd_path)

                self.cur.execute("update {} set test_gd = ?, ctrl_gd = ?, comp_gd = ?, status = ? where run_name = ?"\
                        .format(m.group("pipeline")), [results_test_gd_path, results_ctrl_gd_path, results_comp_gd_path,Job.Status.COMPLETED, m.group("run_name")])


            





