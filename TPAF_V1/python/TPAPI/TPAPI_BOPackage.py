# esalste
from __future__ import with_statement
import TPAPI
import logging
import os
import sys
import subprocess
import shutil
import warnings
import zipfile

class BOuniverse(object):
    
    def __init__(self,versionID, outputDir, BIversion):
        
        self.logger = logging.getLogger('TPAPI.TPAPI_TP.BOPackage')
        self.versionID = versionID
        self.BIversion = BIversion
        self.userPath = sys.getBaseProperties().getProperty("user.home")
        self.boTemplateDir = self.userPath + '\\My Business Objects Documents\\templates\\'
        self.name = self.versionID.split(":")[0]
        self.version = self.versionID.split("((",1)[1].split("))",1)[0]
        self.outDirectory = outputDir + "\\BO"
        self.createDirectories(self.boTemplateDir,self.outDirectory)
        
    def createUniverse(self,bisIp,odbcConnection,server,userName = None,passWord = None):
        self.boAction = 'createUnv'
        self.backgroudinit(self.boAction,bisIp,odbcConnection,server,userName,passWord)
    
    def updateUniverse(self,bisIp,odbcConnection,server,userName = None,passWord = None):
        self.boAction = 'updateUnv'
        self.backgroudinit(self.boAction,bisIp,odbcConnection,server,userName,passWord)

        
    def createVerificationReport(self,bisIp,odbcConnection,server,userName = None,passWord = None):
        self.boAction = 'createRep'
        self.backgroudinit(self.boAction,bisIp,odbcConnection,server,userName,passWord)
    
    def createBOReferenceDoc(self,bisIp,odbcConnection,server,userName = None,passWord = None):
        self.boAction = 'createDoc'
        self.backgroudinit(self.boAction,bisIp,odbcConnection,server,userName,passWord)
    
    def backgroudinit(self,boAction,bisIp,odbcConnection,server,userName = None,passWord = None):   
    
        if userName == '' or userName == None:
            self.userName = 'Administrator'
        else:
            self.userName = userName
        
        if passWord == '' or passWord == None:
            self.passWord = ''
        else:
            self.passWord = passWord
        self.boAction = boAction
        self.PortNumber = '6400'
        self.authentication = 'ENTERPRISE'
        self.boVersion = 'XI'
        self.bisIp = bisIp
        self.boRepositry = self.bisIp + ':' + self.PortNumber
        self.odbcConnection = odbcConnection
        self.baseDefinition = str(TPAPI.getBaseTPName(server))
        
        self.parameter = [];
        
        self.homeDir = os.path.expanduser('~')
        self.bointffile = self.outDirectory.split('Output')[0] + "\\Environment\\"+ self.BIversion +"\\TPIDE_BOIntf.exe"
                
        self.parameter.append(self.bointffile)
        self.parameter.append(self.boAction);
        self.parameter.append(self.userName);
        self.parameter.append(self.passWord);
        self.parameter.append(self.boRepositry);
        self.parameter.append(self.odbcConnection);
        self.parameter.append(self.versionID);
        self.parameter.append(self.baseDefinition);
        self.parameter.append(self.outDirectory);
        self.parameter.append(self.boVersion);
        self.parameter.append(self.authentication);
        
        self.backGroundTask(self.outDirectory,self.parameter,self.logger)    
   
    def createBOPackage(self, Rstate, LockedBy, License, encrypt):
        from com.distocraft.dc5000.etl.importexport import ETLCExport
        from org.apache.velocity import VelocityContext
        from org.apache.velocity.app import Velocity
        from org.apache.velocity.context import Context
        from java.util import Vector
        from tpapi.eniqInterace import VersionInfo
        from java.io import StringWriter
        from java.util import Properties
        
        vmPath = self.outDirectory.split('Output')[0]+'Environment'
        p = Properties();
        p.setProperty("file.resource.loader.path", vmPath);
        Velocity.init(p);
        
        print "outputDirectory " + str(self.outDirectory)
        
        fileList = os.listdir(self.outDirectory)
        print str(fileList)
        
        boPackageName = "BO_"+ self.name.split("_",1)[1]
        
        basdir = boPackageName + "_" + Rstate + "_" +"b" + self.version
        installDir = basdir + '\\install'
        unvDir = basdir + '\\unv'
        repDir = basdir + '\\rep'        
        
        if not os.path.exists(basdir):
            os.makedirs(basdir)
        if not os.path.exists(installDir):
            os.makedirs(installDir)
        if not os.path.exists(unvDir):
            os.makedirs(unvDir)
        if not os.path.exists(repDir):
            os.makedirs(repDir)

        outputFileName = boPackageName + "_" + Rstate + "_" +"b" + self.version + ".zip"
        
        versionProps = open(installDir+'\\version.properties','w')
        vec = Vector()
        context = VelocityContext()
        context.put("metadataversion", "")
        context.put("techpackname", boPackageName)
        context.put("author", LockedBy)
        context.put("version", Rstate)
        context.put("buildnumber", self.version)
        context.put("buildtag", self.version)
        
        licenseName = ''     
        if License != None:
            licenseName = License
        context.put("licenseName", licenseName)
        context.put("required_tech_packs", vec)
        
        strw = StringWriter()
        isMergeOk = Velocity.mergeTemplate('version.vm', Velocity.ENCODING_DEFAULT, context, strw)
        if isMergeOk:
            versionProps.write(strw.toString())
        versionProps.close()
        
        boUnvPath = self.outDirectory + "\\unv"
        boUnvFileList = os.listdir(boUnvPath)
        
        for boUnvFile in boUnvFileList:
                source = os.path.join(boUnvPath,boUnvFile)
                destination = os.path.join(unvDir,boUnvFile)
                shutil.copy(source, destination)
                
        boRepPath = self.outDirectory + "\\rep"
        boRepFileList = os.listdir(boRepPath)
        
        for boRepFile in boRepFileList:
                source = os.path.join(boRepPath,boRepFile)
                destination = os.path.join(repDir,boRepFile)
                shutil.copy(source, destination)  
                
        Z = zipfile.ZipFile(outputFileName, 'w')
        directories = ['install','unv','rep']
        for directory in directories:
            for dirpath,dirs,files in os.walk(basdir+'\\'+directory):
                for f in files:
                    if not f.endswith('.tpi'):
                        fn = os.path.join(dirpath, f)
                        Z.write(fn, directory+'\\'+f, zipfile.ZIP_DEFLATED )
        Z.close()
        
