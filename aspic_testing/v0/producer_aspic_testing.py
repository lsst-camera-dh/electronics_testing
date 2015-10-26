#!/usr/bin/env python
import os, glob
from lcatr.harness import config
print "executing producer_test_job.py"

IRODS = True
#this is temporary stuff to get going
cfg=config.Config()
basedir = os.environ['ASPIC_BASE_DIR']
uid = cfg.unit_id

logdir = os.path.join(basedir,"Logs")
chipdir = os.path.join(basedir,"CHIP%s"%uid)
if not IRODS:
    input_file = glob.glob(os.path.join(logdir,"log-%s-*.txt"%uid))[0]
    os.system('cp %s .'%input_file)
    os.system('ln -s %s .'%rel_path)
else :
    ss = "filename=`ils %s | grep log-%s`; iget %s/`echo $filename`"%(logdir,uid\
,logdir)
    os.system(ss)
    input_file = glob.glob('log-%s*'%uid)[0]
    os.system('iget -r %s'%chipdir)

print "copying %s to current directory"%input_file


