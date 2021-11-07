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
from util.date import Date
from util.emailer import PiMailer
from util.temp import PiTemp
    
class Main:
    
    
    def backup(self):
        print('backing up server...')
        
    def scheduleJobs(self):
        print('starting cron jobs for server...')
        os.popen('cron/./crontab.sh')
        
    def start(self):
        print('starting server...')
        self.scheduleJobs()
        
    def startMonitors(self):
        print('starting monitors...')
        
    def grantPermissions(self):
        print('granting permissions...')
        os.popen('chmod +x cron/crontab.sh')
        
    def clean(self):
        print('cleaning current server...')
        
    def install(self, name):
        print('installing server...')
        installer = Installer()
        installer.serverExists()
        
    def update(self):
        print('updating server...')
        
    def __init__(self):
        self.backup()
        self.grantPermissions()
        self.startMonitors()
        self.start()
        # os.popen("vcgencmd measure_temp").readline()
        
main = Main()
main.install('NERDCraft 1.17')