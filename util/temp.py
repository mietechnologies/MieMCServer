import os
import re
import time

from .date import Date
from .cron import CronScheduler

# dev imports
import random

class PiTemp:
    root = os.path.dirname(__file__)
    allowedCriticalEventCount = 3
    maximumTemp = 70.0
    logfile = "temp_log.txt"
    config = os.path.join(root, 'pitemp-config.txt')

    def __init__(self, max = 70.0, count = 3, logfile = "temp_log.txt"):
        self.logfile = logfile
        self.allowedCriticalEventCount = count
        self.maximumTemp = max
        
        # write config.txt for later use
        config = open(self.config, 'w')
        config = open(self.config, 'a')
        config.write('logfile={}\n'.format(logfile))
        config.write('maximum={}\n'.format(max))
        config.write('minutes={}'.format(count))
        config.close()

    def measureTemp(self):
        # read the current temp directly from the Pi
        # temp = os.popen("vcgencmd measure_temp").readline()
        
        # or generate random numbers for development
        randomTemp = random.uniform(80.0,120.0)
        temp = 'temp={}'.format(randomTemp)
        
        string = temp.replace("temp=", "").replace("'C", "")
        return float(string)
        
    def log(self, message):
        file = open(self.logfile, "a")
        file.write("[PiTemp - {date}] {message}\n".format(Date().timestamp(), message))
        file.close()
        
    def logs(self):
        file = open(self.logfile, 'r')
        logs = file.readlines()
        file.close()
        return logs
        
    def isOverheating(self):
        # grab last logged event
        latestLog = reversed(self.logs())[0]
        
        if 'WARN' in latestLog:
            now = Date().now()
            loggedDate = re.search('\d+\/\d+\/\d+ \d+:\d+:\d+.\d+', latestLog)
            if loggedDate:
                date = Date().timeFromDate(loggedDate.group(0))
                elapsed = Date().elapsedTimeBetweenDates(now, date)
                if elapsed < 1.1 * 60:
                    return True
        return False
        
    def criticalTemperatureReached(self):
        logs = reversed(self.logs())
        # collect warnings from logs
        warnings = []
        for log in logs:
            if 'WARN:' in log:
                warnings.append(log)
        
        # iterate through warnings to determine elapsed time between two logs
        # if elapsed time is greater than 1.1 minutes, return False
        # if less, increment counter
        # if counter is greater than allowedCriticalEventCount, return True
        currentWarning = None
        eventCount = 0
        for warning in warnings:
            if currentWarning == None:
                currentWarning = warning
            else:
                date = re.search('\d+\/\d+\/\d+ \d+:\d+:\d+.\d+', currentWarning)
                otherDate = re.search('\d+\/\d+\/\d+ \d+:\d+:\d+.\d+', warning)
                elapsed = Date().elapsedTimeBetweenDates(date, otherDate)
                if elapsed > 1.1 * 60:
                    return False
                else:
                    eventCount += 1
                    if eventCount > self.allowedCriticalEventCount:
                        return True
                    else:
                        currentWarning = warning
        return False
        
    def start(self):
        if os.path.isfile(self.config) == False:
            file = open(self.config, 'w')
            file.close()
        CronScheduler().createRecurringJob('* * * * *', 'python cron_temp.py', 'measure_temp')
            
    def stop(self):
        CronScheduler().removeJob('measure_temp')
        
    def execute(self):
        # fetch saved values from config
        configuration = open(self.config, 'r').readlines()
        for line in configuration:
            if 'logfile' in line:
                logfile = line.replace('logfile=', '')
                self.logfile = logfile
            if 'maximum' in line:
                maximum = line.replace('maximum=', '')
                self.maximumTemp = int(maximum)
            if 'minutes' in line:
                minutes = line.replace('minutes=', '')
                self.allowedCriticalEventCount = int(minutes)
        
        currentTemp = self.measureTemp()
        if self.isOverheating():
            if currentTemp <= self.maximumTemp:
                self.log("Temperature has dropped to a nominal range [{}]".format(currentTemp))
            else:
                self.log("WARN: Temperature is still too high [{}]".format(currentTemp))
                if self.criticalEventOccured():
                    self.log("ERR: Temperature was too hot for too long")
                    self.stop()
                    print('[PiTemp] A critical temperature has been reached! PiTemp has stopped monitoring the temperature of your Pi... Logs can be found in "{}".'.format(self.logfile))
        else:
            if currentTemp >= self.maximumTemp:
                self.log("WARN: Temp is too high [{}]".format(currentTemp))
                







