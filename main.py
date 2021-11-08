# On start:
    # Create a backup of the Minecraft server that overwrites any existing backup of the same version
    # Start the Minecraft server
    # Start safety monitoring
    # Grant permissions to run shell scripts
# Weekly
    # Create a backup of the Minecraft server that overwrites any existing backup of the same version
# Daily
    # Run any clean up scripts needed
# On Command
    # Create new server with a specific world name
    # Update server to the latest version if needed

import os

from crontab import CronTab

from minecraft.install import Installer
from minecraft.version import Versioner
from util.date import Date
from util.emailer import PiMailer
from util.temp import PiTemp
    
class Main:
    serverLocation = os.path.dirname(__file__)
    
    def backup(self):
        print('backing up server...')
        
    def scheduleJobs(self):
        os.popen('cron/./crontab.sh')
        
    def start(self):
        print('Updating jdk installation (your password may be required)...')
        os.popen('chmod +x jdk.sh')
        os.popen('./jdk.sh')
        
        # print('Starting server...')
        # os.popen('cd {}'.format(self.serverLocation))
        # os.popen('java -Xmx2500M -Xms2500M -jar server.jar nogui')
        
    def startMonitors(self):
        print('starting monitors...')
        self.scheduleJobs()
        
    def grantPermissions(self):
        os.popen('chmod +x cron/crontab.sh')
        
    def clean(self):
        print('cleaning current server...')
        
    def install(self):
        installer = Installer()
        self.serverLocation = installer.installIfNeeded()
        
    def update(self):
        print('updating server...')
        
    def __init__(self):
        self.install()
        self.backup()
        self.grantPermissions()
        self.startMonitors()
        self.start()
        # os.popen("vcgencmd measure_temp").readline()
        
main = Main()