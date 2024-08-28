from __future__ import with_statement
from copy import deepcopy
from pprint import pprint
import TPAPI
import logging
import re
import string
import sys

class Universe(object):
    def __init__(self,versionID,universeName):
 
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.Universe') 
        self.versionID = versionID
        self.universeName = universeName
        self.universeClassObjects = {}
        self.universeTableObjects = {}
        self.universeJoinObjects = {} 
        self.universeExtensionObjects = {}
        self.logger.debug("TPAPI.Universe" + ".__init__()")

    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.Universe" + "._getPropertiesFromServer()")

        crsr.execute("SELECT UNIVERSEEXTENSION,UNIVERSEEXTENSIONNAME FROM dwhrep.UniverseName WHERE VERSIONID =? AND UNIVERSENAME =?", (self.versionID, self.universeName))
        rows = crsr.fetchall()
        for row in rows:
            if row[0] != '':
                unvext=TPAPI.UniverseExtension(self.versionID,self.universeName,row[0],row[1])
                unvext._getPropertiesFromServer(crsr)
                self.universeExtensionObjects[row[0]]=unvext 
        
        self._getUniverseJoins(crsr,'ALL')
        self._getUniverseTables(crsr,'ALL')
        self._getUniverseClasses(crsr,'ALL')

    def _getUniverseTables(self,crsr,unvextension):
        self.logger.debug("TPAPI.Universe" + "._getUniverseTables()")

        if unvextension != None:
            crsr.execute("SELECT TABLENAME FROM dwhrep.UniverseTable where versionid =? and UNIVERSEEXTENSION like ?",(self.versionID,'ALL',))
            resultset = crsr.fetchall()
            for row in resultset:
                unvTab = TPAPI.UniverseTable(self.versionID,'ALL',row[0])
                unvTab._getPropertiesFromServer(crsr)
                self.universeTableObjects[row[0]] = unvTab

    def _getUniverseClasses(self,crsr,unvextension):
        self.logger.debug("TPAPI.Universe" + "._getUniverseClasses()")
        crsr.execute("SELECT CLASSNAME FROM dwhrep.UniverseClass where versionid =? and UNIVERSEEXTENSION like ?",(self.versionID,'ALL',))
        resultset = crsr.fetchall()
        for row in resultset:
            unvClass = TPAPI.UniverseClass(self.versionID,unvextension,row[0])
            unvClass._getPropertiesFromServer(crsr)
            self.universeClassObjects[row[0]] = unvClass

    def _getUniverseJoins(self,crsr,unvextension):
        self.logger.debug("TPAPI.Universe" + "._getUniverseJoins()")
        crsr.execute("SELECT UNIVERSEEXTENSION,SOURCECOLUMN,SOURCETABLE,TARGETCOLUMN,TARGETTABLE,TMPCOUNTER FROM dwhrep.UniverseJoin where versionid =?",(self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            if row[0] == None or row[0] == '' or row[0].upper() == 'ALL':
                unvjoin = TPAPI.UniverseJoin(self.versionID,unvextension,row[1],row[2],row[3],row[4],row[5],)
                #make compositekey
                self.universeJoinObjects[unvjoin.getJoinId()] = unvjoin
                self.universeJoinObjects[unvjoin.getJoinId()]._getPropertiesFromServer(crsr)
    
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
            self.logger.debug(self.universeName + "._getPropertiesFromXls()")
            
            if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                if 'Tables' in xlsDict['Universe'][self.universeName]:
                    for Name,  Values in xlsDict['Universe'][self.universeName]['Tables'].iteritems():
                        if Values['UNIVERSEEXTENSION'].upper() == 'ALL' or Values['UNIVERSEEXTENSION'].upper() == '':
                            unvtab=TPAPI.UniverseTable(self.versionID,'ALL',Name)
                            unvtab._getPropertiesFromXls(Values)
                            self.universeTableObjects[Name]=unvtab
                
                if 'Class' in xlsDict['Universe'][self.universeName]:
                    for Name,  Values in xlsDict['Universe'][self.universeName]['Class'].iteritems():  
                        if Values['UNIVERSEEXTENSION'].upper() == 'ALL' or Values['UNIVERSEEXTENSION'].upper() == '':
                            unvclass=TPAPI.UniverseClass(self.versionID,'ALL',Name)                               
                            unvclass._getPropertiesFromXls(xlsDict['Universe'][self.universeName])                           
                            self.universeClassObjects[unvclass.universeClassName]=unvclass
                
                if 'Joins' in xlsDict['Universe'][self.universeName]:  
                    for Name,  Values in xlsDict['Universe'][self.universeName]['Joins'].iteritems(): 
                        if Values['UNIVERSEEXTENSION'].upper() == 'ALL' or Values['UNIVERSEEXTENSION'].upper() == '':
                            sourcecolumn = Values['SOURCECOLUMN']
                            sourcetable = Values['SOURCETABLE']
                            targetcolumn = Values['TARGETCOLUMN']
                            targettable = Values['TARGETTABLE']
                            unvJoin=TPAPI.UniverseJoin(self.versionID,'ALL',sourcecolumn,sourcetable,targetcolumn,targettable,Name)
                            unvJoin._getPropertiesFromXls(Values)
                            self.universeJoinObjects[unvJoin.getJoinId()]=unvJoin
                
                if 'Extensions' in xlsDict['Universe'][self.universeName]:        
                    for Name,  Values in xlsDict['Universe'][self.universeName]['Extensions'].iteritems():
                        unvextname = Values['UNIVERSEEXTENSIONNAME']
                        unvext=TPAPI.UniverseExtension(self.versionID,self.universeName,Name,unvextname) 
                        unvext._getPropertiesFromXls(xlsDict)
                        self.universeExtensionObjects[Name]=unvext
                                               
                
    def _getPropertiesFromXML(self,xmlElement):
        '''Populates the objects content from an xmlElement.
            
            The method is also responsible for triggering its child objects getPropertiesFromXML() method'''
        self.logger.debug("TPAPI.Universe" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            x = 0
            if elem.tag == 'UniverseExtensions':
                for elem1 in elem:
                    if elem1.tag == 'UniverseExtension':
                        unvExtension= TPAPI.UniverseExtension(self.versionID,self.universeName,elem1.attrib['name'],elem1.attrib['ExtensionName'])
                        x=unvExtension._getPropertiesFromXML(elem1,x)
                        self.universeExtensionObjects[elem1.attrib['name']] = unvExtension
                    
            if elem.tag == 'UniverseTables':
                for elem1 in elem:
                    if elem1.tag == 'UniverseTable':
                        unvTable = TPAPI.UniverseTable(self.versionID,elem1.attrib['extension'],elem1.attrib['name'])
                        unvTable._getPropertiesFromXML(elem1)
                        self.universeTableObjects[elem1.attrib['name']] = unvTable
            if elem.tag == 'UniverseClasses':
                for elem1 in elem:
                    if elem1.tag == 'UniverseClass':
                        unvClass = TPAPI.UniverseClass(self.versionID,elem1.attrib['extension'],elem1.attrib['name'])
                        unvClass._getPropertiesFromXML(elem1)
                        self.universeClassObjects[elem1.attrib['name']] =  unvClass
            if elem.tag == 'UniverseJoins':
                for elem1 in elem:
                    if elem1.tag == 'UniverseJoin':
                        unvJoin = TPAPI.UniverseJoin(self.versionID,'ALL',elem1.attrib['sourceColumn'],elem1.attrib['sourceTable'],elem1.attrib['targetColumn'],elem1.attrib['targetTable'],x)                        
                        unvJoin._getPropertiesFromXML(elem1)
                        self.universeJoinObjects[unvJoin.getJoinId()] = unvJoin
                        x += 1
                    
    def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            for table in self.universeTableObjects.itervalues():
                table._toXLS(workbook)
                
            for uniclass in self.universeClassObjects.itervalues():
                uniclass._toXLS(workbook)
            
            for join in self.universeJoinObjects.itervalues():
                join._toXLS(workbook)
            
            
            if len(self.universeExtensionObjects) != 0:   
                for ext in self.universeExtensionObjects.itervalues():
                    ext._toXLS(workbook)
            else:
                from jxl import Workbook
                from jxl.write import WritableWorkbook 
                from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
                from jxl.write import WritableCell
                from jxl.write import Label
                
                sheet = workbook.getSheet('Universe Extension')
                rowNumber = sheet.getRows()
                
                label = Label(sheet.findCell('Universe Name').getColumn(), rowNumber, self.universeName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, 'ALL')
                sheet.addCell(label)
            
            
    
    
    def _toXML(self,indent=0):
            self.logger.debug("TPAPI.Universe" + "._toXML()")
            
            offset = '    '
            os = "\n" + offset*indent

            outputXML = os +'<UniverseExtensions>'
            for unvExt in self.universeExtensionObjects:
                outputXML += self.universeExtensionObjects[unvExt]._toXML(indent+1)
            outputXML += os +'</UniverseExtensions>'
            outputXML += os +'<UniverseTables>'
            for unvTable in self.universeTableObjects:
                outputXML += str(self.universeTableObjects[unvTable]._toXML(indent+1))
            outputXML += os +'</UniverseTables>'
            outputXML += os +'<UniverseClasses>'           
            for unvClass in self.universeClassObjects:
                outputXML += self.universeClassObjects[unvClass]._toXML(indent+1)
            outputXML += os +'</UniverseClasses>' 
            outputXML += os +'<UniverseJoins>'
            for unvJoin in self.universeJoinObjects:
                outputXML += self.universeJoinObjects[unvJoin]._toXML(indent+1)
            outputXML += os +'</UniverseJoins>'
            return outputXML
        
    def _getPropertiesFromTPI(self,tpidict=None,filename=None):
        '''Populate the objects contents from a tpiDict object or tpi file.
        
        If a tpi file is passed it is converted to a tpiDict object before processing.
    
        Exceptions: 
                   Raised if tpiDict and filename are both None (ie nothing to process)'''
        self.logger.debug(self.universeName + "._getPropertiesFromTPI()")
        if tpidict==None and filename==None:
            strg = 'getPropertiesFromTPI() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                tpidict = TPAPI.TpiDict(filename).returnTPIDict()
            x=0
            for row in tpidict['Universename']['UNIVERSEEXTENSION']:
                ext = tpidict['Universename']['UNIVERSEEXTENSION'][row]
                if ext != '' :
                    extName = tpidict['Universename']['UNIVERSEEXTENSIONNAME'][row]
                    unv = TPAPI.UniverseExtension(self.versionID,self.universeName,ext,extName)
                    x=unv._getPropertiesFromTPI(tpidict,x)
                    self.universeExtensionObjects[ext] = unv
            
            if 'Universetable' in tpidict:        
                for row in tpidict['Universetable']['UNIVERSEEXTENSION']:
                    ext = tpidict['Universetable']['UNIVERSEEXTENSION'][row]
                    if ext.upper() == 'ALL' or ext == '':
                        unvTab = TPAPI.UniverseTable(self.versionID,'ALL',tpidict['Universetable']['TABLENAME'][row])
                        unvTab._getPropertiesFromTPI(tpidict)
                        self.universeTableObjects[tpidict['Universetable']['TABLENAME'][row]] = unvTab
            
            if 'Universeclass' in tpidict:    
                for row in tpidict['Universeclass']['CLASSNAME']:
                    ext = tpidict['Universeclass']['UNIVERSEEXTENSION'][row]
                    if ext.upper() == 'ALL' or ext == '':
                        unvClass = TPAPI.UniverseClass(self.versionID,'ALL',tpidict['Universeclass']['CLASSNAME'][row])
                        unvClass._getPropertiesFromTPI(tpidict)
                        self.universeClassObjects[tpidict['Universeclass']['CLASSNAME'][row]] = unvClass
            
            if 'Universejoin' in tpidict: 
                for row in tpidict['Universejoin']['UNIVERSEEXTENSION']:
                    ext = tpidict['Universejoin']['UNIVERSEEXTENSION'][row]
                    if ext.upper() == 'ALL' or ext == '':
                        #for row in tpidict['Universejoin']['CONTEXT']:
                            x +=1 
                            srcc = tpidict['Universejoin']['SOURCECOLUMN'][row]
                            srct = tpidict['Universejoin']['SOURCETABLE'][row]
                            tgtc = tpidict['Universejoin']['TARGETCOLUMN'][row]
                            tgtt = tpidict['Universejoin']['TARGETTABLE'][row]
                            unvJoin = TPAPI.UniverseJoin(self.versionID,'ALL',srcc,srct,tgtc,tgtt,x)
                            unvJoin._getPropertiesFromTPI(tpidict)
                            self.universeJoinObjects[unvJoin.getJoinId()] = unvJoin


    def _populateRepDbModel(self, TPRepDbInterface):
        if len(self.universeExtensionObjects) == 0:
            RepDbDict = {}
            RepDbDict['UNIVERSEEXTENSION']= ''
            RepDbDict['VERSIONID']=self.versionID
            RepDbDict['UNIVERSENAME']=self.universeName
            RepDbDict['UNIVERSEEXTENSIONNAME']=''
            TPRepDbInterface.populateUniversename(RepDbDict)  
            
        for unvext in self.universeExtensionObjects:
            self.universeExtensionObjects[unvext]._populateRepDbModel(TPRepDbInterface)
        
        for universeClass in self.universeClassObjects:
            self.universeClassObjects[universeClass]._populateRepDbModel(TPRepDbInterface)
        
        tableorderno = 0   
        for universeTable in self.universeTableObjects:
            self.universeTableObjects[universeTable]._populateRepDbModel(TPRepDbInterface,tableorderno)
            tableorderno = tableorderno + 1
        
        for universeJoin in self.universeJoinObjects:
            self.universeJoinObjects[universeJoin]._populateRepDbModel(TPRepDbInterface)
        

    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.name,UniObj.universeName)
            
        ################################################################
        # Universe Extension Diff
        Delta = TPAPI.DictDiffer(self.universeExtensionObjects,UniObj.universeExtensionObjects)
        deltaObj.location.append('UniverseExtension')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeExtensionObjects[item].universeExtension, '', UniObj.universeExtensionObjects[item].universeExtensionName)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeExtensionObjects[item].universeExtension, self.universeExtensionObjects[item].universeExtensionName, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseExtension='+item)
            deltaObj = self.universeExtensionObjects[item].difference(UniObj.universeExtensionObjects[item],deltaObj)
            deltaObj.location.pop() 
            
        ################################################################
        # Universe Class Diff
        Delta = TPAPI.DictDiffer(self.universeClassObjects,UniObj.universeClassObjects)
        deltaObj.location.append('UniverseClass')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeClassObjects[item].universeClassName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeClassObjects[item].universeClassName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseClass='+item)
            deltaObj = self.universeClassObjects[item].difference(UniObj.universeClassObjects[item],deltaObj)
            deltaObj.location.pop() 
        
        ################################################################
        # Universe Table Diff
        Delta = TPAPI.DictDiffer(self.universeTableObjects,UniObj.universeTableObjects)
        deltaObj.location.append('UniverseTable')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeTableObjects[item].tableName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeTableObjects[item].tableName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseTable='+item)
            deltaObj = self.universeTableObjects[item].difference(UniObj.universeTableObjects[item],deltaObj)
            deltaObj.location.pop()  
        
        
        ################################################################
        # Universe Joins Diff
        Delta = TPAPI.DictDiffer(self.universeJoinObjects,UniObj.universeJoinObjects)
        deltaObj.location.append('UniverseJoin')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeJoinObjects[item].joinID, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeJoinObjects[item].joinID, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseJoin='+item)
            deltaObj = self.universeJoinObjects[item].difference(UniObj.universeJoinObjects[item],deltaObj)
            deltaObj.location.pop()   
        
        return deltaObj
        
class UniverseExtension(object):
    def __init__(self,versionID,universeName,universeExtension=None,universeExtensionName=None):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseExtension')
        self.logger.debug("TPAPI.UniverseExtension" + ".__init__()")
        self.versionID = versionID
        self.universeName = universeName
        self.universeExtension = universeExtension
        self.universeExtensionName = universeExtensionName
        self.universeClassObjects = {}
        self.universeTableObjects = {}
        self.universeJoinObjects = {} 
        self.properties = {}
        
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
        self.logger.debug(self.universeName + "._getPropertiesFromXls()")
            
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict() 
                
                
            for Name,  Values in xlsDict['Universe'][self.universeName]['Tables'].iteritems():
                if self.universeExtension in Values['UNIVERSEEXTENSION']:
                    unvtab=TPAPI.UniverseTable(self.versionID,Values['UNIVERSEEXTENSION'],Name)
                    unvtab._getPropertiesFromXls(Values)
                    self.universeTableObjects[Name]=unvtab
                
            for Name,  Values in xlsDict['Universe'][self.universeName]['Class'].iteritems():  
                if self.universeExtension in Values['UNIVERSEEXTENSION']:
                    unvclass=TPAPI.UniverseClass(self.versionID,Values['UNIVERSEEXTENSION'],Name)                               
                    unvclass._getPropertiesFromXls(xlsDict['Universe'][self.universeName])                           
                    self.universeClassObjects[unvclass.universeClassName]=unvclass
                
            for Name,  Values in xlsDict['Universe'][self.universeName]['Joins'].iteritems():        
                if self.universeExtension in Values['UNIVERSEEXTENSION']:
                    sourcecolumn = Values['SOURCECOLUMN']
                    sourcetable = Values['SOURCETABLE']
                    targetcolumn = Values['TARGETCOLUMN']
                    targettable = Values['TARGETTABLE']
                    unvJoin=TPAPI.UniverseJoin(self.versionID,Values['UNIVERSEEXTENSION'],sourcecolumn,sourcetable,targetcolumn,targettable,Name)
                    unvJoin._getPropertiesFromXls(Values)
                    self.universeJoinObjects[unvJoin.getJoinId()]=unvJoin
                        
    def _getPropertiesFromXML(self,xmlElement,x):
        
        self.logger.debug("TPAPI.UniverseExtension" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.tag == 'UniverseTables':
                for elem1 in elem:
                    if elem1.tag == 'UniverseTable':
                        unvTable = TPAPI.UniverseTable(self.versionID,elem1.attrib['extension'],elem1.attrib['name'])
                        unvTable._getPropertiesFromXML(elem1)
                        self.universeTableObjects[elem1.attrib['name']] = unvTable
            if elem.tag == 'UniverseClasses':
                for elem1 in elem:
                    if elem1.tag == 'UniverseClass':
                        unvClass = TPAPI.UniverseClass(self.versionID,elem1.attrib['extension'],elem1.attrib['name'])
                        unvClass._getPropertiesFromXML(elem1)
                        self.universeClassObjects[elem1.attrib['name']] =  unvClass
            if elem.tag == 'UniverseJoins':
                for elem1 in elem:
                    if elem1.tag == 'UniverseJoin':
                        unvJoin = TPAPI.UniverseJoin(self.versionID,self.universeExtension,elem1.attrib['sourceColumn'],elem1.attrib['sourceTable'],elem1.attrib['targetColumn'],elem1.attrib['targetTable'],x)
                        unvJoin._getPropertiesFromXML(elem1)
                        self.universeJoinObjects[unvJoin.getJoinId()] = unvJoin
                        x += 1
        return x
    
    def _toXLS(self, workbook):
            ''' Converts the object to an excel document
            
            Parent toXLS() method is responsible for triggering child object toXLS() methods
            '''
            
            from jxl import Workbook
            from jxl.write import WritableWorkbook 
            from jxl.write import WritableSheet        #These imported are not referenced directly but they are required. 
            from jxl.write import WritableCell
            from jxl.write import Label
            
            sheet = workbook.getSheet('Universe Extension')
            rowNumber = sheet.getRows()
            
            label = Label(sheet.findCell('Universe Name').getColumn(), rowNumber, self.universeName)
            sheet.addCell(label)
            label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
            sheet.addCell(label)
            label = Label(sheet.findCell('Universe Ext Name').getColumn(), rowNumber, self.universeExtensionName)
            sheet.addCell(label)
            
            for table in self.universeTableObjects.itervalues():
                table._toXLS(workbook)
            
            for uniClass in self.universeClassObjects.itervalues():
                uniClass._toXLS(workbook)
                
            for join in self.universeJoinObjects.itervalues():
                join._toXLS(workbook)
    
        
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseExtension" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os + '<UniverseExtension  name="'+str(self.universeExtension)+ '" ExtensionName= "' + self.universeExtensionName +'">'
        outputXML += os2 +'<UniverseTables>'
        for unvTable in self.universeTableObjects:
            outputXML += str(self.universeTableObjects[unvTable]._toXML(indent+2))
        outputXML += os2 +'</UniverseTables>'
        outputXML += os2 +'<UniverseClasses>'           
        for unvClass in self.universeClassObjects:
            outputXML += self.universeClassObjects[unvClass]._toXML(indent+2)
        outputXML += os2 +'</UniverseClasses>'
        outputXML += os2 +'<UniverseJoins>'
        for unvJoin in self.universeJoinObjects:
            outputXML += self.universeJoinObjects[unvJoin]._toXML(indent+2)
        outputXML += os2 +'</UniverseJoins>' 
        outputXML += os +'</UniverseExtension>'
        return outputXML
    
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.UniverseExtension" + "._getPropertiesFromServer()")
        self._getUniverseJoins(crsr)
        self._getUniverseTables(crsr)
        self._getUniverseClasses(crsr)
        
    def _getUniverseTables(self,crsr):
        self.logger.debug("TPAPI.Universe" + "._getUniverseTables()")
        
        if self.universeExtension != None:
            crsr.execute("SELECT TABLENAME,UNIVERSEEXTENSION FROM dwhrep.UniverseTable where versionid =?",(self.versionID,))
            resultset = crsr.fetchall()
            for row in resultset:
                if self.universeExtension in row[1]:
                    unvTab = TPAPI.UniverseTable(self.versionID,row[1],row[0])
                    unvTab._getPropertiesFromServer(crsr)
                    self.universeTableObjects[row[0]] = unvTab

    def _getUniverseClasses(self,crsr):
        self.logger.debug("TPAPI.Universe" + "._getUniverseClasses()")

        crsr.execute("SELECT CLASSNAME,UNIVERSEEXTENSION FROM dwhrep.UniverseClass where versionid =?",(self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            if self.universeExtension in row[1]:
                unvClass = TPAPI.UniverseClass(self.versionID,row[1],row[0])
                self.universeClassObjects[row[0]] = unvClass
                self.universeClassObjects[row[0]]._getPropertiesFromServer(crsr)

    def _getUniverseJoins(self,crsr):
        self.logger.debug("TPAPI.Universe" + "._getUniverseJoins()")

        crsr.execute("SELECT UNIVERSEEXTENSION,SOURCECOLUMN,SOURCETABLE,TARGETCOLUMN,TARGETTABLE,TMPCOUNTER FROM dwhrep.UniverseJoin where versionid =?",(self.versionID,))
        resultset = crsr.fetchall()
        for row in resultset:
            if self.universeExtension in row[0]:
                unvjoin = TPAPI.UniverseJoin(self.versionID,row[0],row[1],row[2],row[3],row[4],row[5],)
                #make compositekey
                self.universeJoinObjects[unvjoin.getJoinId()] = unvjoin
                self.universeJoinObjects[unvjoin.getJoinId()]._getPropertiesFromServer(crsr)
        
        

    def _getPropertiesFromTPI(self,tpidict,x):
        if 'Universetable' in tpidict:
            for row in tpidict['Universetable']['UNIVERSEEXTENSION']:
                extensionList = tpidict['Universetable']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension in extensionList:
                    unvTab = TPAPI.UniverseTable(self.versionID,tpidict['Universetable']['UNIVERSEEXTENSION'][row],tpidict['Universetable']['TABLENAME'][row])
                    unvTab._getPropertiesFromTPI(tpidict)
                    self.universeTableObjects[tpidict['Universetable']['TABLENAME'][row]] = unvTab
        
        if 'Universeclass' in tpidict:        
            for row in tpidict['Universeclass']['CLASSNAME']:
                extensionList = tpidict['Universeclass']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension in extensionList:
                    unvClass = TPAPI.UniverseClass(self.versionID,tpidict['Universeclass']['UNIVERSEEXTENSION'][row],tpidict['Universeclass']['CLASSNAME'][row])
                    unvClass._getPropertiesFromTPI(tpidict)
                    self.universeClassObjects[tpidict['Universeclass']['CLASSNAME'][row]] = unvClass
        
        if 'Universejoin' in tpidict:       
            for row in tpidict['Universejoin']['UNIVERSEEXTENSION']:
                extensionList = tpidict['Universejoin']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension in extensionList:
                
               # for row in tpidict['Universejoin']['CONTEXT']:
                    x +=1 
                    srcc = tpidict['Universejoin']['SOURCECOLUMN'][row]
                    srct = tpidict['Universejoin']['SOURCETABLE'][row]
                    tgtc = tpidict['Universejoin']['TARGETCOLUMN'][row]
                    tgtt = tpidict['Universejoin']['TARGETTABLE'][row]
                    unvJoin = TPAPI.UniverseJoin(self.versionID,tpidict['Universejoin']['UNIVERSEEXTENSION'][row],srcc,srct,tgtc,tgtt,x)
                    unvJoin._getPropertiesFromTPI(tpidict)
                    self.universeJoinObjects[unvJoin.getJoinId()] = unvJoin  
        return x         
        
        
    def _populateRepDbModel(self,TPRepDbInterface):
        RepDbDict = {}
        RepDbDict['UNIVERSEEXTENSION']=self.universeExtension
        RepDbDict['VERSIONID']=self.versionID
        RepDbDict['UNIVERSENAME']=self.universeName
        RepDbDict['UNIVERSEEXTENSIONNAME']=self.universeExtensionName
        TPRepDbInterface.populateUniversename(RepDbDict)  
        
        for universeClass in self.universeClassObjects:
            self.universeClassObjects[universeClass]._populateRepDbModel(TPRepDbInterface)
        
        tableorderno = 0   
        for universeTable in self.universeTableObjects:
            self.universeTableObjects[universeTable]._populateRepDbModel(TPRepDbInterface,tableorderno)
            tableorderno = tableorderno + 1
        
        for universeJoin in self.universeJoinObjects:
            self.universeJoinObjects[universeJoin]._populateRepDbModel(TPRepDbInterface)
        
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.universeExtensionName,UniObj.universeExtensionName)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
        
        ################################################################
        # Universe Class Diff
        Delta = TPAPI.DictDiffer(self.universeClassObjects,UniObj.universeClassObjects)
        deltaObj.location.append('UniverseClass')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeClassObjects[item].universeClassName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeClassObjects[item].universeClassName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseClass='+item)
            deltaObj = self.universeClassObjects[item].difference(UniObj.universeClassObjects[item],deltaObj)
            deltaObj.location.pop() 
        
        ################################################################
        # Universe Table Diff
        Delta = TPAPI.DictDiffer(self.universeTableObjects,UniObj.universeTableObjects)
        deltaObj.location.append('UniverseTable')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeTableObjects[item].tableName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeTableObjects[item].tableName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseTable='+item)
            deltaObj = self.universeTableObjects[item].difference(UniObj.universeTableObjects[item],deltaObj)
            deltaObj.location.pop()  
        
        
        ################################################################
        # Universe Joins Diff
        Delta = TPAPI.DictDiffer(self.universeJoinObjects,UniObj.universeJoinObjects)
        deltaObj.location.append('UniverseJoin')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeJoinObjects[item].joinID, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeJoinObjects[item].joinID, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseJoin='+item)
            deltaObj = self.universeJoinObjects[item].difference(UniObj.universeJoinObjects[item],deltaObj)
            deltaObj.location.pop()   
        
        return deltaObj
             
class UniverseTable(object):
    
    def __init__(self,versionID,universeExtension,tableName):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseTable')
        self.logger.debug("TPAPI.UniverseTable" + ".__init__()")
        self.versionID = versionID
        self.extensionList = [] #extensions ? NEEDED
        self.universeExtension = universeExtension
        self.tableName = tableName
        self.properties = {}
        
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseTable" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os + '<UniverseTable name="'+self.tableName  +'" extension="'+self.universeExtension+'">'
        for prop in self.properties:
            outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
        outputXML += os +'</UniverseTable>'
        
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
            
            sheet = workbook.getSheet('Universe Topology Tables')
            dict = TPAPI.XlsDict().UniTableDict
            rowNumber = sheet.getRows()
            
            addRow = True
            columnNumber = sheet.findCell('Topology Table Name').getColumn()
            TableNameColumn = sheet.getColumn(columnNumber)
            del TableNameColumn[0]
            for tableNameCell in TableNameColumn:
                if tableNameCell.getContents() == self.tableName:
                    addRow = False

            if addRow:
                label = Label(sheet.findCell('Topology Table Name').getColumn(), rowNumber, self.tableName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
                sheet.addCell(label)
                
                for FDColumn, Parameter in dict.iteritems():
                    if Parameter in self.properties.keys():
                        value = self.properties[Parameter]
                        label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                        sheet.addCell(label)
            
    
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.UniverseTable" + "._getPropertiesFromServer()")

        crsr.execute("SELECT OWNER,ALIAS,ORDERNRO FROM dwhrep.UniverseTable where versionid =? and TableName=?",(self.versionID,self.tableName,))
        resultset = crsr.fetchall()
        desc = crsr.description
        for row in resultset:
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] == 'ORDERNRO':
                    value = TPAPI.strFloatToInt(value)
                
                self.properties[x[0]] = value
                i+=1

    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.UniverseTable" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
                
    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.UniverseTable" + "._getPropertiesFromTPI")
        for row in tpiDict['Universetable']['TABLENAME']:
            if self.tableName == tpiDict['Universetable']['TABLENAME'][row]:
                #extensionList = tpiDict['Universetable']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension in tpiDict['Universetable']['UNIVERSEEXTENSION'][row] or self.universeExtension.upper() == 'ALL':
                    for col in tpiDict['Universetable']:
                        if col=='OWNER' or col=='ALIAS' or col=='ORDERNRO':
                            self.properties[col] = tpiDict['Universetable'][col][row]
                        
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
            '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
            self.logger.debug(self.tableName + "._getPropertiesFromXls()")
            
            if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
            else:
                if filename is not None:
                    self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                for Name, Value in xlsDict.iteritems(): 
                    if Name != 'UNIVERSEEXTENSION':                
                        self.properties[Name] = Value
                
    
    def _populateRepDbModel(self, TPRepDbInterface,OrderNo):
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID       
        RepDbDict['TABLENAME'] = self.tableName
        RepDbDict['OBJ_BH_REL'] = 0
        RepDbDict['ELEM_BH_REL'] = 0
        RepDbDict['INHERITANCE'] = 0
        RepDbDict['ORDERNRO'] = OrderNo
        RepDbDict['UNIVERSEEXTENSION'] = self.universeExtension
        
        TPRepDbInterface.populateUniversetable(RepDbDict)
    
    
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.tableName,UniObj.tableName)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
            
        return deltaObj
            
        
class UniverseClass(object):
            
    def __init__(self,versionID,universeExtension,universeClassName):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseClass') 
        self.versionID = versionID
        self.universeClassName = universeClassName
        self.universeExtension = universeExtension # needed?
        self.universeObjObjects = {}
        self.universeConditionObjects = {}
        self.properties = {}
        self.logger.debug("TPAPI.UniverseClass" + ".__init__()")
    
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseClass" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML =os+'<UniverseClass  name="'+self.universeClassName  + '" extension="'+self.universeExtension  +'">'
        for prop in self.properties:
            outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
        outputXML += os2 +'<UniverseObjects>'
        for unvObj in self.universeObjObjects:
            outputXML += self.universeObjObjects[unvObj]._toXML(indent+2)
        outputXML += os2 + '</UniverseObjects>'
        outputXML += os2 +'<UniverseConditions>'
        for unvCondition in self.universeConditionObjects:
            outputXML += self.universeConditionObjects[unvCondition]._toXML(indent+2)
        outputXML += os2 +'</UniverseConditions>'
        outputXML += os+'</UniverseClass>'
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
            
            sheet = workbook.getSheet('Universe Class')
            dict = TPAPI.XlsDict().UniClassDict
            rowNumber = sheet.getRows()
            
            addRow = True
            columnNumber = sheet.findCell('Topology & Key Class Name').getColumn()
            ClassNameColumn = sheet.getColumn(columnNumber)
            del ClassNameColumn[0]
            for classNameCell in ClassNameColumn:
                if classNameCell.getContents() == self.universeClassName:
                    addRow = False

            if addRow:
                label = Label(sheet.findCell('Topology & Key Class Name').getColumn(), rowNumber, self.universeClassName)
                sheet.addCell(label)
                label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
                sheet.addCell(label)
                
                for FDColumn, Parameter in dict.iteritems():
                    if Parameter in self.properties.keys():
                        value = self.properties[Parameter]
                        label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                        sheet.addCell(label)
                
                for object in self.universeObjObjects.itervalues():
                    object._toXLS(workbook)
                    
                for con in self.universeConditionObjects.itervalues():
                    con._toXLS(workbook)
    
            
    def _getPropertiesFromXML(self,xmlelement):
        self.logger.debug("TPAPI.UniverseClass" + "._getPropertiesFromXML()")
        for elem1 in xmlelement:
            if elem1.tag == 'UniverseObjects':
                for elem2 in elem1:
                    if elem2.tag == 'UniverseObject':
                        uo = TPAPI.UniverseObject(self.versionID,elem2.attrib['extension'],elem2.attrib['name'],elem2.attrib['class'])
                        uo._getPropertiesFromXML(elem2)
                        self.universeObjObjects[elem2.attrib['name']] = uo
                
            elif elem1.tag == 'UniverseConditions':
                for elem2 in elem1:
                    if elem2.tag == 'UniverseCondition':
                        uc = TPAPI.UniverseCondition(self.versionID,elem2.attrib['extension'],elem2.attrib['class'],elem2.attrib['name'])
                        uc._getPropertiesFromXML(elem2)
                        self.universeConditionObjects[elem2.attrib['name']] = uc
            else:
                if elem1.text is None:
                    self.properties[elem1.tag] = ''
                else:
                    self.properties[elem1.tag] = TPAPI.safeNull(elem1.text)                        

    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.UniverseClass" + "._getPropertiesFromServer()")

        crsr.execute("SELECT DESCRIPTION,PARENT,ORDERNRO FROM dwhrep.UniverseClass where versionid =? and CLASSNAME =?",(self.versionID, self.universeClassName,))
        resultset = crsr.fetchall()
        desc = crsr.description
        for row in resultset: 
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] == 'ORDERNRO':
                    value = TPAPI.strFloatToInt(value)
                self.properties[x[0]] = value
                i+=1
        self._getUniverseObjects(crsr)
        self._getUniverseConditions(crsr)
        
    def _getUniverseObjects(self,crsr):
        self.logger.debug("TPAPI.UniverseClass" + "._getUniverseObjects()")

        crsr.execute('SELECT OBJECTNAME FROM dwhrep.UniverseObject where versionid=? and classname=?',(self.versionID,self.universeClassName,))
        resultset = crsr.fetchall()
        for row in resultset: 
            unvObj = TPAPI.UniverseObject(self.versionID,self.universeExtension,self.universeClassName,row[0])
            unvObj._getPropertiesFromServer(crsr)
            self.universeObjObjects[row[0]] = unvObj                   
    
    def _getUniverseConditions(self,crsr):
        self.logger.debug("TPAPI.UniverseClass" + "._getUniverseConditions()")
        
        crsr.execute("SELECT UNIVERSECONDITION FROM dwhrep.UniverseCondition where versionid =? and CLASSNAME=?",(self.versionID,self.universeClassName,))
        resultset = crsr.fetchall()
        for row in resultset:
            unvCond= TPAPI.UniverseCondition(self.versionID,self.universeExtension,self.universeClassName,row[0])
            unvCond._getPropertiesFromServer(crsr)
            self.universeConditionObjects[row[0]] = unvCond

    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.UniverseClass" + "._getPropertiesFromTPI()")
        for row in tpiDict['Universeclass']['CLASSNAME']:
            if self.universeClassName == tpiDict['Universeclass']['CLASSNAME'][row] and self.universeExtension.upper() in tpiDict['Universeclass']['UNIVERSEEXTENSION'][row].upper():
                self.properties['ORDERNRO'] = TPAPI.strFloatToInt(tpiDict['Universeclass']['ORDERNRO'][row])
                self.properties['DESCRIPTION'] = TPAPI.safeNull(tpiDict['Universeclass']['DESCRIPTION'][row])
                self.properties['PARENT'] = str(tpiDict['Universeclass']['PARENT'][row])

        #create objects
        if 'Universeobject' in tpiDict:
            for row in tpiDict['Universeobject']['UNIVERSEEXTENSION']:
                #extensionList = tpiDict['Universeobject']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension.upper() == tpiDict['Universeobject']['UNIVERSEEXTENSION'][row].upper():
                    className = tpiDict['Universeobject']['CLASSNAME'][row]
                    if self.universeClassName == className:
                        objName = tpiDict['Universeobject']['OBJECTNAME'][row]
                        unvObj = TPAPI.UniverseObject(self.versionID,self.universeExtension,self.universeClassName,objName)
                        unvObj._getPropertiesFromTPI(tpiDict)
                        self.universeObjObjects[objName] = unvObj
                
        if 'Universecondition' in tpiDict:
            for row in tpiDict['Universecondition']['UNIVERSECONDITION']:
                #extensionList = tpiDict['Universecondition']['UNIVERSEEXTENSION'][row].split(',')
                if self.universeExtension.upper() in tpiDict['Universecondition']['UNIVERSEEXTENSION'][row].upper():
                    className = tpiDict['Universecondition']['CLASSNAME'][row]
                    if self.universeClassName == className:
                        condName = tpiDict['Universecondition']['UNIVERSECONDITION'][row]
                        unvCond = TPAPI.UniverseCondition(self.versionID,self.universeExtension,self.universeClassName,condName)
                        unvCond._getPropertiesFromTPI(tpiDict)
                        self.universeConditionObjects[condName] = unvCond
                    
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
            
            If a xls file is passed it is converted to a xlsDict object before processing.

            Exceptions: 
                       Raised if xlsDict and filename are both None (ie nothing to process)'''
        
        self.logger.debug(self.universeClassName + "._getPropertiesFromXls()")
        if xlsDict==None and filename==None:
                strg = '_getPropertiesFromXls() Nothing to Process'
                raise Exception(strg)
                self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
            
            
            for Name, Value in xlsDict['Class'][self.universeClassName].iteritems():
                if Name != 'UNIVERSEEXTENSION':
                    self.properties[Name] = Value
            

            if self.universeClassName in xlsDict['Object']:
                for Name,  Values in xlsDict['Object'][self.universeClassName].iteritems():
                    if Values['UniverseClass'] == self.universeClassName:
                        unobj = TPAPI.UniverseObject(self.versionID,self.universeExtension,self.universeClassName,Name)                        
                        unobj._getPropertiesFromXls(Values)
                        self.universeObjObjects[Name] = unobj
                        
            if self.universeClassName in xlsDict['Conditions']:
                for Name,  Values in xlsDict['Conditions'][self.universeClassName].iteritems():
                    if Values['CONDOBJCLASS'] == self.universeClassName:
                        uncon = TPAPI.UniverseCondition(self.versionID,self.universeExtension,self.universeClassName,Name)                        
                        uncon._getPropertiesFromXls(Values)
                        self.universeConditionObjects[Name] = uncon

    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = {}        
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['UNIVERSEEXTENSION'] = self.universeExtension
        RepDbDict['CLASSNAME'] = self.universeClassName
        RepDbDict['OBJ_BH_REL'] = 0
        RepDbDict['ELEM_BH_REL'] = 0
        RepDbDict['INHERITANCE'] = 0
        
        if self.universeClassName.upper().endswith('KEYS'):
            from java.lang import Long
            RepDbDict['ORDERNRO'] = Long.MAX_VALUE
        
        TPRepDbInterface.populateUniverseclass(RepDbDict)
        
        condorderno = 0
        joinorderno = 0
                
        for universeCondition in self.universeConditionObjects:
            self.universeConditionObjects[universeCondition]._populateRepDbModel(TPRepDbInterface,condorderno)
            condorderno = condorderno + 1
            
        for universeObject in self.universeObjObjects:
            self.universeObjObjects[universeObject]._populateRepDbModel(TPRepDbInterface,joinorderno)
            joinorderno = joinorderno + 1    
                  
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.tableName,UniObj.tableName)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
        
        ################################################################
        # Universe Object Diff
        Delta = TPAPI.DictDiffer(self.universeObjObjects,UniObj.universeObjObjects)
        deltaObj.location.append('UniverseObject')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeObjObjects[item].universeObjectName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeObjObjects[item].universeObjectName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseObject='+item)
            deltaObj = self.universeObjObjects[item].difference(UniObj.universeObjObjects[item],deltaObj)
            deltaObj.location.pop()
            
        ################################################################
        # Universe Conditions Diff
        Delta = TPAPI.DictDiffer(self.universeConditionObjects,UniObj.universeConditionObjects)
        deltaObj.location.append('UniverseCondition')
        for item in Delta.added():
            deltaObj.addChange('<Added>', UniObj.universeConditionObjects[item].universeConditionName, '', item)
      
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', self.universeConditionObjects[item].universeConditionName, item, '')
        
        deltaObj.location.pop()
        
        for item in Delta.common():
            deltaObj.location.append('UniverseCondition='+item)
            deltaObj = self.universeConditionObjects[item].difference(UniObj.universeConditionObjects[item],deltaObj)
            deltaObj.location.pop() 
        
            
        return deltaObj
    

class UniverseObject(object):
            
    def __init__(self,versionID,universeExtension,universeClassName,universeObjectName):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseObject')
        self.versionID = versionID
        self.universeClassName = universeClassName
        self.universeExtension = universeExtension
        self.universeObjectName = universeObjectName
        self.properties = {}
        self.logger.debug("TPAPI.UniverseObject" + ".__init__()")
    
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseObject" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os +'<UniverseObject name="'+self.universeObjectName  +'" class="'+self.universeClassName  +'" extension="'+self.universeExtension  +'">'
        for prop in self.properties:
            outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
        outputXML +=os +'</UniverseObject>'
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
            
            sheet = workbook.getSheet('Universe Topology Objects')
            dict = TPAPI.XlsDict().UniObjDict
            rowNumber = sheet.getRows()
            
            label = Label(sheet.findCell('Unv. Object').getColumn(), rowNumber, self.universeObjectName)
            sheet.addCell(label)
            label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
            sheet.addCell(label)
            label = Label(sheet.findCell('Unv. Class').getColumn(), rowNumber, self.universeClassName)
            sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                    sheet.addCell(label)
    
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.UniverseObject" + "._getPropertiesFromServer()")

        crsr.execute("SELECT DESCRIPTION,OBJECTTYPE,QUALIFICATION,AGGREGATION,OBJSELECT,OBJWHERE,PROMPTHIERARCHY,ORDERNRO FROM dwhrep.UniverseObject where versionid =? and CLASSNAME=? AND OBJECTNAME =?",(self.versionID,self.universeClassName,self.universeObjectName,))
        resultset = crsr.fetchall()
        desc = crsr.description
        for row in resultset: 
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] == 'ORDERNRO':
                    value = TPAPI.strFloatToInt(value)
                
                self.properties[x[0]] = value
                i+=1
                        
    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.UniverseObject" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
                

    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.UniverseObject" + "._getPropertiesFromTPI()")
        
        for row in tpiDict['Universeobject']['UNIVERSEEXTENSION']:
            #extensionList = tpiDict['Universeobject']['UNIVERSEEXTENSION'][row].split(',')
            if self.universeExtension.upper() in tpiDict['Universeobject']['UNIVERSEEXTENSION'][row].upper():
                if self.universeClassName == tpiDict['Universeobject']['CLASSNAME'][row] and self.universeObjectName == tpiDict['Universeobject']['OBJECTNAME'][row]:
                    #DESCRIPTION,OBJECTTYPE,QUALIFICATION,AGGREGATION,OBJSELECT,OBJWHERE,PROMPTHIERARCHY,OBJ_BH_REL,ELEM_BH_REL,INHERITANCE,ORDERNRO
                    self.properties['DESCRIPTION'] = tpiDict['Universeobject']['DESCRIPTION'][row]
                    self.properties['OBJECTTYPE'] = tpiDict['Universeobject']['OBJECTTYPE'][row]
                    self.properties['QUALIFICATION'] = tpiDict['Universeobject']['QUALIFICATION'][row]
                    self.properties['AGGREGATION'] = tpiDict['Universeobject']['AGGREGATION'][row]
                    self.properties['OBJSELECT'] = tpiDict['Universeobject']['OBJSELECT'][row]
                    self.properties['OBJWHERE'] = tpiDict['Universeobject']['OBJWHERE'][row]
                    self.properties['PROMPTHIERARCHY'] = tpiDict['Universeobject']['PROMPTHIERARCHY'][row]
                    self.properties['ORDERNRO'] = tpiDict['Universeobject']['ORDERNRO'][row]
                    #self.properties['ELEM_BH_REL'] = tpiDict['Universeobject']['ELEM_BH_REL'][row]
                    #self.properties['INHERITANCE'] = tpiDict['Universeobject']['INHERITANCE'][row]
                    
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
        
        If a xls file is passed it is converted to a xlsDict object before processing.

        Exceptions: 
                   Raised if xlsDict and filename are both None (ie nothing to process)'''
        self.logger.debug(self.universeObjectName + "._getPropertiesFromXls()")
        
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
            
            for Name, Value in xlsDict.iteritems():
                if Name != 'UNIVERSEEXTENSION' and Name != 'UniverseClass':                 
                    self.properties[Name] = Value
    
    def _populateRepDbModel(self, TPRepDbInterface, OrderNo):
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['CLASSNAME'] = self.universeClassName
        RepDbDict['UNIVERSEEXTENSION'] = self.universeExtension
        RepDbDict['OBJECTNAME'] = self.universeObjectName
        RepDbDict['OBJ_BH_REL'] = 0
        RepDbDict['ELEM_BH_REL'] = 0
        RepDbDict['INHERITANCE'] = 0
        RepDbDict['ORDERNRO']= OrderNo
        
        TPRepDbInterface.populateUniverseobject(RepDbDict)          
                    
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.universeObjectName,UniObj.universeObjectName)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
        
        return deltaObj

                        
