#!/usr/bin/env python
import os, glob
from lcatr.harness import config
print "executing producer_test_job.py"

#this is temporary stuff to get going
cfg=config.Config()

basedir = os.environ['ASPIC_BASE_DIR']

input_file = glob.glob(os.path.join(basedir,"log-%s-*.txt"%cfg.unit_id))[0]
print "creating symlink to %s"%input_file
os.system('ln -s %s ./results_file'%input_file)
