from configuration import config
from util.logger import log
from rcon import Client

DEBUG = False

def run_command(command: str, configuration):
    '''Runs a single command string on the Minecraft server via RCON.

    Parameters:
        command -- The command string you wish to issue to Minecraft.
    '''
    if DEBUG:
        print(f'Not running {command}; project in DEBUG')
        return

    configuration.rcon.read()
    if configuration.rcon.enabled and configuration.rcon.password != "":
        with Client(configuration.server.url,
                    configuration.rcon.port,
                    passwd=configuration.rcon.password) as client:

            response = client.run(command)
            __handleResponse(response, command)
    else:
        log("ERR: RCON has not been correctly initialized.")

def run_terminal(configuration, commands: list[str] = None):
    '''Starts a RCON session that either takes in a list of commands and runs
    them one after another until complete, or will ask for input, run the 
    command, and output the response until the exit keyword is input.

    Parameters:
        commands -- This value is None by default, and does not require a 
        value. But you can pass a list of strings.
    '''
    if DEBUG:
        print(f'Not running {commands}; project in DEBUG')
        return

    configuration.rcon.read()
    if configuration.rcon.enabled and configuration.rcon.password != "":
        with Client(configuration.server.url,
                    configuration.rcon.port,
                    passwd=configuration.rcon.password) as client:
            
            if commands:
                for command in commands:
                    response = client.run(command)
                    __handleResponse(response, command)
            else:
                exit_command = "!exit"
                user_input = input(">> ")

                while (user_input != exit_command):
                    response = client.run(user_input)
                    __handleResponse(response, user_input)
                    user_input = input(">> ")
    else:
        log("ERR: RCON has not been correctly initialized.")

def __handleResponse(response: str, command: str):
    invalid_responses = ["Unknown command",
                         "Expected whitespace",
                         "Invalid or unknown"]
    
    if response in invalid_responses:
        log("Could not execute command [{}]: {}".format(command,
                                                        response))
    elif response:
        log(response)
