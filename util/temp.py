import os
import time

from date import Date

# dev imports
import random

class PiTemp:
    allowedCriticalEventCount = 3
    maximumTemp = 70.0
    logFileName = "temp_log.txt"
    
    criticalEventCount = 0
    isOverheating = False

    def __init__(self, max = 70.0, count = 3, logfile = "temp_log.txt"):
        self.logFileName = logfile
        self.allowedCriticalEventCount = count
        self.maximumTemp = max

    def measureTemp(self):
        # generate random numbers for development (vcgencmd is a Pi-specific command)
        # temp = os.popen("vcgencmd measure_temp").readline()
        randomTemp = random.uniform(80.0,120.0)
        temp = 'temp={}'.format(randomTemp)
        string = (temp.replace("temp=",""))
        return float(string)
        
    def log(self, message):
        file = open(self.logFileName, "a")
        file.write("[PiTemp - {date}] {message}\n".format(date=Date().timestamp(), message=message))
        file.close()
        
    def start(self):
        while True:
            currentTemp = self.measureTemp()
            if self.isOverheating:
                if currentTemp < self.maximumTemp:
                    self.log("Temperature has dropped to a nominal range [{}]".format(currentTemp))
                    self.isOverheating = False
                    self.criticalEventCount = 0
                else:
                    self.log("WARN: Temperature is still too high [{}]".format(currentTemp))
                    self.criticalEventCount += 1
                    if self.criticalEventCount > self.allowedCriticalEventCount:
                        self.log("ERR: Temperature was too hot for too long")
                        print("[PiTemp] A critical temperature has been reached! Logs can be found in 'temp_log.txt' in your project's root directory.")
                        return True
            else:
                if currentTemp > self.maximumTemp:
                    self.log("WARN: Temp is too high [{}]".format(currentTemp))
                    self.isOverheating = True
            time.sleep(1)
