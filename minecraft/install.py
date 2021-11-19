import requests

class Installer:
    currentBuild = None
    currentVersion = None
    latestBuild = None
    latestVersion = None
    newVersionUrl = None
    
    def getCurrentVersion(self):
        print('Fetching current version, please wait...')
    
    def getLatestVersion(self):
        print('Fetching latest version, please wait...')
        
        # Download the JSON from the Paper downloads site
        buildsRequest = requests.get('https://papermc.io/api/v2/projects/paper/version_group/1.17/builds')
        buildsJson = buildsRequest.json()
        
        # Grab a reference to the Minecraft build code
        self.latestVersion = buildsJson['version_group']
        
        # Builds come back in earliest to latest, so we grab a reference to the last item in the list
        builds = buildJson['builds']
        latestBuild = builds[-1]
        filename = latestBuild['downloads']['application']['name']
        self.latestBuild = latestBuild['build']
        self.newVersionUrl = 'https://papermc.io/api/v2/projects/paper/versions/{version}/builds/{build}/downloads/{downloads.name}'
        
        
        
        
        
        
        
        
        
        