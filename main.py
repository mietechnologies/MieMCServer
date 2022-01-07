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

from re import sub
from util.backup import Backup
from util.date import Date
from util import configuration as c
from requests.api import delete
from minecraft.version import Versioner, UpdateType
from util.maintenance import Maintenance
from util.mielib.custominput import bool_input
from minecraft.install import Installer
from util.cron import CronScheduler
from util import configuration as c
from util.backup import Backup
from util.temp import PiTemp
from util.syslog import log
from util.date import Date
from scripts import reboot
from time import sleep
import command as cmd
import argparse
import os

VERSION = "1.0.0"

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
    maintenance_action = args.maintenance
    debug = args.debug
    update_config = args.update_config
    if c.Temperature.exists():
        critical_events = args.critical_events

    if c.Temperature.exists():
        critical_events = args.critical_events

    running_log = []

    if debug is not False:
        runDebug()
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
        running_log.append('-bu {}'.format(c.Maintenance.backup_path))
        cmd.runCommand("say System is backing up Minecraft world.")
        filename = 'world.{}.zip'.format(Date.strippedTimestamp())
        Backup.put(Installer.server_dir, c.Maintenance.backup_path, filename)

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

    if c.Temperature.exists() and critical_events:
        running_log.append('-ce')
        PiTemp.execute()

    if update_config:
        running_log.append('-uc')
        updateConfig(update_config)

    if schedule_maintenance:
        running_log.append('-m')
        Maintenance.schedule()

    if start_maintenance:
        running_log.append('-sm')
        Maintenance.start()

    if end_maintenance:
        running_log.append('-em')
        Maintenance.end()

    if not running_log and not c.Maintenance.is_running():
        run()

def maintenance():
    executeCleanCommands()
    trimEnd()
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

def trimEnd():
    log('Trimming the end!')
    log('To keep specific end regions, update the end-regions.txt file in the project root with the regions you would like to keep.')
    log('To determine what region files to keep, see Xisumavoid\'s video at https://www.youtube.com/watch?v=fGlqDBcgmIc')
    dir = os.path.dirname(__file__)
    endRegionDir = os.path.join(dir, 'server/world_the_end/DIM1/region')
    endRegionLog = os.path.join(dir, 'end-regions.txt')
    regionsToKeep = linesFromFile(endRegionLog)
    filecount = 0
                
    for file in os.listdir(endRegionDir):
        if file not in regionsToKeep:
            region = os.path.join(endRegionDir, file)
            os.remove(region)
            filecount += 1

    log('Finished trimming the end! Removed {} region(s)!'.format(filecount))

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

        # This is presumably the first run so the EULA has not yet been
        # accepted, meaning that starting the server WILL fail
        startServer()

        c.RCON.build()
        root_dir = os.path.dirname(__file__)
        eula = os.path.join(root_dir, 'server/eula.txt')
        if c.Minecraft.accept_eula():
            lines = linesFromFile(eula, False)
            with open(eula, 'w') as eula_out:
                for line in lines:
                    eula_out.write(line.replace('eula=false', 'eula=true'))
            log('User has accepted Minecraft\'s EULA!')
            startServer()
            log("Server started!")
        else:
            log('User has declined Minecraft\'s EULA!')
            log('Gefore running the Minecraft server, you MUST accept ' \
                f'Minecraft\'s EULA by updating the { eula } file!')

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
    cmd.runCommand('stop')

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

def updateConfig(collection):
    
    if collection.lower() == "minecraft":
        c.Minecraft.reset()
        c.Minecraft.build()
    elif collection.lower() == "email":
        c.Email.reset()
        c.Email.build()
    elif collection.lower() == "maintenance":
        c.Maintenance.reset()
        c.Maintenance.build()
    elif collection.lower() == "messaging":
        c.Messaging.reset()
        c.Messaging.build()
    elif collection.lower() == "rcon":
        c.RCON.build()
    elif collection.lower() == "server":
        c.Server.build()
    elif collection.lower() == "temperature":
        c.Temperature.build()

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

def main():

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
        "etc. [not case sensitive])", nargs='?', dest="update_config", 
        type=str, required=False)

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
