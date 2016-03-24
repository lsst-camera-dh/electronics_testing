from openpyxl import load_workbook
from  eTraveler.clientAPI.connection import Connection
import yaml, os

savedir='test'
excel_file='AutoChanger_BOM_simplifiee_20151009.xlsx'

myConn = Connection('jrb', 'Raw', prodServer=False)


class yamlAssembly():
    def __init__(self, record):
        self._yaml = yaml.load(open("assembly_template.yml"))
        self._name = (record[3].value).encode('utf-8')
        self._yaml['HardwareGroup'] = self._name
        self.registerHardware(self._name, record)

    def registerHardware(self, name, rec):
        newId = ''
        try: 
            newId=myConn.defineHardwareType(name=name, 
                                            description=rec[7].value,
                                            sequenceWidth='0')
            print 'New hardware type defined.  Returned id is ', newId
        except Exception,msg:
            print 'Hardware type definition failed with exception ',msg

    def registerRelationship(self, relname, name):
        newId = ''
        try:
            myConn.defineRelationshipType(name = relname, 
                                          description = 'rel type via eT API',
                                          hardwareTypeName = self._name,
                                          numItems = 1,
                                          minorTypeName = name,
                                          slotNames = 'na'
                                          )
            print 'New relationship defined with id ', newId
        except Exception, msg:
            print 'Relationship definition failed with exception ', msg 
    def save(self):
        with open(os.path.join(savedir,'%s.yaml'%self._name), 'w') as outfile:
            outfile.write( os.path.join(savedir,yaml.dump(self._yaml, default_flow_style=False)) )
    
    def addRelationship(self, gg):
        name = (gg[3].value).encode('utf-8')
        if gg[0].value == 3:
            self.registerHardware(name, gg)#the deepest elements need registration
        sequence = self._yaml['Sequence'][0]
        relname = '%s-%s'%(self._name, name)
        new_relationship = {'RelationshipName':relname, 'RelationshipAction':'install'}
        self.registerRelationship(relname, name)
        if sequence['RelationshipTasks'] is None:
            sequence['RelationshipTasks'] = [new_relationship]
        else:
            sequence['RelationshipTasks'].append(new_relationship)


try :
    wb = load_workbook(filename = excel_file, read_only=True)
    ws = wb.active
    gen = ws.iter_rows()
except:
    wb = load_workbook(filename = excel_file)
    ws = wb.active
    gen = ws.rows

print "excel sheet %s loaded"%excel_file
#yaml_struct = []
#gen=ws.iter_rows()
d0 = None
d1 = None
d2 = None
for gg in gen:
    if gg[3].value == None:
        continue
    elif gg[3].value == "Handling Tools":
        break
    #print gg[3].value
    if gg[0].value == 0:
        d0 = yamlAssembly(gg)
    if gg[0].value == 1:
        if d1 is not None:
            d1.save()
        d0.addRelationship(gg)
        d1 = yamlAssembly(gg)
    if gg[0].value == 2:
        if d2 is not None:
            d2.save()
        d1.addRelationship(gg)
        d2 = yamlAssembly(gg)
    if gg[0].value == 3:
        d2.addRelationship(gg)
d0.save()
    #     print gg[3].value 
    #     for gg in gen:
    #         if gg[0].value==2:
    #             print '\t', gg[3].value
    #             for gg in gen:
    #                 if gg[0].value==3 or gg[0].value==None:
    #                     print '\t\t', gg[3].value
    #                 else:
    #                     break
    #         else:
    #             break
