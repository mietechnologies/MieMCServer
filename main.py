# ****************************** Developer Notes ******************************
# Goal: This script will run and maintain a Minecraft Server, utilizing crontab
# jobs to handle maintenance, and allowing for custom commands to be run from
# the terminal. 
# 1. Setup the basic argument system
#    - No Args: This will be the initial call. It will start everything,
#      from the ground up. It will generate the config file, setup all the
#      needed cron jobs, and start the Minecraft server.
#    - '-mcv', '--mc-version': This will return the currently used Minecraft
#      Server Version.
#    - '-v', '--version': This will return the version of this software.
#    - '-c', '--command': This will accept a string (which will need rapped in
#      quotations) that will run a command on the server (as long as its running)
#    - '-u', '--update': Checks for a Minecraft Server update, and updates if
#      newer version exists.
#    - '-bu', '--backup': This will backup the Minecraft Server
# *****************************************************************************

from util.backup import Backup
from util.date import Date
from util import configuration as c
from minecraft.version import Versioner, UpdateType
from util.mielib.custominput import bool_input
from minecraft.install import Installer
from util.syslog import log, clear_log
from util.emailer import Emailer
from util.cron import CronScheduler
from scripts import reboot
import argparse, sys, os
from rcon import Client
import asyncio
import zipfile
from time import sleep

from util.temp import PiTemp

VERSION = "1.1.2"

def parse(args):
    mc_version = args.minecraft_version
    version = args.version
    command = args.command
    commands = args.commands
    update = args.update
    backup = args.path
    method = args.generate_config
    clean = args.clean
    stop = args.stop
    restart = args.restart
    if c.Temperature.exists():
        critical_events = args.critical_events

    running_log = []

    if debug is not False:
        run_debug()
        print('******* DEBUG EXECUTION FINISHED ******\n')
        return

    # Done
    if mc_version is not False:
        running_log.append('-mcv')
        if c.Minecraft.build is not None:
            log("Minecraft Server: {}".format(c.Minecraft.version_str()))
        else:
            log("Minecraft Server has not been installed yet.")
    
    # Done
    if version is not False:
        running_log.append('-v')
        log("minePi Version v{}".format(VERSION))

    # Done
    if command is not None:
        running_log.append('-c {}'.format(command))
        runCommand(command)
        
    if update is not None:
        running_log.append('-u')
        updateServer(update)

    if backup:
        running_log.append('-bu {}'.format(c.Maintenance.backup_path))
        runCommand("say System is backing up Minecraft world.")
        filename = 'world.{}.zip'.format(Date.strippedTimestamp())
        Backup.put(Installer.server_dir, c.Maintenance.backup_path, filename)

    if method is not None:
        running_log.append('-gc {}'.format(method))
        generateConfig(method)

    if clean:
        running_log.append('-k')
        runCommand("say System maintenance scripts are being ran.")
        maintenance()

    if commands:
        running_log.append('-rc')
        executeCommandList()

    if stop:
        running_log.append('-q')
        runCommand("say The server is being saved, and then stopped in 60 " \
            "seconds.")
        sleep(60)
        stopServer()

    if restart:
        running_log.append('-q')
        runCommand("say The server is being restarted in 60 seconds.")
        sleep(60)
        reboot.run()

    if c.Temperature.exists() and critical_events:
        running_log.append('-ce')
        PiTemp.execute()

    if not running_log:
        run()

def maintenance():
    executeCleanCommands()
    trimEnd()
    executeCustomShellScript()

def executeCleanCommands():
    log('Running clean up commands...')
    dir = os.path.dirname(__file__)
    cleanCommandFile = os.path.join(dir, 'clean-commands.txt')
    for command in linesFromFile(cleanCommandFile):
        runCommand(command)

def executeCommandList():
    log('Running custom commands...')
    dir = os.path.dirname(__file__)
    custom_command_file = os.path.join(dir, 'commands.txt')
    for command in linesFromFile(custom_command_file, deleteFetched=True):
        runCommand(command)

def executeCustomShellScript():
    log('Running custom shell script...')
    dir = os.path.dirname(__file__)
    custom_script = os.path.join(dir, 'scripts/custom-command.sh')
    os.chmod(custom_script, 0o755)
    os.system(custom_script)

def linesFromFile(file: str, deleteFetched: bool = False):
    lines = []
    with open(file, 'r') as fileIn:
        tmpLines = fileIn.readlines()
        fileOut = open(file, 'w')
        for line in tmpLines:
            # Always preserve all comments and empty lines when fetching commands from a file:
            if '#' in line:
                fileOut.write(line)
            elif line == '\n':
                fileOut.write(line)
            # If line is command and fetched commands should be kept:
            elif not deleteFetched:
                lines.append(line.replace('\n', ''))
                fileOut.write(line)
            # If line is command and fetched commands should be removed:
            elif deleteFetched: 
                lines.append(line.replace('\n', ''))
            # Otherwise, the line is unhandled; log the line that was encountered and keep it in the file
            else:
                log('Line from {} not recognized [{}]'.format(file, line))
                fileOut.write(line)
    return lines

