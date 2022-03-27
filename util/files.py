'''
This module acts as a file url provider to all other project files.
'''

import os


__this_dir = os.path.dirname(__file__)
__root_dir = os.path.join(__this_dir, '..')
__logs_dir = os.path.join(__root_dir, 'logs')

def bootlog() -> str:
    return os.path.join(__logs_dir, 'bootlog.txt')

def log() -> str:
    return os.path.join(__logs_dir, 'log.txt')