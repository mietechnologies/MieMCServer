#!/usr/bin/python

# On start, we want to:
# - Backup current world
# - Send logs to owner via email
# - Execute list of user-entered commands
# - Launch server

import sys
sys.path.append('..')

from main import Main

if __name__ == '__main__':
    main = Main()
    main.trim()
    main.backup()
    main.checkVersion()
    main.startMonitors()
    main.start()
    main.commands()
