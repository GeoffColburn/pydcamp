#!/usr/bin/env python
import os
import glob

class Settings:
    __instance = None

    def __init__(self, args):

        assert Settings.__instance == None

        #Directories setup for dcamp.
        self.data      = args.data       #Holds control gds.
        self.downloads = args.downloads  #Holds Genbank and Fastq files.
        self.output    = args.output     #Holds output from pipeline runs, contains test gds.
        self.logs      = args.logs       #Holds sterr/stdout logs from pipelines runs.
        self.results   = args.results    #Holds post-pipeline job analysis files.
        
        #Output directories from pipelines.
        self.test_paths = args.test_paths 

        #Paths for this job, which will be put in the results directory.
        self.job_name = args.job_name 
        self.job_dir = os.path.join(self.results, self.job_name)
        self.job_css_path = os.path.join(self.job_dir, "dcamp/style.css")
        self.job_index_path = os.path.join(self.job_dir, "index.html")
        self.job_make_test_path = os.path.join(self.job_dir, "make_test.html")
        self.job_validation_table_path = os.path.join(self.job_dir, "dcamp/validation_table.txt")
        self.job_mutation_rates_table_path = os.path.join(self.job_dir, "dcamp/mutation_rates.txt")

        self.shared_dir_path = os.path.join(os.environ["HOME"], "local/share/dcamp")
        self.shared_css_style_pth = os.path.join(self.shared_dir_path, "dcamp/style.css")

        #Data:
        self.ctrl_gd_fmt = os.path.join(self.data, "{}.gd")

        #Output:
        self.output_gd_fmt = os.path.join(self.output, "{}/{}/output/output.gd")
        self.output_vcf_fmt = os.path.join(self.output, "{}/{}/output/output.vcf")

        #Logs:
        self.log_fmt = os.path.join(self.logs, "{}/{}.log.txt")

        Settings.__instance = self

    @staticmethod
    def instance():
        assert Settings.__instance != None
        return Settings.__instance
    
    def job_paths(self, job_id, run_id):
        dir = os.path.join(self.job_dir, "{}/{}".format(job_id, run_id))
        job_path = os.path.join(self.job_dir, job_id)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return (os.path.join(dir, "ctrl.gd"),\
                os.path.join(dir, "test.gd"),\
                os.path.join(dir, "comp.gd"),\
                job_path)



