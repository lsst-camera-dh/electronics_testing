import glob, os, subprocess
from  eTraveler.clientAPI.connection import Connection

data_dir="/sps/lsst/DataBE/ASPIC_production/"
archive_dir="/lsst-fr/data/camera/ASPIC_data"


#chipdirs = glob.glob(os.path.join(data_dir,"CHIP*"))
chipdirs = glob.glob(os.path.join(data_dir,"CHIP0395"))
logdir =  os.path.join(data_dir,'Logs')

logfiles = glob.glob(os.path.join(logdir,"log-*.txt"))
logfiles = filter(lambda x: (not 'try' in x)and(not 'Test' in x)and(('PreScreening' in x)or('PostScreening' in x)or('ClearPending' in x)), logfiles)

myConn = Connection('cohen', db='Dev', prodServer=False)

#for chipdir in chipdirs[2:3]:
for chipdir in chipdirs:
    unit_str = chipdir.split('CHIP')[1]

    snid = unit_str
    manufacturer = "QuikPak"
    #Promex 01xx need to be turned into LCA-11721-ASPIC-P1xx
    if snid[0:2]=='01':
        snid='P1'+snid[2:]
        manufacturer = "Promex"
    snid='LCA-11721-ASPIC-'+snid


    chiplogs = filter(lambda x: 'log-%s'%unit_str in x, logfiles)
    
    #register hardware
    try: 
        newId = myConn.registerHardware(htype='LCA-11721', site='CCIN2P3',  
                                        manufacturer=manufacturer, location='Cabinet',
                                        experimentSN=snid) 
        print 'New hardware registered.  Returned id is ', newId
    except Exception,msg:
        if 'Duplicate experiment serial number' in msg.message:
            pass
        else:
            print 'Hardware registration failed with exception ',msg


    #run the JH on each logfile
    print chipdir, chiplogs
    #for log in ['/sps/lsst/DataBE/ASPIC_production/Logs/log-0366-PostScreening-20160202.txt']:
    for log in chiplogs:
        print 'running harnessed job for ', log
        myConn.env['ASPIC_LOGFILE'] = log
        print 'setting ASPIC_LOGFILE env var to ', myConn.env['ASPIC_LOGFILE']
        try:
            myConn.runHarnessed(experimentSN=snid,
                                hardwareId=unit_str,
                                travelerName='ASPIC_batch_ingest',
#                                travelerName='ASPIC_data_ingest',
                                version='v1',
                                hardwareGroup='LCA-11721',
                                htype='LCA-11721',
                                site='CCIN2P3', 
                                travelerVersion='1',
#                                jhInstall='wbf-test')
                                jhInstall='cohen')
#                                jhInstall='jct-test')
            print "Traveler execution succeeded"
        except Exception,msg:
            print 'Traveler execution failed with exception ', msg

        #finally set the new status of the hardware
        if 'PostScreening' in log:
            #first check presence of RefLow3:
            files = glob.glob(os.path.join(logdir, "log-%s-%s-*.txt"%(unit_str, 'PostReflow3')))
            if files!=[]:
                log=files[0]
            status = subprocess.check_output(['sed', '-n', '/%s/p'%'#status', log])
            status = status.split()[1]
            print log,status
            if status == 'Pending':
                log = [l for l in chiplogs if 'ClearPending' in l][0]
                status = subprocess.check_output(['sed', '-n', '/%s/p'%'#status', log])
                status = status.split()[1]
            label = status
            if status in ['Used', 'Reserved']:
                label = status
                if label == 'Used':
                    label = 'Destroyed (Used)'
                status = 'Rejected'

            print status, label
            errorCode = myConn.adjustHardwareLabel(experimentSN=snid,
                                                   htype='LCA-11721',
                                                   label=label,
                                                   reason='set by eTraveler API',
                                                   activityId=None)

            errorCode = myConn.setHardwareStatus(experimentSN=snid,
                                                 htype='LCA-11721',
                                                 status=status,
                                                 reason='set by eTraveler API',
                                                 activityId=None)

        #change hardware location
        errorCode = myConn.setHardwareLocation(experimentSN=snid, htype='LCA-11721',
                                               siteName='SLAC', locationName='Cabinet')
        print "hardware location return code: ", errorCode
