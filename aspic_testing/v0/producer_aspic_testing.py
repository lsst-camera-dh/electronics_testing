#!/usr/bin/env python
import os, sys
import siteUtils
print "executing producer_test_job.py"

IRODS = False

uid = siteUtils.getUnitId()

if not IRODS:
    basedir = "/sps/lsst/DataBE/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    input_file = os.environ['ASPIC_LOGFILE']
    if input_file =='UNDEFINED':
        raise KeyError('LCATR_ASPIC_LOGFILE SET TO %s!'%input_file)
    os.system('cp %s .'%input_file)
    os.system('ln -s %s .'%chipdir)
else :
    basedir = "/lsst-fr/home/lsstcamera/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    input_file = os.environ['LCATR_ASPIC_LOGFILE']
    if input_file =='UNDEFINED':
        pass
    ss = "iget %s"%input_file
    os.system(ss)
    os.system('iget -r %s'%chipdir)

print "copying %s to current directory"%input_file


