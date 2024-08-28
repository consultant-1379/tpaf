''' TPAPI Functions'''
from __future__ import with_statement
import subprocess
import TPAPI
from xml.etree import ElementTree
from ftplib import FTP
import os
import sys
import zipfile
import zlib
import shutil
import re
import csv 
import pickle
import itertools
import logging
import warnings
import java.lang.Runtime as RT
logger = logging.getLogger('TPAPI.TPAPI_TP.TechPackVersion')

DTD = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Techpack
  [     <!ELEMENT Techpack (Versioning*)>
    <!ELEMENT Versioning (VersionInfo*,SupportedVendorReleases*,Tables*, BusyHours*, ExternalStatements*, Interfaces*)>
        <!ATTLIST Versioning name CDATA #REQUIRED >
    <!ELEMENT VersionInfo ANY>
    <!ELEMENT SupportedVendorReleases (VendorRelease*) >
    <!ELEMENT VendorRelease (#PCDATA) >
    <!ELEMENT Tables (Table*) >
    <!ELEMENT Table ANY >
        <!ATTLIST Table name CDATA #REQUIRED >
        <!ATTLIST Table tableType CDATA #REQUIRED >
        <!ATTLIST Table classification CDATA #REQUIRED >
    <!ELEMENT Attributes (Attribute*) >
    <!ELEMENT Attribute ANY>
        <!ATTLIST Attribute name CDATA #REQUIRED >
        <!ATTLIST Attribute attributeType CDATA #REQUIRED >
    <!ELEMENT Parsers (Parser*) >
    <!ELEMENT Parser (Transformations*,Dataformats*) >
        <!ATTLIST Parser type CDATA #REQUIRED >
    <!ELEMENT Transformations (OrderNo*) >
        <!ATTLIST Transformations transformerID CDATA #REQUIRED >
    <!ELEMENT OrderNo ANY>
        <!ATTLIST OrderNo index CDATA #REQUIRED >
    <!ELEMENT Dataformats (Dataformat*) >
    <!ELEMENT Dataformat (TableTags*,AttributeTags*) >
        <!ATTLIST Dataformat DataFormatID CDATA #REQUIRED >
    <!ELEMENT TableTags (TableTag*) >
    <!ELEMENT TableTag (#PCDATA) >
    <!ELEMENT AttributeTags ANY>
    <!ELEMENT BusyHours (BusyHour*)>
    <!ELEMENT BusyHour (BusyHourObjectName, RankingTable, BusyHourSupportedTables, BusyHourTypes*)>
    <!ELEMENT BusyHourObjectName (#PCDATA) >
    <!ELEMENT RankingTable (#PCDATA)>
    <!ELEMENT BusyHourSupportTables (BusyHourSupportTable*)>
    <!ELEMENT BusyHourSupportTable (#PCDATA)>
    <!ELEMENT BusyHourTypes (BusyHourType*)>
    <!ELEMENT BusyHourType ANY>
        <!ATTLIST BusyHourType name CDATA #REQUIRED>
    <!ELEMENT GroupTypes (GroupType*) >
    <!ELEMENT GroupType (Dataname*)>
        <!ATTLIST GroupType name CDATA #REQUIRED>
    <!ELEMENT Dataname (Property*)>
        <!ATTLIST Dataname name CDATA #REQUIRED>
    <!ELEMENT ExternalStatements (ExternalStatement*) >
    <!ELEMENT ExternalStatement ANY >
        <!ATTLIST ExternalStatement name CDATA #REQUIRED >
    <!ELEMENT MetaCollectionSets (MetaCollectionSet*) >
    <!ELEMENT MetaCollectionSet (ANY, MetaCollections) >
        <!ATTLIST MetaCollectionSet CollectionSetName CDATA #REQUIRED >
        <!ATTLIST MetaCollectionSet CollectionSetID CDATA #REQUIRED >
    <!ELEMENT MetaCollections (ANY, MetaTransferActions) >
        <!ATTLIST MetaCollections collectionName CDATA #REQUIRED >
    <!ELEMENT MetaTransferActions ANY>
        <!ATTLIST MetaTransferActions transferActionName CDATA #REQUIRED >
    <!ELEMENT Interfaces (Interface*) >
    <!ELEMENT Interface (IntfVersioning*,Dependencies*,Techpacks*,Configuration*)>
        <!ATTLIST Interface name CDATA #REQUIRED >
    <!ELEMENT IntfVersioning ANY >
        <!ATTLIST IntfVersioning intfVersion CDATA #REQUIRED >
    <!ELEMENT Dependencies ANY>
    <!ELEMENT Techpacks ANY>
    <!ELEMENT Configuration ANY>
  ]>
'''

def unzipTpi(tpiFile,outDir):
    '''Unzips a tpi (tpiFile) file to the specified output directory. Function
    
    tpiFile: tpiFile to be extracted
    outDir: Output directory destination
    
   Exceptions:
            Raised if the file does not end with .tpi
            Raised if its not a valid zipfFile'''
       
    logger.debug("TPAPI.unzipTpi() on file" +tpiFile)
    extractDirName = tpiFile.split('.')[0]
    if os.path.splitext(tpiFile)[1] != '.tpi':
        strg = "TPAPI.unzipTpi() file " +tpiFile + " : is not a .tpi file.. exiting"
        logger.debug(strg)
        raise Exception(strg)
        
    if not zipfile.is_zipfile(tpiFile):
        strg()
        logger.debug("TPAPI.unzipTpi() file " +tpiFile + " is not a valid zip file..exiting")
        logger.debug(strg)
        raise Exception(strg)
    
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
               
    os.mkdir(outDir)
    
    zfile = zipfile.ZipFile(tpiFile)
    for name in zfile.namelist():
        (dirName, fileName) = os.path.split(name)
        
        newDir = outDir + '/' + dirName
        if not os.path.exists(newDir):
            os.mkdir(newDir)
        
        if fileName != '':
            # file
            fd = open(outDir + '/' + name, 'wb')
            fd.write(zfile.read(name))
            fd.close()

    zfile.close()

def copyTpiToTemp(filePath):
    tpifilename = filePath.split('/')[-1]
    copyPath = sys.getBaseProperties().getProperty("user.home")+'\\TPAF\\tpi_tmp'
    
    if os.path.exists(copyPath):
        shutil.rmtree(copyPath)
              
    os.mkdir(copyPath)
    
    shutil.copyfile(filePath, copyPath + '/' + tpifilename)
    return copyPath + '/' + tpifilename

def encryptZipFile(filePath):
    from com.ericsson.procus.tpaf.encryption import ZipCrypter
    
    keymodulate='123355219375882378192369770441285939191353866566017497282747046709534536708757928527167390021388683110840288891057176815668475724440731714035455547579744783774075008195670576737607241438665521837871490309744873315551646300131908174140715653425601662203921855253249615512397376967139410627761058910648132466577'
    keyexponent='56150463164644751914716495900093720157414415481292002669315194431219529412326876784449358059082155035515624734089410543128644396470938683386571095646717819191489425302090971582044719505456351962678152676022843274039720191188252080851399964166276217240881859709097082858039511039553656980967803072308827430913'
    
    if filePath:
        zipCrypter = ZipCrypter()            
        zipCrypter.setFile(filePath)
        zipCrypter.setCryptType('encrypt')
        zipCrypter.setIsPublicKey('false')
        zipCrypter.setKeyModulate(keymodulate)
        zipCrypter.setKeyExponent(keyexponent)
        zipCrypter.execute()
        
def decryptTpiFile(filename):
   
    from com.ericsson.procus.tpaf.encryption import ZipCrypter
    from com.ericsson.procus.tpaf.encryption import ZipCrypterExtractor
    cryptMode = 'decrypt'
    ISPUBLICKEY = 'true'
    if filename:
        zipCrypterExtract = ZipCrypter()
        zipCrypterExtract.setFile(filename)
        zipCrypterExtract.setCryptType(cryptMode)
        zipCrypterExtract.setIsPublicKey(ISPUBLICKEY)
        zipCrypterExtract.execute()


def getFTPConnection(host, user, password):
    return FTP(host, user, password)

def getENIQversion(ftp):
    filePath = sys.getBaseProperties().getProperty("user.home")+'\\TPAF\\eniq_status.txt'
    file = open(filePath, 'wb')
    ftp.retrbinary('RETR /eniq/admin/version/eniq_status', file.write)
    file.close()
    f=open(filePath, 'r')
    version = f.readline().split(' ')[1].split('_')[3]
    f.close()
    os.remove(filePath)
    return version               
            
def getBaseTPName(server):
    with TPAPI.DbAccess(server,'dwhrep') as crsr:
        crsr.execute("SELECT VERSIONID from dwhrep.Versioning where TECHPACK_TYPE =?", ('BASE',))
        baseTPs = TPAPI.rowToList(crsr.fetchall()) 
        return sorted(baseTPs)[-1]

def printMem():
    '''Prints System Memory'''
    rt = RT.getRuntime()
    mb = 1024*1024
    free = rt.freeMemory() / mb
    tot = rt.totalMemory() / mb
    print "Free Memory:" + str(free) + "Mb"
    print "Used Memory:" + str((tot - free)) + "Mb"
    print "Total Memory:" + str(tot) + "Mb"

def printRow(resultset):
    ''' Print a row'''
    for row in resultset:
        numofcols = len(row)
        while numofcols > 0: 
            print row[numofcols-1] + " |" ,
            numofcols-= 1
        print "\n",

def printColumnNames(desc):
    '''Print column Names for the result'''
    for x in desc:
        print x[0]
        
def dictToSQL(mydict,tablename):
    '''Prepare SQL from a dict'''
    # one row!
    dictCopy = mydict
    for k,v in dictCopy.items():
        if v is None:
            del dictCopy[k] 
        sql = 'INSERT INTO dwhrep.' +tablename
        sql += ' ('
        sql += ', '.join(dictCopy)
        sql += ') VALUES ('
        sql += ','.join(map(pad,dictCopy))
        sql += ');'
        values = dictCopy.values()
    return sql,values

def pad(key):
    '''Used during sql updates'''
    return '?'

def rowToDictionary(row, desc):
    '''Conver a row to a dictionary'''
    mydict = {}
    i = 0
    for x in desc:
        mydict[x[0]] = row[i]
        i+=1
    return mydict
                             
def rowToList(resultset):
    '''Convert single column resultset to a list'''
    mylist = []
    for i in resultset:
        mylist.append(i[0],)
    return mylist     

def printDict(dictionary):    
    '''Print Dictionary'''
    for i in dictionary:
        print i +  "=" + str(dictionary[i])
        
def compareRStates(rstate1,rstate2):
    '''Compare two rstates 
        
        returns -1 if rtate1 is newer than rstate2, 0 if they are equal and 1 if rstate is older than rstate2'''
    if rstate1[0] == 'R' and rstate2[0] == 'R':
        if rstate1[1:-1].isdigit and rstate2[1:-1].isdigit:
            digit1 = rstate1[1:-1]
            digit2 = rstate2[1:-1]
            if int(digit1) > int(digit2):
                return -1
            elif int(digit1) == int(digit2):
                if rstate1[-1].isalpha and rstate2[-1].isalpha:
                    alpha1 = rstate1[-1]
                    alpha2 = rstate2[-1]
                    if alpha1 > alpha2:
                        return -1
                    elif alpha1 == alpha2:
                        return 0
                    else:
                        return 1
            else:
                return 1

def pingServer(addr):
    '''Returns a True or False value if the server is pingable'''
    return_code = True
    if os._name == "nt":  # running on windows
        cmd = "ping -n 1 %s" % addr
    else: 
        cmd = "/usr/sbin/ping %s" % addr
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        retcode = p.wait()
        if retcode == 1:
            return_code = False
        else:
            return_code = True
    except subprocess.CalledProcessError:
        return_code = False
    return return_code

def safeNull(elementText):
    '''Converts a None type object to an empty string.Used by FromXML methods for handling element tags with empty
    values'''
    if elementText == None:
        elementText = ''
        return elementText
    else:
        return elementText.strip() 
    
def strFloatToInt(value):
    '''Converts string float to string int'''
    value = str(value).replace(".0", "")
    return value

def checkNull(inputStr):
    '''Check if string is null'''
    if inputStr == 'null' or inputStr == 'None':
        return ''
    else:
        return inputStr
    
def fileToXMLObject(xmlfile):
    '''Convert File to XML Object'''
    xmlString = xmlfile.read()
    xmlObject = ElementTree.fromstring(xmlString)
    return xmlObject
    
def escape(text):
    '''return text that is safe to use in an XML string'''
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        ">": "&gt;",
        "<": "&lt;",
    }   
    return "".join(html_escape_table.get(c,c) for c in str(text))

def unescape(s):
    '''change XML string to text'''
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&")
    return s    

def pickleTechpack(VersionID,server):
    '''Function to convert techpack to python bytestream. For Faster testing - No need to load from tpi or server'''
    tpv = TPAPI.TechPackVersion(VersionID)
    tpv.getPropertiesFromServer(server)
    myPickle = pickle()
    myPickle.dump(tpv, file.open('testpickle',"w"))
    
def getTechpackDwhInfo(server,VersionID):
    ''' Retrieves DWH info of tech pack
    
        Returns: A Dictionary structure of all tables and  columns
    
    '''
    with TPAPI.DbAccess(server,'dwhrep') as crsr:
        temp = "%"+VersionID+"%"
        tables = []
        tpDwhInfo = {}
        crsr.execute("SELECT BASETABLENAME FROM dwhrep.MeasurementTable WHERE MTABLEID like ?", (temp,))
        resultset = crsr.fetchall()
        for row in resultset:
            tables.append(str(row[0]))
        for table in tables:
            tablename = VersionID + ":"+str(table) 
            crsr.execute("SELECT DATANAME FROM dwhrep.MeasurementColumn WHERE MTABLEID like ?",(str(tablename),))
            resultset = crsr.fetchall()
            i = 0
            columns = []
            for row in resultset:
                columns.append(str(row[0]))
                i =i+1
            tpDwhInfo[str(table)] = columns
    return tpDwhInfo   
    
   
def writeXMLFile(toXMLString,filename):
    '''Writes an XMLString to a file'''
    
    print "writeXMLFile"
    fh = open(filename,"w")
    offset = 0
    os = "\n" + " "*offset
    os2 = os + " "*offset
    fh.writelines(DTD)
    fh.writelines(toXMLString)
    fh.close()
    return

def getTechPacks(server):
    '''Get list of all techpacks on a server.
    
    Returns:
            List of Techpacks on the server
    
    '''
    techpacks=[]
    db = TPAPI.DbAccess(server, "dwhrep")
    try:
        crsr = db.getCursor() 
        crsr.execute("SELECT DISTINCT VERSIONID FROM dwhrep.Versioning")
        for i in crsr.fetchall():
            techpacks.append(i[0])
    finally:
        del db 
    return techpacks

def getTechPackVersions(server):
    '''get list of all techpacks on a server.
    
    Returns:
            Dictionary of tchpack versions on the server
    '''
    techpackVersions ={}
    db = TPAPI.DbAccess(server, "dwhrep")
    try:
        crsr = db.getCursor() 
        crsr.execute("SELECT VERSIONID,TECHPACK_NAME,TECHPACK_VERSION FROM dwhrep.Versioning ORDER BY VERSIONID")
        for i in crsr.fetchall():
            techpackVersions[i[0]]=(i[1],i[2])
    finally:
        del db 
    return techpackVersions

def getInterfaces(server):
    '''get list of all interfaces on the server'''
    '''Columns:INTERFACENAME,STATUS,INTERFACETYPE,DESCRIPTION,DATAFORMATTYPE,INTERFACEVERSION,LOCKEDBY,LOCKDATE,PRODUCTNUMBER,ENIQ_LEVEL,RSTATE'''
    interfaces=[]
    db = TPAPI.DbAccess(server, "dwhrep")
    try:
        crsr = db.getCursor() 
        crsr.execute("SELECT INTERFACENAME,INTERFACEVERSION,DATAFORMATTYPE,RSTATE FROM dwhrep.DataInterface")
        c = 0
        for res in crsr.fetchall():
            interfaces.append([])
            interfaces[c].append(res[0])
            interfaces[c].append(res[1])
            interfaces[c].append(res[2])
            interfaces[c].append(res[3])
            c+=1 
    finally:
        del db
    return interfaces

def getRepositoryInfo(server):
        '''return a nested dictionary of the dwhrep structure, containing tables,column and column parameters'''
        dwhrepDict = {}
        db = TPAPI.DbAccess(server, "DBA")
        try:
            crsr = db.getCursor()
            crsr.execute("SELECT table_name FROM sys.systable where creator=104")
            resultset = crsr.fetchall()
            for row in resultset:
                tableName = row[0].rstrip()
                dwhrepDict[tableName] = {}
                crsr.execute("select CNAME,coltype,length,nulls,default_value from sys.syscolumns where TNAME =?",(tableName,))
                rset2 = crsr.fetchall()
                for column in rset2:
                    dwhrepDict [tableName][column[0]] = {'coltype':column[1],'lenght':column[2],'nulls':column[3],'default_value':column[4]}
        finally:
                del db 
        return  dwhrepDict 

def compareRepositories(dwhrepDict1,dwhrepDict2):
        '''Compare Tables & Keys and properties of two dwhreps'''
        additionalTables = {}
        modifiedTables = {}
        if len(dwhrepDict1) > len(dwhrepDict2):
            print "extra tables found in first rep"
            for table in dwhrepDict1:
                if table not in dwhrepDict2:
                    print "extra table is " + table
                    additionalTables[table] = {}
                if table in dwhrepDict2:
                    if len(dwhrepDict1[table]) > len(dwhrepDict2[table]):
                        print "extra columns found in " + table
                        modifiedTables[table] = {}
                    else:
                        pass
        print "                                    "
        print "New Tables"
        print "                                    "    
        for addTable in additionalTables:
            print "NEW TABLE: " + addTable
            print "****************************"
            for column in dwhrepDict1[addTable]:
                print str(column)
            print "*****************************" 
        print "                                    "
        print "New Columns in Existing Tables"
        print "                                    "         
        for modTable in modifiedTables:
            print "*****************************"
            print modTable
            for column in dwhrepDict1[modTable]:
                if column not in dwhrepDict2[modTable]:
                    print "NEW COLUMN :" + str(column) 
            print "*****************************"

def generate_dicts(cur):    
    ''' easy access to data by column name
        example usage:
            versionID = 'DC_E_BSS:((66))'
            with TPAPI.DbAccess(server,'dwhrep') as crsr:
                crsr.execute("SELECT * from dwhrep.Versioning WHERE VERSIONID =?", (versionID,))
                for row in TPAPI.generate_dicts(crsr):
                    print row['TECHPACK_NAME'], row['TECHPACK_VERSION'], row['DESCRIPTION'] 
    '''
    column_names = [d[0].upper() for d in cur.description ]
    while True:
        rows = cur.fetchall()
        if not rows:
            return 
        for row in rows:
            yield dict(itertools.izip(column_names, row))   
           
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    import warnings
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

class DictDiffer(object):
    """
    Class for calculating the difference between two dictionaries.
    
    """
    def __init__(self, current_dict, past_dict):
        '''Initialised with the two dictionary objects to be compared'''
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        '''Returns:
                Dictionary of added items'''
        return self.set_past - self.intersect 
    def removed(self):
        '''Returns:
                Dictionary of removed items'''
        return self.set_current - self.intersect 
    def changed(self):
        '''Returns:
                Dictionary of changed items'''
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        '''Returns:
                Dictionary of unchanged items'''
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
    def common(self):
        '''Returns:
                Dictionary of common items'''
        return self.intersect
  
class TpiDict(object):
    '''Class for extraction and intermediate storage of metadata from inside a tpi file.'''
    
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TpiDict, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance    
    
    def __init__(self,filename=None,directory=None):
        self.logger = logging.getLogger('TPAPI.TPAPI_Util.tpiDict()')
        if filename == None and directory == None:
            self.logger.error('TPAPI.TPAPI_Util.tpiDict() error no filename or directory specified..exiting')
            return
        
        
        self.tpidict = {}
        tpis = [] 
        extractedDirs = [] 
        self.filename = filename
        self.directory = directory
        self.interfaceSql = False
        BaseDest = sys.getBaseProperties().getProperty("user.home")+'\\TPAF\\tpi_tmp'
        unzipDest = BaseDest + '\\unzip'
        
        if filename is not None:
            if os.path.exists(filename):
                self.logger.debug('TPAPI.TPAPI_Util.tpiDict() file ' + filename + 'exists')
                fileName = os.path.basename(filename)
                directoryName = os.path.dirname(filename)
                if directoryName != '':
                    absInputDir = os.path.abspath(directoryName)
                else:
                    # No path found, use current directory
                    absInputDir = os.path.abspath(os.path.dirname(os.getcwd()))
                filePath = os.path.join(absInputDir,fileName)
                #unzipDest = os.path.join(absInputDir,'tmp')                
                
                self.logger.info('TPAPI.TPAPI_Util.tpiDict() unzipping  ' + filePath)
                TPAPI.unzipTpi(filePath,unzipDest)
                extractedDirs.append(unzipDest)
               
        elif directory is not None:
            if os.path.isdir(directory):
                absInputDir = os.path.abspath(directory)
                for myfile in os.listdir(absInputDir):
                    if myfile.endswith(".tpi"):
                        if fileName.find('INTF_') == 0:
                            self.interfaceSql = True
                        tpiFile = os.path.join(absInputDir,myfile)
                        destDir = os.path.join(absInputDir,'/tmp')
                        TPAPI.unzipTpi(tpiFile,destDir)
                        tpis.append(myfile)
                        extractedDirs.append(myfile.split('.')[0])

        for dir in extractedDirs:
            if os.path.exists(os.path.join(absInputDir,dir)):
                # Dirs contained in  the tpi file
                for dir2 in os.listdir(os.path.join(absInputDir,dir)):
                    for fileName in os.listdir(os.path.join(absInputDir,dir,dir2)):
                        if fileName.find('Tech_Pack') == 0:    
                            if re.match('.*(\.sql)',fileName):
                                path = os.getcwd()
                                sqlFile = open(os.path.join(absInputDir,dir,dir2,fileName))
                                lines = sqlFile.readlines()
                                count=0
                                
                                testString = ''
                                string = ''
                                completelines=[]
                                while count <= len(lines)-1:
                                    if self.interfaceSql:
                                        testString = lines[count]
                                        if len(testString) > 2 and not testString.startswith('--'):
                                            string = string + lines[count]
                                            if re.match('.*\)(\r)?', string):
                                                completelines.append(string)
                                                string = ''
                                    else:
                                        string = string + lines[count]
                                        if string[:-1].endswith(');'):
                                            completelines.append(string)
                                            string = ''     
                                    count = count +1   
                                for line in completelines:
                                    matchObj = re.match('insert into\s(.+?)[\s|\(]\(?.+? ',line)
                                    tableName = matchObj.group(1) 
                                    if tableName not in self.tpidict:
                                        self.tpidict[tableName] = {}                      
                                    columns = line[line.find('(')+1:line.find(')')].split(',')
                                    if self.interfaceSql :
                                        vals = line[line.find('(',line.index(')'))+1:-2]
                                    else:
                                        vals = line[line.find('(',line.index(')'))+1:-3]
                                    p=[]
                                    p.append(vals)
                                    testReader = csv.reader(p,quotechar="'", skipinitialspace=True)
                                    for row in testReader:   
                                        for col,val in zip(columns,row):
                                            col = col.strip()
                                            val = val.strip().strip("'")
                                            val = val.rstrip('\\')                 
                                            if col not in self.tpidict[tableName]:
                                                self.tpidict[tableName][col] = {}
                                            self.tpidict[tableName][col][len(self.tpidict[tableName][col])+1 ] =  val

                                sqlFile.close()
                            elif re.match('.*(\.xml)',fileName):
                                if self.interfaceSql:
                                    xmlFile = open(os.path.join(absInputDir,dir,dir2,fileName),"rb")
                                    for line in xmlFile:
                                        # escape commas found in the description field
                                        line = re.sub("'.+\s,'.+(,).+'\s,.+'",' &comma ',line)
                                        matchObj = re.search('.+<(.+?)\s.+?',line)
                                        #index = 0
                                        if matchObj:
                                            tableName = matchObj.group(1)
                                            if tableName not in self.tpidict:
                                                self.tpidict[tableName] = {}
                                                index = 0
                                            matchObj1 = re.search('.+<.+?\s(.+?)/>',line)
                                            if matchObj1:
                                                kevals = matchObj1.group(1)
                                            mysplit = re.split('"\s', kevals)
                                            
                                            for entry in mysplit:
                                                # Where clause can have multiple equals signs which mess up the splitting of the string
                                                s = re.split('="',entry)
                                                if len(s) > 1:
                                                    column =  s[0]
                                                    value = s[1].strip('"')
                                                if column not in self.tpidict[tableName]:
                                                    self.tpidict[tableName][column] = {} 
                                                self.tpidict[tableName][column][str(index)] =  value
                                            index = index + 1
                                    xmlFile.close()
        #shutil.rmtree(BaseDest)
               
    def printDict(self):
        f = open('tpiDict.txt', 'w')
        for table in self.tpidict:
            f.write("table is " + table +"\n")
            for column in self.tpidict[table]:
                f.write("column is " + column+"\n")
                for row in self.tpidict[table][column]:
                    f.write("row is " + str(row)+"\n")
                    f.write("value is " +self.tpidict[table][column][row]+"\n")

    def returnTPIDict(self):
        return self.tpidict      


class XlsDict(object):
    '''Class for extraction and intermediate storage of metadata from inside a xls file.'''
    
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(XlsDict, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    VersioningDict = {'Name': 'TECHPACK_NAME', 'Description': 'DESCRIPTION', 'Release': 'TECHPACK_VERSION',
                      'Product number': 'PRODUCT_NUMBER', 'License': 'LICENSENAME', 'Type': 'TECHPACK_TYPE',
                      'Supported Versions': 'VENDORRELEASE', 'Build Number': 'BUILD_NUMBER', 'Dependency TechPack': 'Dependency'}
    InterfaceDict = {'Interface R-State': 'RSTATE', 'Interface Type': 'INTERFACETYPE', 'Description': 'DESCRIPTION', 
                     'Tech Pack': 'intfTechpacks', 'Dependencies': 'dependencies', 'Parser Name': 'DATAFORMATTYPE', 
                     'Element Type': 'ELEMTYPE'}
    FactTableDict = {'Fact Table Description': 'DESCRIPTION',  'Universe Class': 'CLASSIFICATION',
                  'Table Sizing': 'SIZING', 'Total aggregation': 'TOTALAGG', 'Object BHs': 'OBJECTBH', 'Element BHs': 'ELEMENTBHSUPPORT',
                  'Rank Table': 'RANKINGTABLE', 'Count Table': 'DELTACALCSUPPORT', 'Vector Table': 'VECTORSUPPORT', 'Plain Table': 'PLAINTABLE',
                  'Universe Extension': 'UNIVERSEEXTENSION', 'Joinable': 'JOINABLE'}
    FTKeysDict = {'Key Description': 'DESCRIPTION', 'Data type': 'DATATYPE', 'Duplicate Constraint': 'UNIQUEKEY',
                  'Nullable': 'NULLABLE', 'IQ Index': 'INDEXES', 'Universe object': 'UNIVOBJECT',
                  'Element Column': 'ISELEMENT', 'IncludeSQL': 'INCLUDESQL'}
    FTCountersDict = {'Counter Description': 'DESCRIPTION', 'Data type': 'DATATYPE', 'Time Aggregation': 'TIMEAGGREGATION',
                  'Group Aggregation': 'GROUPAGGREGATION', 'Universe Object': 'UNIVOBJECT', 'Universe Class': 'UNIVCLASS',
                  'Counter Type': 'COUNTERTYPE', 'IncludeSQL': 'INCLUDESQL'}
    VectorsDict = {'From': 'VFROM', 'To': 'VTO', 'Vector Description': 'MEASURE'}
    TopTableDict = {'Topology Table Description': 'DESCRIPTION', 'Source Type': 'UPDATE_POLICY'}
    TopKeysDict = {'Key Description': 'DESCRIPTION', 'Data type': 'DATATYPE', 'Duplicate Constraint': 'UNIQUEKEY', 
                   'Nullable': 'NULLABLE', 'Universe Class': 'UNIVERSECLASS', 'Universe Object': 'UNIVERSEOBJECT', 
                   'Universe Condition': 'UNIVERSECONDITION', 'IncludeSQL': 'INCLUDESQL', 'Include Update': 'INCLUDEUPD'}
    TransDict = {'Transformation Type': 'TYPE', 'Transformation Source': 'SOURCE', 'Transformation Target': 'TARGET', 
                 'Transformation Config': 'CONFIG'}
    BHDict = {'Description': 'DESCRIPTION', 'Where Clause': 'WHERECLAUSE', 'Criteria': 'BHCRITERIA', 
              'Aggregation Type': 'AGGREGATIONTYPE', 'Loopback': 'LOOKBACK', 'P Threshold': 'P_THRESHOLD', 'N Threshold': 'N_THRESHOLD'}
    ESDict = {'Database Name': 'DBCONNECTION', 'Definition': 'STATEMENT'}
    RODict = {'Fact Table': 'MEASTYPE', 'Level': 'MEASLEVEL', 'Object Class': 'OBJECTCLASS', 'Object Name': 'OBJECTNAME'}
    RCDict = {'Fact Table': 'FACTTABLE', 'Level': 'VERLEVEL', 'Condition Class': 'CONDITIONCLASS', 'Condition': 'VERCONDITION',
              'Prompt Name (1)': 'PROMPTNAME1', 'Prompt Value (1)': 'PROMPTVALUE1', 'Prompt Name (2)': 'PROMPTNAME2', 
              'Prompt Value (2)': 'PROMPTVALUE2', 'Object Condition': 'OBJECTCONDITION', 'Prompt Name (3)': 'PROMPTNAME3', 
              'Prompt Value (3)': 'PROMPTVALUE3'}
    UniExtDict = {'Universe Ext Name': 'UNIVERSEEXTENSIONNAME'}
    UniTableDict = {'Topology Table Owner': 'OWNER', 'Table Alias': 'ALIAS', 'Universe Extension': 'UNIVERSEEXTENSION'}
    UniClassDict = {'Class Description': 'DESCRIPTION', 'Parent Class Name': 'PARENT', 'Universe Extension': 'UNIVERSEEXTENSION'}
    UniObjDict = {'Unv. Class': 'UniverseClass', 'Unv. Description': 'DESCRIPTION', 'Unv. Type': 'OBJECTTYPE', 'Unv. Qualification': 'QUALIFICATION',
                  'Unv. Aggregation': 'AGGREGATION', 'Select statement': 'OBJSELECT', 'Where Clause': 'OBJWHERE', 
                  'Prompt Hierarchy': 'PROMPTHIERARCHY', 'Universe Extension': 'UNIVERSEEXTENSION'}
    UniConDict = {'Condition Description': 'DESCRIPTION', 'Where Clause': 'CONDWHERE', 'Auto generate': 'AUTOGENERATE', 
                  'Condition object class': 'CONDOBJCLASS', 'Condition object': 'CONDOBJECT', 'Prompt Text': 'PROMPTTEXT', 
                  'Multi selection': 'MULTISELECTION', 'Free text': 'FREETEXT', 'Universe Extension': 'UNIVERSEEXTENSION'}
    UniJoinsDict = {'Source Table': 'SOURCETABLE', 'Source Level': 'SOURCELEVEL', 'Source Columns': 'SOURCECOLUMN',
                    'Target Table': 'TARGETTABLE', 'Target Level': 'TARGETLEVEL', 'Target Columns': 'TARGETCOLUMN',
                    'Join Cardinality': 'CARDINALITY', 'Contexts': 'CONTEXT', 'Excluded contexts': 'EXCLUDEDCONTEXTS', 
                    'Universe Extension': 'UNIVERSEEXTENSION'}
    verObjDict = {'Fact Table': 'MEASTYPE', 'Level': 'MEASLEVEL','Object Class': 'OBJECTCLASS','Object Name': 'OBJECTNAME'}
    verConDict = {'Fact Table': 'FACTTABLE', 'Level': 'VERLEVEL','Condition Class': 'CONDITIONCLASS','Condition': 'VERCONDITION',
                  'Prompt Name (1)': 'PROMPTNAME1', 'Prompt Value (1)': 'PROMPTVALUE1','Prompt Name (2)': 'PROMPTNAME2','Prompt Value (2)': 'PROMPTVALUE2',
                  'Object Condition': 'OBJECTCONDITION', 'Prompt Name (3)': 'PROMPTNAME3','Prompt Value (3)': 'PROMPTVALUE3'}
    
    updatePolicylist = ["Static", "Predefined", "Dynamic", "Timed Dynamic", "History Dynamic" ]
    
    def __init__(self,filename=None):
        self.logger = logging.getLogger('TPAPI.TPAPI_Util.XlsDict()')
        if filename == None:
            self.logger.error('TPAPI.TPAPI_Util.XlsDict() error no filename or directory specified..exiting')
            return
                
        from java.io import File
        from jxl import Workbook
        from jxl import Sheet       #These imported are not referenced directly but they are required. 
        from jxl import Cell
        
        self.xlsdict = {}
        workbook = Workbook.getWorkbook(File(filename)) #Open the FD
        
        #CoverSheet and Versioning information
        sheet = workbook.getSheet('Coversheet')
        self.xlsdict['Versioning'] = {}
        for FDColumn, Parameter in self.VersioningDict.iteritems():
            rowNumber = sheet.findCell(FDColumn).getRow()
            value = sheet.getRow(rowNumber)[1].getContents()
            value = value.strip()
            if Parameter == 'VENDORRELEASE':
                value = value.split(',')
            self.xlsdict['Versioning'][Parameter] = value
        
        #Interfaces
        sheet = workbook.getSheet('Interfaces')
        self.xlsdict['Interfaces'] = {}
        rowNumber = sheet.findCell('Interface').getRow()
        IntfNameRow = sheet.getRow(rowNumber)
        del IntfNameRow[0] #Remove the header entry
        for intfNameCell in IntfNameRow:
            intfName = intfNameCell.getContents()
            if intfName != '':
                self.xlsdict['Interfaces'][intfName] = {}
                self.xlsdict['Interfaces'][intfName]['intfConfig'] = {}
                HeaderCol = sheet.getColumn(0)
                del HeaderCol[0]
                for rowCell in HeaderCol:
                    headerValue = rowCell.getContents()
                    value = ''
                    try:
                        value = sheet.getColumn(intfNameCell.getColumn())[rowCell.getRow()].getContents()
                        self.xlsdict['Interfaces'][intfName][self.InterfaceDict[headerValue]] = self.encodeValue(value)
                    except:
                        self.xlsdict['Interfaces'][intfName]['intfConfig'][headerValue] = self.encodeValue(value)
        
        #Fact tables 
        sheet = workbook.getSheet('Fact Tables')
        self.xlsdict['Tables'] = {}
        columnNumber = sheet.findCell('Fact Table Name').getColumn()
        TableNameColumn = sheet.getColumn(columnNumber)
        del TableNameColumn[0]
        for tableNameCell in TableNameColumn:
            tableName = tableNameCell.getContents().strip()
            if tableName != '':
                self.xlsdict['Tables'][tableName] = {}
                self.xlsdict['Tables'][tableName]['TABLETYPE'] = 'Measurement'
            HeaderRow = sheet.getRow(0)
            del HeaderRow[0]
            for colCell in HeaderRow:
                headerValue = colCell.getContents()
                value = ''
                try:
                    value = sheet.getRow(tableNameCell.getRow())[colCell.getColumn()].getContents()
                    if value == 'Y' or value == 'y':
                        value = 1
                    self.xlsdict['Tables'][tableName][self.FactTableDict[headerValue]] = self.encodeValue(value)
                except:
                    if value != '':
                        if 'Parser' not in self.xlsdict['Tables'][tableName]:
                            self.xlsdict['Tables'][tableName]['Parser'] = {}
                        if headerValue not in self.xlsdict['Tables'][tableName]['Parser']:
                            self.xlsdict['Tables'][tableName]['Parser'][headerValue] = {}
                        if 'DATATAGS' not in self.xlsdict['Tables'][tableName]['Parser'][headerValue]:
                            self.xlsdict['Tables'][tableName]['Parser'][headerValue]['DATATAGS'] = {}
                        self.xlsdict['Tables'][tableName]['Parser'][headerValue]['DATATAGS'] = value
        
        #Fact table Keys
        sheet = workbook.getSheet('Keys')
        FTcol = sheet.getColumn(sheet.findCell('Fact Table Name').getColumn())
        del FTcol[0]
        KNcol = sheet.getColumn(sheet.findCell('Key Name').getColumn())
        del KNcol[0]
        for KeyNameCell in KNcol:
            KeyName = KeyNameCell.getContents().strip()
            if KeyName.strip() != '':
                tableName = FTcol[KeyNameCell.getRow()-1].getContents().strip()
                if 'measurementKey' not in self.xlsdict['Tables'][tableName]:
                    self.xlsdict['Tables'][tableName]['measurementKey'] = {}
                self.xlsdict['Tables'][tableName]['measurementKey'][KeyName] = {}
                tempDict = self.parseFDRows(self.FTKeysDict, sheet, self.xlsdict['Tables'][tableName]['measurementKey'], KeyNameCell, False)
                self.xlsdict['Tables'][tableName]['measurementKey'] = tempDict
        
        #Fact table Counters
        sheet = workbook.getSheet('Counters')
        FTcol = sheet.getColumn(sheet.findCell('Fact Table Name').getColumn())
        del FTcol[0]
        CNcol = sheet.getColumn(sheet.findCell('Counter Name').getColumn())
        del CNcol[0]
        for CounterNameCell in CNcol:
            CounterName = CounterNameCell.getContents()
            if CounterName != '':
                tableName = FTcol[CounterNameCell.getRow()-1].getContents().strip()
                if 'measurementCounter' not in self.xlsdict['Tables'][tableName]:
                    self.xlsdict['Tables'][tableName]['measurementCounter'] = {}
                self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName] = {}
                tempDict = self.parseFDRows(self.FTCountersDict, sheet, self.xlsdict['Tables'][tableName]['measurementCounter'], CounterNameCell, False)
                self.xlsdict['Tables'][tableName]['measurementCounter'] = tempDict
        
        #Vectors
        sheet = workbook.getSheet('Vectors')
        FTcol = sheet.getColumn(sheet.findCell('Fact Table Name').getColumn())
        del FTcol[0]
        CNcol = sheet.getColumn(sheet.findCell('Counter Name').getColumn())
        del CNcol[0]
        VRcol = sheet.getColumn(sheet.findCell('Vendor Release').getColumn())
        del VRcol[0]
        Incol = sheet.getColumn(sheet.findCell('Index').getColumn())
        del Incol[0]
        for IndexCell in Incol:
            index = IndexCell.getContents()
            if index != '':
                vendRel = VRcol[IndexCell.getRow()-1].getContents().strip()
                CounterName = CNcol[IndexCell.getRow()-1].getContents().strip()
                tableName = FTcol[IndexCell.getRow()-1].getContents().strip()
                if 'Vectors' not in self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]:
                    self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors'] = {}
                if vendRel not in self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors']:
                    self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors'][vendRel] = {}
                self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors'][vendRel][index] = {}
                tempDict = self.parseFDRows(self.VectorsDict, sheet, self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors'][vendRel], IndexCell, False)
                self.xlsdict['Tables'][tableName]['measurementCounter'][CounterName]['Vectors'][vendRel] = tempDict
        
        #Topology table
        sheet = workbook.getSheet('Topology Tables')
        columnNumber = sheet.findCell('Topology Table Name').getColumn()
        TableNameColumn = sheet.getColumn(columnNumber)
        del TableNameColumn[0]
        for tableNameCell in TableNameColumn:
            tableName = tableNameCell.getContents()
            if tableName != '':
                self.xlsdict['Tables'][tableName] = {}
                self.xlsdict['Tables'][tableName]['TABLETYPE'] = 'Reference'
            HeaderRow = sheet.getRow(0)
            del HeaderRow[0]
            for colCell in HeaderRow:
                headerValue = colCell.getContents()
                value = ''
                try:
                    value = sheet.getRow(tableNameCell.getRow())[colCell.getColumn()].getContents()
                    if self.TopTableDict[headerValue] == 'UPDATE_POLICY':
                        value = str(self.updatePolicylist.index(value))
                    self.xlsdict['Tables'][tableName][self.TopTableDict[headerValue]] = value
                except:
                    if value != '':
                        if 'Parser' not in self.xlsdict['Tables'][tableName]:
                            self.xlsdict['Tables'][tableName]['Parser'] = {}
                        if headerValue not in self.xlsdict['Tables'][tableName]['Parser']:
                            self.xlsdict['Tables'][tableName]['Parser'][headerValue] = {}
                        if 'DATATAGS' not in self.xlsdict['Tables'][tableName]['Parser'][headerValue]:
                            self.xlsdict['Tables'][tableName]['Parser'][headerValue]['DATATAGS'] = {}
                        self.xlsdict['Tables'][tableName]['Parser'][headerValue]['DATATAGS'] = value
                        
        #Topology Keys
        sheet = workbook.getSheet('Topology Keys')
        TTcol = sheet.getColumn(sheet.findCell('Topology Table name').getColumn())
        del TTcol[0]
        KNcol = sheet.getColumn(sheet.findCell('Key Name').getColumn())
        del KNcol[0]
        for KeyNameCell in KNcol:
            KeyName = KeyNameCell.getContents()
            tableName = TTcol[KeyNameCell.getRow()-1].getContents()
            if 'referenceKey' not in self.xlsdict['Tables'][tableName]:
                self.xlsdict['Tables'][tableName]['referenceKey'] = {}
            self.xlsdict['Tables'][tableName]['referenceKey'][KeyName] = {}
            tempDict = self.parseFDRows(self.TopKeysDict, sheet, self.xlsdict['Tables'][tableName]['referenceKey'], KeyNameCell, False)
            self.xlsdict['Tables'][tableName]['referenceKey'] = tempDict
        
        
        #Transformations
        sheet = workbook.getSheet('Transformations')
        TNcol = sheet.getColumn(sheet.findCell('Fact Table or Reference Table').getColumn())
        del TNcol[0]
        PNcol = sheet.getColumn(sheet.findCell('Measurement Interface').getColumn())
        del PNcol[0]
        for parserCell in PNcol:
            parserName = parserCell.getContents().strip()
            if parserName != '':
                tableName = TNcol[parserCell.getRow()-1].getContents().strip()
                transRowID = parserCell.getRow()
                if 'Parser' not in self.xlsdict['Tables'][tableName]:
                    self.xlsdict['Tables'][tableName]['Parser'] = {}
                if parserName not in self.xlsdict['Tables'][tableName]['Parser']:
                    self.xlsdict['Tables'][tableName]['Parser'][parserName] = {}
                if transRowID not in self.xlsdict['Tables'][tableName]['Parser'][parserName]:
                    self.xlsdict['Tables'][tableName]['Parser'][parserName][transRowID-1] = {}
                for FDColumn, Parameter in self.TransDict.iteritems(): 
                    columnNumber = sheet.findCell(FDColumn).getColumn()
                    value = sheet.getColumn(columnNumber)[transRowID].getContents()
                    self.xlsdict['Tables'][tableName]['Parser'][parserName][transRowID-1][Parameter] = self.encodeValue(value)
                    
        #DataFormat
        sheet = workbook.getSheet('Data Format')
        attrList = ['measurementCounter', 'measurementKey' , 'referenceKey']
        header = sheet.getRow(0)
        TNcol = sheet.getColumn(sheet.findCell('Table Name').getColumn())
        ANcol = sheet.getColumn(sheet.findCell('Counter/key Name').getColumn())
        
        for HeaderColumn in header:
            parserName = HeaderColumn.getContents()
            colNumber = HeaderColumn.getColumn()
            if parserName != 'Table Name' and  parserName != 'Counter/key Name':
                formats = sheet.getColumn(colNumber)
                del formats[0]
                for formatCell in formats:
                    format = formatCell.getContents()
                    rowNumber = formatCell.getRow()
                    if format != '':
                        tableName = TNcol[rowNumber].getContents().strip()
                        attrName = ANcol[rowNumber].getContents().strip()
                        
                        if 'Parser' not in self.xlsdict['Tables'][tableName]:
                            self.xlsdict['Tables'][tableName]['Parser'] = {}
                        if parserName not in self.xlsdict['Tables'][tableName]['Parser']:
                            self.xlsdict['Tables'][tableName]['Parser'][parserName] = {}
                        if 'ATTRTAGS' not in self.xlsdict['Tables'][tableName]['Parser'][parserName]:
                            self.xlsdict['Tables'][tableName]['Parser'][parserName]['ATTRTAGS'] = {}
                        
                        self.xlsdict['Tables'][tableName]['Parser'][parserName]['ATTRTAGS'][str(attrName)] = self.encodeValue(format)
                        
                        for attrtype in attrList:
                            if attrtype in self.xlsdict['Tables'][tableName]:
                                if attrName in self.xlsdict['Tables'][tableName][attrtype]:
                                    self.xlsdict['Tables'][tableName][attrtype][attrName]['DATAID'] = self.encodeValue(format)
              
        #BH
        sheet = workbook.getSheet('BH')
        self.xlsdict['BHOBJECT'] = {}
        BHcol = sheet.getColumn(sheet.findCell('Object Name').getColumn())
        del BHcol[0]
        PHcol = sheet.getColumn(sheet.findCell('Placeholder Name').getColumn())
        del PHcol[0]
        for PHCell in PHcol:
            PHName = PHCell.getContents()
            BHName = BHcol[PHCell.getRow()-1].getContents()
            if BHName != '':
                if BHName not in self.xlsdict['BHOBJECT']:
                    self.xlsdict['BHOBJECT'][BHName] = {}
                self.xlsdict['BHOBJECT'][BHName][PHName] = {}
                tempDict = self.parseFDRows(self.BHDict, sheet, self.xlsdict['BHOBJECT'][BHName], PHCell, False)
                self.xlsdict['BHOBJECT'][BHName] = tempDict
        
        #BH Rank Keys
        sheet = workbook.getSheet('BH Rank Keys')
        BHcol = sheet.getColumn(sheet.findCell('Object Name').getColumn())
        del BHcol[0]
        PHcol = sheet.getColumn(sheet.findCell('Placeholder Name').getColumn())
        del PHcol[0]
        for PHCell in PHcol:
            PHName = PHCell.getContents()
            BHName = BHcol[PHCell.getRow()-1].getContents()
            if BHName != '':
                if 'RANKINGKEYS' not in self.xlsdict['BHOBJECT'][BHName][PHName]:
                    self.xlsdict['BHOBJECT'][BHName][PHName]['RANKINGKEYS'] = {}
                if 'TYPENAME' not in self.xlsdict['BHOBJECT'][BHName][PHName]:
                    self.xlsdict['BHOBJECT'][BHName][PHName]['TYPENAME'] = []    
                KeyName = sheet.getColumn(sheet.findCell('Key Name').getColumn())[PHCell.getRow()].getContents()
                SourceTable = sheet.getColumn(sheet.findCell('Source Fact Table Name').getColumn())[PHCell.getRow()].getContents()
                rankSourceTable = ''
                if ',' in SourceTable:
                    rankSourceTable = SourceTable.split(',')[0]
                
                self.xlsdict['BHOBJECT'][BHName][PHName]['RANKINGKEYS'][KeyName] = self._getRankKeyValue(rankSourceTable, KeyName)
                self.xlsdict['BHOBJECT'][BHName][PHName]['TYPENAME'] = SourceTable
                
        #External Statments
        EStxtFileName = filename.replace('.xls', '.txt')
        ESCollection = self.loadEStxtFile(EStxtFileName)
        
        sheet = workbook.getSheet('External Statement')
        self.xlsdict['ExternalStatements'] = {}
        columnNumber = sheet.findCell('View Name').getColumn()
        ESNameColumn = sheet.getColumn(columnNumber)
        del ESNameColumn[0]
        for EsNameCell in ESNameColumn:
            ESName = EsNameCell.getContents()
            if ESName != '':
                self.xlsdict['ExternalStatements'][ESName] = {}
                self.xlsdict['ExternalStatements'][ESName]['EXECUTIONORDER'] = str(EsNameCell.getRow())
            for FDColumn, Parameter in self.ESDict.iteritems():
                columnNumber = sheet.findCell(FDColumn).getColumn()
                value = ''
                try:
                    value = sheet.getColumn(columnNumber)[EsNameCell.getRow()].getContents()

                    if Parameter == 'STATEMENT':
                        if value in EStxtFileName:
                            value = ESCollection[ESName]
                except:
                    pass
                self.xlsdict['ExternalStatements'][ESName][Parameter] = self.encodeValue(value)
                
        
        UniName = ''       
        #Universe Extensions
        sheet = workbook.getSheet('Universe Extension')
        self.xlsdict['Universe'] = {}
        Unicol = sheet.getColumn(sheet.findCell('Universe Name').getColumn())
        del Unicol[0]
        UEcol = sheet.getColumn(sheet.findCell('Universe Extension').getColumn())
        del UEcol[0]
        for UniExtNameCell in UEcol:
            UniExtName = UniExtNameCell.getContents()
            if UniExtName != '':
                UniName = Unicol[UniExtNameCell.getRow()-1].getContents()
                if UniName not in self.xlsdict['Universe']:
                    self.xlsdict['Universe'][UniName] = {}
                    self.xlsdict['Universe'][UniName]['Extensions'] = {}
                
                if UniExtName != '' and UniExtName.upper() != 'ALL':  
                    self.xlsdict['Universe'][UniName]['Extensions'][UniExtName] = {}
                    tempDict = self.parseFDRows(self.UniExtDict, sheet, self.xlsdict['Universe'][UniName]['Extensions'], UniExtNameCell, True)
                    self.xlsdict['Universe'][UniName]['Extensions'] = tempDict
            
        if UniName != None and UniName != '':   
            #Universe Tables
            sheet = workbook.getSheet('Universe Topology Tables')
            self.xlsdict['Universe'][UniName]['Tables'] = {}
            columnNumber = sheet.findCell('Topology Table Name').getColumn()
            TableNameColumn = sheet.getColumn(columnNumber)
            del TableNameColumn[0]
            for tableNameCell in TableNameColumn:
                tableName = tableNameCell.getContents()
                if tableName != '':
                    self.xlsdict['Universe'][UniName]['Tables'][tableName] = {}
                tempDict = self.parseFDRows(self.UniTableDict, sheet, self.xlsdict['Universe'][UniName]['Tables'], tableNameCell, True)
                self.xlsdict['Universe'][UniName]['Tables'] = tempDict
                
            #Universe Class
            sheet = workbook.getSheet('Universe Class')
            self.xlsdict['Universe'][UniName]['Class'] = {}
            columnNumber = sheet.findCell('Topology & Key Class Name').getColumn()
            ClassNameColumn = sheet.getColumn(columnNumber)
            del ClassNameColumn[0]
            for ClassNameCell in ClassNameColumn:
                ClassName = ClassNameCell.getContents()
                if ClassName != '':
                    self.xlsdict['Universe'][UniName]['Class'][ClassName] = {}
                tempDict = self.parseFDRows(self.UniClassDict, sheet, self.xlsdict['Universe'][UniName]['Class'], ClassNameCell, True)
                self.xlsdict['Universe'][UniName]['Class'] = tempDict
                
            #Universe Objects
            sheet = workbook.getSheet('Universe Topology Objects')
            self.xlsdict['Universe'][UniName]['Object'] = {}
            columnNumber = sheet.findCell('Unv. Object').getColumn()
            ObjNameColumn = sheet.getColumn(columnNumber)
            del ObjNameColumn[0]
            classColNumber = sheet.findCell('Unv. Class').getColumn()
            ClassNameColumn = sheet.getColumn(classColNumber)
            for ObjNameCell in ObjNameColumn:
                ObjName = ObjNameCell.getContents()
                className = ClassNameColumn[ObjNameCell.getRow()].getContents()
                if className not in self.xlsdict['Universe'][UniName]['Object']:
                    self.xlsdict['Universe'][UniName]['Object'][className] = {}
                if ObjName != '':
                    self.xlsdict['Universe'][UniName]['Object'][className][ObjName] = {}
                tempDict = self.parseFDRows(self.UniObjDict, sheet, self.xlsdict['Universe'][UniName]['Object'][className], ObjNameCell, True)
                self.xlsdict['Universe'][UniName]['Object'][className] = tempDict
                
            #Universe Conditions
            sheet = workbook.getSheet('Universe Conditions')
            self.xlsdict['Universe'][UniName]['Conditions'] = {}
            columnNumber = sheet.findCell('Condition Name').getColumn()
            ConNameColumn = sheet.getColumn(columnNumber)
            del ConNameColumn[0]
            classColNumber = sheet.findCell('Condition object class').getColumn()
            ClassNameColumn = sheet.getColumn(classColNumber)
            for ConNameCell in ConNameColumn:
                ConName = ConNameCell.getContents()
                className = ClassNameColumn[ConNameCell.getRow()].getContents()
                if className not in self.xlsdict['Universe'][UniName]['Conditions']:
                    self.xlsdict['Universe'][UniName]['Conditions'][className] = {}
                if ConName != '':
                    self.xlsdict['Universe'][UniName]['Conditions'][className][ConName] = {}
                tempDict = self.parseFDRows(self.UniConDict, sheet, self.xlsdict['Universe'][UniName]['Conditions'][className], ConNameCell, True)
                self.xlsdict['Universe'][UniName]['Conditions'][className] = tempDict
                
            #Universe Joins
            sheet = workbook.getSheet('Universe Joins')
            self.xlsdict['Universe'][UniName]['Joins'] = {}
            Cells = sheet.getColumn(0)
            del Cells[0]
            for join in Cells:
                if join.getContents() != None and join.getContents().strip() != '':
                    self.xlsdict['Universe'][UniName]['Joins'][join.getRow()] = {}
                    for FDColumn, Parameter in self.UniJoinsDict.iteritems():
                        columnNumber = sheet.findCell(FDColumn).getColumn()
                        value = ''
                        try:
                            value = sheet.getColumn(columnNumber)[join.getRow()].getContents()
                        except:
                            pass
                        self.xlsdict['Universe'][UniName]['Joins'][join.getRow()][Parameter] = self.encodeValue(value)
        
        #Verificaton Objects
        sheet = workbook.getSheet('Report objects')
        self.xlsdict['ReportObjects'] = {}
        Cells = sheet.getColumn(0)
        del Cells[0]
        for obj in Cells:
            if obj.getContents() != '':
                name = obj.getRow()
                self.xlsdict['ReportObjects'][name] = {}
                for FDColumn, Parameter in self.verObjDict.iteritems():
                    columnNumber = sheet.findCell(FDColumn).getColumn()
                    value = ''
                    try:
                        value = sheet.getColumn(columnNumber)[obj.getRow()].getContents()
                    except:
                        pass
                    self.xlsdict['ReportObjects'][name][Parameter] = self.encodeValue(value)
                
        #Verificaton Conditions
        sheet = workbook.getSheet('Report conditions')
        self.xlsdict['ReportConditions'] = {}
        Cells = sheet.getColumn(0)
        del Cells[0]
        for con in Cells:
            if con.getContents() != '':
                name = con.getRow()
                self.xlsdict['ReportConditions'][name] = {}
                for FDColumn, Parameter in self.verConDict.iteritems():
                    columnNumber = sheet.findCell(FDColumn).getColumn()
                    value = ''
                    try:
                        value = sheet.getColumn(columnNumber)[con.getRow()].getContents()
                    except:
                        pass
                    self.xlsdict['ReportConditions'][name][Parameter] = self.encodeValue(value)
        
    def parseFDRows(self, mappingDict, FDsheet, destinationDict, destinationKey, getOrderNo):
        KeyName = destinationKey.getContents()
        rowNumber = destinationKey.getRow()
        if KeyName != '':
            if getOrderNo:
                destinationDict[KeyName]['ORDERNRO'] = str(rowNumber)

            for FDColumn, Parameter in mappingDict.iteritems():            
                columnNumber = FDsheet.findCell(FDColumn).getColumn()
                value = ''
                try:
                    value = FDsheet.getColumn(columnNumber)[rowNumber].getContents()
                    value = value.strip()
                except:
                    pass
                if value == 'Y' or value == 'y':
                    value = 1
                if Parameter == 'DATATYPE':
                    datatype,datasize,datascale = self.parseDataType(value)
                    value = datatype
                    destinationDict[KeyName]['DATASIZE'] = datasize
                    destinationDict[KeyName]['DATASCALE'] = datascale
                destinationDict[KeyName][Parameter] = self.encodeValue(value)
        return destinationDict
    
    def loadEStxtFile(self, filename):
        ESCollection = {}
        if os.path.isfile(filename):
            filecontents = open(filename, 'r').read()
            filecontents = filecontents.split('@@')
            for ES in filecontents:
                if ES != '':
                    info = ES.split('==')
                    ESCollection[info[0]] = info[1]
        return ESCollection
    
    def encodeValue(self, value):
        try:
            value = str(value).strip()
        except:
            value = value.encode('ascii', 'ignore')
        return value
    
    def _getRankKeyValue(self, SourceTable, KeyName):
        tableName = SourceTable.rsplit('_', 1)[0]
        if tableName in self.xlsdict['Tables']:
            return SourceTable + '.' + KeyName
        
        return KeyName
            
        
    
    def parseDataType(self, datatype):
        #datatype(datasize,datascale)
        #datatype(datascale)
        #datatype
        
        datasize = '0'
        datascale = '0'
        
        if '(' in datatype:
            parts = datatype.split('(')
            datatype = parts[0]
            if ',' in parts[1]:
                datasize = parts[1].split(',')[0]
                datascale = parts[1].split(',')[1].replace(')','')
            else:
                datasize = parts[1].replace(')','')
        
        return datatype,datasize,datascale
                        
    def returnXlsDict(self):
        return self.xlsdict
