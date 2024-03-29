import os, sys, traceback
import textwrap
from discord import SyncWebhook
from util import monitor
from util.emailer import Mailer
from util.date import Date
from configuration import config

sys.excepthook = lambda type, value, tb: __handle_uncaught_exception(type, value, tb)

__util_dir = os.path.dirname(__file__)
__root_dir = os.path.join(__util_dir, "..")
__log_dir = os.path.join(__root_dir, "logs")
__log_file = os.path.join(__log_dir, "log.txt")

def create_log_directory():
    if not os.path.exists(__log_dir):
        os.mkdir(__log_dir)

def __handle_uncaught_exception(error_type, exception, tb):
    error = repr(exception)
    trace = "".join(traceback.format_tb(tb))
    log(f'{error}\nTraceback (most recent call last):\n{trace}')

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

    # To eliminate user-confusion, we will send a message to the configured
    # Discord server ONLY if the server HASN'T started successfully when it
    # encounters an error.
    if not monitor.startup_completed_successfully():
        message_discord('It looks like I just encountered an unhandled error. The ' \
            'server might be down for a little while, but someone will get to it ' \
            'as soon as they can. Please be patient.')

    configuration = config.File(log)
    email_log(subject, body, configuration)

def log(message, silently=False, display_date=False):
    '''A method to log events within the program. Calling this method will log 
    the current time and the given message. It can also print the log message
    to the console for the user to view'''
    create_log_directory()

    with open(__log_file, 'a', encoding='utf8') as logs:
        timestamp = Date.timestamp()
        print_message = f'[{timestamp}] {message}'
        if not silently:
            if display_date:
                print(print_message)
            else:
                print(message)
        logs.write(print_message + "\n")

def clear_log():
    '''Deletes the current log file'''
    os.remove(__log_file)

def email_log(subject, body, configuration):
    '''A helper method to email the current log file along with a subject and
    body'''
    mailer = Mailer(subject, body, configuration)
    mailer.attach(__log_file)
    mailer.send()

def message_discord(message: str):
    '''A helper function to send a message to the Discord server if
       this setting is enabled.'''

    config_file = config.File(log)

    if config_file.messaging.discord:
        webhook = SyncWebhook.from_url(config_file.messaging.discord)
        webhook.send(textwrap.dedent(message))
