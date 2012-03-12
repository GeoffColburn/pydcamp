#!/usr/bin/env python
import os
import glob

class Settings:
    __instance = None

    def __init__(self, args):

        assert Settings.__instance == None

        self.data      = args.data
        self.downloads = args.downloads
        self.output    = args.output
        self.logs      = args.logs
        self.results   = args.results 

        self.name      = args.name 
        self.job_paths = args.job_paths

        self.job_dir = os.path.join(self.results, self.name)

        self.shared_dir_path = os.path.join(os.environ["HOME"], "local/share/dcamp")
        self.shared_css_style_pth = os.path.join(self.shared_dir_path, "dcamp/style.css")

        #Data:
        self.data_ctrl_gd_fmt = os.path.join(self.data, "{}.gd")
        self.ctrl_gd_fmt = os.path.join(self.data, "{}.gd")


        #Output:
        self.output_gd_fmt = os.path.join(self.output, "{}/{}/output/output.gd")
        self.output_vcf_fmt = os.path.join(self.output, "{}/{}/output/output.vcf")

        #Logs:
        self.logs_log_fmt = os.path.join(self.logs, "{}/{}.log.txt")

        #Results::Original
        self.results_test_gd_fmt    = os.path.join(self.results, "{}/{}/test.gd")
        self.results_ctrl_gd_fmt = os.path.join(self.results, "{}/{}/control.gd")
        self.results_comp_gd_fmt    = os.path.join(self.results, "{}/{}/comp.gd")

        self.results_orig_test_gd_fmt = os.path.join(self.results, "{}/{}/orig_test.gd")
        self.results_orig_test_af_099_gd_fmt = os.path.join(self.results, "{}/{}/orig_test_af_099.gd")
        self.results_orig_test_af_100_gd_fmt = os.path.join(self.results, "{}/{}/orig_test_af_100.gd")
        self.results_orig_ctrl_gd_fmt = os.path.join(self.results, "{}/{}/orig_ctrl.gd")
        self.results_log_fmt = os.path.join(self.results, "{}/{}/log.txt")
        self.results_error_log_fmt = os.path.join(self.results, "{}/{}/error_log.txt")
        #Results::Normalized
        self.results_norm_test_gd_fmt = os.path.join(self.results, "{}/{}/norm_test.gd")
        self.results_norm_test_af_099_gd_fmt = os.path.join(self.results, "{}/{}/norm_test_af_099.gd")
        self.results_norm_test_af_100_gd_fmt = os.path.join(self.results, "{}/{}/norm_test_af_100.gd")
        self.results_norm_ctrl_gd_fmt = os.path.join(self.results, "{}/{}/norm_ctrl.gd")
        #Results::Compared
        self.results_comp_orig_test_gd_fmt = os.path.join(self.results, "{}/{}/comp_orig_test.gd")
        self.results_comp_orig_test_af_099_gd_fmt = os.path.join(self.results, "{}/{}/comp_orig_test_af_099.gd")
        self.results_comp_orig_test_af_100_gd_fmt = os.path.join(self.results, "{}/{}/comp_orig_test_af_100.gd")
        self.results_comp_norm_test_gd_fmt = os.path.join(self.results, "{}/{}/comp_norm_test.gd")
        self.results_comp_norm_test_af_099_gd_fmt = os.path.join(self.results, "{}/{}/comp_norm_test_af_099.gd")
        self.results_comp_norm_test_af_100_gd_fmt = os.path.join(self.results, "{}/{}/comp_norm_test_af_100.gd")
        #Results::Dcamp
        self.results_dcamp = os.path.join(self.results, "dcamp")
        self.results_index_pth = os.path.join(self.results, "index.html")
        self.results_dcamp_validation_table_pth = os.path.join(self.results_dcamp, "validation_table.txt")
        self.results_dcamp_paths_db_pth = os.path.join(self.results_dcamp, "paths.db")
        self.results_dcamp_css_pth = os.path.join(self.results_dcamp, "style.css")
        self.results_dcamp_validation_pth = os.path.join(self.results_dcamp, "validation.html")
        self.results_dcamp_prediction_pth = os.path.join(self.results_dcamp, "prediction.html")
        self.results_dcamp_genome_diff_compare_fmt = os.path.join(self.results_dcamp, "{}.html")



        Settings.__instance = self

    @staticmethod
    def instance():
        assert Settings.__instance != None
        return Settings.__instance
    
    @staticmethod
    def JobPaths(job_id, run_id):
        settings = Settings.instance()
        dir = os.path.join(settings.job_dir, "{}/{}".format(job_id, run_id))
        return (os.path.join(dir, "ctrl.gd"), os.path.join(dir, "test.gd"), os.path.join(dir, "comp.gd"))

        def makedirs(self):
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)


        def __iter__(self):
            return self.data.__iter()


    def create_results_dir(self):
        #Pipeline directories
        for path in glob.glob(os.path.join(self.output, '*/*')):
            new_path = path.replace(self.output, self.results)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
        #Dcamp
        if not os.path.exists(self.results_dcamp):
            os.makedirs(self.results_dcamp)


