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

import argparse
import command as cmd
import subprocess
import os
from time import sleep

from util import path, shell
from util.backup import Backup
from util.date import Date
from configuration import config
from minecraft.version import Versioner, UpdateType
from util.maintenance import Maintenance
from util.mielib.custominput import bool_input
from minecraft.install import Installer
from util.cron import CronScheduler
from util.backup import Backup
from util.path import project_path
from util.temp import PiTemp
from util.logger import log
from util.date import Date
from scripts import reboot

VERSION = "1.2.1"

def parse(args):
    config_file = config.File()

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
    maintenance_action = args.maintenance
    debug = args.debug
    update_config = args.update_config
    if config_file.is_raspberry_pi():
        critical_events = args.critical_events

    if config_file.is_raspberry_pi():
        critical_events = args.critical_events

    running_log = []

    if debug is not False:
        run_debug()
        return

    # Done
    if mc_version is not False:
        running_log.append('-mcv')
        if config_file.minecraft.build is not None:
            log("Minecraft Server: {}".format(config_file.Minecraft.version_str()))
        else:
            log("Minecraft Server has not been installed yet.")

    # Done
    if version is not False:
        running_log.append('-v')
        log("minePi Version v{}".format(VERSION))

    if command is not None:
        running_log.append('-c {}'.format(command))
        if command == "":
            cmd.runTerminal()
        else:
            cmd.runCommand(command)

    if update is not None:
        running_log.append('-u')
        updateServer(update)

    if backup:
        running_log.append('-bu {}'.format(config_file.maintenance.path()))
        cmd.runCommand("say System is backing up Minecraft world.")
        filename = 'world.{}.zip'.format(Date.strippedTimestamp())
        Backup.put(Installer.server_dir, config_file.maintenance.path(), filename)

    if method is not None:
        running_log.append('-gc {}'.format(method))
        generateConfig(method)

    if clean:
        running_log.append('-k')
        cmd.runCommand("say System maintenance scripts are being ran.")
        maintenance()

    if commands:
        running_log.append('-rc')
        executeCommandList()

    if stop:
        running_log.append('-q')
        cmd.runCommand("say The server is being saved, and then stopped " \
            "in 60 seconds.")
        sleep(60)
        stopServer()

    if restart:
        running_log.append('-q')
        cmd.runCommand("say Saving and stopping server in 30 seconds for system " \
            "restart.")
        sleep(30)
        stopServer()
        sleep(60)
        reboot.run()

    if maintenance_action is not None:
        running_log.append(f'-m {maintenance_action}')
        if maintenance_action == 'schedule':
            Maintenance.schedule()
        elif maintenance_action == 'start':
            Maintenance.start()
        else:
            Maintenance.end()

    if config_file.temperature.exists() and critical_events:
        running_log.append('-ce')
        PiTemp.execute()

    if update_config:
        running_log.append('-uc')
        updateConfig(update_config)

    if not running_log and not config_file.maintenance.maintenance_running:
        run()

def maintenance():
    executeCleanCommands()
    trim_end_regions()
    executeCustomShellScript()

def executeCleanCommands():
    log('Running clean up commands...')
    dir = os.path.dirname(__file__)
    cleanCommandFile = os.path.join(dir, 'clean-commands.txt')
    cmd.runTerminal(linesFromFile(cleanCommandFile))

