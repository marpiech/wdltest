import json
import re
import os
import time
import logging
import subprocess

class TestRunner(object):

    def __init__(self, configuration, cromwell):
        self.logger = logging.getLogger(__name__)
        self.configuration = configuration
        self.cromwell = cromwell

    def run(self):
        exitCode = 0
        for testJson in self.configuration["tests"]:
            try:
                self.cromwell.submitJob(self.configuration["wdl"], testJson["inputs"])
                status = "Started"
                start = time.time()
                while status != "Failed" and status != "Succeeded":
                    time.sleep(1)
                    previousStatus = status
                    status = self.cromwell.getStatus()
                    if status != previousStatus:
                        start = time.time()
                        if previousStatus != "Started": print()
                    diff = int(time.time() - start)
                    print("Cromwell job status " + status + " " + str(diff) + "s                     ", end ="\r")
                    #self.logger.debug("Cromwell job status " + status)
                print()
                for condition in testJson["conditions"]:
                    try:
                        bashCommand = condition["command"].replace("$file", self.cromwell.getPathToOutput(condition["file"]))
                        process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, error = process.communicate()
                        output = output.decode("utf-8").strip() + error.decode("utf-8").strip()
                        returnCode = process.poll()
                        if returnCode == 0:
                            print("[PASSED] Test '" + condition["name"] + "'")
                        else:
                            print("[ERROR] Test '" + condition["name"] + "' failed with message: " + condition["error_message"])
                            exitCode = 1
                
                    except Exception as e:
                        print("[ERROR] Test '" + condition["name"] + "' failed because file " + condition["file"] + " does not exists. " + e)
                        exitCode = 1
                    
            except Exception as e:
                exitCode = 1
                print("ERROR " + str(e))
                self.cromwell.stop()   

        return exitCode         
