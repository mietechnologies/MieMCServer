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
import zipfile

from util.cron import CronScheduler
from util.config import Config
from util.date import Date
from util.emailer import PiMailer
from util.temp import PiTemp
    
class Main:
    rootDir = os.path.dirname(__file__)
    backupsDir = os.path.join(rootDir, 'minecraft/backups')
    serverDir = os.path.join(rootDir, 'minecraft/server')
    endDir = os.path.join(serverDir, 'world_the_end/DIM1/region')
    
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
        if not os.path.isdir(self.backupsDir):
            os.mkdir(self.backups)
        zipFilename = '{}/world.zip'.format(self.backups)
        zip = zipfile.ZipFile(zipFilename, 'w', zipfile.ZIP_DEFLATED)
        for root, dir, files in os.walk(self.serverDir):
            for file in files:
                if '.jar' not in file:
                    zip.write(
                        os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                        os.path.join(path, '..')))
        zip.close()
        
    def checkVersion(self):
        print('checking for version updates...')
        
    def criticalEventOccured(self, type):
        ubject = 'Oh, no! Your RasPi has encountered a critical event...'
        body = ''
        
        if self.criticalTemp:
            body += 'Your RasPi has reached and maintained a critical temperature for too long!\n'
            body += 'Log files from your RasPi have been attached below for your convenience.\n'
            body += 'Please take some time to diagnose and fix the issue and then restart your RasPi. :)\n\n'
            
        self.mailer.sendMail('michael.craun@gmail.com', subject, body, ['logs.txt'])
        
    def startMonitors(self):
        # start temperature monitor
        self.tempMonitor.start()
        
        # schedule cron jobs
        CronScheduler().createRecurringJob('* * * * *', 'python cron/cron_events.py', 'event_monitoring')
        CronScheduler().createRecurringJob('0 8 * * *', 'sudo reboot -p', 'daily reboot')
        
    def trim(self):
        print('trimming the end...')
        
    def configure(self):
        config = Config()
        current = config.read()
        if current == None: 
            print('No cofiguration found! Starting configuration...')
            config.start()
            
        # parse current and assign config values
        current = config.read()
        # self.allottedRam = current['allottedRam']
        self.allottedRam = current['allottedRam']
        self.backupDay = current['backupDay']
        self.backupHour = current['backupHour']
        self.dailyClean = current['dailyClean']
        self.weeklyDay = current['weeklyDay']
        self.weeklyHour = current['weeklyHour']
        
    def updateConfig(self):
        print('should update config...')
        
    def detectCriticalEvents(self):
        if self.tempMonitor.criticalTemperatureReached():
            self.criticalEventOccured('temp')