def executeCommandList():
    log('Running custom commands...')
    dir = os.path.dirname(__file__)
    custom_command_file = os.path.join(dir, 'commands.txt')
    cmd.runTerminal(linesFromFile(custom_command_file, deleteFetched=True))

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
    config_file = config.File()

    if config_file.exists:
        log("Found config.yml")
        setupCrontab()
        start_server()
    else:
        log("Did not find config.yml")
        generateConfig("manual")
        setupCrontab()

        if config_file.is_modded():
            print('Please restart your system to complete installation.')
        else:
            # This is presumably the first run so the EULA has not yet been
            # accepted, meaning that starting the server WILL fail
            start_server()

            root_dir = os.path.dirname(__file__)
            eula = os.path.join(root_dir, 'server/eula.txt')
            if config_file.minecraft.accept_eula():
                lines = linesFromFile(eula, False)
                with open(eula, 'w') as eula_out:
                    for line in lines:
                        eula_out.write(line.replace('eula=false', 'eula=true'))
                log('User has accepted Minecraft\'s EULA!')
                start_server()
                log("Server started!")
            else:
                log('User has declined Minecraft\'s EULA!')
                log('Gefore running the Minecraft server, you MUST accept ' \
                    f'Minecraft\'s EULA by updating the { eula } file!')

def run_debug():
    '''
    A method for running any debug functionality. For PR verification purposes,
    any methods and functionality called here should be left here for your PR to
    allow your PR reviewer to easily pull down and test any changes you make.
    '''
    # Shut off calling server commands for debugging purposes
    cmd.DEBUG = True

    # DO NOT DELETE EITHER OF THE DEBUGGING LINES
    # These are here to give you and testers clear start and stop lines for debugging.
    print('\n****** DEBUGGING STARTED ******\n')
    
    modded = config.File().modded
    modded.build()

    print('\n***** DEBUGGING FINISHED ******\n')

def startMonitorsIfNeeded():
    dir = os.path.dirname(__file__)
    prog = os.path.join(dir, 'main.py')
    scheduler = CronScheduler()
    config_file = config.File()

    # Temp if on RasPi
    if config_file.temperature.exists():
        log('Start monitor of CPU temp...')
        critical_events_command = 'python {} --critical-events'.format(prog)
        scheduler.createRecurringJob(
            '* * * * *', 
            critical_events_command, 
            'detect_critical_events')

def stopMonitors():
    CronScheduler().removeJob('detect_critical_events')

def start_server():
    """
    Starts the server... I mean, the name of the method kinda says it all, no?
    NOTE: This method will start the modded server if configured OR will start the
    Vanilla server otherwise.
    """

    config_file = config.File()

    startMonitorsIfNeeded()
    log("Starting server...")
    server = path.project_path('server')
    bootlog = path.project_path('logs', 'bootlog.txt')

    if config_file.is_modded():
        shell.run(f'{config_file.modded.run_command()} > {bootlog}', server)
    else:
        Installer.install()
        ram = f'{config_file.minecraft.allocated_ram}M'
        script = path.project_path('scripts', 'start-server.sh')
        shell.run(f'{script} {ram} {server} > {bootlog}')

def stopServer():
    stopMonitors()
    cmd.runCommand('stop')

