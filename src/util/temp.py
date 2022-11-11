import os

from util.date import Date

from configuration import config
from util.logger import log

# dev imports
import random

class PiTemp:
    __dir = os.path.dirname(__file__)
    __root = os.path.join(__dir, '..')

    config_file = config.File()

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
        current = cls.measure()
        if cls.config_file.temperature.is_overheating(current) and Temperature.elapsed > 0:
            cls.config_file.temperature.elapsed += 1
            log("[PiTemp] - WARN: Temperature is still too high [{}]".format(current))
            if cls.config_file.temperature.elapsed > cls.config_file.temperature.minutes:
                log("[PiTemp] - ERR: Temperature was too hot for too long - rebooting")
                os.popen('sudo reboot')
        elif cls.config_file.temperature.is_overheating(current):
            log("[PiTemp] - WARN: Temp is too high [{}]".format(current))
            cls.config_file.temperature.elapsed += 1
        else:
            cls.config_file.temperature.elapsed = 0

        cls.config_file.temperature.update()