class UniverseCondition(object):
    
    def __init__(self,versionID,universeExtension,universeClassName,universeConditionName):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseCondition')
        self.logger.debug("TPAPI.UniverseCondition" + ".__init__()")
        self.versionID = versionID
        self.universeExtension  = universeExtension
        self.universeClassName = universeClassName
        self.universeConditionName = universeConditionName
        self.properties = {}
        
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseCondition" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os + '<UniverseCondition name="'+self.universeConditionName  +'" class="'+self.universeClassName  +'" extension="'+self.universeExtension  +'">'
        for prop in self.properties:
            outputXML += os2+'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
        outputXML += os + '</UniverseCondition>'
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
            
            sheet = workbook.getSheet('Universe Conditions')
            dict = TPAPI.XlsDict().UniConDict
            rowNumber = sheet.getRows()
            
            label = Label(sheet.findCell('Condition Name').getColumn(), rowNumber, self.universeConditionName)
            sheet.addCell(label)
            label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
            sheet.addCell(label)
            label = Label(sheet.findCell('Class').getColumn(), rowNumber, self.universeClassName)
            sheet.addCell(label)
            
            for FDColumn, Parameter in dict.iteritems():
                if Parameter in self.properties.keys():
                    value = self.properties[Parameter]
                    if value == 1 or value == '1':
                        value = 'Y'
                    elif value == 0 or value == '0':
                        value = ''
                    label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                    sheet.addCell(label)
    
    def _getPropertiesFromServer(self,crsr):
        self.logger.debug("TPAPI.UniverseCondition" + "._getPropertiesFromServer()")

        crsr.execute("SELECT DESCRIPTION,CONDWHERE,AUTOGENERATE,CONDOBJCLASS,CONDOBJECT,PROMPTTEXT,MULTISELECTION,FREETEXT,ORDERNRO FROM dwhrep.UniverseCondition where versionid =? and classname=? and universecondition=?",(self.versionID,self.universeClassName,self.universeConditionName,))
        resultset = crsr.fetchall()
        desc = crsr.description
        for row in resultset:
            i = 0
            for x in desc:
                value = str(row[i])
                if x[0] == 'ORDERNRO':
                    value = TPAPI.strFloatToInt(value)
                
                self.properties[x[0]] = value
                i+=1

    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.UniverseCondition" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
                
    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.UniverseCondition" + "._getPropertiesFromTPI()")
        for row in tpiDict['Universecondition']['UNIVERSEEXTENSION']:
            #extensionList = string.split(tpiDict['Universecondition']['UNIVERSEEXTENSION'][row],',')
            if self.universeExtension.upper() in tpiDict['Universecondition']['UNIVERSEEXTENSION'][row].upper():
                if (self.universeClassName == tpiDict['Universecondition']['CLASSNAME'][row]) and (self.universeConditionName == tpiDict['Universecondition']['UNIVERSECONDITION'][row]):
                    self.properties['DESCRIPTION'] = tpiDict['Universecondition']['DESCRIPTION'][row]
                    self.properties['CONDWHERE'] = tpiDict['Universecondition']['CONDWHERE'][row]
                    self.properties['AUTOGENERATE'] = tpiDict['Universecondition']['AUTOGENERATE'][row]
                    self.properties['CONDOBJCLASS'] = tpiDict['Universecondition']['CONDOBJCLASS'][row]
                    self.properties['CONDOBJECT'] = tpiDict['Universecondition']['CONDOBJECT'][row]
                    self.properties['PROMPTTEXT'] = tpiDict['Universecondition']['PROMPTTEXT'][row]
                    self.properties['MULTISELECTION'] = tpiDict['Universecondition']['MULTISELECTION'][row]
                    self.properties['FREETEXT'] = tpiDict['Universecondition']['FREETEXT'][row]                    
                    self.properties['ORDERNRO'] = tpiDict['Universecondition']['ORDERNRO'][row]
    
    def _getPropertiesFromXls(self,xlsDict=None,filename=None):
        '''Populate the objects contents from a xlsDict object or xls file.
        
        If a xls file is passed it is converted to a xlsDict object before processing.

        Exceptions: 
                   Raised if xlsDict and filename are both None (ie nothing to process)'''
        self.logger.debug(self.universeConditionName + "._getPropertiesFromXls()")
        
        if xlsDict==None and filename==None:
            strg = '_getPropertiesFromXls() Nothing to Process'
            raise Exception(strg)
            self.logger.error(strg)
        else:
            if filename is not None:
                self.logger.debug('_getPropertiesFromXls() extracting from ' + filename)
                xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
            
            for Name, Value in xlsDict.iteritems():
                if Name != 'UNIVERSEEXTENSION':                
                    self.properties[Name] = Value
            
            self._completeModel()
    
    def _completeModel(self):
        if 'MULTISELECTION' not in self.properties or self.properties['MULTISELECTION'] == '':
            self.properties['MULTISELECTION'] = '0'
    
    def _populateRepDbModel(self, TPRepDbInterface,OrderNo):
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['CLASSNAME'] = self.universeClassName
        RepDbDict['UNIVERSEEXTENSION'] = self.universeExtension
        RepDbDict['UNIVERSECONDITION'] = self.universeConditionName
        RepDbDict['OBJ_BH_REL'] = 0
        RepDbDict['ELEM_BH_REL'] = 0
        RepDbDict['INHERITANCE'] = 0
        RepDbDict['ORDERNRO']= OrderNo

        TPRepDbInterface.populateUniversecondition(RepDbDict)
                   
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.universeConditionName,UniObj.universeConditionName)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            if item != 'ORDERNRO':
                deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
        
        return deltaObj



