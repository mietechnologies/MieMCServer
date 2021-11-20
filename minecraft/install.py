# Purpose: This class is responsible for downloading and installing any update needed and/or requested
# This includes the initial installation as well as any automatic updates required. It will:
# 1. Consult with the Versioner to confirm if it needs to download any update
# 2. Download any needed update to a temp directory
#    NOTE: the Installer should not install major or minor updates automatically; only build updates)
# 3. Rename and move the downloaded jar file to the server directory
# 4. Update versionlogs with newest version

import os
import requests
import sys
sys.path.append('..')

from minecraft.version import Versioner
from util.logger import log

class Installer:
    # Like: https://papermc.io/api/v2/projects/paper/versions/1.17.1/builds/386/downloads/paper-1.17.1-386.jar
    downloadUrlTemplate = 'https://papermc.io/api/v2/projects/paper/versions/{}/builds/{}/downloads/{}'
    minecraftDir = os.path.dirname(__file__)
    serverDir = os.path.join(minecraftDir, 'server')
    serverJar = os.path.join(serverDir, 'paper.jar')
    tempJar = os.path.join(minecraftDir, 'paper.jar')
    
    # Initialize utilities
    versioner = Versioner()
    
    def install(self):
        current = self.versioner.getCurrentVersion()
        latest = self.versioner.getLatestVersion()
        shouldInstallLatest = False
        
        # Should install latest server build if not currently installed or if current build is outdated
        if current == None: shouldInstallLatest = True
        elif current['build'] < latest['build']: shouldInstallLatest = True

        # Otherwise, if latest does not match current, user should be alerted
        if shouldInstallLatest: 
            self.installLatest(latest)
        elif current != latest:
            build = latest['build']
            version = latest['version']
            message = 'Version {}:{} has been released! Please consider updating!'.format(version, build)
            log(message)

        log('Version {}:{} has been installed...'.format(latest['version'], latest['build']))

    def installLatest(self, version):
        # Construct download url and download
        log('Downloading latest build of server jar...')
        build = version['build']
        file = version['filename']
        version = version['version']
        url = self.downloadUrlTemplate.format(version, build, file)
        source = self.downloadFrom(url)
        
        # Move downloaded jar to server directory
        log('Moving new jar to server directory...')
        if os.path.isdir(self.serverDir) == False:
            os.mkdir(self.serverDir)
        os.replace(source, self.serverJar)

    def downloadFrom(self, url):
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(self.tempJar, 'wb') as file:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                    else:
                        log('ERR: Unable to download file!')
                        return None

        log('Download complete!')
        return self.tempJar



        




