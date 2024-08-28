''' Created 12 Dec 2011 esalste
    modified 27/01/2012 esmipau to jython and to use DbAccess class
'''

from __future__ import with_statement
import TPAPI
import logging
import string
import sys, traceback
import warnings
from copy import deepcopy
from TPAPI_Util import deprecated

class InterfaceVersion(object):
    '''Class to represent a version of an Interface'''
       
    def __init__(self,intfName=None,intfVersion=None):
        '''Class is instantiated with interface name and interface version:
            Both default to None if not specified, resulting in a new interface
            
            
        Instance Variables:
        
            self.intfVersionID = self.name  + ":" + self.intfVersion
                Description: versionID of the interface
                Type: String
                
            #rename to properties
            self.versioning:
                Description: Properties of the Interface version
                Type: Dictionary
                    Keys:
                        INTERFACENAME
                        STATUS
                        INTERFACETYPE
                        DESCRIPTION
                        DATAFORMATTYPE
                        INTERFACEVERSION
                        LOCKEDBY
                        LOCKDATE
                        PRODUCTNUMBER
                        ENIQ_LEVEL
                        RSTATE
                        INSTALLDESCRIPTION
                
            self.dependencies:
                Description: Rstate of the dependent Techpack
                Type:Dictionary
                    Keys: name of the techpack 
            
            
            self.intfConfig:
                Description: configuration instructions for the parser (tied to the interface)
                Type: Dictionary
                    Keys: Common ones listed for reference but many custom/per parser parameters also will exist
                          Custom entries will have the parserType + "." preceding the parameter name (Key) eg. MDCParser.vendorIDMask
        
                             ProcessedFiles.fileNameFormat
                             ProcessedFiles.processedDir
                             afterParseAction
                             archivePeriod 
                             baseDir
                             dirThreshold
                             doubleCheckAction
                             dublicateCheck
                             failedAction 
                             inDir
                             interfaceName
                             loaderDir
                             maxFilesPerRun
                             minFileAge
                             outDir 
                             parserType 
                             thresholdMethod
                             useZip
                             workers
                             

            self.intfTechpacks: = {}
                Description: Rstate of the dependent Techpack
                Type: Dictionary
                
            self.etlrepCollectionSetID:
                Description: CollectionSetID of the interface. Used to retrieve etlrep set information for the interface
                Type: int
                
            self.etlrepMetaCollectionSetObject:
                Description: Child etlrepMetaCollectionSetObject of the Interface Version
                Type: etlrepMetaCollectionSetObject
        
        '''
        
        if (intfName == None and intfVersion !=None) or (intfName != None and intfVersion == None):
            raise TypeError("Cant set one and not the other")
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.Interface.InterfaceVersion')
        if intfName == None and intfVersion == None:
            self.name = 'UNINITIALISED'
            self.intfVersion = '0'     
        else:
            self.name = intfName
            self.intfVersion = intfVersion
            
            
        self.intfVersionID = self.name  + ":" + self.intfVersion
        self.versioning = {} 
        self.dependencies = {}
        self.intfConfig = {}
        self.intfTechpacks = {}
        self.etlrepCollectionSetID = ''
        self.etlrepMetaCollectionSetObject = None
        

    def getPropertiesFromServer(self,server):
        '''Get the properties of the techpack version object from the server'''
        
        dwhrepcrsr = TPAPI.DbAccess(server,'dwhrep').getCursor()
        etlrep = TPAPI.DbAccess(server,'etlrep').getCursor()
        
        
        self._getVersioning(dwhrepcrsr)
        self._getCollectionSetID(etlrep)
        self._getInterfaceConfig(etlrep)
        self._getDependencies(dwhrepcrsr)
        self._getTechpacks(dwhrepcrsr)
        
        
    def _getVersioning(self,crsr):
        '''Populates the versioning dictionary for the interface version'''
        crsr.execute("SELECT * FROM dwhrep.DataInterface WHERE INTERFACENAME=? AND INTERFACEVERSION=?", (self.name,self.intfVersion,))
        desc = crsr.description
        row = crsr.fetchone()
        if row is not None:
            self.versioning = {}
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] != 'STATUS' and x[0] != 'INTERFACENAME':
                    if value != None and value != 'None':
                        self.versioning[x[0]] = value
                i+=1   

    def _getDependencies(self,crsr):
        '''Populates the dependencies dictionary for the interface version'''
        crsr.execute("SELECT TECHPACKNAME,TECHPACKVERSION FROM dwhrep.InterfaceDependency WHERE INTERFACENAME=? AND INTERFACEVERSION=?", (self.name,self.intfVersion,))
        for res in crsr.fetchall():
            tpName=str(res[0])
            tpVersion=str(res[1])
            self.dependencies[tpName] = tpVersion
    
    def _getTechpacks(self,crsr):
        '''Populate the intfTechpacks dictionary for the interface version. This is the list
        of techpacks that the interface can install'''
        crsr.execute("SELECT TECHPACKNAME,TECHPACKVERSION FROM dwhrep.InterfaceTechpacks WHERE INTERFACENAME =? AND INTERFACEVERSION=?", (self.name,self.intfVersion,))
        res = crsr.fetchall()
        if res:
            for row in res:
                tpName = str(row[0])
                tpVersion = str(row[1])
                self.intfTechpacks[tpName] = tpVersion

    def _getCollectionSetID(self,crsr):
        '''Gets the collection setid of the interface version'''
        crsr.execute("SELECT COLLECTION_SET_ID FROM etlrep.META_COLLECTION_SETS WHERE COLLECTION_SET_NAME = ? AND VERSION_NUMBER =?",(self.name,self.intfVersion,))
        res = crsr.fetchone()
        if res:
            self.etlrepCollectionSetID = str(res[0])            
    

    def _getInterfaceConfig(self,crsr):
        '''Populate the intfConfig dictionary with configuration parameters for the interface version
        Dictionary is dynamically created as parameters can differ in number from interface to interface'''
        crsr.execute("SELECT ACTION_CONTENTS_01 from etlrep.META_TRANSFER_ACTIONS WHERE COLLECTION_SET_ID =? AND ACTION_TYPE = 'Parse'",(self.etlrepCollectionSetID,))
        res = crsr.fetchone()
        if res:
            config_list = res[0].replace('\r', '\n')
            config_list = config_list.rsplit('\n')[2:]
            for item in config_list:
                if item != '':
                    kvp = item.split("=",1)
                    param = kvp[0]
                    action = ''
                    try:
                        action = kvp[1]
                    except:
                        pass
                    self.intfConfig[param]= action

        values = []
        crsr.execute("SELECT NAME, INTERVAL_HOUR, INTERVAL_MIN, SCHEDULING_HOUR, SCHEDULING_MIN from etlrep.META_SCHEDULINGS WHERE COLLECTION_SET_ID =?",(self.etlrepCollectionSetID,))
        resultset = crsr.fetchall()
        for row in resultset:
            if 'TriggerAdapter_' in row[0]:
                for value in row:
                    if '.0' in str(value):
                        item = TPAPI.strFloatToInt(value)
                        if item == '0':
                            item = '00'
                        values.append(item)
                self.intfConfig['AS_Interval']= values[0] + ',' + values[1]
                self.intfConfig['AS_SchBaseTime']= values[2] + ',' + values[3]
             
        if 'outDir' in self.intfConfig:
            elementType = self.intfConfig['outDir'].split('/')
            elementType = elementType[len(elementType)-2]
            self.versioning['ELEMTYPE'] = elementType
    
    def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            sheet = workbook.getSheet('Interfaces')
            dict = TPAPI.XlsDict().InterfaceDict
            colNumber = sheet.getColumns()
            
            label = Label(colNumber, sheet.findCell('Interface').getRow(), self.intfVersionID)
            sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.versioning.keys():
                    value = self.versioning[Parameter]
                    label = Label(colNumber, sheet.findCell(FDColumn).getRow(), str(value))
                    sheet.addCell(label)
                if Parameter == 'dependencies':
                    value = ','.join(['%s:%s' % (key, value) for (key, value) in self.dependencies.items()])
                    label = Label(colNumber, sheet.findCell(FDColumn).getRow(), value)
                    sheet.addCell(label)
                if Parameter == 'intfTechpacks':
                    value = ','.join(['%s:%s' % (key, value) for (key, value) in self.intfTechpacks.items()])
                    label = Label(colNumber, sheet.findCell(FDColumn).getRow(), value)
                    sheet.addCell(label)
                        
            for Parameter, value in self.intfConfig.iteritems():
                paramRow = None
                paramCell = sheet.findCell(Parameter)
                if paramCell == None:
                    paramRow = sheet.getRows()
                    label = Label(0, paramRow, Parameter)
                    sheet.addCell(label)
                else:
                    paramRow = paramCell.getRow()
                
                label = Label(colNumber, paramRow, value)
                sheet.addCell(label)
                

 
    def toXML(self,offset=0):
        '''Write the object to an xml formatted string
        
        Offset value is used for string indentation. Default to 0
        Parent toXML() method is responsible for triggering child object toXML() methods.

        Return Value: xmlString 
        '''
        offset += 4
        os = "\n" + " "*offset
        os2 = os+" "*offset
        os3 = os2+" "*offset
        os4 = os3+" "*offset
        outputXML = os2+'<Interface name="' + self.name + '">'
        outputXML +=os3+ '<IntfVersioning intfVersion="' + self.intfVersion + '">'
        for item in sorted(self.versioning.iterkeys()):
            outputXML += os4+'<'+str(item)+'>'+ str(self.versioning[item]) +'</'+str(item)+'>'
        outputXML += os3+'</IntfVersioning>'
        outputXML += os3+'<Dependencies>'
        for item in sorted(self.dependencies.iterkeys()):
            outputXML += os4+'<'+str(item)+'>'+ self.dependencies[item] +'</'+str(item)+'>'
        outputXML += os3+'</Dependencies>'
        outputXML += os3+'<Techpacks>'
        for item in sorted(self.intfTechpacks.iterkeys()):
            if item in self.dependencies:
                outputXML += os4+'<'+str(item)+'>'+ self.intfTechpacks[item] +'</'+str(item)+'>'
        outputXML += os3+'</Techpacks>'
        outputXML += os3+'<Configuration>'
        for item in sorted(self.intfConfig.iterkeys()):
            outputXML += os4+'<'+str(item)+'>'+ str(self.intfConfig[item]) +'</'+str(item)+'>'
        outputXML += os3+'</Configuration>'
        outputXML += os2+'</Interface>'

        return outputXML
    
  
    def getPropertiesFromXML(self,xmlElement):
        '''Populates the objects content from an xmlElement.
            
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
            
        for element in xmlElement:
            if element.tag == 'IntfVersioning':
                for elem1 in element:
                    self.versioning[elem1.tag] = TPAPI.safeNull(elem1.text)
            elif element.tag == 'Dependencies':
                for elem1 in element:
                    self.dependencies[elem1.tag]=TPAPI.safeNull(elem1.text)
            elif element.tag == 'Techpacks':
                for elem1 in element:
                    self.intfTechpacks[elem1.tag]=TPAPI.safeNull(elem1.text)
            elif element.tag == 'Configuration':
                for elem1 in element:
                    self.intfConfig[elem1.tag]=TPAPI.safeNull(elem1.text)
            else:
                raise "Error, tag type %s not recognised." % element.tag
            
    def getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a XlsDict object or xls file.
        
        If a xls file is passed it is converted to a XlsDict object before processing.

        Exceptions: 
                   Raised if XlsDict and filename are both None (ie nothing to process)
        '''
        self.logger.debug(self.intfVersionID + ".getPropertiesFromXls()")

        if xlsDict==None and filename==None:
            strg = 'getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('getPropertiesFromTPI() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
            for Name, Value in xlsDict.iteritems():
                if Name == 'dependencies':
                    deps = xlsDict['dependencies'] + ','
                    entries = deps.split(',')
                    for item in entries:
                        tp = item.split(':')
                        if tp[0] != '':
                            self.dependencies[tp[0]] = tp[1]
                        
                elif Name == 'intfConfig':
                    for key, value in xlsDict['intfConfig'].iteritems():
                        if value != '':
                            self.intfConfig[key.strip('\n\r')] = value
                        
                elif Name == 'intfTechpacks':
                    deps = xlsDict['intfTechpacks'] + ','
                    entries = deps.split(',')
                    for item in entries:
                        tp = item.split(':')
                        if tp[0] != '':
                            self.intfTechpacks[tp[0]] = tp[1]
                        
                else:
                    self.versioning[Name] = Value
            

    def getPropertiesFromTPI(self,tpiDict=None,filename=None):
        '''Populate the objects contents from a tpiDict object or tpi file.
        
        If a tpi file is passed it is converted to a tpiDict object before processing.

        Exceptions: 
                   Raised if tpiDict and filename are both None (ie nothing to process)
                   Raised if there is a tpi dict key error'''
                   

        dict = {'Datainterface' : self._tpiDataInterface,
                'Interfacedependency' : self._tpiInterfaceDependency,
                'InterfaceTechpacks' : self._tpiInterfaceTechpacks,
                'META_TRANSFER_ACTIONS' : self._tpiMetaTransferActions,
                #'META_COLLECTION_SETS' : self._tpiMetaCollectionSets,
        }
            
        self.logger.debug(self.name + "._getPropertiesFromTPI()")
        if tpiDict==None and filename==None:
            strg = 'getPropertiesFromTPI() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                tpiDict = TPAPI.TpiDict(filename).returnTPIDict()
            for key in tpiDict:
                try:
                    if key in dict:
                        dict.get(key)(tpiDictionary=tpiDict)
                except:
                    strg  = 'getPropertiesFromTPI() tpi dict key error = ' + key
                    raise Exception(strg)
                    self.logger.error(strg)
                    

    def _tpiDataInterface(self, tpiDictionary):      
        self.name = tpiDictionary['Datainterface']['interfacename'][1]
        self.intfVersion = tpiDictionary['Datainterface']['interfaceversion'][1]
        self.intfVersionID = self.name  + ":" + self.intfVersion
        
        for column in tpiDictionary['Datainterface']:
                self.versioning[column] = tpiDictionary['Datainterface'][column][1]

    def _tpiInterfaceDependency(self, tpiDictionary):        
        for row in tpiDictionary['Interfacedependency']['interfacename']:
            for row2 in tpiDictionary['Interfacedependency']['interfaceversion']:
                self.dependencies[tpiDictionary['Interfacedependency']['techpackname'][row]] = tpiDictionary['Interfacedependency']['techpackversion'][row]      

    def _tpiInterfaceTechpacks(self, tpiDictionary):          
        for row in tpiDictionary['InterfaceTechpacks']['interfacename']:
            self.intfTechpacks[tpiDictionary['InterfaceTechpacks']['techpackname'][row]] = tpiDictionary['InterfaceTechpacks']['techpackversion'][row]
            

    def _tpiMetaTransferActions(self, tpiDictionary):          
        '''Here is a new comment'''
        for row in tpiDictionary['META_TRANSFER_ACTIONS']['ACTION_CONTENTS']:
            if tpiDictionary['META_TRANSFER_ACTIONS']['ACTION_TYPE'][row]=="Parse":
                configs =  tpiDictionary['META_TRANSFER_ACTIONS']['ACTION_CONTENTS'][row]
                configs = TPAPI.unescape(configs)
                config_list = configs.rsplit() # split to list on newline
                config_list = config_list[2:]
                for line in config_list:
                    my_list = line.split(';')
                    for line in my_list:
                        if '=' in line:
                            line = line.lstrip(';')
                            line = line.strip('&#xD')
                            param,action = line.split("=",1) # split the parameters and actions on first equals
                            self.intfConfig[param]= action 
        
        if 'outDir' in self.intfConfig:
            elementType = self.intfConfig['outDir'].split('/')
            elementType = elementType[len(elementType)-2]
            self.versioning['ELEMTYPE'] = elementType
                
    
    def _tpiMetaCollectionSets(self, tpiDictionary):
        '''
        Because TPAPI.EtlrepSetCollection makes a check against the techpack name and version number. The versioning needs to be populated first. 
        The order of keys in the tpiDict cannot be guaranteed so populating the versioning information is done first here. 
        '''
        self._tpiVersioning(tpiDictionary=tpiDictionary)        
        for row in tpiDictionary['META_COLLECTION_SETS']['COLLECTION_SET_NAME']:
            self.etlrepCollectionSetID = tpiDictionary['META_COLLECTION_SETS']['etlrepCollectionSetID'][row]
            metaCollectionSetObject = TPAPI.EtlrepSetCollection(self.name,self.intfVersion)
            metaCollectionSetObject.getPropertiesFromTPI(tpiDictionary)
            self.etlrepMetaCollectionSetObject = metaCollectionSetObject
      
    def isDependantOn(self, techPackVersion):
        for dependencyName in self.dependencies.keys():
            dependencyVersion = self.dependencies[dependencyName]
            if dependencyName == techPackVersion.versioning['TECHPACK_NAME'] and TPAPI.compareRStates(dependencyVersion, techPackVersion.versioning['TECHPACK_VERSION']) >= 0:
                return True
        return False

    def _populateRepDbModel(self, IntfRepDbInterface):
        RepDbDict = {}
        
        #Interfacetechpacks
        for tpName, Rstate in self.intfTechpacks.iteritems():
            RepDbDict['INTERFACENAME'] = self.name
            RepDbDict['INTERFACEVERSION'] = self.intfVersion
            RepDbDict['TECHPACKNAME'] = tpName
            RepDbDict['TECHPACKVERSION'] = Rstate
            IntfRepDbInterface.populateInterfacetechpacks(RepDbDict)
        
        RepDbDict = {}
        #Interfacedependency
        for tpName, Rstate in self.dependencies.iteritems():
            RepDbDict['INTERFACENAME'] = self.name
            RepDbDict['INTERFACEVERSION'] = self.intfVersion
            RepDbDict['TECHPACKNAME'] = tpName
            RepDbDict['TECHPACKVERSION'] = Rstate
            IntfRepDbInterface.populateInterfacedependency(RepDbDict)
        
        RepDbDict = {} 
        #Datainterface        
        TempDict = {}
        TempDict['INTERFACENAME'] = self.name
        TempDict['STATUS'] = '1'
        TempDict['INTERFACEVERSION'] = self.intfVersion
        TempDict['PRODUCTNUMBER'] = ''
        TempDict['INSTALLDESCRIPTION'] = ''
        RepDbDict = dict(self.versioning.items() + TempDict.items())
        IntfRepDbInterface.populateDatainterface(RepDbDict)
    
    
    def deleteIntf(self, server):
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.setRockFactoryAutoCommit(False)
        try:
            IntfRepDbInterface.deleteFromDB(self.intfVersionID)
            IntfRepDbInterface.commit()
        except:
            traceback.print_exc(file=sys.stdout) 
            IntfRepDbInterface.rollback()
        IntfRepDbInterface.setRockFactoryAutoCommit(True)
    
    def CreateIntf(self,server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
                
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.setRockFactoryAutoCommit(False)
        
        try:
            self._populateRepDbModel(IntfRepDbInterface)
            IntfRepDbInterface.insertToDB()
            IntfRepDbInterface.commit()
        except:
            traceback.print_exc(file=sys.stdout) 
            IntfRepDbInterface.rollback()

        IntfRepDbInterface.setRockFactoryAutoCommit(True)
        engine.setAndWaitActiveExecutionProfile("Normal")
        
    def createTPInstallFile(self, server, buildNumber, outputPath, encrypt):
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.createTPInstallFile(self.intfVersionID, buildNumber, outputPath, encrypt)
        
    def generateSets(self, server, outputPath):
        setsDict = {}
        setsDict['intfConfig'] = deepcopy(self.intfConfig)
        setsDict['INTERFACENAME'] = self.name
        setsDict['INTERFACEVERSION'] = self.intfVersion
        setsDict['INTERFACETYPE'] = self.versioning['INTERFACETYPE']
        setsDict['DATAFORMATTYPE'] = self.versioning['DATAFORMATTYPE']
        if 'ELEMTYPE' in self.versioning:
            setsDict['ELEMTYPE'] = self.versioning['ELEMTYPE']
        else:
            setsDict['ELEMTYPE'] = self.intfTechpacks.keys()[0]
        
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.setRockFactoryAutoCommit(False)
        try:
            IntfRepDbInterface.generateIntfSets(setsDict, outputPath)
            IntfRepDbInterface.commit()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            IntfRepDbInterface.rollback()
            raise Exception(exception)
        
        IntfRepDbInterface.setRockFactoryAutoCommit(True)
        
    def activateIntf(self, server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
        
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.setRockFactoryAutoCommit(True)
        IntfRepDbInterface.activateIntf(self.intfVersionID, engine)
        
        engine.setAndWaitActiveExecutionProfile("Normal")
    
    def deActivateIntf(self, server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
        
        IntfRepDbInterface = TPAPI.IntfRepDbInterface(server)
        IntfRepDbInterface.setRockFactoryAutoCommit(True)
        IntfRepDbInterface.deactivateIntf(self.intfVersionID)
        
        engine.setAndWaitActiveExecutionProfile("Normal")


    def difference(self,intfVerObject,deltaObj=None):
        '''Calculates the difference between two external interface version objects
            
            Method takes intfVerObject,deltaObj and deltaTPV as inputs.
            intfVerObject: The interface version to be compared against
            DeltaObj: The single object that gets passed through the entire diff recording the changes.
            DeltaTPV: A TechPackVersion Object that gets passed through the entire diff recording only new content.
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            Note: Interface Version does not have any child objects
            
            Returns:
                    diffFlag (Boolean indicating where a change was found or not)
                    deltaObj
                    deltaTPV 
        '''        
        
        if deltaObj==None:
            deltaObj = TPAPI.Delta(self.intfVersionID,intfVerObject.intfVersionID)
        
        #########################################################################################################################################
        # Versioning diff
        Delta = TPAPI.DictDiffer(self.versioning,intfVerObject.versioning)
        excludedProperties = ['LOCKDATE', 'INTERFACEVERSION', 'LOCKEDBY', 'ENIQ_LEVEL', 'STATUS', 'INSTALLDESCRIPTION', 'ELEMTYPE', 'PRODUCTNUMBER']
        deltaObj.location.append('Versioning')
        for item in Delta.changed():
            if item not in excludedProperties:
                deltaObj.addChange('<Changed>', item, self.versioning[item], intfVerObject.versioning[item])
        
        for item in Delta.added():
            if item not in excludedProperties:
                deltaObj.addChange('<Added>', item, '', intfVerObject.versioning[item])
                
        for item in Delta.removed():
            if item not in excludedProperties:
                deltaObj.addChange('<Removed>', item, self.versioning[item], '')

        deltaObj.location.pop()
        
        #########################################################################################################################################
        # Dependencies diff
        Delta = TPAPI.DictDiffer(self.dependencies,intfVerObject.dependencies)
        deltaObj.location.append('Dependencies')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.dependencies[item], intfVerObject.dependencies[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', intfVerObject.dependencies[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.dependencies[item], '')

        deltaObj.location.pop()
        
        #########################################################################################################################################
        # IntfConfig diff        
        Delta = TPAPI.DictDiffer(self.intfConfig,intfVerObject.intfConfig)
        deltaObj.location.append('IntfConfig')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.intfConfig[item], intfVerObject.intfConfig[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', intfVerObject.intfConfig[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.intfConfig[item], '')

        deltaObj.location.pop()
        
        #########################################################################################################################################
        # IntfTechPacks diff        
        Delta = TPAPI.DictDiffer(self.intfTechpacks,intfVerObject.intfTechpacks)
        deltaObj.location.append('IntfConfig')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.intfTechpacks[item], intfVerObject.intfTechpacks[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', intfVerObject.intfTechpacks[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.intfTechpacks[item], '')

        deltaObj.location.pop()
        
        return deltaObj   
    
    def toString(self):
        '''Prints basic interface properties and configuration to a string'''
        self.printVersionSummary()
        self.printVersionInfo()
        
    def printVersionInfo(self):
        print "ENIQ Interface Information"
        print "--------------------------"
        print "Interface : " + self.name + " " + self.intfVersion 
        print "\nVersioning"
        print "----------" 
        TPAPI.printDict(self.versioning)
        print "\nTechpack Dependencies"
        print "----------"
        TPAPI.printDict(self.dependencies)
        print "\nInterface Configuration Parameters"
        print "----------------------------------"
        TPAPI.printDict(self.intfConfig)
        
    def printVersionSummary(self):
        print "ENIQ Interface Summary Information"
        print "Interface : " + self.name + " " + self.intfVersion
        TPAPI.printDict(self.versioning) 
        print "\nConfig\n------"
        TPAPI.printDict(self.intfConfig) 
        print "Collection Set Id: " + str(self.etlrepCollectionSetID)

class Interface(object): 
    '''Class to represent an Interface at its highest abstract level. 
    
    Contains a collection of interface versions for the Interface'''
    
    name = ''
    intfType = ''
    intfRState = ''
    intfVersion = ''
    listOfVersionIDs = []
    listOfInterfaceVersionObjects = []
    intfActiveVersion = None
    intfActivations = []
    properties = {}
    
    def __init__(self,intfName):
        
        
        self.name = intfName
        

    def toString(self):
        print "initialised with " + self.name
        for i in self.listOfInterfaceVersionObjects:
            print i.toString()
            
    def getAllProperties(self,server):
        ''' Get Versioning Information for all versions of the interface on the server'''
        with TPAPI.DbAccess(server,'dwhrep') as crsr:
            crsr.execute("SELECT INTERFACEVERSION FROM dwhrep.DataInterface WHERE INTERFACENAME=?", (self.name,))
            for row in crsr.fetchall():
                intfVersion = str(row[0])
                self.__populateProperties(server, intfVersion)
            self.getActiveDataInterface(server)
        return
    
    def getPropertiesFromServer(self,server, intfVersion):
        '''Get Versioning Information for a specific version of an Interface'''
        if intfVersion not in self.listOfVersionIDs:
            self.__populateProperties(server, intfVersion)
        return self.listOfInterfaceVersionObjects[intfVersion]
              
    def __populateProperties(self, server, intfVersion):
        '''Creates instances for the interfaces'''
        self.listOfVersionIDs.append(intfVersion)
        intf = TPAPI.InterfaceVersion(self.name,intfVersion)
        intf.getPropertiesFromServer(server)
        self.listOfInterfaceVersionObjects.append(intf)
        
        
    def getActivatedInterfaces(self,server):
        '''gets the list of activated version of the interface - from etlrep'''
        with TPAPI.DbAccess(server,'etlrep') as crsr:
            crsr.execute("SELECT COLLECTION_SET_NAME FROM META_COLLECTION_SETS WHERE COLLECTION_SET_NAME LIKE ? AND ENABLED_FLAG='Y'",  ('%' + self.name + '%',))
            for row in crsr.fetchall():
                setName = str(row[0])
                self.intfActivations.append(setName)
        return
    
    def getActiveDataInterface(self,server):
        '''gets the activated version of the interface - from dwhrep.DataInterfaces'''
        if self.intfActiveVersion is None:
            with TPAPI.DbAccess(server,'dwhrep') as crsr:
                crsr.execute("SELECT INTERFACEVERSION FROM dwhrep.DataInterface WHERE INTERFACENAME =? AND STATUS=1", (self.name,))
                self.intfActiveVersion = str(crsr.fetchone()[0])
        return self.intfActiveVersion



    
    

        
