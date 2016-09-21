import glob, os, subprocess, sys
from  eTraveler.clientAPI.connection import Connection
from exceptions import ValueError, IndexError
import numpy as np

def input_parsing(inputs, move_to=None):
    """
    parse input in order to build the list of requested chip directories, and
    the site and location to move to, as an option.
    inputs : list of chip numbers, either a number strig (e.g. 0001), or a wildcard
    string (e.g. 01*) or a file containing chip numbers.
    assume that user only input ASPIC numbers
    """
    chips = inputs
    
    if '*' in chips:
        chipdirs = glob.glob(os.path.join(data_dir,"CHIP"+chips))
    elif os.path.exists(chips):
        chiplist=np.loadtxt(chips, dtype=str)
        chipdirs = [os.path.join(data_dir,"CHIP"+chip) for chip in chiplist]
    else:
        chipdirs = os.path.join(data_dir,"CHIP"+chips)
        if not os.path.exists(chipdirs):
            raise ValueError("%s not valid, %s not found"%(chips,chipdirs))
        else :
            chipdirs = [chipdirs]

    if move_to is not None:
        try:
            site,location = move_to.split('/')
        except:
            raise ValueError('move_to argument must be in format site/location')

    return chipdirs, site, location

def change_location(connection, snid, site, location) :
        #change hardware location
        errorCode = connection.setHardwareLocation(experimentSN=snid, htype='LCA-11721',
                                                   siteName=site, locationName=location)
        print "%s hardware location return code: "%snid, errorCode


def batch_process(myConn, chipdirs, logfiles, site, location):
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
                                    version='v1',
                                    hardwareGroup='LCA-11721',
                                    htype='LCA-11721',
                                    site='CCIN2P3', 
                                   # travelerVersion='1',
                                    jhInstall='cohen')
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

                #finally change the location if the chip has been shipped.
                change_location(myConn, snid, site, location)


if __name__ == "__main__":
    data_dir="/sps/lsst/DataBE/ASPIC_production/"
    archive_dir="/lsst-fr/data/camera/ASPIC_data"

    print 'running script %s ...'%sys.argv[0]
    print 'data_dir is ', data_dir
    print 'archive_dir is ', archive_dir

    try:
        chips = sys.argv[1]
    except IndexError:
        raise IndexError('chip idea input (e.g. 0001 or 01* or a file with chip ids) needs to be provided')

    if len(sys.argv)==2:
        move_to = 'CCIN2P3/Cabinet'
    else:
        move_to = sys.argv[2]

    chipdirs, site, location = input_parsing(chips, move_to=move_to)

    #need to clean the list of usable logs
    logdir =  os.path.join(data_dir,'Logs')
    logfiles = glob.glob(os.path.join(logdir,"log-*.txt"))
    logfiles = filter(lambda x: (not 'try' in x)and(not 'Test' in x)and(('PreScreening' in x)or('PostScreening' in x)or('ClearPending' in x)), logfiles)

    myConn = Connection('cohen', db='Dev', prodServer=False)
    batch_process(myConn, chipdirs, logfiles, site, location)
