#!/usr/bin/env python
import sys, os
import sqlite3
import glob
import shutil
import argparse

import breseq.command
from libdcamp.settings import Settings
from breseq.genome_diff import GenomeDiff
from libdcamp.html_factory import HtmlFactory


class Job:
    class Status:
        FAILED = "FAILED"
        COMPLETED = "COMPLETED"
        NO_CONTROL = "NO_CONTROL"
    
    class VcfOption:
        NONE   = ""
        AF_100 = "--AF-100"
        AF_099 = "--AF-099"

    def __init__(self, settings = Settings()): 
        self.settings = settings
        self.pipelines = list()
        for path in glob.glob(os.path.join(self.settings.output, '*')):
            self.pipelines.append(os.path.basename(path))

        #Setup Database, each pipeline has it's own table:
        #self.con = sqlite3.connect(":memory:")
        self.con = sqlite3.connect(self.settings.results_dcamp_paths_db_pth)
        self.cur = self.con.cursor()
        for pipeline in self.pipelines:
            self.cur.execute("""create table if not exists {} 
                    (run_name text primary key,
                    status text,
                    orig_ctrl_gd text,
                    orig_test_vcf text,
                    orig_test_gd text,
                    orig_test_af_099_gd text,
                    orig_test_af_100_gd text,

                    norm_ctrl_gd text,
                    norm_test_gd text,
                    norm_test_af_099_gd text,
                    norm_test_af_100_gd text,

                    comp_orig_test_gd text,
                    comp_orig_test_af_099_gd text,
                    comp_orig_test_af_100_gd text,
                    comp_norm_test_gd text,
                    comp_norm_test_af_099_gd text,
                    comp_norm_test_af_100_gd text,

                    log text)""".format(pipeline))

    def RunHasCompleted(self, pipeline, run_name):
        if pipeline.lower() == "breseq":
            return os.path.exists(self.settings.output_gd_fmt.format(pipeline, run_name, "output"))
        else:
            return os.path.exists(self.settings.output_gd_fmt.format(pipeline, run_name, run_name)) or\
                   os.path.exists(self.settings.output_vcf_fmt.format(pipeline, run_name, run_name))

#Paths database methods.
    def SetupPathsDataBase(self):
        paths = glob.glob(os.path.join(self.settings.output, "*/*"))
        for path in paths:
            tokens = path.split('/')
            pipeline = tokens.pop(1)
            run_name = tokens.pop(1)
            self.cur.execute("insert or replace into {} (run_name) values(?)".format(pipeline), [run_name])

    def TablesInDb(self):
        ret_val = list()
        for table in self.cur.execute("select name from sqlite_master where type='table'"):
            ret_val.append(table[0])
        return ret_val

    def RunNamesInDbTable(self, table):
        ret_val = list()
        for run_name in self.cur.execute("select run_name from {}".format(table)):
            ret_val.append(run_name[0])
        return ret_val
    
    def CommitDb(self):
        self.con.commit()


#File handling methods.
#Step 1
    def HandleBreseqOrigTestGds(self, verbose = True): 
        """Your starting point for the breseq pipeline... This needs to run first to determined
        which runs have been COMPLETED; determined by if there exists a finale genome diff file."""
        for pipeline in self.TablesInDb():
            if pipeline.lower() != "breseq": continue
            self.cur.execute("select run_name from {}".format(pipeline))
            for run_name, in self.cur.fetchall():
                status = Job.Status.FAILED
                if self.RunHasCompleted(pipeline, run_name):
                    status = Job.Status.COMPLETED
                    old_path = self.settings.output_gd_fmt.format(pipeline, run_name, "output")
                    new_path = self.settings.results_orig_test_gd_fmt.format(pipeline, run_name)

                    if not os.path.exists(new_path):
                        shutil.copy2(old_path, new_path)
                    self.cur.execute("update {} set orig_test_gd = ? where run_name = ?"\
                            .format(pipeline), (new_path, run_name))
                else:
                    status = Job.Status.FAILED

                self.cur.execute("update {} set status = ? where run_name = ?"\
                        .format(pipeline), (status, run_name))
