from __future__ import with_statement
import TPAPI
import logging
from copy import deepcopy

class Attribute(object):
        '''Class to represent any column in a table. Identified by its
        name and attributeType. attributeType property is either 'measurementCounter','referenceKey' or 'measurementKey'.
        '''

        def __init__(self,name,typeid,attributeType):
            '''
            Initialised with name and the attributeType
            
            self.attributeType:
                Description: Type of the attribute. either 'measurementCounter', 'referenceKey' or 'measurementKey'
                Type:String
                
            self.name:
                Description: name of the attribute
                Type: String
                
            self.properties:
                Description: Contains the properties of for the attribute object
                Type: Dictionary
                Keys: (Dependent on the attribute Type)
                
                'measurementCounter':
                        DESCRIPTION
                        TIMEAGGREGATION
                        GROUPAGGREGATION
                        COUNTAGGREGATION
                        DATATYPE
                        DATASIZE
                        DATASCALE
                        INCLUDESQL
                        UNIVOBJECT
                        UNIVCLASS
                        COUNTERTYPE
                        COUNTERPROCESS
                        DATAID
                        
                        
                'measurementKey':
                        DESCRIPTION
                        ISELEMENT
                        UNIQUEKEY
                        DATATYPE
                        DATASIZE
                        DATASCALE
                        NULLABLE
                        INDEXES
                        INCLUDESQL
                        UNIVOBJECT
                        JOINABLE
                        DATAID
                        
                'referenceKey':
                        DATATYPE
                        DATASIZE
                        DATASCALE
                        NULLABLE
                        INDEXES
                        UNIQUEKEY
                        INCLUDESQL
                        INCLUDEUPD
                        DESCRIPTION
                        DATAID

            '''
            
            self.logger = logging.getLogger('TPAPI.TPAPI_TP.TechPackVersion.FactTableVersion.Attribute')
            validAttTypes = ['measurementCounter','referenceKey','measurementKey']
            if attributeType not in validAttTypes:
                strg = 'TPAPI.TPAPI_TP.TechPackVersion.FactTableVersion.Attribute.init() invalid attributeType'
                self.logger.error(strg)
                raise Exception(strg)
            self.typeid = typeid
            self.attributeType = attributeType
            self.name = name
            self.properties = {}
            self.vectors = {}
            self._parentTableName = '' #this is set outside the class by the get properties from tpi method of the table class, NOT always populated
            self.logger.debug(self.name + ".__init__()")
        
        def _getPropertiesFromServer(self,crsr):
            '''Gets the properties of the attribute from the server using the tables typeid.
            
            Populates self.properties dictionary depending on the attributeType
            
            Sql Statement:
                    SELECT DATATYPE,DATASIZE,DATASCALE,NULLABLE,INDEXES,UNIQUEKEY,INCLUDESQL,INCLUDEUPD,DESCRIPTION,DATAID,UNIVERSECONDITION,UNIVERSECLASS,UNIVERSEOBJECT  from dwhrep.ReferenceColumn
                    SELECT DESCRIPTION,ISELEMENT,UNIQUEKEY,DATATYPE,DATASIZE,DATASCALE,NULLABLE,INDEXES,INCLUDESQL,UNIVOBJECT,JOINABLE,DATAID from dwhrep.MeasurementKey
                    SELECT DESCRIPTION,TIMEAGGREGATION,GROUPAGGREGATION,COUNTAGGREGATION,DATATYPE,DATASIZE,DATASCALE,INCLUDESQL,UNIVOBJECT,UNIVCLASS,COUNTERTYPE,COUNTERPROCESS,DATAID from dwhrep.MeasurementCounter WHERE TYPEID=? AND DATANAME=?        
            
            Exceptions:
                    Raised if attributeType is not recognised
            
            '''
            self.logger.debug(self.name + ".getAttributeProperties()")
    
            if self.attributeType == 'referenceKey':                    
                self.key = True
                crsr.execute("SELECT DATATYPE,DATASIZE,DATASCALE,NULLABLE,UNIQUEKEY,INCLUDESQL,INCLUDEUPD,DESCRIPTION,DATAID,UNIVERSEOBJECT,UNIVERSECLASS,UNIVERSECONDITION  from dwhrep.ReferenceColumn WHERE TYPEID =? AND DATANAME=? AND BASEDEF=?", (self.typeid,self.name,0,))
            elif self.attributeType =='measurementKey':
                self.key = True
                crsr.execute("SELECT DESCRIPTION,ISELEMENT,UNIQUEKEY,DATATYPE,DATASIZE,DATASCALE,NULLABLE,INDEXES,INCLUDESQL,UNIVOBJECT,JOINABLE,DATAID from dwhrep.MeasurementKey WHERE TYPEID=? AND DATANAME=?",(self.typeid,self.name,))
            elif self.attributeType =='measurementCounter':                    
                self.key = False
                crsr.execute("SELECT DESCRIPTION,TIMEAGGREGATION,GROUPAGGREGATION,DATATYPE,DATASIZE,DATASCALE,INCLUDESQL,UNIVOBJECT,UNIVCLASS,COUNTERTYPE,DATAID from dwhrep.MeasurementCounter WHERE TYPEID=? AND DATANAME=?",(self.typeid,self.name,))
            else:
                raise "Error, attribute type %s is not recognised." % self.attributeType
            
            resultset = crsr.fetchall()
            desc = crsr.description
            for row in resultset: 
                i = 0
                for x in desc:                 
                    self.properties[x[0]] = TPAPI.checkNull(str(row[i]).strip())
                    i+=1
                
            if self.attributeType =='measurementCounter':
                if self.properties['COUNTERTYPE'].upper() == 'VECTOR':
                    crsr.execute("SELECT VENDORRELEASE,VINDEX from dwhrep.MeasurementVector WHERE TYPEID=? AND DATANAME=?",(self.typeid,self.name,))
                    rows = crsr.fetchall()
                    for row in rows:
                        vendRel = TPAPI.checkNull(str(row[0]).strip())
                        index = TPAPI.strFloatToInt(str(row[1]).strip())
                        if vendRel not in self.vectors:
                            self.vectors[vendRel] = {}
                        vector = TPAPI.Vector(self.typeid, self.name, index, vendRel)
                        vector._getPropertiesFromServer(crsr)
                        self.vectors[vendRel][index] = vector
    
        def difference(self,attObject,deltaObj=None):
            '''Calculates the difference between two attribute objects
            
            Method takes attObject,deltaObj and deltaTPV as inputs.
            attObject: The table to be compared against
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
                deltaObj = TPAPI.Delta(self.name,attObject.name)
            
            ############################################## Properties Difference #####################################################
            deltaObj.location.append('Properties') 

            Delta = TPAPI.DictDiffer(self.properties,attObject.properties)
            for item in Delta.changed():
                deltaObj.addChange('<Changed>', item, self.properties[item], attObject.properties[item])
        
            for item in Delta.added():
                deltaObj.addChange('<Added>', item, '', attObject.properties[item])
                    
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', item, self.properties[item], '')
            
            deltaObj.location.pop()
            
            ############################################## Vectors Difference #####################################################
            deltaObj.location.append('Vectors')

            Delta = TPAPI.DictDiffer(self.vectors,attObject.vectors)        
            for item in Delta.added():
                deltaObj.addChange('<Added>', item, '', item)
                    
            for item in Delta.removed():
                deltaObj.addChange('<Removed>', item, item, '')
                
            for item in Delta.changed():
                indexDelta = TPAPI.DictDiffer(self.vectors[item],attObject.vectors[item])
                for entry in indexDelta.added():
                    deltaObj.addChange('<Added>', item, '', entry)
                        
                for entry in indexDelta.removed():
                    deltaObj.addChange('<Removed>', +entry, entry, '')
                    
                for entry in indexDelta.changed():
                    self.vectors[item][entry].difference(attObject.vectors[item][entry],deltaObj)

            
            deltaObj.location.pop()

            return deltaObj
        
        
        def _toXLS(self, workbook, tableName):
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
            
            if self.attributeType == 'measurementKey':
                sheet = workbook.getSheet('Keys')
                dict = TPAPI.XlsDict().FTKeysDict
                rowNumber = sheet.getRows()
                label = Label(sheet.findCell('Fact Table Name').getColumn(), rowNumber, tableName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Key Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
            
            if self.attributeType == 'measurementCounter':
                sheet = workbook.getSheet('Counters')
                dict = TPAPI.XlsDict().FTCountersDict
                rowNumber = sheet.getRows()
                label = Label(sheet.findCell('Fact Table Name').getColumn(), rowNumber, tableName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Counter Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
            
            if self.attributeType == 'referenceKey':
                sheet = workbook.getSheet('Topology Keys')
                dict = TPAPI.XlsDict().TopKeysDict
                rowNumber = sheet.getRows()
                label = Label(sheet.findCell('Topology Table name').getColumn(), rowNumber, tableName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Key Name').getColumn(), rowNumber, self.name)
                sheet.addCell(label)
                
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    if value == 1 or value == '1':
                        value = 'Y'
                    elif value == 0 or value == '0':
                        value = ''
                    if Parameter == 'DATATYPE':
                        value = self._createDataTypeForXls()
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                    sheet.addCell(label)
            
            for indices in self.vectors.itervalues():
                for vector in indices.itervalues():
                    vector._toXLS(workbook, tableName, self.name)
                
        def _createDataTypeForXls(self):
            dataype = self.properties['DATATYPE']
            if 'DATASIZE' in self.properties.keys():
                if self.properties['DATASIZE'] != '':
                    dataype = dataype + '('+str(self.properties['DATASIZE'])
                    if 'DATASCALE' in self.properties.keys():
                        if self.properties['DATASCALE'] != '':
                            dataype = dataype + ','+str(self.properties['DATASCALE'])
                    dataype = dataype + ')'
            return dataype
            

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
            os4 = os3 + offset

            outputXML = os+'<Attribute name="'+self.name+ '" attributeType ="'+self.attributeType +'">' 
            for attr in self.properties:
                outputXML += os2+'<'+str(attr)+'>'+TPAPI.escape(self.properties[attr])+'</'+str(attr)+'>'
            
            outputXML += os2+'<Vectors>'
            for vector in sorted(self.vectors.keys()):
                for index in sorted(self.vectors[vector].keys()):
                    self.vectors[vector][index]._toXML(indent+2)
            outputXML += os2+'</Vectors>'
            outputXML += os+'</Attribute>'
            return outputXML
                      
        def _getPropertiesFromXML(self,xmlElement):
            '''Populates the objects content from an xmlElement.
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
            
            self.logger.debug(self.name + "._getPropertiesFromXML()")
            for elem1 in xmlElement:
                if elem1.tag=='Vectors':
                        for elem2 in elem1:
                            if elem2.tag=='Vector':
                                vendRel = elem2.attrib['VendorRelease']
                                index = elem2.attrib['index']
                                if vendRel not in self.vectors:
                                    self.vectors[vendRel] = {}
                                vector = TPAPI.Vector(self.typeid, self.name, index, vendRel)
                                vector._getPropertiesFromXML(elem2)
                                self.vectors[vendRel][index] = vector

                elif elem1.text is None:
                    self.properties[elem1.tag] = ''
                else:
                    self.properties[elem1.tag] = TPAPI.safeNull(elem1.text)

        def _getPropertiesFromTPI(self,tpidict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing
            
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

                if self.attributeType =='measurementKey':
                    for row in tpidict['Measurementkey']['DATANAME']:
                        if tpidict['Measurementkey']['DATANAME'][row] == self.name and tpidict['Measurementkey']['TYPEID'][row] == self.typeid:
                            self.properties['DESCRIPTION'] = TPAPI.checkNull(tpidict['Measurementkey']['DESCRIPTION'][row])
                            self.properties['ISELEMENT'] = TPAPI.checkNull(tpidict['Measurementkey']['ISELEMENT'][row])
                            self.properties['UNIQUEKEY'] = TPAPI.checkNull(tpidict['Measurementkey']['UNIQUEKEY'][row])
                            self.properties['DATATYPE'] = TPAPI.checkNull(tpidict['Measurementkey']['DATATYPE'][row])
                            self.properties['DATASCALE'] = TPAPI.checkNull(tpidict['Measurementkey']['DATASCALE'][row])
                            self.properties['NULLABLE'] = TPAPI.checkNull(tpidict['Measurementkey']['NULLABLE'][row])
                            self.properties['INDEXES'] = TPAPI.checkNull(tpidict['Measurementkey']['INDEXES'][row])
                            self.properties['INCLUDESQL'] = TPAPI.checkNull(tpidict['Measurementkey']['INCLUDESQL'][row])
                            self.properties['UNIVOBJECT'] = TPAPI.checkNull(tpidict['Measurementkey']['UNIVOBJECT'][row])
                            self.properties['JOINABLE'] = TPAPI.checkNull(tpidict['Measurementkey']['JOINABLE'][row])
                            self.properties['DATAID'] = TPAPI.checkNull(tpidict['Measurementkey']['DATAID'][row])
                            self.properties['DATASIZE'] = TPAPI.checkNull(tpidict['Measurementkey']['DATASIZE'][row])

                elif self.attributeType == 'measurementCounter':
                    for row in tpidict['Measurementcounter']['DATANAME']:
                        if tpidict['Measurementcounter']['DATANAME'][row] == self.name and tpidict['Measurementcounter']['TYPEID'][row] == self.typeid:
                            self.properties['DESCRIPTION'] = TPAPI.checkNull(tpidict['Measurementcounter']['DESCRIPTION'][row])
                            self.properties['TIMEAGGREGATION'] = TPAPI.checkNull(tpidict['Measurementcounter']['TIMEAGGREGATION'][row])
                            self.properties['GROUPAGGREGATION'] = TPAPI.checkNull(tpidict['Measurementcounter']['GROUPAGGREGATION'][row])
                            self.properties['DATATYPE'] = TPAPI.checkNull(tpidict['Measurementcounter']['DATATYPE'][row])
                            self.properties['DATASIZE'] = TPAPI.checkNull(tpidict['Measurementcounter']['DATASIZE'][row])
                            self.properties['DATASCALE'] = TPAPI.checkNull(tpidict['Measurementcounter']['DATASCALE'][row])
                            self.properties['INCLUDESQL'] = TPAPI.checkNull(tpidict['Measurementcounter']['INCLUDESQL'][row])
                            self.properties['UNIVOBJECT'] = TPAPI.checkNull(tpidict['Measurementcounter']['UNIVOBJECT'][row])
                            self.properties['UNIVCLASS'] = TPAPI.checkNull(tpidict['Measurementcounter']['UNIVCLASS'][row])
                            self.properties['COUNTERTYPE'] = TPAPI.checkNull(tpidict['Measurementcounter']['COUNTERTYPE'][row])
                            self.properties['DATAID'] = TPAPI.checkNull(tpidict['Measurementcounter']['DATAID'][row])

                elif self.attributeType == 'referenceKey':
                    for row in tpidict['Referencecolumn']['DATANAME']:
                        if tpidict['Referencecolumn']['DATANAME'][row] == self.name and tpidict['Referencecolumn']['TYPEID'][row] == self.typeid:
                            self.properties['DATATYPE'] = TPAPI.checkNull(tpidict['Referencecolumn']['DATATYPE'][row])
                            self.properties['DATASIZE'] = TPAPI.checkNull(tpidict['Referencecolumn']['DATASIZE'][row])
                            self.properties['DATASCALE'] = TPAPI.checkNull(tpidict['Referencecolumn']['DATASCALE'][row])
                            self.properties['NULLABLE'] = TPAPI.checkNull(tpidict['Referencecolumn']['NULLABLE'][row])
                            self.properties['UNIQUEKEY'] = TPAPI.checkNull(tpidict['Referencecolumn']['UNIQUEKEY'][row])
                            self.properties['INCLUDESQL'] = TPAPI.checkNull(tpidict['Referencecolumn']['INCLUDESQL'][row])
                            self.properties['INCLUDEUPD'] = TPAPI.checkNull(tpidict['Referencecolumn']['INCLUDEUPD'][row])
                            self.properties['DESCRIPTION'] = TPAPI.checkNull(tpidict['Referencecolumn']['DESCRIPTION'][row])
                            self.properties['DATAID'] = TPAPI.checkNull(tpidict['Referencecolumn']['DATAID'][row])
                            self.properties['UNIVERSEOBJECT'] = TPAPI.checkNull(tpidict['Referencecolumn']['UNIVERSEOBJECT'][row])
                            self.properties['UNIVERSECLASS'] = TPAPI.checkNull(tpidict['Referencecolumn']['UNIVERSECLASS'][row])
                            self.properties['UNIVERSECONDITION'] = TPAPI.checkNull(tpidict['Referencecolumn']['UNIVERSECONDITION'][row])
                
                if self.attributeType == 'measurementCounter' and self.properties['COUNTERTYPE'].upper() == 'VECTOR':
                    if 'MeasurementVector' in tpidict:
                        for row in tpidict['MeasurementVector']['VINDEX']:
                            if self.name == tpidict['MeasurementVector']['DATANAME'][row] and tpidict['MeasurementVector']['TYPEID'][row] == self.typeid:
                                vendRel = tpidict['MeasurementVector']['VENDORRELEASE'][row]
                                if vendRel not in self.vectors:
                                    self.vectors[vendRel] = {}
                                vector = TPAPI.Vector(self.typeid, self.name,tpidict['MeasurementVector']['VINDEX'][row], vendRel)
                                vector._getPropertiesFromTPI(tpidict)
                                self.vectors[vendRel][tpidict['MeasurementVector']['VINDEX'][row]] = vector
                            
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
                
                for Name, Value in xlsDict.iteritems():
                    if Name == 'Vectors':
                        for vendRel, indices in Value.iteritems():
                            if vendRel not in self.vectors:
                                self.vectors[vendRel] = {}
                            
                            for index, properties in indices.iteritems():
                                vector = TPAPI.Vector(self.typeid, self.name, index, vendRel)
                                vector._getPropertiesFromXls(properties)
                                self.vectors[vendRel][index] = vector
                            
                    else:
                        self.properties[Name] = Value
                    
            self._completeModel()
        
        def _completeModel(self):
            if self.attributeType == 'measurementCounter':
                if 'INCLUDESQL' not in self.properties or self.properties['INCLUDESQL'] == '':
                    self.properties['INCLUDESQL'] = '0'
            
            elif self.attributeType == 'measurementKey':
                if 'ISELEMENT' not in self.properties or self.properties['ISELEMENT'] == '':
                    self.properties['ISELEMENT'] = '0'
                if 'UNIQUEKEY' not in self.properties or self.properties['UNIQUEKEY'] == '':
                    self.properties['UNIQUEKEY'] = '0'
                if 'INCLUDESQL' not in self.properties or self.properties['INCLUDESQL'] == '':
                    self.properties['INCLUDESQL'] = '0'
                if 'NULLABLE' not in self.properties or self.properties['NULLABLE'] == '':
                    self.properties['NULLABLE'] = '0'
                if 'JOINABLE' not in self.properties or self.properties['JOINABLE'] == '':
                    self.properties['JOINABLE'] = '0'
                     
            elif self.attributeType == 'referenceKey':
                if 'UNIQUEKEY' not in self.properties or self.properties['UNIQUEKEY'] == '':
                    self.properties['UNIQUEKEY'] = '0'
                if 'NULLABLE' not in self.properties or self.properties['NULLABLE'] == '':
                    self.properties['NULLABLE'] = '0'
                    
            if 'DATAID' not in self.properties or self.properties['DATAID'] == '':
                    self.properties['DATAID'] = ''
                
        
        def _populateRepDbModel(self, TPRepDbInterface, typeid, colnumber):
            RepDbDict = {}
            RepDbDict = deepcopy(self.properties)
            RepDbDict['DATANAME'] = self.name
            RepDbDict['TYPEID'] = typeid
            RepDbDict['COLNUMBER'] = colnumber
            
            if self.attributeType == 'measurementCounter':
                #MeasurementCounter
                RepDbDict['COUNTERPROCESS'] = self.properties['COUNTERTYPE']
                
                TPRepDbInterface.populateMeasurementCounter(RepDbDict)
            
            elif self.attributeType == 'measurementKey':
                #MeasurementKey
                RepDbDict['UNIQUEVALUE'] = 255
                RepDbDict['JOINABLE'] = 0
                RepDbDict['ROPGRPCELL'] = 0
                
                TPRepDbInterface.populateMeasurementKey(RepDbDict)
                
            elif self.attributeType == 'referenceKey':
                #MeasurementKey
                RepDbDict['UNIQUEVALUE'] = 255
                RepDbDict['INDEXES'] = 'HG'
                RepDbDict['COLTYPE'] = 'COLUMN'
                RepDbDict['BASEDEF'] = 0
                
                TPRepDbInterface.populateReferencecolumn(RepDbDict)
            
            for indices in self.vectors.itervalues():
                for vector in indices.itervalues():
                    print vector
                    vector._populateRepDbModel(TPRepDbInterface)
        