def setupCrontab():
    dir = os.path.dirname(__file__)
    prog = os.path.join(dir, 'main.py')
    scheduler = CronScheduler()
    config_file = config.File()
    
    restart_command = "python3 {} --run-commands --stop --restart".format(prog)
    scheduler.createRecurringJob(config_file.maintenance.complete_shutdown,
                                 restart_command,
                                 "maintenance.restart")
    log("Scheduling crontab job 'maintenance.restart'")
    # Backup
    backup_command = "python3 {} --backup".format(prog)
    scheduler.createRecurringJob(config_file.maintenance.backup_schedule(),
                                 backup_command,
                                 "maintenance.backup")
    log("Scheduling crontab job 'maintenance.backup'")
    # Maintenance
    maintenance_command = "python3 {} --clean".format(prog)
    scheduler.createRecurringJob(config_file.maintenance.schedule,
                                 maintenance_command,
                                 "maintenance.scripts")
    log("Scheduling crontab job 'maintenance.scripts'")
    # Updates
    update_command = "python3 {} --update".format(prog)
    scheduler.createRecurringJob(config_file.maintenance.update_schedule(),
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
    config_file = config.File()
    
    if method.lower() == "auto":
        user_response = bool_input("This will override your current " \
        "config.yml, are you sure you want to do that?", default=False)
        if user_response:
            log("Automatically generating a default config.yml")
            config_file.generate()
            log("config.yml generated!")
        else:
            log("Generate config cancelled")
    elif method.lower() == "manual":
        log("Generating user-interactive config.yml", silently=True)
        built = config_file.build()
        if not built:
            log("Generate config cancelled")
        else:
            log("config.yml generated!")
    else:
        print("'{}' is not a valid input. Please consult the help ['-h'] " \
            " menu to learn more. ".format(method))

def updateConfig(collection):
    config_file = config.File()
    
    if collection.lower() == "minecraft":
        config_file.minecraft.reset()
        config_file.minecraft.build()
    elif collection.lower() == "email":
        config_file.email.reset()
        config_file.email.build()
    elif collection.lower() == "maintenance":
        config_file.maintenance.reset()
        config_file.maintenance.build()
    elif collection.lower() == "messaging":
        config_file.messaging.reset()
        config_file.messaging.build()
    elif collection.lower() == "rcon":
        config_file.rcon.build()
    elif collection.lower() == "server":
        config_file.server.build()
    elif collection.lower() == "temperature":
        config_file.temperature.build()

def updateServer(override):
    config_file = config.File()

    if not config_file.exists:
        log("Cancelling... You haven't setup a config.yml file yet. You can " \
            "generate a config file by running the command 'python3 main.py -" \
            "gc'")
    elif config_file.is_modded():
        log('Cancelling... You have chosen to set up a modded server and this functionality ' \
            'doesn\'t exist yet.')
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
                elif not config_file.maintenance.allows_major_udpates():
                    log("Did not update due to your settings. Please update " \
                        "manually.")
                    should_update = False
            else:
                should_update = True

            if should_update:
                Installer.install(override_settings=should_update)

def installRequirements():
    requirements = project_path('', 'requirements.txt')
    with subprocess.Popen('pip install pipreqs') as process:
        process.communicate()
    with subprocess.Popen('pipreqs') as process:
        process.communicate()
    with subprocess.Popen(f'pip install -r {requirements}') as process:
        process.communicate()

def main():
    # installRequirements()

    parser = argparse.ArgumentParser(description="This program is your " \
        "one-stop shop for running and maintaining a Minecraft Server.")

    parser.add_argument('-mcv', '--minecraft-version', help="The version of " \
        "your Minecraft Server.", dest="minecraft_version",
        action="store_true", required=False)

    parser.add_argument('-v', '--version', help="The version of this software.",
        dest="version", action="store_true", required=False)

    parser.add_argument('-c', '--command', help="If ran by itself, without " \
        "the addition of an argument, this will start a terminal which you " \
        "can enter multiple commands in sequence. If an argument is passed " \
        "it will run that command only. In order to stop the terminal you " \
        "can enter '!exit' and it will safely end the terminal session.", 
        dest="command", nargs="?", const="", type=str, required=False)

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

    parser.add_argument(
        '-m',
        '--maintenance',
        help='Schedule, start, or end maintenance for your Minecraft server ' \
            'or hosting system.',
        const='schedule',
        type=str,
        nargs='?',
        choices=('schedule', 'start', 'end')
    )

    parser.add_argument('-uc', '--update-config', help="This command enables " \
        "the user to update a configuration collection by passing the " \
        "desired collection's name in as a parameter. (i.e. Email, Minecraft, " \
        "etconfig_file. [not case sensitive])", nargs='?', dest="update_config", 
        type=str, required=False)

    parser.add_argument('-D', '--debug', help='This will run any processes ' \
        'implemented in the runDebug method of main.py. WARN: This command ' \
        'will ignore any and all other commands!', dest='debug', 
        action='store_true', required=False)

    config_file = config.File()
    if config_file.is_raspberry_pi():
        parser.add_argument('-ce', '--critical-events', help='Checks for any critical ' \
            'events that may be occuring on your Raspberry Pi.', dest='critical_events', action='store_true', required=False)

    parser.set_defaults(func=parse)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
