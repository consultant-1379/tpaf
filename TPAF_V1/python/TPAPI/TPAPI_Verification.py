from __future__ import with_statement
import TPAPI
import re
import logging
import sys
from copy import deepcopy


class VerificationObject(object):

    def __init__(self,versionID,measLevel,objectClass,objectName):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.VerificationObject') 
        self.versionID = versionID
        self.measLevel = measLevel
        self.objectClass= objectClass
        self.objectName= objectName
        self.properties = {}
        self.logger.debug("TPAPI.VerificationObject" + ".__init__()")
    
    def _toXML(self,offset=0):
        self.logger.debug("TPAPI.VerificationObject"+"_toXML()")
        offset += 4
        os = "\n" + " "*offset
        os4 = os+ " "*12
        os5 = os4+ " "*4
        outputXML = os4 + '<VerificationObject level="'+self.measLevel+ '" class="'+str(self.objectClass) + '" name="'+str(self.objectName)  +'">'
        for prop in self.properties:
            outputXML += os5+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'        
        outputXML += os4 + '</VerificationObject>'
        return outputXML
    
    def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            sheet = workbook.getSheet('Report objects')
            rowNumber = sheet.getRows()
            
            label = Label(sheet.findCell('Fact Table').getColumn(), rowNumber,  self.properties['MEASTYPE'])
            sheet.addCell(label)
            label = Label(sheet.findCell('Level').getColumn(), rowNumber,  self.measLevel)
            sheet.addCell(label)
            label = Label(sheet.findCell('Object Class').getColumn(), rowNumber, self.objectClass)
            sheet.addCell(label)
            label = Label(sheet.findCell('Object Name').getColumn(), rowNumber, self.objectName)
            sheet.addCell(label)
    
    def _difference(self):
        self.logger.debug("TPAPI.VerificationObject" + "._difference")
    
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.VerificationObject"+ "._getPropertiesFromServer()")

        crsr.execute("SELECT MEASTYPE FROM dwhrep.VerificationObject where VERSIONID =? and measLevel=? and objectClass=? and objectName=?",(self.versionID,self.measLevel,self.objectClass,self.objectName))
        row = crsr.fetchone()
        desc = crsr.description
        if row is not None:
            i = 0
            for x in desc:
                self.properties[x[0]] = row[i]
                i+=1  
    
    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.VerificationObject"+ "._getPropertiesFromTpi()")
        for row in tpiDict['Verificationobject']['OBJECTNAME']:
            measLevel  = tpiDict['Verificationobject']['MEASLEVEL'][row]
            objectClass = tpiDict['Verificationobject']['OBJECTCLASS'][row]
            objectName = tpiDict['Verificationobject']['OBJECTNAME'][row]
            if self.measLevel == measLevel and self.objectClass == objectClass and self.objectName == objectName:
                self.properties['MEASTYPE'] = tpiDict['Verificationobject']['MEASTYPE'][row]
                


    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.VerificationObject"+ "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
                
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
        
        self.logger.debug("TPAPI.VerificationObject" + "._getPropertiesFromXls()")
            
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
             
            self.measLevel = xlsDict['MEASLEVEL']
            self.objectClass = xlsDict['OBJECTCLASS']
            self.objectName = xlsDict['OBJECTNAME']
            self.properties['MEASTYPE'] = xlsDict['MEASTYPE']
            
    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['MEASLEVEL'] = self.measLevel
        RepDbDict['OBJECTCLASS'] = self.objectClass
        RepDbDict['OBJECTNAME'] = self.objectName
        TPRepDbInterface.populateVerificationobject(RepDbDict)

