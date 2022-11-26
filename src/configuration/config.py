import os
from configuration.email import Email
from configuration.maintenance import Maintenance
from configuration.messaging import Messaging
from configuration.minecraft import Minecraft
from configuration.modded import Modded
from configuration.rcon import RCON
from configuration.server import Server
from configuration.temperature import Temperature
from util import data
from util import path
from util.mielib import custominput as ci

class File:
    __log = None
    __file_dir = path.project_path(filename='config.yml')

    data = {}
    exists = False

    minecraft = Minecraft(data.get('Minecraft', {}))
    email = Email(data.get('Email', {}))
    messaging = Messaging(data.get('Messaging', {}))
    maintenance = Maintenance(data.get('Maintenance', {}))
    modded = Modded(data.get('Modded', {}))
    temperature = Temperature(data.get('Temperature', {}))
    server = Server(data.get('Server', {}))
    rcon = RCON(data.get('RCON', {}))

    def __init__(self, logger):
        self.__log = logger

        parsed = data.parse_yaml(self.__file_dir)
        self.data = {} if parsed is None else parsed
        self.exists = parsed is not None

        self.minecraft = Minecraft(self.data.get('Minecraft', {}))
        self.email = Email(self.data.get('Email', {}))
        self.messaging = Messaging(self.data.get('Messaging', {}))
        self.maintenance = Maintenance(self.data.get('Maintenance', {}))
        self.modded = Modded(self.data.get('Modded', {}), self.__log)
        self.temperature = Temperature(self.data.get('Temperature', {}))
        self.server = Server(self.data.get('Server', {}))
        self.rcon = RCON(self.data.get('RCON', {}), self.__log)

    def update(self):
        data.write_yaml(self.data, self.__file_dir)

    def update_section(self, name: str, child_data: dict):
        '''
        Replaces a specific section of the data dictionary and updates the config.yml
        file.
        '''

        self.data[name] = child_data
        self.update()

    def generate(self):
        self.minecraft.reset()
        self.email.reset()
        self.messaging.reset()
        self.maintenance.reset()

        if os.path.exists(self.__file_dir):
            os.remove(self.__file_dir)
        
        self.minecraft.update()
        self.email.update()
        self.messaging.update()
        self.maintenance.update()
        self.update()

    def build(self):
        if path.isfile(self.__file_dir):
            user_response = ci.bool_input("This will override your current " \
                "config.yml, are you sure you want to do that?", default=False)
            if user_response:
                path.remove(file=self.__file_dir)
            else:
                return False

        print("I will ask a series of questions to build your config.yml\n" \
            "You are free to edit your config.yml file manually after creation.")

        raspberry = ci.bool_input('First, I need to know if you\'re using a ' \
            'Raspberry Pi.', default=False)

        if raspberry:
            self.data['Temperature'] = self.temperature.build()

        self.data['Email'] = self.email.build()
        self.data['Messaging'] = self.messaging.build()
        self.data['Server'] = self.server.build()
        self.data['Maintenance'] = self.maintenance.build()

        # Should not be able to install a modded server on a Raspberry Pi. The
        # system requirements would just be too much for the little guy.
        # if not raspberry:
        if self.modded.query():
            self.data['Modded'] = self.modded.build()
        else:
            self.data['Minecraft'] = self.minecraft.build_object()

        self.data['RCON'] = self.rcon.build()

        self.update()

        return True

    def is_modded(self) -> bool:
        return self.modded.data != {}

    def is_raspberry_pi(self) -> bool:
        return self.temperature.data != {}
