#!/usr/bin/env python
from distutils.core import setup


setup(name = "dcamp",
      package_dir = {'':"src"},
      packages = ["extern", "breseq", "libdcamp"],
      scripts = ["src/dcamp.py", "src/pipelines/breakdancer.py"],
     )
