'''Copyright Ericsson.. Created 06 Dec 2011 
esalste,esiranv,epausmi'''

from __future__ import with_statement
from xml.etree import ElementTree
import TPAPI
import string
import re
import logging
import traceback
import sys
import warnings
from TPAPI_Util import deprecated



class TechPackVersion(object):
    '''Class to represent a version of a TechPack in TPAPI.

     '''
    
    def __init__(self,versionID=None):
        '''If the versionID is not specified an empty object will be created with versionID set to default value of "UNINITIALISED:((0))". 
        When an UNINITIALISED techpack gets its properties from a tpi the versionID is updated from inside the file.
        When an INITIALISED techpack reads it properties from an xml file, its versionID is not updated from inside the file
        
        
        Instance Variables:
           self.versionID:
                Description: versionID of the techpack version. eg DC_E_BSS:((100)).
                Type:String
                
           self.tpName:
                Description: Name of the techpack. eg DC_E_BSS
                Type:String
                
           self.versionNumber:
               Description: versionNumber of the techpack version with brackets. eg ((100))
               Type:String
            
           self.versionNo:
               Description: versionNo of the techpack versions without brackets: eg 100
               Type:String (int)
               
           self.versioning: 
               Description: Stores top level versioning (properties) information of the techpack version.
               Type: Dictionary
               Keys: VERSIONID, DESCRIPTION, STATUS, TECHPACK_NAME, TECHPACK_VERSION, TECHPACK_TYPE,
                       PRODUCT_NUMBER, LOCKEDBY, LOCKDATE, BASEDEFINITION, BASEVERSION, INSTALLDESCRIPTION,
                       UNIVERSENAME, UNIVERSEEXTENSION, ENIQ_LEVEL, LICENSENAME
                       
           self.measurementTableNames: 
               Description: Measurement table (names) associated with the techpack version.
               Type: List
               
           self.measurementTableObjects: 
               Description: Measurement table objects associated with the techpack version.
               Type: Dictionary
               Keys: Measurement table names
               
           self.referenceTableNames:
               Description: Reference table (names) associated with the techpack version.
               Type: List
           
           self.referenceTableObjects:
               Description: Reference table object associated with the techpack version.
               Type: Dictionary
               Keys: Reference table names
           
           self.supportedVendorReleases:
               Description: Vendor Releases that the techpack version supports.
               Type: List
        
           self.busyHourNames:
               Description: Busy Hour Object (names) associated with the techpack version.. eg UPLINK.
               Type: List
               
           self.busyHourObjects:
               Description: Busy Hour Objects associated with the techpack version.
               Type: Dictionary
               Keys: Busy Hour Object Names
               
           self.groupTypes:
               Description: ENIQ Events only. Dictionary containing groupType information.
               Type: Dictionary of Dictionaries
               Keys: GROUPTYPE
                   Sub Keys: DATANAME, DATATYPE, DATASIZE, DATASCALE, NULLABLE
               
           self.externalStatementObjects:
               Description: External Statement Objects associated with the techpack version.
               Type: Dictionary
               Keys: External Statement Name
               
           self.interfaceNames:
               Description: InterfaceNames and versions associated with the techpack version. Dictionary value is the interface version.
               Type: Dictionary
               Keys: name of the interface
               
           self.interfaceObjects:
               Description: Interface Objects associated with the techpack version.
               Type: Dictionary
               Keys: name of the interface
               
           self.collectionSetID:
               Description: CollectionSetID of the Techpack version. Used to retrieve etlrep information from the database.
               Type: int
               
           self.etlrepMetaCollectionSetObject:
               Description: etlrepMetaCollectionSetObject associated with the techpack version.
               Type: etlrepMetaCollectionSet Object
                  
           self.universeObjects:
               Description: Universe (Model) Object associated with the techpack version. Not to be confused with objects of a universe
               Type: Dictionary
               Keys:
        
           '''
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.TechPackVersion') 
        self.versionID = None
        self.tpname = None
        self.versionNumber = None
        self.versionNo = None
        self._intialiseVersion(versionID) #Version ID is parsed to get further information from string for versionNumber,versionNo,versionID
        self.logger.debug('Created TechPackVersion instance with versionid =' + str(self.versionID))
        self.versioning = {}
        self.measurementTableNames = []
        self.measurementTableObjects = {}
        self.referenceTableNames = []
        self.referenceTableObjects = {}
        self.supportedVendorReleases = []
        self.dependencyTechPacks = {}
        self.busyHourNames = []
        self.busyHourObjects = {}
        self.groupTypes = {} # events
        self.externalStatementObjects = {}
        self.interfaceNames = {} 
        self.interfaceObjects = {}
        self.collectionSetID = None # could possibly be hidden
        self.etlrepMetaCollectionSetObject = None  # could possibly be hidden
        self.universeObjects = {} # universe python object # not objects of a universe
        self.verificationObjectObjects = []
        self.verificationConditionObjects = []

    def _intialiseVersion(self, versionID):
        '''Initialise the TechPackVersion versionID.
        If versionID string is none, the TechPackVersion versionID is populated with a default value of UNINITIALISED:((0))
        TechPackVersion tpName and versionNumber,versionNo properties are set by parsing the versionID string.
        '''
        
        if versionID == None:
            versionID = 'UNINITIALISED:((0))'
        self.tpName = versionID.rsplit(':')[0]
        self.versionNumber = versionID.rsplit(':')[1]
        try:
            self.versionNo = re.search('\(\((.*)\)\)',versionID).group(1)   # build number ie without the brackets eg '6'
        except:
            self.logger.error('Could not get versionNo from versionID ' + versionID)
        
        self.versionID = versionID
        self.logger.debug(versionID + ".intialiseVersion()")
        
        
    def getPropertiesFromServer(self,server):
        '''Populates the model of the TechPackVersion from metadata on the server
        
        This is a container method for triggering a sequence of methods that populate
        individual parts of the model.
        '''
        self.logger.debug(self.versionID + ".getPropertiesFromServer()")
        
        crsr = TPAPI.DbAccess(server,'dwhrep').getCursor()
        
        self._getVersioning(crsr)    
        self._getFactTables(crsr)
        self._getReferenceTables(crsr)
        self._getInterfaceNames(crsr)
        self._getInterfaceObjects(server)
        self._getFactTableObjects(crsr)
        self._getReferenceTableObjects(crsr)
        self._getBusyHours(crsr)
        self._getBusyHourObjects(crsr)
        self._getExternalStatements(crsr)
        self._getSupportedVendorReleases(crsr)
        self._getUniverses(crsr)
