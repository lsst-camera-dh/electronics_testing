#!/usr/bin/env python
import os, glob
import siteUtils
print "executing producer_test_job.py"

IRODS = True

uid = siteUtils.getUnitId()

if not IRODS:
    basedir = "/sps/lsst/DataBE/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    input_file = glob.glob(os.path.join(logdir,"log-%s-*.txt"%uid))[0]
    os.system('cp %s .'%input_file)
    os.system('ln -s %s .'%chipdir)
else :
    basedir = "/lsst-fr/home/lsstcamera/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    ss = "filename=`ils %s | grep log-%s`; iget %s/`echo $filename`"%(logdir,uid\
,logdir)
    os.system(ss)
    input_file = glob.glob('log-%s*'%uid)[0]
    os.system('iget -r %s'%chipdir)

print "copying %s to current directory"%input_file


