import os

from .date import Date

utilDir = os.path.dirname(__file__)
rootDir = os.path.join(utilDir, '..')
logfile = os.path.join(rootDir, 'logs.txt')
logs = None

def log(message):
    logs = open(logfile, 'a')
    timestamp = Date().timestamp()
    printMessage = '[{}] {}'.format(timestamp, message)
    print(printMessage, file=logs)
    
def start(message):
    logs = open(logfile, 'w')
    timestamp = Date().timestamp()
    printMessage = '[{}] {}'.format(timestamp, message)
    print(printMessage, file=logs)