#         self._getCollectionSetID(server)
#         if self.collectionSetID: # Some TPs may not have set information created initially so a check is carried out before attempting to retrieve set information
#             self._getEtlrepSetCollectionObject(server)
#         if self.versioning['TECHPACK_TYPE'] == 'ENIQ_EVENT':
#             self.logger.debug(self.versionID + " = ENIQ EVENTS TECHPACK")
#             self._getGroupTypes(server)
        self._getVerificationInfo(crsr)

    def getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a XlsDict object or xls file.
        
        If a xls file is passed it is converted to a XlsDict object before processing.

        Exceptions: 
                   Raised if XlsDict and filename are both None (ie nothing to process)
        '''
        self.logger.debug(self.versionID + ".getPropertiesFromXls()")

        if xlsDict==None and filename==None:
            strg = 'getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('getPropertiesFromTPI() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
            
            versionID = xlsDict['Versioning']['TECHPACK_NAME'] + ':((' + xlsDict['Versioning']['BUILD_NUMBER'] + '))'
            self._intialiseVersion(versionID)
            
            for entry in xlsDict['Versioning']:
                if entry != 'BUILD_NUMBER' and entry != 'VENDORRELEASE' and entry != 'Dependency':
                    self.versioning[entry] = TPAPI.checkNull(xlsDict['Versioning'][entry])
                
            #Supported Vendor Releases
            self.supportedVendorReleases = xlsDict['Versioning']['VENDORRELEASE']
            
            deps = xlsDict['Versioning']['Dependency'] + ','
            entries = deps.split(',')
            for item in entries:
                tp = item.split(':')
                if tp[0] != '':
                    self.dependencyTechPacks[tp[0]] = tp[1]
            
            
            elemBHsupport = []
            #Tables and BH
            for Name, Values in xlsDict['Tables'].iteritems():
                ft = TPAPI.Table(Name,self.versionID)
                ft.tableType = Values['TABLETYPE']
                ft._getPropertiesFromXls(xlsDict)
                if Values['TABLETYPE'] == 'Measurement':
                    self.measurementTableNames.append(Name)
                    self.measurementTableObjects[ft.name] = ft
                elif Values['TABLETYPE'] == 'Reference':
                    self.referenceTableNames.append(Name)
                    self.referenceTableObjects[ft.name] = ft
                      
                #ELEM BusyHour handling
                if 'RANKINGTABLE' in Values.keys() and 'ELEMENTBHSUPPORT' in Values.keys():
                    if Values['RANKINGTABLE'] == '1' and Values['ELEMENTBHSUPPORT'] == '1':
                        bho = TPAPI.BusyHour(self.versionID,'ELEM')
                        bho.rankingTable = Name
                        bho._getPropertiesFromXls(xlsDict)
                        bho._createDefaultBusyHourTypes()
                        self.busyHourNames.append('ELEM')
                        self.busyHourObjects['ELEM'] = bho
                    
                    if Values['RANKINGTABLE'] != '1' and Values['ELEMENTBHSUPPORT'] == '1':
                        elemBHsupport.append(Name)
                    
                #Object BusyHour support
                if 'OBJECTBH' in Values.keys(): 
                    BHobjs = Values['OBJECTBH']+','
                    BHobjs = BHobjs.split(',')
                    for bh in BHobjs:
                        if bh != None and bh != '':
                            if bh not in self.busyHourObjects:
                                bho = TPAPI.BusyHour(self.versionID,bh)
                                bho._getPropertiesFromXls(xlsDict)
                                bho._createDefaultBusyHourTypes()
                                self.busyHourNames.append(bh)
                                self.busyHourObjects[bh] = bho 
                            
                            if Values['RANKINGTABLE'] != '1':
                                self.busyHourObjects[bh].supportedTables.append(Name)              
                            else:
                                self.busyHourObjects[bh].rankingTable = Name
           
            if len(elemBHsupport)>0:
                self.busyHourObjects['ELEM'].supportedTables = elemBHsupport
            
            if 'Universe' in xlsDict.keys():   
                for Name,  Values in xlsDict['Universe'].iteritems():
                    unv=TPAPI.Universe(self.versionID,Name)
                    unv._getPropertiesFromXls(xlsDict)
                    self.universeObjects[unv.universeName]=unv
            
            if 'ExternalStatements' in xlsDict.keys():           
                for Name, Values in xlsDict['ExternalStatements'].iteritems():
                    ext = TPAPI.ExternalStatement(self.versionID, Name)
                    ext._getPropertiesFromXls(xlsDict)
                    self.externalStatementObjects[Name] = ext
            
            if 'ReportObjects' in xlsDict.keys():         
                for Name, RoDict in xlsDict['ReportObjects'].iteritems():
                    ro = TPAPI.VerificationObject(self.versionID,'','','')
                    ro._getPropertiesFromXls(RoDict)
                    self.verificationObjectObjects.append(ro)
            
            if 'ReportConditions' in xlsDict.keys():   
                for Name, RCDict in xlsDict['ReportConditions'].iteritems():
                    rc = TPAPI.VerificationCondition(self.versionID,'','','')
                    rc._getPropertiesFromXls(RCDict)
                    self.verificationConditionObjects.append(rc)
            
            if 'Interfaces' in xlsDict.keys():
                for Name, IntfDict in xlsDict['Interfaces'].iteritems():
                        items = Name.split(':')
                        Interface = TPAPI.InterfaceVersion(items[0], items[1])
                        Interface.getPropertiesFromXls(IntfDict)
                        self.interfaceObjects[items[0]] = Interface
                        self.interfaceNames[items[0]] = items[1]
                    
            
                

    def getPropertiesFromTPI(self,tpiDict=None,filename=None): 
        '''Populate the objects contents from a tpiDict object or tpi file.
        
        If a tpi file is passed it is converted to a tpiDict object before processing.

        Exceptions: 
                   Raised if tpiDict and filename are both None (ie nothing to process)
                   Raised if there is tpi dict key error'''
                   
        self.logger.debug(self.versionID + ".getPropertiesFromTPI()")

        dict = {'Versioning' : self._tpiVersioning,
        'Measurementtype' : self._tpiMeasurementType,
        'Referencetable' : self._tpiReferenceTable,
        'Busyhour' : self._tpiBusyHour,
        'Supportedvendorrelease' : self._tpiSupportedVendorRelease,
        'Externalstatement' : self._tpiExternalStatement,
        'InterfaceTechpacks' : self._tpiInterfaceTechpacks,
        #'META_COLLECTION_SETS' : self._tpiMetaCollectionSets,
        'Universename' : self._tpiUniverses,
        'Verificationobject' : self._tpiVerificationObjects,
        'Verificationcondition' : self._tpiVerificationConditions,
        }
        
        if tpiDict==None and filename==None:
            strg = 'getPropertiesFromTPI() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('getPropertiesFromTPI() extracting from ' + filename)
                tpiDict = TPAPI.TpiDict(filename).returnTPIDict()
            self._tpiVersioning(tpiDictionary=tpiDict)
            for key in tpiDict: 
                if key in dict:
                    dict.get(key)(tpiDictionary=tpiDict)
 
                    
    def _tpiUniverses(self,tpiDictionary):
        self.logger.debug(self.versionID + "._tpiUniverses()")
        '''Extracts Universe Info from the tpiDictionary'''

        for row in tpiDictionary['Universename']['UNIVERSENAME']:
            name = tpiDictionary['Universename']['UNIVERSENAME'][row]
            unv = TPAPI.Universe(self.versionID,name)
            unv._getPropertiesFromTPI(tpidict=tpiDictionary)
            self.universeObjects[name] = unv

    def _tpiVerificationObjects(self,tpiDictionary):
        self.logger.debug(self.versionID + "._tpiVerificationObjects()")
        for row in tpiDictionary['Verificationobject']['OBJECTNAME']:
            measLevel  = tpiDictionary['Verificationobject']['MEASLEVEL'][row]
            objectClass = tpiDictionary['Verificationobject']['OBJECTCLASS'][row]
            objectName = tpiDictionary['Verificationobject']['OBJECTNAME'][row]
            vo = TPAPI.VerificationObject(self.versionID,measLevel,objectClass,objectName)
            vo._getPropertiesFromTPI(tpiDictionary)
            self.verificationObjectObjects.append(vo)

 
    def _tpiVerificationConditions(self,tpiDictionary):
        self.logger.debug(self.versionID + "._tpiVerificationConditions()")
        for row in tpiDictionary['Verificationcondition']['VERCONDITION']:
            conClass = tpiDictionary['Verificationcondition']['CONDITIONCLASS'][row]
            verCon = tpiDictionary['Verificationcondition']['VERCONDITION'][row]
            verLevel = tpiDictionary['Verificationcondition']['VERLEVEL'][row]
            vc = TPAPI.VerificationCondition(self.versionID,conClass,verCon,verLevel)
            vc._getPropertiesFromTPI(tpiDictionary) # implement
            self.verificationConditionObjects.append(vc)

    def _tpiMeasurementType(self, tpiDictionary):
            '''Extracts MeasurementType information from the tpiDictionary'''
            for row in tpiDictionary['Measurementtype']['TYPENAME']:
                self.measurementTableNames.append(tpiDictionary['Measurementtype']['TYPENAME'][row])
                ft = TPAPI.Table(tpiDictionary['Measurementtype']['TYPENAME'][row],self.versionID)
                ft.tableType = 'Measurement'
                ft._getPropertiesFromTPI(tpiDictionary)
                self.measurementTableObjects[ft.name] = ft
     
    def _tpiReferenceTable(self, tpiDictionary):    
            '''Extracts referenceType information from the tpiDictionary'''             
            for row in tpiDictionary['Referencetable']['TYPENAME']:
                if tpiDictionary['Referencetable']['BASEDEF'][row] != '1':
                    self.referenceTableNames.append(tpiDictionary['Referencetable']['TYPENAME'][row])
                    ft = TPAPI.Table(tpiDictionary['Referencetable']['TYPENAME'][row],self.versionID)
                    ft.tableType = 'Reference'
                    ft._getPropertiesFromTPI(tpiDictionary)
                    self.referenceTableObjects[ft.name] = ft
                    
    def _tpiBusyHour(self, tpiDictionary):
            '''Extracts BusyHour information from the tpiDictionary'''            
            for row in tpiDictionary['Busyhour']['BHOBJECT']:
                if tpiDictionary['Busyhour']['BHOBJECT'][row] not in self.busyHourNames:
                    self.busyHourNames.append(tpiDictionary['Busyhour']['BHOBJECT'][row])

            for bh in self.busyHourNames:
                bho = TPAPI.BusyHour(self.versionID,bh)
                bho._getPropertiesFromTPI(tpiDictionary)
                self.busyHourObjects[bh] = bho  
            
            
    def _tpiSupportedVendorRelease(self, tpiDictionary):
            '''Extracts SupportedVendorRelease information from the tpiDictionary'''           
            for row in tpiDictionary['Supportedvendorrelease']['VENDORRELEASE']:
                self.supportedVendorReleases.append(tpiDictionary['Supportedvendorrelease']['VENDORRELEASE'][row])
                 
            
    def _tpiExternalStatement(self, tpiDictionary):   
        '''Extracts ExternalStatement information from the tpiDictionary''' 

        tempCollection = {}
        for row in tpiDictionary['Externalstatement']['STATEMENTNAME']:
            if tpiDictionary['Externalstatement']['BASEDEF'][row] != '1':
                ext = TPAPI.ExternalStatement(self.versionID, tpiDictionary['Externalstatement']['STATEMENTNAME'][row])
                ext._getPropertiesFromTPI(tpiDict=tpiDictionary)
                tempCollection[tpiDictionary['Externalstatement']['STATEMENTNAME'][row]] = ext
            
        ExecOrder = 1
        for ES in sorted(tempCollection.keys()):
            self.externalStatementObjects[str(ExecOrder)] = tempCollection[ES]
            ExecOrder = ExecOrder + 1
             

    def _tpiInterfaceTechpacks(self, tpiDictionary):                
            '''Extracts InterfaceTechpacks information from the tpiDictionary'''
            for row in tpiDictionary['InterfaceTechpacks']['interfacename']:
                self.interfaceNames[tpiDictionary['InterfaceTechpacks']['interfacename'][row]] = tpiDictionary['InterfaceTechpacks']['interfaceversion'][row]
            for intf in self.interfaceNames:
                intfObject = TPAPI.InterfaceVersion(intf,self.interfaceNames[intf])
                intfObject.getPropertiesFromTPI(tpiDict=tpiDictionary)
                self.interfaceObjects[intf] = intfObject            
                
             
             
    def _tpiMetaCollectionSets(self, tpiDictionary):
        '''Extract EtlrepMestatCollectionObject information from the tpiDictionary'''        
        for row in tpiDictionary['META_COLLECTION_SETS']['COLLECTION_SET_NAME']:
            self.collectionSetID = tpiDictionary['META_COLLECTION_SETS']['COLLECTION_SET_ID'][row]
            metaCollectionSetObject = TPAPI.EtlrepSetCollection(self.tpName,self.versionNumber)
            metaCollectionSetObject._getPropertiesFromTPI(tpiDictionary)
            self.etlrepMetaCollectionSetObject = metaCollectionSetObject


    def _tpiVersioning(self, tpiDictionary):
        '''Extracts Versioning information from the tpiDictionary'''
        self._intialiseVersion(tpiDictionary['Versioning']['VERSIONID'][1])
        properties = [ 'DESCRIPTION', 'STATUS', 'TECHPACK_NAME', 'TECHPACK_VERSION', 'TECHPACK_TYPE', 'PRODUCT_NUMBER', 'LOCKEDBY', 'LOCKDATE', 'ENIQ_LEVEL', 'LICENSENAME']
        for column in tpiDictionary['Versioning']:
            if column in properties:
                self.versioning[column] = TPAPI.checkNull(tpiDictionary['Versioning'][column][1])
        
        if 'Techpackdependency' in tpiDictionary:
            for column in tpiDictionary['Techpackdependency']['VERSIONID']:
                self.dependencyTechPacks[tpiDictionary['Techpackdependency']['TECHPACKNAME'][column]] = tpiDictionary['Techpackdependency']['VERSION'][column]

    def addInterface(self,interfaceVersionObject):
        '''Add Interface to self.interfaceObjects dictionary of the TechPackVersion
        '''
        self.interfaceObjects[interfaceVersionObject.name] = interfaceVersionObject
    
    
    def removeInterface(self,interfaceVersionName):
        '''Remove Interface from the dictionary of interface objects of the TechPackVersion
         '''
        del self.interfaceObjects[interfaceVersionName]
  
    def _getVersioning(self,crsr):
        '''Populate the versioning dictionary of the TechPackVersion from the server
        
        SQL Statement:
                 SELECT * from dwhrep.Versioning where VERSIONID =?
        Exceptions:
                 Raised if the Techpack is not present on the server
        ''' 
        
        self.logger.debug(self.versionID + "._getVersioning()")

        crsr.execute("SELECT * from dwhrep.Versioning where VERSIONID =?", (self.versionID,))
        desc = crsr.description
        row = crsr.fetchone()
        if row is not None:
            self.versioning = {}
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] != 'STATUS':
                    if value != None and value != 'None':
                        self.versioning[x[0]] = value
                i+=1
        else:
            strg = self.versionID + ": Techpack not installed on server"
            self.logger.warning(strg)
            raise Exception(strg)
        
        crsr.execute("SELECT TECHPACKNAME, VERSION from dwhrep.TechPackDependency where VERSIONID =?", (self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            self.dependencyTechPacks[row[0]] = row[1]
            
        # Force compulsory values
        if 'TECHPACK_TYPE' not in self.versioning:
            self.versioning['TECHPACK_TYPE'] = 'Not set'
        if 'TECHPACK_VERSION' not in self.versioning:
            self.versioning['TECHPACK_VERSION'] = self.versionID

    def _getFactTables(self,crsr):
        '''Populate measurementTableNames list with the table names from the server
    
        SQL Statement:
                "SELECT TYPENAME from dwhrep.MeasurementType where VERSIONID =?
        '''
        self.logger.debug(self.versionID + ".getFactTables()")
        
        crsr.execute("SELECT TYPENAME from dwhrep.MeasurementType where VERSIONID =?", (self.versionID,))
        self.measurementTableNames = TPAPI.rowToList(crsr.fetchall())
            
    def _getFactTableObjects(self,crsr):
        '''Get measurement table objects associated with the TechPackVersion from the server.
        
        Creates measurementTableVersion objects using names from the measurementTable list.
        Calls the TPAPI_Table.getPropertiesFromServer() method on the measurementTableVersion
        and then adds the measurementTableVersion object to the measurementTableObjects dictionary
        '''
        self.logger.debug(self.versionID + ".getFactTableObjects()")
        for measurementtable in self.measurementTableNames:
            ft = TPAPI.Table(measurementtable,self.versionID)
            if self.versioning['TECHPACK_TYPE'] == 'ENIQ_EVENT':
                ft._getEventsPropertiesFromServer(crsr)
            else:
                ft._getPropertiesFromServer(crsr)
            self.measurementTableObjects[ft.name] = ft # add table object to the measurementtable dictionary
    
    def _getReferenceTables(self,crsr):
        '''Populate referenceTableNames list with the table names from the server
        
        SQL Statement:
                "SELECT TYPENAME from dwhrep.dwhrep.ReferenceTable where VERSIONID =?
        '''
        self.logger.debug(self.versionID + ".getReferenceTables()")

        crsr.execute("SELECT TYPENAME from dwhrep.ReferenceTable where VERSIONID =? and BASEDEF =?", (self.versionID,'0',))
        self.referenceTableNames = TPAPI.rowToList(crsr.fetchall())
            
    def _getReferenceTableObjects(self,crsr):
        '''Get reference table objects associated with the TechPack Version from the server
        
        Creates factTableVersion objects using the names from the referenceTable list.
        Calls the TPAPI_Table.getPropertiesFromServer() method on the referenceTableVersion
        and then adds the referenceTableVersion object to the referenceTableObjects dictionary
        '''
        self.logger.debug(self.versionID + ".getReferenceTableObjects()")
        for refTable in self.referenceTableNames:
            rt = TPAPI.Table(refTable,self.versionID)
            rt._getPropertiesFromServer(crsr)
            self.referenceTableObjects[rt.name] = rt
            
            
    def _getUniverses(self,crsr):
        '''Gets the universes objects associated with the Techpack Version from the server'''
        self.logger.debug(self.versionID + "._getUniverses()")
        
        crsr.execute("SELECT UNIVERSENAME FROM dwhrep.UniverseName WHERE VERSIONID =?", (self.versionID,))
        rows = crsr.fetchall()
        unvname = ''
        for row in rows:
            unvname = row[0]
            unv = TPAPI.Universe(self.versionID,unvname)
            unv._getPropertiesFromServer(crsr)
            self.universeObjects[unvname]= unv

    #TODO Rename to getInterfaceInformation
    def _getInterfaceNames(self,crsr):
        '''Gets the interfaces dependent on the techpack
        
        Gets all interface information from the server for the techpack, and does a comparison using TPAPI.compareRStates to discover
        if the particular interface is dependent on the techpack version. If it is dependent a self.interfaces dictionary is
        populated with interface name and the InterfaceVersion object. This information is used to instantiate interface objects.
        
        SQL Statement:
                SELECT TECHPACKVERSION, INTERFACENAME,INTERFACEVERSION FROM dwhrep.InterfaceTechpacks WHERE TECHPACKNAME =?  
        '''
        self.logger.debug(self.versionID + ".getInterfaceNames()")

        crsr.execute("SELECT TECHPACKVERSION, INTERFACENAME,INTERFACEVERSION FROM dwhrep.InterfaceTechpacks WHERE TECHPACKNAME =?", (self.tpName,) )
        resultset = crsr.fetchall()
        for row in resultset:
            tpVersion=str(row[0])
            #TODO is a try necessary?
            try : 
                if self.versioning['TECHPACK_VERSION'] == tpVersion or TPAPI.compareRStates(self.versioning['TECHPACK_VERSION'], tpVersion):
                    self.interfaceNames[str(row[1])] = str(row[2])
            except:
                #Interface not dependent
                pass

            
    def _getInterfaceObjects(self,server):

        '''Gets dependant interface objects associated with the TechPack Version from the server
        
        Using the information in the interfaces dictionary InterfaceVersion objects are
        created and the TPAPI_Intf.getPropertiesFromServer() method is called for each.
        InterfaceVersion Objects are then appended to the interfaceObject dictionary
        '''
        self.logger.debug(self.versionID + ".getInterfaceObjects()")
        for intf in self.interfaceNames:
            intfObject = TPAPI.InterfaceVersion(intf,self.interfaceNames[intf])
            intfObject.getPropertiesFromServer(server)
            self.interfaceObjects[intf] = intfObject
                

    def _getBusyHours(self,crsr):
        '''Get the list of all busy hour object names associated with the TP from the server

        The Busy Hour names are appended to busyHourNames list. This list of name is used to 
        create Busy Hour objects in the TechPackVersion model
        
        SQL Statement:
                    SELECT DISTINCT BHOBJECT from dwhrep.busyhour where VERSIONID =?
        
        '''
        self.logger.debug(self.versionID + ".getBusyHours()")

        crsr.execute("SELECT DISTINCT BHOBJECT from dwhrep.busyhour where VERSIONID =?", (self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            self.busyHourNames.append(str(row[0]))
    
    def _getBusyHourObjects(self,crsr):
        '''Create busy hour (object) objects
        
        Busy hour objects are initiated using busy hour object names in the busyHourNames list
        their getPropertiesFromServer method is called and the object is then appended
        to the busyHourObjects list
        '''
        
        self.logger.debug(self.versionID + ".getBusyHourObjects()")
        for bh in self.busyHourNames:
            bho = TPAPI.BusyHour(self.versionID,bh)
            bho._getPropertiesFromServer(crsr)
            self.busyHourObjects[bh] = bho

    def _getExternalStatements(self,crsr):
        '''Create External Statement objects associated with the TechPackVersion
        
        Fetches the names of statements from the server, initialises the objects,
        calls the TPAPI_ExternalStatement.getPropertiesFromServer() and appends the objects to the
        externalStatementObjects dictionary
        
        SQL Statement:
            SELECT STATEMENTNAME FROM dwhrep.ExternalStatement WHERE VERSIONID =?"   
        '''

        self.logger.debug(self.versionID + "._getExternalStatements()")

        NoOfBaseES = 0
        crsr.execute("SELECT EXECUTIONORDER FROM dwhrep.ExternalStatement WHERE VERSIONID =? and BASEDEF =?", (self.versionID,'1',))
        resultset = crsr.fetchall()
        for row in resultset:
            if int(row[0]) > NoOfBaseES:
                NoOfBaseES = int(row[0])
            
            
        crsr.execute("SELECT STATEMENTNAME FROM dwhrep.ExternalStatement WHERE VERSIONID =? and BASEDEF =?", (self.versionID,'0',))
        resultset = crsr.fetchall()
        for row in resultset:
            name = str(row[0])
            ext = TPAPI.ExternalStatement(self.versionID, name)
            ext._getPropertiesFromServer(crsr, NoOfBaseES)
            self.externalStatementObjects[name] = ext

    def _getSupportedVendorReleases(self,crsr):
        ''' Gets the vendor releases associated with a TechPackVersion from the server
        
        Vendor Releases are appended to the supportedVendorReleases list
        
        SQL Statement:
                    SELECT VENDORRELEASE FROM dwhrep.SupportedVendorRelease WHERE VERSIONID =?"                    
        '''
        self.logger.debug(self.versionID + ".getSupportedVendorReleases()")

        crsr.execute("SELECT VENDORRELEASE FROM dwhrep.SupportedVendorRelease WHERE VERSIONID =?", (self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            self.supportedVendorReleases.append(str(row[0]))
                
                
    def _getVerificationInfo(self,crsr):
        '''Gets the verification report objects associated with the Techpack version from the server'''
        self.logger.debug(self.versionID + "._getVerification()")
        self._getVerificationObjects(crsr)
        self._getVerificationConditions(crsr)
#
    def _getVerificationObjects(self,crsr):
        crsr.execute("SELECT measLevel,objectClass,objectName FROM dwhrep.VerificationObject WHERE VERSIONID =?", (self.versionID,))
        rows = crsr.fetchall()
        for row in rows:
            vo = TPAPI.VerificationObject(self.versionID,row[0],row[1],row[2])
            vo._getPropertiesFromServer(crsr)
            self.verificationObjectObjects.append(vo)
           
    def _getVerificationConditions(self,crsr):
        crsr.execute("SELECT conditionClass,verCondition,verLevel FROM dwhrep.VerificationCondition WHERE VERSIONID =?", (self.versionID,))
        rows = crsr.fetchall()
        for row in rows:
            vc = TPAPI.VerificationCondition(self.versionID,row[0],row[1],row[2])
            vc._getPropertiesFromServer(crsr)
            self.verificationConditionObjects.append(vc)
    
    #####################################################
    ### ENIQ EVENTS SPECIFIC
    
    def _getGroupTypes(self,server):
        
        #TODO Group types could be remeasurementored to an object
        #TODO rename method to getGroupTypesFromServer()
        '''Get the group types associated with an ENIQ Events TPV
        
        Returned information is added to the groupTypes Dictionary
        
        SQL Statement:
                    SELECT GROUPTYPE,DATANAME,DATATYPE,DATASIZE,DATASCALE,NULLABLE FROM dwhrep.GroupTypes WHERE VERSIONID =?"
        '''

        self.logger.debug(self.versionID + ".getGroupTypes()")
        with TPAPI.DbAccess(server,'dwhrep') as crsr:
            crsr.execute("SELECT GROUPTYPE,DATANAME,DATATYPE,DATASIZE,DATASCALE,NULLABLE FROM dwhrep.GroupTypes WHERE VERSIONID =?", (self.versionID,))
            resultset = crsr.fetchall()
            for row in resultset:
                if str(row[0]) not in self.groupTypes:
                    self.groupTypes[str(row[0])] = {}
                self.groupTypes[str(row[0])][str(row[1])] = {'DATATYPE':str(row[2]),'DATASIZE':str(row[3]),'DATASCALE':str(row[4]),'NULLABLE':str(row[5])}
    
    
    ###############################################
    # ETLREP

    def _getCollectionSetID(self,server):
        #TODO Rename to getCollectionSetIDFromServer
        '''Get the CollectionSetID for the techpack from the server and set the collectionSetID string of the 
        TechPackVersion object with the returned value. 
        
        This will only be present if the techpack has had sets generated for it. The collectionSetID string 
        is used to fetch set information from the etlrep db.
        
        SQL Statement:
                    SELECT COLLECTION_SET_ID from etlrep.META_COLLECTION_SETS where COLLECTION_SET_NAME =? and VERSION_NUMBER =?"
        '''
        with TPAPI.DbAccess(server,'etlrep') as crsr:
            crsr.execute("SELECT COLLECTION_SET_ID from etlrep.META_COLLECTION_SETS where COLLECTION_SET_NAME =? and VERSION_NUMBER =?", (self.tpName,self.versionNumber,))
            row = crsr.fetchone()
            if row:
                self.collectionSetID = str(row[0])
            else:
                pass

    
    def _getEtlrepSetCollectionObject(self,server):
        '''Create the EtlrepSetCollection object associated with the TechPackVersion
        '''
        metaCollectionSetObject = TPAPI.EtlrepSetCollection(self.tpName,self.versionNumber)
        metaCollectionSetObject._getProperties(server)
        self.etlrepMetaCollectionSetObject = metaCollectionSetObject

    def difference(self,tpvObject):
        ''' Calculates the difference between two TechPackVersion Objects
            
            Method takes the TechPackVersion to be compared against as input
            Prior to the diff a deltaObject is created for recording the differences
            A DeltaTPV (TechPackVersion Object) is created for capturing objects that have new or changed content (depreciated)
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            Returns:
                    deltaObj
            
        '''
        self.logger.debug(self.versionID + ".difference()")
        deltaObj = TPAPI.Delta(self.versionID,tpvObject.versionID)
        
        #########################################################################################################################################
        # Versioning diff
        Delta = TPAPI.DictDiffer(self.versioning,tpvObject.versioning)
        deltaObj.location.append('Versioning')
        excludedProperties = ['LOCKDATE', 'VERSIONID', 'LOCKEDBY', 'ENIQ_LEVEL', 'STATUS', 'BASEDEFINITION']
        for item in Delta.changed():
            if item not in excludedProperties:
                deltaObj.addChange('<Changed>', item, self.versioning[item], tpvObject.versioning[item])
        
        for item in Delta.added():
            if item not in excludedProperties:
                deltaObj.addChange('<Added>', item, '', tpvObject.versioning[item])
                
        for item in Delta.removed():
            if item not in excludedProperties:
                deltaObj.addChange('<Removed>', item, self.versioning[item], '')

        deltaObj.location.pop()
        
        #########################################################################################################################################
        # Dependency TP diff
        Delta = TPAPI.DictDiffer(self.dependencyTechPacks,tpvObject.dependencyTechPacks)
        deltaObj.location.append('DependencyTechPacks')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.dependencyTechPacks[item], tpvObject.dependencyTechPacks[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', tpvObject.dependencyTechPacks[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.dependencyTechPacks[item], '')

        deltaObj.location.pop()
        
        #########################################################################################################################################
        #Vendor Release Diff
        deltaObj.location.append('SupportedVendorReleases')
        Delta = list(set(tpvObject.supportedVendorReleases) - set(self.supportedVendorReleases))
        for item in Delta:
            deltaObj.addChange('<Added>', 'Properties', '', item)
        
        Delta = list(set(self.supportedVendorReleases) - set(tpvObject.supportedVendorReleases))
        for item in Delta:
            deltaObj.addChange('<Removed>', 'Properties', item, '')
        
        deltaObj.location.pop()
                
        ##############################################################################################################################################
        #Measurement Table Diff
        Delta = TPAPI.DictDiffer(self.measurementTableObjects,tpvObject.measurementTableObjects)
        deltaObj.location.append('Table')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.measurementTableObjects[item].tableType, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.measurementTableObjects[item].tableType, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('Table='+item)
            deltaObj = self.measurementTableObjects[item].difference(tpvObject.measurementTableObjects[item],deltaObj)
            deltaObj.location.pop()
            
        ##############################################################################################################################################
        #Reference Table Diff
        Delta = TPAPI.DictDiffer(self.referenceTableObjects,tpvObject.referenceTableObjects)
        deltaObj.location.append('Table')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.referenceTableObjects[item].tableType, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.referenceTableObjects[item].tableType, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('Table='+item)
            deltaObj = self.referenceTableObjects[item].difference(tpvObject.referenceTableObjects[item],deltaObj)
            deltaObj.location.pop()
        
        ##########################################################################################################################################
        #Busy Hour Diff
        Delta = TPAPI.DictDiffer(self.busyHourObjects,tpvObject.busyHourObjects)
        deltaObj.location.append('BusyHour')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.busyHourObjects[item].rankingTable, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.busyHourObjects[item].rankingTable, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('BusyHour='+item)
            deltaObj = self.busyHourObjects[item].difference(tpvObject.busyHourObjects[item],deltaObj)
            deltaObj.location.pop()
        
        ##########################################################################################################################################
        #External Statements Diff
        Delta = TPAPI.DictDiffer(self.externalStatementObjects,tpvObject.externalStatementObjects)
        deltaObj.location.append('ExternalStatement')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.externalStatementObjects[item].name, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.externalStatementObjects[item].name, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('ExternalStatement='+item)
            deltaObj = self.externalStatementObjects[item].difference(tpvObject.externalStatementObjects[item],deltaObj)
            deltaObj.location.pop()
        
        #########################################################################################################################################
        #Universe Diff
        Delta = TPAPI.DictDiffer(self.universeObjects,tpvObject.universeObjects)
        deltaObj.location.append('Universe')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.universeObjects[item].universeName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeObjects[item].universeName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('Universe='+item)
            deltaObj = self.universeObjects[item].difference(tpvObject.universeObjects[item],deltaObj)
            deltaObj.location.pop()
            
        #########################################################################################################################################
        #Interface Diff
        Delta = TPAPI.DictDiffer(self.interfaceObjects,tpvObject.interfaceObjects)
        deltaObj.location.append('Interface')
        for item in Delta.added():
            deltaObj.addChange('<Added>', tpvObject.interfaceObjects[item].intfVersionID, '', item)
       
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.interfaceObjects[item].intfVersionID, item, '')
         
        deltaObj.location.pop()
         
        for item in Delta.common():
            deltaObj.location.append('Interface='+item)
            deltaObj = self.interfaceObjects[item].difference(tpvObject.interfaceObjects[item],deltaObj)
            deltaObj.location.pop()
        
        
        return deltaObj 
    
    
    def toXLS(self, templateLocation, outputPath):
        ''' Converts the object to an excel document
            
        Parent toXLS() method is responsible for triggering child object toXLS() methods
        '''
        
        import os
        from java.io import File
        from jxl import Workbook
        from jxl.write import WritableWorkbook 
        from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
        from jxl.write import WritableCell
        from jxl.write import Label 
        
        fileName = self.tpName+'_'+str(self.versionNo)+'_'+self.versioning['TECHPACK_VERSION']+'.xls'
        
        template = Workbook.getWorkbook(File(templateLocation+'\\FD_Template.xls'))
        workbook = Workbook.createWorkbook(File(outputPath+'\\'+fileName), template)
        
        sheet = workbook.getSheet('Coversheet')
        Versdict = TPAPI.XlsDict().VersioningDict
        for FDColumn, Parameter in Versdict.iteritems():
            headercell = sheet.findCell(FDColumn)
            label = ''
            if Parameter == 'VENDORRELEASE':
                label = Label(headercell.getColumn()+1, headercell.getRow(), ",".join(self.supportedVendorReleases))
            elif Parameter == 'BUILD_NUMBER':
                label = Label(headercell.getColumn()+1, headercell.getRow(), str(self.versionNo))
            elif Parameter == 'Dependency':
                dependencies = []
                for key, value in self.dependencyTechPacks.iteritems():
                    dependencies.append(key + ':' + value)
                label = Label(headercell.getColumn()+1, headercell.getRow(), ",".join(dependencies))
            else:
                label = Label(headercell.getColumn()+1, headercell.getRow(), self.versioning[Parameter])
            
            sheet.addCell(label)
        
        TransformationCollection = {} #This is required to ensure the sequence of transformations for multiple parsers   
        for MeasTable in self.measurementTableObjects.itervalues():
            TransformationCollection = MeasTable._toXLS(workbook, TransformationCollection)
        
        for RefTable in self.referenceTableObjects.itervalues():   
            TransformationCollection = RefTable._toXLS(workbook, TransformationCollection)
        
        for parser, transcollection in TransformationCollection.iteritems():
            for orderNum in sorted(transcollection.keys()):
                transcollection[orderNum]._toXLS(workbook)

        for BH in self.busyHourObjects.itervalues():   
            BH._toXLS(workbook)
         
        for ES in self.externalStatementObjects.itervalues():   
            ES._toXLS(workbook, outputPath+'\\'+fileName)
             
        for Uni in self.universeObjects.itervalues():   
            Uni._toXLS(workbook)
         
        for Intf in self.interfaceObjects.itervalues():   
            Intf._toXLS(workbook)
            
        for verCon in self.verificationConditionObjects:
            verCon._toXLS(workbook)
        
        for verobj in self.verificationObjectObjects:
            verobj._toXLS(workbook)
            
        workbook.write(); 
        workbook.close();
        template.close();
    

    def toXML(self,indent=1):
        '''Converts the object to an xmlString representation
        
        Indent value is used for string indentation. Default to 1
        Parent toXML() method is responsible for triggering child object toXML() methods.

        Return Value: xmlString 
        '''
        self.logger.debug(self.versionID + ".toXML()")
        
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        os3 = os2 + offset
        os4 = os3 + offset
        
        outputXML = ''
        outputXML += '<Techpack name="' + self.versionID +'">'
        
        #Versioning Information
        outputXML += os+'<Versioning>'
        for item in sorted(self.versioning.iterkeys()):
            outputXML += os2+'<'+str(item)+'>'+TPAPI.escape(self.versioning[item])+'</'+str(item)+'>'
        
        outputXML += os2+'<SupportedVendorReleases>'
        for item in self.supportedVendorReleases:
            outputXML += os3+'<VendorRelease>' + item + '</VendorRelease>'
        outputXML += os2+'</SupportedVendorReleases>'
        
        outputXML += os2+'<Dependencies>'
        for item in sorted(self.dependencyTechPacks.iterkeys()):
            outputXML += os3+'<'+str(item)+'>'+ self.dependencyTechPacks[item] +'</'+str(item)+'>'
        outputXML += os2+'</Dependencies>'
        
        outputXML += os+'</Versioning>'
        
        
        #Tables
        outputXML += os+'<Tables>'
        for table in sorted(self.measurementTableObjects.iterkeys()):
            outputXML += self.measurementTableObjects[table]._toXML(indent+1)
        for table in sorted(self.referenceTableObjects.iterkeys()):
            outputXML += self.referenceTableObjects[table]._toXML(indent+1)
        outputXML += os+'</Tables>'
        
        
        #BusyHours
        outputXML += os+'<BusyHours>'
        for bh in sorted(self.busyHourObjects.iterkeys()):
            outputXML += self.busyHourObjects[bh]._toXML(indent+1)
        outputXML += os+'</BusyHours>'
        
        
        #External Statements
        outputXML += os+'<ExternalStatement>'
        tempDict = {}
        for ES in self.externalStatementObjects:
            exeorder = self.externalStatementObjects[ES].properties['EXECUTIONORDER']
            tempDict[exeorder] = self.externalStatementObjects[ES]._toXML(indent+1)
        
        for ES in sorted(tempDict.iterkeys()): 
            outputXML += tempDict[ES]
        
        outputXML += os+'</ExternalStatement>'   
        
        #Events Group Types
        if 'TECHPACK_TYPE' in self.versioning:
            if self.versioning['TECHPACK_TYPE']=='ENIQ_EVENT':
                for groupType in self.groupTypes:
                    outputXML += os2+'<GroupType name="' + TPAPI.escape(groupType) + '">'
                    for dataName in self.groupTypes[groupType]:
                        outputXML += os3+'<DataName name="' + TPAPI.escape(dataName) + '">' 
                        for prop in self.groupTypes[groupType][dataName]:
                            outputXML += os4+'<Property  key="' + str(prop) + '" val="' + TPAPI.escape(self.groupTypes[groupType][dataName][prop]) + '"/>'   
                        outputXML += os3+'</DataName> '
                    outputXML += os2+'</GroupType>'
        
        
        #Business Objects information
        outputXML += os+'<BO>'
        outputXML += os2+'<Universes>'
        for unv in sorted(self.universeObjects.iterkeys()):
            outputXML += os3+'<Universe name="' + unv +'">'
            outputXML += self.universeObjects[unv]._toXML(indent+3)
            outputXML += os3+'</Universe>'
        outputXML += os2+'</Universes>'
        
        outputXML += os2+'<Verification>'
        outputXML += os3+'<VerificationObjects>'
        for vo in self.verificationObjectObjects:
            outputXML += vo._toXML(indent+2)             
        outputXML += os3+'</VerificationObjects>'
        
        outputXML += os3+'<VerificationConditions>'
        for vc in self.verificationConditionObjects:
            outputXML += vc._toXML(indent+2)
        outputXML += os3+'</VerificationConditions>'
        
        outputXML += os2+'</Verification>'
        outputXML += os+'</BO>'
        
        #ETLREP        
        if self.collectionSetID and self.etlrepMetaCollectionSetObject != None:
            outputXML += os+'<MetaCollectionSets>'            
            outputXML += os2+'<MetaCollectionSet CollectionSetName="' + self.tpName + '" CollectionSetID="' +str(self.collectionSetID) +'">'
            outputXML += self.etlrepMetaCollectionSetObject._toXML(indent+2)
            outputXML += os2+'</MetaCollectionSet>'
            outputXML += os+'</MetaCollectionSets>'
            
        #Interfaces
        outputXML += os+'<Interfaces>'
        for intf in self.interfaceObjects:
            outputXML += self.interfaceObjects[intf].toXML()
        outputXML += os+'</Interfaces>'
        
        outputXML +='\n</Techpack>'
        
        
        return outputXML 
    
        
    def getPropertiesFromXML(self,xmlElement=None,filename=None):
        '''Populates the objects content from an xmlElement or an XML file
        
        getPropertiesFromXML() method is responsible for triggering its child objects getPropertiesFromXML() method
        
        '''
        self.logger.debug(self.versionID + ".getPropertiesFromXML()")
        if filename is not None:
            xmlElement = TPAPI.fileToXMLObject(open(filename,'r'))
            
        self._intialiseVersion(xmlElement.attrib['name'])
        for elem1 in xmlElement:
            
            #Populate Versioning
            if elem1.tag=='Versioning':
                for elem2 in elem1:
                    if elem2.tag=='SupportedVendorReleases':
                        for elem3 in elem2:
                            if elem3.tag=='VendorRelease':
                                self.supportedVendorReleases.append(TPAPI.safeNull(elem3.text))
                    elif elem2.tag=='Dependencies':
                        for elem3 in elem2:
                            self.dependencyTechPacks[elem3.tag] = TPAPI.safeNull(elem3.text)
                    else:
                        self.versioning[elem2.tag] = TPAPI.safeNull(elem2.text)
                        
            #Populate Tables
            if elem1.tag=='Tables':
                for elem2 in elem1:
                    if elem2.tag=='Table':
                        t = TPAPI.Table(elem2.attrib['name'],self.versionID)
                        t.tableType = elem2.attrib['tableType']
                        t._getPropertiesFromXML(elem2)

                        if elem2.attrib['tableType'] == 'Measurement':
                                self.measurementTableObjects[elem2.attrib['name']] = t
                        if elem2.attrib['tableType'] == 'Reference':
                                self.referenceTableObjects[elem2.attrib['name']] = t
                                            
            #Parsers (ENIQ 2.X, not used)                
            if elem1.tag=='Parsers':
                for elem2 in elem2:
                    if elem2.tag=='Parser':
                        if elem2.attrib['type'] not in self.parserNames:
                            self.parserNames.append(elem2.attrib['type'])
                        tpParser = TPAPI.Parser(self.versionID,self.tpName,elem2.attrib['type'])
                        tpParser.getPropertiesFromXML(elem2)
                        self.parserObjects[elem2.attrib['type']] = tpParser
                        
            #BusyHours
            if elem1.tag == 'BusyHours':
                for elem2 in elem1:
                    bhName =  elem2.attrib['name']
                    bh = TPAPI.BusyHour(self.versionID,bhName)
                    bh._getPropertiesFromXML(elem2)
                    self.busyHourObjects[bhName] = bh
                    
            #Interfaces    
            if elem1.tag == 'Interfaces':
                    for elem2 in elem1:
                        if elem2.tag == 'Interface':   
                            name = elem2.attrib['name']
                            for elem3 in elem2:
                                if elem3.tag == 'IntfVersioning':                                             
                                    intf = TPAPI.InterfaceVersion(name,elem3.attrib['intfVersion'])
                                    intf.getPropertiesFromXML(elem2)
                                    self.interfaceObjects[elem2.attrib['name']]= intf
            
            #External Statements
            if elem1.tag == 'ExternalStatement':
                for elem2 in elem1:
                    if elem2.tag == 'ExternalStatement':
                        name = elem2.attrib['name']
                        es = TPAPI.ExternalStatement(self.versionID, name)
                        es._getPropertiesFromXML(elem2)
                        self.externalStatementObjects[name] = es
            
            #BO details                             
            if elem1.tag == 'BO':
                for elem2 in elem1:
                    if elem2.tag == 'Universes':
                        for elem3 in elem2:
                            if elem3.tag == 'Universe':
                                uo = TPAPI.Universe(self.versionID,elem3.attrib['name'])
                                uo._getPropertiesFromXML(elem3)
                                self.universeObjects[elem3.attrib['name']] = uo
                    if elem2.tag == 'Verification':
                        for elem3 in elem2:
                            if elem3.tag == 'VerificationConditions':
                                for elem4 in elem3:
                                    vc = TPAPI.VerificationCondition(self.versionID,elem4.attrib['class'],elem4.attrib['condition'],elem4.attrib['level'])
                                    vc._getPropertiesFromXML(elem4)
                                    self.verificationConditionObjects.append(vc)
                            if elem3.tag == 'VerificationObjects':
                                for elem4 in elem3:
                                    vo = TPAPI.VerificationObject(self.versionID,elem4.attrib['level'],elem4.attrib['class'],elem4.attrib['name'])
                                    vo._getPropertiesFromXML(elem4)
                                    self.verificationObjectObjects.append(vo)

                                        
    def _populateRepDbModel(self, TPRepDbInterface):
        
        for tpName, Rstate in self.dependencyTechPacks.iteritems():
            RepDbDict = {}
            RepDbDict['VERSIONID'] = self.versionID
            RepDbDict['TECHPACKNAME'] = tpName
            RepDbDict['VERSION'] = Rstate
            TPRepDbInterface.populateTechPackDependency(RepDbDict)
        
        self.versioning['TECHPACK_NAME'] = self.tpName
        TPRepDbInterface.populateVersioning(self.versioning, self.versionID)       
        
        TPRepDbInterface.populateSupportedVendorReleases(self.supportedVendorReleases, self.versionID)
        
        for busyhour in self.busyHourObjects:
            self.busyHourObjects[busyhour]._populateRepDbModel(TPRepDbInterface)
        
        for table in self.measurementTableObjects:
            self.measurementTableObjects[table]._populateRepDbModel(TPRepDbInterface)
            
        for table in self.referenceTableObjects:
            self.referenceTableObjects[table]._populateRepDbModel(TPRepDbInterface)
        
        for universe in self.universeObjects:
            self.universeObjects[universe]._populateRepDbModel(TPRepDbInterface)
        
        for verificObject in self.verificationObjectObjects:
            verificObject._populateRepDbModel(TPRepDbInterface)
        
        for verificCondition in self.verificationConditionObjects:
            verificCondition._populateRepDbModel(TPRepDbInterface)
        
        for ExtStatement in self.externalStatementObjects:
            self.externalStatementObjects[ExtStatement]._populateRepDbModel(TPRepDbInterface)
            
            
    def deleteTP(self, server):
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(False)
        try:
            TPRepDbInterface.deleteFromDB(self.versionID)
            TPRepDbInterface.commit()
        except:
            traceback.print_exc(file=sys.stdout) 
            TPRepDbInterface.rollback()
        TPRepDbInterface.setRockFactoryAutoCommit(True)
        
    
    def CreateTP(self,server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
      
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(False)
        
        self.versioning['BASEDEFINITION'] = TPAPI.getBaseTPName(server)
        self.versioning['STATUS'] = 1
        try:
            self._populateRepDbModel(TPRepDbInterface)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            TPRepDbInterface.rollback()
            raise Exception(exception)
        
        
        
        try:
            TPRepDbInterface.insertToDB()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            TPRepDbInterface.rollback()
            raise Exception(exception)
        
        
        
        
        
        try:
            TPRepDbInterface.commit()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            TPRepDbInterface.rollback()
            raise Exception(exception)
        
        
        

        TPRepDbInterface.setRockFactoryAutoCommit(True)
        engine.setAndWaitActiveExecutionProfile('Normal')
        
    def createDocumentation(self, server, outputPath):
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.generateDocumentation(self.versionID, outputPath)
    
    def createTPInstallFile(self, server, buildNumber, outputPath, encrypt):
        try:
            TPRepDbInterface = TPAPI.TPRepDbInterface(server)
            TPRepDbInterface.createTPInstallFile(self.versionID, buildNumber, outputPath, encrypt)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise Exception(exception)
        
    
    def generateSets(self, server, outputPath):
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(False)
        try:
            TPRepDbInterface.generateSets(self.versionID, outputPath)
            TPRepDbInterface.commit()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            TPRepDbInterface.rollback()
            raise Exception(exception)
        TPRepDbInterface.setRockFactoryAutoCommit(True)
    
    def deleteSets(self, server):
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(False)
        try:
            TPRepDbInterface.deleteSets(self.tpName, '((' + self.versionNo + '))')
            TPRepDbInterface.commit()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            TPRepDbInterface.rollback()
            raise Exception(exception)
        
        TPRepDbInterface.setRockFactoryAutoCommit(True)
    
    def activateTP(self, server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
        
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(True)
        TPRepDbInterface.activateTP(self.versionID, engine)
        
        engine.setAndWaitActiveExecutionProfile("Normal")
    
    def deActivateTP(self, server):
        from tpapi.eniqInterface import EngineInterface
        engine = EngineInterface(server, 1200, 'TransferEngine')
        engine.setAndWaitActiveExecutionProfile("NoLoads")
        
        TPRepDbInterface = TPAPI.TPRepDbInterface(server)
        TPRepDbInterface.setRockFactoryAutoCommit(True)
        TPRepDbInterface.deactivateTP(self.versionID)
        
        engine.setAndWaitActiveExecutionProfile("Normal")
                 

class TechPack(object): 
    '''Class to represent a techpack. ie a container for multiple techpack versions
        
        Techpack = DC_E_BSS,
        Techpack Version = DC_E_BSS:((100))
    '''
    
    versionID = ''
    tpName =''
    ACTIVETP ='NOT_ACTIVE' 
    listOfVersionIDs = ''
    listTechPackVersionObjects =[]

    def __init__(self,tpName):
        '''Class'''
        
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.TechPack')
        self.logger.debug(self.tpName+ ".init()")

        self.tpName = tpName
        self.listOfVersionIDs =[]

        
    def toString(self):
        self.logger.debug(self.tpName+ ".toString()")
        outputString = ''
        outputString += self.tpName + "\n"
        outputString += "Active Version: " + self.ACTIVETP + "\n\n"
        for tpv in self.listTechPackVersionObjects:
            outputString += tpv.toString()
        return outputString
    
    def fileToXML(self,xmlfile):
        xmlString = xmlfile.read()
        xmlObject = ElementTree.fromstring(xmlString)
        return xmlObject
    
    def toXML(self,offset=0):
        '''Write the object to an xml formatted string
        
        Offset value is used for string indentation. Default to 0
        Parent toXML() method is responsible for triggering child object toXML() methods.

        Return Value: xmlString 
        '''
        
        self.logger.debug(self.tpName+ ".toXML()")
        offsetStr = "\n" + " "*offset
        outputXML = offsetStr
        outputXML += '<Techpack name="' + self.tpName +'" activeTechPack="' + self.ACTIVETP +'">' + offsetStr
        for tpv in self.listTechPackVersionObjects:
            outputXML += tpv.toXML(offset)
        outputXML += '</Techpack>' + offsetStr 
        return outputXML
    
    def getInstalledVersions(self, server):
        ''' return a list of the versions of the named TP installed on the specified server'''
        self.logger.debug(self.tpName+ ".getInstalledVersions()")
        reslist = []
        with TPAPI.DbAccess(server,'dwhrep') as crsr:
            crsr.execute("SELECT VERSIONID FROM dwhrep.Versioning WHERE TECHPACK_NAME=?", [self.tpName])
            for res in crsr.fetchall():
                reslist.append(res[0])
        return reslist
    
    def getAllProperties(self,server):
        ''' Get Versioning Information for all versions of the techpack on the server'''
        self.logger.debug(self.tpName+ ".getAllProperties()")
        with TPAPI.DbAccess(server,'dwhrep') as crsr:
            crsr.execute("SELECT VERSIONID FROM dwhrep.Versioning WHERE TECHPACK_NAME=?", [self.tpName])
            for res in crsr.fetchall():
                versionID=res[0]
                self.__populateProperties(versionID, server)
                
        self.getActiveTP(server)
        return
                
    def getPropertiesFromServer(self,server, versionID):
        '''Get Versioning Information for a specific version of a techpack'''
        self.logger.debug(self.tpName+ ".getPropertiesFromServer()")
        if versionID not in self.listOfVersionIDs:
            self.__populateProperties(versionID, server)
        return self.listTechPackVersionObjects[versionID]        
              
    def __populateProperties(self, versionID, server):
        '''makes sure we have the current tech pack version properties loaded'''
        self.logger.debug(self.tpName+ ".__populateProperties()")
        if versionID not in self.listOfVersionIDs: 
            self.listOfVersionIDs.append(versionID)
            tpv = TechPackVersion(versionID)
            tpv.getPropertiesFromServer(server)
            self.listTechPackVersionObjects.append(tpv)
        
    def getActiveTP(self, server):
        ''' Gets the active version of the techpack '''
        ''' If not active ACTIVETP attribute is set to NOT_ACTIVE'''
        self.logger.debug(self.tpName+ ".getActiveTP()")
        if self.ACTIVETP is not 'NOT_ACTIVE':
            return self.ACTIVETP
        with TPAPI.DbAccess(server,'dwhrep') as crsr:        
            
            crsr.execute("SELECT VERSIONID FROM dwhrep.TPActivation WHERE TECHPACK_NAME =?", (self.tpName,))
            row=crsr.fetchone()
            if row:
                self.ACTIVETP = str(row[0])
            else:
                self.ACTIVETP = 'NOT_ACTIVE'
            return self.ACTIVETP
            
 
    def printTPInfo(self):
        self.logger.debug(self.tpName+ ".printTPInfo()")
        #print self.versionID
        self.cursorDwhrep.execute('SELECT TECHPACK_VERSION,PRODUCT_NUMBER,DESCRIPTION,BASEDEFINITION,LICENSENAME  FROM dwhrep.Versioning WHERE VERSIONID=?',self.versionID )
        row = self.cursorDwhrep.fetchall();
        for i in row:
            print "\n"
            print "TechPack: " + self.versionID
            print "RState: " + i.TECHPACK_VERSION
            print "Product Number: " + i.PRODUCT_NUMBER
            print "Description: " + i.DESCRIPTION
            print "Base Definition: " + i.BASEDEFINITION
            print "Licenses: " + i.LICENSENAME
    
        self.cursorDwhrep.execute("SELECT UNIVERSENAME,UNIVERSEEXTENSION,UNIVERSEEXTENSIONNAME FROM dwhrep.UniverseName WHERE VERSIONID =?", self.versionID)
        row = self.cursorDwhrep.fetchall();
        print "\nUniverse Info: "
        for i in row:
            print "Universe Name: " + i.UNIVERSENAME
            print "Universe Extension: " + i.UNIVERSEEXTENSION
            print "Universe Extension Name: " + i.UNIVERSEEXTENSIONNAME
    
        self.cursorDwhrep.execute("SELECT VENDORRELEASE FROM dwhrep.SupportedVendorRelease WHERE VERSIONID =?",self.versionID)
        row = self.cursorDwhrep.fetchall();
        print "\nVendor Releases: "
        for i in row:
            print i.VENDORRELEASE
        return
