# During reboot, we want to:
# - Reboot

import os
import sys

os.popen('sudo reboot -f')
