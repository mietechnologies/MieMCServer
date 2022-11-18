from util.logger import log
from util.mielib import custominput as ci
from util.path import isfile, project_path
from util.extension import cleanString

class RCON:
    enabled = False
    password = None
    port = None

    def build(self):
        print('RCON is a protocol that allows server administrators to ' \
            'remotely execute Minecraft commands.')
        print('Mie-MCServer uses RCON to run clean up commands to ' \
            'automatically maintain your server.')
        print('Please take a moment to set up RCON by answering the ' \
            'following questions.')
        self.port = ci.int_input('What internet port would you like to use ' \
            'for RCON?', 25575)
        self.password = ci.password_input('What password would you like to ' \
            'use for issuing commands via RCON?', pattern=r'^[a-zA-Z0-9_]+$')
        self.enabled = True
        self.update()

    def read(self):
        properties = project_path('server/server.properties')
        if isfile(properties):
            with open(properties, 'r', encoding='utf8').readlines() as lines:
                for line in lines:
                    if 'rcon.port' in line:
                        self.port = int(cleanString(line, ['rcon.port=', '\n']))
                    elif 'enable-rcon' in line:
                        self.enabled = bool(cleanString(line, ['enable-rcon=', '\n']))
                    elif 'rcon.password' in line:
                        self.password = cleanString(line, ['rcon.password=', '\n'])
        else:
            from ..util.logger import log
            log('ERR: No server.properties file found!')

    def update(self):
        properties = project_path('server', 'server.properties')
        if isfile(properties):
            with open(properties, 'r', encoding='utf8') as file_in:
                lines = file_in.readlines()
                with open(properties, 'w', encoding='utf8') as file_out:
                    for line in lines:
                        if 'rcon.port' in line:
                            line = f'rcon.port={self.port}\n'
                        elif 'enable-rcon' in line:
                            line = f'enable-rcon={self.enabled}\n'.lower()
                        elif 'rcon.password' in line:
                            line = f'rcon.password={self.password}\n'
                        
                        file_out.write(line)
        else:
            log('ERR: No server.properties file found!')

