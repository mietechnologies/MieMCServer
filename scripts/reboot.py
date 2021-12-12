import sys, os
sys.path.append("..")
from util.syslog import log, clear_log, email_log

def run():
    subject = "Friendly Reminder; Maintenance Reboot"
    body = "Hey there,\nJust a friendly heads up that your system is being " \
        "rebooted for maintenance purposes. This is completely normal.\n\n" \
        "I've attached the log file that has accumulated since your last " \
        "reboot.\n\nA new log file will be created as soon as your system is " \
        "back online.\n\nThanks,\nMinePi"
    log("System is rebooting...", silently=True)
    email_log(subject, body)
    clear_log()
    os.system('sudo reboot')