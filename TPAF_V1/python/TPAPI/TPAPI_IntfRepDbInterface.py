'''
Created on 2 May 2013

@author: ebrifol
'''

import TPAPI

class IntfRepDbInterface(object):
    
    def __init__(self,server):
        self.server = server
        self.Datainterface = {}
        self.Interfacetechpacks = {}
        self.Interfacedependency = {}
        
        self.etlrep = None
        self.dwhrep = None
        self.dwhRock = None
        self.dbaDwhRock = None
        self.createRockFactoryConnections()
        
        self.TargetEniqVersion = TPAPI.getENIQversion(TPAPI.getFTPConnection(self.server, 'dcuser', 'dcuser'))
        
        
    def createRockFactoryConnections(self):
        from ssc.rockfactory import RockFactory
        from com.distocraft.dc5000.etl.rock import Meta_databases
        from com.distocraft.dc5000.etl.rock import Meta_databasesFactory
        
        self.etlrep = RockFactory("jdbc:sybase:Tds:"+ self.server +":2641", "etlrep", "etlrep", "com.sybase.jdbc3.jdbc.SybDriver", "TPAPI", True)
        self.dwhrep = RockFactory("jdbc:sybase:Tds:"+ self.server +":2641", "dwhrep", "dwhrep", "com.sybase.jdbc3.jdbc.SybDriver", "TPAPI", True)
        
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
        
        self.dwhRock = RockFactory(dbURL, dwhdb.getUsername(), dwhdb.getPassword(), dwhdb.getDriver_name(), "TPAPI", True)
        self.dbaDwhRock = RockFactory(dbURL, dbadwhdb.getUsername(), dbadwhdb.getPassword(), dwhdb.getDriver_name(),"TPAPI", True)
    
    def setRockFactoryAutoCommit(self, state):
        self.dwhrep.getConnection().setAutoCommit(state)
        self.etlrep.getConnection().setAutoCommit(state)
        self.dwhRock.getConnection().setAutoCommit(state)
        self.dbaDwhRock.getConnection().setAutoCommit(state)
    
    def populateInterfacedependency(self,IntfDepDict):
        from com.distocraft.dc5000.repository.dwhrep import Interfacedependency       
        KEY = IntfDepDict['INTERFACENAME'] + ':' + IntfDepDict['INTERFACEVERSION'] + ':' + IntfDepDict['TECHPACKNAME'] + ':' + IntfDepDict['TECHPACKVERSION']
        if KEY not in self.Interfacedependency:
            self.Interfacedependency[KEY] = self.populateObjectFromDict(Interfacedependency, IntfDepDict)
    
    def populateInterfacetechpacks(self,IntfTPDict):
        from com.distocraft.dc5000.repository.dwhrep import Interfacetechpacks       
        KEY = IntfTPDict['INTERFACENAME'] + ':' + IntfTPDict['INTERFACEVERSION'] + ':' + IntfTPDict['TECHPACKNAME'] + ':' + IntfTPDict['TECHPACKVERSION']
        if KEY not in self.Interfacetechpacks:
            self.Interfacetechpacks[KEY] = self.populateObjectFromDict(Interfacetechpacks, IntfTPDict)
      
    def populateDatainterface(self,DataIntfDict):
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        DataIntfDict['ENIQ_LEVEL'] = self.TargetEniqVersion       
        KEY = DataIntfDict['INTERFACENAME'] + ':' + DataIntfDict['INTERFACEVERSION']
        if KEY not in self.Datainterface:
            self.Datainterface[KEY] = self.populateObjectFromDict(Datainterface, DataIntfDict)
    
    def deactivateIntf(self, versionID):
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        from com.distocraft.dc5000.repository.dwhrep import Interfacemeasurement
        from com.distocraft.dc5000.repository.dwhrep import InterfacemeasurementFactory
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from com.distocraft.dc5000.etl.rock import Meta_collections
        from com.distocraft.dc5000.etl.rock import Meta_collectionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actions
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actionsFactory
        
        items = versionID.split(':')
        dataIntf = Datainterface(self.dwhrep, items[0], items[1])
        dataIntf.setStatus(long(float(0)))
        dataIntf.saveDB()
        
        im_cond = Interfacemeasurement(self.dwhrep)
        im_cond.setInterfacename(dataIntf.getInterfacename())
        im_cond.setInterfaceversion(dataIntf.getInterfaceversion())
        imf = InterfacemeasurementFactory(self.dwhrep, im_cond)
        for im in imf.get():
            im.deleteDB()
            
        mcs = Meta_collection_sets(self.etlrep)
        mcsF = Meta_collection_setsFactory(self.etlrep, mcs)
        if mcsF != None and len(mcsF.get()) > 0:
            for metacs in mcsF.get():
                if metacs.getCollection_set_name() == dataIntf.getInterfacename() or dataIntf.getInterfacename() + "-" in metacs.getCollection_set_name():
                    metaCollectionSetName = metacs.getCollection_set_name()
                    interfaceVersion = metacs.getVersion_number()
                    
                    mcs = Meta_collection_sets(self.etlrep)
                    mcs.setCollection_set_name(metaCollectionSetName)
                    mcs.setVersion_number(interfaceVersion)
                    mcsFF = Meta_collection_setsFactory(self.etlrep, mcs)
                    if mcsFF != None and len(mcsFF.get()) > 0:
                        metacss = mcsFF.getElementAt(0)
                        mc = Meta_collections(self.etlrep)
                        mc.setCollection_set_id(metacss.getCollection_set_id())
                        mc.setVersion_number(interfaceVersion)
                        mcF = Meta_collectionsFactory(self.etlrep, mc)
                        for metac in mcF.get():
                            metac.setEnabled_flag('N')
                            metac.saveDB()
                            
                            mta = Meta_transfer_actions(self.etlrep)
                            mta.setCollection_set_id(metacs.getCollection_set_id())
                            mta.setVersion_number(interfaceVersion)
                            mtaF = Meta_transfer_actionsFactory(self.etlrep ,mta)
                            for action in mtaF.get():
                                action.setEnabled_flag('N')
                                action.saveDB()
                                    
                        metacss.setEnabled_flag('N')
                        metacss.saveDB()
    
    def activateIntf(self, versionID, engine):
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        from com.distocraft.dc5000.repository.dwhrep import DatainterfaceFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacetechpacks
        from com.distocraft.dc5000.repository.dwhrep import InterfacetechpacksFactory
        from com.distocraft.dc5000.repository.dwhrep import Tpactivation
        from com.distocraft.dc5000.repository.dwhrep import TpactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Typeactivation
        from com.distocraft.dc5000.repository.dwhrep import TypeactivationFactory
        from com.distocraft.dc5000.repository.dwhrep import Dataformat
        from com.distocraft.dc5000.repository.dwhrep import DataformatFactory
        from com.distocraft.dc5000.repository.dwhrep import Defaulttags
        from com.distocraft.dc5000.repository.dwhrep import DefaulttagsFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacemeasurement
        from com.distocraft.dc5000.repository.dwhrep import InterfacemeasurementFactory
        from com.distocraft.dc5000.repository.dwhrep import Transformer
        from com.distocraft.dc5000.repository.dwhrep import TransformerFactory
        
        dataFormats = {}
        
        dataFormatType = ''
        items = versionID.split(':')
        IntfName = items[0]
        IntfVersion = items[1]
        dataIntf = Datainterface(self.dwhrep, IntfName, IntfVersion)
        dataIntf.setStatus(long(float(1)))
        dataIntf.saveDB()
        dataInterfaceFactory = DatainterfaceFactory(self.dwhrep, dataIntf)
        if len(dataInterfaceFactory.get()) > 0:
            targetDataInterface = dataInterfaceFactory.getElementAt(0)
            dataFormatType = targetDataInterface.getDataformattype()
            
        whereInterfaceTechPacks = Interfacetechpacks(self.dwhrep)
        whereInterfaceTechPacks.setInterfacename(IntfName)
        whereInterfaceTechPacks.setInterfaceversion(IntfVersion)
        interfaceTechPacksFactory = InterfacetechpacksFactory(self.dwhrep,whereInterfaceTechPacks)
        for currentTechPack in interfaceTechPacksFactory.get():
            techPackName = currentTechPack.getTechpackname()
            
            whereTPActivation = Tpactivation(self.dwhrep)
            whereTPActivation.setTechpack_name(techPackName)
            whereTPActivation.setStatus("ACTIVE")
            tpActivationFactory = TpactivationFactory(self.dwhrep,whereTPActivation)
            for currentTpActivation in tpActivationFactory.get():
                techPackVersionId = currentTpActivation.getVersionid()
                
                whereTypeActivation = Typeactivation(self.dwhrep)
                whereTypeActivation.setTechpack_name(techPackName)
                typeActivationFactory = TypeactivationFactory(self.dwhrep, whereTypeActivation)
                for currentTypeActivation in typeActivationFactory.get():
                    typeName = currentTypeActivation.getTypename()
                    DataFormatTypeId = techPackVersionId + ':' + typeName + ':' + dataFormatType
                    
                    whereDataFormat = Dataformat(self.dwhrep)
                    whereDataFormat.setDataformatid(DataFormatTypeId)
                    dataFormatFactory = DataformatFactory(self.dwhrep, whereDataFormat)
                    for currentDataFormat in dataFormatFactory.get():
                        
                        whereDefaultTags = Defaulttags(self.dwhrep)
                        whereDefaultTags.setDataformatid(currentDataFormat.getDataformatid())
                        defaultTagsFactory = DefaulttagsFactory(self.dwhrep,whereDefaultTags)
                        for currentDefaultTag in defaultTagsFactory.get():
                            dataFormats[currentDefaultTag.getTagid() + '#' + currentDataFormat.getDataformatid()] = currentDataFormat

        whereInterfaceMeasurement = Interfacemeasurement(self.dwhrep)
        whereInterfaceMeasurement.setInterfacename(IntfName)
        whereInterfaceMeasurement.setInterfaceversion(IntfVersion)
        interfaceMeasurementFactory = InterfacemeasurementFactory(self.dwhrep, whereInterfaceMeasurement)
        for currentInterfaceMeasurement in interfaceMeasurementFactory.get():
            currentInterfaceMeasurement.deleteDB()
            
        for uniqueId, currentDataFormat in dataFormats.iteritems():
            currentTagId = uniqueId.split('#')[0]
            description = ''
            
            whereDefaultTag = Defaulttags(self.dwhrep)
            whereDefaultTag.setDataformatid(currentDataFormat.getDataformatid())
            defaultTagsFactory = DefaulttagsFactory(self.dwhrep, whereDefaultTag)
            if len(defaultTagsFactory.get()) > 0:
                description = defaultTagsFactory.getElementAt(0).getDescription()
            
            whereTransformer = Transformer(self.dwhrep)
            whereTransformer.setTransformerid(currentDataFormat.getDataformatid())
            transformerFactory = TransformerFactory(self.dwhrep, whereTransformer)
            
            IntfMeasDict = {}
            IntfMeasDict['TAGID'] = currentTagId
            IntfMeasDict['DESCRIPTION'] = description
            IntfMeasDict['DATAFORMATID'] = currentDataFormat.getDataformatid()
            IntfMeasDict['INTERFACENAME'] = IntfName
            IntfMeasDict['INTERFACEVERSION'] = IntfVersion
            IntfMeasDict['TECHPACKVERSION'] = 'N/A'
            if len(transformerFactory.get()) > 0:
                IntfMeasDict['TRANSFORMERID'] = currentDataFormat.getDataformatid()
            else:
                IntfMeasDict['TRANSFORMERID'] = None
            IntfMeasDict['STATUS'] = long(float(1))
            
            from java.util import Date
            from java.sql import Timestamp
            currentTime = Date()
            currentTimeTimestamp = Timestamp(currentTime.getTime())
            IntfMeasDict['MODIFTIME'] = currentTimeTimestamp.toString()
            self.populateObjectFromDict(Interfacemeasurement, IntfMeasDict).insertDB()
            
            #engine.fastGracefulEngineRestart(240);
            #scheduler.refreshSchedulerConnectionAfterEngineRestart(120);
            engine.rundirectoryCheckerSet(IntfName)
                    

    def generateIntfSets(self, setsDict, vmPath):
        from com.distocraft.dc5000.repository.dwhrep import Versioning
        from com.distocraft.dc5000.repository.dwhrep import VersioningFactory
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actions
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_schedulings
        from com.distocraft.dc5000.etl.rock import Meta_schedulingsFactory
        from com.ericsson.eniq.common.setWizards import CreateIDiskmanagerSet
        from java.util import Properties
        from org.apache.velocity.app import Velocity
        
        
        vmPath = vmPath.split('Output')[0]+'Environment'
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        setName = setsDict['INTERFACENAME']
        version = setsDict['INTERFACEVERSION']
        type = setsDict['INTERFACETYPE']
        elementTypeF = setsDict['ELEMTYPE']
        formatType = setsDict['DATAFORMATTYPE']
        
        mwhere = Meta_collection_sets(self.etlrep)
        mwhere.setCollection_set_name(setName)
        mwhere.setVersion_number(version)
        mcsf = Meta_collection_setsFactory(self.etlrep,mwhere)
                
        etl_tp = None
        if len(mcsf.get()) <= 0:
            csw = Meta_collection_sets(self.etlrep)
            csf = Meta_collection_setsFactory(self.etlrep, csw)
            largest = -1
            for mc in csf.get():
                if largest < mc.getCollection_set_id():
                    largest = mc.getCollection_set_id()
            largest = largest + 1
                
            etl_tp = Meta_collection_sets(self.etlrep)
            etl_tp.setCollection_set_id(largest)
            etl_tp.setCollection_set_name(setName)
            etl_tp.setVersion_number(version)
            etl_tp.setDescription("Interface " + setName + " by TPAF")
            etl_tp.setEnabled_flag("Y")
            etl_tp.setType("Interface")
            etl_tp.insertDB(False, False)
        else:
            etl_tp = mcsf.getElementAt(0)
        
        ENIQ_LEVEL = int(self.TargetEniqVersion.split('.')[0])
        
        cdc = None
        if ENIQ_LEVEL<12:
            from com.ericsson.eniq.common.setWizards import CreateIDirCheckerSet
            cdc = CreateIDirCheckerSet(type, etl_tp.getVersion_number(), self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, elementTypeF)
        else:
            from com.ericsson.eniq.common.setWizards import CreateIDirCheckerSetFactory
            try:
                cdc = CreateIDirCheckerSetFactory.createIDirCheckerSet(type, etl_tp.getVersion_number(), self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, elementTypeF)
            except:
                cdc = CreateIDirCheckerSetFactory.createIDirCheckerSet(type, etl_tp.getVersion_number(), self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, elementTypeF, formatType)
                
        cdc.removeSets()
        cdc.create(False)
        
        cdm = CreateIDiskmanagerSet(type, etl_tp.getVersion_number(), self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, elementTypeF)
        cdm.removeSets(True)
        cdm.create(False, True)
        
        TechPacks = []
        ver = Versioning(self.dwhrep)
        verF = VersioningFactory(self.dwhrep, ver, True)
        for v in verF.get():
            versionNumber = v.getVersionid().split(':')[1]
            TechPacks.append(v.getTechpack_name() + ':' + v.getTechpack_version()+ ':' + versionNumber)
        
        cis = None
        if ENIQ_LEVEL<12:
            from com.ericsson.eniq.common.setWizards import CreateInterfaceSet
            cis = CreateInterfaceSet(type, '5.2', version, '', self.dwhrep, self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, version, formatType, formatType, elementTypeF, '2')
        else:
            from com.ericsson.eniq.common.setWizards import CreateInterfaceSetFactory
            from tpapi.eniqInterface.rescource import DummyResourceMap
            
            application = DummyResourceMap()
            cis = CreateInterfaceSetFactory.createInterfaceSet(type, '5.2', version, '', self.dwhrep, self.etlrep, long(float(etl_tp.getCollection_set_id())), setName, version, formatType, formatType, elementTypeF, '2', application.getResourceMap())
        
        cis.removeTechpacks(TechPacks, formatType, True)
        cis.createTechpacks(False, TechPacks, formatType, True)
        
        config = setsDict['intfConfig']
        newConfig = ''
        existingParams = []
        mta = Meta_transfer_actions(self.etlrep)
        mta.setCollection_set_id(etl_tp.getCollection_set_id())
        mta.setAction_type('Parse')
        mtaF = Meta_transfer_actionsFactory(self.etlrep, mta)
        for a in mtaF.get():          
            config_list = a.getAction_contents().replace('\r', '\n')
            config_list = config_list.rsplit('\n')[2:]
            
            for item in config_list:
                if item != '':
                    kvp = item.split("=",1)
                    param = kvp[0]
                    action = ''
                    try:
                        action = kvp[1]
                    except:
                        pass
                    
                    if param in config.keys():
                        existingParams.append(param)
                        if action != '':
                            action = action.replace(action,config[param])
                        else:
                            action = config[param]+action
                    newConfig = newConfig + param + '=' + action + '\n'
            
            
            
