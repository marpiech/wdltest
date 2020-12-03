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
        self.logger.debug("Cromwell started")
        exitCode = 0
        for testJson in self.configuration["tests"]:
            try:
                self.cromwell.submitJob(self.configuration["wdl"], testJson["inputs"])
                status = "Started"
                start = time.time()
                while status != "Failed" and status != "Succeeded":
                    time.sleep(1)
                    previousStatus = status
                    #self.logger.debug(status)
                    status = self.cromwell.getStatus()
                    #self.logger.debug(status)
                    if status != previousStatus:
                        start = time.time()
                        if previousStatus != "Started": print()
                    diff = int(time.time() - start)
                    print("Cromwell job status " + status + " " + str(diff) + "s                     ", end ="\r")
                    #self.logger.debug("Cromwell job status " + status)
                print()
                #self.logger.debug("DEBUG")
                for condition in testJson["conditions"]:
                    #self.logger.debug("CONDITION " + str(condition))
                    try:
                        if self.cromwell.getPathToOutput(condition["file"]) == 'missing':
                            self.logger.error("[ERROR] Test '" + condition["name"] + "' failed with message: no " + condition["file"] + " file in workflow outputs")
                            exitCode = 1
                        else:
                            bashCommand = condition["command"].replace("$file", self.cromwell.getPathToOutput(condition["file"]))
                            process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            output, error = process.communicate()
                            output = output.decode("utf-8").strip() + error.decode("utf-8").strip()
                            returnCode = process.poll()
                            if returnCode == 0:
                                self.logger.info("[PASSED] Test '" + condition["name"] + "'")
                            else:
                                self.logger.error("[ERROR] Test '" + condition["name"] + "' failed with message: " + condition["error_message"])
                                exitCode = 1
                
                    except Exception as e:
                        self.logger.error("[ERROR] Test '" + condition["name"] + "' failed because file " + condition["file"] + " does not exists. " + e)
                        exitCode = 1
                    
            except Exception as e:
                exitCode = 1
                print("ERROR " + str(e))
                self.cromwell.stop()   

        return exitCode         
