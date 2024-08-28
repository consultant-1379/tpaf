import sys
import inspect
import os

class DRM(object):
    def __init__(self,modulelocation):
        self.file_obj = None
        sys.path.append(modulelocation)
        self.modules = {}
        for module in os.listdir(modulelocation):
            if module[-3:] == '.py':
                self.modules[module[:-3]] = __import__(module[:-3], locals(), globals())
            
    def getRuleSetsProperties(self):
        RulesDict = {}
        for key, module in self.modules.iteritems():
            clsmembers = inspect.getmembers(module, inspect.isclass)
            for classmember, location in clsmembers:
                RulesDict[classmember] = {}
                
                rules = inspect.getmembers(location, inspect.ismethod)
                for rule, rulelocation in rules:
                    RulesDict[classmember][rule] = rulelocation.__doc__

        return RulesDict
                    
    def executeRules(self, TP_Obj, moduleName, RulesDict):
        ErrorDict = {}
        clsmembers = inspect.getmembers(self.modules[moduleName], inspect.isclass)  
        for classmember, location in clsmembers:
            if moduleName == classmember:
                rule_obj = location()
                for rule in RulesDict:
                    ErrorDict = getattr(rule_obj,rule)(TP_Obj, ErrorDict)            
            
        return ErrorDict
    
    def printErrorDictToFile(self, ErrorDict):
        self.file_obj=open('Errors.txt', 'w')
        self._pretty(ErrorDict)


    def _pretty(self, dict_obj, indent=0):
        for key, value in dict_obj.iteritems():
            if isinstance(value, dict):
                self.file_obj.write('\t' * indent + str(key)+'\n')
                self._pretty(value, indent+1)
            else:
                self.file_obj.write('\t' * indent + str(key) + ' : ' + str(value)+'\n')

        

        
        
