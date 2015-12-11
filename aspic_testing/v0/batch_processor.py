import glob, os
from  eTraveler.clientAPI.connection import Connection

data_dir="/sps/lsst/DataBE/ASPIC_production/"
archive_dir="/lsst-fr/data/camera/ASPIC_data"


chipdirs = glob.glob(os.path.join(data_dir,"CHIP*"))
logdir =  os.path.join(data_dir,'Logs')

logfiles = glob.glob(os.path.join(logdir,"log-*.txt"))
logfiles = filter(lambda x: (not 'try' in x)and(not 'Test' in x)and(('PreScreening' in x)or('PostScreening' in x)or('ClearPending' in x)), logfiles)

myConn = Connection('cohen', 'Dev', prodServer=False)

for chipdir in chipdirs[2:3]:
    unit_str = chipdir.split('CHIP')[1]
    chiplogs = filter(lambda x: 'log-%s'%unit_str in x, logfiles)
    
    #register hardware
    try: 
        newId = myConn.registerHardware(htype='LCA-ASPIC', site='CCIN2P3',  
                                        manufacturer='NA', location='Cabinet',
                                        experimentSN=unit_str) 
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
        os.environ['ASPIC_LOGFILE']=log
        try:
            #myConn.runHarnessedById(hardwareId=newId, 
            myConn.runHarnessed(experimentSN=unit_str,
                                hardwareId=unit_str,
                                travelerName='ASPIC_data_ingest',
                                version='v1',
                                hardwareGroup='LCA-ASPIC',
                                htype='LCA-ASPIC',
                                site='CCIN2P3', 
                                jhInstall='wbf-test')
            print "Traveler execution succeeded"
        except Exception,msg:
            print 'Traveler execution failed with exception ', msg

    
