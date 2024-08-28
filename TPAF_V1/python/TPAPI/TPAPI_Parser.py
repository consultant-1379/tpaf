
from __future__ import with_statement
import TPAPI
import logging
import copy
import sys, traceback

class Parser(object):
    '''Class to represent a parser object. Identified by VersionID, parentTableName and parserType. Child object of TechPackVersion'''

    def __init__(self,versionID,parentTableName,parserType):
        '''Class is instantiated using versionID, parentTableName and parserType
        
        Instance Variables:
        
            self.versionID:
                Description: VersionID of the TechPackVersion
                Type:String
                
            self.parserType:
                Description: Type of parser eg Ascii,mdc
                Type:String
                
            self.parentTableName = parentTableName # parent table name
                Description: Parent Table name
                Type:String
            
            self.transformationObjects:
                Description: List of child transformation objects in sequence
                Type:List
        
            self.attributeTags:
                Description: stores the mappings between attribute "column names" and their data tags
                Type:Dictionary
                Keys: Attribute (Column) Names
                          
            self.dataTags:
                Description: A list of data tags which load to the table
                Type:List

            self.dataFormatID:
                Description: Unique Identifier of the parser (self.versionID + ":" + self.parentTableName + ":" + self.parserType)
                Type:String
                
            self.transformerID: 
                Description: Unique Identifier of the transformation (self.versionID + ":" + self.parentTableName + ":" + self.parserType)
                            Used to fetch transformations from db
                Type:String
        
        
        '''
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.Parser')
        self.versionID = versionID
        self.parserType = parserType 
        self.parentTableName = parentTableName
        self.transformationObjects = []
        self.attributeTags = {} # stores the mappings between attribute "column names" and their data tags.. ie database vs data
        self.dataTags = [] # stores the mappings between table names and their data tags
        self.dataFormatID = self.versionID + ":" + self.parentTableName + ":" + self.parserType
        self.transformerID = self.versionID + ":" + self.parentTableName + ":" + self.parserType # used to fetch transformationObjects for the parser object
        self.parentAttributeNames = [] # This is used to only get TP specific information. Should not load data from base TP
    
    
    def _getPropertiesFromServer(self,crsr):
        ''''Gets all properties (and child objects) from the server
    
        In this particular case Parser objects dont have a properties dictionary.
        They have transformation objects,tagids and dataids associated with them'''
        
        self._getTransformations(crsr)
        if not self.parentTableName.endswith('BH'):
            self._getTagIDs(crsr)
            self._getDataIDs(crsr)
    
    def setAttributeNames(self, listOfNames):
        self.parentAttributeNames = listOfNames
    
    def _getTagIDs(self,crsr):
        '''Gets TableTags information for the server for the parser object.
        
        Gets the TAGID tags and appends it to a list of dataTags.
        This list defines the default mappings between measurement files received from network elements and measurement tables
        
        
        SQL Executed:
                    SELECT TAGID FROM dwhrep.DefaultTags where DATAFORMATID=?
                    
        
        '''
        crsr.execute("SELECT TAGID FROM dwhrep.DefaultTags where DATAFORMATID=?",(self.dataFormatID,))
        resultset = crsr.fetchall()
        for row in resultset:
            self.dataTags.append(str(row[0]))
                       
    def _getDataIDs(self,crsr):
        '''Gets attributeTags information for the server for the parser object
        
        Gets the DATANAME  and DATAID
        
        creates the parser object and appends it
        to the list of attributeTags
        
        The Dictionary contains the tags for each counter with respect to each table
        
        The Dictionary defines the default mappings between counters of the measurement files received from network elements and 
        Counters in the measurement tables of TECHPACK
        
        
        SQL Executed:
                    SELECT DATANAME,DATAID FROM dwhrep.DataItem where DATAFORMATID=?
        
        '''
        crsr.execute("SELECT DATANAME,DATAID FROM dwhrep.DataItem where DATAFORMATID=?",(self.dataFormatID,))
        rows = crsr.fetchall()        
        for row in rows:
            if row is not None:
                if row[0] in self.parentAttributeNames:
                    self.attributeTags[row[0]] = str(row[1])

    def _getTransformations(self,crsr):
        '''Gets transformation information for the server for the parser object,creates the transformation object and appends it
        to the list of transformationObjects'''
        rowIDs = []
        
        crsr.execute("SELECT ORDERNO FROM dwhrep.Transformation where TRANSFORMERID=?",(self.transformerID,))
        row = crsr.fetchall()
        for x in row:
            rowIDs.append(int(TPAPI.strFloatToInt(x[0])))
          
        for rowid in sorted(rowIDs):
            transformation = TPAPI.Transformation(rowid, self.transformerID)
            transformation._getPropertiesFromServer(crsr)
            self.transformationObjects.append(transformation)

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

        outputXML  = os+ '<Parser type="'+self.parserType+'">'

        outputXML +=os2+ '<Dataformat DataFormatID="'+self.transformerID+'">'
        tags = []
        for tag in self.dataTags:
            tags.append(tag)
        outputXML +=os3+'<TableTags>'
        for tag in tags:
            outputXML +=os4+ '<TableTag>'+str(tag)+'</TableTag>'
        outputXML +=os3+'</TableTags>'
        outputXML +=os3+'<attributeTags>'
        
        for col,row in self.attributeTags.iteritems():
            outputXML += os4+'<'+str(col)+'>'+str(row)+'</'+str(col)+'>'
        outputXML +=os3+'</attributeTags>'
        outputXML +=os2+ '</Dataformat>'
        
        if len(self.transformationObjects) > 0:
            outputXML +=os2+ '<Transformations transformerID="'+self.transformerID+'">'
            for transformer in self.transformationObjects:
                outputXML += transformer._toXML(indent+2)
            outputXML +=os2+'</Transformations>'
        
        outputXML +=os+'</Parser>'
        return outputXML
    
    def _getPropertiesFromXML(self,xmlElement):
        '''Populates the objects content from an xmlElement.
        
        The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
        index = 0 
        for elem in xmlElement:
            if elem.tag=='Transformations':
                for elem1 in elem:
                    if elem1.tag == "OrderNo":
                        transformation = TPAPI.Transformation(elem1.attrib['index'], self.transformerID)
                        transformation._getPropertiesFromXML(elem1)
                        self.transformationObjects.append(transformation)
                        index = index + 1         
            
            if elem.tag == 'Dataformat':
                for elem1 in elem:
                    for elem2 in elem1:
                        if elem1.tag == "TableTags":
                            self.dataTags.append(elem2.text)
                        if elem1.tag == 'attributeTags':
                            self.attributeTags[elem2.tag]= elem2.text
    
    
    def _getPropertiesFromTPI(self,tpiDict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing.

            Exceptions: 
                       Raised if tpiDict and filename are both None (ie nothing to process)'''
            
            self.logger.debug(self.parserType + "._getPropertiesFromTPI()")
            if tpiDict==None and filename==None:
                strg = 'getPropertiesFromTPI() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    tpiDict = TPAPI.TpiDict(filename).returnTPIDict()

            rowIDs = []
            index = 0
            for row in tpiDict['Transformation']['TRANSFORMERID']:
                if tpiDict['Transformation']['TRANSFORMERID'][row].lower() == self.transformerID.lower():
                    if row in tpiDict['Transformation']['ORDERNO']:
                        rowIDs.append(int(tpiDict['Transformation']['ORDERNO'][row]))
            
            rowIDs.sort()           
            for rowid in rowIDs:
                transformation = TPAPI.Transformation(rowid ,self.transformerID)
                transformation._getPropertiesFromTPI(tpiDict)
                self.transformationObjects.append(transformation)
            
            if not self.parentTableName.endswith('BH'):
                for row in tpiDict['Dataitem']['DATAFORMATID']:
                    if tpiDict['Dataitem']['DATAFORMATID'][row].lower() == self.dataFormatID.lower():
                        if tpiDict['Dataitem']['DATANAME'][row] in self.parentAttributeNames:
                            self.attributeTags[tpiDict['Dataitem']['DATANAME'][row]] = tpiDict['Dataitem']['DATAID'][row]
                
                for row in tpiDict['Defaulttags']['DATAFORMATID']:
                    if tpiDict['Defaulttags']['DATAFORMATID'][row].lower() == self.dataFormatID.lower():
                        self.dataTags.append(tpiDict['Defaulttags']['TAGID'][row])
                
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
            self.logger.debug(self.dataFormatID + "._getPropertiesFromXls()")
            
            if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                    
                rowIDs = xlsDict.keys()    
                rowIDs.sort()
                
                for rowid in rowIDs:
                    if rowid != 'DATATAGS' and rowid != 'ATTRTAGS':
                        transformation = TPAPI.Transformation(rowid ,self.transformerID)
                        transformation._getPropertiesFromXls(xlsDict[rowid])
                        self.transformationObjects.append(transformation)
                        
                if 'DATATAGS' in xlsDict:
                    if ';' in xlsDict['DATATAGS']:
                        tableTags = xlsDict['DATATAGS'].split(';')
                        for tag in tableTags:
                            if tag != '':
                                self.dataTags.append(tag.strip())
                    else:
                        self.dataTags.append(xlsDict['DATATAGS'].strip())
                
                if 'ATTRTAGS' in xlsDict.keys():
                    for key, value in xlsDict['ATTRTAGS'].iteritems():
                        self.attributeTags[key] = value
                        
                        
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
        
        sheet = workbook.getSheet('Data Format')
        rowNumber = sheet.getRows()
        
        parserColumn = None
        parserCell = sheet.findCell(self.parserType)
        if parserCell == None:
            parserColumn = sheet.getColumns()
            label = Label(parserColumn, 0, self.parserType)
            sheet.addCell(label)
        else:
            parserColumn = parserCell.getColumn()
        
        tableCell = sheet.findCell(self.parentTableName)
        if tableCell != None:
            rowNumber = tableCell.getRow()
          
        for AttName,format in sorted(self.attributeTags.iteritems()):
            label = Label(sheet.findCell('Table Name').getColumn(), rowNumber, self.parentTableName)
            sheet.addCell(label)
            label = Label(sheet.findCell('Counter/key Name').getColumn(), rowNumber, AttName)
            sheet.addCell(label)
            label = Label(parserColumn, rowNumber, format)
            sheet.addCell(label)
            rowNumber = rowNumber +1        
        
        if self.parentTableName.startswith('DC'):
            sheet = workbook.getSheet('Fact Tables')
            parserColumn = None
            parserCell = sheet.findCell(self.parserType)
            if parserCell == None:
                parserColumn = sheet.getColumns()
                label = Label(parserColumn, 0, self.parserType)
                sheet.addCell(label)
            else:
                parserColumn = parserCell.getColumn()
            
            label = Label(parserColumn, 0, self.parserType)
            sheet.addCell(label)
            
            label = Label(parserColumn, sheet.findCell(self.parentTableName).getRow(), ";".join(self.dataTags))
            sheet.addCell(label)
        
        if self.parentTableName.startswith('DIM'):
            sheet = workbook.getSheet('Topology Tables')
            parserColumn = None
            parserCell = sheet.findCell(self.parserType)
            if parserCell == None:
                parserColumn = sheet.getColumns()
                label = Label(parserColumn, 0, self.parserType)
                sheet.addCell(label)
            else:
                parserColumn = parserCell.getColumn()
            
            label = Label(parserColumn, 0, self.parserType)
            sheet.addCell(label)
            
            label = Label(parserColumn, sheet.findCell(self.parentTableName).getRow(), ";".join(self.dataTags))
            sheet.addCell(label)
        
        
        if self.parserType not in TransformationCollection:
            TransformationCollection[self.parserType] = {}
        
        for trans in self.transformationObjects:
            TransformationCollection[self.parserType][int(trans.rowID)] = trans
        
        return TransformationCollection
        
                    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}
        RepDbDict[self.dataFormatID] = self.attributeTags 
        TPRepDbInterface.populateAttributeTags(RepDbDict)
        
        TPRepDbInterface.populateDefaultTags(self.dataFormatID, self.dataTags)
        
        for transformation in self.transformationObjects:
            transformation._populateRepDbModel(TPRepDbInterface)
        
      
    def difference(self,prsrObj,deltaObj=None):
        '''Calculates the difference between two parser objects
        
            Method takes prsrObj,deltaObj and deltaTPV as inputs.
            prsrObj: The parser to be compared against
            DeltaObj: The single object that gets passed through the entire diff recording the changes.
            DeltaTPV: A TechPackVersion Object that gets passed through the entire diff recording only new content.
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            
            Parser Difference method deviates from other diff methods in that it explicity calculates the diff for transformations.
            Transformation objects do not have a diff method.
            Transformation Hash value is used to find index changes in transformationObjects. If a transformation has moved sequence it index will be reported as
            having being moved, if the other transformationObjects have not changed sequence (but their index has moved) they are ignored . Transformations 
            are either new, deleted or have has their index changed. Diff does not happen at the transformation object level
            because its possible to have two transformationObjects under the same parser object with exactly the same properties/config
            
            Returns:
                    diffFlag (Boolean indicating where a change was found or not)
                    deltaObj
                    deltaTPV 
        '''
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.parserType,prsrObj.parserType)
            
        ############################################## Attribute Tags Difference #####################################################
        deltaObj.location.append('AttributeTags') 

        Delta = TPAPI.DictDiffer(self.attributeTags,prsrObj.attributeTags)
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.attributeTags[item], prsrObj.attributeTags[item])
    
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', prsrObj.attributeTags[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.attributeTags[item], '')
        
        deltaObj.location.pop()
        
        ############################################## Data Tags Difference #####################################################
        deltaObj.location.append('DataTags') 
        
        Delta = list(set(prsrObj.dataTags) - set(self.dataTags))    
        for item in Delta:
            deltaObj.addChange('<Added>', item, '', item)
                
        Delta = list(set(self.dataTags) - set(prsrObj.dataTags))    
        for item in Delta:
            deltaObj.addChange('<Removed>', item, item, '')
        
        deltaObj.location.pop()
        
        ############################################## Transformation Difference #####################################################  
        origHashDict = {}
        upgradeHashDict = {}
         
        for transformation in self.transformationObjects:
            hashval = transformation._getHash()
            origHashDict[hashval] = transformation
         
        for transformation in prsrObj.transformationObjects:
            hashval = transformation._getHash()
            upgradeHashDict[hashval] = transformation
        
        upgradeHashListCopy = copy.deepcopy(upgradeHashDict.keys()) 
        origHashListCopy = copy.deepcopy(origHashDict.keys()) 
        deltaTransforms = set(upgradeHashDict.keys()).difference(set(origHashDict.keys()))
        removedTransforms = set(origHashDict.keys()).difference(set(upgradeHashDict.keys())) 
        
        deltaObj.location.append('Transformation')
        for x in removedTransforms:
            origHashListCopy.remove(x)
            deltaObj.addChange('<Removed>', origHashDict[x].transformerID, origHashDict[x].rowID, '')          
             
        for x in deltaTransforms:
            upgradeHashListCopy.remove(x)
            deltaObj.addChange('<Added>', upgradeHashDict[x].transformerID, '', upgradeHashDict[x].rowID)
          
        for trans in list(origHashListCopy):
            if upgradeHashListCopy.index(trans) != origHashListCopy.index(trans):
                deltaObj.addChange('<Changed>', upgradeHashDict[trans].transformerID, origHashDict[trans].rowID, upgradeHashDict[trans].rowID)
        
        deltaObj.location.pop()
        
        return deltaObj