#Step 1.1
    def HandleTestVcfs(self):
        """Your starting point for the pipelines that output a vcf file(gatk and samtools)... 
        This needs to run first to determined which runs have been COMPLETED; determined by if
        there exists a finale vcf file."""
        for pipeline in self.TablesInDb():
            if pipeline.lower() == "breseq": continue
            self.cur.execute("select run_name from {}".format(pipeline))
            for run_name, in self.cur.fetchall():
                old_path = self.settings.output_vcf_fmt.format(pipeline, run_name, run_name)
                status = Job.Status.COMPLETED if os.path.exists(old_path) else Job.Status.FAILED
                if status == Job.Status.COMPLETED:
                    new_path = self.settings.results_orig_test_vcf_fmt.format(pipeline, run_name)
                    if not os.path.exists(new_path):
                        shutil.copy2(old_path, new_path)
                    self.cur.execute("update {} set orig_test_vcf = ?, status = ? where run_name = ?"\
                            .format(pipeline), [new_path, status, run_name])
                else:
                    self.cur.execute("update {} set status = ? where run_name = ?"\
                            .format(pipeline), [status, run_name])
#Step 1.2
    def HandleConvertVcfsToGds(self, vcf_option):
        """Convert all vcf files into genome diff files, it looks in the results directory for the vcf 
        file so HandleTestVcfs() needs to run first. Currently we allow for 3 options:
            1) Allow all entries.
            2) Allow only entries with an AF or AF1 value of 1.00. 
            3) Allow only entries with an AF or AF1 values less than 1.00. 
            """
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, orig_test_vcf from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, orig_test_vcf in self.cur.fetchall():
                new_path = ""
                key = ""
                if vcf_option == Job.VcfOption.NONE:
                    new_path = self.settings.results_orig_test_gd_fmt.format(pipeline, run_name)
                    key = "orig_test_gd"
                if vcf_option == Job.VcfOption.AF_099:
                    new_path = self.settings.results_orig_test_af_099_gd_fmt.format(pipeline, run_name)
                    key = "orig_test_af_099_gd"
                if vcf_option == Job.VcfOption.AF_100:
                    new_path = self.settings.results_orig_test_af_100_gd_fmt.format(pipeline, run_name)
                    key = "orig_test_af_100_gd"
                assert new_path

                if not os.path.exists(new_path):
                    breseq.command.vcf2gd(orig_test_vcf, new_path, vcf_option)

                self.cur.execute("update {} set {} = ? where run_name = ?"\
                        .format(pipeline, key), [new_path, run_name])
#Step 1.3
    def HandleOrigCtrlGds(self):
        """ Run the HandleTest methods first to determine which control genome diffs we need to
        evaluate, then set status = NO_CONTROL if there is no control genome_diff in
        the self.settings.data directory. Then moves and renames the control genome diffs
        to the appropriate results directory."""
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, status from {}".format(pipeline))
            for run_name, status in self.cur.fetchall():
                if status != Job.Status.COMPLETED: continue
                old_path = self.settings.data_ctrl_gd_fmt.format(run_name)
                new_path = self.settings.results_orig_ctrl_gd_fmt.format(pipeline, run_name)
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    shutil.copy2(old_path, new_path)
                if not os.path.exists(old_path):
                    status = Job.Status.NO_CONTROL

                self.cur.execute("update {} set orig_ctrl_gd = ?, status = ? where run_name = ?"\
                        .format(pipeline), [new_path, status, run_name])

#File normalizing methods.
#Step 2.X
    def HandleNormCtrlGds(self):
        """Normalize the control genome diff file, get the reference sequences from it's header 
        info and then look in the self.settings.downloads directory for it."""
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, orig_ctrl_gd from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, orig_ctrl_gd in self.cur.fetchall():
                #Get reference sequences file paths from the control gd.
                gd = GenomeDiff(orig_ctrl_gd)
                tokens = gd.header_info().ref_seqs
                ref_seq_paths = list()
                for token in tokens:
                    file_name = os.path.basename(token)
                    ref_seq_paths.append(os.path.join(self.settings.downloads, file_name))
                assert ref_seq_paths

                new_path = self.settings.results_norm_ctrl_gd_fmt.format(pipeline, run_name)
                if not os.path.exists(new_path):
                    breseq.command.normalize_gd(orig_ctrl_gd, ref_seq_paths, new_path)
                self.cur.execute("update {} set norm_ctrl_gd = ?"\
                        .format(pipeline), [new_path])
                

