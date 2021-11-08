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

import shutil
import os

from crontab import CronTab

from minecraft.install import Installer
from minecraft.version import Versioner
from util.date import Date
from util.emailer import PiMailer
from util.temp import PiTemp
    
class Main:
    root = os.path.dirname(__file__)
    serverDir = os.path.dirname(__file__)
    
    def backup(self):
        print('backing up server...')
        
    def start(self, allottedRam):
        # print('Updating jdk installation (your password may be required)...')
        # os.popen('chmod +x jdk.sh')
        # os.popen('./jdk.sh')
        
        print('Starting server! If you a java exception, please ensure that you have the latest jdk installed...')
        os.popen('cd {}'.format(self.serverDir))
        os.popen('java -Xmx{}M -Xms{}M -jar server.jar nogui'.format(allottedRam, allottedRam))
        
    def startMonitors(self):
        print('starting monitors...')
        
    def clean(self):
        print('cleaning up server...')
        
    def install(self):
        installer = Installer()
        self.serverDir = installer.installIfNeeded()
        
    def update(self):
        print('updating server...')
        
    def __init__(self):
        self.install()
        self.backup()
        self.startMonitors()
        self.start(3 * 1024)
        # os.popen("vcgencmd measure_temp").readline()
        
main = Main()