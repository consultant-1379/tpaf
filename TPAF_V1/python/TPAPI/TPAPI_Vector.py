from __future__ import with_statement
import TPAPI
import logging
from copy import deepcopy

class Vector(object):

    def __init__(self,typeid, parentAttName, Index, VendorRelease):
        
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.TechPackVersion.Table.Attribute.Vectors')
        self.typeid = typeid
        self.parentAttName = parentAttName
        self.VendorRelease = VendorRelease
        self.Index = Index
        self.properties = {}
    
    def _getPropertiesFromServer(self,crsr): 
        crsr.execute("SELECT VFROM,VTO,MEASURE from dwhrep.MeasurementVector WHERE TYPEID=? AND DATANAME=? AND VINDEX=? AND VENDORRELEASE=?",(self.typeid, self.parentAttName,self.Index,self.VendorRelease,))
            
        resultset = crsr.fetchall()
        desc = crsr.description
        for row in resultset: 
            i = 0
            for x in desc:            
                self.properties[x[0]] = TPAPI.checkNull(str(row[i]).strip())
                i+=1
    
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
                
            
            for row in tpidict['MeasurementVector']['VINDEX']:
                if self.name == tpidict['MeasurementVector']['DATANAME'][row] and tpidict['MeasurementVector']['TYPEID'][row] == self.typeid:
                    if self.Index == tpidict['MeasurementVector']['VINDEX'][row] and tpidict['MeasurementVector']['VENDORRELEASE'][row] == self.VendorRelease:
                        self.properties['VFROM'] = TPAPI.checkNull(tpidict['MeasurementVector']['VFROM'][row])
                        self.properties['VTO'] = TPAPI.checkNull(tpidict['MeasurementVector']['VTO'][row])
                        self.properties['MEASURE'] = TPAPI.checkNull(tpidict['MeasurementVector']['MEASURE'][row])
            
    
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
        
        If a xls file is passed it is converted to a xlsDict object before processing.

        Exceptions: 
                   Raised if xlsDict and filename are both None (ie nothing to process)'''
        self.logger.debug(self.Index + "._getPropertiesFromXls()")
        
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
            for Name, Value in xlsDict.iteritems():
                self.properties[Name] = Value
    
    def _getPropertiesFromXML(self,xmlElement):
        '''Populates the objects content from an xmlElement.
        The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
        
        self.logger.debug(self.name + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
    
    def _toXLS(self, workbook, tableName, AttName):
        ''' Converts the object to an excel document
        
        Parent toXLS() method is responsible for triggering child object toXLS() methods
        '''
        
        from jxl import Workbook
        from jxl.write import WritableWorkbook 
        from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
        from jxl.write import WritableCell
        from jxl.write import Label 
        
        sheet = workbook.getSheet('Vectors')
        Vectordict = TPAPI.XlsDict().VectorsDict
        rowNumber = sheet.getRows()
        label = Label(sheet.findCell('Fact Table Name').getColumn(), rowNumber, tableName)
        sheet.addCell(label)
        label = Label(sheet.findCell('Counter Name').getColumn(), rowNumber, AttName)
        sheet.addCell(label)
        label = Label(sheet.findCell('Vendor Release').getColumn(), rowNumber, self.VendorRelease)
        sheet.addCell(label)
        label = Label(sheet.findCell('Index').getColumn(), rowNumber, self.Index)
        sheet.addCell(label)
            
        for FDColumn, Parameter in Vectordict.iteritems():
            if Parameter in self.properties.keys():
                value = self.properties[Parameter]
                label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                sheet.addCell(label)
         
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VINDEX'] = self.Index
        RepDbDict['TYPEID'] = self.typeid
        RepDbDict['DATANAME'] = self.parentAttName
        RepDbDict['VENDORRELEASE'] = self.VendorRelease
        RepDbDict['QUANTITY'] = 0
        
        TPRepDbInterface.populateMeasurementVector(RepDbDict)
    
    def _toXML(self,indent=0):
        '''Write the object to an xml formatted string
        Offset value is used for string indentation. Default to 0
        Parent toXML() method is responsible for triggering child object toXML() methods.
        Return Value: xmlString 
        '''
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset

        outputXML  =os+'<Vector VendorRelease="'+self.VendorRelease+ '" index ="'+self.Index +'">' 
        for attr in self.properties:
            outputXML += os2+'<'+str(attr)+'>'+TPAPI.escape(self.properties[attr])+'</'+str(attr)+'>'

        outputXML +=os+'</Vector>'
        return outputXML
    
    def difference(self,VecObject,deltaObj=None):
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
            deltaObj = TPAPI.Delta(self.Index,VecObject.Index)
        
        ############################################## Properties Difference #####################################################
        deltaObj.location.append('Properties') 

        Delta = TPAPI.DictDiffer(self.properties,VecObject.properties)
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.properties[item], VecObject.properties[item])
    
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', VecObject.properties[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.properties[item], '')
        
        deltaObj.location.pop()