#Step 2.X
    def HandleNormTestGds(self):
        """Normalize orig_test_gd, orig_test_af_099_gd and orig_test_af_100_gd, we'll also need to 
        grab the orig_ctrl_gd for it's header information to determine what reference sequence files
        the genome diffs need to be normalized to and then look in the self.settings.downloads 
        directory for that file."""
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, orig_test_gd, orig_test_af_099_gd, orig_test_af_100_gd,\
                    orig_ctrl_gd from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, orig_test_gd, orig_test_af_099_gd, orig_test_af_100_gd,\
                    orig_ctrl_gd in self.cur.fetchall():
                #Get reference sequences file paths from the control gd.
                gd = GenomeDiff(orig_ctrl_gd)
                tokens = gd.header_info().ref_seqs
                ref_seq_paths = list()
                for token in tokens:
                    file_name = os.path.basename(token)
                    ref_seq_paths.append(os.path.join(self.settings.downloads, file_name))
                assert ref_seq_paths

                test_path = self.settings.results_norm_test_gd_fmt.format(pipeline, run_name)
                test_af_099_path = self.settings.results_norm_test_af_099_gd_fmt.format(pipeline, run_name)
                test_af_100_path = self.settings.results_norm_test_af_100_gd_fmt.format(pipeline, run_name)

                if not os.path.exists(test_path):
                    breseq.command.normalize_gd(orig_test_gd, ref_seq_paths, test_path)

                if not os.path.exists(test_af_099_path):
                    breseq.command.normalize_gd(orig_test_af_099_gd, ref_seq_paths, test_af_099_path)

                if not os.path.exists(test_af_100_path):
                    breseq.command.normalize_gd(orig_test_af_100_gd, ref_seq_paths, test_af_100_path)

                self.cur.execute("update {} set norm_test_gd = ?, norm_test_af_099_gd = ?,\
                        norm_test_af_100_gd = ? where run_name = ?"\
                        .format(pipeline), [test_path, test_af_099_path, test_af_100_path, run_name])

#File compare methods.
#Step 3
    def HandleCompOrigGds(self):
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, orig_test_gd, orig_test_af_099_gd, orig_test_af_100_gd,\
                    orig_ctrl_gd from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, orig_test_gd, orig_test_af_099_gd, orig_test_af_100_gd,\
                    orig_ctrl_gd in self.cur.fetchall():

                test_path = self.settings.results_comp_orig_test_gd_fmt.format(pipeline, run_name)
                test_af_099_path = self.settings.results_comp_orig_test_af_099_gd_fmt.format(pipeline, run_name)
                test_af_100_path = self.settings.results_comp_orig_test_af_100_gd_fmt.format(pipeline, run_name)

                if not os.path.exists(test_path):
                    breseq.command.compare_gd(orig_ctrl_gd, orig_test_gd, test_path)

                if not os.path.exists(test_af_099_path):
                    breseq.command.compare_gd(orig_ctrl_gd, orig_test_gd, test_af_099_path)

                if not os.path.exists(test_af_100_path):
                    breseq.command.compare_gd(orig_ctrl_gd, orig_test_gd, test_af_100_path)
                            
                self.cur.execute("update {} set comp_orig_test_gd = ?, comp_orig_test_af_099_gd = ?,\
                        comp_orig_test_af_100_gd = ? where run_name = ?"\
                        .format(pipeline), [test_path, test_af_099_path, test_af_100_path, run_name])

