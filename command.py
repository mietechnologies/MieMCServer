from util.configuration import RCON
from util.syslog import log
from rcon import Client

def runCommand(command: str):
    RCON.read()
    if RCON.enabled and RCON.password != "":
        with Client("mieserver.ddns.net",
                    RCON.port,
                    passwd=RCON.password) as client:

            response = client.run(command)
            invalid_responses = ["Unknown command",
                                 "Expected whitespace",
                                 "Invalid or unknown"]

            if response in invalid_responses:
                log("Could not execute command [{}]: {}".format(command,
                                                                response))
            else:
                log(response)
    else:
        log("ERR: RCON has not been correctly initialized.")

