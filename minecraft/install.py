# Purpose: install the latest version of Minecraft server on call

import os
import re
import requests

from util.date import Date

class Installer:
    dir = os.path.dirname(__file__)
    serverRoot = os.path.join(dir, 'server')
    changelog = os.path.join(serverRoot, 'changelog.txt')
    versionManifest = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
    
    # Determine if a server has been created already
    def serverExists(self):
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
    
    # A helper function to log files to the changelog for the server
    def log(self, message):
        file = open(self.changelog, 'a')
        file.write('[MinePi - {date}] {message}\n'.format(date=Date().timestamp(), message=message))
        file.close()
        
    def installIfNeeded(self):
        if self.serverExists():
            current = self.currentVersion()
            latest = self.latestVersion()
            # If not on latest version, alert user
            if current != latest['id']:
                print('Version {} is now available for release! Consider upgrading at your convenience.'.format(latest['id']))
            location = os.path.join(self.serverRoot, current)
            return location
        else:
            print('No server has been created! Installing now...')
            # Get latest version and version url
            latest = self.latestVersion()
            latestVersion = latest['id']
            manifestUrl = latest['url']
            
            # Get download url by downloading and parsing version manifest
            manifestRequest = requests.get(manifestUrl)
            manifestJson = manifestRequest.json()
            downloadUrl = manifestJson['downloads']['server']['url']
            
            # Create the directory for the version at ../server/{version}
            versionDir = os.path.join(self.serverRoot, latestVersion)
            if os.path.isdir(versionDir) == False:
                os.mkdir(versionDir)
            
            # Download latest version at ../server/{version}/server.jar
            print('Downloading {} server.jar now!'.format(latestVersion))
            location = os.path.join(versionDir, 'server.jar')
            with requests.get(downloadUrl, stream=True) as request:
                request.raise_for_status()
                with open(location, 'wb') as file:
                    for chunk in request.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if and set chunk_size parameter to None.
                        # if chunk:
                        file.write(chunk)
                    return location
            
            # Update changelog with new version
            self.log('[INSTALL] {}'.format(latestVersion))
            

            
            
            








