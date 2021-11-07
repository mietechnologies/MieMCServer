# Purpose: install the latest version of Minecraft server on call

import os
import requests

class Installer:
    # Determine if a server has been created already
    def serverExists(self):
        if os.path.isdir('../server'):
            dir = os.listdir('../server')
            if len(dir) > 0:
                print('Minecraft server has alread been installed!')
                return True
        print('Minecraft server has not been installed...')
        return False
        
    def currentVersion(self):
        file = open('../server/version.txt')
        version = file.readline()
        print(version)
        
    def latestVersion(self):
        print('checking latest version...')
        link = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
        request = requests.get(link)
        '
        
        '
        json = request.json()
        print(json)
        latestVersion = json['latest']['release']
        return latestVersion
        
    def __init__(self):
        print('starting installer...')
        if self.serverExists():
            latest = self.latestVersion()
            current = self.currentVersion()
            # Fetch latest version 
            # Compare against current version
            # If not on latest version, alert user
        else:
            # Install latest version of Minecraft server with name given
            print('installing latest version of Minecraft server...')
            latest = self.latestVersion()
            








