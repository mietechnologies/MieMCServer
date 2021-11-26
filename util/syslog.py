from .emailer import Emailer
import os, sys, traceback
from .date import Date

sys.excepthook = lambda type, value, tb: handleUncaughtException(type, value, tb)

__util_dir = os.path.dirname(__file__)
__root_dir = os.path.join(__util_dir, "..")
__log_file = os.path.join(__root_dir, "logs.txt")

def handleUncaughtException(type, exception, tb):
    error = repr(exception)
    trace = "".join(traceback.format_tb(tb))
    log("{}\nTraceback (most recent call last):\n{}".format(error, trace))

    subject = "Uncaught Exception Encountered!"
    body = ("Hey there!\nWish I was bringing you better news, but it looks " \
        "like I've encountered an unhandled exception:\n\n{}\nTraceback " \
        "(most recent call last):\n{}\n\nUnfortunately, this means that the " \
        "server has failed...\nBelow I have attached the logs of the " \
        "server's recent activity. Perhaps some of the last entries can " \
        "point you in the right direction on what may have caused the issue." \
        "\n\nThansk,\nMinePi"
            .format(error, trace))

    email_log(subject, body)

def log(message, silently = False):
    '''A method to log events within the program. Calling this method will log 
    the current time and the given message. It can also print the log message 
    to the console for the user to view'''
    with open(__log_file, "a") as logs:
        timestamp = Date.timestamp()
        printMessage = "[{}] {}".format(timestamp, message)
        if not silently:
            print(printMessage)
        logs.write(printMessage + "\n")

def clear_log():
    '''Deletes the current log file'''
    os.remove(__log_file)

def email_log(subject, body):
    '''A helper method to email the current log file along with a subject and 
    body'''
    mailer = Emailer(subject, body)
    mailer.attach(__log_file)
    mailer.send()