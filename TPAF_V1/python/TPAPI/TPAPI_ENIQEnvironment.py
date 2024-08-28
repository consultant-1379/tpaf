'''
Created on 25 Mar 2013

@author: ebrifol
'''

import TPAPI
import sys
import os

class ENIQEnvironment(object):
    
    def __init__(self,server):
        self.server = server
    
    def setupOnlaptop(self, outputPath):
        requiredList = ['repository','common','engine','scheduler','licensing', 'dwhmanager']
        libsList = ['velocity']
        dirlist = []
        
        self.createDirectories(outputPath)
        
        if str(outputPath) not in sys.path:
            sys.path.append(str(outputPath))
        
        ''' Start FTP to collect the jars from the requiredList
        Get the 3pp jars from the libs directory in ENIQ
        Get the required property files ''' 
        ftp = TPAPI.getFTPConnection(self.server, 'dcuser', 'dcuser')
        ftp.cwd('/eniq/sw/platform')
        ftp.retrlines('LIST',dirlist.append)
        for dirName in dirlist:
            directory = dirName.split(' ')[-1]
            if directory.split('-')[0] in requiredList:
                jarname = directory.split('-')[0]
                ftp.cwd(directory+'/dclib')
                fileName = open(outputPath+'\\'+jarname+'.jar', 'wb+')
                ftp.retrbinary('RETR '+jarname+'.jar', fileName.write)
                fileName.close()
                if outputPath+'\\'+jarname+'.jar' in sys.path:
                    sys.path.remove(outputPath+'\\'+jarname+'.jar')
                sys.path.append(outputPath+'\\'+jarname+'.jar')
                if directory.split('-')[0] == 'common':
                    ftp.cwd('/eniq/sw/platform/'+directory+'/classes/5.2')
                    files = ftp.nlst()
                    for fileName in files:
                        if fileName.endswith('.vm'):
                            vm = open(outputPath+'\\5.2\\'+fileName, 'wb+')
                            ftp.retrbinary('RETR '+fileName, vm.write)
                            vm.close()
                if directory.split('-')[0] == 'dwhmanager':
                    ftp.cwd('/eniq/sw/platform/'+directory+'/classes/')
                    files = ftp.nlst()
                    for fileName in files:
                        if fileName.endswith('.vm'):
                            vm = open(outputPath+'\\'+fileName, 'wb+')
                            ftp.retrbinary('RETR '+fileName, vm.write)
                            vm.close()
                ftp.cwd('/eniq/sw/platform')
            elif directory.split('-')[0] == 'libs':
                ftp.cwd(directory+'/dclib')
                jarlist = ftp.nlst()
                for jar in jarlist:
                    if jar.split('-')[0] in libsList:
                        fileName = open(outputPath+'\\'+jar, 'wb+')
                        ftp.retrbinary('RETR '+jar, fileName.write)
                        fileName.close()
                        if outputPath+'\\'+jar in sys.path:
                            sys.path.remove(outputPath+'\\'+jar)
                        sys.path.append(outputPath+'\\'+jar)
                ftp.cwd('/eniq/sw/platform')
            elif directory.split('-')[0] == 'export':
                ftp.cwd(directory+'/dclib')
                jarlist = ftp.nlst()
                for jar in jarlist:
                    fileName = open(outputPath+'\\'+jar, 'wb+')
                    ftp.retrbinary('RETR '+jar, fileName.write)
                    fileName.close()
                    if outputPath+'\\'+jar in sys.path:
                        sys.path.remove(outputPath+'\\'+jar)
                    sys.path.append(outputPath+'\\'+jar)
                ftp.cwd('/eniq/sw/platform')

        # get installer.jar
        ftp.cwd('/eniq/sw/installer/lib')
        fileName = open(outputPath+'\\installer.jar', 'wb+')
        ftp.retrbinary('RETR '+'installer.jar', fileName.write)
        fileName.close()
        if outputPath+'\\installer.jar' in sys.path:
            sys.path.remove(outputPath+'\\installer.jar')
        sys.path.append(outputPath+'\\installer.jar')
        # get anty.jar
        ftp.cwd('/eniq/sw/runtime/ant/lib')
        fileName = open(outputPath+'\\ant.jar', 'wb+')
        ftp.retrbinary('RETR '+'ant.jar', fileName.write)
        fileName.close()
        if outputPath+'\\ant.jar' in sys.path:
            sys.path.remove(outputPath+'\\ant.jar')
        sys.path.append(outputPath+'\\ant.jar')

        ftp.cwd('/eniq/sw/conf')
        if os.path.isfile(outputPath+'\\ETLCServer.properties'):
            os.remove(outputPath+'\\ETLCServer.properties')
        file = open(outputPath+'\\ETLCServer.properties', 'wb+')
        ftp.retrbinary('RETR ETLCServer.properties', file.write)
        file.close()
        
        file = open(outputPath+'\\static.properties', 'wb+')
        ftp.retrbinary('RETR static.properties', file.write)
        file.close()
                
        #Set the SystemProperty CONF_DIR to where the property file can be found. 
        from java.lang import System
        System.setProperty("CONF_DIR", outputPath+'\\')
        
        #Add custom jar for Engine and Scheduler RMI interface and Sets generation
        if outputPath + '\\ENIQInterface.jar' in sys.path:
            sys.path.remove(outputPath + '\\ENIQInterface.jar')
        sys.path.append(outputPath + '\\ENIQInterface.jar')
        #This is needed for a dummy ResourceMap used to create Interface Sets
        if outputPath + '\\appframework.jar' in sys.path:
            sys.path.remove(outputPath + '\\appframework.jar')
        sys.path.append(outputPath + '\\appframework.jar')
        if outputPath + '\\swing-worker.jar' in sys.path:
            sys.path.remove(outputPath + '\\swing-worker.jar')
        sys.path.append(outputPath + '\\swing-worker.jar')
        
        #Change the DB URL in the property file so it wont look at localhost
        file = open(outputPath+'\\ETLCServer.properties', 'r+')
        lines = file.readlines()
        file.truncate(0)
        for line in lines:
            replaceLine = line
            if line.startswith('ENGINE_DB_URL'):
                replaceLine = replaceLine.replace('jdbc:sybase:Tds:repdb', 'jdbc:sybase:Tds:'+ self.server)
            file.write(replaceLine)
        file.close()
        
        #Initialise the StaticProperties class. This is used when activating the techpack. 
        from java.util import Properties
        from java.io import FileInputStream
        from com.distocraft.dc5000.common import StaticProperties
        props = Properties()
        staticPropertiesInputStream = FileInputStream(outputPath+'\\static.properties')
        props.load(staticPropertiesInputStream);
        StaticProperties.giveProperties(props)
    
    def createDirectories(self, outputPath):
        ''' Set up the directory for the ENIQ files. 
        Delete contents of directory if it exists, else create the directory '''
       

        if os.path.exists(outputPath+'\\5.2'):
            fileList = os.listdir(outputPath+'\\5.2')
            for filename in fileList:
                item=os.path.join(outputPath+'\\5.2\\',filename)
#                 if os.path.isfile(item):
#                     if item in sys.path:
#                         sys.path.remove(item)
#                     os.remove(item)
                    
        else:
            os.makedirs(outputPath+'\\5.2' , 0755)
        
        sys.path.append(str(outputPath+'\\5.2'))
      
    def collectVelocityFile(self, ftp):            
        files = ftp.nlst()
        for file in files:
            if file.endswith('.vm'):
                vm = open(outputPath+'\\5.2\\'+file, 'wb+')
                ftp.retrbinary('RETR '+file, vm.write)
                vm.close()
        
        
    def setupOnServer(self):
        pass
        