#             config_list = a.getAction_contents().rsplit('\r') # split to list on newline
#             config_list = config_list[2:]
#             for item in config_list:
#                 if item.count('=', 0,len(item)) > 1:
#                     list2 = item.rsplit('\n')
#                     for item1 in list2:
#                         if item1 != '':
#                             param,action = item1.split("=",1) # split the parameters and actions on first equals
#                             param = param.strip('\n\r')
#                             action = action.strip('\n\r')
#                             if param in config.keys():
#                                 existingParams.append(param)
#                                 if action[:-1] != '':
#                                     action = action.replace(action,config[param])
#                                 else:
#                                     action = config[param]+action
#                             line = param + '=' + action
#                 else:
#                     if '=' in item:
#                         param,action = item.split("=",1) # split the parameters and actions on first equals
#                         param = param.strip('\n\r')
#                         action = action.strip('\n\r')
#                         if param in config.keys():
#                             existingParams.append(param)
#                             if action[:-1] != '':
#                                 action = action.replace(action,config[param])
#                             else:
#                                 action = config[param]+action
#                         line = param + '=' + action
#                 newConfig = newConfig + line
    
            for param, action in config.iteritems():
                if param not in existingParams and param != 'AS_Interval' and param != 'AS_SchBaseTime':
                    newConfig = newConfig + param + '=' + action + '\n'

            a.setAction_contents(newConfig)
            a.saveDB()
        
        
        sch = Meta_schedulings(self.etlrep)
        sch.setCollection_set_id(etl_tp.getCollection_set_id())
        sch.setName('TriggerAdapter_'+setName+'_'+formatType)
        schF = Meta_schedulingsFactory(self.etlrep, sch)

        for s in schF.get():
            if 'AS_Interval' in config.keys():
                items = config['AS_Interval'].split(',')
                s.setInterval_hour(long(float(items[0])))
                s.setInterval_min(long(float(items[1])))
            if 'AS_SchBaseTime' in config.keys():
                items = config['AS_SchBaseTime'].split(',')
                s.setScheduling_hour(long(float(items[0])))
                s.setScheduling_min(long(float(items[1])))
            s.saveDB()
        
           
    def createTPInstallFile(self, versionID, buildNumber, outputPath, encrypt):
        import shutil
        import os
        import zipfile
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        from com.distocraft.dc5000.repository.dwhrep import DatainterfaceFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacetechpacks
        from com.distocraft.dc5000.repository.dwhrep import InterfacetechpacksFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacedependency
        from com.distocraft.dc5000.repository.dwhrep import InterfacedependencyFactory
        from com.distocraft.dc5000.etl.importexport import ETLCExport
        from tpapi.eniqInterface import VersionInfo
        from org.apache.velocity import VelocityContext
        from org.apache.velocity.app import Velocity
        from org.apache.velocity.context import Context
        from java.util import Vector
        from java.util import Properties
        
        basedir = outputPath
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        
        vmPath = outputPath.split('Output')[0]+'Environment'
        
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        items = versionID.split(':')
        dataIntf = Datainterface(self.dwhrep, items[0], items[1])
        IntfName = dataIntf.getInterfacename()
        newBuildTag = dataIntf.getRstate() + '_b' + str(buildNumber)
        
        oldversion = versionID.split(':')[1]
        newVersion = '(('+str(buildNumber)+'))'
        
        intfOutputFile = IntfName+'_'+ newBuildTag+'.tpi'
        
        #Create .sql file in sql directory
        intfDir = basedir+'\\interface'
        if not os.path.exists(intfDir):
            os.makedirs(intfDir)
        sqlFile = open(intfDir+'\\Tech_Pack_' + IntfName + '.sql','w')
        
        aimf = DatainterfaceFactory(self.dwhrep, dataIntf)
        for im in aimf.get():
            sqlFile.write('\n-- Datainterface\n'+im.toSQLInsert().replace(oldversion,newVersion))
            
        aimt = Interfacetechpacks(self.dwhrep)
        aimt.setInterfacename(dataIntf.getInterfacename())
        aimt.setInterfaceversion(dataIntf.getInterfaceversion())
        aimtf = InterfacetechpacksFactory(self.dwhrep, aimt)
        for imt in aimtf.get():
            sqlFile.write('\n-- InterfaceTechpacks\n'+imt.toSQLInsert().replace(oldversion,newVersion))
            
        infd = Interfacedependency(self.dwhrep)
        infd.setInterfacename(dataIntf.getInterfacename())
        infd.setInterfaceversion(dataIntf.getInterfaceversion())
        infdf = InterfacedependencyFactory(self.dwhrep, infd)
        for id in infdf.get():
            sqlFile.write('\n-- InterfaceDependency\n'+id.toSQLInsert().replace(oldversion,newVersion))
        
        sqlFile.close()
        
        setFile = open(intfDir+'\\Tech_Pack_' + IntfName + '.xml','w')
        replaseStr = '#version#=' + oldversion + ',#techpack#=' + IntfName
        des = ETLCExport(None, self.etlrep.getConnection())
        from java.io import StringWriter
        filecontents = des.exportXml(replaseStr)
        filecontents = filecontents.getBuffer().toString().replace(oldversion, newVersion)
        setFile.write(filecontents)
        setFile.close()
        
        #Create install directory for version.properties and install.xml
        installDir = basedir+'\\install'
        if not os.path.exists(installDir):
            os.makedirs(installDir)
        
        installXml = open(installDir+'\\install.xml','w')
        installXmlContent = None
        try:
            installXmlContent = dataIntf.getInstalldescription()
        except:
            pass
        
        if installXmlContent != None and len(installXmlContent) > 0:
            installXml.write(installXmlContent)
        else:
            context = None
            vmFile = 'install.vm'
            strw = StringWriter()
            isMergeOk = Velocity.mergeTemplate(vmFile, Velocity.ENCODING_DEFAULT, context, strw)
            if isMergeOk:
                installXml.write(strw.toString().encode('ascii', 'ignore'))
        installXml.close()
        
        versionProps = open(installDir+'\\version.properties','w')
        vec = Vector()
        context = VelocityContext()
        itd = Interfacedependency(self.dwhrep)
        itd.setInterfacename(dataIntf.getInterfacename())
        itd.setInterfaceversion(dataIntf.getInterfaceversion())
        itdF = InterfacedependencyFactory(self.dwhrep, itd)
        for i in itdF.get():
            vi = VersionInfo()
            vi.setTechpackname(i.getTechpackname())
            vi.setVersion(i.getTechpackversion())
            vec.add(vi)
        context.put("required_tech_packs", vec)
        context.put("metadataversion", "3")
        context.put("techpackname", dataIntf.getInterfacename())
        context.put("author", dataIntf.getLockedby())
        context.put("version", dataIntf.getRstate())
        context.put("buildnumber", buildNumber)
        context.put("buildtag", "")
        context.put("licenseName", "")
        
        strw = StringWriter()
        isMergeOk = Velocity.mergeTemplate('version.vm', Velocity.ENCODING_DEFAULT, context, strw)
        if isMergeOk:
            versionProps.write(strw.toString().encode('ascii', 'ignore'))
        versionProps.close()
        
        Z = zipfile.ZipFile(basedir+'\\Unencrypted_'+intfOutputFile, 'w')
        directories = ['install','interface']
        for directory in directories:
            for dirpath,dirs,files in os.walk(basedir+'\\'+directory):
                for f in files:
                    if not f.endswith('.tpi'):
                        fn = os.path.join(dirpath, f)
                        Z.write(str(fn), str(directory+'\\'+f), zipfile.ZIP_DEFLATED )
        Z.close()
        
        dirs = os.listdir(basedir)
        for dir in dirs:
            if not dir.endswith('.tpi'):
                shutil.rmtree(basedir+'\\'+dir)
        
        if encrypt == 'True':
            shutil.copy(basedir+'\\Unencrypted_'+intfOutputFile, basedir+'\\'+intfOutputFile)
            TPAPI.encryptZipFile(basedir+'\\'+intfOutputFile)
        
    def insertToDB(self):
        for key, value in self.Datainterface.iteritems():
            value.insertDB()
        for key, value in self.Interfacetechpacks.iteritems():
            value.insertDB()
        for key, value in self.Interfacedependency.iteritems():
            value.insertDB()
    
    def deleteFromDB(self, versionid):
        from com.distocraft.dc5000.repository.dwhrep import Datainterface
        from com.distocraft.dc5000.repository.dwhrep import DatainterfaceFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacemeasurement
        from com.distocraft.dc5000.repository.dwhrep import InterfacemeasurementFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacetechpacks
        from com.distocraft.dc5000.repository.dwhrep import InterfacetechpacksFactory
        from com.distocraft.dc5000.repository.dwhrep import Interfacedependency
        from com.distocraft.dc5000.repository.dwhrep import InterfacedependencyFactory
        from com.distocraft.dc5000.etl.rock import Meta_collections
        from com.distocraft.dc5000.etl.rock import Meta_collectionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actions
        from com.distocraft.dc5000.etl.rock import Meta_transfer_actionsFactory
        from com.distocraft.dc5000.etl.rock import Meta_schedulings
        from com.distocraft.dc5000.etl.rock import Meta_schedulingsFactory
        from com.distocraft.dc5000.etl.rock import Meta_collection_sets
        from com.distocraft.dc5000.etl.rock import Meta_collection_setsFactory

        items = versionid.split(':')
        name = items[0]
        version = items[1]
        dataIntf = Datainterface(self.dwhrep, name, version)
        
        aim = Interfacemeasurement(self.dwhrep)
        aim.setInterfacename(name)
        aim.setInterfaceversion(version)
        aimf = InterfacemeasurementFactory(self.dwhrep,aim)
        for im in aimf.get():
            im.deleteDB()
            
        aimt = Interfacetechpacks(self.dwhrep)
        aimt.setInterfacename(name)
        aimt.setInterfaceversion(version)
        aimtf = InterfacetechpacksFactory(self.dwhrep, aimt)
        for imt in aimtf.get():
            imt.deleteDB()
            
        infdt = Interfacedependency(self.dwhrep)
        infdt.setInterfacename(name)
        infdt.setInterfaceversion(version)
        infdtf = InterfacedependencyFactory(self.dwhrep,infdt)
        for imt in infdtf.get():
            imt.deleteDB()
         
        removeList = []
        mc = Meta_collections(self.etlrep)
        mc.setVersion_number(version)
        mcF = Meta_collectionsFactory(self.etlrep, mc)
        for m in mcF.get():
            mta = Meta_transfer_actions(self.etlrep)
            mta.setCollection_id(m.getCollection_id())
            mta.setCollection_set_id(m.getCollection_set_id())
            mtaF = Meta_transfer_actionsFactory(self.etlrep, mta)
            for a in mtaF.get():
                try:
                    action = ''
                    if 'interfaceName=' in a.getAction_contents():
                        action = a.getAction_contents().rsplit('interfaceName=')[1]
                    
                   
