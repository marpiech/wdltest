import json
import re
import os

class TestConfiguration(object):

    def __init__(self, path):
        with open(path, 'r') as json_file:
            json_text = json_file.read()#.replace('${ROOTDIR}','/home/marpiech/workflows')
            variables = re.findall(r"\$\{[A-Za-z_-]+\}", json_text)
            for variable in variables:
                varname = variable.replace('$','').replace('{','').replace('}','')
                try:
                    json_text = json_text.replace(variable,os.environ[varname])
                except: raise Exception("Variable " + varname + " is undefined")
            #print(json_text)

            #exit(0)
            #print(json_text)
            #replace("${ROOTDIR}","/home/marpiech/workflows/")
            self.textConfig = json.loads(json_text)

    def getConfiguration(self):
        return self.textConfig