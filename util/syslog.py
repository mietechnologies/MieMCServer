from .emailer import Emailer
import os, sys, traceback
import textwrap
from .date import Date
from .configuration import Messaging
from discord import Webhook, RequestsWebhookAdapter

sys.excepthook = lambda type, value, tb: __handleUncaughtException(type, value, tb)

__util_dir = os.path.dirname(__file__)
__root_dir = os.path.join(__util_dir, "..")
__log_dir = os.path.join(__root_dir, "logs")
__log_file = os.path.join(__log_dir, "log.txt")

def create_log_directory():
    if not os.path.exists(__log_dir):
        os.mkdir(__log_dir)

def __handleUncaughtException(type, exception, tb):
    error = repr(exception)
    trace = "".join(traceback.format_tb(tb))
    log("{}\nTraceback (most recent call last):\n{}".format(error, trace))

    subject = "Uncaught Exception Encountered!"
    body = ("Hey there!\n\tI wish I was bringing you better news, but it looks" \
        " like I've encountered an unhandled exceptions:\n\n{}\nTraceback " \
        "(most recent call last):\n{}\n\n\tUnfortunately, this is an error I am" \
        " currenty unable to handle on my own. Depending on where this error" \
        " originated from, your Minecraft server may not be started as a " \
        "result.\n\nThanks,\nMIE-MCServer\n\nP.S. If you've encountered the " \
        "same error multiple times, and its not a result of a change you've " \
        "made to the program, please create an issue at: "\
        "https://github.com/mietechnologies/MIE-MCServer/issues"
            .format(error, trace))

    messageDiscord('It looks like I just encountered an unhandled error. The ' \
        'server might be down for a little while, but someone will get to it ' \
        'as soon as they can. Please be patient.')
    email_log(subject, body)

def log(message, silently=False, display_date=False):
    '''A method to log events within the program. Calling this method will log 
    the current time and the given message. It can also print the log message 
    to the console for the user to view'''
    create_log_directory()
    
    with open(__log_file, "a") as logs:
        timestamp = Date.timestamp()
        printMessage = "[{}] {}".format(timestamp, message)
        if not silently:
            if display_date:
                print(printMessage)
            else:
                print(message)
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

def messageDiscord(message: str):
    '''A helper function to send a message to the Discord server if 
       this setting is enabled.'''

    if Messaging.discord:
        webhook = Webhook.from_url(Messaging.discord, adapter=RequestsWebhookAdapter())
        webhook.send(textwrap.dedent(message))