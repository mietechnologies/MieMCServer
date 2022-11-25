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
from typing import List
import subprocess
import os
from time import sleep

import command as cmd
from configuration import config
from minecraft.install import Installer
from minecraft.interactions import install_datapack
from minecraft.version import Versioner, UpdateType
from scripts import reboot
from util import files, path, scripting, shell
from util.backup import Backup
from util.date import Date
from util.backup import Backup
from util.date import Date
from util.maintenance import Maintenance
from util.mielib.custominput import bool_input
from util.cron import CronScheduler
from util.backup import Backup
from util.monitor import Monitor
from util.path import project_path
from util.temp import PiTemp
from util.logger import log
from util.date import Date

VERSION = "1.4.0"

def parse(args):
    configuration = config.File(log)

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
    if configuration.is_raspberry_pi():
        critical_events = args.critical_events

    if configuration.is_raspberry_pi():
        critical_events = args.critical_events

    running_log = []

    if debug is not False:
        run_debug()
        return

    # Done
    if mc_version is not False:
        running_log.append('-mcv')
        if configuration.minecraft.build is not None:
            log(f"Minecraft Server: {configuration.minecraft.version_str()}")
        else:
            log("Minecraft Server has not been installed yet.")

    # Done
    if version is not False:
        running_log.append('-v')
        log(f"minePi Version v{VERSION}")

    if command is not None:
        running_log.append(f'-c {command}')
        if command == "":
            cmd.run_terminal(configuration)
        else:
            cmd.run_command(command, configuration)

    if update is not None:
        running_log.append('-u')
        updateServer(update, configuration)

    if backup:
        running_log.append(f'-bu {configuration.maintenance.path()}')
        cmd.run_command("say System is backing up Minecraft world.", configuration)
        filename = f'world.{Date.strippedTimestamp()}.zip'
        backup_manager = Backup(configuration, log)
        backup_manager.put(Installer.server_dir, configuration.maintenance.path(), filename)

    if method is not None:
        running_log.append(f'-gc {method}')
        generate_config(method, configuration)

    if clean:
        running_log.append('-k')
        scripting.maintenance(configuration)

    if commands:
        running_log.append('-rc')
        scripting.run_user_commands()

    if stop:
        running_log.append('-q')
        cmd.run_command("say The server is being saved, and then stopped " \
            "in 60 seconds.", configuration)
        sleep(60)
        stop_server(configuration)

    if restart:
        running_log.append('-q')
        cmd.run_command("say Saving and stopping server in 30 seconds for system " \
            "restart.", configuration)
        sleep(30)
        stop_server(configuration)
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

    if configuration.temperature.exists() and critical_events:
        running_log.append('-ce')
        PiTemp.execute()

    if update_config:
        running_log.append('-uc')
        updateConfig(update_config, configuration)

    running_log = __parse_interaction_methods(args, running_log)

    if not running_log:
        run(configuration)

def __parse_interaction_methods(args, running_log: List[str]) -> List[str]:
    datapack_path = args.install_datapack

    if datapack_path:
        running_log.append(f'-dp {datapack_path}')
        install_datapack(datapack_path)

    return running_log

def maintenance(configuration):
    execute_clean_commands(configuration)
    trim_end_regions()
    execute_custom_shell_script()

def execute_clean_commands(configuration):
    log('Running clean up commands...')
    file = project_path('scripts', 'clean-commands.txt')
    cmd.run_terminal(configuration, files.lines_from_file(file))

def execute_command_list(configuration):
    log('Running custom commands...')
    custom_command_file = project_path('scripts', 'commands.txt')
    cmd.run_terminal(configuration, files.lines_from_file(custom_command_file, deleteFetched=True))

def execute_custom_shell_script():
    log('Running custom shell script...')
    custom_script = project_path('scripts', 'custom-command.sh')
    os.chmod(custom_script, 0o755)
    os.system(custom_script)

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
    regions_to_keep = files.lines_from_file(end_region_log)
    filecount = 0

    # Iterate through all subdirectories of the end region root directory
    # and the files contained within each
    for directory in os.listdir(end_dir):
        end_regions = os.path.join(end_dir, directory)
        if os.path.isdir(end_regions):
            dir_count = 0
            for file in os.listdir(end_regions):
                # If the file is not listed in the regions to keep, delete it
                if file not in regions_to_keep:
                    region = os.path.join(end_regions, file)
                    os.remove(region)
                    dir_count += 1
                    filecount += 1
            if dir_count > 0:
                log(f'Removed {dir_count} from {directory}!')
    log(f'Finished trimming the end! Removed {filecount} region(s)!')

