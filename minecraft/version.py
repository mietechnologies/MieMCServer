# Purpose: This class should act as a global "versioner" for the MinePi project to limit
# repetitive code used in the various other files in the MinePi project.

import sys
sys.path.append('..')

import os
import re
import requests

from util import logger

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
    versionManifestUrlTemplate = 'https://papermc.io/api/v2/projects/paper/version_group/{}'
    manifestUrlTemplate = "https://papermc.io/api/v2/projects/paper/version_group/{}/builds"
    downloadUrlTemplat = "https://papermc.io/api/v2/projects/paper/versions/{}/builds/{}/downloads/{}"
    
    dir = os.path.dirname(__file__)
    serverDir = os.path.join(dir, 'server')
    versionlog = os.path.join(serverDir, 'versionlog.txt')
                
    # Extracts the data that we care about (if it exists) from any JSON return. 
    def extractDataFrom(self, json):
        output = {}
        # If JSON contains an error
        if 'error' in json.keys(): otput['error'] = json['error']
        
        # If JSON is a version packet. Note that this assumes that version and version_group are in order
        # from oldest to newest. If this changes in the future, this method WILL break.
        if 'version_group' in json.keys(): output['versionGroup'] = float(json['version_group'])
        if 'versions' in json.keys(): output['version'] = json['versions'][-1]
        
        # If JSON is a build collection packet. Note that this assumes that build is in order from oldest
        # to newest. If this changes in the furute, this method WILL break.
        if 'builds' in json.keys():
            latestBuild = json['builds'][-1]
            if 'version' in latestBuild.keys(): output['version'] = latestBuild['version']
            if 'build' in latestBuild.keys(): output['build'] = int(latestBuild['build'])
            if 'downloads' in latestBuild.keys():
                downloads = latestBuild['downloads']
                if 'application' in downloads.keys():
                    application = downloads['application']
                    if 'name' in application.keys():
                        output['filename'] = application['name']
                        
        return output
        
    # Reads the current version from the versionlog, if it exists. Otherwise, assumes no server has been
    # installed yet and returns None.
    def getCurrentVersion(self):
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
        # Sanity check; getCurrentVersion should always be called first, but just in case it isn't...
        if self.currentVersionGroup == None:
            logger.log('WARN: No current version group found; did you use getCurrentVersion first?')
            self.getCurrentVersion()
            
        # If currentVersion is still None, there is no version currently installed. Should fetch the
        # latest iteration of the default version (1.17)
        if self.currentVersionGroup == None:
            logger.log('ERR: There is no currently installed Minecraft Server!')
            self.currentVersionGroup = 1.17
            
        # Attempt to download the JSON from the version group 0.01 greater than the current version group
        # If this fails, there is no greater version group, so data for the current version group should 
        # be fetched. Otherwise, there is a new version, so an update message should be displayed.
        # WARN: At some point in the future, the Minecraft Server version numbers may drastically change 
        # and this code has no way to detect that. Ideas to help this situation in the future:
        # - Add a check against the last install date and if it has been more than some arbitrary amount 
        #   of time since the server was updated, we should display a message to alert the user so they 
        #   can update manually.
        versionToCheck = self.currentVersionGroup + 0.01
        newVersionRequest = requests.get(self.versionManifestUrlTemplate.format(versionToCheck))
        statusCode = newVersionRequest.status_code
        if statusCode >= 200 and statusCode < 300: self.latestVersionGroup = versionToCheck
        else: self.latestVersionGroup = self.currentVersionGroup
        
        # Download the JSON from the Paper downloads site
        manifestRequest = requests.get(self.manifestUrlTemplate.format(self.latestVersionGroup))
        manifest = self.extractDataFrom(manifestRequest.json())
        return manifest
        
    # Determine if a server has been created already
    def serverExists(self):
        if os.path.isdir(self.serverRoot) == False:
            os.mkdir(self.serverRoot)
            
        if os.path.isfile(self.changelog) == False:
            changelog = open(self.changelog, "w")
            changelog.close()
            
        serverContents = os.listdir(self.serverRoot)
        if len(serverContents) == 0:
            # No server has been downloaded and/or created yet
            return False
        else:
            # The folder has contents, but it's not completely accurate to say that a sever exists
            # To make positive confirmation that a server has been installed, read the changelog
            # and see if it contains a line that indicates the server has been installed
            changelog = open(self.changelog, 'r').read()
            if '[INSTALL]' in changelog: return True
            else: return False








