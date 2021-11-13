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

from minecraft.install import Installer
from minecraft.version import Versioner
from util import cron
from util.config import Config
from util.date import Date
from util.emailer import PiMailer
from util.temp import PiTemp
    
class Main:
    root = os.path.dirname(__file__)
    serverDir = os.path.dirname(__file__)
    
    # config
    allottedRam = 1024
    backupDay = 5
    backupHour = 6
    dailyHour = 8
    weeklyDay = 5
    weeklyHour = 7
    
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
        
        print('Starting server! If you encounter a java exception, please ensure that you have the latest jdk installed...')
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
        
    def messageServer(self, message):
        print('should message server with {}'.format(message))
        
    def dailyClean(self):
        print('should do daily clean...')
        
    def weeklyClean(self):
        print('should do weekly clean...')
        
    def startMonitors(self):
        self.tempMonitor.start()
        cron.createRecurringJob('* * * * *', 'python cron_events.py', 'even_monitoring')
        cron.createRecurringJon('* * * * *', 'python minecraft/dailyCleanMessage.py', 'daily_clean_message')
        cron.createRecurringJon('* * * * *', 'python minecraft/dailyClean.py', 'daily_clean')
        cron.createRecurringJon('* * * * *', 'python minecraft/weeklyBackupMessage.py', 'weekly_backup_message')
        cron.createRecurringJon('* * * * *', 'python minecraft/clean.py', 'weekly_backup')
        cron.createRecurringJon('* * * * *', 'python minecraft/weeklyCleanMessage.py', 'weekly_clean_message')
        cron.createRecurringJon('* * * * *', 'python minecraft/weeklyClean.py', 'weekly_clean')
        
    def clean(self):
        print('cleaning up server...')
        
    def configure(self):
        config = Config()
        current = config.read()
        if current == None: config.start()
            
        # parse current and assign config values
        current = config.read()
        for line in current:
            print(line)
        
    def updateConfig(self):
        print('should update config...')
        
    def install(self):
        installer = Installer()
        self.serverDir = installer.installIfNeeded()
        
    def update(self):
        print('updating server...')
        
    def detectCriticalEvents(self):
        if self.tempMonitor.criticalTemperatureReached():
            self.criticalEventOccured('temp')








