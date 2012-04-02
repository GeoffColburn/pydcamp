import os, sys
import re
import glob
from collections import defaultdict


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
            for path in glob.glob(self.file_wrangle_fmt.format(dir_path, '*')):
                search = "[/](?P<job_id>\w+)[/](?P<run_id>[\w\W]+)[/]" + key
                m = re.search(search, path)
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


