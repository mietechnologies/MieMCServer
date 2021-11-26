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

import argparse, sys, os
from util.configuration import File, Minecraft
from util.emailer import Emailer
from minecraft.version import Versioner
from util.syslog import log, clear_log
import zipfile
from time import sleep # TODO: Remove me once we're ready to go to production

VERSION = "0.0.1"

def parse(args):
    mc_version = args.minecraft_version
    version = args.version
    command = args.command
    update = args.update
    backup = args.path
    method = args.generate_config

    running_log = []

    if mc_version is not False:
        running_log.append('-mcv')
        if Minecraft.build is not None:
            log("Minecraft Server: {}".format(Minecraft.version_str()))
        else:
            log("Minecraft Server has not been installed yet.")
    
    if version is not False:
        running_log.append('-v')
        log("minePi Version v{}".format(VERSION))

    if command is not None:
        running_log.append('-c {}'.format(command))
        log("Command Passed: {}".format(command))

    if update is not None:
        running_log.append('-u')
        
        if update == "":

        log("Update in progress...")
        sleep(5)
        log("Update complete!")

    if backup is not None:
        # Check to see if the input is 'Default', if it is use the config
        # location. If not, use the passed in path
        if backup is "Default":
            path = "/usr/brett/minecraft/backup"
        else:
            path = backup
        running_log.append('-bu {}'.format(path))
        log("Backing up to: {}".format(path))
        sleep(2)
        log("Backup complete!")

    if method is not None:
        running_log.append('-gc {}'.format(method))
        generateConfig(method)

    if not running_log:
        run()

def run():
    log("Checking config.yml...")
    if File.exists:
        log("Found config.yml")
        # Trim End
        # Backup
        # CheckVersion
        # Update, if appropriate
        # Start Server
        # Run post-start commands
    else:
        log("Did not find config.yml")
        generateConfig("auto")
        # Run Cron setup
        # Download latest Minecraft Server
        # Start Server

def generateConfig(method):
    validInput = False
    user_response = None
    while (not validInput):
        user_response = input("This will override your current config.yml," \
            " are you sure you want to do that? [y/N] ")
        if user_response.lower() in ["y", "n", "yes", "no", ""]:
            validInput = True
        else:
            print("I'm sorry, I didn't understand your answer.")

    if user_response.lower() in ["y", "yes"]:
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
        dest="path", nargs="?", const="Default", type=str, required=False)

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