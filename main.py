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
from util.configuration import File, Minecraft, Maintenance
from minecraft.version import Versioner, UpdateType
from util.mielib.custominput import bool_input
from minecraft.install import Installer
from util.syslog import log, clear_log
from util.emailer import Emailer
import argparse, sys, os
from rcon import Client
import asyncio
import zipfile
from time import sleep # TODO: Remove me once we're ready to go to production

VERSION = "0.0.1"

# TODO: UPDATE ALL OF THE PATH OBJECTS TO REFLECT THE NEW FILE SYSTEM
def parse(args):
    mc_version = args.minecraft_version
    version = args.version
    command = args.command
    update = args.update
    backup = args.path
    method = args.generate_config
    clean = args.clean

    running_log = []

    # Done
    if mc_version is not False:
        running_log.append('-mcv')
        if Minecraft.build is not None:
            log("Minecraft Server: {}".format(Minecraft.version_str()))
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
        

    # TODO: This needs finished
    if update is not None:
        running_log.append('-u')
        updateServer(update)

    if backup is not None:
        running_log.append('-bu {}'.format(Maintenance.backup_path))
        filename = 'world.{}.zip'.format(Date.strippedTimestamp())
        Backup.put(Installer.server_dir, Maintenance.backup_path, filename)

    # Mostly Done TODO: Will need updated once I update configuration
    if method is not None:
        running_log.append('-gc {}'.format(method))
        generateConfig(method)

    if clean:
        running_log.append('-k')
        clean()

    # TODO: This logic still needs fleshed out
    if not running_log:
        run()

def clean():
    trimEnd()

def trimEnd():
    log('Trimming the end!')
    log('To keep specific end regions, update the end-regions.txt file in the project root with the regions you would like to keep.')
    log('To determine what region files to keep, see Xisumavoid\'s video at https://www.youtube.com/watch?v=fGlqDBcgmIc')
    dir = os.path.dirname(__file__)
    endRegionDir = os.path.join(dir, 'server/world_the_end/DIM1/region')
    endRegionLog = os.path.join(dir, 'end-regions.txt')
    regionsToKeep = []
    filecount = 0

    if os.path.isfile(endRegionLog):
        lines = open(endRegionLog, 'r').readlines()
        for line in lines:
            if line.startswith('#') == False and line != '':
                regionsToKeep.append(line.replace('\n', ''))
                
    for file in os.listdir(endRegionDir):
        if file not in regionsToKeep:
            region = os.path.join(endRegionDir, file)
            os.remove(region)
            filecount += 1

    log('Finished trimming the end! Removed {} region(s)!'.format(filecount))

def run():
    log("Checking config.yml...")
    if File.exists:
        log("Found config.yml")
        clean()
        # Backup
        Installer.install()
        log("Starting server...")
        ram = "{}M".format(Minecraft.allocated_ram)
        # CD into server directory
        current_dir = os.path.dirname(__file__)
        script_path = os.path.join(current_dir, "scripts/start-server.sh")
        log("Setting up bootlog file...")
        bootlog_path = os.path.join(current_dir, "logs/bootlog.txt")
        server_dir = os.path.join(current_dir, "server")
        os.popen("{} {} {} > {}".format(script_path,
                                        ram,
                                        server_dir,
                                        bootlog_path))
        # Start Server
        # Run post-start commands
    else:
        log("Did not find config.yml")
        generateConfig("auto")
        # Run Cron setup
        # Download latest Minecraft Server
        # Start Server

    log("Server started!")

def generateConfig(method):
    user_response = bool_input("This will override your current config.yml," \
            " are you sure you want to do that?", default=False)

    if user_response:
        if method.lower() == "auto":
            log("Automatically generating a default config.yml")
            File.generate()
            log("Config.yml generated!")
        elif method.lower() == "manual":
            log("Generating user-interactive config.yml", silently=True)
            File.build()
        else:
            print("'{}' is not a valid input. Please consult the help ['-h'] " \
                " menu to learn more. ".format(method))
    else:
        log("Generate config cancelled.")

def updateServer(override):
    if not File.data:
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
                if not Maintenance.update_allow_major_update:
                    user_input = bool_input("The setting to allow major updates " \
                        "is set to 'False'. Would you like to override this " \
                        "setting for this update?")
                    should_update = user_input
                else:
                    should_update = True
            else:
                should_update = True

            if should_update:
                Installer.install(override_settings=should_update)

def runCommand(command):
    # TODO: Reference the server.properties file for the password
    with Client('mieserver.ddns.net', 25575, passwd='test') as client:
        response = client.run(command)

        print(response)

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

    parser.add_argument('-k', '--clean', help='Run clean up scripts to help with '\
        'lag on your Minecraft Server.', dest='clean', action='store_true', 
        required=False)

    parser.add_argument('-gc', '--generate-config', help="This will generate " \
        "the configuration for this program. It will take one of two inputs: " \
        "'auto' or 'manual'. By picking 'auto' we will handle creating a " \
        "config file for you with some default inputs. If you select 'manual'" \
        " we will ask you a series of questions to build you your config. You" \
        " may manually edit or re-generate your config at any time.", 
        dest="generate_config", nargs="?" ,const="auto", type=str,
        required=False)

    parser.set_defaults(func=parse)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()