def trim_end_regions():
    '''
    Cleans the subdirectories related to the end to serve two purposes:
        1. Eliminates lag related to unused and loaded end chunks
        2. Eliminates the need for players to travel very far to find resources
           related to the end
    '''

    log('Trimming the end!')
    log('To keep specific end regions, update the end-regions.txt file in ' \
        'the project root with the regions you would like to keep.')
    log('To determine what region files to keep, see Xisumavoid\'s video at ' \
        'https://www.youtube.com/watch?v=fGlqDBcgmIc')
    
    # Fetch the end region root directory
    root_dir = os.path.dirname(__file__)
    end_dir = os.path.join(root_dir, 'server/world_the_end/DIM1')

    # Fetch the regions the user would like to keep
    end_region_log = os.path.join(root_dir, 'end-regions.txt')
    regions_to_keep = linesFromFile(end_region_log)
    filecount = 0

    # Iterate through all subdirectories of the end region root directory
    # and the files contained within each
    for directory in os.listdir(end_dir):
        path = os.path.join(end_dir, directory)
        if os.path.isdir(path):
            dir_count = 0
            for file in os.listdir(path):
                # If the file is not listed in the regions to keep, delete it
                if file not in regions_to_keep:
                    region = os.path.join(path, file)
                    os.remove(region)
                    dir_count += 1
                    filecount += 1
            if dir_count > 0:
                log(f'Removed {dir_count} from {directory}!')
    log(f'Finished trimming the end! Removed {filecount} region(s)!')

def run():
    log("Checking config.yml...")
    if c.File.exists:
        log("Found config.yml")
        setupCrontab()
        Installer.install()
        startServer()
    else:
        log("Did not find config.yml")
        generateConfig("manual")
        setupCrontab()
        Installer.install(override_settings = True)
        startServer()
        c.RCON.build()
        

    log("Server started!")

def startMonitorsIfNeeded():
    dir = os.path.dirname(__file__)
    prog = os.path.join(dir, 'main.py')
    scheduler = CronScheduler()

    # Temp if on RasPi
    if c.Temperature.exists():
        log('Start monitor of CPU temp...')
        critical_events_command = 'python {} --critical-events'.format(prog)
        scheduler.createRecurringJob(
            '* * * * *', 
            critical_events_command, 
            'detect_critical_events')

def stopMonitors():
    CronScheduler().removeJob('detect_critical_events')

def startServer():
    startMonitorsIfNeeded()
    log("Starting server...")
    ram = "{}M".format(c.Minecraft.allocated_ram)
    current_dir = os.path.dirname(__file__)
    script_path = os.path.join(current_dir, "scripts/start-server.sh")
    log("Setting up bootlog file...")
    bootlog_path = os.path.join(current_dir, "logs/bootlog.txt")
    server_dir = os.path.join(current_dir, "server")
    os.popen("{} {} {} > {}".format(script_path,
                                    ram,
                                    server_dir,
                                    bootlog_path))

def stopServer():
    stopMonitors()
    runCommand('stop')

def setupCrontab():
    dir = os.path.dirname(__file__)
    prog = os.path.join(dir, 'main.py')
    scheduler = CronScheduler()
    
    restart_command = "python3 {} --run-commands --stop --restart".format(prog)
    scheduler.createRecurringJob(c.Maintenance.complete_shutdown,
                                 restart_command,
                                 "maintenance.restart")
    log("Scheduling crontab job 'maintenance.restart'")
    # Backup
    backup_command = "python3 {} --backup".format(prog)
    scheduler.createRecurringJob(c.Maintenance.backup_schedule,
                                 backup_command,
                                 "maintenance.backup")
    log("Scheduling crontab job 'maintenance.backup'")
    # Maintenance
    maintenance_command = "python3 {} --clean".format(prog)
    scheduler.createRecurringJob(c.Maintenance.schedule,
                                 maintenance_command,
                                 "maintenance.scripts")
    log("Scheduling crontab job 'maintenance.scripts'")
    # Updates
    update_command = "python3 {} --update".format(prog)
    scheduler.createRecurringJob(c.Maintenance.update_schedule,
                                 update_command,
                                 "maintenance.update")
    log("Scheduling crontab job 'maintenance.update'")
    # Reboot
    reboot_command = "python3 {}".format(prog)
    scheduler.createRecurringJob("@reboot",
                                 reboot_command,
                                 "reboot")
    log("Scheduling crontab job 'reboot'")

def generateConfig(method):
    
    if method.lower() == "auto":
        user_response = bool_input("This will override your current " \
        "config.yml, are you sure you want to do that?", default=False)
        if user_response:
            log("Automatically generating a default config.yml")
            c.File.generate()
            log("config.yml generated!")
        else:
            log("Generate config cancelled")
    elif method.lower() == "manual":
        log("Generating user-interactive config.yml", silently=True)
        built = c.File.build()
        if not built:
            log("Generate config cancelled")
        else:
            log("config.yml generated!")
    else:
        print("'{}' is not a valid input. Please consult the help ['-h'] " \
            " menu to learn more. ".format(method))

