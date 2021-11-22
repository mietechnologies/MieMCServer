import os
import sys
import traceback

from .date import Date
from .emailer import PiMailer

# set the excepthook to route through the MinePi logger
sys.excepthook = lambda type, value, tb: handleUncaughtException(type, value, tb)

utilDir = os.path.dirname(__file__)
rootDir = os.path.join(utilDir, '..')
logfile = os.path.join(rootDir, 'logs.txt')
logs = None

def handleUncaughtException(type, exception, tb):
	error = repr(exception)
	trace = ''.join(traceback.format_tb(tb))
	print('{}\nTraceback (most recent call last):\n{}'.format(error, trace))

	subject = 'Uncaught Exception Encountered!'
	body = '''
	Hey there! 
	Wish I was bringing you better news, but it looks like I've encountered an unhandled exception:
	
	{}
	Traceback (most recent call last):
	{}
	Unfotunately, this means that the server has failed to start...
	Either resolve the issue yourself or forward this email to support with a copy of your logs.

	Thanks,
	MinePi
	'''.format(error, trace)
	mailer = PiMailer('smtp.gmail.com', 587, 'ras.pi.craun@gmail.com', 'dymdu9-vowjIt-kejvah')
	mailer.sendMail('michael.craun@gmail.com', subject, body)

def log(message):
    logs = open(logfile, 'a')
    timestamp = Date().timestamp()
    printMessage = '[{}] {}'.format(timestamp, message)
    print(printMessage)
    print(printMessage, file=logs)
    
def start(message):
    logs = open(logfile, 'w')
    timestamp = Date().timestamp()
    printMessage = '[{}] {}'.format(timestamp, message)
    print(printMessage)
    print(printMessage, file=logs)