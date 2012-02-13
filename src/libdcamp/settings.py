#!/usr/bin/env python
import os
import glob

class Settings:
    def __init__(self,\
                 data = "01_Data",\
                 downloads = "02_Downloads",\
                 output = "03_Output",\
                 logs = "04_Logs",\
                 results = "05_Results"):

        #Data:
        self.data = data
        self.data_ctrl_gd_fmt = os.path.join(self.data, "{}.gd")

        #Downloads:
        self.downloads = downloads

        #Output:
        self.output = output
        self.output_gd_fmt = os.path.join(self.output, "{}/{}/output/{}.gd")
        self.output_vcf_fmt = os.path.join(self.output, "{}/{}/output/{}.vcf")

        #Logs:
        self.logs = logs
        self.logs_log_fmt = os.path.join(self.logs, "{}/{}.log.txt")

        #Results:
        self.results = results
        #Results::Original
        self.results_orig_test_vcf_fmt = os.path.join(self.results, "{}/{}/orig_test.vcf")
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
        self.results_index_pth = os.path.join(self.results, "index.html")
        self.results_dcamp = os.path.join(self.results, "dcamp")
        self.results_dcamp_paths_db_pth = os.path.join(self.results_dcamp, "paths.db")
        self.results_dcamp_css_pth = os.path.join(self.results_dcamp, "style.css")
        self.results_dcamp_validation_pth = os.path.join(self.results_dcamp, "validation.html")
        self.results_dcamp_validation_pth = os.path.join(self.results_dcamp, "validation.html")
        self.results_dcamp_validation_pth = os.path.join(self.results_dcamp, "validation.html")
        self.results_dcamp_prediction_pth = os.path.join(self.results_dcamp, "prediction.html")


    def CreateResultsDir(self):
        #Pipeline directories
        for path in glob.glob(os.path.join(self.output, '*/*')):
            new_path = path.replace(self.output, self.results)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
        #Dcamp
        if not os.path.exists(self.results_dcamp):
            os.makedirs(self.results_dcamp)


