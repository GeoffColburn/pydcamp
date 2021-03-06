import os, sys
import re
import glob
from collections import defaultdict


def tree(): return defaultdict(tree)


class FileWrangler:
    def __init__(self, dir_paths, key):
        #Path to wrangle/search for.
        self.file_wrangle_fmt = os.path.join("{}/{}", key) 
        
        #Data structures for efficient access to paths.
        self.data_list = list()
        self.data_dict = defaultdict(dict)
        self.job_ids = list()
        self.run_ids = list()

        #Sets to collect only unique values for job_ids and run_ids.
        seen_job_ids = set()
        seen_run_ids = set()

        for dir_path in dir_paths:
            dir_path = dir_path.strip('/')
            job_id = dir_path.split('/').pop()
            for path in glob.glob(self.file_wrangle_fmt.format(dir_path, '*')):
                run_id = path[len(dir_path) + 1:].split('/').pop(0)
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

class Wrangler(defaultdict):
    def __init__(self, dir_paths, key):
        defaultdict.__init__(self, dict)
        self.data_list = list()
        self.job_ids = set()
        self.run_ids = set()

        dir_paths = [os.path.join(dir_path.strip('/'), key.strip('/')) for dir_path in dir_paths]
        for dir_path in dir_paths:
            for file_path in glob.glob(dir_path):
                tokens = file_path.split('/')
                comp_gd  = file_path
                run_name = tokens[-2]
                pipeline = tokens[-3]
                self[pipeline][run_name] = comp_gd
        for pipeline in self.keys():
            self.job_ids.add(pipeline)
            for run_name, file_path in self[pipeline].iteritems():
                self.data_list.append((pipeline, run_name, file_path))
                self.run_ids.add(run_name)

    def __iter__(self):
        return self.data_list.__iter__()

    def file_exists(self, pipeline, run_name):
        return pipeline in self.keys() and run_name in self[pipeline].keys()

    def get_file(self, pipeline, run_name):
        if self.file_exists(pipeline, run_name):
            return self[pipeline][run_name]
        else:
            return None

    @staticmethod
    def comp_gds(dir_paths):
        return Wrangler(dir_paths, "*/*/comp.gd")
    @staticmethod
    def test_gds(dir_paths):
        return Wrangler(dir_paths, "*/*/output/output.gd")


