import subprocess
import requests
import os
import logging
import threading
import socket
import random
import time
import json
import regex
import getpass ## for username
from shutil import copyfile
from datetime import datetime

class CromwellHandler(object):

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.checkJava()
        self.downloadCromwell()
        self.mode = self.config['cromwell']['mode']
        if(self.mode == "server"):
            self.port = self.getPort()
            self.localhost = "127.0.0.1"
            cromwellThread = threading.Thread(target = self.startCromwell)
            cromwellThread.start()
            self.waitForCromwell()

    def checkJava(self):
        self.logger.debug('Checking if java is installed')
        bashCommand = "java -version"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode("utf-8").strip() + error.decode("utf-8").strip()
        if(not (("vm" in output) or ("VM" in output))):
            raise Exception("JVM is not installed")

    def downloadCromwell(self):
        dir = self.config['paths']['dir']
        if(not os.path.isdir(dir)):
            os.mkdir(dir)
            os.chmod(dir, 0o776)
        path = dir + "/cromwell.jar"
        url = self.config['cromwell']['url']
        if(not os.path.isfile(path)):
            self.logger.debug('Downloading cromwell')
            request = requests.get(url, allow_redirects=True)
            open(path, 'wb').write(request.content)
            os.chmod(path, 0o666)
        configSourcePath = os.path.dirname(__file__) + "/cromwell.cfg"
        configDestinationPath = dir + "/cromwell.cfg" 
        if(not os.path.isfile(configDestinationPath)):
            copyfile(configSourcePath, configDestinationPath)
            os.chmod(configDestinationPath, 0o666)

    def getPort(self):
        for i in range(0, 19):
            port = random.randint(8000,8999)
            if self.isPortAvailable(port):
                return port
        raise Exception("Could not find free port to allocate for Cromwell")

    def isPortAvailable(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.localhost,port))
        if result == 0:
            return False
        else:
            return True
        sock.close()

    def startCromwell(self):
        bashCommand = "java -Dconfig.file=" + self.config['paths']['dir'] + " -Dwebservice.port=" + str(self.port) + " -jar " + self.config['paths']['dir'] + "/cromwell.jar server"
        self.cromwellProcess = subprocess.Popen(bashCommand.split(), cwd=self.config['paths']['dir'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def getCromwellUrl(self):
        return "http://" + self.localhost + ":" + str(self.port)

    def waitForCromwell(self):
        self.logger.debug("Waiting for cromwell server")
        url = self.getCromwellUrl() + "/engine/v1/status"
        for i in range(0, 29):
            time.sleep(1)
            try:
                resp = requests.get(url)
                return
            except:
                pass
        raise Exception("Could not connect to Cromwell")

    def submitJob(self, wdl, inputs, id):
        self.logger.debug("Submmitting job in " + self.mode + " mode")
        if self.mode == "server":
            multipart_form_data = {
                'workflowSource': ("workflow.wdl", open( wdl, "rb")),
                'workflowInputs': ("inputs.json", json.dumps(inputs)),
            }
            response = requests.post(self.getCromwellUrl() + "/api/workflows/v1", files=multipart_form_data)
            self.job = json.loads(response.content.decode("utf-8"))["id"]
            self.logger.debug("Submitted job " + self.job)
        if self.mode == "run":
            self.basePath = self.config['paths']['dir'] + "/" + getpass.getuser() + "/" + os.path.basename(os.path.dirname(wdl))
            if(not os.path.isdir(self.basePath)):
                os.makedirs(self.basePath)
                os.chmod(self.basePath, 0o776)
            self.runPath = self.basePath + "/" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "/" + id
            if(not os.path.isdir(self.runPath)):
                os.makedirs(self.runPath)
                os.chmod(self.runPath, 0o776)
            self.inputPath = self.runPath + "/inputs.json"
            self.logPath = self.runPath + "/cromwell-execution.log"

            self.returnCode = -1
            self.logger.debug("PATH: " + self.runPath)
            with open(self.inputPath, "w") as inputs_file:
                print(json.dumps(inputs), file=inputs_file)
            bashCommand = "java -Dconfig.file=" + self.config['paths']['dir'] + "/cromwell.cfg" + " -jar " + self.config['paths']['dir'] + "/cromwell.jar run " + wdl + " --inputs " + self.inputPath
            self.cromwellProcess = subprocess.Popen(bashCommand.split(), cwd=self.runPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log = ""
            self.status = "Running"
            with open(self.logPath, "w") as log_file:
                for line in iter(self.cromwellProcess.stdout.readline, ""):
                    printline = line.decode("utf-8").replace('\n', '')
                    if "to Done" in printline:
                        print(printline)
                    print(printline, file=log_file)
                    self.log = self.log + line.decode("utf-8").replace('\n', '')
                    if "workflow finished with status" in printline:
                        self.status = printline.split()[-1].replace("'", '').replace('.',' ')
                    if line == b'' and self.cromwellProcess.poll() is not None:
                        break
            #print (self.status)
            if "Succeeded" in self.status:
                #print("in Succeeded")
                #self.logger.debug(self.log)
                pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
                jsons = pattern.findall(self.log)
                #self.logger.debug(jsons)
                for jsonitem in jsons:
                    #self.logger.debug(jsonitem)
                    if jsonitem.find('"outputs":') != -1:
                        #self.logger.debug("IN")
                        rawoutputs = json.loads(jsonitem)
                #self.logger.debug(self.outputs)
                rawoutputs = rawoutputs["outputs"]
                self.outputs = dict()
                for key in rawoutputs:
                    #self.logger.debug("key: " + key)
                    try:
                        
                        #self.logger.debug("key: " + key.split('.')[-1])
                    
                        self.outputs[key.split('.')[-1]] = rawoutputs[key]
                    except Exception as e:
                        self.logger.debug("error: " + str(e))
                self.cromwellProcess.stdout.close()
                self.returnCode = self.cromwellProcess.wait()
                self.logger.debug("Finished run")
                self.logger.info("Path to log " + self.logPath)
            else:
                #print("not succeeded")
                self.outputs = dict()
                self.cromwellProcess.stdout.close()
                self.logger.info("Workflow failed")
                self.logger.info("Path to log " + self.logPath)
                self.returnCode = 1
            #print(self.outputs)

    def getStatus(self):
        if self.mode == "server":
            response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/status")
            status = json.loads(response.content.decode("utf-8"))
            if status["status"] == "fail":
                return "Submitted unregistered"
            return status["status"]
        if self.mode == "run":
            if self.returnCode == -1:
                return "Running"
            if self.returnCode == 0:
                return "Succeeded"
            if self.returnCode > 0:
                return "Failed"

    def getMetadata(self):
        response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/metadata")
        return json.loads(response.content.decode("utf-8"))

    def getOutputs(self):
        response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/outputs")
        return json.loads(response.content.decode("utf-8"))

    def getPathToOutput(self, desiredOutput):
        if self.mode == "server":
            outputs = self.getOutputs()["outputs"]
            #print(outputs)
            for key in outputs.keys():
                workflow, output = os.path.splitext(key)
                if(output.replace('.', '') == desiredOutput):
                    return outputs[key]
            raise Exception("Could not find path to output: " + desiredOutput)
        if self.mode == "run":
            if desiredOutput in self.outputs:
                output = self.outputs[desiredOutput]
                if "list" in type(output).__name__:
                    return output[0]
                return output
            else:
                return 'missing'
            

    def stop(self):
        if self.mode == "server":
            self.cromwellProcess.terminate()
            self.cromwellProcess.kill()