class VerificationCondition(object):

    def __init__(self,versionID,conditionClass,verCondition,verLevel):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.VerificationCondition') 
        self.versionID = versionID
        self.conditionClass = conditionClass
        self.verCondition = verCondition
        self.verLevel = verLevel
        self.properties = {}
        self.logger.debug("TPAPI.VerificationCondition" + ".__init__()")
        
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.VerificationCondition"+ "._getPropertiesFromServer()")        

        crsr.execute("SELECT FACTTABLE,CONDITIONCLASS,PROMPTNAME1,PROMPTVALUE1,PROMPTNAME2,PROMPTVALUE2,OBJECTCONDITION,PROMPTNAME3,PROMPTVALUE3 FROM dwhrep.VerificationCondition where VERSIONID =? and CONDITIONCLASS=? and VERCONDITION=? and VERLEVEL=?",(self.versionID,self.conditionClass,self.verCondition,self.verLevel))
        row = crsr.fetchone()
        desc = crsr.description
        if row is not None:
            i = 0
            for x in desc:
                self.properties[x[0]] = row[i]
                i+=1        
            
    def _toXML(self,offset=0):
        self.logger.debug("TPAPI.VerificationCondition"+"_toXML()")
        offset += 4
        os = "\n" + " "*offset
        os4 = os+ " "*12
        os5 = os4+ " "*4
        outputXML = os4 + '<VerificationCondition class="'+self.conditionClass+ '" condition="'+str(self.verCondition) + '" level ="'+str(self.verLevel)  +'">'
        for prop in self.properties:
            outputXML += os5+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'        
        outputXML += os4 + '</VerificationCondition>'
        return outputXML
    
    def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            sheet = workbook.getSheet('Report conditions')
            rowNumber = sheet.getRows()
            dict = TPAPI.XlsDict().verConDict
            
            label = Label(sheet.findCell('Condition Class').getColumn(), rowNumber,  self.conditionClass)
            sheet.addCell(label)
            label = Label(sheet.findCell('Condition').getColumn(), rowNumber,  self.verCondition)
            sheet.addCell(label)
            label = Label(sheet.findCell('Level').getColumn(), rowNumber, self.verLevel)
            sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                    sheet.addCell(label)            
    
    def _difference(self):
        self.logger.debug("TPAPI.VerificationCondition" + "._difference")


    def _getPropertiesFromTPI(self,tpiDictionary):
        self.logger.debug("TPAPI.VerificationCondition"+ "._getPropertiesFromTpi()")
        for row in tpiDictionary['Verificationcondition']['VERCONDITION']:
            conClass = tpiDictionary['Verificationcondition']['CONDITIONCLASS'][row]
            verCon = tpiDictionary['Verificationcondition']['VERCONDITION'][row]
            verLevel = tpiDictionary['Verificationcondition']['VERLEVEL'][row]
            if self.conditionClass == conClass and self.verCondition == verCon and self.verLevel == verLevel:
                self.properties['FACTTABLE'] = tpiDictionary['Verificationcondition']['FACTTABLE'][row]
                self.properties['CONDITIONCLASS'] = tpiDictionary['Verificationcondition']['CONDITIONCLASS'][row]
                self.properties['PROMPTNAME1'] = tpiDictionary['Verificationcondition']['PROMPTNAME1'][row]
                self.properties['PROMPTVALUE1'] = tpiDictionary['Verificationcondition']['PROMPTVALUE1'][row]
                self.properties['PROMPTNAME2'] = tpiDictionary['Verificationcondition']['PROMPTNAME2'][row]
                self.properties['PROMPTVALUE2'] = tpiDictionary['Verificationcondition']['PROMPTVALUE2'][row]
                self.properties['OBJECTCONDITION'] = tpiDictionary['Verificationcondition']['OBJECTCONDITION'][row]
                self.properties['PROMPTNAME3'] = tpiDictionary['Verificationcondition']['PROMPTNAME3'][row]
                self.properties['PROMPTVALUE3'] = tpiDictionary['Verificationcondition']['PROMPTVALUE3'][row]

    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.VerificationCondition"+ "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
                
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
        
        self.logger.debug("TPAPI.VerificationCondition" + "._getPropertiesFromXls()")
            
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
             
            self.conditionClass = xlsDict['CONDITIONCLASS']
            self.verCondition = xlsDict['VERCONDITION']
            self.verLevel = xlsDict['VERLEVEL']
            self.properties['FACTTABLE'] = xlsDict['FACTTABLE']
            self.properties['CONDITIONCLASS'] = xlsDict['CONDITIONCLASS']
            self.properties['PROMPTNAME1'] = xlsDict['PROMPTNAME1']
            self.properties['PROMPTVALUE1'] = xlsDict['PROMPTVALUE1']
            self.properties['PROMPTNAME2'] = xlsDict['PROMPTNAME2']
            self.properties['PROMPTVALUE2'] = xlsDict['PROMPTVALUE2']
            self.properties['OBJECTCONDITION'] = xlsDict['OBJECTCONDITION']
            self.properties['PROMPTNAME3'] = xlsDict['PROMPTNAME3']
            self.properties['PROMPTVALUE3'] = xlsDict['PROMPTVALUE3']
    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['CONDITIONCLASS'] = self.conditionClass
        RepDbDict['VERCONDITION'] = self.verCondition
        RepDbDict['VERLEVEL'] = self.verLevel
        TPRepDbInterface.populateVerificationcondition(RepDbDict)