def run(configuration: config.File):
    log('Installing prerequisites...')
    __project_preinstalls()

    log("Checking config.yml...")

    if configuration.exists:
        log("Found config.yml")
        setup_crontab(configuration)
        start_server(configuration)
    else:
        log("Did not find config.yml")
        generate_config("manual", configuration)
        setup_crontab(configuration)

        if configuration.is_modded():
            if bool_input('Would you like to restart the system to start the server ' \
                'automatically?'):
                reboot.run()
            else:
                log('Please restart the system to start the server.')
        else:
            # This is presumably the first run so the EULA has not yet been
            # accepted, meaning that starting the server WILL fail
            start_server(configuration)

            eula = project_path('server', 'eula.txt')
            if configuration.minecraft.accept_eula():
                files.update(eula, 'eula=false', 'eula=true')
                log('User has accepted Minecraft\'s EULA!')
                start_server(configuration)
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
    # Implement any debug functionality below:

    eula = project_path('server', 'eula.txt')
    files.update(eula, 'eula=false', 'eula=true')

    # DO NOT DELETE THE BELOW LINE
    # Deleting this line WILL cause build errors!!
    print('\n***** DEBUGGING FINISHED ******\n')

def startMonitorsIfNeeded(configuration: config.File):
    prog = project_path(filename='main.py')
    scheduler = CronScheduler()

    # Start general system monitors
    monitors = Monitor()
    monitors.start_server_start_monitor(
        timeout=configuration.maintenance.startup_timeout,
        log=log)

    # Temp if on RasPi
    if configuration.temperature.exists():
        log('Start monitor of CPU temp...')
        critical_events_command = f'python {prog} --critical-events'
        scheduler.createRecurringJob(
            '* * * * *',
            critical_events_command,
            'detect_critical_events'
        )

def stopMonitors():
    CronScheduler().removeJob('detect_critical_events')

def start_server(configuration: config.File):
    """
    Starts the server... I mean, the name of the method kinda says it all, no?
    NOTE: This method will start the modded server if configured OR will start the
    Vanilla server otherwise.
    """

    startMonitorsIfNeeded(configuration)
    log("Starting server...")
    server = path.project_path('server')
    bootlog = path.project_path('logs', 'bootlog.txt')

    if configuration.is_modded():
        shell.run(f'{configuration.modded.run_command()} > {bootlog}', server)
    else:
        Installer.install()
        scripting.start(configuration.minecraft.allocated_ram)

def stop_server(configuration):
    stopMonitors()
    scripting.stop()
    cmd.run_command('stop', configuration)

def __project_preinstalls():
    print('Pre-installing needed dependencies to run this command; your ' \
        'input may be required!')

    this_dir = os.path.dirname(__file__)
    logs_dir = os.path.join(this_dir, 'logs')
    requirements = os.path.join(logs_dir, 'requirements.txt')

    os.system('apt-get install python3-pip')
    os.system('pip install pipreqs')
    os.system(f'pipreqs {logs_dir}')
    os.system(f'pip install -r {requirements}')
    os.remove(requirements)

def setup_crontab(configuration: config.File):
    prog = project_path(filename='main.py')
    scheduler = CronScheduler()

    log("Scheduling crontab job 'maintenance.restart'")
    restart_command = f"python3 {prog} --run-commands --stop --restart"
    scheduler.createRecurringJob(
        configuration.maintenance.complete_shutdown,
        restart_command,
        "maintenance.restart"
    )

    # Backup
    log("Scheduling crontab job 'maintenance.backup'")
    backup_command = f"python3 {prog} --backup"
    scheduler.createRecurringJob(
        configuration.maintenance.backup_schedule(),
        backup_command,
        "maintenance.backup"
    )

    # Maintenance
    log("Scheduling crontab job 'maintenance.scripts'")
    maintenance_command = f"python3 {prog} --clean"
    scheduler.createRecurringJob(
        configuration.maintenance.schedule,
        maintenance_command,
        "maintenance.scripts"
    )
    
    # Updates
    log("Scheduling crontab job 'maintenance.update'")
    update_command = f"python3 {prog} --update"
    scheduler.createRecurringJob(
        configuration.maintenance.update_schedule(),
        update_command,
        "maintenance.update"
    )

    # Reboot
    log("Scheduling crontab job 'reboot'")
    reboot_command = f"python3 {prog}"
    scheduler.createRecurringJob(
        "@reboot",
        reboot_command,
        "reboot"
    )

