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
    
    currentBuild = None
    currentVersion = None
    currentVersionGroup = None
    latestBuild = None
    latestVersion = None
    latestVersionGroup = None
    newVersionUrl = None
    manifestTemplate = 'https://papermc.io/api/v2/projects/paper/version_group/{}'
    
    
    dir = os.path.dirname(__file__)
    serverDir = os.path.join(dir, 'server')
    versionlog = os.path.join(serverDir, 'versionlog.txt')
    
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
                
    def extractDataFrom(self, json):
        output = {}
        # If JSON contains an error
        if 'error' in json.keys(): otput['error'] = json['error']
        
        # If JSON is a version packet
        if 'version_group' in json.keys(): output['versionGroup'] = json['version_group']
        if 'versions' in json.keys(): output['version'] = json['versions'][-1]
        
        # If JSON is a build collection packet
        if 'builds' in json.keys():
            latestBuild = json['builds'][-1]
            if 'version' in latestBuild.keys(): output['version'] = latestBuild['version']
            if 'build' in latestBuild.keys(): output['build'] = latestBuild['build']
            if 'downloads' in latestBuild.keys():
                downloads = latestBuild['downloads']
                if 'application' in downloads.keys():
                    application = downloads['application']
                    if 'name' in application.keys():
                        output['filename'] = application['name']
                        
        return output
                
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
        
    def getCurrentVersion(self):
        print('Fetching current version, please wait...')
        
        # If the version log exists, we can assume that the Paper server has already been installed, 
        # so we need to parse the lines contained within and pull out the latest version group, 
        # version, and build.
        if os.path.isfile(self.versionlog):
            # Read file's lines, pull out last (latest) and use regex to extract installation data from line
            # Like: [INSTALL - 11/17/2021 06:54:37] 1.17:1.17.1:386
            versionlog = open(self.versionlog, 'r').readlines()
            latestLog = versionlog[-1]
            
            pattern = '\d+.\d+:\d+.\d+.\d+:\d+'
            installData = re.search(pattern, latestLog)
            if installData: 
                data = installData.group(0)
                installation = '{}'.format(data).split(':')
                # Sanity check; if any more or any less, this line is not a valid installation log
                if len(installation) == 3:
                    self.currentBuild = int(installation[2])
                    self.currentVersion = installation[1]
                    self.currentVersionGroup = float(installation[0])
            return { 
                'build' : self.currentBuild, 
                'version' : self.currentVersion, 
                'versionGroup' : self.currentVersionGroup 
            }
        else:
            # No version has been installed yet...
            return None
    
    # Fetches the version and build code of the latest stable release of the Paper Minecraft server jar.
    # WARN: self.getCurrentVersion should always be called before this method!
    def getLatestVersion(self):
        print('Fetching latest version, please wait...')
        
        # Sanity check; getCurrentVersion should always be called first, but just in case it isn't...
        if self.currentVersionGroup == None:
            self.getCurrentVersion()
            
        # If currentVersion is still None, there is no version currently installed. Should just fetch
        # the latest 1.17.1 version by default.
        if self.currentVersionGroup == None:
            self.latestVersionGroup = 1.17
            versionsRequest = requests.get(self.manifestTemplate.format(self.latestVersionGroup))
            manifests = self.extractDataFrom(versionsRequest.json())
            
            # TODO: Implement
            return {  }
            
        # Attempt to download the JSON from the version group 0.01 greater than the current version group
        # If this fails, there is no greater version group, so data for the current version group should 
        # be fetched. Otherwise, there is a new version, so an update message should be displayed.
        # WARN: At some point in the future, the Minecraft Server version numbers may drastically change 
        # and this code has no way to detect that. In the future, we should add a check against the last 
        # install date and if it has been more than some arbitrary amount of time since the server was 
        # updated, we should display a message to alert the user so they can update manually.
        versionToCheck = self.currentVersionGroup + 0.01
        manifestRequest = requests.get(self.manifestTemplate.format(versionToCheck))
        statusCode = manifestRequest.status_code
        if statusCode >= 200 and statusCode < 300: self.latestVersionGroup = versionToCheck
        else: self.latestVersionGroup = self.currentVersionGroup
        
        # TODO: This is wrong...
        # Download the JSON from the latest versions Paper downloads site
        paperManifest = self.manifestTemplate.format(self.latestVersion)
        self.manifestTemplate = '{}/builds'.format(paperManifest)
        manifestRequest = requests.get(self.manifestTemplate)
        manifest = manifestRequest.json()
    
        # TODO: This is wrong...    
        # Builds come back in earliest to latest, so we grab a reference to the last item in the list
        # and capture the data we need from it
        builds = manifest['builds']
        latestBuild = builds[-1]
        filename = latestBuild['downloads']['application']['name']
        self.latestVersion = latestBuild['version']
        self.latestBuild = latestBuild['build']
        self.newVersionUrl = 'https://papermc.io/api/v2/projects/paper/versions/{}/builds/{}/downloads/{}'.format(self.latestVersion, self.latestBuild, filename)
        
        # TODO: This is wrong...
        return { 
            'version' : self.latestVersion, 
            'build' : self.latestBuild, 
            'download' : self.newVersionUrl 
        }









versioner = Versioner()
print(versioner.getCurrentVersion())
print(versioner.getLatestVersion())