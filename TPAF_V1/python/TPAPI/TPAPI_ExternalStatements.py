
from __future__ import with_statement
import TPAPI
import logging
from copy import deepcopy


class ExternalStatement(object):
    
    '''Class to represent ExternalStatement object. A child object of TechPack Version'''
        
    def __init__(self,versionID, name):
        '''Class is instantiated with the versionID and name of the External Statement
            
            Instance Variables:
            
            self.versionID:
                Description: VersionID of the TechPackVersion
                Type:String
                
           self.name:
               Description: name of the external statement
               Type: String
               
            self.properties:
                Description: Properties of the external statement
                Type: Dictionary
                Keys: 
                    EXECUTIONORDER
                    DBCONNECTION
                    STATEMENT
        '''
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.BusyHour')
        self.versionID = versionID
        self.name = name
        self.properties = {}

    def _getPropertiesFromServer(self,crsr, NoOfBaseES=None):
        '''Get all the properties associated with the External statement object'''
        
        if NoOfBaseES == None:
            NoOfBaseES = 0
        
        self._getExternalStatements(crsr, NoOfBaseES)

    def _getExternalStatements(self,crsr, NoOfBaseES):
        '''Gets external statement information from the dwhrep
        
        SQL Executed:
                    SELECT EXECUTIONORDER,DBCONNECTION,STATEMENT,\BASEDEF FROM dwhrep.ExternalStatement WHERE VERSIONID =? AND STATEMENTNAME =?
        '''
        self.logger.debug(self.versionID + "._getExternalStatements()")
        crsr.execute("SELECT EXECUTIONORDER,DBCONNECTION,STATEMENT,\
        BASEDEF FROM dwhrep.ExternalStatement WHERE VERSIONID =? AND STATEMENTNAME =?", (self.versionID, self.name,))
        resultset = crsr.fetchall()
        for row in resultset:
            if str(row[3]) == '0':
                self.properties['DBCONNECTION'] = str(row[1])
                self.properties['STATEMENT'] = str(row[2]).strip()
                ExecOrder = TPAPI.strFloatToInt(str(row[0]))
                self.properties['EXECUTIONORDER'] = str(int(ExecOrder) - NoOfBaseES)
                
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
            
            for Name, Value in xlsDict['ExternalStatements'][self.name].iteritems():
                self.properties[Name] = Value
    
    def _toXLS(self, workbook, filename):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label 
            
            sheet = workbook.getSheet('External Statement')
            dict = TPAPI.XlsDict().ESDict
            label = Label(sheet.findCell('View Name').getColumn(), int(self.properties['EXECUTIONORDER']), self.name)
            sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    
                    label = Label(sheet.findCell(FDColumn).getColumn(), int(self.properties['EXECUTIONORDER']), value)
                    if Parameter == 'STATEMENT':
                        if len(value) > 500:
                            ESfilename = filename.replace('.xls', '.txt')
                            label = Label(sheet.findCell(FDColumn).getColumn(), int(self.properties['EXECUTIONORDER']), ESfilename.rsplit('\\',1)[1])
                            ESFile = open(ESfilename, 'a')
                            ESFile.write('@@'+self.name+'=='+self.properties['STATEMENT'])
                            ESFile.close()
                            
                    sheet.addCell(label)

    
    def _toXML(self,indent=0):
        '''Write the object to an xml formatted string
        
        Offset value is used for string indentation. Default to 0
        Parent toXML() method is responsible for triggering child object toXML() methods.

        Return Value: xmlString 
        '''
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os+'<ExternalStatement name="' + self.name + '">'
        for prop in self.properties:
            outputXML += os2+'<'+prop+'>'+ TPAPI.escape(self.properties[prop]) +'</'+prop+'>'
        outputXML += os+'</ExternalStatement>'   
        return outputXML 

    def _getPropertiesFromXML(self,xmlElement):
        '''Populates the objects content from an xmlElement
        
        The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
        self.logger.info(self.versionID + " Inside _getPropertiesFromXML function") 
        for elem in xmlElement:
            self.properties[elem.tag] = TPAPI.safeNull(elem.text)     
    
    def _getPropertiesFromTPI(self,tpiDict=None,filename=None):
            '''Populate the objects contents from a tpiDict object or tpi file.
            
            If a tpi file is passed it is converted to a tpiDict object before processing.

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
            for row in tpiDict['Externalstatement']['STATEMENTNAME']:
                if tpiDict['Externalstatement']['STATEMENTNAME'][row] == self.name:
                    self.properties['EXECUTIONORDER'] = tpiDict['Externalstatement']['EXECUTIONORDER'][row]
                    self.properties['DBCONNECTION'] = tpiDict['Externalstatement']['DBCONNECTION'][row]
                    self.properties['STATEMENT'] = tpiDict['Externalstatement']['STATEMENT'][row]
                    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['STATEMENTNAME'] = self.name
        RepDbDict['BASEDEF'] = 0
        TPRepDbInterface.populateExternalStatement(RepDbDict)
       
    def difference(self,extStateObject,deltaObj=None):
        '''Calculates the difference between two external statement objects
            
            Method takes extStateObject,deltaObj and deltaTPV as inputs.
            extStateObject: The External Statement to be compared against
            DeltaObj: The single object that gets passed through the entire diff recording the changes.
            DeltaTPV: A TechPackVersion Object that gets passed through the entire diff recording only new content.
            
            The Difference method will trigger the difference method of its child objects, passing
            in the object to compare, deltaObj and deltaTPV. After calculating the diff the child object passes these objects
            back in conjunction with a flag to say whether a (only new or changed content.. not deleted) was found or not. This flag is used to decide
            whether a child object should be added to the parent object in the DeltaTPV.
            
            Note: External statement does not have any child objects
            
            Returns:
                    diffFlag (Boolean indicating where a change was found or not)
                    deltaObj
                    deltaTPV 
            
        '''
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.name,extStateObject.name)
        
        deltaObj.location.append('Properties') 

        Delta = TPAPI.DictDiffer(self.properties,extStateObject.properties)
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.properties[item], extStateObject.properties[item])
    
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', extStateObject.properties[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.properties[item], '')
        
        deltaObj.location.pop()

        return deltaObj
    