def updateServer(override):
    if not c.File.data:
        log("Cancelling... You haven't setup a config.yml file yet. You can " \
            "generate a config file by running the command 'python3 main.py -" \
            "gc'")
    else:
        update, version = Versioner.hasUpdate()

        if update is not UpdateType.NONE:
            should_update = False
            output = "You have a {} update. Version {} is available".format(
                update,
                Versioner.versionString(version)
            )
            log(output)

            if update is UpdateType.MAJOR:
                if override.lower() in ["y", "yes", "true"]:
                    should_update = True
                elif not c.Maintenance.update_allow_major_update:
                    log("Did not update due to your settings. Please update " \
                        "manually.")
                    should_update = False
            else:
                should_update = True

            if should_update:
                Installer.install(override_settings=should_update)

def runCommand(command):
    c.RCON.read()
    if c.RCON.enabled and c.RCON.password != '':
        with Client('minecraun.ddns.net', c.RCON.port, passwd=c.RCON.password) as client:
            response = client.run(command)
            # Sqizzle any known errors so we can log them
            if 'Unknown command' in response:
                log('Could not execute command [{}]: {}'.format(command, response))
            elif 'Expected whitespace' in response:
                log('Could not execute command [{}]: {}'.format(command, response))
            elif 'Invalid or unknown' in response:
                log('Could not execute command [{}]: {}'.format(command, response))
            elif response == '': 
                log('Issued server command [{}]'.format(command))
            else: 
                log(response)
    else: 
        log('ERR: RCON has not been correctly initialized!')

def run_debug():
    '''
    A helper method to make debugging and testing the application and 
    implementations easier.
    '''

    # DO NOT DELETE THE LINE BELOW!
    print('\n\n***** EXECUTING DEBUG METHODS ******') 

    print('Copying files from the server; your input may be required...')
    root_dir = os.path.dirname(__file__)
    remote_dir = 'bachapin@mieserver.ddns.net:/home/bachapin/MIE-MCServer/' \
        'server/world_the_end/DIM1'
    local_dir = os.path.join(root_dir, 'server/world_the_end')
    os.system(f'scp -r {remote_dir} {local_dir}')

    trim_end_regions()
    print('\n****** NOTE: The console above should state that several regions ' \
        'were deleted! *******')
    trim_end_regions()
    print('\n****** NOTE: The console above should state that 0 regions were ' \
        'deleted! ******')

def main():

    parser = argparse.ArgumentParser(description="This program is your " \
        "one-stop shop for running and maintaining a Minecraft Server.")

    parser.add_argument('-mcv', '--minecraft-version', help="The version of " \
        "your Minecraft Server.", dest="minecraft_version",
        action="store_true", required=False)

    parser.add_argument('-v', '--version', help="The version of this software.",
        dest="version", action="store_true", required=False)

    parser.add_argument('-c', '--command', help="This will run a command on " \
        "the Minecraft Server", dest="command", type=str, required=False)

    parser.add_argument('-u', '--update', help="Checks to see if there is a " \
        "newer version of Minecraft Server. If there is, it will install the " \
        "latest version.", dest="update", nargs="?", const="", required=False)

    parser.add_argument('-bu', '--backup', help="Backup your Minecraft Server", 
        dest="path", action='store_true', required=False)

    parser.add_argument('-k', '--clean', help='Run clean up scripts to help with '\
        'lag on your Minecraft Server.', dest='clean', action='store_true', 
        required=False)

    parser.add_argument('-r', '--restart', help='This command completely ' \
        'restarts your server hardware.', dest='restart', action='store_true',
        required=False)

    parser.add_argument('-q', '--stop', help='This will stop the Minecraft ' \
        'server.', dest='stop', action='store_true', required=False)

    parser.add_argument('-rc', '--run-commands', help='Run the commands ' \
        'line by line in the commands.txt file.', dest='commands',
        action='store_true', required=False)

    parser.add_argument('-gc', '--generate-config', help="This will generate " \
        "the configuration for this program. It will take one of two inputs: " \
        "'auto' or 'manual'. By picking 'auto' we will handle creating a " \
        "config file for you with some default inputs. If you select 'manual'" \
        " we will ask you a series of questions to build you your config. You" \
        " may manually edit or re-generate your config at any time.", 
        dest="generate_config", nargs="?" ,const="auto", type=str,
        required=False)

    parser.add_argument('-D', '--debug', help='This will run any processes ' \
        'implemented in the runDebug method of main.py. WARN: This command ' \
        'will ignore any and all other commands!', dest='debug', 
        action='store_true', required=False)

    if c.Temperature.exists():
        parser.add_argument('-ce', '--critical-events', help='Checks for any critical ' \
            'events that may be occuring on your Raspberry Pi.', dest='critical_events', action='store_true', required=False)

    parser.set_defaults(func=parse)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
