
from __future__ import with_statement
import TPAPI
import re
import logging
from copy import deepcopy
import warnings
from TPAPI_Util import deprecated

class Table(object):
        '''Class to represent a table in a Tech Pack Version. Child of TechPackVersion class. Uniquely identified by its
        name and versionid (combined these are know as the typeid). Tables can be of either 'Measurement' or 'Reference' type
        '''
        def __init__(self,name,versionID):
            '''Class is initialised with the name of the table and the teckpack versionID
            
            Instance Variables:
            
               self.versionID:
                    Description: versionID of the parent techpack version. eg DC_E_BSS:((100)).
                    Type:String
                    
                self.tableType:
                    Description: Type of the table either 'Measurement' or 'Reference'.
                    Type:String
                    
                self.name:
                    Description: Name of the table.
                    Type: String
                    
                self.properties:
                    Description: Contains the properties of the table.
                    Type: Dictionary
                    Keys: Dependent on the tableType
                        Reference Table Keys: 
                                              DESCRIPTION
                                              UPDATE_POLICY
                                              TABLE_TYPE
                                              DATAFORMATSUPPORT
                                              
                        Measurement Table Keys: 
                                                TYPECLASSID
                                                DESCRIPTION
                                                JOINABLE
                                                SIZING
                                                TOTALAGG
                                                ELEMENTBHSUPPORT
                                                RANKINGTABLE
                                                DELTACALCSUPPORT
                                                PLAINTABLE
                                                UNIVERSEEXTENSION
                                                VECTORSUPPORT
                                                DATAFORMATSUPPORT
                                                VENDORID
                                                TYPENAME
                                                FOLDERNAME
                                                TYPEID
                                                VERSIONID
                        
                self.attributeObjects:
                    Description: Contains the attribute objects associated with the table.
                    Type:Dictionary
                    Keys: Attribute Names
                    
                self.parserNames:
                    Description: Parser names associated with the fact table.. ie ascii, mdc.
                    Type:List
                    
                self.parserObjects:
                    Description: Contains the Parser Objects associated with a table.
                    Type: Dictionary
                    Keys: Parser Names
                
                self.universeClass:
                    Description: The universe class the table object belongs to.
                    Type: String
                    
                self.typeid:
                    Description: Unique identifier of a table (versionID + ":" + name) eg. DC_E_BSS:((100)):DC_E_BSS_MEASTABLE
                    Type:String
                    
                self.typeClassID:
                    Description: Unique identifier for the universe class the table is associated with (versionid + ":" + tpname + ":" + universeClass).eg. DC_E_STN:((13)):DC_E_STN_IPv6PingMeasurement
                    Type: String
                
                self.mtableIDs:
                    Description: Partition types of the table (versionID+":"+name+":" + RAW/PLAIN/DAY/COUNT) ie DC_E_BSS:((100)):DC_E_BSS_MEASTABLE:RAW).
                    Type: List
            '''
            self.logger = logging.getLogger('TPAPI.TPAPI_TP.TechPackVersion.Table')
            self.versionID = versionID
            self.tableType = '' 
            self.name = name
            self.properties = {} 
            self.attributeObjects = {}
            self.parserNames = []
            self.parserObjects = {} 
            self.universeClass = ''
            self.typeid = versionID + ":" + name
            self.typeClassID = '' 
            self.mtableIDs = []
            self.logger.debug(self.versionID + ":" +self.name + ".__init__()")
            
        def _getTableTypeFromServer(self,crsr):
            '''Get and sets the tableType of the table from a lookup to the dwhrep
            
            self.tableType is set to either 'Measurement','Reference' or 'UNDEF'
            Depending on result returned.
            
            SQL Executed:
                    SELECT COUNT(*) from dwhrep.MeasurementType WHERE TYPEID =?
                    SELECT COUNT(*) from dwhrep.ReferenceTable WHERE TYPEID =?
            
            Exceptions:
                        Raised if the table is not found in the dwhrep
            '''
            
            self.logger.debug(self.versionID + ":" +self.name + "._getTableTypeFromServer()")

            crsr.execute("SELECT COUNT(*) from dwhrep.MeasurementType WHERE TYPEID =?", (self.typeid,)) 
            row = crsr.fetchone()
            if row[0] > 0:
                self.tableType = 'Measurement'
                return
            else:
                crsr.execute("SELECT COUNT(*) from dwhrep.ReferenceTable WHERE TYPEID =?", (self.typeid,))
                row = crsr.fetchone()
                if row[0] > 0:
                    self.tableType = 'Reference'
                    return
                else:
                    strg = '_getTableTypeFromServer() Table not found in dwhrep'
                    raise Exception(strg)
                    self.logger.error(strg)
         
        def _getPropertiesFromServer(self,crsr):
            '''Gets all properties (and child objects) of the table from the server
            
            This method triggers multiple sub methods for retrieving information
            from the dwhrep
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getPropertiesFromServer()")
            self._getTableTypeFromServer(crsr)            
            if self.tableType == 'Reference':
                self._getReferenceTablePropertiesFromServer(crsr)
                self._getAllAttributes(crsr)
            elif self.tableType == 'Measurement':
                self._getMeasurementTablePropertiesFromServer(crsr)
                self._getAllAttributes(crsr)
            else:
                pass
            self._getMeasurementTypeClassIDFromServer(crsr)
            self._getMeasurementUniverseClassFromServer(crsr)
            self._getParserNamesFromServer(crsr)
            self._getParserObjects(crsr)
        
        def _getEventsPropertiesFromServer(self,server):
            '''Gets all properties (and child objects) of the table for an Events Techpack, from the server
            
            This method triggers multiple sub methods for retrieving information
            from the dwhrep
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getEventsPropertiesFromServer()")
            self._getTableTypeFromServer(server)
            if self.tableType == 'Reference':
                self._getReferenceTablePropertiesFromServer(server)
                self._getAllAttributes(server)
            elif self.tableType == 'Measurement':
                self._getEventMeasurementTablePropertiesFromServer(server)
                self._getAllAttributes(server)
            else:
                pass
            self._getParserNamesFromServer(server)
            self._getParserObjects(server)
        
        def _getPropertiesFromTPI(self,tpidict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing.

            Exceptions: 
                       Raised if tpiDict and filename are both None (ie nothing to process)'''
            self.logger.debug(self.name + "._getPropertiesFromTPI()")
            if tpidict==None and filename==None:
                strg = 'getPropertiesFromTPI() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    tpidict = TPAPI.TpiDict(filename).returnTPIDict()  
                if self.tableType =='Measurement':
                    for row in tpidict['Measurementtype']['TYPEID']:
                        if self.typeid == tpidict['Measurementtype']['TYPEID'][row]:
                            self.tableType = 'Measurement'
                            self.properties['TYPECLASSID'] = tpidict['Measurementtype']['TYPECLASSID'][row]
                            self.properties['DESCRIPTION'] = tpidict['Measurementtype']['DESCRIPTION'][row]
                            self.properties['JOINABLE'] = tpidict['Measurementtype']['JOINABLE'][row]
                            self.properties['SIZING'] = tpidict['Measurementtype']['SIZING'][row]
                            self.properties['TOTALAGG'] = tpidict['Measurementtype']['TOTALAGG'][row]
                            self.properties['ELEMENTBHSUPPORT'] = tpidict['Measurementtype']['ELEMENTBHSUPPORT'][row]
                            self.properties['RANKINGTABLE'] = tpidict['Measurementtype']['RANKINGTABLE'][row]
                            self.properties['DELTACALCSUPPORT'] = tpidict['Measurementtype']['DELTACALCSUPPORT'][row]
                            self.properties['PLAINTABLE'] = tpidict['Measurementtype']['PLAINTABLE'][row]
                            self.properties['UNIVERSEEXTENSION'] = tpidict['Measurementtype']['UNIVERSEEXTENSION'][row]
                            self.properties['VECTORSUPPORT'] = TPAPI.checkNull(tpidict['Measurementtype']['VECTORSUPPORT'][row])
                            self.properties['DATAFORMATSUPPORT'] = tpidict['Measurementtype']['DATAFORMATSUPPORT'][row]
                            self.properties['TYPEID']=tpidict['Measurementtype']['TYPEID'][row]
                            self.properties['VERSIONID']=tpidict['Measurementtype']['VERSIONID'][row]
                            
                            for row in tpidict['Measurementtypeclass']['TYPECLASSID']:
                                if self.properties['TYPECLASSID'].lower() == tpidict['Measurementtypeclass']['TYPECLASSID'][row].lower():
                                    self.universeClass = tpidict['Measurementtypeclass']['DESCRIPTION'][row]
                            for row in tpidict['Measurementkey']['TYPEID']:
                                if self.typeid == tpidict['Measurementkey']['TYPEID'][row]:
                                    att = TPAPI.Attribute(tpidict['Measurementkey']['DATANAME'][row],self.typeid,'measurementKey')
                                    att._getPropertiesFromTPI(tpidict)
                                    self.attributeObjects[tpidict['Measurementkey']['DATANAME'][row]] = att
                            for row in tpidict['Measurementcounter']['TYPEID']:
                                if self.typeid == tpidict['Measurementcounter']['TYPEID'][row]:
                                    att = TPAPI.Attribute(tpidict['Measurementcounter']['DATANAME'][row],self.typeid,'measurementCounter')
                                    att._getPropertiesFromTPI(tpidict)
                                    self.attributeObjects[tpidict['Measurementcounter']['DATANAME'][row]] = att                     
                            break
         
                elif self.tableType == 'Reference':
                    for row in tpidict['Referencetable']['TYPEID']:
                        if self.typeid == tpidict['Referencetable']['TYPEID'][row]:
                            self.typeFlag = 'Reference'
                            self.properties['DESCRIPTION'] = tpidict['Referencetable']['DESCRIPTION'][row]
                            self.properties['UPDATE_POLICY'] = tpidict['Referencetable']['UPDATE_POLICY'][row]
                            self.properties['DATAFORMATSUPPORT'] = tpidict['Referencetable']['DATAFORMATSUPPORT'][row]
                            for row in tpidict['Referencecolumn']['TYPEID']:
                                if self.typeid == tpidict['Referencecolumn']['TYPEID'][row]:
                                    if tpidict['Referencecolumn']['BASEDEF'][row] == '0':
                                        att = TPAPI.Attribute(tpidict['Referencecolumn']['DATANAME'][row],self.typeid,'referenceKey')
                                        att._getPropertiesFromTPI(tpidict)
                                        self.attributeObjects[tpidict['Referencecolumn']['DATANAME'][row]] = att
                            break

                if 'Dataformat' in tpidict:
                    for row in tpidict['Dataformat']['DATAFORMATTYPE']: 
                        if tpidict['Dataformat']['DATAFORMATTYPE'][row] not in self.parserNames:
                            self.parserNames.append(tpidict['Dataformat']['DATAFORMATTYPE'][row])    
                    for prsr in self.parserNames:
                        parser = TPAPI.Parser(self.versionID,self.name,prsr)
                        parser.setAttributeNames(self.attributeObjects.keys())
                        parser._getPropertiesFromTPI(tpidict)
                        self.parserObjects[prsr] = parser
                    
            self._completeModel()
        
        def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
            self.logger.debug(self.name + "._getPropertiesFromXls()")
            
            if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                for Name, Values in xlsDict['Tables'][self.name].iteritems():
                    if Name == 'measurementKey' or Name == 'measurementCounter' or Name == 'referenceKey':
                        for entry, properties in Values.iteritems():
                            att = TPAPI.Attribute(entry,self.typeid,Name)
                            att._getPropertiesFromXls(properties)
                            self.attributeObjects[entry] = att
                    elif Name == 'Parser':
                        for entry, properties in Values.iteritems():
                            if self.tableType == 'Measurement':
                                if 'DATATAGS' in xlsDict['Tables'][self.name]:
                                    properties['DATATAGS'] = xlsDict['Tables'][self.name]['Parser'][entry]['DATATAGS']
                            elif self.tableType == 'Reference':
                                if 'DATATAGS' in xlsDict['Tables'][self.name]['Parser'][entry]:
                                    properties['DATATAGS'] = xlsDict['Tables'][self.name]['Parser'][entry]['DATATAGS']
                            self.parserNames.append(entry)
                            parser = TPAPI.Parser(self.versionID,self.name,entry)
                            parser._getPropertiesFromXls(properties)
                            self.parserObjects[entry] = parser
                    elif Name == 'CLASSIFICATION':
                        self.universeClass = Values
                    elif Name == 'OBJECTBH':
                        pass
                    else:
                        if Name != 'TABLETYPE':
                            self.properties[Name] = Values
                            
            self._completeModel()
   
            
        def _getMeasurementTypeClassIDFromServer(self,crsr):
            '''Gets the typeClassID for a measurement table from the server
            
            SQL Executed:
                    SELECT TYPECLASSID from dwhrep.measurementType where TYPEID =?
            '''
            self.logger.debug(self.versionID + "._getMeasurementTypeClassIDFromServer()")
            
            if self.name.rsplit('_')[0] != 'DIM' and self.name.rsplit('_')[-1] != 'AGGLEVEL':
                crsr.execute("SELECT TYPECLASSID from dwhrep.measurementType where TYPEID =?", (self.typeid ,))
                row = crsr.fetchone()
                self.typeClassID = str(row[0])
            
        def _getMeasurementUniverseClassFromServer(self,crsr):     
            '''Gets the universeClass for a measurement table from the server
            
            SQL Executed:
                        SELECT DESCRIPTION from dwhrep.measurementTypeClass where TYPECLASSID =?
            '''
            self.logger.debug(self.versionID + "._getMeasurementUniverseClassFromServer()")

            if self.typeClassID != '':
                crsr.execute("SELECT DESCRIPTION from dwhrep.measurementTypeClass where TYPECLASSID =?", (self.typeClassID ,))
                row = crsr.fetchone()
                self.universeClass = str(row[0])
        
        def _getMeasurementTablePropertiesFromServer(self,crsr):
            '''Populates the properties dictionary of the Measurement table from the server
            
            SQL Executed:
                        SELECT TYPECLASSID,DESCRIPTION,JOINABLE,SIZING,TOTALAGG,ELEMENTBHSUPPORT,RANKINGTABLE,DELTACALCSUPPORT,PLAINTABLE,UNIVERSEEXTENSION,VECTORSUPPORT,DATAFORMATSUPPORT,VENDORID,TYPENAME,FOLDERNAME,TYPEID,VERSIONID from dwhrep.MeasurementType WHERE TYPEID =?
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getMeasurementTablePropertiesFromServer()")
    
            crsr.execute("SELECT TYPECLASSID,DESCRIPTION,JOINABLE,SIZING,TOTALAGG,ELEMENTBHSUPPORT,RANKINGTABLE,DELTACALCSUPPORT,PLAINTABLE,UNIVERSEEXTENSION,VECTORSUPPORT,DATAFORMATSUPPORT,VENDORID,TYPENAME,FOLDERNAME,TYPEID from dwhrep.MeasurementType WHERE TYPEID =?", (self.typeid,)) 
            row = crsr.fetchone()
            self.properties['TYPECLASSID'] = TPAPI.checkNull(str(row[0]))
            self.properties['DESCRIPTION'] = TPAPI.checkNull(str(row[1]).strip())
            self.properties['JOINABLE'] = TPAPI.checkNull(str(row[2]))
            self.properties['SIZING'] = TPAPI.checkNull(str(row[3]))
            self.properties['TOTALAGG'] = TPAPI.checkNull(str(row[4]))
            self.properties['ELEMENTBHSUPPORT'] = TPAPI.checkNull(str(row[5]))
            self.properties['RANKINGTABLE'] = TPAPI.checkNull(str(row[6]))
            self.properties['DELTACALCSUPPORT'] = TPAPI.checkNull(str(row[7]))
            self.properties['PLAINTABLE'] = TPAPI.checkNull(str(row[8]))
            self.properties['UNIVERSEEXTENSION'] = TPAPI.checkNull(str(row[9]))             
            self.properties['VECTORSUPPORT'] = TPAPI.checkNull(str(row[10]))
            self.properties['DATAFORMATSUPPORT'] = TPAPI.checkNull(str(row[11]))
            self.properties['TYPEID']=TPAPI.checkNull(str(row[15]))
        
            if self.properties['DELTACALCSUPPORT'] == '1':
                supportedVendorReleases = []
                crsr.execute("SELECT VENDORRELEASE FROM dwhrep.SupportedVendorRelease WHERE VERSIONID =?", (self.versionID,))
                resultset = crsr.fetchall()
                for row in resultset:
                    supportedVendorReleases.append(str(row[0]))
                
                update = False
                crsr.execute("SELECT VENDORRELEASE FROM dwhrep.MeasurementDeltaCalcSupport where TYPEID=?",(self.typeid,))
                resultset = crsr.fetchall()
                for row in resultset:
                    supportedVendorReleases.remove(str(row[0]))

                self.properties['DELTACALCSUPPORT'] = ",".join(supportedVendorReleases)

            

        def _getReferenceTablePropertiesFromServer(self,crsr):
            '''Populates the properties dictionary of the Reference table from the server
            
            SQL Executed:
                        SELECT DESCRIPTION,UPDATE_POLICY,TABLE_TYPE,DATAFORMATSUPPORT from dwhrep.ReferenceTable WHERE TYPEID =?
    
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getReferenceTablePropertiesFromServer()")
 
            crsr.execute("SELECT DESCRIPTION,UPDATE_POLICY,DATAFORMATSUPPORT from dwhrep.ReferenceTable WHERE TYPEID =?", (self.typeid,)) 
            row = crsr.fetchone()
            self.properties['DESCRIPTION'] = str(row[0]).strip()
            self.properties['UPDATE_POLICY'] = TPAPI.strFloatToInt(str(row[1]))
            self.properties['DATAFORMATSUPPORT'] = str(row[2])

        def _getEventMeasurementTablePropertiesFromServer(self,server):
            '''Populates the properties dictionary of the events Measurement table from the server
            
            SQL Executed:
                        SELECT TYPECLASSID,DESCRIPTION,JOINABLE,SIZING,TOTALAGG,ELEMENTBHSUPPORT,RANKINGTABLE,DELTACALCSUPPORT,PLAINTABLE,UNIVERSEEXTENSION,VECTORSUPPORT,DATAFORMATSUPPORT,ONEMINAGG,MIXEDPARTITIONSTABLE,EVENTSCALCTABLE,LOADFILE_DUP_CHECK,FIFTEENMINAGG from dwhrep.MeasurementType WHERE TYPEID =?
            
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getEventMeasurementTablePropertiesFromServer()")
            with TPAPI.DbAccess(server,'dwhrep') as crsr:
                crsr.execute("SELECT TYPECLASSID,DESCRIPTION,JOINABLE,SIZING,TOTALAGG,ELEMENTBHSUPPORT,RANKINGTABLE,DELTACALCSUPPORT,PLAINTABLE,UNIVERSEEXTENSION,VECTORSUPPORT,DATAFORMATSUPPORT,ONEMINAGG,MIXEDPARTITIONSTABLE,EVENTSCALCTABLE,LOADFILE_DUP_CHECK,FIFTEENMINAGG from dwhrep.MeasurementType WHERE TYPEID =?", (self.typeid,)) 
                row = crsr.fetchone()
                self.properties['TYPECLASSID'] = str(row[0])
                self.properties['DESCRIPTION'] = str(row[1])
                self.properties['JOINABLE'] = str(row[2])
                self.properties['SIZING'] = str(row[3])
                self.properties['TOTALAGG'] = str(row[4])
                self.properties['ELEMBHSUPPORT'] = str(row[5])
                self.properties['RANKINGTABLE'] = str(row[6])
                self.properties['DELTACALCSUPPORT'] = str(row[7])
                self.properties['PLAINTABLE'] = str(row[8])
                self.properties['UNIVERSEEXTENSION'] = str(row[9])
                self.properties['VECTORSUPPORT'] = str(row[10])
                self.properties['DATAFORMATSUPPORT'] = str(row[11])
                self.properties['ONEMINAGG'] = str(row[12])
                self.properties['MIXEDPARTITIONSTABLE'] = str(row[13])
                self.properties['EVENTSCALCTABLE'] = str(row[14])
                self.properties['LOADFILEDUPCHECK'] = str(row[15])
                self.properties['FIFTEENMINAGG'] = str(row[16])
            return   

        def _getAllAttributes(self,crsr):
            '''Get attributes information associated with the table from the server.
            
             Creates a child attribute object and adds the object to the self.attributeObjects dictionary'''
            self.logger.debug(self.versionID + ":" +self.name + "._getAllAttributes()")
                
            if self.tableType == 'Reference':
                crsr.execute("SELECT DATANAME FROM dwhrep.ReferenceColumn where TYPEID=? AND BASEDEF=?",(self.typeid,0,))
                row = crsr.fetchall()
                for refKey in row:
                    att = TPAPI.Attribute(str(refKey[0]),self.typeid,'referenceKey')
                    att._getPropertiesFromServer(crsr)
                    self.attributeObjects[str(refKey[0])] = att
            elif self.tableType == 'Measurement':
                crsr.execute("SELECT DATANAME FROM dwhrep.MeasurementKey where TYPEID=?",(self.typeid,))
                row = crsr.fetchall()
                for measKey in row:
                    att = TPAPI.Attribute(str(measKey[0]),self.typeid,'measurementKey')
                    att._getPropertiesFromServer(crsr)
                    self.attributeObjects[str(measKey[0])] = att
                crsr.execute("SELECT DATANAME FROM dwhrep.MeasurementCounter where TYPEID=?",(self.typeid,))
                row = crsr.fetchall()
                for measCounter in row:
                    att = TPAPI.Attribute(str(measCounter[0]),self.typeid,'measurementCounter')
                    att._getPropertiesFromServer(crsr)
                    self.attributeObjects[str(measCounter[0])] = att 
        
        def _getParserNamesFromServer(self,crsr):
            '''Get a list of parser names (ie mdc,ascii) associated with the measurement table from the server
            
            Names are appended to self.parserNames list
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._getParserNamesFromServer()")
                
            crsr.execute("SELECT DISTINCT DATAFORMATTYPE FROM dwhrep.DataFormat WHERE TYPEID =?", (self.typeid,)) 
            resultset = crsr.fetchall()
            for row in resultset:
                self.parserNames.append(str(row[0])) 

        def _getParserObjects(self,crsr):
            '''Gets child parser objects of the table 
            
            Using self.parserNames the method get parser information from the server, creates the child parser
            object and adds the object to the self.parserObjects dictionary'''
            self.logger.debug(self.versionID + ":" +self.name + "._getParserObjects()")

            for prsr in self.parserNames:
                parser = TPAPI.Parser(self.versionID,self.name,prsr)
                parser.setAttributeNames(self.attributeObjects.keys())
                parser._getPropertiesFromServer(crsr)
                self.parserObjects[prsr] = parser
        
        
        def _getTypeClassID(self):
            '''Getter for self.typeClassID'''         
            self._setTypeClassID()
            return self.typeClassID

        def _setTypeClassID(self):
            '''Setter for self.typeClassID'''
            self.typeClassID = self.versionID + ":" + self.versionID.rsplit(':')[0] + "_" + self.universeClass
            
            
        def _toXLS(self, workbook, TransformationCollection):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label 
            
            sheet = None
            dict = None
            rowNumber = None
            mappingDicts = TPAPI.XlsDict()
            
            if self.tableType == 'Measurement':
                sheet = workbook.getSheet('Fact Tables')
                dict = mappingDicts.FactTableDict
                rowNumber = sheet.getRows()
                label = Label(sheet.findCell('Fact Table Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
                
            elif self.tableType == 'Reference':
                sheet = workbook.getSheet('Topology Tables')
                dict = mappingDicts.TopTableDict
                rowNumber = sheet.getRows()
                label = Label(sheet.findCell('Topology Table Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    if Parameter == 'UPDATE_POLICY':
                        value = mappingDicts.updatePolicylist[int(value)]
                    if value == 1 or value == '1':
                        value = 'Y'
                    elif value == 0 or value == '0':
                        value = ''
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                    sheet.addCell(label)
                elif Parameter == 'CLASSIFICATION':
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(self.universeClass))
                    sheet.addCell(label)
                    
            for attribute in self.attributeObjects.itervalues():
                attribute._toXLS(workbook, self.name)
            
            for parser in self.parserObjects.itervalues():
                parser._toXLS(workbook, TransformationCollection)
            
            return TransformationCollection
            
        def _completeModel(self):
            if self.tableType == 'Measurement':
                if 'ELEMENTBHSUPPORT' not in self.properties or self.properties['ELEMENTBHSUPPORT'] == '':
                    self.properties['ELEMENTBHSUPPORT'] = '0'
                if 'PLAINTABLE' not in self.properties or self.properties['PLAINTABLE'] == '':
                    self.properties['PLAINTABLE'] = '0'
                if 'RANKINGTABLE' not in self.properties or self.properties['RANKINGTABLE'] == '':
                    self.properties['RANKINGTABLE'] = '0'
                if 'TOTALAGG' not in self.properties or self.properties['TOTALAGG'] == '':
                    self.properties['TOTALAGG'] = '0'            
                if 'VECTORSUPPORT' not in self.properties or self.properties['VECTORSUPPORT'] == '':
                    self.properties['VECTORSUPPORT'] = '0'
                if 'JOINABLE' not in self.properties or self.properties['JOINABLE'] == '':
                    self.properties['JOINABLE'] = ''
                if 'DELTACALCSUPPORT' not in self.properties or self.properties['DELTACALCSUPPORT'] == '':
                    self.properties['DELTACALCSUPPORT'] = '0'
            
            self.properties['DATAFORMATSUPPORT'] = '1'

        def _toXML(self,indent=0):
            '''Write the object to an xml formatted string
            
            Indent value is used for string indentation. Default to 0
            Parent toXML() method is responsible for triggering child object toXML() methods.
    
            Return Value: xmlString 
            '''
            self.logger.debug(self.versionID + ":" +self.name + "._toXML()")
            
            offset = '    '
            os = "\n" + offset*indent
            os2 = os + offset

            outputXML =os+'<Table name="'+self.name+ '" tableType="'+self.tableType+ '" universeClass= "'+self.universeClass +'">'
            for prop in self.properties:
                outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
            outputXML  += os2 + '<Attributes>'
            for attribute in self.attributeObjects:
                outputXML += self.attributeObjects[attribute]._toXML(indent+2)
            outputXML  += os2 + '</Attributes>'
            outputXML  += os2 + '<Parsers>' 
            for parser in self.parserObjects:
                outputXML += self.parserObjects[parser]._toXML(indent+2)
            outputXML  += os2 + '</Parsers>'
            outputXML +=os+'</Table>'
            return outputXML
        
        def _getPropertiesFromXML(self,xmlElement):
            '''Populates the objects content from an xmlElement.
            
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
            
            self.logger.debug(self.versionID + ":" +self.name + "._getPropertiesFromXML()")
            self.tableType = xmlElement.attrib['tableType']
            self.universeClass = xmlElement.attrib['universeClass'] 
            for elem1 in xmlElement:
                if elem1.tag=='Attributes':
                        for elem2 in elem1:
                            if elem2.tag=='Attribute':
                                tpAttrb = TPAPI.Attribute(elem2.attrib['name'],self.typeid,elem2.attrib['attributeType'])
                                tpAttrb._getPropertiesFromXML(elem2)
                                self.attributeObjects[elem2.attrib['name']] = tpAttrb  
                elif elem1.tag=='Parsers':
                        for elem2 in elem1:
                            if elem2.tag=='Parser':
                                if elem2.attrib['type'] not in self.parserNames:
                                    self.parserNames.append(elem2.attrib['type'])
                                tpParser = TPAPI.Parser(self.versionID,self.name,elem2.attrib['type'])
                                tpParser._getPropertiesFromXML(elem2)
                                self.parserObjects[elem2.attrib['type']] = tpParser
                else:
                    self.properties[elem1.tag] = TPAPI.safeNull(elem1.text)

        
        def difference(self,tableObject,deltaObj=None):
            '''Calculates the difference between two table objects
            
            Method takes tableObject,deltaObj and deltaTPV as inputs.
            TableObject: The table to be compared against
            DeltaObj: The single object that gets passed through the entire diff recording the changes.
            DeltaTPV: A TechPackVersion Object that gets passed through the entire diff recording only new content.
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            Returns:
                    diffFlag (Boolean indicating where a change was found or not)
                    deltaObj
                    deltaTPV 
            
            '''
            
            if deltaObj is None:
                deltaObj = TPAPI.Delta(self.typeid,tableObject.typeid)
            
            ############################################## Properties Difference #####################################################
            deltaObj.location.append('Properties') 
            if self.universeClass != tableObject.universeClass:
                deltaObj.addChange('<Changed>', 'Classification', self.universeClass, tableObject.universeClass)

            Delta = TPAPI.DictDiffer(self.properties,tableObject.properties)
            for item in Delta.changed():
                if item != 'TYPEID' and item !=  'TYPECLASSID' and item !=  'VERSIONID':
                    deltaObj.addChange('<Changed>', item, self.properties[item], tableObject.properties[item])
        
            for item in Delta.added():
                if item != 'TYPEID' and item !=  'TYPECLASSID' and item !=  'VERSIONID':
                    deltaObj.addChange('<Added>', item, '', tableObject.properties[item])
                    
            for item in Delta.removed():
                if item != 'TYPEID' and item !=  'TYPECLASSID' and item !=  'VERSIONID':
                    deltaObj.addChange('<Removed>', item, self.properties[item], '')
            
            deltaObj.location.pop()
            
            ############################################## Attributes Difference #####################################################
            Delta = TPAPI.DictDiffer(self.attributeObjects,tableObject.attributeObjects)
            deltaObj.location.append('Attribute')
            for item in Delta.added():
                deltaObj.addChange('<Added>', tableObject.attributeObjects[item].attributeType, '', item)
          
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', self.attributeObjects[item].attributeType, item, '')
            
            deltaObj.location.pop()
              
            for item in Delta.common():
                deltaObj.location.append('Attribute='+item)
                deltaObj = self.attributeObjects[item].difference(tableObject.attributeObjects[item],deltaObj)
                deltaObj.location.pop()
            
            
            ############################################## Parser Difference #####################################################
            Delta = TPAPI.DictDiffer(self.parserObjects,tableObject.parserObjects)
            deltaObj.location.append('Parser')
            for item in Delta.added():
                deltaObj.addChange('<Added>', tableObject.parserObjects[item].parserType, '', item)
          
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', self.parserObjects[item].parserType, item, '')
            
            deltaObj.location.pop()
              
            for item in Delta.common():
                deltaObj.location.append('Parser='+item)
                deltaObj = self.parserObjects[item].difference(tableObject.parserObjects[item],deltaObj)
                deltaObj.location.pop()
            
            return deltaObj
        
        def _populateRepDbModel(self, TPRepDbInterface):
            if self.tableType == 'Measurement':
                
                self.properties['TYPECLASSID'] = self._getTypeClassID()
                self.properties['VERSIONID'] = self.versionID
                
                #MeasurementTypeClass
                RepDbDict = {}
                RepDbDict = deepcopy(self.properties)
                RepDbDict['DESCRIPTION'] = self.universeClass
                TPRepDbInterface.populateMeasurementTypeClass(RepDbDict)
                
                DELTACALCSUPPORT = 0
                #Measurementdeltacalcsupport
                if 'DELTACALCSUPPORT' in self.properties:
                    if self.properties['DELTACALCSUPPORT'] != None and self.properties['DELTACALCSUPPORT'].strip() != '0':
                        RepDbDict = {}
                        RepDbDict['TYPEID'] = self.versionID + ":" + self.name
                        RepDbDict['VERSIONID'] = self.versionID
                        RepDbDict['VENDORRELEASE'] = self.properties['DELTACALCSUPPORT']
                        TPRepDbInterface.populateMeasurementdeltacalcsupport(RepDbDict)
                        DELTACALCSUPPORT = 1
                
                #MeasurementType
                RepDbDict = {}
                RepDbDict = deepcopy(self.properties)
                RepDbDict['TYPEID'] = self.versionID + ":" + self.name
                RepDbDict['TYPENAME'] = self.name
                RepDbDict['VENDORID'] = self.versionID.rsplit(':')[0]
                RepDbDict['FOLDERNAME'] = self.name
                RepDbDict['OBJECTID'] = self.versionID + ":" + self.name
                RepDbDict['OBJECTNAME'] = self.name
                RepDbDict['DELTACALCSUPPORT'] = DELTACALCSUPPORT
                TPRepDbInterface.populateMeasurementType(RepDbDict)
            
            if self.tableType == 'Reference':
                RepDbDict = {}
                RepDbDict = deepcopy(self.properties)
                RepDbDict['VERSIONID'] = self.versionID
                RepDbDict['TYPEID'] = self.versionID + ":" + self.name
                RepDbDict['TYPENAME'] = self.name
                RepDbDict['OBJECTID'] = self.versionID + ":" + self.name
                RepDbDict['OBJECTNAME'] = self.name
                RepDbDict['BASEDEF'] = 0
                TPRepDbInterface.populateReferencetable(RepDbDict)
                   
            measCounterColNumber = 1
            measKeyColNumber = 1
            refKeyColNumber = 100
            for attribute in sorted(self.attributeObjects.iterkeys()):
                if self.attributeObjects[attribute].attributeType == 'measurementCounter':
                    self.attributeObjects[attribute]._populateRepDbModel(TPRepDbInterface, self.typeid, measCounterColNumber)
                    measCounterColNumber = measCounterColNumber + 1
                if self.attributeObjects[attribute].attributeType == 'referenceKey':
                    self.attributeObjects[attribute]._populateRepDbModel(TPRepDbInterface, self.typeid, refKeyColNumber)
                    refKeyColNumber = refKeyColNumber + 1
                if self.attributeObjects[attribute].attributeType == 'measurementKey':
                    self.attributeObjects[attribute]._populateRepDbModel(TPRepDbInterface, self.typeid, measKeyColNumber)
                    measKeyColNumber = measKeyColNumber + 1
            
            for parserName, parser in self.parserObjects.iteritems():
                parser._populateRepDbModel(TPRepDbInterface)
