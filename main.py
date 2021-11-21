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

import json
import os
import shutil
import sys
import zipfile

from minecraft.install import Installer
from minecraft.version import Versioner
from util import logger
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
    allottedRam = 2500
    dailyHour = 8

    bootlog = 'bootlog.txt'
    commandfile = 'commands.json'
    logfile = 'logs.txt'

    # setup utilities
    installer = Installer()
    mailer = PiMailer('smtp.gmail.com', 587, 'ras.pi.craun@gmail.com', 'dymdu9-vowjIt-kejvah')
    tempMonitor = PiTemp(70, 3, logfile)
    versioner = Versioner()

    def backup(self):
        logger.log('Backing up the current world...')
        if not os.path.isdir(self.backupsDir):
            os.mkdir(self.backups)
        zipFilename = '{}/world.zip'.format(self.backupsDir)
        zip = zipfile.ZipFile(zipFilename, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.serverDir):
            for file in files:
                zip.write(
                    os.path.join(root, file), 
                    os.path.relpath(os.path.join(root, file), 
                    os.path.join(self.serverDir, '..')))
        zip.close()
        logger.log('Finished creating backup! Preparing to offload...')
        
        # TODO: Offload zip to third-party

    def checkVersion(self):
        logger.log('Checking for version updates! Please wait...')
        body = ''
        subject = 'A new version of the Paper Minecraft server is available!'
        current = self.versioner.getCurrentVersion()
        latest = self.versioner.getLatestVersion()
        if current == None:
            logger.log('No server currently installed! Installing now...')
            self.installer.install()
        elif current['build'] < latest['build']:
            logger.log('Outdated build detected! Installing latest build for {} now...'.format(latest['version']))
            self.installer.install()
        else: 
            build = latest['build']
            version = latest['version']
            subject = 'Minecraft server {}:{} available now!'.format(version, build)
            body = """
                Hello there!
                Just wanted to let you know that a new version of the Paper Miecraft server [{}:{}] has been released!
                If you have a momemnt, please consider updating the server!
                
                Thanks a bunch,
                MinePi
            """.format(version, build)
            logger.log('A new version of the Minecraft server has been detected and an email has been sent to the owner!')
            self.mailer.sendMail('michael.craun@gmail.com', subject, body)

    def commands(self):
        # Execute any server commands given by the owner
        file = os.path.join(self.rootDir, self.commandfile)
        local = open(file, 'r').read()
        jsonCommands = json.loads(local)
        commands = jsonCommands['commands']
        if commands != None and commands != []:
            logger.log('Executing owner commands...')
            for command in commands:
                logger.log('COMMAND: {}'.format(command))
                os.popen(command)

        # Prepare file for next run
        local = open(file, 'w')
        local.write(json.dumps({ "commands" : [  ] }))
        local.close()

    def criticalEventOccured(self, type):
        ubject = 'Oh, no! Your RasPi has encountered a critical event...'
        body = ''

        if self.criticalTemp:
            body += 'Your RasPi has reached and maintained a critical temperature for too long!\n'
            body += 'Log files from your RasPi have been attached below for your convenience.\n'
            body += 'Please take some time to diagnose and fix the issue and then restart your RasPi. :)\n\n'

        self.mailer.sendMail('michael.craun@gmail.com', subject, body, ['logs.txt'])

    def sendLogs(self):
        subject = 'Daily Report [{}]'.format(Date().timestamp())
        body = '''
        Hey there!
        Just sending you your daily report! You can find logs attached below:

        Thanks a bunch,
        MinePi
        
        '''

        # Files sent to the sendMail method cannot be string references, so we will create os path references
        # for these files before sending them
        bootlog = os.path.join(self.rootDir, self.bootlog)
        logfile = os.path.join(self.rootDir, self.logfile)
        self.mailer.sendMail('michael.craun@gmail.com', subject, body, [bootlog, logfile])
        
    # WARN: Should only be called when first creating the MinePi server and/or when transferring the server to 
    # another RasPi!
    # Configures the MinePi for hosting a Minecraft server by completing the following tasks:
    # - Installs any needed dependencies for running the project
    # - Creates the appropriate directories and files:
    #   - minecraft/backups
    #   - minecraft/server
    #   - logfile.txt
    # - Asks user for configuration input
    # - Grant permissions to use shell scripts
    # - Installs current stable version of Minecraft server
    # - Schedules self-maintenance cron jobs
    def setup(self):
        # Sanity check to make absolutely sure that we aren't overwriting anything already on the MinePi
        if os.path.isdir(self.serverDir):
            logger.log('This MinePi has already been configured! Stopping process!')
        else:
            logger.log('Installing needed dependencies! Your input may be required...')
            os.popen('sudo apt-get install screen')
            os.popen('sudo apt-get install python3-pip')
            os.popen('sudo pip install python-crontab')
            
            cron = CronScheduler()
            config = Config()
            installer = Installer()
                
            # Otherwise, continue with configuration
            logger.log('Configuring this MinePi server. Please wait...')
            
            # Create appropriate directories and files
            os.mkdir(self.serverDir)
            os.mkdir(self.backupsDir)
            file = open(self.bootlog, 'w')
            file = open(self.commandfile, 'w')
            file = open(self.logfile, 'w')
            # TODO: Create other files here using `file = ...`
            file.close()
            
            # Run user-needed configuration
            logger.log('WARN: System configuration has not been implemented! Continuing with defaults...')
            logger.log('System configuration defaults are:')
            logger.log('allottedRam={}'.format(self.allottedRam))
            logger.log('rebootSchedule={}'.format(self.dailyHour))
            # config.start()
            # current = config.read()
            # self.allottedRam = current['allottedRam']
            # self.backupHour = current['backupHour']
            
            # Grant permissions to use shell scripts
            os.popen('sudo chmod +x /home/pi/minePi/cron/start-server.sh')
            
            # Install current stable version of Minecraft server
            logger.log('Initializing server jar...')
            self.installer.install()
            
            # Schedule cron jobs
            logger.log('Scheduling self-maintenance cron jobs...')
            cron.createRecurringJob('@reboot', 'start.py', 'server_start')
            cron.createRecurringJob('* * * * *', 'criticalEvents.py', 'event_monitoring')
            cron.createRecurringJob('0 8 * * *', 'reboot.py', 'daily reboot')
            
            # Configuartion is complete; wait 30 seconds, then reboot
            logger.log('Configuration complete! Rebooting this MinePi...')
            time.sleep(30)
            os.popen('python cron/reboot.py')
        
    # Starting the server
    def start(self):
        logger.log('Starting server...')
        ram = '{}M'.format(self.allottedRam)
        self.configure()
        os.popen('sudo ./start-server.sh {} > /home/pi/minePi/bootlog.txt'.format(ram))
        # os.popen('screen bash')
        # os.popen('cd {}'.format(self.serverDir))
        # os.popen('java -XmX{}M -Xms{}M -jar paper.jar nogui'.format(self.allottedRam, self.allottedRam))

    def startMonitors(self):
        # start temperature monitor
        self.tempMonitor.start()

    def trim(self):
        logger.log('trimming the end...')

    def configure(self):
        config = Config()
        current = config.read()
        if current == None:
            logger.log('No cofiguration found! Starting configuration...')
            config.start()

        # parse current and assign config values
        current = config.read()
        self.allottedRam = current['allottedRam']
        self.backupHour = current['backupHour']

    def updateConfig(self):
        logger.log('should update config...')

    def detectCriticalEvents(self):
        if self.tempMonitor.criticalTemperatureReached():
            self.criticalEventOccured('temp')





