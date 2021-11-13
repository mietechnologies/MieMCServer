# Purpose: install the latest version of Minecraft server on call

import os
import requests
import shutil

from util.date import Date
from minecraft.version import Versioner

class Installer:
    dir = os.path.dirname(__file__)
    cleanSciptsDir = os.path.join(dir, 'clean_scripts')
    changelog = os.path.join(dir, 'server/changelog.txt')
    
    # A helper function to log files to the changelog for the server
    def log(self, message):
        file = open(self.changelog, 'a')
        file.write('[MinePi - {date}] {message}\n'.format(date=Date().timestamp(), message=message))
        file.close()
        
    def copyCleanScripts(self, destination):
        # Create server-specific clean_scripts dir
        destinationCleanDir = os.path.join(destination, 'clean_scripts')
        os.mkdir(destinationCleanDir)
        
        # Copy files from clean_scripts dir to server clean_scripts dir and update permissions
        scripts = os.listdir(self.cleanSciptsDir)
        for script in scripts:
            srcPath = os.path.join(self.cleanSciptsDir, script)
            shutil.copy2(srcPath, destinationCleanDir)
            
            destPath = os.path.join(destinationCleanDir, script)
            os.popen('chmod +x {}'.format(destPath))
    
    # If the server has already been installed, returns the location of the latest server.jar file.
    # Otherwise, downloads the latest stable release to the project's directory and returns the 
    # location of the file.
    def installIfNeeded(self):
        versioner = Versioner()
        exists = versioner.serverExists()
        if exists:
            print('Minecraft server already installed! Checking for new versions...')
            current = versioner.currentVersion()
            latest = versioner.latestVersion()
            # If not on latest version, alert user
            if current != latest['id']:
                print('Version {} is now available for release! Consider upgrading at your convenience.'.format(latest['id']))
            location = versioner.fetchVersionDirectory(current)
            return location
        else:
            print('No server has been created! Installing now...')
            # Get latest version and version url
            latest = versioner.latestVersion()
            latestVersion = latest['id']
            manifestUrl = latest['url']
            
            # Get download url by downloading and parsing version manifest
            manifestRequest = requests.get(manifestUrl)
            manifestJson = manifestRequest.json()
            downloadUrl = manifestJson['downloads']['server']['url']
            
            # Download latest version at ../server/{version}/server.jar
            print('Downloading {} server.jar now!'.format(latestVersion))
            versionDir = versioner.fetchVersionDirectory(latestVersion)
            location = os.path.join(versionDir, 'server.jar')
            file = open(location, "r")
            file.close()
            
            with requests.get(downloadUrl, stream=True) as request:
                request.raise_for_status()
                with open(location, 'wb') as file:
                    for chunk in request.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if and set chunk_size parameter to None.
                        # if chunk:
                        file.write(chunk)
                        
                    # Copy clean scripats and update changelog with new version and return
                    self.copyCleanScripts(versionDir)
                    self.log('[INSTALL] {}'.format(latestVersion))
                    return versionDir
            

            
            
            








