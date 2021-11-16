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
    allottedRam = 2500
    dailyHour = 8

    logfile = 'logs.txt'

    # setup utilities
    mailer = PiMailer('smtp.gmail.com', 587, 'ras.pi.craun@gmail.com', 'dymdu9-vowjIt-kejvah')
    tempMonitor = PiTemp(70, 3, logfile)

    def backup(self):
        print('Backing up the current world...')
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
        print('Finished creating backup! Preparing to offload...')
        
        # TODO: Offload zip to third-party

    def checkVersion(self):
        print('checking for version updates...')

    def commands(self):
        print('executing owner commands...')

    def criticalEventOccured(self, type):
        ubject = 'Oh, no! Your RasPi has encountered a critical event...'
        body = ''

        if self.criticalTemp:
            body += 'Your RasPi has reached and maintained a critical temperature for too long!\n'
            body += 'Log files from your RasPi have been attached below for your convenience.\n'
            body += 'Please take some time to diagnose and fix the issue and then restart your RasPi. :)\n\n'

        self.mailer.sendMail('michael.craun@gmail.com', subject, body, ['logs.txt'])

    def sendLogs(self):
        print('sending logs to owner...')
        
    # WARN: Should only be called when first creating the MinePi server and/or when transferring the server to 
    # another RasPi!
    # Configures the MinePi for hosting a Minecraft server by completing the following tasks:
    # - Installs any needed dependencies for running the project
    # - Creates the appropriate directories and files:
    #   - minecraft/backups
    #   - minecraft/server
    # - Asks user for configuration input
    # - Grant permissions to use shell scripts
    # - Installs current stable version of Minecraft server
    # - Schedules self-maintenance cron jobs
    def setup(self):
        # Sanity check to make absolutely sure that we aren't overwriting anything already on the MinePi
        if os.path.isdir(self.serverDir):
            print('This MinePi has already been configured! Stopping process!')
        else:
            print('Installing needed dependencies! Your input may be required...')
            os.popen('sudo apt-get install screen')
            os.popen('sudo apt-get install python3-pip')
            os.popen('sudo pip install python-crontab')
            
            cron = CronScheduler()
            config = Config()
                
            # Otherwise, continue with configuration
            print('Configuring this MinePi server. Please wait...')
            
            # Create appropriate directories and files
            os.mkdir(self.serverDir)
            os.mkdir(self.backupsDir)
            file = open(self.logfile, 'w')
            # TODO: Create other files here using `file = ...`
            file.close()
            
            # Run user-needed configuration
            print('WARN: System configuration has not been implemented! Continuing with defaults...')
            print('System configuration defaults are:')
            print('allottedRam={}'.format(self.allottedRam))
            print('rebootSchedule={}'.format(self.dailyHour))
            # config.start()
            # current = config.read()
            # self.allottedRam = current['allottedRam']
            # self.backupHour = current['backupHour']
            
            # Grant permissions to use shell scripts
            os.popen('sudo chmod +x /home/pi/minePi/cron/start-server.sh')
            
            # Install current stable version of Minecraft server
            # print('Installing latest stable version of Minecraft server...')
            print('WARN: Automatic installation of Minecraft Server has not been implemented!')
            print('Please download and install a Paper Minecraft server at /home/pi/minePi/minecraft/server/paper.jar')
            
            # schedule cron jobs
            print('Scheduling self-maintenance cron jobs...')
            cron.createRecurringJob('@reboot', 'start.py', 'server_start')
            cron.createRecurringJob('* * * * *', 'criticalEvents.py', 'event_monitoring')
            cron.createRecurringJob('0 8 * * *', 'reboot.py', 'daily reboot')
            
            # Configuartion is complete; wait 30 seconds, then exit ssh and reboot
            print('Configuration complete! Rebooting this MinePi...')
            time.sleep(30)
            os.popen('python cron/reboot.py')
        
    # Starting the server
    def start(self):
        print('Starting server...')
        ram = '{}M'.format(self.allottedRam)
        self.configure()
        os.popen('sudo ./start-server.sh {}'.format(ram))
        # os.popen('screen bash')
        # os.popen('cd {}'.format(self.serverDir))
        # os.popen('java -XmX{}M -Xms{}M -jar paper.jar nogui'.format(self.allottedRam, self.allottedRam))

    def startMonitors(self):
        # start temperature monitor
        self.tempMonitor.start()

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
        self.allottedRam = current['allottedRam']
        self.backupHour = current['backupHour']

    def updateConfig(self):
        print('should update config...')

    def detectCriticalEvents(self):
        if self.tempMonitor.criticalTemperatureReached():
            self.criticalEventOccured('temp')