#Step 3
    def HandleCompNormGds(self):
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name, norm_test_gd, norm_test_af_099_gd, norm_test_af_100_gd,\
                    norm_ctrl_gd from {} where status = ?"\
                    .format(pipeline), [Job.Status.COMPLETED])
            for run_name, norm_test_gd, norm_test_af_099_gd, norm_test_af_100_gd,\
                    norm_ctrl_gd in self.cur.fetchall():

                test_path = self.settings.results_comp_orig_test_gd_fmt.format(pipeline, run_name)
                test_af_099_path = self.settings.results_comp_orig_test_af_099_gd_fmt.format(pipeline, run_name)
                test_af_100_path = self.settings.results_comp_orig_test_af_100_gd_fmt.format(pipeline, run_name)

                if not os.path.exists(test_path):
                    breseq.command.compare_gd(norm_ctrl_gd, norm_test_gd, test_path)

                if not os.path.exists(test_af_099_path):
                    breseq.command.compare_gd(norm_ctrl_gd, norm_test_gd, test_af_099_path)

                if not os.path.exists(test_af_100_path):
                    breseq.command.compare_gd(norm_ctrl_gd, norm_test_gd, test_af_100_path)
                            
                self.cur.execute("update {} set comp_norm_test_gd = ?, comp_norm_test_af_099_gd = ?,\
                        comp_norm_test_af_100_gd = ? where run_name = ?"\
                        .format(pipeline), [test_path, test_af_099_path, test_af_100_path, run_name])


    def HandleLogs(self, verbose = True):
        for pipeline in self.TablesInDb():
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

    def TestDB(self): 
#        for table in self.TablesInDb():
#            for run_name, in self.cur.execute("select run_name from {} where status = ?"\
#                    .format(table), [Job.Status.FAILED]):
#                print run_name

       for table in self.TablesInDb():
            for row in self.cur.execute("select * from {}".format(table)):
                print row

       #     #for run_name in self.RunNamesInDbTable("breseq"):
                
def do_gather_results(): 
    """Step 1 After a TACC job, moves, renames and converts files output from 
    different pipelines and put them in the 'results' directory."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",      dest = "data",      default = "01_Data")
    parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    parser.add_argument("--output",    dest = "output",    default = "03_Output")
    parser.add_argument("--logs",      dest = "logs",      default = "04_Logs")
    parser.add_argument("--results",   dest = "results",   default = "05_Results")
    args = parser.parse_args()

    settings = Settings(args.data, args.downloads, args.output, args.logs, args.results)
    settings.CreateResultsDir()
    job = Job(settings)
    job.SetupPathsDataBase()

    ##Step 1: Original.
    job.HandleLogs()
    job.HandleBreseqOrigTestGds()
    job.HandleTestVcfs()
    job.HandleOrigCtrlGds()
    job.HandleConvertVcfsToGds(Job.VcfOption.NONE)          
    job.HandleConvertVcfsToGds(Job.VcfOption.AF_099)    
    job.HandleConvertVcfsToGds(Job.VcfOption.AF_100)            
    job.CommitDb()


def do_normalize_results():
    """Step 2 After a TACC job, normalizes files in the results directory and parses the
    'downloads' directory for sequence files to normalize with."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",      dest = "data",      default = "01_Data")
    parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    parser.add_argument("--output",    dest = "output",    default = "03_Output")
    parser.add_argument("--logs",      dest = "logs",      default = "04_Logs")
    parser.add_argument("--results",   dest = "results",   default = "05_Results")
    args = parser.parse_args()

    settings = Settings(args.data, args.downloads, args.output, args.logs, args.results)
    settings.CreateResultsDir()
    job = Job(settings)

    #Step 2: Normalize.
    job.HandleNormCtrlGds()
    job.HandleNormTestGds()

    job.CommitDb()

def do_compare_results():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",      dest = "data",      default = "01_Data")
    parser.add_argument("--downloads", dest = "downloads", default = "02_Downloads")
    parser.add_argument("--output",    dest = "output",    default = "03_Output")
    parser.add_argument("--logs",      dest = "logs",      default = "04_Logs")
    parser.add_argument("--results",   dest = "results",   default = "05_Results")
    args = parser.parse_args()

    settings = Settings(args.data, args.downloads, args.output, args.logs, args.results)
    settings.CreateResultsDir()
    job = Job(settings)

    ##Step 3: Compare.
    job.HandleCompCtrlGds()
    job.HandleCompTestGds()

    job.CommitDb()
    

def main():
    command = sys.argv.pop(1).lower()

    if command == "gather-results": do_gather_results()
    if command == "normalize-results": do_normalize_results()
    if command == "compare-results": do_compare_results()

    
    #html_factory = HtmlFactory(settings)
    ##html_factory.CreateIndexPage("index.html")
    #html_factory.CreateValidationPage("index.html")






if __name__ == "__main__":
    main()
