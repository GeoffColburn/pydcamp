#!/usr/bin/env python
from distutils.core import setup


setup(name = "dcamp",
      package_dir = {'':"src"},
      packages = ["extern", "breseq", "libdcamp", "pipelines"],
      scripts = ["src/dcamp.py"],
     )
