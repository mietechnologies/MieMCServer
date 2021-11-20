# During reboot, we want to:
# - Send current logs to user
#	- /logs.txt
#	- /bootlogs.txt
# - Reboot

import os
import sys

from main import Main

if __name__ == '__main__':
	main = Main()
	main.sendLogs()
	os.system('sudo reboot')
