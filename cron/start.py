#!/usr/bin/python

# On start, we want to:
# - Backup current world
# - Send logs to owner via email
# - Execute list of user-entered commands
# - Launch server

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from main import Main
from util import logger

if __name__ == '__main__':
	main = Main()
	main.trim()
	main.backup()
	main.checkVersion()
	main.startMonitors()
	main.start()
	main.commands()
