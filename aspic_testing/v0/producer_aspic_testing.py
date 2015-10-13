#!/usr/bin/env python
import os, glob
from lcatr.harness import config
print "executing producer_test_job.py"

#this is temporary stuff to get going
cfg=config.Config()

basedir = os.environ['ASPIC_BASE_DIR']

input_file = glob.glob(os.path.join(basedir,"Logs","log-%s-*.txt"%cfg.unit_id))[0]
print "copying %s to current directory"%input_file
os.system('cp %s .'%input_file)

input_info=os.path.basename(input_file).split('-')
rel_path = os.path.join(basedir,"CHIP%s"%input_info[1])
print "creating symlink to %s"%rel_path
os.system('ln -s %s .'%rel_path)