def generate_config(method: str, configuration: config.File):
    if method.lower() == "auto":
        user_response = bool_input("This will override your current " \
        "config.yml, are you sure you want to do that?", default=False)
        if user_response:
            log("Automatically generating a default config.yml")
            configuration.generate()
            log("config.yml generated!")
        else:
            log("Generate config cancelled")
    elif method.lower() == "manual":
        log("Generating user-interactive config.yml", silently=True)
        built = configuration.build()
        if not built:
            log("Generate config cancelled")
        else:
            log("config.yml generated!")
    else:
        print(f"'{method}' is not a valid input. Please consult the help ['-h'] " \
            " menu to learn more. ")

def updateConfig(collection: str, configuration: config.File):
    if collection.lower() == "minecraft":
        configuration.minecraft.reset()
        configuration.minecraft.build()
    elif collection.lower() == "email":
        configuration.email.reset()
        configuration.email.build()
    elif collection.lower() == "maintenance":
        configuration.maintenance.reset()
        configuration.maintenance.build()
    elif collection.lower() == "messaging":
        configuration.messaging.reset()
        configuration.messaging.build()
    elif collection.lower() == "rcon":
        configuration.rcon.build()
    elif collection.lower() == "server":
        configuration.server.build()
    elif collection.lower() == "temperature":
        configuration.temperature.build()

def updateServer(override, configuration: config.File):
    if not configuration.exists:
        log("Cancelling... You haven't setup a config.yml file yet. You can " \
            "generate a config file by running the command 'python3 main.py -" \
            "gc'")
    elif configuration.is_modded():
        log('Cancelling... You have chosen to set up a modded server and this functionality ' \
            'doesn\'t exist yet.')
    else:
        update, version = Versioner.has_update()

        if update is not UpdateType.NONE:
            should_update = False
            output = f"You have a {update} update. Version {Versioner.version_string(version)} ' \
                'is available"
            log(output)

            if update is UpdateType.MAJOR:
                if override.lower() in ["y", "yes", "true"]:
                    should_update = True
                elif not configuration.maintenance.allows_major_udpates():
                    log("Did not update due to your settings. Please update " \
                        "manually.")
                    should_update = False
            else:
                should_update = True

            if should_update:
                Installer.install(override_settings=should_update)

def installRequirements():
    requirements = project_path(filename='requirements.txt')
    with subprocess.Popen('pip install pipreqs') as process:
        process.communicate()
    with subprocess.Popen('pipreqs') as process:
        process.communicate()
    with subprocess.Popen(f'pip install -r {requirements}') as process:
        process.communicate()

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
        "etconfig_file. [not case sensitive])", nargs='?', dest="update_config", 
        type=str, required=False)

    parser.add_argument('-D', '--debug', help='This will run any processes ' \
        'implemented in the runDebug method of main.py. WARN: This command ' \
        'will ignore any and all other commands!', dest='debug', 
        action='store_true', required=False)

    __add_helper_methods(parser)

    config_file = config.File(log)
    if config_file.is_raspberry_pi():
        parser.add_argument(
            '-ce',
            '--critical-events',
            help='Checks for any critical events that may be occuring on your Raspberry Pi.',
            dest='critical_events',
            action='store_true',
            required=False
        )

    parser.set_defaults(func=parse)
    args = parser.parse_args()
    args.func(args)

def __add_helper_methods(parser: argparse.ArgumentParser):
    parser.add_argument('-dp', '--install-datapack', help='This command ' \
        'installs a datapack (or collection of datapacks contained in one ' \
        'directory) when supplied with a file path.', nargs='?',
        dest='install_datapack', type=str, required=False)

if __name__ == "__main__":
    main()
