import subprocess

filename = '/sps/lsst/DataBE/ASPIC_production/Logs/log-0109-PostScreening-20151123.txt'
md={}
for tag in ['#setup', '#step', '#chip', '#timestamp']:
    out = subprocess.check_output(['sed', '-n', '/%s/p'%tag,filename])
    out = out.split('\n')[0]
    md[tag.strip('#')] = out.strip('%s '%tag)
print md
