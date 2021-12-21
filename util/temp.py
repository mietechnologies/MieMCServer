import os

from util.date import Date

from .configuration import Temp
from .syslog import log

# dev imports
import random

class PiTemp:
    __dir = os.path.dirname(__file__)
    __root = os.path.join(__dir, '..')

    @classmethod
    def measure(cls):
        # read the current temp directly from the Pi
        temp = os.popen("vcgencmd measure_temp").readline()
        
        # or generate random numbers for development
        # randomTemp = random.uniform(80.0,120.0)
        # temp = 'temp={}'.format(randomTemp)
        
        string = temp.replace("temp=", "").replace("'C", "")
        return float(string)

    @classmethod
    def execute(cls):
        ''' 
        Takes and stores a measurement of the Raspberry Pi's CPU temperature as well as 
        a current timestamp. The stored values are then compared to determine if the
        system should restart or not.
        '''
        Temp.current = cls.measure()
        Temp.date = Date().timestamp()
        if Temp.overheating:
            if Temp.current <= Temp.maximum:
                log("[PiTemp] - Temperature has dropped to a nominal range [{}]".format(Temp.current))
                Temp.elapsed = 0
            else:
                Temp.elapsed += 1
                log("[PiTemp] - WARN: Temperature is still too high [{}]".format(Temp.current))
                if Temp.elapsed > Temp.minutes:
                    log("[PiTemp] - ERR: Temperature was too hot for too long - rebooting")
                    os.popen('sudo reboot')
        else:
            if Temp.current >= Temp.maximum:
                log("[PiTemp] - WARN: Temp is too high [{}]".format(Temp.current))
                Temp.elapsed = 0
                Temp.overheating = True
        Temp.update()