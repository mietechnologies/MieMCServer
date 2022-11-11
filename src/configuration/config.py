import os
import yaml
from .email import Email
from .maintenance import Maintenance
from .messaging import Messaging
from .minecraft import Minecraft
from .modded import Modded
from .rcon import RCON
from .server import Server
from .temperature import Temperature
from util.mielib import custominput as ci

class File:
    __util_dir = os.path.dirname(__file__)
    __root_dir = os.path.join(__util_dir, "..")
    __file_dir = os.path.join(__root_dir, "config.yml")

    data = {}
    exists = False

    minecraft = Minecraft(data.get('Minecraft', {}))
    email = Email(data.get('Email', {}))
    messaging = Messaging(data.get('Messaging', {}))
    maintenance = Maintenance(data.get('Maintenance', {}))
    modded = Modded(data.get('Modded', {}))
    temperature = Temperature(data.get('Temperature', {}))
    server = Server(data.get('Server', {}))
    rcon = RCON()

    def __init__(self):
        if os.path.exists(self.__file_dir):
            self.exists = True
            with open(self.__file_dir, "r", encoding='utf8') as file:
                self.data = yaml.load(file, yaml.Loader)
        else:
            self.data = {}

        self.minecraft = Minecraft(self.data.get('Minecraft', {}))
        self.email = Email(self.data.get('Email', {}))
        self.messaging = Messaging(self.data.get('Messaging', {}))
        self.maintenance = Maintenance(self.data.get('Maintenance', {}))
        self.modded = Modded(self.data.get('Modded', {}))
        self.temperature = Temperature(self.data.get('Temperature', {}))
        self.server = Server(self.data.get('Server', {}))
        self.rcon = RCON()

    def update(self):
        with open(self.__file_dir, "w", encoding='utf8') as file:
            yaml.dump(self.data, file, default_flow_style=False)

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

    def build(self):
        if os.path.exists(self.__file_dir):
            user_response = ci.bool_input("This will override your current " \
                "config.yml, are you sure you want to do that?", default=False)
            if user_response:
                os.remove(self.__file_dir)
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

        # Should not be able to install a modded server on a Raspberry Pi. The
        # system requirements would just be too much for the little guy.
        # if not raspberry:
        if self.modded.query():
            self.data['Modded'] = self.modded.build()
        else:
            self.data['Minecraft'] = self.minecraft.build_object()

        self.data['Maintenance'] = self.maintenance.build()

        return True

    def build_rcon(self):
        self.data['RCON'] = self.rcon.build()
        self.update()
