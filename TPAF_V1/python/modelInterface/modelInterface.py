'''
Created on 23 Jul 2013

@author: ebrifol
'''
import TPAPI
from DRT import DesignRulesTool
import sys
import os
import traceback
from com.ericsson.procus.tpaf.model import ModelInterface
from com.ericsson.procus.tpaf.utils import ModelException
from java.util import HashMap;
from java.util import ArrayList;
from java.util import UUID

class modelInterface(ModelInterface):
    
    TechPackName = None
    ProductNumber = 'Unknown'
    EniqVersion = 'Unknown'
    Rstate = 'Unknown'
    LoadSource = 'Unknown'
    LoadDate = ''
    Dictionary = None

    
    def __init__(self):
        self.tp = None
        self.UID = str(UUID.randomUUID())
    
    def getModelUID(self):
        return self.UID
    
    def getTechPackName(self):
        return self.TechPackName
    
    def getProductNumber(self):
        return self.ProductNumber
    
    def getRstate(self):
        return self.Rstate
    
    def getEniqVersion(self):
        return self.EniqVersion
    
    def getLoadDate(self):
        return self.LoadDate
    
    def setLoadDate(self, date):
        self.LoadDate = date
    
    def getLoadSource(self):
        return self.LoadSource
    
    def setLoadSource(self, Location):
        self.LoadSource = Location
    
    def getVersioningInformation(self):
        versioningInfo = HashMap()
        for key, value in sorted(self.tp.versioning.iteritems()):
            versioningInfo.put(key, value)
        return versioningInfo
    
    def getSupportedVendorReleases(self):
        supportedReleases = ",".join(self.tp.supportedVendorReleases)
        return supportedReleases
    
    def updateLockedInfo(self, LockedBy, LockedDate):
        self.tp.versioning['LOCKEDBY'] = LockedBy
        self.tp.versioning['LOCKDATE'] = LockedDate
    
    def updateENIQversion(self, ENIQverison):
        self.tp.versioning['ENIQ_LEVEL'] = ENIQverison
        
    
    def DecryptTpi(self, tpiPath):
        try:
            tpiPath = tpiPath.replace('\\','/')
            copyPath = TPAPI.copyTpiToTemp(tpiPath)
            TPAPI.decryptTpiFile(copyPath)
            return copyPath
        except:
            traceback.print_exc(file=sys.stdout)
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def loadDictionaryFromTpi(self, tpiPath):
        try:
            tpiPath = tpiPath.replace('\\','/') 
            self.Dictionary = TPAPI.TpiDict(tpiPath).returnTPIDict()
        except:
            traceback.print_exc(file=sys.stdout)
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def populateModelFromTPIdictionary(self):
        try: 
            self.tp = TPAPI.TechPackVersion('DC_E_LOAD:((1))')
            self.tp.getPropertiesFromTPI(tpiDict=self.Dictionary)
            self.TechPackName = self.tp.versionID
            if 'TECHPACK_VERSION' in self.tp.versioning:
                self.Rstate = self.tp.versioning['TECHPACK_VERSION']
            if 'PRODUCT_NUMBER' in self.tp.versioning:
                self.ProductNumber = self.tp.versioning['PRODUCT_NUMBER']
            if 'ENIQ_LEVEL' in self.tp.versioning:
                self.EniqVersion = self.tp.versioning['ENIQ_LEVEL']
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        finally:
            self.Dictionary.clear()
    
    def populateModelFromXML(self, xmlPath):
        try: 
            xmlPath = xmlPath.replace('\\','/') 
            self.tp = TPAPI.TechPackVersion('DC_E_LOAD:((1))')
            self.tp.getPropertiesFromXML(filename=xmlPath)
            self.TechPackName = self.tp.versionID
            if 'TECHPACK_VERSION' in self.tp.versioning:
                self.Rstate = self.tp.versioning['TECHPACK_VERSION']
            if 'PRODUCT_NUMBER' in self.tp.versioning:
                self.ProductNumber = self.tp.versioning['PRODUCT_NUMBER']
            if 'ENIQ_LEVEL' in self.tp.versioning:
                self.EniqVersion = self.tp.versioning['ENIQ_LEVEL']
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def loadDictionaryFromFD(self, FDpath):
        try:
            FDpath = FDpath.replace('\\','/') 
            self.Dictionary = TPAPI.XlsDict(FDpath).returnXlsDict()
        except:
            traceback.print_exc(file=sys.stdout)
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
            
    def populateModelFromFDdictionary(self):
        try: 
            self.tp = TPAPI.TechPackVersion('DC_E_LOAD:((1))')
            self.tp.getPropertiesFromXls(xlsDict=self.Dictionary)
            self.TechPackName = self.tp.versionID
            if 'TECHPACK_VERSION' in self.tp.versioning:
                self.Rstate = self.tp.versioning['TECHPACK_VERSION']
            if 'PRODUCT_NUMBER' in self.tp.versioning:
                self.ProductNumber = self.tp.versioning['PRODUCT_NUMBER']
            if 'ENIQ_LEVEL' in self.tp.versioning:
                self.EniqVersion = self.tp.versioning['ENIQ_LEVEL']
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        finally:
            self.Dictionary.clear()
    
    def getTPNameFromServer(self, serverName):
        ListofNames = ArrayList()
        try:
            Names = TPAPI.getTechPacks(serverName)
            for name in sorted(Names):
                if name.startswith('DC') or name.startswith('DIM'):
                    ListofNames.add(name)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            ListofNames.add(exception)
        return ListofNames
    
    def populateModelFromServer(self, serverName, TPName):
        try:
            self.tp = TPAPI.TechPackVersion(TPName)
            self.tp.getPropertiesFromServer(serverName)
            self.TechPackName = self.tp.versionID
            if 'TECHPACK_VERSION' in self.tp.versioning:
                self.Rstate = self.tp.versioning['TECHPACK_VERSION']
            if 'PRODUCT_NUMBER' in self.tp.versioning:
                self.ProductNumber = self.tp.versioning['PRODUCT_NUMBER']
            if 'ENIQ_LEVEL' in self.tp.versioning:
                self.EniqVersion = self.tp.versioning['ENIQ_LEVEL']
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    def setupENIQEnvironment(self, server, path):
        try:
            path = path.replace('\\','/') 
            TPAPI.ENIQEnvironment(server).setupOnlaptop(path)
        except:
            traceback.print_exc(file=sys.stdout)
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createTechPack(self, server):
        try:
            self.tp.CreateTP(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createTechPackSets(self, server, outputPath):
        try:
            outputPath = outputPath.replace('\\','/')
            self.tp.generateSets(server, outputPath)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def activateTechPack(self, server):
        try:
            self.tp.activateTP(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createTechPacktpi(self, server, build, outputPath, encrypt):
        try:
            outputPath = outputPath.replace('\\','/')
            self.tp.createTPInstallFile(server, build, outputPath, encrypt)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    def createInterfaces(self, server):
        try:
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                InterfaceObject.CreateIntf(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createInterfaceSets(self, server, outputPath):
        try:
            outputPath = outputPath.replace('\\','/')
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                InterfaceObject.generateSets(server, outputPath)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createInterfacetpis(self, server, outputPath, encrypt):
        try:
            outputPath = outputPath.replace('\\','/')
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                buildNumber = InterfaceObject.intfVersionID.split(':')[1]
                buildNumber = buildNumber.replace('((','')
                buildNumber = buildNumber.replace('))','')
                InterfaceObject.createTPInstallFile(server, int(buildNumber), outputPath, encrypt)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def activateInterfaces(self, server):
        try:
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                InterfaceObject.activateIntf(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    def deactivateTechPack(self, server):
        try:
            self.tp.deActivateTP(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def deleteSetsTechPack(self, server):
        try:
            self.tp.deleteSets(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    def deleteTechPack(self, server):
        try:
            self.tp.deleteTP(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def deActivateInterfaces(self, server):
        try:
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                InterfaceObject.deActivateIntf(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def deleteInterfaces(self, server):
        try:
            for InterfaceObject in self.tp.interfaceObjects.itervalues():
                InterfaceObject.deleteIntf(server)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    
    def createTechPackDescDoc(self, server, outputPath):
        try:
            outputPath = outputPath.replace('\\','/')
            self.tp.createDocumentation(server, outputPath)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createTechPackXLSDoc(self, templateLocation, outputPath):
        try:
            outputPath = outputPath.replace('\\','/')
            self.tp.toXLS(templateLocation, outputPath)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createTechPackXMlDoc(self, outputPath):
        try:
            outputPath = outputPath.replace('\\','/')
            fileName = outputPath+'\\'+self.getTechPackOutputName()+'.xml'
            TPAPI.writeXMLFile(self.tp.toXML(), fileName)
        except:
            traceback.print_exc(file=sys.stdout)
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    def getTechPackOutputName(self):
        return self.tp.tpName+'_'+str(self.tp.versionNo)+'_'+self.tp.versioning['TECHPACK_VERSION']
        
    def getRuleSetProperties(self, RuleSetPath):
        rules = HashMap()
        try:
            RuleSetPath = RuleSetPath.replace('\\','/')
            self.rulesTool = DesignRulesTool.DRM(RuleSetPath)
            Dictionary = self.rulesTool.getRuleSetsProperties()
             
            for key, value in Dictionary.iteritems():
                ruleInfo = HashMap()
                for rule, docString in value.iteritems():
                    ruleInfo.put(rule, docString)
                rules.put(key, ruleInfo)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        return rules
     
    def executeRules(self, moduleName, RulesToRun):
        errors = HashMap()
        try:
            ErrorDict = self.rulesTool.executeRules(self.tp, moduleName, RulesToRun)
            
            for rule in sorted(ErrorDict.iterkeys()):
                errorInfo = HashMap()
                errorlist  = ArrayList()
                for errorMessage, errorItems in ErrorDict[rule].iteritems():
                    for item in errorItems:
                        errorlist.add(item)
                    errorInfo.put(errorMessage, errorlist)
                errors.put(rule, errorInfo)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        return errors
    
    def runDifference(self, diffModel, outputDir):
        try:
            outputDir = outputDir.replace('\\','/')
            tpd = self.tp.difference(diffModel.tp)
            if tpd.getNumOfDifferences() > 0:
                f=open(outputDir+'\\DifferenceOuput.txt', 'w')
                f.write('Difference results between '+self.TechPackName+' and '+ diffModel.TechPackName+'\n\n')
                f.write(tpd.toString())
                f.close()
            return tpd.getNumOfDifferences()
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
        
    
    def initBOUniverse(self, outputDir, BIversion):
        try:
            outputDir = outputDir.replace('\\','/')
            self.BO = TPAPI.BOuniverse(self.TechPackName, outputDir, BIversion)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    
    def createUniverse(self, BISIP, ODBC, repDb, username, password):
        try:
            self.BO.createUniverse(BISIP,ODBC,repDb,username,password)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def updateUniverse(self, BISIP, ODBC, repDb, username, password):
        try:
            self.BO.updateUniverse(BISIP,ODBC,repDb,username,password)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createVerificationReports(self, BISIP, ODBC, repDb, username, password):
        try:
            self.BO.createVerificationReport(BISIP,ODBC,repDb,username,password)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createBOReferenceDoc(self, BISIP, ODBC, repDb, username, password):
        try:
            self.BO.createBOReferenceDoc(BISIP,ODBC,repDb,username,password)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)
    
    def createBOPackage(self, LockedBy):
        try:
            self.BO.createBOPackage(self.Rstate, LockedBy, self.EniqVersion, encrypt)
        except:
            exception = ''.join(traceback.format_exception(*sys.exc_info())[-2:]).strip().replace('\n',': ')
            raise ModelException(exception)

    def getServerENIQVersion(self, server):
        ftp = TPAPI.getFTPConnection(server, 'dcuser', 'dcuser')
        version = TPAPI.getENIQversion(ftp)
        return version
