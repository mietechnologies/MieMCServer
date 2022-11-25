import os

class PiTemp:
    __configuration = None
    __log = None

    @classmethod
    def __init__(cls, configuration, logger):
        cls.__configuration = configuration
        cls.__log = logger

    @classmethod
    def measure(cls):
        '''
        Measures the current temperature of the Raspberry Pi's CPU.
        '''
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

        temperature_config = cls.__configuration.temperature
        current = cls.measure()
        if temperature_config.is_overheating(current) and temperature_config.elapsed > 0:
            temperature_config.elapsed += 1
            cls.__log(f"[PiTemp] - WARN: Temperature is still too high [{current}]")
            if temperature_config.elapsed > temperature_config.minutes:
                cls.__log("[PiTemp] - ERR: Temperature was too hot for too long - rebooting")
                os.popen('sudo reboot')
        elif temperature_config.is_overheating(current):
            cls.__log(f"[PiTemp] - WARN: Temp is too high [{current}]")
            temperature_config.elapsed += 1
        else:
            temperature_config.elapsed = 0

        temperature_config.update()