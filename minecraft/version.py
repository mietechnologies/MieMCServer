# Purpose: This class should act as a global "versioner" for the MinePi project to limit
# repetitive code used in the various other files in the MinePi project.

import os
import re
import requests

class Versioner:
    dir = os.path.dirname(__file__)
    serverRoot = os.path.join(dir, 'server')
    changelog = os.path.join(serverRoot, 'changelog.txt')
    versionManifest = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
    
    # Determine if a server has been created already
    def serverExists(self):
        if os.path.isdir(self.serverRoot) == False:
            os.mkdir(self.serverRoot)
            
        if os.path.isfile(self.changelog) == False:
            changelog = open(self.changelog, "w")
            changelog.close()
            
        serverContents = os.listdir(self.serverRoot)
        if len(serverContents) == 0:
            # No server has been downloaded yet
            return False
        else:
            # The folder has contents, but it's not completely accurate to say that a sever exists
            # To make positive confirmation that a server has been installed, read the changelog
            # and see if it contains a line that indicates the server has been installed
            changelog = open(self.changelog, 'r').read()
            if '[INSTALL]' in changelog:
                return True
            else:
                return False
    
    # Fetches the current version by opening the changelog and checking the its lines in reverse order
    # for a version number that has been installed
    def currentVersion(self):
        changelog = open(self.changelog, 'r')
        lines = list(reversed(changelog.readlines()))
        for line in lines:
            if '[INSTALL]' in line:
                result = re.search('\d+\.\d+\.\d+', line)
                if result:
                    version = result.group(0)
                    return version
        return None
    
    # Obtains the latest server release version by downloading the official Minecraft version manifest
    # and extracting the value from the JSON
    def latestVersion(self):
        request = requests.get(self.versionManifest)
        json = request.json()
        latestVersion = json['latest']['release']
        
        # Find latest version url by iterating through versions array defined in json
        versions = json['versions']
        for version in versions:
            if version['id'] == latestVersion:
                return version
                
    # Creates and retuns a directory for a given version
    def fetchVersionDirectory(self, name):
        # Check for and create version folder if needed
        location = os.path.join(self.serverRoot, name)
        if os.path.isdir(location) == False:
            os.mkdir(location)
        
        # Check for and create server.jar if needed
        jar = os.path.join(location, 'server.jar')
        if os.path.isfile(jar) == False:
            file = open(jar, "w")
            file.close()
            
        return location









