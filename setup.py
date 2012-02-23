#!/usr/bin/env python
from distutils.core import setup


setup(name = "dcamp",
      package_dir = {'':"src"},

      packages = ["extern", "breseq", "libdcamp", "pipelines"],

      scripts = ["src/dcamp.py",
                 "extern/breakdancer/cpp/breakdancer_max",
                 "extern/breakdancer/perl/AlnParser.pm",
                 "extern/breakdancer/perl/Poisson.pm",
                 "extern/breakdancer/perl/bam2cfg.pl"],

      data_files = [("share/dcamp/gatk", ["share/GenomeAnalysisTK-1.4/GenomeAnalysisTK.jar",
                                          "share/GenomeAnalysisTK-1.4/AnalyzeCovariates.jar"]),

                    ("share/dcamp/picard_tools", ["share/picard_tools/AddOrReplaceReadGroups.jar",
                                                  "share/picard_tools/MarkDuplicates.jar", 
                                                  "share/picard_tools/CreateSequenceDictionary.jar",
                                                  "share/picard_tools/ValidateSamFile.jar"]),
                    ("share/dcamp/dcamp", ["share/dcamp/style.css"])]
      )#End setup.