class UniverseJoin(object):

    def __init__(self,versionID,unvextension,sourceColumn,sourceTable,targetColumn,targetTable,tmpCounter):
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.UniverseJoin')
        self.logger.debug("TPAPI.UniverseJoin" + ".__init__()")
        self.versionID = versionID
        self.universeExtension=unvextension
        self.sourceColumn = sourceColumn
        self.sourceTable = sourceTable # refactor to list
        self.sourceTableList = string.split(sourceTable,',')
        self.targetColumn = targetColumn
        self.targetTable = targetTable
        self.tmpCounter = tmpCounter # is this needed?
        self.properties = {} 
        self.contextList = []
        self.joinID = sourceColumn + ":" + sourceTable + ":" + targetColumn + ":" + targetTable #for diff
           
    def _toXML(self,indent=0):
        self.logger.debug("TPAPI.UniverseJoin" + "._toXML()")
        
        offset = '    '
        os = "\n" + offset*indent
        os2 = os + offset
        
        outputXML = os+ '<UniverseJoin sourceColumn="'+self.sourceColumn+'" sourceTable="'+self.sourceTable+'" targetColumn="'+self.targetColumn+'" targetTable="'+self.targetTable+'">'
        for prop in self.properties:
            outputXML += os2 +'<'+str(prop)+'>'+ TPAPI.escape(self.properties[prop]) +'</'+str(prop)+'>'
        outputXML +=os+ '</UniverseJoin>'
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
            
            sheet = workbook.getSheet('Universe Joins')
            dict = TPAPI.XlsDict().UniJoinsDict
            rowNumber = sheet.getRows()
            
            
            addRow = True
            SourceTableColumn = sheet.getColumn(sheet.findCell('Source Table').getColumn())
            del SourceTableColumn[0]
            for SourceTableCell in SourceTableColumn:
                sourceTable = SourceTableCell.getContents()
                sourceColumn = sheet.getColumn(sheet.findCell('Source Columns').getColumn())[SourceTableCell.getRow()]
                targetTable = sheet.getColumn(sheet.findCell('Target Table').getColumn())[SourceTableCell.getRow()]
                targetColumn = sheet.getColumn(sheet.findCell('Target Columns').getColumn())[SourceTableCell.getRow()]                
                if sourceTable == self.sourceTable and sourceColumn == self.sourceColumn and targetTable == self.targetTable and targetColumn == self.targetColumn:
                    addRow = False

            if addRow:
                label = Label(sheet.findCell('Source Table').getColumn(), rowNumber, self.sourceTable)
                sheet.addCell(label)
                label = Label(sheet.findCell('Source Columns').getColumn(), rowNumber, self.sourceColumn)
                sheet.addCell(label)
                label = Label(sheet.findCell('Target Table').getColumn(), rowNumber, self.targetTable)
                sheet.addCell(label)
                label = Label(sheet.findCell('Target Columns').getColumn(), rowNumber, self.targetColumn)
                sheet.addCell(label)
                label = Label(sheet.findCell('Universe Extension').getColumn(), rowNumber, self.universeExtension)
                sheet.addCell(label)
                
                for FDColumn, Parameter in dict.iteritems():
                    if Parameter in self.properties.keys():
                        value = self.properties[Parameter]
                        label = Label(sheet.findCell(FDColumn).getColumn(), rowNumber, str(value))
                        sheet.addCell(label)
    
    def _contextSplit(self):
            if 'CONTEXT' in self.properties.iterkeys():
                self.contextList = string.split(self.properties['CONTEXT'],',')
                
    def getJoinId(self):
        return self.joinID
    
    def _getPropertiesFromServer(self,crsr): 
        self.logger.debug("TPAPI.UniverseJoin" + "._getPropertiesFromServer()")  

        crsr.execute("SELECT SOURCELEVEL,TARGETLEVEL,CARDINALITY,CONTEXT,EXCLUDEDCONTEXTS FROM dwhrep.UniverseJoin where versionid =? and sourceColumn=? and sourceTable=? and targetColumn=? and targettable=?",(self.versionID,self.sourceColumn,self.sourceTable,self.targetColumn,self.targetTable))
        row = crsr.fetchone()
        desc = crsr.description
        if row is not None:
            i = 0
            for x in desc:
                self.properties[x[0]] = str(row[i])
                i+=1
        self._contextSplit()

    def _getPropertiesFromXML(self,xmlElement):
        self.logger.debug("TPAPI.UniverseJoin" + "._getPropertiesFromXML()")
        for elem in xmlElement:
            if elem.text is None:
                self.properties[elem.tag] = ''
            else:
                self.properties[elem.tag] = TPAPI.safeNull(elem.text)
        self._contextSplit()
        
        
    def _getPropertiesFromTPI(self,tpiDict):
        self.logger.debug("TPAPI.UniverseJoin" + "._getPropertiesFromTPI()")
        for row in tpiDict['Universejoin']['CONTEXT']:
            srcc = tpiDict['Universejoin']['SOURCECOLUMN'][row]
            srct = tpiDict['Universejoin']['SOURCETABLE'][row]
            tgtc = tpiDict['Universejoin']['TARGETCOLUMN'][row]
            tgtt = tpiDict['Universejoin']['TARGETTABLE'][row]
            uniext = tpiDict['Universejoin']['UNIVERSEEXTENSION'][row]
            if uniext == '':
                uniext = 'ALL'
            if self.sourceColumn == srcc and self.sourceTable == srct and self.targetTable == tgtt and self.targetColumn == tgtc and self.universeExtension.upper() in uniext:    
                cols = ('SOURCELEVEL','TARGETLEVEL','CARDINALITY','CONTEXT','EXCLUDEDCONTEXTS')
                for col in cols:
                    self.properties[col] = tpiDict['Universejoin'][col][row]
                    
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
                    self.logger.debug('_getPropertiesFromTPI() extracting from ' + filename)
                    xlsDict = TPAPI.XlsDict(filename).returnXlsDict()
                
                for Name, Value in xlsDict.iteritems():
                    if Name != 'SOURCETABLE' and Name != 'SOURCECOLUMN' and Name != 'TARGETTABLE' and Name != 'TARGETCOLUMN' and Name != 'UNIVERSEEXTENSION':
                        self.properties[Name] = Value
    
    def _populateRepDbModel(self, TPRepDbInterface):
        RepDbDict = deepcopy(self.properties)
        RepDbDict['VERSIONID'] = self.versionID
        RepDbDict['SOURCECOLUMN'] = self.sourceColumn
        RepDbDict['SOURCETABLE'] = self.sourceTable      
        RepDbDict['TARGETCOLUMN'] = self.targetColumn
        RepDbDict['TARGETTABLE'] = self.targetTable
        RepDbDict['TMPCOUNTER'] = self.tmpCounter
        RepDbDict['UNIVERSEEXTENSION']=self.universeExtension
        
        TPRepDbInterface.populateUniversejoin(RepDbDict)
        
    
    
    def difference(self,UniObj,deltaObj=None):
        
        if deltaObj is None:
            deltaObj = TPAPI.Delta(self.joinID,UniObj.joinID)
         
        #########################################################################################################################################
        # Properties diff
        Delta = TPAPI.DictDiffer(self.properties,UniObj.properties)
        deltaObj.location.append('Properties')
        for item in Delta.changed():
            deltaObj.addChange('<Changed>', item, self.properties[item], UniObj.properties[item])
        
        for item in Delta.added():
            deltaObj.addChange('<Added>', item, '', UniObj.properties[item])
                
        for item in Delta.removed():
            deltaObj.addChange('<Removed>', item, self.properties[item], '')

        deltaObj.location.pop()
        
        return deltaObj


        
        
        
    