#                     config_list = a.getAction_contents().rsplit('\r')
#                     #config_list = config_list[7:]
#                     action = ''
#                     for line in config_list:
#                         if line.strip() != '' and line.strip() != '#':
#                             param,action = line.split("=",1)
#                             if param == 'interfaceName':
#                                 print 'FOUND IT: ' + action
#                                 action=action[:-1]
                    
                    #print action + ' : ' + name        
                    #if action == name:
                    if action.startswith(name):
                        if a.getCollection_set_id() not in removeList:
                            removeList.append(a.getCollection_set_id())
                except:
                    pass
                        
        for collection_set_id in removeList:
            rmc = Meta_collections(self.etlrep)
            rmc.setCollection_set_id(collection_set_id)
            rmc.setVersion_number(version)
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
                
            rmcs = Meta_collection_sets(self.etlrep)
            rmcs.setCollection_set_id(collection_set_id)
            rmcsF = Meta_collection_setsFactory(self.etlrep, rmcs)
            rmcsF.getElementAt(0).deleteDB()
                        
        dataIntf.deleteDB()        
        
    
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
    
    def populateObjectFromDict(self, Object, Dict):
        obj = Object(self.dwhrep, True)         
        items = dir(Object)
        for i in items:
            if i.startswith('set'):
                propertyName = i.split('set')[1].upper()
                if propertyName in Dict:
                    propertyType = str(vars(Object)[i.split('set')[1].lower()]).split(' ')[3].split('.')[2]
                    value = None
                    if propertyType == 'String':
                        value = Dict[propertyName].strip()
                    elif propertyType == 'Integer':
                        if Dict[propertyName] == '' or Dict[propertyName] == '0':
                            value = 0
                        else:
                            value = int(Dict[propertyName])
                    elif propertyType == 'Long':
                        value = long(Dict[propertyName])
                    elif propertyType == 'Timestamp':
                        from java.sql import Timestamp
                        value = Timestamp.valueOf(Dict[propertyName])
                    getattr(obj,i)(value)
        return obj