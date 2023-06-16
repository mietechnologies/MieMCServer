'''
Handles any and all scripting done in conjunction with the server files.
'''

import os

import command as cmd
from util import path, shell
from util.extension import lines_from_file
from util.logger import log

__THIS_DIR = os.path.dirname(__file__)
__SCRIPTS_DIR = os.path.join(__THIS_DIR, '../scripts')

def start(ram: int):
    '''
    Handles running any scripting required when the server starts.
    '''
    __run_user_bash_script('start')

    server_dir = path.project_path('server')
    logfile = path.project_path('logs', 'bootlog.txt')
    shell.run(f'java -Xmx{ram}M -Xms512M -jar paper.jar nogui > {logfile}', server_dir)

def stop():
    '''
    Hanldes running any scripting required when the server stops.
    '''
    __run_user_bash_script('stop')

def maintenance(configuration):
    '''
    A public-facing function for running all maintenance scripts
    '''
    cmd.run_command('say System maintenance scripts are being ran...', configuration)
    __run_clean_commands(configuration)
    __trim_end_regions()
    run_user_commands(configuration)
    __run_user_bash_script('clean')

def __run_clean_commands(configuration):
    log('Running clean commands...')
    clean_commands = os.path.join(__SCRIPTS_DIR, 'clean-commands.txt')
    commands = lines_from_file(clean_commands)
    cmd.run_terminal(configuration, commands)

def run_user_commands(configuration):
    '''
    Handles running user-entered commands from the `commands.txt` file.
    '''
    log('Running custom commands...')
    command_file = os.path.join(__SCRIPTS_DIR, 'commands.txt')
    commands = lines_from_file(command_file)
    cmd.run_terminal(configuration, commands)

def __run_user_bash_script(during_process: str):
    log(f'Running custom shell script during {during_process}...')
    bash_script = os.path.join(__SCRIPTS_DIR, 'custom-command.sh')
    os.chmod(bash_script, 0o755)
    os.system(f'{bash_script} {during_process}')

def __trim_end_regions():
    '''
    Cleans the subdirectories related to the end to serve two purposes:
        1. Eliminates lag related to unused and loaded end chunks
        2. Eliminates the need for players to travel very far to find resources
           related to the end
    '''

    log('Trimming the end!')
    log('To keep specific end regions, update the end-regions.txt file in ' \
        'the project root with the regions you would like to keep.')
    log('To determine what region files to keep, see Xisumavoid\'s video at ' \
        'https://www.youtube.com/watch?v=fGlqDBcgmIc')

    end_dir = os.path.join(__THIS_DIR, '../server/world_the_end/DIM1')
    end_region_log = os.path.join(__SCRIPTS_DIR, 'end-regions.txt')
    regions_to_keep = lines_from_file(end_region_log)
    filecount = 0

    if not os.path.isdir(end_dir):
        log('End directory does not exist! Please run setup via `python main.py` first!')
        return
        
    # Iterate through all subdirectories of the end region root directory
    # and the files contained within each
    for directory in os.listdir(end_dir):
        path = os.path.join(end_dir, directory)
        if os.path.isdir(path):
            dir_count = 0
            for file in os.listdir(path):
                # If the file is not listed in the regions to keep, delete it
                if file not in regions_to_keep:
                    region = os.path.join(path, file)
                    os.remove(region)
                    dir_count += 1
                    filecount += 1
            if dir_count > 0:
                log(f'Removed {dir_count} from {directory}!')
    log(f'Finished trimming the end! Removed {filecount} region(s)!')
