'''
Created on 8 Mar 2013

@author: ebrifol
'''

import TPAPI
import sys
import traceback

class TPRepDbInterface(object):
    
    def __init__(self,server):
        self.server = server
        self.versionID = None
        self.TargetEniqVersion = None
        self.Versioning = None
        self.TechPackDependency = {}
        self.SupportedVendorReleases = []
        self.RefTables = {}
        self.RefKeys = {}
        self.MeasTypes = {}
        self.MeasTypeClass = {}
        self.MeasCounts = {}
        self.MeasKeys = {}
        self.MeasobjBHsupport = {}
        self.MeasDeltaCalcSupprt = {}
        self.MeasVectors = {}
        self.Transformer = {}
        self.Transformation = {}
        self.AttributeTags = {}
        self.DefaultTags = []
        self.BusyHourRankingTable = ''
        self.BusyHour = {}
        self.BusyHourMapping = {}
        self.BusyHourPlaceholders = {}
        self.BusyHourRankkeys = {}
        self.BusyHourSource = {}
        self.Universenames = {}
        self.Universetables = {}
        self.Universeclasses = {}
        self.Universeobjects = {}
        self.Universeconditions = {}
        self.Universejoins = {}
        self.Universecomputedobjects = {}
        self.Universeformulas = {}
        self.Universeparameters = {}
        self.Verificationobjects = {}
        self.Verificationconditions = {}
        self.ExternalStatements = {}
        
        self.etlrep = None
        self.dwhrep = None
        self.dwhRock = None
        self.dbaDwhRock = None
        self.createRockFactoryConnections()
        
        
    def createRockFactoryConnections(self):
        from ssc.rockfactory import RockFactory
        from com.distocraft.dc5000.etl.rock import Meta_databases
        from com.distocraft.dc5000.etl.rock import Meta_databasesFactory
        
        self.etlrep = RockFactory("jdbc:sybase:Tds:"+ self.server +":2641", "etlrep", "etlrep", "com.sybase.jdbc3.jdbc.SybDriver", "TPAF", True)
        self.dwhrep = RockFactory("jdbc:sybase:Tds:"+ self.server +":2641", "dwhrep", "dwhrep", "com.sybase.jdbc3.jdbc.SybDriver", "TPAF", True)
        
        mdbdwh = Meta_databases(self.etlrep)
        mdbdwh.setConnection_name("dwh")
        mdbdwh.setType_name("USER")
        mdbdwhf = Meta_databasesFactory(self.etlrep, mdbdwh)
        dwhdb = mdbdwhf.get().get(0)
        
        mdbadwhdb = Meta_databases(self.etlrep)
        mdbadwhdb.setConnection_name("dwh")
        mdbadwhdb.setType_name("DBA")
        mdbadwhdbf = Meta_databasesFactory(self.etlrep, mdbadwhdb)
        dbadwhdb = mdbadwhdbf.get().get(0)
        
        dbURL = dwhdb.getConnection_string()
        ix = dbURL.index("dwhdb")
        if ix >= 0:
            parts = dbURL.split("dwhdb")
            dbURL = parts[0] + self.server + parts[1]
        
        self.dwhRock = RockFactory(dbURL, dwhdb.getUsername(), dwhdb.getPassword(), dwhdb.getDriver_name(), "TPAF", True)
        self.dbaDwhRock = RockFactory(dbURL, dbadwhdb.getUsername(), dbadwhdb.getPassword(), dwhdb.getDriver_name(),"TPAF", True)
    
    def setRockFactoryAutoCommit(self, state):
        self.dwhrep.getConnection().setAutoCommit(state)
        self.etlrep.getConnection().setAutoCommit(state)
        self.dwhRock.getConnection().setAutoCommit(state)
        self.dbaDwhRock.getConnection().setAutoCommit(state)
    
    def populateVersioning(self,VersioningDict, versionID):
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        self.versionID = versionID
        VersioningDict['VERSIONID'] = versionID
        self.TargetEniqVersion = TPAPI.getENIQversion(TPAPI.getFTPConnection(self.server, 'dcuser', 'dcuser'))
        VersioningDict['ENIQ_LEVEL'] = self.TargetEniqVersion
        self.Versioning = self.populateObjectFromDict(Versioning, VersioningDict)
        
    def populateTechPackDependency(self,DepsDict):
        from com.distocraft.dc5000.repository.dwhrep import Techpackdependency
        KEY = DepsDict['VERSIONID'] + ":" + DepsDict['TECHPACKNAME']
        if KEY not in self.TechPackDependency:
            self.TechPackDependency[KEY] = self.populateObjectFromDict(Techpackdependency, DepsDict)
    
    def populateSupportedVendorReleases(self, supportedVendorReleases, versionID):
        from com.distocraft.dc5000.repository.dwhrep import Supportedvendorrelease
        for vendorRelease in supportedVendorReleases:
            RepVendorRelease = Supportedvendorrelease(self.dwhrep, True)
            RepVendorRelease.setVersionid(versionID)
            RepVendorRelease.setVendorrelease(vendorRelease)
            self.SupportedVendorReleases.append(RepVendorRelease)
    
    def populateReferencetable(self,RefTypeDict):
        from com.distocraft.dc5000.repository.dwhrep import Referencetable       
        TYPEID = RefTypeDict['TYPEID']
        if TYPEID not in self.RefTables:
            self.RefTables[TYPEID] = self.populateObjectFromDict(Referencetable, RefTypeDict)  
    
    def populateMeasurementType(self,MeasTypeDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype       
        TYPEID = MeasTypeDict['TYPEID']
        if TYPEID not in self.MeasTypes:
            self.MeasTypes[TYPEID] = self.populateObjectFromDict(Measurementtype, MeasTypeDict)

    
    def populateMeasurementTypeClass(self,MeasTypeClassDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementtypeclass
        TYPECLASSID = MeasTypeClassDict['TYPECLASSID']
        if TYPECLASSID not in self.MeasTypeClass:
            self.MeasTypeClass[TYPECLASSID] = self.populateObjectFromDict(Measurementtypeclass, MeasTypeClassDict)

    def populateMeasurementCounter(self, MeasCountDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementcounter       
        KEY = MeasCountDict['TYPEID'] + ":" + MeasCountDict['DATANAME']
        MeasCountDict['COUNTAGGREGATION'] = self.evaluteCountAggreation(MeasCountDict)
        if KEY not in self.MeasCounts:
            self.MeasCounts[KEY] = self.populateObjectFromDict(Measurementcounter, MeasCountDict)
    
    def populateMeasurementKey(self, MeasKeyDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementkey         
        KEY = MeasKeyDict['TYPEID'] + ":" + MeasKeyDict['DATANAME']
        if KEY not in self.MeasKeys:
            self.MeasKeys[KEY] = self.populateObjectFromDict(Measurementkey, MeasKeyDict)
            
    def populateReferencecolumn(self, RefKeyDict):
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn         
        KEY = RefKeyDict['TYPEID'] + ":" + RefKeyDict['DATANAME']
        if KEY not in self.RefKeys:
            self.RefKeys[KEY] = self.populateObjectFromDict(Referencecolumn, RefKeyDict)
    
    def populateMeasurementdeltacalcsupport(self, MeasdeltaCalcDict):
        '''Special handling is needed here to map all possible vendor releases and vendor releases the table is associated with'''
        from com.distocraft.dc5000.repository.dwhrep import Measurementdeltacalcsupport
        ''' Count Aggregation will be evalutated using these two lists when populating counters. '''
        self.CountAggSupportedList = []
        self.CountAggNotSupportedList = []
        supportedReleases = MeasdeltaCalcDict['VENDORRELEASE']+','
        supportedReleases = supportedReleases.split(',')
        for Release in self.SupportedVendorReleases:
            MeasdeltaCalcDict['VENDORRELEASE'] = Release.getVendorrelease()
            if Release.getVendorrelease() in supportedReleases:
                MeasdeltaCalcDict['DELTACALCSUPPORT'] = 1
                self.CountAggSupportedList.append(MeasdeltaCalcDict['VENDORRELEASE'])
            else:
                MeasdeltaCalcDict['DELTACALCSUPPORT'] = 0
                self.CountAggNotSupportedList.append(MeasdeltaCalcDict['VENDORRELEASE'])
                
            KEY = MeasdeltaCalcDict['TYPEID'] + ":" + MeasdeltaCalcDict['VENDORRELEASE'] + ":" + MeasdeltaCalcDict['VERSIONID']
            if KEY not in self.MeasDeltaCalcSupprt:
                self.MeasDeltaCalcSupprt[KEY] = self.populateObjectFromDict(Measurementdeltacalcsupport, MeasdeltaCalcDict)
           
    def populateMeasurementobjBhSupport(self, MeasbhSupDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport         
        KEY = MeasbhSupDict['TYPEID'] + ":" + MeasbhSupDict['OBJBHSUPPORT']
        if KEY not in self.MeasobjBHsupport:
            self.MeasobjBHsupport[KEY] = self.populateObjectFromDict(Measurementobjbhsupport, MeasbhSupDict)
    
    def populateMeasurementVector(self, MeasVecDict):
        from com.distocraft.dc5000.repository.dwhrep import Measurementvector         
        KEY = MeasVecDict['TYPEID'] + ":" + MeasVecDict['DATANAME'] + ":" + MeasVecDict['VENDORRELEASE'] + ":" + MeasVecDict['VINDEX']
        if KEY not in self.MeasVectors:
            self.MeasVectors[KEY] = self.populateObjectFromDict(Measurementvector, MeasVecDict)
    
    def populateBusyHour(self,BusyHourDict):
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        BusyHourDict['BHLEVEL'] = self.BusyHourRankingTable
        KEY = BusyHourDict['VERSIONID'] + ":" + BusyHourDict['BHLEVEL'] + ":" + BusyHourDict['BHTYPE']
        KEY = KEY + ":" + BusyHourDict['TARGETVERSIONID'] + ":" + BusyHourDict['BHOBJECT'] 
        if KEY not in self.BusyHour:
            self.BusyHour[KEY] = self.populateObjectFromDict(Busyhour,BusyHourDict)

    def populateBusyHourMapping(self,BusyHourMapDict):
        from com.distocraft.dc5000.repository.dwhrep import Busyhourmapping
        KEY = BusyHourMapDict['VERSIONID'] + ":" + BusyHourMapDict['BHLEVEL'] + ":" + BusyHourMapDict['BHTYPE'] 
        KEY = KEY + ":" + BusyHourMapDict['TARGETVERSIONID'] + ":" + BusyHourMapDict['BHOBJECT'] + ":" + BusyHourMapDict['TYPEID'] 
        if KEY not in self.BusyHourMapping:
            self.BusyHourMapping[KEY] = self.populateObjectFromDict(Busyhourmapping,BusyHourMapDict)
       
    def populateBusyhourPlaceholders(self,BusyHourPlaceholdersDict):
        from com.distocraft.dc5000.repository.dwhrep import Busyhourplaceholders
        KEY = BusyHourPlaceholdersDict['VERSIONID'] + ":" + BusyHourPlaceholdersDict['BHLEVEL']  
        if KEY not in self.BusyHourPlaceholders:
            self.BusyHourPlaceholders[KEY] = self.populateObjectFromDict(Busyhourplaceholders,BusyHourPlaceholdersDict)
   
    def populateBusyhourRankkeys(self,BusyhourRankkeysDict):
        from com.distocraft.dc5000.repository.dwhrep import Busyhourrankkeys
        BusyhourRankkeysDict['BHLEVEL'] = self.BusyHourRankingTable
        KEY = BusyhourRankkeysDict['VERSIONID'] + ":" + BusyhourRankkeysDict['BHLEVEL'] + ":" + BusyhourRankkeysDict['BHTYPE']
        KEY = KEY + ":" + BusyhourRankkeysDict['TARGETVERSIONID'] + ":" + BusyhourRankkeysDict['BHOBJECT'] + ":" + BusyhourRankkeysDict['KEYNAME']
        if KEY not in self.BusyHourRankkeys:
            self.BusyHourRankkeys[KEY] = self.populateObjectFromDict(Busyhourrankkeys,BusyhourRankkeysDict)
     
    def populateBusyhourSource(self,BusyHourSourceDict):
        from com.distocraft.dc5000.repository.dwhrep import Busyhoursource
        BusyHourSourceDict['BHLEVEL'] = self.BusyHourRankingTable
        KEY = BusyHourSourceDict['VERSIONID'] + ":" + BusyHourSourceDict['BHLEVEL'] + ":" + BusyHourSourceDict['BHTYPE']
        KEY = KEY + ":" + BusyHourSourceDict['TARGETVERSIONID'] + ":" + BusyHourSourceDict['BHOBJECT']+ ":" + BusyHourSourceDict['TYPENAME'] 
        if KEY not in self.BusyHourSource:
            self.BusyHourSource[KEY] = self.populateObjectFromDict(Busyhoursource,BusyHourSourceDict)
            
    def populateTransformer(self, transformerDict):
        from com.distocraft.dc5000.repository.dwhrep import Transformer
        KEY = transformerDict['TRANSFORMERID']
        transformerDict['VERSIONID'] = self.Versioning.getVersionid()
        if KEY not in self.Transformer:
            self.Transformer[KEY] = self.populateObjectFromDict(Transformer, transformerDict)
            
    def populateTransformation(self, transformationDict):
        from com.distocraft.dc5000.repository.dwhrep import Transformation
        KEY = transformationDict['TRANSFORMERID']+':'+transformationDict['ORDERNO']
        if KEY not in self.Transformation:
            self.Transformation[KEY] = self.populateObjectFromDict(Transformation, transformationDict)
    
    def populateAttributeTags(self, AttributeTagsDict):
        self.AttributeTags = dict(self.AttributeTags.items() + AttributeTagsDict.items())
        
    def populateDefaultTags(self, dataformatID, defaultTags):
        from com.distocraft.dc5000.repository.dwhrep import Defaulttags
        for tag in defaultTags:
            RepDbDict = {}
            RepDbDict['TAGID'] = tag
            RepDbDict['DATAFORMATID'] = dataformatID
            RepDbDict['DESCRIPTION'] = 'tag'
            self.DefaultTags.append(self.populateObjectFromDict(Defaulttags, RepDbDict))
    
    def populateUniversename(self, UniversenameDict):
        from com.distocraft.dc5000.repository.dwhrep import Universename
        KEY = UniversenameDict['VERSIONID']+':'+UniversenameDict['UNIVERSEEXTENSION']
        if KEY not in self.Universenames:
            self.Universenames[KEY] = self.populateObjectFromDict(Universename, UniversenameDict)
            
    def populateUniversetable(self, UniversetableDict):
        from com.distocraft.dc5000.repository.dwhrep import Universetable
        KEY = UniversetableDict['TABLENAME']+':'+UniversetableDict['UNIVERSEEXTENSION']
        if KEY not in self.Universetables:
            self.Universetables[KEY] = self.populateObjectFromDict(Universetable, UniversetableDict)
            
    def populateUniverseclass(self, UniverseclassDict):
        from com.distocraft.dc5000.repository.dwhrep import Universeclass
        KEY = UniverseclassDict['CLASSNAME']+':'+UniverseclassDict['UNIVERSEEXTENSION']
        if KEY not in self.Universeclasses:
            self.Universeclasses[KEY] = self.populateObjectFromDict(Universeclass, UniverseclassDict)
            
    def populateUniverseobject(self, UniobjectDict):
        from com.distocraft.dc5000.repository.dwhrep import Universeobject
        KEY = UniobjectDict['CLASSNAME']+':'+UniobjectDict['UNIVERSEEXTENSION']+':'+UniobjectDict['OBJECTNAME']
        if KEY not in self.Universeobjects:
            self.Universeobjects[KEY] = self.populateObjectFromDict(Universeobject, UniobjectDict)
            
    def populateUniversecondition(self, UniconDict):
        from com.distocraft.dc5000.repository.dwhrep import Universecondition
        KEY = UniconDict['CLASSNAME']+':'+UniconDict['UNIVERSEEXTENSION']+':'+UniconDict['UNIVERSECONDITION']
        if KEY not in self.Universeconditions:
            self.Universeconditions[KEY] = self.populateObjectFromDict(Universecondition, UniconDict)
            
    def populateUniversejoin(self, UnijoinDict):
        from com.distocraft.dc5000.repository.dwhrep import Universejoin
        KEY = UnijoinDict['SOURCETABLE']+':'+UnijoinDict['SOURCECOLUMN']+':'+UnijoinDict['TARGETTABLE']
        KEY = KEY+':'+UnijoinDict['TARGETCOLUMN']+':'+str(UnijoinDict['TMPCOUNTER'])
        if KEY not in self.Universejoins:
            self.Universejoins[KEY] = self.populateObjectFromDict(Universejoin, UnijoinDict)
            
    def populateUniversecomputedobject(self, UnicompobjDict):
        from com.distocraft.dc5000.repository.dwhrep import Universecomputedobject
        KEY = UnicompobjDict['CLASSNAME']+':'+UnicompobjDict['UNIVERSEEXTENSION']+':'+UnicompobjDict['OBJECTNAME']
        if KEY not in self.Universecomputedobjects:
            self.Universecomputedobjects[KEY] = self.populateObjectFromDict(Universecomputedobject, UnicompobjDict)
            
    def populateUniverseformulas(self, UniformsDict):
        from com.distocraft.dc5000.repository.dwhrep import Universeformulas
        KEY = UniformsDict['NAME']
        if KEY not in self.Universeformulas:
            self.Universeformulas[KEY] = self.populateObjectFromDict(Universeformulas, UniformsDict)
            
    def populateUniverseparameters(self, UniparamsDict):
        from com.distocraft.dc5000.repository.dwhrep import Universeparameters
        KEY = UniparamsDict['CLASSNAME']+':'+UniparamsDict['OBJECTNAME']+':'+UniparamsDict['UNIVERSEEXTENSION']+':'+UniparamsDict['ORDERNRO']
        if KEY not in self.Universeparameters:
            self.Universeparameters[KEY] = self.populateObjectFromDict(Universeparameters, UniparamsDict)
    
    def populateVerificationcondition(self, VerConDict):
        from com.distocraft.dc5000.repository.dwhrep import Verificationcondition
        KEY = VerConDict['VERLEVEL']+':'+VerConDict['CONDITIONCLASS']+':'+VerConDict['VERCONDITION']
        if KEY not in self.Verificationconditions:
            self.Verificationconditions[KEY] = self.populateObjectFromDict(Verificationcondition, VerConDict)
            
    def populateVerificationobject(self, VerObjDict):
        from com.distocraft.dc5000.repository.dwhrep import Verificationobject
        KEY = VerObjDict['MEASLEVEL']+':'+VerObjDict['OBJECTCLASS']+':'+VerObjDict['OBJECTNAME']
        if KEY not in self.Verificationobjects:
            self.Verificationobjects[KEY] = self.populateObjectFromDict(Verificationobject, VerObjDict)
            
    def populateExternalStatement(self, ESDict):
        from com.distocraft.dc5000.repository.dwhrep import Externalstatement
        KEY = int(ESDict['EXECUTIONORDER'])
        if KEY not in self.ExternalStatements:
            self.ExternalStatements[KEY] = self.populateObjectFromDict(Externalstatement, ESDict)
    
    def evaluteCountAggreation(self, MeasCountDict):
        if self.MeasTypes[MeasCountDict['TYPEID']].getDeltacalcsupport() == 1:
            if len(self.CountAggSupportedList) == 0:
                return 'GAUGE'
            elif len(self.CountAggNotSupportedList) == 0:
                return 'PEG'
            else:
                return ','.join(self.CountAggSupportedList) + ';PEG/' + ','.join(self.CountAggNotSupportedList) + ';GAUGE'
            
        return ''
      
    def deactivateTP(self, versionID):
        from com.distocraft.dc5000.repository.dwhrep import Tpactivation
        from com.distocraft.dc5000.repository.dwhrep import TpactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Typeactivation
        from com.distocraft.dc5000.repository.dwhrep import TypeactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Dwhtechpacks
        from com.distocraft.dc5000.repository.dwhrep import DwhtechpacksFactory
        from com.distocraft.dc5000.repository.dwhrep import Externalstatementstatus
        from com.distocraft.dc5000.repository.dwhrep import ExternalstatementstatusFactory
        from com.distocraft.dc5000.repository.dwhrep import Dwhtype
        from com.distocraft.dc5000.repository.dwhrep import DwhtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Dwhcolumn
        from com.distocraft.dc5000.repository.dwhrep import DwhcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Dwhpartition
        from com.distocraft.dc5000.repository.dwhrep import DwhpartitionFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementobjbhsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import BusyhourFactory
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import VersioningFactory
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from com.distocraft.dc5000.etl.rock import Meta_collections
        from com.distocraft.dc5000.etl.rock import Meta_collectionsFactory
        
        #f = open('DEACTIVATE.txt', 'w')
        import time
        start_time = time.time()
        
        self.Versioning = Versioning(self.dwhrep, versionID)
        
        tpName = self.Versioning.getTechpack_name()
        
        tpa = Tpactivation(self.dwhrep)
        tpa.setTechpack_name(tpName)

        tpaF = TpactivationFactory(self.dwhrep, tpa)
        for tpatmp in tpaF.get():
            typeAct = Typeactivation(self.dwhrep)
            typeAct.setTechpack_name(tpatmp.getTechpack_name())
            typeActF = TypeactivationFactory(self.dwhrep, typeAct)
            for typeActtmp in typeActF.get():
                typeActtmp.deleteDB()   
            dwhtp = Dwhtechpacks(self.dwhrep)
            dwhtp.setVersionid(tpatmp.getVersionid())
            dwhtpF = DwhtechpacksFactory(self.dwhrep, dwhtp)
            for dwhtptmp in dwhtpF.get():
                ext = Externalstatementstatus(self.dwhrep)
                ext.setTechpack_name(dwhtptmp.getTechpack_name())
                extF = ExternalstatementstatusFactory(self.dwhrep, ext)
                for exttmp in extF.get():
                    exttmp.deleteDB();
                
                dwhtype = Dwhtype(self.dwhrep)
                dwhtype.setTechpack_name(dwhtptmp.getTechpack_name())
                dwhtypeF = DwhtypeFactory(self.dwhrep, dwhtype)
                for dwhtypetmp in dwhtypeF.get():
                    containsView = False
                    dwhcolumn = Dwhcolumn(self.dwhrep)
                    dwhcolumn.setStorageid(dwhtypetmp.getStorageid())
                    dwhcolumnF = DwhcolumnFactory(self.dwhrep, dwhcolumn)
                    for dwhcolumntmp in dwhcolumnF.get():
                        if dwhcolumntmp.getIncludesql() == 1:
                            containsView = True
                        dwhcolumntmp.deleteDB();

                    dwhpar = Dwhpartition(self.dwhrep)
                    dwhpar.setStorageid(dwhtypetmp.getStorageid())
                    dwhparF = DwhpartitionFactory(self.dwhrep, dwhpar)
                    for dwhpartmp in dwhparF.get():
                        self.dwhRock.getConnection().createStatement().execute("Drop table " + dwhpartmp.getTablename())
                        dwhpartmp.deleteDB()
                    
                    if dwhtypetmp.getViewtemplate() != None and len(dwhtypetmp.getViewtemplate()) != 0:
                        if dwhtypetmp.getTablelevel() == 'COUNT':
                            viewName = dwhtypetmp.getTypename() + '_DELTA'
                            self.dwhRock.getConnection().createStatement().execute("Drop view " + viewName)
                            
                        dwhTypeCond = Dwhtype(self.dwhrep)
                        dwhTypeCond.setTypename(dwhtypetmp.getTypename())
                        dwhTypeCond.setTablelevel('COUNT')
                        dwhTypeResult = DwhtypeFactory(self.dwhrep, dwhTypeCond) 
                        if dwhTypeResult != None and len(dwhTypeResult.get()) != 0:
                            if dwhtypetmp.getTablelevel() == 'RAW' or dwhtypetmp.getTablelevel() == 'COUNT':
                                viewName = dwhtypetmp.getBasetablename() + '_DISTINCT_DATES'
                                self.dwhRock.getConnection().createStatement().execute("Drop view " + viewName)
                        
                        self.dwhRock.getConnection().createStatement().execute("Drop view " + dwhtypetmp.getBasetablename())
                    
                    if dwhtypetmp.getPublicviewtemplate() != None and len(dwhtypetmp.getPublicviewtemplate()) != 0:
                        if containsView:
                            self.dbaDwhRock.getConnection().createStatement().execute("Drop view dcpublic." + dwhtypetmp.getBasetablename())

                    if dwhtypetmp.getTablelevel() == "DAYBH":
                        calcTableName = dwhtypetmp.getBasetablename() + "_CALC"
                        self.dwhRock.getConnection().createStatement().execute("Drop table " + calcTableName)
                     
                    dwhtypetmp.deleteDB()
    
                dwhtptmp.deleteDB();

            tpatmp.deleteDB()
            
            viewClauses = []
            mt_cond = Measurementtype(self.dwhrep)
            mt_cond.setVersionid(versionID)
            mt_condF = MeasurementtypeFactory(self.dwhrep, mt_cond)
            for mt in mt_condF.get():
                mobhs = Measurementobjbhsupport(self.dwhrep)

                mobhs.setTypeid(mt.getTypeid())
                mobhsF = MeasurementobjbhsupportFactory(self.dwhrep, mobhs)
                if mobhsF.get() != None and mobhsF.get().size() > 0:
                    for measObjbhs in mobhsF.get():
                        bhlevel = mt.getTypename()
                        bh_cond = Busyhour(self.dwhrep)
                        bh_cond.setVersionid(mt.getVersionid())
                        bh_cond.setBhlevel(bhlevel)
                        bh_cond.setBhobject(measObjbhs.getObjbhsupport())
                        bh_cond.setBhelement(0)
                        vc_condF = BusyhourFactory(self.dwhrep, bh_cond)
                        for bh in vc_condF.get():
                            name = mt.getTypename() + "_RANKBH_" + measObjbhs.getObjbhsupport() + "_" + bh.getBhtype()
                            viewClauses.append("DROP VIEW " + name)
                
                if mt.getElementbhsupport() != None and mt.getRankingtable() != None:
                    if mt.getElementbhsupport() > 0 and mt.getRankingtable() > 0:
                        bh_cond = Busyhour(self.dwhrep)
                        bh_cond.setVersionid(mt.getVersionid())
                        bh_cond.setBhelement(1)
                        vc_condF = BusyhourFactory(self.dwhrep, bh_cond)
                        for bh in vc_condF.get():
                            name = mt.getVendorid() + "_ELEMBH_RANKBH_" + bh.getBhobject() + "_" + bh.getBhtype()
                            viewClauses.append("DROP VIEW " + name)
                
                obj_bh = Busyhour(self.dwhrep)
                obj_bh.setVersionid(self.versionID)
                vc_condF = BusyhourFactory(self.dwhrep, obj_bh)
                for bh in vc_condF.get():
                    if bh.getVersionid() != bh.getTargetversionid():
                        name = None
                        if bh.getBhelement().equals(0):
                            name = bh.getBhlevel() + "_RANKBH_" + bh.getBhobject() + "_" + bh.getBhtype()
                        else:
                            v = Versioning(self.dwhrep, True)
                            v.setVersionid(bh.getTargetversionid())
                            vF = VersioningFactory(self.dwhrep, v, True)
                            targetTP = vF.get().elementAt(0)
                            name = targetTP.getTechpack_name() + "_ELEMBH_RANKBH_" + bh.getBhobject() + "_" + bh.getBhtype()
                        viewClauses.append("DROP VIEW " + name)
                        
            if len(viewClauses) > 0:
                for stmt in viewClauses:
                    try:
                        self.dwhRock.getConnection().createStatement().execute(stmt)
                    except:
                        print "Error : " + stmt+'\n'
                    
            mcs = Meta_collection_sets(self.etlrep)
            mcs.setCollection_set_name(tpatmp.getTechpack_name())
            mcs.setVersion_number(tpatmp.getVersionid().split(":")[1])
            mcsF = Meta_collection_setsFactory(self.etlrep, mcs)
            if mcsF.get() != None and mcsF.get().size() > 0:
                metacs = mcsF.getElementAt(0)
                mc = Meta_collections(self.etlrep)
                mc.setCollection_set_id(metacs.getCollection_set_id())
                mc.setVersion_number(tpatmp.getVersionid().split(":")[1])
                mcF = Meta_collectionsFactory(self.etlrep, mc)
                metaColls = mcF.get()
                for metac in metaColls:
                    metac.setEnabled_flag("N")
                    metac.saveDB()
                metacs.setEnabled_flag("N")
                metacs.saveDB()

    def activateTP(self, versionID, engine):
        from com.distocraft.dc5000.repository.dwhrep import Tpactivation
        from com.distocraft.dc5000.repository.dwhrep import TpactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Typeactivation
        from com.distocraft.dc5000.repository.dwhrep import TypeactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementvector
        from com.distocraft.dc5000.repository.dwhrep import MeasurementvectorFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementobjbhsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtable
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtableFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.dwhm import VersionUpdateAction
        from com.distocraft.dc5000.repository.cache import ActivationCache
        from com.distocraft.dc5000.repository.cache import PhysicalTableCache
        from com.distocraft.dc5000.dwhm import StorageTimeAction
        from com.distocraft.dc5000.dwhm import PartitionAction
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import BusyhourFactory
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from com.distocraft.dc5000.etl.rock import Meta_collections
        from com.distocraft.dc5000.etl.rock import Meta_collectionsFactory
               
        self.deactivateTP(versionID)
        
        newActivation = False
        targetTPActivation = Tpactivation(self.dwhrep)
        tpa = Tpactivation(self.dwhrep)
        tpa.setTechpack_name(self.Versioning.getTechpack_name())
        tpaF = TpactivationFactory(self.dwhrep, tpa)
        predecessorTPActivation = None
        if tpaF!=None and tpaF.size()>0:
            predecessorTPActivation = tpaF.getElementAt(0)
        if predecessorTPActivation != None:
            '''Update the previous installation of the tech pack.
            The new tech pack is the same as the old one, except the new versionid
            '''
            targetTPActivation = predecessorTPActivation
            targetTPActivation.setVersionid(self.Versioning.getVersionid())
            targetTPActivation.setModified(0)
            targetTPActivation.updateDB()
        else:
            ''''Insert the tech pack activation data.'''
            targetTPActivation.setTechpack_name(self.Versioning.getTechpack_name())
            targetTPActivation.setStatus("ACTIVE")
            targetTPActivation.setVersionid(self.Versioning.getVersionid())
            targetTPActivation.setType(self.Versioning.getTechpack_type())
            targetTPActivation.setModified(0)
            targetTPActivation.insertDB()
            newActivation = True
            
        typeActivations = {}
        
        '''First get the TypeActivations of type Measurement.
          Get all MeasurementTypes related to this VersionID.'''
        whereMeasurementType = Measurementtype(self.dwhrep)
        whereMeasurementType.setVersionid(targetTPActivation.getVersionid())
        meastypeFactory = MeasurementtypeFactory(self.dwhrep, whereMeasurementType)
        
        for targetMeasurementType in meastypeFactory.get():
            targetTypeId = targetMeasurementType.getTypeid()
            targetTypename = targetMeasurementType.getTypename()
            
            if targetMeasurementType.getJoinable() != None and len(targetMeasurementType.getJoinable()) != 0:
                uniqueName,typeActivation = self._populateTypeActivationObj(targetTypename + "_PREV", "Measurement", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),None, "PLAIN")
                typeActivations[uniqueName] = typeActivation
            
            if targetMeasurementType.getVectorsupport() != None and int(targetMeasurementType.getVectorsupport()) == 1:
                mv_cond = Measurementvector(self.dwhrep)
                mv_cond.setTypeid(targetMeasurementType.getTypeid())
                vc_condF = MeasurementvectorFactory(self.dwhrep, mv_cond)
                for vc in vc_condF.get():
                    typename = targetMeasurementType.getTypename().replace('DC','DIM')+ "_"+ vc.getDataname()
                    uniqueName,typeActivation = self._populateTypeActivationObj(typename, "Reference", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),None, "PLAIN")
                    if uniqueName not in typeActivations:
                        typeActivations[uniqueName] = typeActivation

            
            mobhs = Measurementobjbhsupport(self.dwhrep)
            mobhs.setTypeid(targetMeasurementType.getTypeid())
            mobhsF = MeasurementobjbhsupportFactory(self.dwhrep, mobhs)

            if targetMeasurementType.getElementbhsupport() != None and int(targetMeasurementType.getElementbhsupport()) == 1:
                '''replace DC_E_XXX with DIM_E_XXX_ELEMBH_BHTYPE'''
                typename = targetMeasurementType.getVendorid().replace('DC','DIM')+ "_ELEMBH_BHTYPE"
                '''Adding new ELEMBH table.'''
                uniqueName,typeActivation = self._populateTypeActivationObj(typename, "Reference", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),None, "PLAIN")
                if uniqueName not in typeActivations:
                    typeActivations[uniqueName] = typeActivation
                    
            if mobhsF != None and len(mobhsF.get()) == 0:
                '''replace DC_E_XXX_YYY with DIM_E_XXX_YYY_BHTYPE'''
                typename = targetMeasurementType.getTypename().replace('DC','DIM')+ "_BHTYPE";
                '''Adding new OBJBH table.'''
                uniqueName,typeActivation = self._populateTypeActivationObj(typename, "Reference", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),None, "PLAIN")
                if uniqueName not in typeActivations:
                    typeActivations[uniqueName] = typeActivation
                    
            whereMeasurementTable = Measurementtable(self.dwhrep)
            whereMeasurementTable.setTypeid(targetTypeId)
            measurementTableFactory = MeasurementtableFactory(self.dwhrep,whereMeasurementTable)
            for targetMeasurementTable in measurementTableFactory.get():
                targetTableLevel = targetMeasurementTable.getTablelevel()
                '''All the needed data is gathered from tables.
                  Add the Typeactivation of type Measurement to
                  typeActivations-vector to be saved later.'''
                uniqueName,typeActivation = self._populateTypeActivationObj(targetTypename, "Measurement", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),targetMeasurementTable.getPartitionplan(), targetTableLevel)
                if uniqueName not in typeActivations:
                    typeActivations[uniqueName] = typeActivation
                
            '''Next get the TypeActivations of type Reference.
              Get all ReferenceTables related to this VersionID.'''
            whereReferenceTable = Referencetable(self.dwhrep)
            whereReferenceTable.setVersionid(targetTPActivation.getVersionid())
            referenceTableFactory = ReferencetableFactory(self.dwhrep,whereReferenceTable)
            for targetReferenceTable in referenceTableFactory.get():
                typename = targetReferenceTable.getTypename()
                uniqueName,typeActivation = self._populateTypeActivationObj(typename, "Reference", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(),None, "PLAIN")
                if uniqueName not in typeActivations:
                    typeActivations[uniqueName] = typeActivation
                
                if targetReferenceTable.getUpdate_policy() != None:
                    if targetReferenceTable.getUpdate_policy() == 2 or targetReferenceTable.getUpdate_policy() == 3:
                        uniqueName,typeActivation = self._populateTypeActivationObj(typename + "_CURRENT_DC", "Reference", targetTPActivation.getTechpack_name(), targetTPActivation.getStatus(), None, "PLAIN")
                        if uniqueName not in typeActivations:
                            typeActivations[uniqueName] = typeActivation
            
        if newActivation:
            for uniqueName, typeActivation in typeActivations.iteritems():
                typeActivation.insertDB()
        else:
            whereTypeActivation = Typeactivation(self.dwhrep)
            whereTypeActivation.setTechpack_name(targetTPActivation.getTechpack_name())
            typeActivationRockFactory = TypeactivationFactory(self.dwhrep,whereTypeActivation)
            for currenttypeActivation in typeActivationRockFactory.get():
                uniqueName = currenttypeActivation.getTechpack_name() + "/" + currenttypeActivation.getTypename() + "/"+ currenttypeActivation.getTablelevel()
                if uniqueName in typeActivations:
                    currenttypeActivation.setPartitionplan(typeActivations[uniqueName].getPartitionplan())
                    currenttypeActivation.updateDB()
                    del typeActivations[uniqueName]
            for uniqueName, typeActivation in typeActivations.iteritems():
                typeActivation.insertDB()
        
        
        ''' For some reason the logger has to be passed into StorageTimeAction and ParitionAction.
        Had to create a dummy logger object to pass in otherwise it would throw null pointer exceptions when referencing the logger ''' 
        from java.util.logging import Logger
        from java.util.logging import Level
        logger = Logger.getLogger("TPAF")
        logger.setLevel(Level.ALL)
                 
        v = VersionUpdateAction(self.dwhrep, self.dwhrep, targetTPActivation.getTechpack_name(), logger)
        v.execute()
        ActivationCache.initialize(self.etlrep, self.dwhrep.getDbURL(), self.dwhrep.getUserName(), self.dwhrep.getPassword())
        
        try:
            PhysicalTableCache.initialize(self.etlrep, self.dwhrep.getDbURL(), self.dwhrep.getUserName(), self.dwhrep.getPassword(), self.dwhRock.getDbURL(), self.dwhRock.getUserName(), self.dwhRock.getPassword())
        except:
            PhysicalTableCache.initialize(self.etlrep, self.dwhrep.getDbURL(), self.dwhrep.getUserName(), self.dwhrep.getPassword())
               
        StorageTimeAction(self.dwhrep, self.etlrep,self.dwhRock, self.dbaDwhRock, targetTPActivation.getTechpack_name(), logger, True)
        PartitionAction(self.dwhrep, self.dwhRock, targetTPActivation.getTechpack_name(),logger)
        
        where = Busyhour(self.dwhrep)
        where.setVersionid(self.Versioning.getVersionid())
        where.setReactivateviews(1)
        fac = BusyhourFactory(self.dwhrep, where)
        for bhCheck in fac.get():
            bhCheck.setReactivateviews(0)
            bhCheck.updateDB()
            
        mcs = Meta_collection_sets(self.etlrep)
        mcs.setCollection_set_name(self.Versioning.getTechpack_name())
        mcs.setVersion_number(self.Versioning.getVersionid().split(":")[1])
        mcsF = Meta_collection_setsFactory(self.etlrep,mcs)
        
        mcF = None
        if mcsF != None and mcsF.get() != None and len(mcsF.get()) > 0:
            metacs = mcsF.getElementAt(0)
            mc = Meta_collections(self.etlrep)
            mc.setCollection_set_id(metacs.getCollection_set_id())
            mc.setVersion_number(self.Versioning.getVersionid().split(":")[1])
            mcF = Meta_collectionsFactory(self.etlrep, mc)
            for metac in mcF.get():
                metac.setEnabled_flag("Y")
                metac.saveDB()
            metacs.setEnabled_flag("Y")
            metacs.saveDB()
            
        techpack = self.Versioning.getTechpack_name()
        if techpack == 'AlarmInterfaces' or techpack == 'DC_Z_ALARM':
            for metac in mcF.get():
                collectionName = metac.getCollection_name()
                if collectionName.startsWith("Directory_Checker"):
                    try:
                        engine.rundirectoryCheckerSetForAlarmInterfaces(techpack, collectionName)
                    except:
                        print 'Directory Checker failed: '+ techpack + ' : ' + collectionName
        else:
            try:
                engine.rundirectoryCheckerSet(techpack)
            except:
                print 'Directory checker failed to run: ' + techpack
     
    
    def _populateTypeActivationObj(self, typename, type, techpackName, status, partition, tableLevel):
        from com.distocraft.dc5000.repository.dwhrep import Typeactivation
        preTypeActivation = Typeactivation(self.dwhrep)
        preTypeActivation.setTypename(typename)
        preTypeActivation.setTablelevel(tableLevel)
        preTypeActivation.setStoragetime(long(-1))
        preTypeActivation.setType(type)
        preTypeActivation.setTechpack_name(techpackName)
        preTypeActivation.setStatus(status)
        preTypeActivation.setPartitionplan(partition)
        uniqueName = preTypeActivation.getTechpack_name() + "/" + preTypeActivation.getTypename() + "/"+ preTypeActivation.getTablelevel()
        return uniqueName,preTypeActivation
    
    def deleteSets(self, techpackName, techpackVersion):
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from com.distocraft.dc5000.etl.rock import Meta_collections
        from com.distocraft.dc5000.etl.rock import Meta_collectionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actions
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_schedulings
        from com.distocraft.dc5000.etl.rock import Meta_schedulingsFactory
        
        rmcs = Meta_collection_sets(self.etlrep)
        rmcs.setCollection_set_name(techpackName)
        rmcs.setVersion_number(techpackVersion)
        rmcsF = Meta_collection_setsFactory(self.etlrep, rmcs)
        tp = rmcsF.getElementAt(0)
        if tp != None:
            collection_set_id = tp.getCollection_set_id()
            
            rmc = Meta_collections(self.etlrep);
            rmc.setCollection_set_id(collection_set_id)
            rmc.setVersion_number(techpackVersion)
            rmcF = Meta_collectionsFactory(self.etlrep, rmc)
            for m in rmcF.get():
                mta = Meta_transfer_actions(self.etlrep)
                mta.setCollection_id(m.getCollection_id())
                mta.setCollection_set_id(collection_set_id)
                mtaF = Meta_transfer_actionsFactory(self.etlrep, mta)
                for a in mtaF.get():
                    a.deleteDB()
                
                ms = Meta_schedulings(self.etlrep)
                ms.setCollection_id(m.getCollection_id())
                ms.setCollection_set_id(collection_set_id)
                msF = Meta_schedulingsFactory(self.etlrep, ms)
                for s in msF.get():
                    s.deleteDB()
                m.deleteDB()
            tp.deleteDB()
                
    
    def generateSets(self, versionID, vmpath):
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from java.util import Properties
        from org.apache.velocity.app import Velocity
        
        from java.util import Vector
        skiplist = Vector()
        
        vmPath = vmpath.split('Output')[0]+'Environment' 
        vmPath = vmPath.replace('\\','/')     
        
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        self.Versioning = Versioning(self.dwhrep, versionID)
        setName = self.Versioning.getTechpack_name()
        setVersion = self.Versioning.getVersionid().split(":")[1]
        
        mwhere = Meta_collection_sets(self.etlrep)
        mwhere.setCollection_set_name(setName)
        mwhere.setVersion_number(setVersion)
        mcsf = Meta_collection_setsFactory(self.etlrep,mwhere)
        
        metaCollectionSet = None
        if len(mcsf.get()) <= 0:
            csw = Meta_collection_sets(self.etlrep);
            csf = Meta_collection_setsFactory(self.etlrep, csw)
            largest = -1
            for mc in csf.get():
                if largest < mc.getCollection_set_id():
                    largest = mc.getCollection_set_id()
            
            metaCollectionSet = Meta_collection_sets(self.etlrep)
            metaCollectionSet.setCollection_set_id(long(float(largest+1)))
            metaCollectionSet.setCollection_set_name(setName)
            metaCollectionSet.setVersion_number(setVersion)
            ''' CONDITIONS FOR CUSTOM AND SYSTEM TP'S REMOVED. NOT SUPPORTED!! '''
            metaCollectionSet.setType("Techpack");
            metaCollectionSet.setDescription("TechPack " + setName + " " + setVersion + " by TPAF b")
            
            metaCollectionSet.setEnabled_flag("Y")
            metaCollectionSet.insertDB(False, False)
        else:
            metaCollectionSet = mcsf.get().get(0)
        
        Cs_id = metaCollectionSet.getCollection_set_id()
        Cs_name = metaCollectionSet.getCollection_set_name()
        
        try:
            from com.ericsson.eniq.common.setWizards import CreateDWHMSet
            cls = CreateDWHMSet(setName, setVersion, self.etlrep, long(float(Cs_id)), Cs_name, True)
            cls.removeSets()
            cls.create(False)
        except:
            pass
        
        cls = None
        try:
            from com.ericsson.eniq.common.setWizards import CreateLoaderSetFactory
            cls = CreateLoaderSetFactory.createLoaderSet("5.2", setName, setVersion, versionID, self.dwhrep, self.etlrep, int(Cs_id), Cs_name, True)
        except:
            from com.ericsson.eniq.common.setWizards import CreateLoaderSet
            cls = CreateLoaderSet("5.2", setName, setVersion, versionID, self.dwhrep, self.etlrep, int(Cs_id), Cs_name, True)
        
        cls.removeSets()
        cls.create(False)
        
        
        try:
            from com.ericsson.eniq.common.setWizards import CreateAggregatorSet
            cas = CreateAggregatorSet("5.2",setName, setVersion, versionID, self.dwhrep, self.etlrep, int(Cs_id), True)
            cas.removeSets()
            cas.create(False)
        except:
            pass
        
        
        cdc = None
        try:
            from com.ericsson.eniq.common.setWizards import CreateTPDirCheckerSetFactory
            cdc = CreateTPDirCheckerSetFactory.createTPDirCheckerSet(setName, setVersion, versionID, "Techpack", self.dwhrep, self.etlrep, long(float(Cs_id)), Cs_name)
        except:
            from com.ericsson.eniq.common.setWizards import CreateTPDirCheckerSet
            cdc = CreateTPDirCheckerSet(setName, setVersion, versionID, self.dwhrep, self.etlrep, long(float(Cs_id)), Cs_name)
        
        cdc.removeSets(True)
        cdc.create(True, False)
        
        
        try:
            from com.ericsson.eniq.common.setWizards import CreateTPDiskmanagerSet
            cdm = CreateTPDiskmanagerSet(setName, setVersion, self.etlrep, long(float(Cs_id)), Cs_name)
            cdm.removeSets()
            cdm.create(False, True)
        except:
            pass
        
        
        tls = None
        try:
            from com.ericsson.eniq.common.setWizards import CreateTopologyLoaderSetFactory
            tls = CreateTopologyLoaderSetFactory.createTopologyLoaderSet("5.2", setName, setVersion, versionID,self.dwhrep, self.etlrep, int(Cs_id), Cs_name, True)
        except:
            from com.ericsson.eniq.common.setWizards import CreateTopologyLoaderSet
            tls = CreateTopologyLoaderSet("5.2", setName, setVersion, versionID,self.dwhrep, self.etlrep, int(Cs_id), Cs_name, True)
        
        tls.removeSets(skiplist)
        tls.create(False)
          
    
    def createTPInstallFile(self, versionID, buildNumber, outputPath, encrypt):
        import shutil
        import os
        import zipfile
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import VersioningFactory
        from com.distocraft.dc5000.repository.dwhrep import Supportedvendorrelease
        from com.distocraft.dc5000.repository.dwhrep import SupportedvendorreleaseFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtypeclass
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeclassFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementkey
        from com.distocraft.dc5000.repository.dwhrep import MeasurementkeyFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcounter
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcounterFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementvector
        from com.distocraft.dc5000.repository.dwhrep import MeasurementvectorFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementdeltacalcsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementdeltacalcsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementobjbhsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtable
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtableFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcolumn
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import BusyhourFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourrankkeys
        from com.distocraft.dc5000.repository.dwhrep import BusyhourrankkeysFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhoursource
        from com.distocraft.dc5000.repository.dwhrep import BusyhoursourceFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourmapping
        from com.distocraft.dc5000.repository.dwhrep import BusyhourmappingFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourplaceholders
        from com.distocraft.dc5000.repository.dwhrep import BusyhourplaceholdersFactory
        from com.distocraft.dc5000.repository.dwhrep import Techpackdependency
        from com.distocraft.dc5000.repository.dwhrep import TechpackdependencyFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeclass
        from com.distocraft.dc5000.repository.dwhrep import UniverseclassFactory
        from com.distocraft.dc5000.repository.dwhrep import Verificationobject
        from com.distocraft.dc5000.repository.dwhrep import VerificationobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Verificationcondition
        from com.distocraft.dc5000.repository.dwhrep import VerificationconditionFactory
        from com.distocraft.dc5000.repository.dwhrep import Universetable
        from com.distocraft.dc5000.repository.dwhrep import UniversetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Universejoin
        from com.distocraft.dc5000.repository.dwhrep import UniversejoinFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeobject
        from com.distocraft.dc5000.repository.dwhrep import UniverseobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Universecomputedobject
        from com.distocraft.dc5000.repository.dwhrep import UniversecomputedobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeparameters
        from com.distocraft.dc5000.repository.dwhrep import UniverseparametersFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeformulas
        from com.distocraft.dc5000.repository.dwhrep import UniverseformulasFactory
        from com.distocraft.dc5000.repository.dwhrep import Universecondition
        from com.distocraft.dc5000.repository.dwhrep import UniverseconditionFactory
        from com.distocraft.dc5000.repository.dwhrep import Transformer
        from com.distocraft.dc5000.repository.dwhrep import TransformerFactory
        from com.distocraft.dc5000.repository.dwhrep import Transformation
        from com.distocraft.dc5000.repository.dwhrep import TransformationFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn
        from com.distocraft.dc5000.repository.dwhrep import ReferencecolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataformat
        from com.distocraft.dc5000.repository.dwhrep import DataformatFactory
        from com.distocraft.dc5000.repository.dwhrep import Defaulttags
        from com.distocraft.dc5000.repository.dwhrep import DefaulttagsFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataitem
        from com.distocraft.dc5000.repository.dwhrep import DataitemFactory
        from com.distocraft.dc5000.repository.dwhrep import Externalstatement
        from com.distocraft.dc5000.repository.dwhrep import ExternalstatementFactory
        from com.distocraft.dc5000.repository.dwhrep import Universename
        from com.distocraft.dc5000.repository.dwhrep import UniversenameFactory
        from com.distocraft.dc5000.repository.dwhrep import Aggregation
        from com.distocraft.dc5000.repository.dwhrep import AggregationFactory
        from com.distocraft.dc5000.repository.dwhrep import Aggregationrule
        from com.distocraft.dc5000.repository.dwhrep import AggregationruleFactory
        from com.distocraft.dc5000.etl.importexport import ETLCExport
        from org.apache.velocity import VelocityContext
        from org.apache.velocity.app import Velocity
        from org.apache.velocity.context import Context
        from org.apache.velocity.runtime.resource.loader import ClasspathResourceLoader
        from org.apache.velocity.app import VelocityEngine
        from org.apache.velocity.runtime import RuntimeConstants
        from java.util import Vector
        from java.io import StringWriter
        from java.util import Properties
        from tpapi.eniqInterface import VersionInfo
        
        self.Versioning = Versioning(self.dwhrep, versionID)
        basedir = outputPath
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        
        oldversion = self.Versioning.getVersionid().split(':')[1]
        newVersion = '(('+str(buildNumber)+'))'
        
        newBuildTag = self.Versioning.getTechpack_version() + '_b' + str(buildNumber)
        techpackName = self.Versioning.getTechpack_name()

        outputFileName = techpackName + '_' + newBuildTag + '.tpi'
        
        vmPath = outputPath.split('Output')[0]+'Environment' 
        vmPath = vmPath.replace('\\','/')     
        
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        #Create .xml file in set directory
        setDir = basedir+'\\set'
        if not os.path.exists(setDir):
            os.makedirs(setDir)
        setFile = open(setDir+'\\Tech_Pack_' + techpackName + '.xml','w')
        
        replaseStr = '#version#=' + oldversion + ',#techpack#=' + techpackName
        des = ETLCExport(None, self.etlrep.getConnection())
        
        filecontents = des.exportXml(replaseStr)
        filecontents = filecontents.getBuffer().toString().replace(oldversion, newVersion)
        setFile.write(filecontents)
        setFile.close()
        
        #Create install directory for version.properties and install.xml
        installDir = basedir+'\\install'
        if not os.path.exists(installDir):
            os.makedirs(installDir)
            
        installXml = open(installDir+'\\install.xml','w')   
        installXmlContent = self.Versioning.getInstalldescription()
        if installXmlContent != None and len(installXmlContent) > 0:
            installXml.write(installXmlContent)
        else:
            context = None
            vmFile = 'install.vm'
            if techpackName == 'AlarmInterfaces' or techpackName == 'DC_Z_ALARM':
                context = VelocityContext()
                context.put("configurationDirectory", "${configurationDirectory}")
                context.put("binDirectory", "${binDirectory}")
            if techpackName == 'AlarmInterfaces':
                vmFile = 'install_AlarmInterfaces.vm'
            elif techpackName == 'DC_Z_ALARM':
                vmFile = 'install_DC_Z_ALARM.vm'
            
            strw = StringWriter()
            isMergeOk = Velocity.mergeTemplate(vmFile, Velocity.ENCODING_DEFAULT, context, strw)
            if isMergeOk:
                installXml.write(strw.toString().encode('ascii', 'ignore'))
        installXml.close()
        
        versionProps = open(installDir+'\\version.properties','w')
        vec = Vector()
        context = VelocityContext()
        tpd = Techpackdependency(self.dwhrep)
        tpd.setVersionid(self.Versioning.getVersionid());
        tpdF = TechpackdependencyFactory(self.dwhrep, tpd)
        for t in tpdF.get():
            vi = VersionInfo()
            vi.setTechpackname(t.getTechpackname())
            vi.setVersion(t.getVersion())
            vec.add(vi)
        context.put("metadataversion", "3")
        context.put("techpackname", self.Versioning.getTechpack_name())
        context.put("author", self.Versioning.getLockedby())
        context.put("version", self.Versioning.getTechpack_version())
        context.put("buildnumber", str(buildNumber))
        context.put("buildtag", "")
        licenseName = ''
        if self.Versioning.getLicensename() != None:
            licenseName = self.Versioning.getLicensename()
        context.put("licenseName", licenseName)
        context.put("required_tech_packs", vec)
        
        strw = StringWriter()
        isMergeOk = Velocity.mergeTemplate('version.vm', Velocity.ENCODING_DEFAULT, context, strw)
        if isMergeOk:
            versionProps.write(strw.toString().encode('ascii', 'ignore'))
        versionProps.close()
        
        #Create .sql file in sql directory
        sqlDir = basedir+'\\sql'
        if not os.path.exists(sqlDir):
            os.makedirs(sqlDir)
        sqlFile = open(sqlDir+'\\Tech_Pack_' + techpackName + '.sql','w')
        
        #Versioning
        versioningF = VersioningFactory(self.dwhrep, self.Versioning)
        for ver in versioningF.get():
            sqlFile.write(ver.toSQLInsert().replace(oldversion,newVersion))
            
            #SupportedVendorReleases
            svr = Supportedvendorrelease(self.dwhrep)
            svr.setVersionid(self.Versioning.getVersionid())
            svrF = SupportedvendorreleaseFactory(self.dwhrep, svr)
            for svr in svrF.get():
                sqlFile.write(svr.toSQLInsert().replace(oldversion,newVersion))
                
            #MeasurementTypeClass
            measurementTypeClass = Measurementtypeclass(self.dwhrep)
            measurementTypeClass.setVersionid(self.Versioning.getVersionid())
            measurementTypeClassF = MeasurementtypeclassFactory(self.dwhrep, measurementTypeClass)
            for mtc in measurementTypeClassF.get():
                sqlFile.write(mtc.toSQLInsert().replace(oldversion,newVersion))
                
                #Measurementtype
                measurementtype = Measurementtype(self.dwhrep)
                measurementtype.setTypeclassid(mtc.getTypeclassid())
                measurementtype.setVersionid(mtc.getVersionid())
                measurementtypeF = MeasurementtypeFactory(self.dwhrep, measurementtype)
                for mt in measurementtypeF.get():
                    sqlFile.write(mt.toSQLInsert().replace(oldversion,newVersion))
                    
                    #Measurementkey
                    measurementkey = Measurementkey(self.dwhrep)
                    measurementkey.setTypeid(mt.getTypeid())
                    measurementkeyF = MeasurementkeyFactory(self.dwhrep,measurementkey)
                    for mk in measurementkeyF.get():
                        sqlFile.write(mk.toSQLInsert().replace(oldversion,newVersion))
                    
                    #Measurementcounter 
                    measurementcounter = Measurementcounter(self.dwhrep)
                    measurementcounter.setTypeid(mt.getTypeid())
                    measurementcounterF = MeasurementcounterFactory(self.dwhrep,measurementcounter)
                    for mc in measurementcounterF.get():
                        sqlFile.write(mc.toSQLInsert().replace(oldversion,newVersion))
                        
                    #MeasurementVector
                    measurementvector = Measurementvector(self.dwhrep)
                    measurementvector.setTypeid(mt.getTypeid())
                    measurementvectorF = MeasurementvectorFactory(self.dwhrep,measurementvector)
                    for mv in measurementvectorF.get():
                        sqlFile.write(mv.toSQLInsert().replace(oldversion,newVersion))
                    
                    #MeasurementDeltaCalcSupport   
                    measurementdeltacalcsupport = Measurementdeltacalcsupport(self.dwhrep)
                    measurementdeltacalcsupport.setTypeid(mt.getTypeid())
                    measurementdeltacalcsupportF = MeasurementdeltacalcsupportFactory(self.dwhrep, measurementdeltacalcsupport)
                    for mdcs in measurementdeltacalcsupportF.get():
                        sqlFile.write(mdcs.toSQLInsert().replace(oldversion,newVersion))
                    
                    #MeasurementObjBHSupport
                    measurementobjbhsupport = Measurementobjbhsupport(self.dwhrep)
                    measurementobjbhsupport.setTypeid(mt.getTypeid())
                    measurementobjbhsupportF = MeasurementobjbhsupportFactory(self.dwhrep, measurementobjbhsupport)
                    for mobs in measurementobjbhsupportF.get():
                        sqlFile.write(mobs.toSQLInsert().replace(oldversion,newVersion))
                    
                    #Measurementtable
                    measurementtable = Measurementtable(self.dwhrep)
                    measurementtable.setTypeid(mt.getTypeid())
                    measurementtableF = MeasurementtableFactory(self.dwhrep,measurementtable)
                    for mtt in measurementtableF.get():
                        sqlFile.write(mtt.toSQLInsert().replace(oldversion,newVersion))
                        
                        measurementcolumn = Measurementcolumn(self.dwhrep)
                        measurementcolumn.setMtableid(mtt.getMtableid())
                        measurementcolumnF = MeasurementcolumnFactory(self.dwhrep,measurementcolumn)
                        for mc in measurementcolumnF.get():
                            sqlFile.write(mc.toSQLInsert().replace(oldversion,newVersion))
                            
            #Busyhour
            bh = Busyhour(self.dwhrep)
            bh.setVersionid(self.Versioning.getVersionid())
            bhf = BusyhourFactory(self.dwhrep, bh)
            for bh in bhf.get():
                sqlFile.write(bh.toSQLInsert().replace(oldversion,newVersion))
            
            #BusyhourRankkeys
            bhrk = Busyhourrankkeys(self.dwhrep)
            bhrk.setVersionid(self.Versioning.getVersionid())
            bhrkF = BusyhourrankkeysFactory(self.dwhrep, bhrk)
            for bhrk in bhrkF.get():
                sqlFile.write(bhrk.toSQLInsert().replace(oldversion,newVersion))
                
            #BusyhourSource
            bhs = Busyhoursource(self.dwhrep)
            bhs.setVersionid(self.Versioning.getVersionid())
            bhsF = BusyhoursourceFactory(self.dwhrep, bhs)
            for bhs in bhsF.get():
                sqlFile.write(bhs.toSQLInsert().replace(oldversion,newVersion))
                
            #BusyhourMapping
            bhm = Busyhourmapping(self.dwhrep)
            bhm.setVersionid(self.Versioning.getVersionid())
            bhmF = BusyhourmappingFactory(self.dwhrep, bhm)
            for bhm in bhmF.get():
                sqlFile.write(bhm.toSQLInsert().replace(oldversion,newVersion))
                
            #BusyhourPlaceHolders
            bhph = Busyhourplaceholders(self.dwhrep)
            bhph.setVersionid(self.Versioning.getVersionid())
            bhphF = BusyhourplaceholdersFactory(self.dwhrep, bhph)
            for bhph in bhphF.get():
                sqlFile.write(bhph.toSQLInsert().replace(oldversion,newVersion))
                
            #TechPackDepedency
            tpd = Techpackdependency(self.dwhrep)
            tpd.setVersionid(self.Versioning.getVersionid())
            tpdF = TechpackdependencyFactory(self.dwhrep, tpd)
            for tpd in tpdF.get():
                sqlFile.write(tpd.toSQLInsert().replace(oldversion,newVersion))
            
            #UniverseClass
            uc = Universeclass(self.dwhrep)
            uc.setVersionid(self.Versioning.getVersionid())
            ucF = UniverseclassFactory(self.dwhrep, uc)
            for uc in ucF.get():
                sqlFile.write(uc.toSQLInsert().replace(oldversion,newVersion))
                
            #Verificationobject
            vo = Verificationobject(self.dwhrep)
            vo.setVersionid(self.Versioning.getVersionid())
            voF = VerificationobjectFactory(self.dwhrep, vo)
            for vo in voF.get():
                sqlFile.write(vo.toSQLInsert().replace(oldversion,newVersion)) 
                
            #VerificationConditions
            vc = Verificationcondition(self.dwhrep)
            vc.setVersionid(self.Versioning.getVersionid())
            vcF = VerificationconditionFactory(self.dwhrep, vc)
            for vc in vcF.get():
                sqlFile.write(vc.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseTable
            ut = Universetable(self.dwhrep)
            ut.setVersionid(self.Versioning.getVersionid())
            utF = UniversetableFactory(self.dwhrep, ut)
            for ut in utF.get():
                sqlFile.write(ut.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseJoin
            uj = Universejoin(self.dwhrep)
            uj.setVersionid(self.Versioning.getVersionid())
            ujF = UniversejoinFactory(self.dwhrep, uj)
            for uj in ujF.get():
                sqlFile.write(uj.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseObject
            uo = Universeobject(self.dwhrep)
            uo.setVersionid(self.Versioning.getVersionid())
            uoF = UniverseobjectFactory(self.dwhrep, uo)
            for uo in uoF.get():
                sqlFile.write(uo.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseComputedObject
            uco = Universecomputedobject(self.dwhrep)
            uco.setVersionid(self.Versioning.getVersionid())
            ucoF = UniversecomputedobjectFactory(self.dwhrep, uco)
            for uco in ucoF.get():
                sqlFile.write(uco.toSQLInsert().replace(oldversion,newVersion))
                
                #UniverseParameters
                up = Universeparameters(self.dwhrep)
                up.setVersionid(uco.getVersionid())
                up.setClassname(uco.getClassname())
                up.setObjectname(uco.getObjectname())
                up.setUniverseextension(uco.getUniverseextension())
                upF = UniverseparametersFactory(self.dwhrep, up)
                for up in upF.get():
                    sqlFile.write(up.toSQLInsert().replace(oldversion,newVersion))
                    
            #UniverseFormulas
            uf = Universeformulas(self.dwhrep)
            uf.setVersionid(self.Versioning.getVersionid())
            ufF = UniverseformulasFactory(self.dwhrep, uf)
            for uf in ufF.get():
                sqlFile.write(uf.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseCondition
            uc = Universecondition(self.dwhrep)
            uc.setVersionid(self.Versioning.getVersionid())
            ucF = UniverseconditionFactory(self.dwhrep, uc)
            for uc in ucF.get():
                sqlFile.write(uc.toSQLInsert().replace(oldversion,newVersion))
                
            #Transformer
            transformer = Transformer(self.dwhrep)
            transformer.setVersionid(self.Versioning.getVersionid())
            transformerF = TransformerFactory(self.dwhrep, transformer)
            for transformer in transformerF.get():
                sqlFile.write(transformer.toSQLInsert().replace(oldversion,newVersion))
                
                #Transformation
                transformation = Transformation(self.dwhrep)
                transformation.setTransformerid(transformer.getTransformerid())
                transformationF = TransformationFactory(self.dwhrep,transformation)
                for transformation in transformationF.get():
                    sqlFile.write(transformation.toSQLInsert().replace(oldversion,newVersion))
            
            #Referencetable
            referencetable = Referencetable(self.dwhrep)
            referencetable.setVersionid(self.Versioning.getVersionid())
            referencetableF = ReferencetableFactory(self.dwhrep,referencetable)
            for referencetable in referencetableF.get():
                sqlFile.write(referencetable.toSQLInsert().replace(oldversion,newVersion))
                
                #Referencecolumn
                referencecolumn = Referencecolumn(self.dwhrep)
                referencecolumn.setTypeid(referencetable.getTypeid())
                referencecolumnF = ReferencecolumnFactory(self.dwhrep,referencecolumn)
                for referencecolumn in referencecolumnF.get():
                    sqlFile.write(referencecolumn.toSQLInsert().replace(oldversion,newVersion))
            
            #Dataformat
            dataformat = Dataformat(self.dwhrep)
            dataformat.setVersionid(self.Versioning.getVersionid())
            dataformatF = DataformatFactory(self.dwhrep, dataformat)
            for dataformat in dataformatF.get():
                sqlFile.write(dataformat.toSQLInsert().replace(oldversion,newVersion))
                
                #Defaulttags
                defaulttags = Defaulttags(self.dwhrep)
                defaulttags.setDataformatid(dataformat.getDataformatid())
                defaulttagsF = DefaulttagsFactory(self.dwhrep, defaulttags)
                for defaulttags in defaulttagsF.get():
                    sqlFile.write(defaulttags.toSQLInsert().replace(oldversion,newVersion))
                
                #Dataitem
                dataitem = Dataitem(self.dwhrep)
                dataitem.setDataformatid(dataformat.getDataformatid())
                dataitemF = DataitemFactory(self.dwhrep, dataitem)
                for dataitem in dataitemF.get():
                    sqlFile.write(dataitem.toSQLInsert().replace(oldversion,newVersion))
                    
            #Externalstatement
            externalstatement = Externalstatement(self.dwhrep)
            externalstatement.setVersionid(self.Versioning.getVersionid())
            externalstatementF = ExternalstatementFactory(self.dwhrep,externalstatement)
            for externalstatement in externalstatementF.get():
                sqlFile.write(externalstatement.toSQLInsert().replace(oldversion,newVersion))
                
            #UniverseName
            universename = Universename(self.dwhrep)
            universename.setVersionid(self.Versioning.getVersionid())
            universenameF = UniversenameFactory(self.dwhrep, universename)
            for universename in universenameF.get():
                sqlFile.write(universename.toSQLInsert().replace(oldversion,newVersion))
                
            #Aggregation
            aggregation = Aggregation(self.dwhrep)
            aggregation.setVersionid(self.Versioning.getVersionid())
            aggregationF = AggregationFactory(self.dwhrep, aggregation)
            for aggregation in aggregationF.get():
                sqlFile.write(aggregation.toSQLInsert().replace(oldversion,newVersion))
                
                #Aggregationrule
                aggregationrule = Aggregationrule(self.dwhrep)
                aggregationrule.setAggregation(aggregation.getAggregation())
                aggregationrule.setVersionid(aggregation.getVersionid())
                aggregationruleF = AggregationruleFactory(self.dwhrep,aggregationrule)
                for aggregationrule in aggregationruleF.get():
                    sqlFile.write(aggregationrule.toSQLInsert().replace(oldversion,newVersion))
            
            try:  
                from com.distocraft.dc5000.repository.dwhrep import Grouptypes
                from com.distocraft.dc5000.repository.dwhrep import GrouptypesFactory    
                #GroupTypes
                gt = Grouptypes(self.dwhrep)
                gt.setVersionid(self.Versioning.getVersionid())
                gtf = GrouptypesFactory(self.dwhrep, gt)
                for gt in gtf.get():
                    sqlFile.write(gt.toSQLInsert().replace(oldversion,newVersion))
            except:
                pass
        
        sqlFile.close()
        
        Z = zipfile.ZipFile(basedir+'\\Unencrypted_'+outputFileName, 'w')
        directories = ['install','set','sql']
        for directory in directories:
            for dirpath,dirs,files in os.walk(basedir+'\\'+directory):
                for f in files:
                    if not f.endswith('.tpi'):
                        fn = os.path.join(dirpath, f)
                        Z.write(str(fn), str(directory+'\\'+f), zipfile.ZIP_DEFLATED)
        Z.close()
            
        dirs = os.listdir(basedir)
        for dir in dirs:
            if not dir.endswith('.tpi'):
                shutil.rmtree(basedir+'\\'+dir)
        
        if encrypt == 'True':
            shutil.copy(basedir+'\\Unencrypted_'+outputFileName, basedir+'\\'+outputFileName)
            TPAPI.encryptZipFile(basedir+'\\'+outputFileName)
        
    
    def _factTableBackgroundGeneration(self, MeasTyp, counters, keys):
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import Aggregation
        from com.distocraft.dc5000.repository.dwhrep import Aggregationrule
        
        createCountTable = False
        if self._verifyNotNone(MeasTyp, 'getDeltacalcsupport') == 1: 
            createCountTable = True
            deltacalbool = False
            if self._countOccuranceInDict(self.MeasDeltaCalcSupprt, MeasTyp.getTypeid()):
                for key, value in self.MeasDeltaCalcSupprt.iteritems():                    
                    keyParts = key.split(':')
                    typeid = keyParts[0] + ':' + keyParts[1]+ ':' + keyParts[2]
                    if MeasTyp.getTypeid() == typeid:
                        if value.getDeltacalcsupport() == 1:
                            deltacalbool = True
                createCountTable = deltacalbool
        
        if self._verifyNotNone(MeasTyp, 'getRankingtable') == 0:
            if self._verifyNotNone(MeasTyp, 'getPlaintable') == 1:
                self._createMeasurementInformation(MeasTyp, keys, counters,'PLAIN')
            elif self._verifyNotNone(MeasTyp, 'getMixedpartitionstable') == 1:
                self._createMeasurementInformation(MeasTyp, keys, counters, 'BIG_RAW')
                self._createMeasurementInformation(MeasTyp, keys, counters, 'RAW')
            else:
                self._createMeasurementInformation(MeasTyp, keys, counters, 'RAW')
                
            if self._verifyNotNone(MeasTyp, 'getTotalagg') == 1:
                self._createMeasurementInformation(MeasTyp, keys, counters, 'DAY')
                
            if self._countOccuranceInDict(self.MeasobjBHsupport, MeasTyp.getTypeid()):
                self._createMeasurementInformation(MeasTyp, keys, counters, 'DAYBH')
                
            if createCountTable:
                self._createMeasurementInformation(MeasTyp, keys, counters, 'COUNT')
                
        else:
            self._createMeasurementInformation(MeasTyp, keys, counters, 'RANKBH')
        
        aggdict = {}
        ruleID = 0
        #AGGREGATIONS
        if self._verifyNotNone(MeasTyp, 'getRankingtable') == 0:
            if self._verifyNotNone(MeasTyp, 'getTotalagg') == 1:
                if createCountTable:
                    aggdict['AGGREGATION'] = MeasTyp.getTypename()+'_COUNT'
                    aggdict['VERSIONID'] = self.Versioning.getVersionid()
                    aggdict['AGGREGATIONTYPE'] = 'TOTAL'
                    aggdict['AGGREGATIONSCOPE'] = 'COUNT'
                    Agg = self.populateObjectFromDict(Aggregation, aggdict)
                    Agg.insertDB()
                    
                aggdict = {}  
                aggdict['AGGREGATION'] = MeasTyp.getTypename()+'_DAY'
                aggdict['VERSIONID'] = self.Versioning.getVersionid()
                aggdict['AGGREGATIONTYPE'] = 'TOTAL'
                aggdict['AGGREGATIONSCOPE'] = 'DAY'
                Agg = self.populateObjectFromDict(Aggregation, aggdict)
                Agg.insertDB()
                
                aggdict = {}
                aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_DAY'
                aggdict['VERSIONID'] = self.Versioning.getVersionid()
                aggdict['RULEID'] = ruleID
                aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAY'
                aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                aggdict['TARGET_LEVEL'] = 'DAY'
                aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAY'
                aggdict['SOURCE_TYPE'] = MeasTyp.getTypename()
                aggdict['RULETYPE'] = 'TOTAL'
                aggdict['AGGREGATIONSCOPE'] = 'DAY'
                if createCountTable:
                    aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':COUNT'
                    aggdict['SOURCE_LEVEL'] = 'COUNT'
                    aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_COUNT'  
                else:
                    aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':RAW'
                    aggdict['SOURCE_LEVEL'] = 'RAW'
                    aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_RAW'
                Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                Agg.insertDB()
                ruleID = ruleID + 1
                
                for typeID, measobjbhsupport in self.MeasobjBHsupport.iteritems():
                    items = typeID.rsplit(':',1)
                    typeid = items[0]
                    if MeasTyp.getTypeid() == typeid:
                        bhtype = measobjbhsupport.getObjbhsupport()
                        
                        #Create DayBH aggregation
                        aggdict = {}  
                        aggdict['AGGREGATION'] = MeasTyp.getTypename()+'_DAYBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['AGGREGATIONTYPE'] = 'DAYBH'
                        aggdict['AGGREGATIONSCOPE'] = 'DAY'
                        Agg = self.populateObjectFromDict(Aggregation, aggdict)
                        Agg.insertDB()
    
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_DAYBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getTypename()
                        aggdict['RULETYPE'] = 'BHSRC'
                        aggdict['AGGREGATIONSCOPE'] = 'DAY'
                        if createCountTable:
                            #Create DayBH-Count aggregations rule (BHSRC)
                            aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':COUNT'
                            aggdict['SOURCE_LEVEL'] = 'COUNT'
                            aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_COUNT'
                        else:
                            #DayBH-Raw aggregation rule (BHSRC)
                            aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':RAW'
                            aggdict['SOURCE_LEVEL'] = 'RAW'
                            aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_RAW'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                        
                        #Create WeekBH aggregation
                        aggdict = {}  
                        aggdict['AGGREGATION'] = MeasTyp.getTypename()+'_WEEKBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['AGGREGATIONTYPE'] = 'DAYBH'
                        aggdict['AGGREGATIONSCOPE'] = 'WEEK'
                        Agg = self.populateObjectFromDict(Aggregation, aggdict)
                        Agg.insertDB()
                
                        #Create WeekBH-DayBH aggregation rules (DAYBHCLASS)
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_WEEKBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getTypename()
                        aggdict['SOURCE_LEVEL'] = 'DAYBH'
                        aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['RULETYPE'] = 'DAYBHCLASS_DAYBH'
                        aggdict['AGGREGATIONSCOPE'] = 'WEEK'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                        
                        #Create MonthBH aggregation
                        aggdict = {}  
                        aggdict['AGGREGATION'] = MeasTyp.getTypename()+'_MONTHBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['AGGREGATIONTYPE'] = 'DAYBH'
                        aggdict['AGGREGATIONSCOPE'] = 'MONTH'
                        Agg = self.populateObjectFromDict(Aggregation, aggdict)
                        Agg.insertDB()
                
                        #Create MonthBH-DayBH aggregation rule (DAYBHCLASS)
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_MONTHBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getTypename()
                        aggdict['SOURCE_LEVEL'] = 'DAYBH'
                        aggdict['SOURCE_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['RULETYPE'] = 'DAYBHCLASS_DAYBH'
                        aggdict['AGGREGATIONSCOPE'] = 'MONTH'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                        
                        #Create DayBH-RankBH aggregation : rule (RANKSRC)
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_DAYBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_MTABLEID'] = self.Versioning.getVersionid()+':'+MeasTyp.getVendorid()+'_'+bhtype+'BH:RANKBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH' 
                        aggdict['SOURCE_LEVEL'] = 'RANKBH'
                        aggdict['SOURCE_TABLE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH_RANKBH' 
                        aggdict['RULETYPE'] = 'RANKSRC'
                        aggdict['AGGREGATIONSCOPE'] = 'DAY'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                        
                        #Create Week-RankBH aggregation : rule (DAYBHCLASS)
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_WEEKBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_MTABLEID'] = self.Versioning.getVersionid()+':'+MeasTyp.getVendorid()+'_'+bhtype+'BH:RANKBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH' 
                        aggdict['SOURCE_LEVEL'] = 'RANKBH'
                        aggdict['SOURCE_TABLE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH_RANKBH' 
                        aggdict['RULETYPE'] = 'DAYBHCLASS'
                        aggdict['AGGREGATIONSCOPE'] = 'WEEK'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                        
                        #Create MonthBH-RankBH aggregation : rule (DAYBHCLASS)
                        aggdict = {}
                        aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_MONTHBH_'+bhtype
                        aggdict['VERSIONID'] = self.Versioning.getVersionid()
                        aggdict['RULEID'] = ruleID
                        aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':DAYBH'
                        aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
                        aggdict['TARGET_LEVEL'] = 'DAYBH'
                        aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_DAYBH'
                        aggdict['SOURCE_MTABLEID'] = self.Versioning.getVersionid()+':'+MeasTyp.getVendorid()+'_'+bhtype+'BH:RANKBH'
                        aggdict['SOURCE_TYPE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH' 
                        aggdict['SOURCE_LEVEL'] = 'RANKBH'
                        aggdict['SOURCE_TABLE'] = MeasTyp.getVendorid()+'_'+bhtype+'BH_RANKBH' 
                        aggdict['RULETYPE'] = 'DAYBHCLASS'
                        aggdict['AGGREGATIONSCOPE'] = 'MONTH'
                        Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
                        Agg.insertDB()
                        ruleID = ruleID + 1
                    
        if createCountTable:
            aggdict = {}
            aggdict['AGGREGATION'] = MeasTyp.getTypename() +'_COUNT'
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['RULEID'] = ruleID
            aggdict['TARGET_MTABLEID'] = MeasTyp.getTypeid()+':COUNT'
            aggdict['TARGET_TYPE'] = MeasTyp.getTypename()
            aggdict['TARGET_LEVEL'] = 'COUNT'
            aggdict['TARGET_TABLE'] = MeasTyp.getTypename() +'_COUNT'
            aggdict['SOURCE_MTABLEID'] = MeasTyp.getTypename()+':RAW'
            aggdict['SOURCE_TYPE'] = MeasTyp.getTypename() 
            aggdict['SOURCE_LEVEL'] = 'RAW'
            aggdict['SOURCE_TABLE'] = MeasTyp.getTypename()+'_RAW'
            aggdict['RULETYPE'] = 'COUNT'
            aggdict['AGGREGATIONSCOPE'] = 'DAY'
            Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
            Agg.insertDB()
            ruleID = ruleID + 1
                    
    def _countOccuranceInDict(self, dictionary, refid):
        for key, value in dictionary.iteritems():
            keyParts = key.split(':')
            typeid = keyParts[0] + ':' + keyParts[1]+ ':' + keyParts[2]
            if refid == typeid:
                return True
        return False
    
    def _createMeasurementInformation(self, MeasTyp, measurementkeys, measurementcounters, tablelevel):
        from com.distocraft.dc5000.repository.dwhrep import Measurementtable
        from com.distocraft.dc5000.repository.dwhrep import Measurementcolumn
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        
        mtableid = MeasTyp.getTypeid() + ':' + tablelevel
        measurementtable = Measurementtable(self.dwhrep, True)
        measurementtable.setMtableid(mtableid)
        measurementtable.setTypeid(MeasTyp.getTypeid())
        measurementtable.setTablelevel(tablelevel)
        measurementtable.setPartitionplan(MeasTyp.getSizing().lower() + '_' + tablelevel.lower())
        if tablelevel == 'PLAIN':
            measurementtable.setBasetablename(MeasTyp.getTypename())
        else:
            measurementtable.setBasetablename(MeasTyp.getTypename() + '_' + tablelevel)
        measurementtable.insertDB()
        
        col = 0
        for measurementkey in measurementkeys:
            col = col + 1
            measurementcolumn = Measurementcolumn(self.dwhrep)
            measurementcolumn.setMtableid(mtableid)
            measurementcolumn.setDataname(self._replaceNone(measurementkey.getDataname))
            measurementcolumn.setColnumber(col)
            measurementcolumn.setDatatype(self._replaceNone(measurementkey.getDatatype))
            measurementcolumn.setDatasize(self._replaceNone(measurementkey.getDatasize))
            measurementcolumn.setDatascale(self._replaceNone(measurementkey.getDatascale))
            measurementcolumn.setUniquevalue(self._replaceNone(measurementkey.getUniquevalue))
            measurementcolumn.setNullable(self._replaceNone(measurementkey.getNullable))
            measurementcolumn.setIndexes(self._replaceNone(measurementkey.getIndexes))
            measurementcolumn.setDescription(self._replaceNone(measurementkey.getDescription))
            if measurementkey.getDataid() == None or len(measurementkey.getDataid()) <1:
                measurementcolumn.setDataid(self._replaceNone(measurementkey.getDataname))
            else:
                measurementcolumn.setDataid(self._replaceNone(measurementkey.getDataid))
            measurementcolumn.setReleaseid(self._replaceNone(self.Versioning.getVersionid))
            measurementcolumn.setUniquekey(self._replaceNone(measurementkey.getUniquekey))
            measurementcolumn.setIncludesql(self._replaceNone(measurementkey.getIncludesql))
            measurementcolumn.setColtype("KEY")
            
            try:
                measurementcolumn.insertDB()
            except:
                print 'Attempt to input duplicate Measurementcolumn'
            
            
        baseVersioning = Versioning(self.dwhrep, self.Versioning.getBasedefinition())
        whereMeasurementcolumn = Measurementcolumn(self.dwhrep)
        whereMeasurementcolumn.setMtableid(baseVersioning.getVersionid() + ':' + tablelevel)
        mcF = MeasurementcolumnFactory(self.dwhrep, whereMeasurementcolumn, True)
        for publicColumn in mcF.get():
            col = col + 1
            measurementcolumn = Measurementcolumn(self.dwhrep)
            measurementcolumn.setMtableid(mtableid)
            measurementcolumn.setDataname(self._replaceNone(publicColumn.getDataname))
            measurementcolumn.setColnumber(col)
            measurementcolumn.setDatatype(self._replaceNone(publicColumn.getDatatype))
            measurementcolumn.setDatasize(self._replaceNone(publicColumn.getDatasize))
            measurementcolumn.setDatascale(self._replaceNone(publicColumn.getDatascale))
            measurementcolumn.setUniquevalue(self._replaceNone(publicColumn.getUniquevalue))
            measurementcolumn.setNullable(self._replaceNone(publicColumn.getNullable))
            measurementcolumn.setIndexes(self._replaceNone(publicColumn.getIndexes))
            measurementcolumn.setDescription(self._replaceNone(publicColumn.getDescription))
            measurementcolumn.setDataid(self._replaceNone(publicColumn.getDataid))
            measurementcolumn.setReleaseid(self._replaceNone(publicColumn.getReleaseid))
            measurementcolumn.setUniquekey(self._replaceNone(publicColumn.getUniquekey))
            measurementcolumn.setIncludesql(self._replaceNone(publicColumn.getIncludesql))
            measurementcolumn.setColtype("PUBLICKEY")
            measurementcolumn.insertDB()
                
        if tablelevel != 'RANKBH':
            for meascounter in measurementcounters:
                col = col + 1
                meascolumn = Measurementcolumn(self.dwhrep)
                meascolumn.setMtableid(mtableid)
                meascolumn.setDataname(self._replaceNone(meascounter.getDataname))
                meascolumn.setColnumber(col)
                meascolumn.setDatatype(self._replaceNone(meascounter.getDatatype))
                meascolumn.setDatasize(self._replaceNone(meascounter.getDatasize))
                meascolumn.setDatascale(self._replaceNone(meascounter.getDatascale))
                meascolumn.setUniquevalue(255)
                meascolumn.setNullable(1)
                meascolumn.setIndexes("")
                meascolumn.setDescription(self._replaceNone(meascounter.getDescription))
                if meascounter.getDataid() == None or len(meascounter.getDataid()) < 1:
                    meascolumn.setDataid(self._replaceNone(meascounter.getDataname))
                else:
                    meascolumn.setDataid(self._replaceNone(meascounter.getDataid))
                meascolumn.setReleaseid(self._replaceNone(self.Versioning.getVersionid))
                meascolumn.setUniquekey(0)
                meascolumn.setIncludesql(self._replaceNone(meascounter.getIncludesql))
                meascolumn.setColtype("COUNTER");
                meascolumn.insertDB()
            
    def refTableBackgroundGeneration(self):
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn
        from com.distocraft.dc5000.repository.dwhrep import ReferencecolumnFactory
        
        baseVersioning = Versioning(self.dwhrep, self.Versioning.getBasedefinition())
        techpack_type = self.Versioning.getTechpack_type() 
        if techpack_type != 'BASE_TECHPACK' and techpack_type != 'SYSTEM_TECHPACK':
            rt = Referencetable(self.dwhrep)
            rt.setVersionid(baseVersioning.getVersionid())
            rtF = ReferencetableFactory(self.dwhrep, rt)
            for tmpRT in rtF.get():
                if tmpRT.getObjectname() == '(DIM_RANKMT)_BHTYPE':
                    mt = Measurementtype(self.dwhrep)
                    mt.setVersionid(self.Versioning.getVersionid())
                    mtF = MeasurementtypeFactory(self.dwhrep, mt)
                    for tmpMT in mtF.get():
                        if tmpMT.getRankingtable() == 1:
                            typeName = tmpRT.getTypename().replace("(DIM_RANKMT)","DIM_" + tmpMT.getObjectname().replace("DC_", ""))
                            typeId = self.Versioning.getVersionid() + ":" + typeName
                            
                            newRT = Referencetable(self.dwhrep)
                            newRT.setTypeid(typeId)
                            newRT.setVersionid(self.Versioning.getVersionid())
                            newRT.setTypename(typeName)
                            newRT.setObjectid(typeId)
                            newRT.setObjectname(typeName)
                            newRT.setObjectversion(tmpRT.getObjectversion())
                            newRT.setObjecttype(tmpRT.getObjecttype())
                            newRT.setDescription(tmpRT.getDescription())
                            newRT.setStatus(tmpRT.getStatus())
                            newRT.setUpdate_policy(tmpRT.getUpdate_policy())
                            newRT.setTable_type(tmpRT.getTable_type())
                            newRT.setDataformatsupport(tmpRT.getDataformatsupport())
                            newRT.setBasedef(1);
                            newRT.insertDB()
                            
                            rc = Referencecolumn(self.dwhrep)
                            rc.setTypeid(tmpRT.getTypeid())
                            rcF = ReferencecolumnFactory(self.dwhrep, rc)
                            for tmpRC in rcF.get():
                                newRC = Referencecolumn(self.dwhrep)
                                newRC.setTypeid(typeId)
                                newRC.setDataname(tmpRC.getDataname())
                                newRC.setColnumber(tmpRC.getColnumber())
                                newRC.setDatatype(tmpRC.getDatatype())
                                newRC.setDatasize(tmpRC.getDatasize())
                                newRC.setDatascale(tmpRC.getDatascale())
                                newRC.setUniquevalue(tmpRC.getUniquevalue())
                                newRC.setNullable(tmpRC.getNullable())
                                newRC.setIndexes(tmpRC.getIndexes())
                                newRC.setUniquekey(tmpRC.getUniquekey())
                                newRC.setIncludesql(tmpRC.getIncludesql())
                                newRC.setIncludeupd(tmpRC.getIncludeupd())
                                newRC.setColtype('PUBLICCOL')
                                newRC.setDescription(tmpRC.getDescription())
                                newRC.setUniverseclass(tmpRC.getUniverseclass())
                                newRC.setUniverseobject(tmpRC.getUniverseobject())
                                newRC.setUniversecondition(tmpRC.getUniversecondition())
                                newRC.setDataid(tmpRC.getDataid())
                                newRC.setBasedef(1)
                                newRC.insertDB()
                        
                elif tmpRT.getObjectname() == 'SELECT_(TPNAME)_AGGLEVEL':
                    typeName = tmpRT.getTypename().replace("(TPNAME)",self.Versioning.getTechpack_name().replace("DC_", ""))
                    typeId = self.Versioning.getVersionid() + ":" + typeName
                    
                    newRT = Referencetable(self.dwhrep)
                    newRT.setTypeid(typeId)
                    newRT.setVersionid(self.Versioning.getVersionid())
                    newRT.setTypename(typeName)
                    newRT.setObjectid(typeId)
                    newRT.setObjectname(typeName)
                    newRT.setObjectversion(tmpRT.getObjectversion())
                    newRT.setObjecttype(tmpRT.getObjecttype())
                    newRT.setDescription(tmpRT.getDescription())
                    newRT.setStatus(tmpRT.getStatus())
                    newRT.setUpdate_policy(tmpRT.getUpdate_policy())
                    newRT.setTable_type(tmpRT.getTable_type())
                    newRT.setDataformatsupport(tmpRT.getDataformatsupport())
                    newRT.setBasedef(1)
                    newRT.insertDB()

                elif tmpRT.getObjectname() == 'PUBLIC_REFTYPE':
                    tmpRcList = []
                    rc = Referencecolumn(self.dwhrep)
                    rc.setTypeid(tmpRT.getTypeid())
                    rcF = ReferencecolumnFactory(self.dwhrep, rc, "ORDER BY COLNUMBER")
                    for tmpRC in rcF.get():
                        tmpRcList.append(tmpRC)
                    
                    rt = Referencetable(self.dwhrep)
                    rt.setVersionid(self.Versioning.getVersionid())
                    rtF = ReferencetableFactory(self.dwhrep, rt)
                    for tmpnewRT in rtF.get():
                        if tmpnewRT.getBasedef() == None or (tmpnewRT.getBasedef() != None and tmpnewRT.getBasedef() != 1):
                            if tmpnewRT.getUpdate_policy() == 2 or tmpnewRT.getUpdate_policy() == 3 or tmpnewRT.getUpdate_policy() == 4:
                                colNumber = 0
                                rc2 = Referencecolumn(self.dwhrep)
                                rc2.setTypeid(tmpnewRT.getTypeid())
                                rcF2 = ReferencecolumnFactory(self.dwhrep, rc2)
                                colNumber = len(rcF2.get()) + 100
                                
                                for tmpRC in tmpRcList:
                                    colNumber = colNumber + 1
                                    
                                    newRC = Referencecolumn(self.dwhrep)
                                    newRC.setTypeid(tmpnewRT.getTypeid())
                                    newRC.setDataname(tmpRC.getDataname())
                                    newRC.setColnumber(colNumber)
                                    newRC.setDatatype(tmpRC.getDatatype())
                                    newRC.setDatasize(tmpRC.getDatasize())
                                    newRC.setDatascale(tmpRC.getDatascale())
                                    newRC.setUniquevalue(tmpRC.getUniquevalue())
                                    newRC.setNullable(tmpRC.getNullable())
                                    newRC.setIndexes(tmpRC.getIndexes())
                                    newRC.setUniquekey(tmpRC.getUniquekey())
                                    newRC.setIncludesql(tmpRC.getIncludesql())
                                    newRC.setIncludeupd(tmpRC.getIncludeupd())
                                    newRC.setColtype("PUBLICCOL")
                                    newRC.setDescription(tmpRC.getDescription())
                                    newRC.setUniverseclass(tmpRC.getUniverseclass())
                                    newRC.setUniverseobject(tmpRC.getUniverseobject())
                                    newRC.setUniversecondition(tmpRC.getUniversecondition())
                                    newRC.setDataid(tmpRC.getDataid())
                                    newRC.setBasedef(1)
                                    newRC.insertDB()
    
    def BusyHourBackgroundGeneration(self):
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import Busyhoursource
        from com.distocraft.dc5000.repository.dwhrep import Aggregation
        from com.distocraft.dc5000.repository.dwhrep import Aggregationrule
        
        aggdict = {}
        for key,value in self.BusyHour.iteritems():
            aggdict['AGGREGATION'] = value.getBhlevel()+'_RANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['AGGREGATIONTYPE'] = 'RANKBH'
            aggdict['AGGREGATIONSCOPE'] = 'DAY'
            Agg = self.populateObjectFromDict(Aggregation, aggdict)
            Agg.insertDB()
            
            aggdict = {}
            aggdict['AGGREGATION'] = value.getBhlevel()+'_RANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['RULEID'] = 0            
            aggdict['RULETYPE'] = 'RANKBH'
            aggdict['TARGET_TYPE'] = value.getBhlevel()
            aggdict['TARGET_LEVEL'] = 'RANKBH'
            aggdict['TARGET_TABLE'] = value.getBhlevel() +'_RANKBH'
            aggdict['TARGET_MTABLEID'] = self.Versioning.getVersionid()+':'+value.getBhlevel()+':RANKBH'
            aggdict['SOURCE_TABLE'] = value.getBhlevel()+'_RANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['SOURCE_TYPE'] = ''
            aggdict['SOURCE_LEVEL'] = ''
            aggdict['SOURCE_MTABLEID'] = ''
            aggdict['AGGREGATIONSCOPE'] = 'DAY'
            aggdict['BHTYPE'] = value.getBhobject()+"_"+value.getBhtype()
            aggdict['ENABLE'] = value.getEnable()
            
            bhSourceFlag = 0
            for key1 in self.BusyHourSource.iterkeys():
                KEY = key1.rsplit(':',1)[0]
                Source_table = key1.rsplit(':',1)[1]
                if bhSourceFlag != 1:
                    if key == KEY:
                        aggdict['SOURCE_TYPE'] = Source_table.rsplit('_',1)[0]
                        aggdict['SOURCE_LEVEL'] = Source_table.rsplit('_',1)[1]
                        aggdict['SOURCE_MTABLEID']= self.Versioning.getVersionid()+':'+Source_table.rsplit('_',1)[0]+':'+Source_table.rsplit('_',1)[1]
                        bhSourceFlag = 1
                    else:
                        aggdict['SOURCE_TYPE'] = ''
                        aggdict['SOURCE_LEVEL'] = ''
                        aggdict['SOURCE_MTABLEID']= ''
                        bhSourceFlag = 1
                        
            Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
            Agg.insertDB()

        aggdict = {}
        for key,value in self.BusyHour.iteritems():
            aggdict['AGGREGATION'] = value.getBhlevel()+'_WEEKRANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['AGGREGATIONTYPE'] = 'RANKBH'
            aggdict['AGGREGATIONSCOPE'] = 'WEEK'
            Agg = self.populateObjectFromDict(Aggregation, aggdict)
            Agg.insertDB()
            
            aggdict = {}
            aggdict['AGGREGATION'] = value.getBhlevel()+'_WEEKRANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['RULEID'] = 1
            aggdict['RULETYPE'] = 'RANKBHCLASS'
            aggdict['TARGET_TYPE'] = value.getBhlevel()
            aggdict['TARGET_LEVEL'] = 'RANKBH'
            aggdict['TARGET_TABLE'] = value.getBhlevel() +'_RANKBH'
            aggdict['TARGET_MTABLEID'] = self.Versioning.getVersionid()+':'+value.getBhlevel()+':RANKBH'
            aggdict['SOURCE_TYPE'] = value.getBhlevel()
            aggdict['SOURCE_LEVEL'] = 'RANKBH'
            aggdict['SOURCE_MTABLEID']= self.Versioning.getVersionid()+':'+value.getBhlevel()+':RANKBH'
            aggdict['SOURCE_TABLE'] = value.getBhlevel() +'_RANKBH'
            aggdict['AGGREGATIONSCOPE'] = 'WEEK'
            aggdict['BHTYPE'] = value.getBhobject()+"_"+value.getBhtype()
            aggdict['ENABLE'] = value.getEnable()
            Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
            Agg.insertDB()

        aggdict = {}     
        for key,value in self.BusyHour.iteritems():
            aggdict['AGGREGATION'] = value.getBhlevel()+'_MONTHRANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['AGGREGATIONTYPE'] = 'RANKBH'
            aggdict['AGGREGATIONSCOPE'] = 'MONTH'
            Agg = self.populateObjectFromDict(Aggregation, aggdict)
            Agg.insertDB()      
            
            aggdict = {}
            aggdict['AGGREGATION'] = value.getBhlevel()+'_MONTHRANKBH_'+value.getBhobject()+"_"+value.getBhtype()
            aggdict['VERSIONID'] = self.Versioning.getVersionid()
            aggdict['RULEID'] = 2
            aggdict['RULETYPE'] = 'RANKBHCLASS'
            aggdict['TARGET_TYPE'] = value.getBhlevel()
            aggdict['TARGET_LEVEL'] = 'RANKBH'
            aggdict['TARGET_TABLE'] = value.getBhlevel() +'_RANKBH'
            aggdict['TARGET_MTABLEID'] = self.Versioning.getVersionid()+':'+value.getBhlevel()+':RANKBH'
            aggdict['SOURCE_TYPE'] = value.getBhlevel()
            aggdict['SOURCE_LEVEL'] = 'RANKBH'
            aggdict['SOURCE_MTABLEID']= self.Versioning.getVersionid()+':'+value.getBhlevel()+':RANKBH'
            aggdict['SOURCE_TABLE'] = value.getBhlevel() +'_RANKBH'
            aggdict['AGGREGATIONSCOPE'] = 'MONTH'
            aggdict['BHTYPE'] = value.getBhobject()+"_"+value.getBhtype()
            aggdict['ENABLE'] = value.getEnable()
            Agg = self.populateObjectFromDict(Aggregationrule, aggdict)
            Agg.insertDB()
    
                                                                                                                                        
    def _populateDataItem(self):
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataformat
        from com.distocraft.dc5000.repository.dwhrep import Dataitem
        from com.distocraft.dc5000.repository.dwhrep import Measurementcolumn
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.repository.dwhrep import ReferencecolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn
        
        mt = Measurementtype(self.dwhrep)
        mt.setVersionid(self.Versioning.getVersionid())
        mt.setDataformatsupport(1)
        mtF = MeasurementtypeFactory(self.dwhrep, mt)
        for mtype in mtF.get():
            for dataformatID, attrTags in self.AttributeTags.iteritems():
                items = dataformatID.rsplit(':',1)
                typeID = items[0]
                dataformattype = items[1]
                if mtype.getTypeid() == typeID:
                    df = Dataformat(self.dwhrep)
                    df.setDataformatid(dataformatID)
                    df.setTypeid(mtype.getTypeid())
                    df.setVersionid(mtype.getVersionid())
                    df.setObjecttype('Measurement')
                    df.setFoldername(mtype.getTypename())
                    df.setDataformattype(dataformattype)
                    df.insertDB()
                    
                    mc = Measurementcolumn(self.dwhrep)
                    mc.setMtableid(mtype.getTypeid() + ':RAW')
                    mcF = MeasurementcolumnFactory(self.dwhrep, mc)
                    for mcol in mcF.get(): 
                        di = Dataitem(self.dwhrep)
                        di.setDataformatid(dataformatID)
                        di.setDataname(mcol.getDataname())
                        di.setColnumber(mcol.getColnumber())
                        if mcol.getDataname() in attrTags:
                            di.setDataid(attrTags[mcol.getDataname()])
                        else:
                            di.setDataid(mcol.getDataid())
                        di.setProcess_instruction(self._getProcessInstructions(mcol.getDataname(), typeID))
                        di.setDatatype(mcol.getDatatype())
                        di.setDatasize(mcol.getDatasize())
                        di.setDatascale(mcol.getDatascale())
                        di.insertDB()
                        
        rt = Referencetable(self.dwhrep)
        rt.setVersionid(self.Versioning.getVersionid())
        rt.setDataformatsupport(1)
        rtF = ReferencetableFactory(self.dwhrep, rt)
        for rtype in rtF.get():
            for dataformatID, attrTags in self.AttributeTags.iteritems():
                items = dataformatID.rsplit(':',1)
                typeID = items[0]
                dataformattype = items[1]
                if rtype.getTypeid() == typeID:
                    df = Dataformat(self.dwhrep)
                    df.setDataformatid(dataformatID)
                    df.setTypeid(rtype.getTypeid())
                    df.setVersionid(rtype.getVersionid())
                    df.setObjecttype('Reference')
                    df.setFoldername(rtype.getObjectname())
                    df.setDataformattype(dataformattype)
                    df.insertDB()
                    
                    rc = Referencecolumn(self.dwhrep)
                    rc.setTypeid(rtype.getTypeid())
                    rcF = ReferencecolumnFactory(self.dwhrep, rc)
                    for rcol in rcF.get():
                        di = Dataitem(self.dwhrep)
                        di.setDataformatid(dataformatID)
                        di.setDataname(rcol.getDataname())
                        di.setColnumber(rcol.getColnumber())
                        if rcol.getDataname() in attrTags:
                            di.setDataid(attrTags[rcol.getDataname()])
                        else:
                            di.setDataid(rcol.getDataname())
                        di.setProcess_instruction(self._getProcessInstructions(rcol.getDataname(), typeID))
                        di.setDatatype(rcol.getDatatype())
                        di.setDatasize(rcol.getDatasize())
                        di.setDatascale(rcol.getDatascale())
                        di.insertDB()
    
    def _getProcessInstructions(self, dataName, typeID):
        if dataName.upper() == 'DCVECTOR_INDEX':
            return ''
        if typeID+':'+dataName in self.MeasKeys:
            return 'key'
        if typeID+':'+dataName in self.MeasCounts:
            return self.MeasCounts[typeID+':'+dataName].getCountertype()
        return ''
    
    def _createBaseExternalStatements(self, ExecOrder):
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import Externalstatement
        from com.distocraft.dc5000.repository.dwhrep import ExternalstatementFactory
        
        baseVersioning = Versioning(self.dwhrep, self.Versioning.getBasedefinition())
        baseVersionId = baseVersioning.getVersionid()
        
        es = Externalstatement(self.dwhrep)
        es.setVersionid(baseVersionId)
        esF = ExternalstatementFactory(self.dwhrep, es, 'ORDER BY EXECUTIONORDER')
        for tmpEs in esF.get():
            if tmpEs.getExecutionorder() > 0:
                
                statementName = tmpEs.getStatementname()
                statement = tmpEs.getStatement()
                ExecOrder = ExecOrder + 1
                
                if tmpEs.getStatementname() == 'create view SELECT_(((TPName)))_AGGLEVEL':
                    tpName = self.Versioning.getTechpack_name().replace('DC_', '')
                    statementName = statementName.replace('(((TPName)))', tpName);
                    statement = statement.replace('(((TPName)))', tpName)
                
                tmpDict = {}
                tmpDict['VERSIONID'] = self.Versioning.getVersionid()
                tmpDict['STATEMENTNAME'] = statementName
                tmpDict['EXECUTIONORDER'] = ExecOrder
                tmpDict['DBCONNECTION'] = tmpEs.getDbconnection()
                tmpDict['STATEMENT'] = statement
                tmpDict['BASEDEF'] = 1
                ES = self.populateObjectFromDict(Externalstatement, tmpDict)
                ES.saveDB()
                
        return ExecOrder
            
        
    def populateObjectFromDict(self, Object, Dict):
        obj = Object(self.dwhrep, True)       
        items = dir(Object)
        for i in items:
            if i.startswith('set'):
                propertyName = i.split('set', 1)[1].upper()
                if propertyName in Dict:
                    propertyType = str(vars(Object)[i.split('set', 1)[1].lower()]).split(' ')[3].split('.')[2]
                    value = Dict[propertyName]
                    if value != None:
                        if propertyType == 'String':
                            value = value.strip()
                        elif propertyType == 'Integer':
                            if value == '' or value == '0':
                                value = 0
                            else:
                                value = int(value)
                        elif propertyType == 'Long':
                            value = long(value)
                        elif propertyType == 'Timestamp':
                            from java.sql import Timestamp
                            value = Timestamp.valueOf(value)
                        getattr(obj,i)(value)
        return obj
    
    def insertToDB(self):
        self.Versioning.insertDB()
        for key, value in self.TechPackDependency.iteritems():
            value.insertDB()
        for Release in self.SupportedVendorReleases:
            Release.insertDB()
        for key, value in self.MeasTypeClass.iteritems():
            value.insertDB()
            
        for key, value in self.MeasTypes.iteritems():
            value.insertDB()
            counters = []
            keys = []

            for counterkey, countervalue in self.MeasCounts.iteritems():
                items = counterkey.rsplit(':',1)
                typeid = items[0]
                if key == typeid:
                    countervalue.insertDB()
                    counters.append(countervalue)
                    
            for keyname, keyvalue in self.MeasKeys.iteritems():
                items = keyname.rsplit(':',1)
                typeid = items[0]
                if key == typeid:
                    keyvalue.insertDB()
                    keys.append(keyvalue)

            self._factTableBackgroundGeneration(value, counters, keys)
 
        for key, value in self.MeasobjBHsupport.iteritems():
            value.insertDB()
        for key, value in self.MeasDeltaCalcSupprt.iteritems():
            if value.getDeltacalcsupport() == 0:
                value.insertDB()
        for key, value in self.MeasVectors.iteritems():
            value.insertDB()

        ExecOrder = 0
        ExecOrder = self._createBaseExternalStatements(ExecOrder) 
        for order in sorted(self.ExternalStatements.keys()):
            difference = 0
            value = self.ExternalStatements[order]
            if value.getExecutionorder() <= ExecOrder:
                difference = ExecOrder - value.getExecutionorder()
                ExecOrder = value.getExecutionorder() + difference + 1
            value.setExecutionorder(ExecOrder)
            value.insertDB()
        
        for key,value in self.BusyHour.iteritems():
            value.insertDB()
        
        for key,value in self.BusyHourMapping.iteritems():
            value.insertDB()
      
        for key,value in self.BusyHourPlaceholders.iteritems():
            value.insertDB()

        for key,value in self.BusyHourSource.iteritems():
            value.insertDB()
        
        for key,value in self.BusyHourRankkeys.iteritems():
            value.insertDB()
        
        self.BusyHourBackgroundGeneration()

        for key, value in self.RefTables.iteritems():
            value.insertDB()
            for keyname, keyvalue in self.RefKeys.iteritems():
                items = keyname.rsplit(':',1)
                typeid = items[0]
                if key == typeid:
                    keyvalue.insertDB()
        
        self.refTableBackgroundGeneration()
                    
        for key, value in self.Transformer.iteritems():
            value.insertDB()  
        for key, value in self.Transformation.iteritems():
            value.insertDB() 

        self._populateDataItem()
        
        for defaultTag in self.DefaultTags:
            defaultTag.insertDB()
            
        for key, value in self.Universenames.iteritems():
            value.insertDB()
        for key, value in self.Universetables.iteritems():
            value.insertDB()
        for key, value in self.Universeclasses.iteritems():
            value.insertDB()
        for key, value in self.Universeobjects.iteritems():
            value.insertDB()
        for key, value in self.Universeconditions.iteritems():
            value.insertDB()
        for key, value in self.Universejoins.iteritems():
            value.insertDB()

        for key, value in self.Universecomputedobjects.iteritems():
            value.insertDB()
        for key, value in self.Universeformulas.iteritems():
            value.insertDB()
        for key, value in self.Universeparameters.iteritems():
            value.insertDB()
 
        for key, value in self.Verificationobjects.iteritems():
            value.insertDB()
        for key, value in self.Verificationconditions.iteritems():
            value.insertDB()
            
        #raise Exception('DELIBERATE EXCEPTION')
            
     
    def deleteFromDB(self, versionid):
        from com.distocraft.dc5000.repository.dwhrep import Tpactivation
        from com.distocraft.dc5000.repository.dwhrep import TpactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import VersioningFactory
        from com.distocraft.dc5000.repository.dwhrep import Supportedvendorrelease
        from com.distocraft.dc5000.repository.dwhrep import SupportedvendorreleaseFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtypeclass
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeclassFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementkey
        from com.distocraft.dc5000.repository.dwhrep import MeasurementkeyFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcounter
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcounterFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementvector
        from com.distocraft.dc5000.repository.dwhrep import MeasurementvectorFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementdeltacalcsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementdeltacalcsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementobjbhsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtable
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtableFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcolumn
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import BusyhourFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourrankkeys
        from com.distocraft.dc5000.repository.dwhrep import BusyhourrankkeysFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhoursource
        from com.distocraft.dc5000.repository.dwhrep import BusyhoursourceFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourmapping
        from com.distocraft.dc5000.repository.dwhrep import BusyhourmappingFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourplaceholders
        from com.distocraft.dc5000.repository.dwhrep import BusyhourplaceholdersFactory
        from com.distocraft.dc5000.repository.dwhrep import Techpackdependency
        from com.distocraft.dc5000.repository.dwhrep import TechpackdependencyFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeclass
        from com.distocraft.dc5000.repository.dwhrep import UniverseclassFactory
        from com.distocraft.dc5000.repository.dwhrep import Verificationobject
        from com.distocraft.dc5000.repository.dwhrep import VerificationobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Verificationcondition
        from com.distocraft.dc5000.repository.dwhrep import VerificationconditionFactory
        from com.distocraft.dc5000.repository.dwhrep import Universetable
        from com.distocraft.dc5000.repository.dwhrep import UniversetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Universejoin
        from com.distocraft.dc5000.repository.dwhrep import UniversejoinFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeobject
        from com.distocraft.dc5000.repository.dwhrep import UniverseobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Universecomputedobject
        from com.distocraft.dc5000.repository.dwhrep import UniversecomputedobjectFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeparameters
        from com.distocraft.dc5000.repository.dwhrep import UniverseparametersFactory
        from com.distocraft.dc5000.repository.dwhrep import Universeformulas
        from com.distocraft.dc5000.repository.dwhrep import UniverseformulasFactory
        from com.distocraft.dc5000.repository.dwhrep import Universecondition
        from com.distocraft.dc5000.repository.dwhrep import UniverseconditionFactory
        from com.distocraft.dc5000.repository.dwhrep import Transformer
        from com.distocraft.dc5000.repository.dwhrep import TransformerFactory
        from com.distocraft.dc5000.repository.dwhrep import Transformation
        from com.distocraft.dc5000.repository.dwhrep import TransformationFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn
        from com.distocraft.dc5000.repository.dwhrep import ReferencecolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataformat
        from com.distocraft.dc5000.repository.dwhrep import DataformatFactory
        from com.distocraft.dc5000.repository.dwhrep import Defaulttags
        from com.distocraft.dc5000.repository.dwhrep import DefaulttagsFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataitem
        from com.distocraft.dc5000.repository.dwhrep import DataitemFactory
        from com.distocraft.dc5000.repository.dwhrep import Externalstatement
        from com.distocraft.dc5000.repository.dwhrep import ExternalstatementFactory
        from com.distocraft.dc5000.repository.dwhrep import Universename
        from com.distocraft.dc5000.repository.dwhrep import UniversenameFactory
        from com.distocraft.dc5000.repository.dwhrep import Aggregation
        from com.distocraft.dc5000.repository.dwhrep import AggregationFactory
        from com.distocraft.dc5000.repository.dwhrep import Aggregationrule
        from com.distocraft.dc5000.repository.dwhrep import AggregationruleFactory
        from com.distocraft.dc5000.repository.dwhrep import Prompt  
        from com.distocraft.dc5000.repository.dwhrep import Promptoption  
        from com.distocraft.dc5000.repository.dwhrep import Promptimplementor
        
        self.Versioning = Versioning(self.dwhrep, versionid)
        tpName = self.Versioning.getTechpack_name()
        
        tpa = Tpactivation(self.dwhrep)
        tpa.setTechpack_name(tpName)
        tpaF = TpactivationFactory(self.dwhrep, tpa)
        for tpatmp in tpaF.get():
            if tpatmp.getVersionid() == versionid:
                pass
                #self.deactivateTP(versionid)
        
        vo = Verificationobject(self.dwhrep)
        vo.setVersionid(self.Versioning.getVersionid())
        vo.deleteDB()
        
        vc = Verificationcondition(self.dwhrep)
        vc.setVersionid(self.Versioning.getVersionid())
        vc.deleteDB()
        
        exs = Externalstatement(self.dwhrep)
        exs.setVersionid(self.Versioning.getVersionid())
        exs.deleteDB()
        
        uf = Universeformulas(self.dwhrep)
        uf.setVersionid(self.Versioning.getVersionid())
        uf.deleteDB()
        
        un = Universeparameters(self.dwhrep)
        un.setVersionid(self.Versioning.getVersionid())
        un.deleteDB()
        
        un = Universejoin(self.dwhrep)
        un.setVersionid(self.Versioning.getVersionid())
        un.deleteDB()
        
        uo = Universeobject(self.dwhrep)
        uo.setVersionid(self.Versioning.getVersionid())
        uo.deleteDB()
        
        uco = Universecomputedobject(self.dwhrep)
        uco.setVersionid(self.Versioning.getVersionid())
        uco.deleteDB()
        
        uc = Universecondition(self.dwhrep)
        uc.setVersionid(self.Versioning.getVersionid())
        uc.deleteDB()
        
        ut = Universetable(self.dwhrep)
        ut.setVersionid(self.Versioning.getVersionid())
        ut.deleteDB()
        
        ucl = Universeclass(self.dwhrep)
        ucl.setVersionid(self.Versioning.getVersionid())
        ucl.deleteDB()
        
        un = Universename(self.dwhrep)
        un.setVersionid(self.Versioning.getVersionid())
        un.deleteDB()
        
        tpd = Techpackdependency(self.dwhrep)
        tpd.setVersionid(self.Versioning.getVersionid())
        tpd.deleteDB()
        
        agr = Aggregationrule(self.dwhrep)
        agr.setVersionid(self.Versioning.getVersionid())
        agr.deleteDB()
        
        agg = Aggregation(self.dwhrep)
        agg.setVersionid(self.Versioning.getVersionid())
        agg.deleteDB()
        
        df = Dataformat(self.dwhrep)
        df.setVersionid(self.Versioning.getVersionid())
        dff = DataformatFactory(self.dwhrep, df)
        for df in dff.get():
            id = df.getDataformatid()
            ditem = Dataitem(self.dwhrep)
            ditem.setDataformatid(id)
            dif = DataitemFactory(self.dwhrep, ditem)
            for di in dif.get():
                di.setDataformatid(id)
                di.deleteDB()
            
            dt = Defaulttags(self.dwhrep)
            dt.setDataformatid(id)
            dtf = DefaulttagsFactory(self.dwhrep, dt)
            for di in dtf.get():
                dt.setDataformatid(id)
                dt.deleteDB()
            
            df.deleteDB()
        
        p = Prompt(self.dwhrep)
        p.setVersionid(self.Versioning.getVersionid())
        p.deleteDB()
        
        po = Promptoption(self.dwhrep)
        po.setVersionid(self.Versioning.getVersionid())
        po.deleteDB()
        
        pi = Promptimplementor(self.dwhrep)
        pi.setVersionid(self.Versioning.getVersionid())
        pi.deleteDB()
        
        rtCond = Referencetable(self.dwhrep)
        rtCond.setVersionid(self.Versioning.getVersionid())
        rtf = ReferencetableFactory(self.dwhrep, rtCond)
        for rt in rtf.get():
            rcCond = Referencecolumn(self.dwhrep)
            rcCond.setTypeid(rt.getTypeid())
            rcf = ReferencecolumnFactory(self.dwhrep, rcCond)
            for rc in rcf.get():
                rc.deleteDB()
            rt.deleteDB()
        
        tt = Transformer(self.dwhrep)
        tt.setVersionid(self.Versioning.getVersionid())
        trf = TransformerFactory(self.dwhrep, tt)
        for t in trf.get():
            tmptransformerid = t.getTransformerid()
            tf = Transformation(self.dwhrep)
            tf.setTransformerid(tmptransformerid)
            tff = TransformationFactory(self.dwhrep, tf)
            for tf in tff.get():
                tf.deleteDB()
            t.deleteDB()
            
        bhCond = Busyhour(self.dwhrep)
        bhCond.setVersionid(self.Versioning.getVersionid())
        busyhourFactory = BusyhourFactory(self.dwhrep, bhCond, True)
        for busyhour in busyhourFactory.get():
            bhS = Busyhoursource(self.dwhrep)
            bhS.setVersionid(busyhour.getVersionid())
            bhS.setTargetversionid(busyhour.getTargetversionid())
            bhS.setBhlevel(busyhour.getBhlevel())
            bhS.setBhobject(busyhour.getBhobject())
            bhS.setBhtype(busyhour.getBhtype())
            bhS.deleteDB(bhS)
            
            bhRK = Busyhourrankkeys(self.dwhrep)
            bhRK.setVersionid(busyhour.getVersionid())
            bhRK.setTargetversionid(busyhour.getTargetversionid())
            bhRK.setBhlevel(busyhour.getBhlevel())
            bhRK.setBhobject(busyhour.getBhobject())
            bhRK.setBhtype(busyhour.getBhtype())
            bhRK.deleteDB(bhRK)
            
            bhm = Busyhourmapping(self.dwhrep)
            bhm.setVersionid(busyhour.getVersionid())
            bhm.setTargetversionid(busyhour.getTargetversionid())
            bhm.setBhlevel(busyhour.getBhlevel())
            bhm.setBhobject(busyhour.getBhobject())
            bhm.setBhtype(busyhour.getBhtype())
            bhm.deleteDB()
            
            busyhour.deleteDB()
        
        bhPH = Busyhourplaceholders(self.dwhrep)
        bhPH.setVersionid(self.Versioning.getVersionid())
        bhPH.deleteDB()
        
        mtype = Measurementtype(self.dwhrep)
        mtype.setVersionid(self.Versioning.getVersionid())
        mtypef = MeasurementtypeFactory(self.dwhrep, mtype)
        for mtype in mtypef.get():
            mtable = Measurementtable(self.dwhrep)
            mtable.setTypeid(mtype.getTypeid())
            mtablef = MeasurementtableFactory(self.dwhrep, mtable)
            for mtable in mtablef.get():
                mCol = Measurementcolumn(self.dwhrep)
                mCol.setMtableid(mtable.getMtableid())
                mCol.deleteDB(mCol)
                
                tmpmt = Measurementtable(self.dwhrep)
                tmpmt.setMtableid(mtable.getMtableid());
                tmpmt.deleteDB()
            
            measurementobjbhsupport = Measurementobjbhsupport(self.dwhrep)
            measurementobjbhsupport.setTypeid(mtype.getTypeid())
            measurementobjbhsupport.deleteDB(measurementobjbhsupport)
            
            mv = Measurementvector(self.dwhrep)
            mv.setTypeid(mtype.getTypeid())
            mv.deleteDB(mv)
            
            mco = Measurementcounter(self.dwhrep)
            mco.setTypeid(mtype.getTypeid())
            mco.deleteDB(mco)
            
            mdcs = Measurementdeltacalcsupport(self.dwhrep)
            mdcs.setTypeid(mtype.getTypeid())
            mdcs.deleteDB(mdcs)
            
            mkey = Measurementkey(self.dwhrep)
            mkey.setTypeid(mtype.getTypeid())
            mkey.deleteDB(mkey)
            
            mt = Measurementtype(self.dwhrep)
            mt.setTypeid(mtype.getTypeid())
            mt.deleteDB()
        
        mclass = Measurementtypeclass(self.dwhrep)
        mclass.setVersionid(self.Versioning.getVersionid())
        mclass.deleteDB(mclass)
        
        svr = Supportedvendorrelease(self.dwhrep)
        svr.setVersionid(self.Versioning.getVersionid())
        svr.deleteDB()
        
        try:
            from com.distocraft.dc5000.repository.dwhrep import Grouptypes
            from com.distocraft.dc5000.repository.dwhrep import GrouptypesFactory
        
            gt = Grouptypes(self.dwhrep)
            gt.setVersionid(self.Versioning.getVersionid())
            gt.deleteDB()
        except:
            pass
        
        self.Versioning.deleteDB()

        #versionparts = versionid.split(':')
        #self.deleteSets(versionparts[0], versionparts[1])

            
    def commit(self):
        self.dwhrep.getConnection().commit()
        self.etlrep.getConnection().commit()
        self.dwhRock.getConnection().commit()
        self.dbaDwhRock.getConnection().commit()
    
    def rollback(self):
        self.dwhrep.getConnection().rollback()
        self.etlrep.getConnection().rollback()
        self.dwhRock.getConnection().rollback()
        self.dbaDwhRock.getConnection().rollback()
    
    def _verifyNotNone(self, obj, method):
        try:
            return int(getattr(obj,method)())
        except:
            return 0
        
    def _replaceNone(self, statement):
        if statement() == None:
            return ''
        else:
            return statement()
    
    def generateDocumentation(self, versionID, outputPath):
        import os
        from java.text import SimpleDateFormat
        from java.util import Date
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import Supportedvendorrelease
        from com.distocraft.dc5000.repository.dwhrep import SupportedvendorreleaseFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtype
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtypeFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementobjbhsupport
        from com.distocraft.dc5000.repository.dwhrep import MeasurementobjbhsupportFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementkey
        from com.distocraft.dc5000.repository.dwhrep import MeasurementkeyFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcounter
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcounterFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhour
        from com.distocraft.dc5000.repository.dwhrep import BusyhourFactory
        from com.distocraft.dc5000.repository.dwhrep import BusyhoursourceFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhoursource
        from com.distocraft.dc5000.repository.dwhrep import BusyhourrankkeysFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourrankkeys
        from com.distocraft.dc5000.repository.dwhrep import BusyhourmappingFactory
        from com.distocraft.dc5000.repository.dwhrep import Busyhourmapping
        from com.distocraft.dc5000.repository.dwhrep import ReferencetableFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencetable
        from com.distocraft.dc5000.repository.dwhrep import MeasurementcolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementcolumn
        from com.distocraft.dc5000.repository.dwhrep import MeasurementtableFactory
        from com.distocraft.dc5000.repository.dwhrep import Measurementtable
        from com.distocraft.dc5000.repository.dwhrep import DatainterfaceFactory
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        from com.distocraft.dc5000.repository.dwhrep import InterfacemeasurementFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacemeasurement
        from com.distocraft.dc5000.repository.dwhrep import DataformatFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataformat
        from com.distocraft.dc5000.repository.dwhrep import ReferencecolumnFactory
        from com.distocraft.dc5000.repository.dwhrep import Referencecolumn
        from org.apache.velocity import VelocityContext
        from org.apache.velocity.app import Velocity
        from java.util import Properties
        from java.io import StringWriter
        
        basedir = outputPath
        if not os.path.exists(basedir):
            os.makedirs(basedir)
            
        vmPath = outputPath.split('Output')[0]+'Environment' 
        vmPath = vmPath.replace('\\','/')     
        
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        context = VelocityContext()
        
        self.Versioning = Versioning(self.dwhrep, versionID)
        
        versID = self.Versioning.getVersionid()
        version = versID.split(':')[1]
        version = version.replace('((', '')
        version = version.replace('))', '')
        
        dte = Date()
        dateFormats = {'year': 'yyyy', 'day': 'dd', 'month': 'MM'}
        for key, formattype in dateFormats.iteritems():
            formatter = SimpleDateFormat(formattype)
            context.put(key, formatter.format(dte))
        
        description = self.Versioning.getDescription().strip()
        if description.endswith(version):
            description = description.rsplit(version, 1)[0]
        
        sdifFile = open(basedir+'\\TP Description ' + description + '.sdif','w')  
        
        tpVers = self.Versioning.getTechpack_version()
        if tpVers.endswith(version):
            tpVers = tpVers.replace('_'+version, 1)

        context.put("revision", tpVers)
        context.put("productNumber", self.Versioning.getProduct_number())
        context.put("versioning", self.Versioning)
        context.put("version", version)
        context.put("description", description.strip())
        context.put("productNumberAndRelease", self.Versioning.getProduct_number() + ' ' + tpVers)
        
        releases = ''
        where = Supportedvendorrelease(self.dwhrep)
        where.setVersionid(versID)
        svrF = SupportedvendorreleaseFactory(self.dwhrep, where)
        for svr in svrF.get():
            releases = releases + svr.getVendorrelease()+','
            
        releases = releases.rsplit(',', 1)[0]
        context.put("releases", releases)
        
        factTableList = {}
        where = Measurementtype(self.dwhrep)
        where.setVersionid(versID)
        mtf = MeasurementtypeFactory(self.dwhrep, where)
        for mt in mtf.get():
            mtCalls = {'OneMinuteAggregation' : 'getOneminagg',
                    'FifteenMinuteAggregation' : 'getFifteenminagg',
                    'totalAggregation' : 'getTotalagg',
                    'totalAggregation' : 'getSonagg',
                    'elementBusyHourSupport' : 'getElementbhsupport',
                    'deltaCalculation' : 'getDeltacalcsupport',
                    'Load File Duplicate Check' : 'getLoadfile_dup_check',
                    }
            if mt.getRankingtable() == 0:
                factTableData = {}
                factTableData["factTable"] = mt.getTypename()
                factTableData["typeID"] = mt.getTypeid()
                factTableData["size"] = mt.getSizing()
                
                methods = dir(mt)
                for key, call in mtCalls.iteritems():
                    if call in methods:
                        value = getattr(mt,call)()
                        if value == 1:
                            factTableData[key] ='Yes'
                        else:
                            factTableData[key] ='No'
                        
                factTableList[mt.getTypename()] = factTableData

                
        for table, data in factTableList.iteritems():
            where = Measurementobjbhsupport(self.dwhrep)
            where.setTypeid(data['typeID'])
            mobhsF = MeasurementobjbhsupportFactory(self.dwhrep, where)
            mobhs = ''
            for mbhs in mobhsF.get():
                mobhs = mobhs + mbhs.getObjbhsupport()+','
            mobhs = mobhs.rsplit(',', 1)[0]
            if len(mobhs) > 0:
                data['objectBusyHourSupport'] = mobhs
            else:
                data['objectBusyHourSupport'] = 'None'
        
            where = Measurementkey(self.dwhrep)
            where.setTypeid(data['typeID'])
            mkF = MeasurementkeyFactory(self.dwhrep, where)
            rows = []
            for mk in mkF.get():
                row = {}
                row['name'] = mk.getDataname()
                row['dataType'] = str(mk.getDatatype()) + '(' + str(mk.getDatasize()) + ')'
                if mk.getUniquekey() == 1:
                    row['duplicateConstraint'] = 'Yes'
                else:
                    row['duplicateConstraint'] = 'No'
                rows.append(row)
            data[data['factTable']+'_keys'] = rows
        
        
            where = Measurementcounter(self.dwhrep)
            where.setTypeid(data['typeID'])
            mcF = MeasurementcounterFactory(self.dwhrep, where)
            rows = []
            for mc in mcF.get():
                row = {}
                row['name'] = mc.getDataname()
                row['timeAggregation'] = mc.getTimeaggregation()
                row['groupAggregation'] = mc.getGroupaggregation()
                row['type'] = mc.getCountertype()
                if mc.getDatascale() != None:
                    if int(mc.getDatascale()) >= 0:
                        row['dataType'] = str(mc.getDatatype()) + '(' + str(mc.getDatasize()) + ',' + str(mc.getDatascale())+ ')'
                    else:
                        row['dataType'] = str(mc.getDatatype()) + '(' + str(mc.getDatasize()) + ')'
                rows.append(row)
            data[data['factTable']+'_counters'] = rows
        context.put("factTableData", factTableList)
        
        bhWhere = Busyhour(self.dwhrep)
        bhWhere.setVersionid(versID)
        bhf = BusyhourFactory(self.dwhrep, bhWhere, 'ORDER BY BHLEVEL, BHTYPE')
        phTypes = ['PP', 'CP']
        bhTypeToString = {'RANKBH_TIMELIMITED' : 'Timelimited',
                    'RANKBH_SLIDINGWINDOW' : 'Slidingwindow',
                    'RANKBH_TIMECONSISTENT' : 'Timelimited + Timeconsistent',
                    'RANKBH_TIMECONSISTENT_SLIDINGWINDOW' : 'Slidingwindow + Timeconsistent',
                    'RANKBH_PEAKROP' : 'Peakrop',
                    }
        if bhf.getElementAt(0) != None:
            if bhf.getElementAt(0).getPlaceholdertype() in phTypes:
                bhLevelList = {}
                for bh in bhf.get():
                    splitList = {}
                    orderPlaceholderList = []
                    if bh.getBhlevel() in bhLevelList.keys():
                        splitList = bhLevelList[bh.getBhlevel()]
                    if bh.getPlaceholdertype() in splitList.keys():
                        orderPlaceholderList = splitList[bh.getPlaceholdertype()]
                    datamap = {}
                    datamap["description"] = bh.getDescription()
                    datamap["criteria"] = bh.getBhcriteria()
                    datamap["whereCondition"] = bh.getWhereclause()
                    datamap["targetVersionId"] = bh.getTargetversionid()
                    datamap["versionId"] = bh.getVersionid()
                    datamap["bhType"] = bh.getBhtype()
                    datamap["bhLevel"] = bh.getBhlevel()
                    datamap["aggregationType"] = bhTypeToString[bh.getAggregationtype()]
                    datamap["bhVersion"] = "1"
                    datamap["grouping"] = '' #Left empty because CR in IDE code. Added to tidy up output Doc.
                    
                    sWhere = Busyhoursource(self.dwhrep)
                    sWhere.setVersionid(bh.getVersionid())
                    sWhere.setTargetversionid(bh.getTargetversionid())
                    sWhere.setBhtype(bh.getBhtype())
                    sWhere.setBhlevel(bh.getBhlevel())
                    bhsF = BusyhoursourceFactory(self.dwhrep, sWhere)
                    source = ''
                    for bhs in bhsF.get():
                        source = source + bhs.getTypename() + ','
                    source = source.rsplit(',', 1)[0]
                    datamap["source"] = source
                    
                    kWhere = Busyhourrankkeys(self.dwhrep)
                    kWhere.setBhtype(bh.getBhtype())
                    kWhere.setBhlevel(bh.getBhlevel())
                    kWhere.setVersionid(bh.getVersionid())
                    kFac = BusyhourrankkeysFactory(self.dwhrep, kWhere)
                    sb = ''
                    for rkey in kFac.get():
                        sb = sb + rkey.getKeyname()+','
                    sb = sb.rsplit(',', 1)[0]
                    datamap["rankKeys"] = sb
                    
                    mWhere = Busyhourmapping(self.dwhrep)
                    mWhere.setBhtype(bh.getBhtype())
                    mWhere.setBhlevel(bh.getBhlevel())
                    mWhere.setVersionid(bh.getVersionid())
                    mFac = BusyhourmappingFactory(self.dwhrep, mWhere)
                    msb = ''
                    for mapping in mFac.get():
                        msb = msb + mapping.getBhtargettype()+','
                    msb = msb.rsplit(',', 1)[0]
                    datamap["bhMappings"] = msb
                    datamap["bhType"] = bh.getBhtype()
                    if bh.getBhcriteria() == None or len(bh.getBhcriteria()) == 0:
                        datamap["defined"] = False
                    else:
                        datamap["defined"] = True
                    orderPlaceholderList.append(datamap)
                    splitList[bh.getPlaceholdertype()] = orderPlaceholderList
                    bhLevelList[bh.getBhlevel()] = splitList
            
                    bhList = {}
                    for bhLevel in sorted(bhLevelList):
                        lList = []
                        if bhLevel in bhList.keys():
                            lList = bhList[bhLevel]
                        for pType in phTypes:
                            if pType in bhLevelList[bhLevel]:
                                lList = lList + bhLevelList[bhLevel][pType]
                        bhList[bhLevel] = lList

                context.put("busyHourData", bhList)
        
        dimensionTableList = {}
        dataTypes = ['tinyint','smallint','int','integer','date','datetime','insigned int']
        UPDATE_METHODS_TEXT = [ "Static", "Predefined", "Dynamic", "Timed Dynamic", "History Dynamic" ]
        where = Referencetable(self.dwhrep)
        where.setVersionid(versID)
        rtF = ReferencetableFactory(self.dwhrep, where)
        for rt in rtF.get():
            dimensionTableData = {}
            dimensionTableData['dimensionTable'] = rt.getTypename()
            dimensionTableData['typeID'] = rt.getTypeid()
            dimensionTableData['updateMethod'] = UPDATE_METHODS_TEXT[int(rt.getUpdate_policy())]
            if 'SELECT_' in rt.getTypename() and '_AGGLEVEL' in rt.getTypename():
                dimensionTableData['type'] = 'view'
            else:
                dimensionTableData['type'] = 'table'
                
            rows = []
            where = Referencecolumn(self.dwhrep)
            where.setTypeid(rt.getTypeid())
            rcF = ReferencecolumnFactory(self.dwhrep, where)
            for rc in rcF.get():
                row = {}
                row["name"] = rc.getDataname()
                sb = rc.getDatatype()
                if rc.getDatatype() not in dataTypes and rc.getDatatype() == 'numeric':
                    sb = sb + '('+ str(rc.getDatasize()) +','+ str(rc.getDatascale()) +')'
                elif rc.getDatatype() not in dataTypes:
                    sb = sb + '(' + str(rc.getDatasize()) + ')'
                row["dataType"] = sb
                if rc.getIncludeupd() == 1:
                    row["includedInUpdates"] = 'Yes'
                else:
                    row["includedInUpdates"] = 'No'
                rows.append(row)
            dimensionTableData[rt.getTypename()+'_columns'] = rows

            dimensionTableList[rt.getTypename()] = dimensionTableData
        context.put("dimensionTableData", dimensionTableList)
        
        interfaceList = {}
        where = Dataformat(self.dwhrep)
        where.setVersionid(versID)
        dfF = DataformatFactory(self.dwhrep, where)
        for df in dfF.get():
            where = Interfacemeasurement(self.dwhrep)
            where.setDataformatid(df.getDataformatid())
            ifmF = InterfacemeasurementFactory(self.dwhrep, where)
            for ifm in ifmF.get():
                where = Datainterface(self.dwhrep)
                where.setInterfacename(ifm.getInterfacename())
                diF = DatainterfaceFactory(self.dwhrep, where)
                di = diF.getElementAt(0)
                interfaceData = {}
                interfaceData["name"] = di.getInterfacename() + "_" + di.getInterfacetype()
                interfaceData["type"] = di.getInterfacetype()
                interfaceList[ifm.getInterfacename()] = interfaceData
        context.put("interfaceData", interfaceList)
        
        sqlInterfaceList = {}
        where = Measurementtype(self.dwhrep)
        where.setVersionid(versID)
        mtf = MeasurementtypeFactory(self.dwhrep, where)
        for mt in mtf.get():
            where = Measurementtable(self.dwhrep)
            where.setTypeid(mt.getTypeid())
            mtbf = MeasurementtableFactory(self.dwhrep, where)
            for mtb in mtbf.get():
                where = Measurementcolumn(self.dwhrep)
                where.setMtableid(mtb.getMtableid())
                where.setIncludesql(1)
                mcF = MeasurementcolumnFactory(self.dwhrep, where)
                columns = []
                for mc in mcF.get():
                    row = {}
                    row['name'] = mc.getDataname()
                    sb = mc.getDatatype()
                    if mc.getDatatype() not in dataTypes and mc.getDatatype() == 'numeric':
                        sb = sb + '('+ str(mc.getDatasize()) +','+ str(mc.getDatascale()) +')'
                    elif mc.getDatatype() not in dataTypes:
                        sb = sb + '('+ str(mc.getDatasize()) +')'
                    row['type'] = sb
                    columns.append(row)
                sqlInterfaceList[mtb.getBasetablename()] = columns
                
        where = Referencetable(self.dwhrep)
        where.setVersionid(versID)
        rtF = ReferencetableFactory(self.dwhrep, where)
        for rt in rtF.get():
            columns = []
            where = Referencecolumn(self.dwhrep)
            where.setTypeid(rt.getTypeid())
            where.setIncludesql(1)
            rcF = ReferencecolumnFactory(self.dwhrep, where)
            for rc in rcF.get():
                row = {}
                row['name'] = rc.getDataname()
                sb = rc.getDatatype()
                if rc.getDatatype() not in dataTypes and rc.getDatatype() == 'numeric':
                    sb = sb + '('+ str(rc.getDatasize()) +','+ str(rc.getDatascale()) +')'
                elif rc.getDatatype() not in dataTypes:
                    sb = sb + '('+ str(rc.getDatasize() )+')'
                row['type'] = sb
                columns.append(row)
            sqlInterfaceList[rt.getTableName()] = columns
        context.put("sqlInterfaceData", sqlInterfaceList)
        
        try:
            from com.distocraft.dc5000.repository.dwhrep import Grouptypes
            from com.distocraft.dc5000.repository.dwhrep import GrouptypesFactory
            data = {}
            where = Grouptypes(self.dwhrep)
            where.setVersionid(versID)
            fac = GrouptypesFactory(self.dwhrep, where)
            for group in fac.get():
                gdata = []
                if group.getGrouptype() in data.keys():
                    gdata = data[group.getGrouptype()]
                gdata.append(group)
                data[group.getGrouptype()] = gdata
            context.put("groupDefData", data)
        except:
            pass
        
        strw = StringWriter()
        isMergeOk = Velocity.mergeTemplate('/SDIFDescTemplate.vm', Velocity.ENCODING_DEFAULT, context, strw)
        if isMergeOk:
            sdifFile.write(strw.toString())
        sdifFile.close()
        
        
                
            
            