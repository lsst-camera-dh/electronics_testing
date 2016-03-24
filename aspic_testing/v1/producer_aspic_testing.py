#!/usr/bin/env python
import os, sys, glob
import siteUtils
print "executing producer_test_job.py"

IRODS = False

uid = siteUtils.getUnitId()
print "Running ASPIC PRODUCER on ", uid
uid=uid.split('LCA-11721-ASPIC-')[1]
uid=uid.replace('P', '0')

if not IRODS:
    basedir = "/sps/lsst/DataBE/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    try:
        input_file = os.environ['ASPIC_LOGFILE']
    except KeyError:
        try:
            input_file = glob.glob(os.path.join(logdir,"log-%s-*.txt"%uid))[0]
        except:
            raise Exception('Input file %s not found in %s'%("log-%s-*.txt"%uid, logdir))
    os.system('cp %s .'%input_file)
    os.system('ln -s %s .'%chipdir)
else :
    basedir = "/lsst-fr/home/lsstcamera/ASPIC_production"
    logdir = os.path.join(basedir,"Logs")
    chipdir = os.path.join(basedir,"CHIP%s"%uid)
    input_file = os.environ['ASPIC_LOGFILE']
    if input_file =='UNDEFINED':
        pass
    ss = "iget %s"%input_file
    os.system(ss)
    os.system('iget -r %s'%chipdir)

print "copying %s to current directory"%input_file


