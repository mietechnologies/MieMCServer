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
    
    # system monitoring
    criticalTemp = False
    logfile = 'logs.txt'
    
    # setup utilities
    mailer = PiMailer('smtp.gmail.com', 587, 'ras.pi.craun@gmail.com', 'dymdu9-vowjIt-kejvah')
    tempMonitor = PiTemp(70, 3, logfile)
    
    def backup(self):
        print('backing up server...')
        
    def start(self, allottedRam):
        # print('Updating jdk installation (your password may be required)...')
        # os.popen('chmod +x jdk.sh')
        # os.popen('./jdk.sh')
        
        print('Starting server! If you a java exception, please ensure that you have the latest jdk installed...')
        os.popen('cd {}'.format(self.serverDir))
        os.popen('java -Xmx{}M -Xms{}M -jar server.jar nogui'.format(allottedRam, allottedRam))
        
    def criticalEventOccured(self, type):
        ubject = 'Oh, no! Your RasPi has encountered a critical event...'
        body = ''
        
        if self.criticalTemp:
            body += 'Your RasPi has reached and maintained a critical temperature for too long!\n'
            body += 'Log files from your RasPi have been attached below for your convenience.\n'
            body += 'Please take some time to diagnose and fix the issue and then restart your RasPi. :)\n\n'
            
        self.mailer.sendMail('michael.craun@gmail.com', subject, body, ['logs.txt'])
        
    def startMonitors(self):
        self.criticalTemp = self.tempMonitor.start()
        
        while True:
            if criticalTemp:
                self.criticalEventOccured('temp')
            
            timestamp = Date().timestamp()
            weekday = Date().weekday()
            hour = Date().hour()
            minute = Date().minute()
            
            if weekday == 0:
                if hour == 6:
                    if minute == 55:
                        print('should be Monday at 2:55 AM; should send message to players. [{}]'.format(timestamp))
                if hour == 7:
                    print('should be Monday at 3 AM; should do weekly cleanup [{}]'.format(timestamp))
            
            if hour == 7:
                if minute == 55:
                    print('should be daily at 3:55 AM; should send message to players [{}]'.format(timestamp))
            if hour == 8:
                print('should be 4 AM on any given day; should do daily cleanup [{}]'.format(timestamp))
        
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
        
main = Main()