#         if encrypt == 'True':
#             shutil.copy("Unencrypted_"+outputFileName, outputFileName)
#             TPAPI.encryptZipFile(outputFileName)
    
    def backGroundTask(self,runDirectory,param,logger):
         
        self.errorLog = ''
        self.param = param
        self.logger = logger
        
        print self.param
        
        bpr = subprocess.Popen(self.param,stdout=subprocess.PIPE)
        
        while bpr.poll() is None:
            output = bpr.stdout.readline()
            print output
              
    def createDirectories(self, reqPath = None, outPath = None):
        
        ''' Set up the directory for the ENIQ files. 
        Delete contents of directory if it exists, else create the directory '''
#         if os.path.exists(reqPath):
#             fileList = os.listdir(reqPath)
#             for filename in fileList:
#                 item=os.path.join(reqPath,filename)
#                 if os.path.isfile(item): 
#                     os.remove(item)
#             
#             boRepTemplatefPath = os.path.split(os.getcwd())[0] + "\\lib\\bointf\\BoRepTemplate\\"
#             boRepTemplateFileList = os.listdir(boRepTemplatefPath)
#                 
#             for TemplateFilename in boRepTemplateFileList:
#                 source = os.path.join(boRepTemplatefPath,TemplateFilename)
#                 destination = os.path.join(reqPath,TemplateFilename)
#                 shutil.copy(source, destination)
#         
#         else:
#             os.makedirs(reqPath , 0755)
#             boRepTemplatefPath = os.path.split(os.getcwd())[0] + "\\lib\\bointf\\BoRepTemplate\\"
#             boRepTemplateFileList = os.listdir(boRepTemplatefPath)
#             for TemplateFilename in boRepTemplateFileList:
#                 source = os.path.join(boRepTemplatefPath,TemplateFilename)
#                 destination = os.path.join(reqPath,TemplateFilename)
#                 shutil.copy(source, destination)
            
        if os.path.exists(outPath):
            pass
        else:
            os.makedirs(outPath , 0755)

    
    