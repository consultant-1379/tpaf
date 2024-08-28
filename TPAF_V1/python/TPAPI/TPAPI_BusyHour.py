# esalste
from __future__ import with_statement
import TPAPI
import logging
import re
import warnings
from TPAPI_Util import deprecated

class BusyHour(object):
        '''Class to represent Busy Hour object associated with a techpack version.
        Uniquely identified by the Busy Hour object name and the techpack versionID.'''
            
        def __init__(self,versionID,name):
            '''Class is instantiated with the versionID and name of the busy hour object
            
            Instance Variables:
            
                self.versionID:
                    Description: VersionID of the TechPackVersion
                    Type:String
                    
                self.name:
                    Description:Name of the busy hour object
                    Type:String
                    
                self.supportedTables:
                    Description: List of tables which retain data for this busy hour
                    Type:List
                    
                self.rankingTable:
                    Description: Ranking table of the busy hour object
                    Type: String
                    
                self.busyHourTypeObjects:
                    Description: Dictionary of Child busy hour type objects
                    Type: Dictionary
                    Keys:
                        Child Busy Hour Type names
            
            '''
            self.logger = logging.getLogger('TPAPI.TPAPI_TP.BusyHour')
            self.versionID = versionID
            self.name = name
            self.supportedTables = []
            self.rankingTable = ''
            self.busyHourTypeObjects = {} 
            
            
        def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
         
            if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                if self.name in xlsDict['BHOBJECT']:
                    for Name, Values in xlsDict['BHOBJECT'][self.name].iteritems():
                        att = TPAPI.BusyHourType(self.versionID,self.name,Name)
                        att._getPropertiesFromXls(Values)
                        self.busyHourTypeObjects[Name] = att
            

        def _getPropertiesFromServer(self,crsr):
            '''Get the properties associated with the busy hour object'''
            self._getBusyHourTypes(crsr)
            self._getBusyHourSupportedTables(crsr)
            self._getBusyHourRankingTable(crsr)
            
        def _getBusyHourTypes(self,crsr):
            '''Gets the busyHour type information for the busy hour object
               
               This function will populate the busyHourTypeObjects dictionary with child busyhour types
               
               SQL Executed: 
                           SELECT BHTYPE FROM dwhrep.BUSYHOUR where VERSIONID=? AND BHOBJECT=?
   
               '''
            crsr.execute("SELECT BHTYPE FROM dwhrep.BUSYHOUR where VERSIONID=? AND BHOBJECT=?",(self.versionID,self.name,))
            resultset = crsr.fetchall()
            for row in resultset:
                bt = BusyHourType(self.versionID,self.name,row[0])
                bt._getPropertiesFromServer(crsr)
                self.busyHourTypeObjects[str(row[0])] = bt
        
        def _getBusyHourSupportedTables(self,crsr):
            '''Gets the list of measurement tables which load for (support) the busy hour object'''
            if self.name == 'ELEM':
                crsr.execute("SELECT DISTINCT TYPENAME FROM dwhrep.MeasurementType where VERSIONID=? AND ELEMENTBHSUPPORT like ? AND RANKINGTABLE =?",(self.versionID,'1','0',))
            else:
                crsr.execute("SELECT DISTINCT BHTARGETTYPE FROM dwhrep.BUSYHOURMAPPING where VERSIONID=? AND BHOBJECT=?",(self.versionID,self.name,))
            resultset = crsr.fetchall()
            for row in resultset:
                self.supportedTables.append(str(row[0]))
        
        def _getBusyHourRankingTable(self,crsr):
            '''Gets the Ranking Table associated with the busyhour object'''
            if self.name == 'ELEM':
                self.rankingTable = self.versionID.rsplit(':')[0] + "_ELEMBH"
            else:
                crsr.execute("SELECT DISTINCT BHLEVEL FROM dwhrep.BUSYHOURMAPPING where VERSIONID=? AND BHOBJECT=?",(self.versionID,self.name,))
                row = crsr.fetchone()
                if row is not None:
                    self.rankingTable = str(row[0])
                        
        def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            sheet = workbook.getSheet('Fact Tables')
            
            if self.name != 'ELEM':
                for tableName in self.supportedTables:
                    columnNumber = sheet.findCell('Object BHs').getColumn()
                    rowNumber = sheet.findCell(tableName).getRow()
                    
                    tableRow = sheet.getRow(rowNumber)
                    value = tableRow[columnNumber].getContents()
                    if value != '' and value != None:
                        value = value + ','
                    label = Label(columnNumber, rowNumber, value + self.name)
                    sheet.addCell(label)
                     
            label = Label(sheet.findCell('Object BHs').getColumn(), sheet.findCell(self.rankingTable).getRow(), self.name)
            sheet.addCell(label)
            
            for BHT in self.busyHourTypeObjects.itervalues():
                BHT._toXLS(workbook)
            
            

        def _toXML(self,indent=0):
            '''Write the object to an xml formatted string
            
            Offset value is used for string indentation. Default to 0
            Parent toXML() method is responsible for triggering child object toXML() methods.
    
            Return Value: xmlString 
            '''
            
            offset = '    '
            os = "\n" + offset*indent
            os2 = os + offset
            os3 = os2 + offset
            
            outputXML = os+'<BusyHour name="' + str(self.name) +'">'
            outputXML += os2+'<RankingTable>'+ str(self.rankingTable) +'</RankingTable>'
            outputXML += os2+'<BusyHourSupportedTables>'  
            for table in self.supportedTables:  
                    outputXML += os3+'<BHSupportedTable>'+ table +'</BHSupportedTable>'          
            outputXML += os2+'</BusyHourSupportedTables>'  
            outputXML += os2+'<BusyHourTypes>' 
            for bhtype in self.busyHourTypeObjects:
                outputXML += self.busyHourTypeObjects[bhtype]._toXML(indent+2)
            outputXML += os2+'</BusyHourTypes>'  
            outputXML += os2+'</BusyHour>'  
            return outputXML 
 
        def _getPropertiesFromXML(self,xmlElement):
            '''Populates the objects content from an xmlElement.
            
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
            
            self.logger.info(self.name + " Inside _getPropertiesFromXML function")
            for elem in xmlElement:
                if elem.tag=='BusyHourObjectName':
                    for elem1 in elem:
                        self.name = TPAPI.safeNull(elem1.text)
                if elem.tag=='RankingTable': 
                    self.rankingTable = TPAPI.safeNull(elem.text)
                if elem.tag=='BusyHourSupportedTables':
                    for elem3 in elem:
                            self.supportedTables.append(TPAPI.safeNull(elem3.text))
                if elem.tag== 'BusyHourTypes':   
                    for elem1 in elem:
                        bht = TPAPI.BusyHourType(self.versionID,self.name,elem1.attrib['name'])
                        bht._getPropertiesFromXML(elem1)
                        self.busyHourTypeObjects[elem1.attrib['name']] = bht


        def _getPropertiesFromTPI(self,tpiDict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing
            
            Exceptions: 
                       Raised if tpiDict and filename are both None (ie nothing to process)'''
            
            self.logger.debug(self.name + "._getPropertiesFromTPI()")
            if tpiDict==None and filename==None:
                strg = 'getPropertiesFromTPI() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    tpidict = TPAPI.TpiDict(filename).returnTPIDict()
                for row in tpiDict['Busyhour']['BHOBJECT']:
                    if tpiDict['Busyhour']['BHOBJECT'][row] == self.name:
                        bht = TPAPI.BusyHourType(self.versionID,self.name,tpiDict['Busyhour']['BHTYPE'][row])
                        bht._getPropertiesFromTPI(tpiDict)
                        self.busyHourTypeObjects[tpiDict['Busyhour']['BHTYPE'][row]] = bht            
                if 'Busyhourmapping' in tpiDict:         
                    for row in tpiDict['Busyhourmapping']['BHOBJECT']:
                        if tpiDict['Busyhourmapping']['BHOBJECT'][row] == self.name: 
                            if tpiDict['Busyhourmapping']['BHTARGETTYPE'][row] not in self.supportedTables:
                                self.supportedTables.append(tpiDict['Busyhourmapping']['BHTARGETTYPE'][row])  
                if self.name == 'ELEM':
                    self.rankingTable = self.versionID.rsplit(':')[0] + "_ELEMBH"
                    
                    for row in tpiDict['Measurementtype']['TYPEID']:
                        if tpiDict['Measurementtype']['RANKINGTABLE'][row] == '0' and tpiDict['Measurementtype']['ELEMENTBHSUPPORT'][row] == '1':
                            self.supportedTables.append(tpiDict['Measurementtype']['TYPENAME'][row])

                else:    
                    if 'Busyhourmapping' in tpiDict:
                        for row in tpiDict['Busyhourmapping']['BHOBJECT']:
                            if tpiDict['Busyhourmapping']['BHOBJECT'][row] == self.name: 
                                if tpiDict['Busyhourmapping']['BHLEVEL'][row] not in self.supportedTables:
                                    self.rankingTable = tpiDict['Busyhourmapping']['BHLEVEL'][row]
                                                  
        def _populateRepDbModel(self, TPRepDbInterface):
            bhDict = {}
            if self.name != 'ELEM':
                for table in self.supportedTables:
                    bhDict['TYPEID'] = self.versionID + ":" +table
                    bhDict['OBJBHSUPPORT'] = self.name
                    TPRepDbInterface.populateMeasurementobjBhSupport(bhDict)
                
                
                bhDict['TYPEID'] = self.versionID + ":" +self.rankingTable
                bhDict['OBJBHSUPPORT'] = self.name
                TPRepDbInterface.populateMeasurementobjBhSupport(bhDict)

            bhDict = {}
            #To populate busy hour place holder count
            bhDict['VERSIONID'] = self.versionID
            bhDict['BHLEVEL'] = self.rankingTable
            
            productPlaceHolderCount= 0
            customPlaceHolderCount= 0
            for key in self.busyHourTypeObjects.iterkeys():
                if key.startswith('PP'):
                    productPlaceHolderCount = productPlaceHolderCount + 1
                elif key.startswith('CP'):
                    customPlaceHolderCount = customPlaceHolderCount + 1
                    
            bhDict['PRODUCTPLACEHOLDERS'] = productPlaceHolderCount
            bhDict['CUSTOMPLACEHOLDERS'] = customPlaceHolderCount
            TPRepDbInterface.populateBusyhourPlaceholders(bhDict)
            
            bhDict = {}
            #To populate BusyHour
            TPRepDbInterface.BusyHourRankingTable = self.rankingTable
                        
            for bhTypeObj in sorted(self.busyHourTypeObjects.iterkeys()):
                self.busyHourTypeObjects[bhTypeObj]._populateRepDbModel(TPRepDbInterface)
                
                if self.name != 'ELEM':
                    for table in self.supportedTables:
                        if table != '' or table != None:
                            bhDict['VERSIONID'] = self.versionID
                            bhDict['BHLEVEL'] = self.rankingTable
                            bhDict['BHTYPE'] = bhTypeObj
                            bhDict['TARGETVERSIONID'] = self.versionID
                            bhDict['BHOBJECT'] = self.name
                            bhDict['TYPEID'] = self.versionID + ":" + table
                            bhDict['BHTARGETTYPE'] = table
                            bhDict['BHTARGETLEVEL'] = self.name + "_" + bhTypeObj
                            bhDict['ENABLE'] = 1
                            
                            TPRepDbInterface.populateBusyHourMapping(bhDict)

        def difference(self,bhObject,deltaObj=None):
            '''Calculates the difference between two busy hour objects
            
            Method takes bhObject,deltaObj and deltaTPV as inputs.
            bhObject: The Busy Hour object to be compared against
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
                deltaObj = TPAPI.Delta(self.name,bhObject.name)
            
            ################################################################
            # BH Rank Table Diff
            if self.rankingTable != bhObject.rankingTable:
                deltaObj.location.append('Rank Table')
                deltaObj.addChange('<Changed>', 'Properties', self.rankingTable, bhObject.rankingTable)
                deltaObj.location.pop()
            
            ################################################################
            # BH Support Tables Diff
            deltaObj.location.append('Supported Table')
            Delta = list(set(bhObject.supportedTables) - set(self.supportedTables))
            for table in Delta:
                deltaObj.addChange('<Added>', 'Properties', '', table)
            
            Delta = list(set(self.supportedTables) - set(bhObject.supportedTables))
            for table in Delta:
                deltaObj.addChange('<Removed>', 'Properties', table, '')
            
            deltaObj.location.pop()
            
            ################################################################
            # BH Type Diff
            Delta = TPAPI.DictDiffer(self.busyHourTypeObjects,bhObject.busyHourTypeObjects)
            deltaObj.location.append('BusyHourType')
            for item in Delta.added():
                deltaObj.addChange('<Added>', bhObject.busyHourTypeObjects[item].name, '', item)
          
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', self.busyHourTypeObjects[item].name, item, '')
            
            deltaObj.location.pop()
            
            for item in Delta.common():
                deltaObj.location.append('BusyHourType='+item)
                deltaObj = self.busyHourTypeObjects[item].difference(bhObject.busyHourTypeObjects[item],deltaObj)
                deltaObj.location.pop()            
            
            return deltaObj
        
        
        def _createDefaultBusyHourTypes(self):
            '''Create the default ENIQ busy hour type objects associated with the Busy Hour Object'''
            
            customPlaceHolders = ['CP0','CP1','CP2','CP3','CP4']
            productPlaceHolders = ['PP0','PP1','PP2','PP3','PP4']
            
            for bhType in productPlaceHolders:   
                if bhType not in self.busyHourTypeObjects:  
                    bhTypeC = TPAPI.BusyHourType(self.versionID,self.name,bhType)
                    bhTypeC._getDefaultProperties()
                    self.busyHourTypeObjects[bhType] = bhTypeC
                            
            for pholder in customPlaceHolders:
                bhTypeC = TPAPI.BusyHourType(self.versionID,self.name,pholder)
                bhTypeC._getDefaultProperties()
                self.busyHourTypeObjects[pholder] = bhTypeC

        

########################################################################################################

class BusyHourType(object):
      #REFACTOR THIS CLASS TO BUSYHOURPLACEHOLDER
    
        '''Class to represent Busy Hour Type (PLACEHOLDER). Child object of Busy Hour.
        Uniquely identified by the versionID, busy hour type, busy hour name.'''
        
        def __init__(self,versionID,bhobjectname,bhtype):
            '''Class is instantiated with versionID, parent bhObjectName and bhtype name
            
            Instance Variables:
            
                self.name:
                    Description: Busy Hour Type Name ge. PP1
                    Type:String
                    
                self.versionID:
                    Description: VersionID of the TechPackVersion
                    Type:String
                    
                self.properties:
                    Description: Contains the properties of the Busy Hour Type
                    Type:Dictionary
                        KEYS:
                        
                self.BHOBjectName:
                    Description: Name of the Parent Busy Hour Object
                    Type:String
            '''
            self.logger = logging.getLogger('TPAPI.TPAPI_TP.BusyHourType')
            self.name = bhtype
            self.versionID = versionID
            self.properties = {}
            self.BHOBjectName = bhobjectname
            self.BHSourceTables = []
            self.rankKeys = {}

        def _getPropertiesFromServer(self,crsr):
            '''Get all the properties associated with the busy hourType object'''

            #AGGREGATIONTYPE
            crsr.execute("SELECT BHCRITERIA,WHERECLAUSE,DESCRIPTION,BHELEMENT,ENABLE,AGGREGATIONTYPE,LOOKBACK,P_THRESHOLD,N_THRESHOLD FROM dwhrep.BUSYHOUR where VERSIONID=? AND BHTYPE=? AND BHOBJECT=?",(self.versionID,self.name,self.BHOBjectName,))
            resultset = crsr.fetchall()
            for row in resultset:
                self.properties['BHCRITERIA'] = str(row[0])
                self.properties['WHERECLAUSE'] = str(row[1])
                self.properties['DESCRIPTION'] = str(row[2])
                self.properties['BHELEMENT'] = str(row[3])
                self.properties['ENABLE'] = str(row[4])
                self.properties['AGGREGATIONTYPE'] = str(row[5])
                self.properties['LOOKBACK'] = str(row[6])
                self.properties['P_THRESHOLD'] = str(row[7])
                self.properties['N_THRESHOLD'] = str(row[8])
                        
            #GET SOURCE TABLE
            crsr.execute("SELECT TYPENAME FROM dwhrep.BusyHourSource where VERSIONID=? AND BHTYPE=? AND BHOBJECT=?",(self.versionID,self.name,self.BHOBjectName,))
            resultset = crsr.fetchall()
            for row in resultset:
                self.BHSourceTables.append(row[0])
            
            crsr.execute("SELECT KEYNAME,KEYVALUE FROM dwhrep.BusyHourRankKeys where VERSIONID=? AND BHTYPE=? AND BHOBJECT=?",(self.versionID,self.name,self.BHOBjectName,))
            resultset = crsr.fetchall()
            for row in resultset:
                self.rankKeys[row[0]] = row[1]

        def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            mappingDicts = TPAPI.XlsDict()
            sheet = workbook.getSheet('BH')
            dict = mappingDicts.BHDict
            rowNumber = sheet.getRows()
            
            if self.properties['BHCRITERIA'] != '':
                label = Label(sheet.findCell('Object Name').getColumn(), rowNumber, self.BHOBjectName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Placeholder Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
                
                for FDColumn, Parameter in dict.iteritems():
                    if Parameter in self.properties.keys():
                        value = self.properties[Parameter]
                        label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                        sheet.addCell(label)
            
            sheet = workbook.getSheet('BH Rank Keys')
            rowNumber = sheet.getRows()
            for keyName, keyValue in self.rankKeys.iteritems():
                label = Label(sheet.findCell('Object Name').getColumn(), rowNumber, self.BHOBjectName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Placeholder Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
                label = Label(sheet.findCell('Key Name').getColumn(), rowNumber, keyName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Source Fact Table Name').getColumn(), rowNumber, ",".join(self.BHSourceTables))
                sheet.addCell(label)
                rowNumber = rowNumber + 1

        def _toXML(self,indent=0):
            '''Write the object to an xml formatted string
            
            Offset value is used for string indentation. Default to 0
            Parent toXML() method is responsible for triggering child object toXML() methods.
    
            Return Value: xmlString 
            '''
            
            offset = '    '
            os = "\n" + offset*indent
            os2 = os + offset
            os3 = os2 + offset
            
            outputXML = os+'<BusyHourType name="' + self.name +'">'
            for prop in self.properties:
                outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'

            #need another level?
            outputXML += os2+'<BusyHourSourceTables>'
            for srct in self.BHSourceTables:
                outputXML += os3+'<BusyHourSourceTable>'+srct+'</BusyHourSourceTable>'
            outputXML += os2+'</BusyHourSourceTables>'
            
            #write rankKeys    
            outputXML += os2+'<BusyHourRankKeys>'
            for rankKey in self.rankKeys:
                outputXML += os3+'<'+str(rankKey)+'>'+ self.rankKeys[rankKey] +'</'+str(rankKey)+'>'
            outputXML += os2+'</BusyHourRankKeys>'
            
            outputXML += os+'</BusyHourType>'
            return outputXML 

        def _getPropertiesFromXML(self,xmlElement):
            '''Populates the objects content from an xmlElement.
            
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
            
            self.logger.info(self.name + " Inside getPropertiesFromXML function")
            for prop1 in xmlElement:
                #CHECK THE TAG NAME
                
                if  prop1.tag == 'BusyHourSourceTables':
                    for prop2 in prop1:
                        self.BHSourceTables.append(prop2.text)
                elif prop1.tag == 'BusyHourRankKeys':
                    for prop2 in prop1:
                        self.rankKeys[prop2.tag] = TPAPI.safeNull(prop2.text)
                else:
                    self.properties[prop1.tag] = TPAPI.safeNull(prop1.text)
                
     
        def _getDefaultProperties(self):
            '''Create the default Properties of the BusyHour type
            Populate the objects contents not from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
                           
            self.properties['BHCRITERIA'] = ''
            self.properties['WHERECLAUSE'] = ''
            self.properties['DESCRIPTION'] = ''
            self.properties['ENABLE'] = '0'
            self.properties['AGGREGATIONTYPE'] = 'RANKBH_TIMELIMITED'
            self.properties['LOOKBACK'] = '0'
            self.properties['P_THRESHOLD'] = '0'
            self.properties['N_THRESHOLD'] = '0'
            
            if self.BHOBjectName == 'ELEM': 
                self.properties['BHELEMENT'] = '1'
            else:
                self.properties['BHELEMENT'] = '0'
                       
            self.BHSourceTables.append('')
        
        
        def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Create the default Properties of the BusyHour type'''
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
                    self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                for Name, Value in xlsDict.iteritems():
                    if Name != 'TYPENAME' and Name != 'RANKINGKEYS':
                        self.properties[Name] = Value
                        
                    else:
                        if Name == 'TYPENAME':
                            self.BHSourceTables = Value.split(',')
                        if Name == 'RANKINGKEYS':
                            self.rankKeys = Value
                
                if self.BHOBjectName == 'ELEM':
                    self.properties['BHELEMENT'] = '1'
                else:
                    self.properties['BHELEMENT'] = '0'

                self.properties['ENABLE'] = '1'
                
        
        def _getPropertiesFromTPI(self,tpiDict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing
            
            Exceptions: 
                       Raised if tpiDict and filename are both None (ie nothing to process)'''
            
            self.logger.debug(self.name + "._getPropertiesFromTPI()")
            if tpiDict==None and filename==None:
                strg = 'getPropertiesFromTPI() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    tpiDict = TPAPI.TpiDict(filename).returnTPIDict()
                
                for row in tpiDict['Busyhour']['BHOBJECT']:
                    if tpiDict['Busyhour']['BHOBJECT'][row] == self.BHOBjectName and tpiDict['Busyhour']['BHTYPE'][row] == self.name:
                        self.properties['BHCRITERIA'] = tpiDict['Busyhour']['BHCRITERIA'][row]
                        self.properties['WHERECLAUSE'] = tpiDict['Busyhour']['WHERECLAUSE'][row]
                        self.properties['DESCRIPTION'] = tpiDict['Busyhour']['DESCRIPTION'][row]
                        self.properties['BHELEMENT'] = tpiDict['Busyhour']['BHELEMENT'][row]
                        self.properties['ENABLE'] = tpiDict['Busyhour']['ENABLE'][row]
                        self.properties['P_THRESHOLD'] = tpiDict['Busyhour']['P_THRESHOLD'][row]
                        self.properties['N_THRESHOLD'] = tpiDict['Busyhour']['N_THRESHOLD'][row]
                        self.properties['LOOKBACK'] = tpiDict['Busyhour']['LOOKBACK'][row]
                        self.properties['AGGREGATIONTYPE'] = tpiDict['Busyhour']['AGGREGATIONTYPE'][row]
                
                if 'Busyhoursource' in tpiDict:
                    for row in tpiDict['Busyhoursource']['BHOBJECT']:
                        if tpiDict['Busyhoursource']['BHOBJECT'][row] == self.BHOBjectName and tpiDict['Busyhoursource']['BHTYPE'][row] == self.name:
                            self.BHSourceTables.append(tpiDict['Busyhoursource']['TYPENAME'][row])
                        
                if 'Busyhourrankkeys' in tpiDict:        
                    for row in tpiDict['Busyhourrankkeys']['BHOBJECT']:
                        if tpiDict['Busyhourrankkeys']['BHOBJECT'][row] == self.BHOBjectName and tpiDict['Busyhourrankkeys']['BHTYPE'][row] == self.name:
                            self.rankKeys[tpiDict['Busyhourrankkeys']['KEYNAME'][row]] = tpiDict['Busyhourrankkeys']['KEYVALUE'][row]
        
        def _populateRepDbModel(self, RepDBInterface):
            bhcriteria = {}
            for key,value in self.properties.iteritems():
                bhcriteria[key] = value    
            bhcriteria['VERSIONID'] = self.versionID
            bhcriteria['TARGETVERSIONID'] = self.versionID
            bhcriteria['BHTYPE'] = self.name
            bhcriteria['BHOBJECT'] = self.BHOBjectName
            bhcriteria['REACTIVATEVIEWS'] = 0
                            
            if bhcriteria['AGGREGATIONTYPE'] == 'RANKBH_TIMELIMITED' or bhcriteria['AGGREGATIONTYPE'] == 'RANKBH_TIMECONSISTENT' or bhcriteria['AGGREGATIONTYPE'] == 'RANKBH_PEAKROP':
                bhcriteria['OFFSET'] = 0
            elif bhcriteria['AGGREGATIONTYPE'] == 'RANKBH_SLIDINGWINDOW' or bhcriteria['AGGREGATIONTYPE'] == 'RANKBH_TIMECONSISTENT_SLIDINGWINDOW':
                bhcriteria['OFFSET'] = 15  
            bhcriteria['GROUPING'] = 'None'
            bhcriteria['WINDOWSIZE']= 60
            bhcriteria['PLACEHOLDERTYPE']= self.name[0:2]
            bhcriteria['CLAUSE']= ''
                
            if bhcriteria: 
                RepDBInterface.populateBusyHour(bhcriteria)
            
            #to populate Busy Hour Source table
            bhcriteria = {}

            for table in self.BHSourceTables:
                if table != '':
                    print table
                    bhcriteria['VERSIONID']=self.versionID
                    bhcriteria['BHTYPE']=self.name
                    bhcriteria['TYPENAME']=table
                    bhcriteria['TARGETVERSIONID']=self.versionID
                    bhcriteria['BHOBJECT']=self.BHOBjectName
                       
                    RepDBInterface.populateBusyhourSource(bhcriteria)
            
            #to populate BusyHourrankkeys
            bhcriteria = {}
            orderNo = 0       
            for key,value in self.rankKeys.iteritems():
                if key != '':
                    bhcriteria['KEYNAME']=key
                    bhcriteria['KEYVALUE']=value
                    bhcriteria['VERSIONID']=self.versionID
                    bhcriteria['BHTYPE']=self.name
                    bhcriteria['TARGETVERSIONID']=self.versionID
                    bhcriteria['BHOBJECT']=self.BHOBjectName
                    bhcriteria['ORDERNBR'] = orderNo
                    orderNo = orderNo + 1
                
                    RepDBInterface.populateBusyhourRankkeys(bhcriteria)
                        
        def difference(self,bhTypeObject,deltaObj=None):
            '''Calculates the difference between two busy hour type objects
            
            Method takes bhTypeObject,deltaObj and deltaTPV as inputs.
            bhTypeObject: The Busy Hour Type object to be compared against
            DeltaObj: The single object that gets passed through the entire diff recording the changes.
            DeltaTPV: A TechPackVersion Object that gets passed through the entire diff recording only new content.
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            Note: BHType does not have any child objects
            
            Returns:
                    diffFlag (Boolean indicating where a change was found or not)
                    deltaObj
                    deltaTPV 
            
            '''
            
            if deltaObj is None:
                deltaObj = TPAPI.Delta(self.name,bhTypeObject.name)
            
            Delta = TPAPI.DictDiffer(self.properties,bhTypeObject.properties)
            deltaObj.location.append('Properties')
            for item in Delta.changed():
                deltaObj.addChange('<Changed>', item, self.properties[item], bhTypeObject.properties[item])
            
            for item in Delta.added():
                deltaObj.addChange('<Added>', item, '', bhTypeObject.properties[item])
                    
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', item, self.properties[item], '')
    
            deltaObj.location.pop()
        
            return deltaObj
