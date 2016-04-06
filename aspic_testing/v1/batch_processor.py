import glob, os
from  eTraveler.clientAPI.connection import Connection

data_dir="/sps/lsst/DataBE/ASPIC_production/"
archive_dir="/lsst-fr/data/camera/ASPIC_data"


#chipdirs = glob.glob(os.path.join(data_dir,"CHIP*"))
chipdirs = glob.glob(os.path.join(data_dir,"CHIP010*"))
logdir =  os.path.join(data_dir,'Logs')

logfiles = glob.glob(os.path.join(logdir,"log-*.txt"))
logfiles = filter(lambda x: (not 'try' in x)and(not 'Test' in x)and(('PreScreening' in x)or('PostScreening' in x)or('ClearPending' in x)), logfiles)

myConn = Connection('cohen', 'Dev', prodServer=False)

#for chipdir in chipdirs[2:3]:
for chipdir in chipdirs:
    unit_str = chipdir.split('CHIP')[1]

    snid = unit_str
    #Promex 01xx need to be turned into LCA-11721-ASPIC-P1xx
    if snid[0:2]=='01':
        snid='P1'+snid[2:]
    snid='LCA-11721-ASPIC-'+snid


    chiplogs = filter(lambda x: 'log-%s'%unit_str in x, logfiles)
    
    #register hardware
    try: 
        newId = myConn.registerHardware(htype='LCA-11721', site='CCIN2P3',  
                                        manufacturer='NA', location='Cabinet',
                                        experimentSN=snid) 
        print 'New hardware registered.  Returned id is ', newId
    except Exception,msg:
        if 'Duplicate experiment serial number' in msg.message:
            pass
        else:
            print 'Hardware registration failed with exception ',msg


    #run the JH on each logfile
    print chipdir, chiplogs
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
            status = subprocess.check_output(['sed', '-n', '/%s/p'%'#status', log])
            errorCode = connection.setHardwareStatus(experimentSN=snid, 
                                                     htype='LCA-11721', 
                                                     status.split()[1], 
                                                     reason='set by eTraveler API', 
                                                     activityId=None)
