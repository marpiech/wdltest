import subprocess
import requests
import os
import logging
import threading
import socket
import random
import time
import json

class CromwellHandler(object):

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.checkJava()
        self.downloadCromwell()
        self.localhost = "127.0.0.1"
        self.port = self.getPort()
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
        path = dir + "/cromwell.jar"
        url = self.config['cromwell']['url']
        if(not os.path.isfile(path)):
            self.logger.debug('Downloading cromwell')
            request = requests.get(url, allow_redirects=True)
            open(path, 'wb').write(request.content)

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
        bashCommand = "java -Dwebservice.port=" + str(self.port) + " -jar " + self.config['paths']['dir'] + "/cromwell.jar server"
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

    def submitJob(self, wdl, inputs):      
        multipart_form_data = {
            'workflowSource': ("workflow.wdl", open( wdl, "rb")),
            'workflowInputs': ("inputs.json", json.dumps(inputs)),
        }
        response = requests.post(self.getCromwellUrl() + "/api/workflows/v1", files=multipart_form_data)
        self.job = json.loads(response.content.decode("utf-8"))["id"]
        self.logger.debug("Submitted job " + self.job)

    def getStatus(self):
        response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/status")
        status = json.loads(response.content.decode("utf-8"))
        if status["status"] == "fail":
            return "Submitted unregistered"
        return status["status"]

    def getMetadata(self):
        response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/metadata")
        return json.loads(response.content.decode("utf-8"))

    def getOutputs(self):
        response = requests.get(self.getCromwellUrl() + "/api/workflows/v1/" + self.job + "/outputs")
        return json.loads(response.content.decode("utf-8"))

    def getPathToOutput(self, desiredOutput):
        outputs = self.getOutputs()["outputs"]
        #print(outputs)
        for key in outputs.keys():
            workflow, output = os.path.splitext(key)
            if(output.replace('.', '') == desiredOutput):
                return outputs[key]
        raise Exception("Could not find path to output: " + desiredOutput)

    def stop(self):
        self.cromwellProcess.terminate()
        self.cromwellProcess.kill()